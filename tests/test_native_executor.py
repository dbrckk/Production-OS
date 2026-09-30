from __future__ import annotations

import threading
from pathlib import Path

import pytest

from production_os.native_executor import (
    NativeExecutionContext,
    execute_browser_native,
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
    decision = select_native_handler(_browser_request())

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
    handoff = _browser_request()
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



def _browser_request(*, persist_session=True):
    handoff = _browser_handoff()
    handoff["browser"] = {
        "config":{
            "schema_version":"production-os/browser-computer-loop/v1",
            "allowed_hosts":["example.com"],
            "persist_session":persist_session,
            "allow_private_network":False,
            "max_turns":4,
        },
        "turns":[
            {
                "schema_version":"production-os/browser-computer-turn/v1",
                "turn_id":"observe-1",
                "actions":[{"action":"snapshot","name":"page"}],
            },
        ],
    }
    return handoff


def test_native_browser_handler_executes_submitted_turns(tmp_path, monkeypatch):
    seen = {}

    def fake_loop(config, input_stream, output_stream, **kwargs):
        seen["config"] = config.to_dict()
        seen["input"] = input_stream.read()
        seen["kwargs"] = kwargs
        output_stream.write('{"status":"succeeded"}\n')
        return {
            "schema_version":"production-os/browser-computer-loop-result/v1",
            "turns":1,
            "succeeded":1,
            "rejected":0,
            "failed":0,
        }

    monkeypatch.setattr(
        "production_os.native_executor.run_browser_turn_loop",
        fake_loop,
    )
    context = NativeExecutionContext(
        job_key="browser-1",
        handoff=_browser_request(),
        runtime_workspace=str(tmp_path),
        cancellation_event=threading.Event(),
        artifacts_dir=None,
    )

    result = execute_native(context)

    assert result["status"] == "succeeded"
    assert result["result"]["browser_loop"]["succeeded"] == 1
    assert '"turn_id":"observe-1"' in seen["input"]


def test_native_browser_handler_uses_runtime_workspace_paths(
    tmp_path,
    monkeypatch,
):
    seen = {}

    def fake_loop(_config, _input, _output, **kwargs):
        seen.update(kwargs)
        return {
            "schema_version":"production-os/browser-computer-loop-result/v1",
            "turns":1,
            "succeeded":1,
            "rejected":0,
            "failed":0,
        }

    monkeypatch.setattr(
        "production_os.native_executor.run_browser_turn_loop",
        fake_loop,
    )
    context = NativeExecutionContext(
        job_key="browser-paths",
        handoff=_browser_request(),
        runtime_workspace=str(tmp_path),
        cancellation_event=threading.Event(),
        artifacts_dir=str(tmp_path / "ignored-artifacts"),
    )

    result = execute_native(context)

    assert result["status"] == "succeeded"
    assert Path(seen["artifacts_dir"]) == tmp_path / "browser-artifacts"
    assert Path(seen["storage_state_path"]) == tmp_path / "browser-state.json"
    assert Path(seen["session_state_path"]) == tmp_path / "browser-session.json"
    assert Path(seen["checkpoint_path"]) == tmp_path / "browser-checkpoint.json"


def test_native_browser_handler_rejects_persistent_session_without_runtime():
    context = NativeExecutionContext(
        job_key="browser-no-runtime",
        handoff=_browser_request(persist_session=True),
        runtime_workspace=None,
        cancellation_event=threading.Event(),
        artifacts_dir="/tmp/browser-artifacts",
    )

    result = execute_native(context)

    assert result["status"] == "failed"
    assert result["reason"] == "native_executor_runtime_unavailable"


def test_native_browser_handler_rejects_missing_browser_request():
    context = NativeExecutionContext(
        job_key="browser-missing-request",
        handoff=_browser_handoff(),
        runtime_workspace=None,
        cancellation_event=threading.Event(),
        artifacts_dir="/tmp/browser-artifacts",
    )

    result = execute_browser_native(context)

    assert result["status"] == "failed"
    assert result["reason"] == "native_executor_invalid_request"


def test_native_browser_handler_preserves_loop_failure_reason(
    tmp_path,
    monkeypatch,
):
    def fake_loop(_config, _input, _output, **_kwargs):
        return {
            "schema_version":"production-os/browser-computer-loop-result/v1",
            "turns":1,
            "succeeded":0,
            "rejected":0,
            "failed":1,
        }

    monkeypatch.setattr(
        "production_os.native_executor.run_browser_turn_loop",
        fake_loop,
    )
    context = NativeExecutionContext(
        job_key="browser-failed-loop",
        handoff=_browser_request(),
        runtime_workspace=str(tmp_path),
        cancellation_event=threading.Event(),
        artifacts_dir=None,
    )

    result = execute_native(context)

    assert result["status"] == "failed"
    assert result["reason"] == "native_executor_failed"
    assert result["result"]["browser_loop"]["failed"] == 1



def test_select_native_handler_rejects_unknown_browser_contract_version():
    decision = select_native_handler({
        "tool_contracts":{
            "browser_computer":{
                "schema_version":"production-os/browser-computer-tool/v999",
            },
        },
    })

    assert decision.supported is False
    assert decision.reason == "native_executor_unsupported"


def test_native_browser_handler_rejects_more_submitted_turns_than_max(
    tmp_path,
    monkeypatch,
):
    handoff = _browser_request()
    handoff["browser"]["config"]["max_turns"] = 1
    handoff["browser"]["turns"].append({
        "schema_version":"production-os/browser-computer-turn/v1",
        "turn_id":"observe-2",
        "actions":[{"action":"snapshot","name":"second"}],
    })
    called = []

    def must_not_run(*_args, **_kwargs):
        called.append(True)
        raise AssertionError("over-limit request must fail before execution")

    monkeypatch.setattr(
        "production_os.native_executor.run_browser_turn_loop",
        must_not_run,
    )
    context = NativeExecutionContext(
        job_key="browser-too-many-turns",
        handoff=handoff,
        runtime_workspace=str(tmp_path),
        cancellation_event=threading.Event(),
        artifacts_dir=None,
    )

    result = execute_native(context)

    assert called == []
    assert result["status"] == "failed"
    assert result["reason"] == "native_executor_invalid_request"
    assert "max_turns" in result["result"]["summary"]


def test_native_browser_handler_classifies_runtime_oserror_as_execution_failure(
    tmp_path,
    monkeypatch,
):
    def fail_runtime(*_args, **_kwargs):
        raise OSError("disk full")

    monkeypatch.setattr(
        "production_os.native_executor.run_browser_turn_loop",
        fail_runtime,
    )
    context = NativeExecutionContext(
        job_key="browser-runtime-io",
        handoff=_browser_request(),
        runtime_workspace=str(tmp_path),
        cancellation_event=threading.Event(),
        artifacts_dir=None,
    )

    result = execute_native(context)

    assert result["status"] == "failed"
    assert result["reason"] == "native_executor_failed"



def test_select_native_handler_accepts_workflow_contract_with_native_request():
    handoff = _browser_request()
    handoff["tool_contracts"]["browser_computer"] = {
        "schema":"production-os/browser-computer-plan/v1",
        "result_schema":"production-os/browser-computer-result/v1",
    }

    decision = select_native_handler(handoff)

    assert decision.supported is True
    assert decision.handler_name == "browser_computer"


def test_select_native_handler_rejects_contract_only_browser_job():
    decision = select_native_handler({
        "tool_contracts":{
            "browser_computer":{
                "schema":"production-os/browser-computer-plan/v1",
                "result_schema":"production-os/browser-computer-result/v1",
            },
        },
    })

    assert decision.supported is False
    assert decision.reason == "native_executor_unsupported"


def test_native_browser_nonpersistent_request_gets_ephemeral_artifacts(
    monkeypatch,
):
    seen = {}

    def fake_loop(_config, _input, _output, **kwargs):
        path = Path(kwargs["artifacts_dir"])
        seen["path"] = path
        seen["exists_during_execution"] = path.is_dir()
        return {
            "schema_version":"production-os/browser-computer-loop-result/v1",
            "turns":1,
            "succeeded":1,
            "rejected":0,
            "failed":0,
        }

    monkeypatch.setattr(
        "production_os.native_executor.run_browser_turn_loop",
        fake_loop,
    )
    context = NativeExecutionContext(
        job_key="browser-ephemeral",
        handoff=_browser_request(persist_session=False),
        runtime_workspace=None,
        cancellation_event=threading.Event(),
        artifacts_dir=None,
    )

    result = execute_native(context)

    assert result["status"] == "succeeded"
    assert seen["exists_during_execution"] is True
