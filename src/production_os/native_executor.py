from __future__ import annotations

import io
import json
import tempfile
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .browser_loop import (
    run_browser_turn_loop,
    validate_browser_loop_config,
)


_BROWSER_HANDLER = "browser_computer"
_BROWSER_TOOL_SCHEMA = "production-os/browser-computer-tool/v1"
_NATIVE_UNSUPPORTED = "native_executor_unsupported"


@dataclass(frozen=True, slots=True)
class NativeExecutionContext:
    job_key: str
    handoff: dict[str, Any]
    runtime_workspace: str | None
    cancellation_event: threading.Event
    artifacts_dir: str | None


@dataclass(frozen=True, slots=True)
class NativeExecutionDecision:
    supported: bool
    handler_name: str | None
    reason: str | None


def select_native_handler(
    handoff: dict[str, Any],
) -> NativeExecutionDecision:
    if not isinstance(handoff, dict):
        return NativeExecutionDecision(
            supported=False,
            handler_name=None,
            reason=_NATIVE_UNSUPPORTED,
        )
    contracts = handoff.get("tool_contracts")
    if not isinstance(contracts, dict):
        contracts = {}
    browser_contract = contracts.get(_BROWSER_HANDLER)
    browser_request = handoff.get("browser")
    contract_supported = (
        isinstance(browser_contract, dict)
        and (
            str(browser_contract.get("schema") or "")
            == "production-os/browser-computer-plan/v1"
            or str(browser_contract.get("schema_version") or "")
            == _BROWSER_TOOL_SCHEMA
        )
    )
    request_supported = (
        isinstance(browser_request, dict)
        and isinstance(browser_request.get("config"), dict)
        and isinstance(browser_request.get("turns"), list)
    )
    if contract_supported and request_supported:
        return NativeExecutionDecision(
            supported=True,
            handler_name=_BROWSER_HANDLER,
            reason=None,
        )
    return NativeExecutionDecision(
        supported=False,
        handler_name=None,
        reason=_NATIVE_UNSUPPORTED,
    )


def _failure(reason: str, summary: str, **result: Any) -> dict[str, Any]:
    return {
        "status":"failed",
        "reason":reason,
        "result":{
            "summary":summary,
            **result,
        },
    }


def execute_browser_native(
    context: NativeExecutionContext,
) -> dict[str, Any]:
    browser = context.handoff.get("browser")
    if not isinstance(browser, dict):
        return _failure(
            "native_executor_invalid_request",
            "native browser request is missing",
        )
    config_payload = browser.get("config")
    turns = browser.get("turns")
    if not isinstance(config_payload, dict) or not isinstance(turns, list):
        return _failure(
            "native_executor_invalid_request",
            "native browser request is invalid",
        )
    if not turns or any(not isinstance(turn, dict) for turn in turns):
        return _failure(
            "native_executor_invalid_request",
            "native browser request requires submitted turns",
        )

    try:
        config = validate_browser_loop_config(config_payload)
    except ValueError as exc:
        return _failure(
            "native_executor_invalid_request",
            str(exc)[:1000],
        )

    if len(turns) > config.max_turns:
        return _failure(
            "native_executor_invalid_request",
            (
                "native browser submitted turns exceed "
                f"max_turns ({len(turns)} > {config.max_turns})"
            ),
        )

    runtime_workspace = (
        Path(context.runtime_workspace).expanduser().resolve()
        if context.runtime_workspace
        else None
    )
    if config.persist_session and runtime_workspace is None:
        return _failure(
            "native_executor_runtime_unavailable",
            "persistent native browser execution requires runtime workspace",
        )

    ephemeral_artifacts: tempfile.TemporaryDirectory[str] | None = None
    if runtime_workspace is not None:
        artifacts_dir = runtime_workspace / "browser-artifacts"
        storage_state_path = runtime_workspace / "browser-state.json"
        session_state_path = runtime_workspace / "browser-session.json"
        checkpoint_path = runtime_workspace / "browser-checkpoint.json"
    else:
        if context.artifacts_dir:
            artifacts_dir = Path(
                context.artifacts_dir
            ).expanduser().resolve()
        else:
            ephemeral_artifacts = tempfile.TemporaryDirectory(
                prefix="production-os-browser-",
            )
            artifacts_dir = Path(ephemeral_artifacts.name).resolve()
        storage_state_path = None
        session_state_path = None
        checkpoint_path = None

    input_stream = io.StringIO(
        "".join(
            json.dumps(
                turn,
                ensure_ascii=False,
                separators=(",", ":"),
            ) + "\n"
            for turn in turns
        )
    )
    output_stream = io.StringIO()
    try:
        try:
            summary = run_browser_turn_loop(
                config,
                input_stream,
                output_stream,
                artifacts_dir=artifacts_dir,
                storage_state_path=storage_state_path,
                session_state_path=session_state_path,
                checkpoint_path=checkpoint_path,
                cancelled=context.cancellation_event.is_set,
            )
        except ValueError as exc:
            return _failure(
                "native_executor_invalid_request",
                str(exc)[:1000],
            )
        except Exception as exc:
            return _failure(
                "native_executor_failed",
                str(exc)[:1000],
            )
    finally:
        if ephemeral_artifacts is not None:
            ephemeral_artifacts.cleanup()

    turn_results = []
    for line in output_stream.getvalue().splitlines():
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(row, dict):
            turn_results.append(row)

    result = {
        "summary":"native browser loop completed",
        "browser_loop":summary,
        "browser_turn_results":turn_results,
    }
    if int(summary.get("failed") or 0) > 0:
        return {
            "status":"failed",
            "reason":"native_executor_failed",
            "result":result,
        }
    if int(summary.get("rejected") or 0) > 0:
        return {
            "status":"failed",
            "reason":"native_executor_invalid_request",
            "result":result,
        }
    return {
        "status":"succeeded",
        "result":result,
    }


def execute_native(
    context: NativeExecutionContext,
) -> dict[str, Any]:
    decision = select_native_handler(context.handoff)
    if not decision.supported:
        return _failure(
            _NATIVE_UNSUPPORTED,
            "native executor does not support this job",
        )
    if decision.handler_name == _BROWSER_HANDLER:
        return execute_browser_native(context)
    return _failure(
        _NATIVE_UNSUPPORTED,
        "native executor does not support this job",
    )
