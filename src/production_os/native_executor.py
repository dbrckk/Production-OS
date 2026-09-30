from __future__ import annotations

import threading
from dataclasses import dataclass
from typing import Any


_BROWSER_HANDLER = "browser_computer"
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
    if _BROWSER_HANDLER in contracts:
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


def execute_native(
    context: NativeExecutionContext,
) -> dict[str, Any]:
    decision = select_native_handler(context.handoff)
    if not decision.supported:
        return {
            "status":"failed",
            "reason":_NATIVE_UNSUPPORTED,
            "result":{
                "summary":"native executor does not support this job",
            },
        }

    # The browser handler is wired in the next implementation task. Keeping
    # this deterministic failure here avoids inventing a second execution
    # path before its request validation and durable runtime semantics exist.
    return {
        "status":"failed",
        "reason":"native_executor_runtime_unavailable",
        "result":{
            "summary":"native browser handler is not available yet",
        },
    }
