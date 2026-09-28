from __future__ import annotations

import hashlib
import ipaddress
import json
import os
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit, urlunsplit


BROWSER_PLAN_SCHEMA = "production-os/browser-computer-plan/v1"
BROWSER_SESSION_SCHEMA = "production-os/browser-computer-session/v1"
BROWSER_CHECKPOINT_SCHEMA = "production-os/browser-computer-checkpoint/v1"
_ALLOWED_ACTIONS = {
    "navigate",
    "click",
    "fill",
    "press",
    "wait_for",
    "extract_text",
    "screenshot",
    "back",
    "forward",
    "checkpoint",
}
_SAFE_NAME = re.compile(r"^[A-Za-z0-9._-]{1,120}$")


@dataclass(frozen=True, slots=True)
class BrowserAction:
    action: str
    selector: str | None = None
    url: str | None = None
    value: str | None = None
    key: str | None = None
    name: str | None = None
    timeout_ms: int = 10000

    def to_dict(self) -> dict[str, Any]:
        payload = {
            "action":self.action,
            "timeout_ms":self.timeout_ms,
        }
        for key in ("selector", "url", "key", "name"):
            value = getattr(self, key)
            if value is not None:
                payload[key] = value
        if self.action != "fill" and self.value is not None:
            payload["value"] = self.value
        return payload


@dataclass(frozen=True, slots=True)
class BrowserPlan:
    allowed_hosts: tuple[str, ...]
    actions: tuple[BrowserAction, ...]
    persist_session: bool
    allow_private_network: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version":BROWSER_PLAN_SCHEMA,
            "allowed_hosts":list(self.allowed_hosts),
            "persist_session":self.persist_session,
            "allow_private_network":self.allow_private_network,
            "actions":[action.to_dict() for action in self.actions],
        }


def _normalize_host(value: str) -> str:
    host = str(value or "").strip().lower().rstrip(".")
    if not host or "/" in host or "@" in host or ":" in host:
        raise ValueError("invalid allowed browser host")
    return host


def _is_private_host(host: str) -> bool:
    normalized = str(host or "").lower().rstrip(".")
    if normalized == "localhost" or normalized.endswith(".localhost"):
        return True
    try:
        address = ipaddress.ip_address(normalized)
    except ValueError:
        return False
    return bool(
        address.is_private
        or address.is_loopback
        or address.is_link_local
        or address.is_reserved
        or address.is_unspecified
    )


def _validate_url(
    url: str,
    allowed_hosts: set[str],
    *,
    allow_private_network: bool,
) -> str:
    value = str(url or "").strip()
    parsed = urlsplit(value)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError("browser navigation requires http or https")
    if parsed.username or parsed.password:
        raise ValueError("browser navigation URL must not contain credentials")
    host = str(parsed.hostname or "").lower().rstrip(".")
    if not host or host not in allowed_hosts:
        raise ValueError("browser navigation host is not allowed")
    if not allow_private_network and _is_private_host(host):
        raise ValueError("browser private-network navigation is disabled")
    return value


