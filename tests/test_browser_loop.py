import io
import json

import pytest

from production_os.browser_loop import (
    BROWSER_LOOP_SCHEMA,
    BROWSER_TURN_RESULT_SCHEMA,
    BROWSER_TURN_SCHEMA,
    _turn_checkpoint_path,
    run_browser_turn_loop,
    validate_browser_loop_config,
)


def _config(**overrides):
    payload = {
        "schema_version":BROWSER_LOOP_SCHEMA,
        "allowed_hosts":["example.com"],
        "persist_session":True,
        "allow_private_network":False,
        "max_turns":4,
    }
    payload.update(overrides)
    return validate_browser_loop_config(payload)


def _turn(turn_id, actions):
    return json.dumps({
        "schema_version":BROWSER_TURN_SCHEMA,
        "turn_id":turn_id,
        "actions":actions,
    })


def test_browser_loop_executes_multiple_turns_with_fixed_host_policy(tmp_path):
    seen = []

    def fake_execute(plan, **kwargs):
        seen.append({
            "plan":plan.to_dict(),
            "checkpoint_path":kwargs["checkpoint_path"],
            "storage_state_path":kwargs["storage_state_path"],
            "session_state_path":kwargs["session_state_path"],
        })
        return {
            "schema_version":"production-os/browser-computer-result/v1",
            "status":"passed",
            "results":[],
        }

    input_stream = io.StringIO(
        _turn("observe-1", [{"action":"snapshot","name":"observe"}])
        + "\n"
        + _turn(
            "act-2",
            [{"action":"click","selector":"#save"}],
        )
        + "\n"
    )
    output_stream = io.StringIO()
    summary = run_browser_turn_loop(
        _config(),
        input_stream,
        output_stream,
        artifacts_dir=tmp_path / "artifacts",
        storage_state_path=tmp_path / "storage.json",
        session_state_path=tmp_path / "session.json",
        checkpoint_path=tmp_path / "checkpoint.json",
        execute_fn=fake_execute,
    )

    assert summary == {
        "schema_version":"production-os/browser-computer-loop-result/v1",
        "turns":2,
        "succeeded":2,
        "rejected":0,
        "failed":0,
    }
    assert len(seen) == 2
    assert seen[0]["plan"]["allowed_hosts"] == ["example.com"]
    assert seen[1]["plan"]["allowed_hosts"] == ["example.com"]
    assert seen[0]["checkpoint_path"] != seen[1]["checkpoint_path"]
    assert seen[0]["checkpoint_path"].endswith(".json")
    rows = [
        json.loads(line)
        for line in output_stream.getvalue().splitlines()
    ]
    assert [row["status"] for row in rows] == ["succeeded", "succeeded"]
    assert all(
        row["schema_version"] == BROWSER_TURN_RESULT_SCHEMA
        for row in rows
    )


def test_browser_loop_rejects_turn_that_expands_navigation_host(tmp_path):
    input_stream = io.StringIO(
        _turn(
            "bad-host",
            [{"action":"navigate","url":"https://evil.example/"}],
        )
        + "\n"
        + _turn(
            "safe",
            [{"action":"navigate","url":"https://example.com/"}],
        )
        + "\n"
    )
    output_stream = io.StringIO()
    calls = []

    def fake_execute(plan, **_kwargs):
        calls.append(plan.to_dict())
        return {"status":"passed"}

    summary = run_browser_turn_loop(
        _config(),
        input_stream,
        output_stream,
        artifacts_dir=tmp_path / "artifacts",
        storage_state_path=tmp_path / "storage.json",
        session_state_path=tmp_path / "session.json",
        checkpoint_path=tmp_path / "checkpoint.json",
        execute_fn=fake_execute,
    )

    rows = [
        json.loads(line)
        for line in output_stream.getvalue().splitlines()
    ]
    assert rows[0]["status"] == "rejected"
    assert "host is not allowed" in rows[0]["error"]
    assert rows[1]["status"] == "succeeded"
    assert len(calls) == 1
    assert summary["rejected"] == 1
    assert summary["succeeded"] == 1


