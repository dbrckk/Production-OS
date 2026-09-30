from __future__ import annotations

import threading

from production_os.native_executor import (
    NativeExecutionContext,
    execute_native,
    select_native_handler,
)


def _browser_handoff():
    return {
        "tool_contracts":{
            "browser_computer":{
                "schema_version":"production-os/browser-computer-tool/v1",
            },
        },
    }


def test_select_native_handler_supports_browser_computer_contract():
    decision = select_native_handler(_browser_handoff())

    assert decision.supported is True
    assert decision.handler_name == "browser_computer"
    assert decision.reason is None


def test_select_native_handler_rejects_unknown_contracts():
    decision = select_native_handler({
        "tool_contracts":{
            "unknown_tool":{"schema_version":"example/unknown/v1"},
        },
    })

    assert decision.supported is False
    assert decision.handler_name is None
    assert decision.reason == "native_executor_unsupported"


def test_select_native_handler_is_deterministic_when_multiple_contracts_exist():
    handoff = _browser_handoff()
    handoff["tool_contracts"]["zzz_unknown"] = {
        "schema_version":"example/unknown/v1",
    }

    first = select_native_handler(handoff)
    second = select_native_handler(handoff)

    assert first == second
    assert first.handler_name == "browser_computer"


def test_execute_native_rejects_unsupported_context_without_side_effects():
    context = NativeExecutionContext(
        job_key="job-1",
        handoff={"tool_contracts":{"unknown":{}}},
        runtime_workspace=None,
        cancellation_event=threading.Event(),
        artifacts_dir=None,
    )

    result = execute_native(context)

    assert result["status"] == "failed"
    assert result["reason"] == "native_executor_unsupported"
    assert result["result"]["summary"] == "native executor does not support this job"