def _browser_plan_fingerprint(plan: BrowserPlan) -> str:
    actions = []
    for action in plan.actions:
        row = action.to_dict()
        if action.action == "fill":
            value = action.value or ""
            row["value_sha256"] = hashlib.sha256(
                value.encode("utf-8")
            ).hexdigest()
            row["value_length"] = len(value)
        actions.append(row)
    canonical = json.dumps(
        {
            "allowed_hosts":list(plan.allowed_hosts),
            "allow_private_network":plan.allow_private_network,
            "persist_session":plan.persist_session,
            "actions":actions,
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _load_browser_checkpoint(
    path: str | Path | None,
    plan: BrowserPlan,
) -> dict[str, Any]:
    if path is None:
        return {}
    target = Path(path).expanduser().resolve()
    try:
        payload = json.loads(target.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return {}
    if not isinstance(payload, dict):
        return {}
    if payload.get("schema_version") != BROWSER_CHECKPOINT_SCHEMA:
        return {}
    if payload.get("plan_fingerprint") != _browser_plan_fingerprint(plan):
        return {}
    try:
        next_action_index = int(payload.get("next_action_index", 0))
    except (TypeError, ValueError):
        return {}
    if not 0 <= next_action_index <= len(plan.actions):
        return {}
    last_url = _safe_resume_url(
        str(payload.get("last_url") or ""),
        set(plan.allowed_hosts),
        allow_private_network=plan.allow_private_network,
    )
    if next_action_index and not last_url:
        return {}
    return {
        "schema_version":BROWSER_CHECKPOINT_SCHEMA,
        "plan_fingerprint":payload["plan_fingerprint"],
        "next_action_index":next_action_index,
        "last_url":last_url,
    }


def _write_browser_checkpoint(
    path: str | Path,
    *,
    plan: BrowserPlan,
    next_action_index: int,
    last_url: str,
) -> dict[str, Any]:
    if not 0 <= int(next_action_index) <= len(plan.actions):
        raise ValueError("browser checkpoint action index is invalid")
    safe_url = _safe_resume_url(
        last_url,
        set(plan.allowed_hosts),
        allow_private_network=plan.allow_private_network,
    )
    if int(next_action_index) and not safe_url:
        raise ValueError("browser checkpoint requires a safe last URL")
    target = Path(path).expanduser().resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version":BROWSER_CHECKPOINT_SCHEMA,
        "plan_fingerprint":_browser_plan_fingerprint(plan),
        "next_action_index":int(next_action_index),
        "last_url":safe_url,
        "updated_at":datetime.now(timezone.utc).isoformat(),
    }
    temp = target.with_suffix(target.suffix + ".tmp")
    temp.write_text(
        json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2),
        encoding="utf-8",
    )
    os.replace(temp, target)
    return payload


def _safe_resume_url(
    value: str,
    allowed_hosts: set[str],
    *,
    allow_private_network: bool,
) -> str | None:
    try:
        validated = _validate_url(
            value,
            allowed_hosts,
            allow_private_network=allow_private_network,
        )
    except ValueError:
        return None
    parsed = urlsplit(validated)
    host = str(parsed.hostname or "").lower().rstrip(".")
    netloc = host
    if parsed.port is not None:
        netloc = f"{host}:{parsed.port}"
    return urlunsplit((
        parsed.scheme,
        netloc,
        parsed.path or "/",
        "",
        "",
    ))


def _load_browser_session(
    path: str | Path | None,
    plan: BrowserPlan,
) -> dict[str, Any]:
    if path is None:
        return {}
    target = Path(path).expanduser().resolve()
    try:
        raw = json.loads(target.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return {}
    if not isinstance(raw, dict):
        return {}
    if raw.get("schema_version") != BROWSER_SESSION_SCHEMA:
        return {}
    last_url = _safe_resume_url(
        str(raw.get("last_url") or ""),
        set(plan.allowed_hosts),
        allow_private_network=plan.allow_private_network,
    )
    if not last_url:
        return {}
    return {
        "schema_version":BROWSER_SESSION_SCHEMA,
        "last_url":last_url,
        "updated_at":str(raw.get("updated_at") or ""),
    }


def _write_browser_session(
    path: str | Path,
    *,
    last_url: str,
    plan: BrowserPlan,
) -> dict[str, Any] | None:
    safe_url = _safe_resume_url(
        last_url,
        set(plan.allowed_hosts),
        allow_private_network=plan.allow_private_network,
    )
    if not safe_url:
        return None
    target = Path(path).expanduser().resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version":BROWSER_SESSION_SCHEMA,
        "last_url":safe_url,
        "updated_at":datetime.now(timezone.utc).isoformat(),
    }
    temp = target.with_suffix(target.suffix + ".tmp")
    temp.write_text(
        json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2),
        encoding="utf-8",
    )
    os.replace(temp, target)
    return payload