def test_browser_loop_stops_after_failed_turn_to_preserve_recovery_fence(tmp_path):
    input_stream = io.StringIO(
        _turn("uncertain", [{"action":"click","selector":"#submit"}])
        + "\n"
        + _turn("must-not-run", [{"action":"snapshot","name":"observe"}])
        + "\n"
    )
    output_stream = io.StringIO()
    calls = []

    def fail_execute(plan, **kwargs):
        calls.append(kwargs["checkpoint_path"])
        raise RuntimeError("browser recovery required before replay")

    summary = run_browser_turn_loop(
        _config(),
        input_stream,
        output_stream,
        artifacts_dir=tmp_path / "artifacts",
        storage_state_path=tmp_path / "storage.json",
        session_state_path=tmp_path / "session.json",
        checkpoint_path=tmp_path / "checkpoint.json",
        execute_fn=fail_execute,
    )

    assert len(calls) == 1
    assert summary["turns"] == 1
    assert summary["failed"] == 1
    rows = [
        json.loads(line)
        for line in output_stream.getvalue().splitlines()
    ]
    assert len(rows) == 1
    assert rows[0]["status"] == "failed"


def test_browser_loop_requires_durable_paths_when_persistent(tmp_path):
    with pytest.raises(
        ValueError,
        match="requires durable storage, session, and checkpoint paths",
    ):
        run_browser_turn_loop(
            _config(),
            io.StringIO(""),
            io.StringIO(),
            artifacts_dir=tmp_path / "artifacts",
        )


def test_browser_loop_enforces_max_turns(tmp_path):
    input_stream = io.StringIO(
        _turn("one", [{"action":"snapshot","name":"one"}])
        + "\n"
        + _turn("two", [{"action":"snapshot","name":"two"}])
        + "\n"
    )
    output_stream = io.StringIO()

    def fake_execute(_plan, **_kwargs):
        return {"status":"passed"}

    summary = run_browser_turn_loop(
        _config(max_turns=1),
        input_stream,
        output_stream,
        artifacts_dir=tmp_path / "artifacts",
        storage_state_path=tmp_path / "storage.json",
        session_state_path=tmp_path / "session.json",
        checkpoint_path=tmp_path / "checkpoint.json",
        execute_fn=fake_execute,
    )

    rows = [
        json.loads(line)
        for line in output_stream.getvalue().splitlines()
    ]
    assert rows[0]["status"] == "succeeded"
    assert rows[1]["status"] == "limit-reached"
    assert summary["turns"] == 1


def test_turn_checkpoint_path_is_stable_and_turn_scoped(tmp_path):
    base = tmp_path / "browser-checkpoint.json"
    first = _turn_checkpoint_path(base, "turn-a")
    again = _turn_checkpoint_path(base, "turn-a")
    other = _turn_checkpoint_path(base, "turn-b")

    assert first == again
    assert first != other
    assert str(tmp_path) in first
    assert "turn-a" not in first


@pytest.mark.parametrize(
    "payload,match",
    [
        (
            {
                "schema_version":"wrong",
                "allowed_hosts":["example.com"],
            },
            "unsupported browser loop schema",
        ),
        (
            {
                "schema_version":BROWSER_LOOP_SCHEMA,
                "allowed_hosts":["example.com"],
                "max_turns":0,
            },
            "max_turns must be between",
        ),
        (
            {
                "schema_version":BROWSER_LOOP_SCHEMA,
                "allowed_hosts":["127.0.0.1"],
            },
            "private-network",
        ),
    ],
)
def test_browser_loop_config_reuses_browser_safety_validation(payload, match):
    with pytest.raises(ValueError, match=match):
        validate_browser_loop_config(payload)



def test_browser_loop_cli_parses_jsonl_runtime_paths():
    from production_os.cli import _parse_args

    args = _parse_args([
        "browser-loop-run",
        "--config", "/tmp/browser-loop.json",
        "--artifacts-dir", "/tmp/artifacts",
        "--storage-state", "/tmp/storage.json",
        "--session-state", "/tmp/session.json",
        "--checkpoint-state", "/tmp/checkpoint.json",
    ])

    assert args.config == "/tmp/browser-loop.json"
    assert args.artifacts_dir == "/tmp/artifacts"
    assert args.storage_state == "/tmp/storage.json"
    assert args.session_state == "/tmp/session.json"
    assert args.checkpoint_state == "/tmp/checkpoint.json"
    assert args.headed is False
