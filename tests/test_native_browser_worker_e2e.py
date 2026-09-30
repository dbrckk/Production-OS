from __future__ import annotations

import json
import threading
import time
from http.server import ThreadingHTTPServer

from production_os.api_auth import TokenAuthorizer, token_digest
from production_os.browser_loop import run_browser_turn_loop
from production_os.control_plane import ControlPlane, make_handler
from production_os.remote_worker import RemoteWorkerClient
from production_os.remote_worker_runner import RemoteWorkerRunner


def _auth():
    return TokenAuthorizer([
        {
            "name":"runner-1",
            "role":"worker",
            "sha256":token_digest("worker-secret"),
        },
    ])


def _server(control):
    server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(control))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread, f"http://127.0.0.1:{server.server_port}"


def _stop(server, thread):
    server.shutdown()
    server.server_close()
    thread.join(timeout=2)


def _browser_handoff():
    return {
        "repository":"dbrckk/native-browser-e2e",
        "task":"Inspect the frontend in the browser.",
        "tool_contracts":{
            "browser_computer":{
                "schema_version":"production-os/browser-computer-tool/v1",
            },
        },
        "browser":{
            "config":{
                "schema_version":"production-os/browser-computer-loop/v1",
                "allowed_hosts":["example.com"],
                "persist_session":True,
                "allow_private_network":False,
                "max_turns":2,
            },
            "turns":[{
                "schema_version":"production-os/browser-computer-turn/v1",
                "turn_id":"observe-1",
                "actions":[{"action":"snapshot","name":"page"}],
            }],
        },
    }


def test_native_browser_worker_completes_without_external_executor(
    tmp_path,
    monkeypatch,
):
    control = ControlPlane(
        str(tmp_path / "native-browser-worker.sqlite"),
        authorizer=_auth(),
    )
    queued = control.queue.enqueue({
        "handoff":_browser_handoff(),
        "required_capabilities":[],
    })
    calls = []

    def fake_loop(config, input_stream, output_stream, **kwargs):
        calls.append({
            "config":config.to_dict(),
            "input":input_stream.read(),
            "runtime_checkpoint":str(kwargs["checkpoint_path"]),
        })
        output_stream.write(json.dumps({
            "schema_version":"production-os/browser-computer-turn-result/v1",
            "turn_id":"observe-1",
            "status":"succeeded",
            "result":{"status":"passed"},
        }) + "\n")
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

    def external_must_not_start(*_args, **_kwargs):
        raise AssertionError("native browser job started external subprocess")

    monkeypatch.setattr(
        "production_os.remote_worker_runner.subprocess.Popen",
        external_must_not_start,
    )

    server, thread, base = _server(control)
    try:
        client = RemoteWorkerClient(
            base,
            "worker-secret",
            "runner-1",
            [],
            timeout=5,
        )
        runner = RemoteWorkerRunner(
            client,
            [],
            executor_mode="auto",
            runtime_root=str(tmp_path / "runtime"),
            heartbeat_interval_seconds=0.02,
            executor_timeout_seconds=2,
        )

        outcomes = runner.run(cycles=1, idle_sleep_seconds=0)

        assert outcomes == [{
            "job_key":queued["key"],
            "status":"completed",
        }]
        assert len(calls) == 1
        assert '"turn_id":"observe-1"' in calls[0]["input"]
        assert calls[0]["runtime_checkpoint"].endswith(
            "browser-checkpoint.json"
        )
        assert control.queue.get(queued["key"])["status"] == "completed"
    finally:
        _stop(server, thread)


def test_native_browser_worker_reuses_durable_runtime_without_replaying_completed_side_effect(
    tmp_path,
    monkeypatch,
):
    control = ControlPlane(
        str(tmp_path / "native-browser-recovery.sqlite"),
        authorizer=_auth(),
    )
    queued = control.queue.enqueue({
        "handoff":_browser_handoff(),
        "required_capabilities":[],
    })
    runtime_root = tmp_path / "runtime"
    side_effects = []
    durable_completion = threading.Event()

    def durable_loop(config, input_stream, output_stream, **kwargs):
        cancelled = kwargs.get("cancelled")

        def fake_execute(_plan, **execute_kwargs):
            side_effects.append("effect")
            execute_kwargs["on_complete"]()
            durable_completion.set()
            deadline = time.time() + 2
            while (
                cancelled is not None
                and not cancelled()
                and time.time() < deadline
            ):
                time.sleep(0.01)
            return {
                "schema_version":"production-os/browser-computer-result/v1",
                "status":"passed",
                "results":[],
            }

        return run_browser_turn_loop(
            config,
            input_stream,
            output_stream,
            artifacts_dir=kwargs["artifacts_dir"],
            storage_state_path=kwargs["storage_state_path"],
            session_state_path=kwargs["session_state_path"],
            checkpoint_path=kwargs["checkpoint_path"],
            headless=kwargs.get("headless", True),
            cancelled=cancelled,
            execute_fn=fake_execute,
        )

    monkeypatch.setattr(
        "production_os.native_executor.run_browser_turn_loop",
        durable_loop,
    )

    server, server_thread, base = _server(control)
    first_outcomes = []
    try:
        first_client = RemoteWorkerClient(
            base,
            "worker-secret",
            "runner-1",
            [],
            timeout=5,
        )
        first_runner = RemoteWorkerRunner(
            first_client,
            [],
            executor_mode="auto",
            runtime_root=str(runtime_root),
            heartbeat_interval_seconds=0.02,
            executor_timeout_seconds=3,
        )
        first_thread = threading.Thread(
            target=lambda: first_outcomes.extend(
                first_runner.run(cycles=1, idle_sleep_seconds=0)
            ),
            daemon=True,
        )
        first_thread.start()

        assert durable_completion.wait(timeout=2)
        first_runner.request_stop()
        first_thread.join(timeout=2)

        assert first_outcomes == [{
            "job_key":queued["key"],
            "status":"abandoned",
            "reason":"worker_shutdown",
        }]
        assert side_effects == ["effect"]
        assert control.queue.get(queued["key"])["status"] == "acked"

        second_client = RemoteWorkerClient(
            base,
            "worker-secret",
            "runner-1",
            [],
            timeout=5,
        )
        second_runner = RemoteWorkerRunner(
            second_client,
            [],
            executor_mode="auto",
            runtime_root=str(runtime_root),
            heartbeat_interval_seconds=0.02,
            executor_timeout_seconds=3,
        )

        second_outcomes = second_runner.run(
            cycles=1,
            idle_sleep_seconds=0,
        )

        assert second_outcomes == [{
            "job_key":queued["key"],
            "status":"completed",
        }]
        assert side_effects == ["effect"]
        assert control.queue.get(queued["key"])["status"] == "completed"
    finally:
        _stop(server, server_thread)
