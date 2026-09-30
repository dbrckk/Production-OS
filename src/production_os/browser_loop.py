from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, TextIO

from .browser_computer import (
    BROWSER_PLAN_SCHEMA,
    _load_browser_checkpoint,
    execute_browser_plan,
    validate_browser_plan,
)


BROWSER_LOOP_SCHEMA = "production-os/browser-computer-loop/v1"
BROWSER_TURN_SCHEMA = "production-os/browser-computer-turn/v1"
BROWSER_TURN_RESULT_SCHEMA = "production-os/browser-computer-turn-result/v1"


@dataclass(frozen=True, slots=True)
class BrowserLoopConfig:
    allowed_hosts: tuple[str, ...]
    persist_session: bool
    allow_private_network: bool
    max_turns: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version":BROWSER_LOOP_SCHEMA,
            "allowed_hosts":list(self.allowed_hosts),
            "persist_session":self.persist_session,
            "allow_private_network":self.allow_private_network,
            "max_turns":self.max_turns,
        }


def validate_browser_loop_config(
    payload: dict[str, Any],
    *,
    max_turns_limit: int = 128,
) -> BrowserLoopConfig:
    if not isinstance(payload, dict):
        raise ValueError("browser loop config must be an object")
    if str(payload.get("schema_version") or "") != BROWSER_LOOP_SCHEMA:
        raise ValueError("unsupported browser loop schema")

    raw_hosts = payload.get("allowed_hosts")
    if not isinstance(raw_hosts, list) or not raw_hosts:
        raise ValueError("browser loop requires allowed_hosts")

    try:
        max_turns = int(payload.get("max_turns", 32))
    except (TypeError, ValueError) as exc:
        raise ValueError("browser loop max_turns is invalid") from exc
    if not 1 <= max_turns <= int(max_turns_limit):
        raise ValueError(
            f"browser loop max_turns must be between 1 and {int(max_turns_limit)}"
        )

    # Reuse the browser-plan validator as the authoritative host/safety parser.
    bootstrap = validate_browser_plan({
        "schema_version":BROWSER_PLAN_SCHEMA,
        "allowed_hosts":raw_hosts,
        "persist_session":bool(payload.get("persist_session", True)),
        "allow_private_network":bool(
            payload.get("allow_private_network", False)
        ),
        "actions":[{"action":"snapshot","name":"bootstrap"}],
    })
    return BrowserLoopConfig(
        allowed_hosts=bootstrap.allowed_hosts,
        persist_session=bootstrap.persist_session,
        allow_private_network=bootstrap.allow_private_network,
        max_turns=max_turns,
    )


def _turn_plan_payload(
    config: BrowserLoopConfig,
    turn: dict[str, Any],
) -> tuple[str, dict[str, Any]]:
    if not isinstance(turn, dict):
        raise ValueError("browser turn must be an object")
    if str(turn.get("schema_version") or "") != BROWSER_TURN_SCHEMA:
        raise ValueError("unsupported browser turn schema")
    turn_id = str(turn.get("turn_id") or "").strip()
    if not turn_id or len(turn_id) > 120:
        raise ValueError("browser turn_id is invalid")
    actions = turn.get("actions")
    if not isinstance(actions, list) or not actions:
        raise ValueError("browser turn requires actions")
    payload = {
        "schema_version":BROWSER_PLAN_SCHEMA,
        "allowed_hosts":list(config.allowed_hosts),
        "persist_session":config.persist_session,
        "allow_private_network":config.allow_private_network,
        "actions":actions,
    }
    return turn_id, payload


def _turn_checkpoint_path(
    checkpoint_path: str | Path | None,
    turn_id: str,
) -> str | None:
    if checkpoint_path is None:
        return None
    base = Path(checkpoint_path).expanduser().resolve()
    digest = hashlib.sha256(turn_id.encode("utf-8")).hexdigest()[:16]
    return str(
        base.with_name(
            f"{base.stem}-turn-{digest}{base.suffix or '.json'}"
        )
    )


TURN_MANIFEST_SCHEMA = "production-os/browser-computer-turn-manifest/v1"