def validate_browser_plan(
    payload: dict[str, Any],
    *,
    max_actions: int = 64,
) -> BrowserPlan:
    if not isinstance(payload, dict):
        raise ValueError("browser plan must be an object")
    if str(payload.get("schema_version") or "") != BROWSER_PLAN_SCHEMA:
        raise ValueError("unsupported browser plan schema")
    if not 1 <= int(max_actions) <= 256:
        raise ValueError("max_actions must be between 1 and 256")

    raw_hosts = payload.get("allowed_hosts")
    if not isinstance(raw_hosts, list) or not raw_hosts:
        raise ValueError("browser plan requires allowed_hosts")
    allowed_hosts = tuple(dict.fromkeys(
        _normalize_host(value)
        for value in raw_hosts
    ))
    if len(allowed_hosts) > 20:
        raise ValueError("browser plan has too many allowed hosts")
    allowed_set = set(allowed_hosts)
    allow_private_network = bool(payload.get("allow_private_network", False))
    if not allow_private_network and any(
        _is_private_host(host)
        for host in allowed_hosts
    ):
        raise ValueError("browser private-network hosts require explicit opt-in")

    raw_actions = payload.get("actions")
    if not isinstance(raw_actions, list) or not raw_actions:
        raise ValueError("browser plan requires actions")
    if len(raw_actions) > int(max_actions):
        raise ValueError("browser plan exceeds max_actions")

    actions: list[BrowserAction] = []
    for index, raw in enumerate(raw_actions):
        if not isinstance(raw, dict):
            raise ValueError(f"browser action {index + 1} must be an object")
        action = str(raw.get("action") or "").strip().lower()
        if action not in _ALLOWED_ACTIONS:
            raise ValueError(f"unsupported browser action: {action!r}")
        try:
            timeout_ms = int(raw.get("timeout_ms", 10000))
        except (TypeError, ValueError) as exc:
            raise ValueError("browser action timeout is invalid") from exc
        if not 100 <= timeout_ms <= 30000:
            raise ValueError("browser action timeout must be 100-30000 ms")

        selector = None
        if action in {"click", "fill", "press", "wait_for", "extract_text"}:
            selector = str(raw.get("selector") or "").strip()
            if not selector or len(selector) > 1000:
                raise ValueError(f"browser action {action} requires selector")

        url = None
        if action == "navigate":
            url = _validate_url(
                str(raw.get("url") or ""),
                allowed_set,
                allow_private_network=allow_private_network,
            )

        value = None
        if action == "fill":
            value = str(raw.get("value") or "")
            if len(value) > 8192:
                raise ValueError("browser fill value is too long")

        key = None
        if action == "press":
            key = str(raw.get("key") or "").strip()
            if not key or len(key) > 80:
                raise ValueError("browser press requires a valid key")

        name = None
        if action in {"extract_text", "screenshot"}:
            name = str(raw.get("name") or f"step-{index + 1}").strip()
            if _SAFE_NAME.fullmatch(name) is None:
                raise ValueError("browser action name is invalid")

        actions.append(BrowserAction(
            action=action,
            selector=selector,
            url=url,
            value=value,
            key=key,
            name=name,
            timeout_ms=timeout_ms,
        ))

    return BrowserPlan(
        allowed_hosts=allowed_hosts,
        actions=tuple(actions),
        persist_session=bool(payload.get("persist_session", True)),
        allow_private_network=allow_private_network,
    )


def execute_browser_plan(
    plan: BrowserPlan,
    *,
    artifacts_dir: str | Path,
    storage_state_path: str | Path | None = None,
    session_state_path: str | Path | None = None,
    checkpoint_path: str | Path | None = None,
    headless: bool = True,
) -> dict[str, Any]:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise RuntimeError(
            "browser runtime requires Playwright in the worker image"
        ) from exc

    artifacts = Path(artifacts_dir).expanduser().resolve()
    artifacts.mkdir(parents=True, exist_ok=True)
    state_path = (
        Path(storage_state_path).expanduser().resolve()
        if storage_state_path is not None
        else None
    )
    session_path = (
        Path(session_state_path).expanduser().resolve()
        if session_state_path is not None
        else None
    )
    checkpoint = _load_browser_checkpoint(
        checkpoint_path,
        plan,
    )
    allowed = set(plan.allowed_hosts)
    previous_session = _load_browser_session(
        session_path,
        plan,
    )
    results: list[dict[str, Any]] = []

    def assert_current_host(page) -> None:
        if not page.url or page.url == "about:blank":
            return
        parsed = urlsplit(page.url)
        if parsed.scheme not in {"http", "https"}:
            raise RuntimeError(
                f"browser navigated to disallowed scheme: {parsed.scheme or '<none>'}"
            )
        host = str(parsed.hostname or "").lower().rstrip(".")
        if host not in allowed:
            raise RuntimeError(
                f"browser navigated to disallowed host: {host or '<none>'}"
            )
        if not plan.allow_private_network and _is_private_host(host):
            raise RuntimeError("browser navigated to private network host")

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=bool(headless))
        context_kwargs: dict[str, Any] = {}
        if state_path is not None and state_path.is_file():
            context_kwargs["storage_state"] = str(state_path)
        context = browser.new_context(**context_kwargs)
        page = context.new_page()
        final_url: str | None = None
        resumed_from_url: str | None = None
        resumed_action_index = 0
        try:
            checkpoint_index = int(
                checkpoint.get("next_action_index") or 0
            )
            checkpoint_url = str(checkpoint.get("last_url") or "")
            first_action = plan.actions[0].action if plan.actions else ""
            previous_url = str(previous_session.get("last_url") or "")
            resume_url = checkpoint_url or previous_url
            should_resume = bool(
                plan.persist_session
                and resume_url
                and (
                    checkpoint_index > 0
                    or first_action != "navigate"
                )
            )
            if should_resume:
                page.goto(
                    resume_url,
                    wait_until="domcontentloaded",
                    timeout=10000,
                )
                assert_current_host(page)
                final_url = page.url
                resumed_from_url = resume_url
                resumed_action_index = checkpoint_index

            for index, action in enumerate(
                plan.actions[checkpoint_index:],
                start=checkpoint_index + 1,
            ):
                if action.action == "navigate":
                    page.goto(
                        action.url,
                        wait_until="domcontentloaded",
                        timeout=action.timeout_ms,
                    )
                elif action.action == "click":
                    page.locator(action.selector).click(timeout=action.timeout_ms)
                elif action.action == "fill":
                    page.locator(action.selector).fill(
                        action.value or "",
                        timeout=action.timeout_ms,
                    )
                elif action.action == "press":
                    page.locator(action.selector).press(
                        action.key or "",
                        timeout=action.timeout_ms,
                    )
                elif action.action == "wait_for":
                    page.locator(action.selector).wait_for(
                        timeout=action.timeout_ms,
                    )
                elif action.action == "extract_text":
                    text = page.locator(action.selector).inner_text(
                        timeout=action.timeout_ms,
                    )
                    results.append({
                        "step":index,
                        "action":action.action,
                        "name":action.name,
                        "text":str(text)[:20000],
                    })
                elif action.action == "screenshot":
                    target = artifacts / f"{action.name}.png"
                    page.screenshot(path=str(target), full_page=True)
                    results.append({
                        "step":index,
                        "action":action.action,
                        "name":action.name,
                        "artifact":str(target),
                    })
                elif action.action == "back":
                    page.go_back(
                        wait_until="domcontentloaded",
                        timeout=action.timeout_ms,
                    )
                elif action.action == "forward":
                    page.go_forward(
                        wait_until="domcontentloaded",
                        timeout=action.timeout_ms,
                    )
                elif action.action == "checkpoint":
                    if not plan.persist_session:
                        raise RuntimeError(
                            "browser checkpoint requires persist_session"
                        )
                    if state_path is None or checkpoint_path is None:
                        raise RuntimeError(
                            "browser checkpoint requires durable state paths"
                        )
                    state_path.parent.mkdir(parents=True, exist_ok=True)
                    context.storage_state(path=str(state_path))
                    if session_path is not None and page.url:
                        _write_browser_session(
                            session_path,
                            last_url=page.url,
                            plan=plan,
                        )
                    _write_browser_checkpoint(
                        checkpoint_path,
                        plan=plan,
                        next_action_index=index,
                        last_url=page.url,
                    )
                    results.append({
                        "step":index,
                        "action":"checkpoint",
                        "next_action_index":index,
                    })

                assert_current_host(page)
                final_url = page.url
                if action.action not in {
                    "extract_text",
                    "screenshot",
                    "checkpoint",
                }:
                    results.append({
                        "step":index,
                        "action":action.action,
                        "url":page.url,
                    })

            if plan.persist_session and state_path is not None:
                state_path.parent.mkdir(parents=True, exist_ok=True)
                context.storage_state(path=str(state_path))
            if (
                plan.persist_session
                and session_path is not None
                and final_url
            ):
                _write_browser_session(
                    session_path,
                    last_url=final_url,
                    plan=plan,
                )
            if checkpoint_path is not None:
                try:
                    Path(checkpoint_path).expanduser().resolve().unlink()
                except FileNotFoundError:
                    pass
        finally:
            context.close()
            browser.close()

    return {
        "schema_version":"production-os/browser-computer-result/v1",
        "status":"passed",
        "final_url":final_url,
        "resumed_from_url":resumed_from_url,
        "resumed_action_index":resumed_action_index,
        "results":results,
        "storage_state_path":(
            str(state_path)
            if plan.persist_session and state_path is not None
            else None
        ),
        "session_state_path":(
            str(session_path)
            if plan.persist_session and session_path is not None
            else None
        ),
        "checkpoint_path":(
            str(Path(checkpoint_path).expanduser().resolve())
            if checkpoint_path is not None
            else None
        ),
    }