def _turn_plan_fingerprint(plan_payload: dict[str, Any]) -> str:
    canonical = json.dumps(
        plan_payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _turn_manifest_path(
    checkpoint_path: str | Path | None,
    turn_id: str,
) -> Path | None:
    turn_checkpoint = _turn_checkpoint_path(checkpoint_path, turn_id)
    if turn_checkpoint is None:
        return None
    base = Path(turn_checkpoint)
    return base.with_suffix(base.suffix + ".manifest.json")


def _read_turn_manifest(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return {}
    if not isinstance(payload, dict):
        return {}
    if payload.get("schema_version") != TURN_MANIFEST_SCHEMA:
        return {}
    if payload.get("status") not in {"in_flight", "completed"}:
        return {}
    fingerprint = str(payload.get("plan_fingerprint") or "")
    if len(fingerprint) != 64:
        return {}
    return {
        "schema_version":TURN_MANIFEST_SCHEMA,
        "status":str(payload["status"]),
        "plan_fingerprint":fingerprint,
        "updated_at":str(payload.get("updated_at") or ""),
    }


def _write_turn_manifest(
    path: Path,
    *,
    plan_fingerprint: str,
    status: str,
) -> dict[str, Any]:
    if status not in {"in_flight", "completed"}:
        raise ValueError("invalid browser turn manifest status")
    payload = {
        "schema_version":TURN_MANIFEST_SCHEMA,
        "status":status,
        "plan_fingerprint":plan_fingerprint,
        "updated_at":datetime.now(timezone.utc).isoformat(),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(
        json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2),
        encoding="utf-8",
    )
    os.replace(temp, path)
    return payload


def run_browser_turn_loop(
    config: BrowserLoopConfig,
    input_stream: TextIO,
    output_stream: TextIO,
    *,
    artifacts_dir: str | Path,
    storage_state_path: str | Path | None = None,
    session_state_path: str | Path | None = None,
    checkpoint_path: str | Path | None = None,
    headless: bool = True,
    execute_fn: Callable[..., dict[str, Any]] = execute_browser_plan,
    cancelled: Callable[[], bool] | None = None,
) -> dict[str, Any]:
    if config.persist_session and (
        storage_state_path is None
        or session_state_path is None
        or checkpoint_path is None
    ):
        raise ValueError(
            "persistent browser loop requires durable storage, session, "
            "and checkpoint paths"
        )

    turns = 0
    succeeded = 0
    rejected = 0
    failed = 0
    was_cancelled = False

    for raw_line in input_stream:
        line = str(raw_line).strip()
        if not line:
            continue
        if cancelled is not None and cancelled():
            was_cancelled = True
            break
        if turns >= config.max_turns:
            payload = {
                "schema_version":BROWSER_TURN_RESULT_SCHEMA,
                "status":"limit-reached",
                "error":"browser loop max_turns reached",
            }
            output_stream.write(json.dumps(payload, ensure_ascii=False) + "\n")
            output_stream.flush()
            break

        turns += 1
        turn_id = ""
        try:
            raw_turn = json.loads(line)
            turn_id, plan_payload = _turn_plan_payload(config, raw_turn)
            plan = validate_browser_plan(plan_payload)
            plan_fingerprint = _turn_plan_fingerprint(plan_payload)
            turn_checkpoint = _turn_checkpoint_path(
                checkpoint_path,
                turn_id,
            )
            manifest_path = _turn_manifest_path(
                checkpoint_path,
                turn_id,
            )
            manifest_exists = (
                manifest_path is not None
                and manifest_path.exists()
            )
            manifest = _read_turn_manifest(manifest_path)
            if manifest_exists and not manifest:
                raise RuntimeError(
                    "browser turn manifest is invalid or tampered"
                )

            def mark_turn_completed() -> None:
                if manifest_path is not None:
                    _write_turn_manifest(
                        manifest_path,
                        plan_fingerprint=plan_fingerprint,
                        status="completed",
                    )

            if manifest:
                if manifest["plan_fingerprint"] != plan_fingerprint:
                    raise RuntimeError(
                        "browser turn id is already bound to a different plan"
                    )
                if manifest["status"] == "completed":
                    result = {
                        "schema_version":
                            "production-os/browser-computer-result/v1",
                        "status":"already-completed",
                        "recovered":True,
                        "results":[],
                    }
                else:
                    if (
                        turn_checkpoint is not None
                        and Path(turn_checkpoint).is_file()
                        and not _load_browser_checkpoint(
                            turn_checkpoint,
                            plan,
                        )
                    ):
                        raise RuntimeError(
                            "browser recovery checkpoint is invalid or tampered"
                        )
                    result = execute_fn(
                        plan,
                        artifacts_dir=artifacts_dir,
                        storage_state_path=storage_state_path,
                        session_state_path=session_state_path,
                        checkpoint_path=turn_checkpoint,
                        on_complete=mark_turn_completed,
                        headless=headless,
                    )
                    if manifest_path is not None:
                        _write_turn_manifest(
                            manifest_path,
                            plan_fingerprint=plan_fingerprint,
                            status="completed",
                        )
            else:
                if manifest_path is not None:
                    _write_turn_manifest(
                        manifest_path,
                        plan_fingerprint=plan_fingerprint,
                        status="in_flight",
                    )
                result = execute_fn(
                    plan,
                    artifacts_dir=artifacts_dir,
                    storage_state_path=storage_state_path,
                    session_state_path=session_state_path,
                    checkpoint_path=turn_checkpoint,
                    on_complete=mark_turn_completed,
                    headless=headless,
                )
                if manifest_path is not None:
                    _write_turn_manifest(
                        manifest_path,
                        plan_fingerprint=plan_fingerprint,
                        status="completed",
                    )
        except (ValueError, json.JSONDecodeError) as exc:
            rejected += 1
            response = {
                "schema_version":BROWSER_TURN_RESULT_SCHEMA,
                **({"turn_id":turn_id} if turn_id else {}),
                "status":"rejected",
                "error":str(exc)[:1000],
            }
        except Exception as exc:
            failed += 1
            response = {
                "schema_version":BROWSER_TURN_RESULT_SCHEMA,
                **({"turn_id":turn_id} if turn_id else {}),
                "status":"failed",
                "error":str(exc)[:1000],
            }
        else:
            succeeded += 1
            response = {
                "schema_version":BROWSER_TURN_RESULT_SCHEMA,
                "turn_id":turn_id,
                "status":"succeeded",
                "result":result,
            }

        output_stream.write(
            json.dumps(response, ensure_ascii=False, separators=(",", ":"))
            + "\n"
        )
        output_stream.flush()
        if response["status"] == "failed":
            # A failed turn may have an unresolved in-flight browser side
            # effect. Stop before accepting any different turn. Recovery must
            # retry the same turn id/plan so its durable checkpoint is reused.
            break

    summary = {
        "schema_version":"production-os/browser-computer-loop-result/v1",
        "turns":turns,
        "succeeded":succeeded,
        "rejected":rejected,
        "failed":failed,
    }
    if cancelled is not None:
        summary["cancelled"] = was_cancelled
    return summary
