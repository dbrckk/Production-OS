from __future__ import annotations

import json
import sys
import threading
from http.server import ThreadingHTTPServer

from production_os.api_auth import TokenAuthorizer, token_digest
from production_os.control_plane import ControlPlane, make_handler
from production_os.remote_worker import RemoteWorkerClient
from production_os.remote_worker_runner import RemoteWorkerRunner


def _server(control):
    server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(control))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread, f"http://127.0.0.1:{server.server_port}"


def _stop(server, thread):
    server.shutdown()
    server.server_close()
    thread.join(timeout=2)


def _auth():
    return TokenAuthorizer([
        {
            "name":"runner-1",
            "role":"worker",
            "sha256":token_digest("worker-secret"),
        },
        {
            "name":"other-worker",
            "role":"worker",
            "sha256":token_digest("other-secret"),
        },
    ])


def test_worker_session_self_registers_and_reconciles_previous_claim(tmp_path):
    control = ControlPlane(str(tmp_path / "session.sqlite"), authorizer=_auth())
    server, thread, base = _server(control)
    try:
        client = RemoteWorkerClient(
            base,
            "worker-secret",
            "runner-1",
            ["python"],
            timeout=5,
        )
        session = client.open_session(
            max_concurrency=1,
            active_job_keys=[],
        )
        assert session["worker"]["worker_id"] == "runner-1"
        assert session["worker"]["capabilities"] == ["python"]
        assert session["recovered_jobs"] == []

        queued = control.queue.enqueue({
            "handoff":{"repository":"dbrckk/runner","task":"execute"},
            "required_capabilities":["python"],
        })
        job = client.claim()
        assert job is not None
        assert job.key == queued["key"]
        assert client.ack(job.key)["status"] == "acked"

        restarted = RemoteWorkerClient(
            base,
            "worker-secret",
            "runner-1",
            ["python"],
            timeout=5,
        )
        reconciled = restarted.open_session(
            max_concurrency=1,
            active_job_keys=[],
        )
        assert reconciled["recovered_jobs"] == [{
            "key":job.key,
            "worker_id":"runner-1",
            "previous_status":"acked",
            "status":"queued",
        }]
        assert control.queue.get(job.key)["status"] == "queued"
    finally:
        _stop(server, thread)


def test_worker_session_rejects_token_identity_mismatch(tmp_path):
    control = ControlPlane(str(tmp_path / "identity.sqlite"), authorizer=_auth())
    server, thread, base = _server(control)
    try:
        client = RemoteWorkerClient(
            base,
            "other-secret",
            "runner-1",
            [],
            timeout=5,
        )
        try:
            client.open_session(max_concurrency=1, active_job_keys=[])
        except RuntimeError as exc:
            assert "worker identity mismatch" in str(exc)
        else:
            raise AssertionError("worker token must not open another worker session")
    finally:
        _stop(server, thread)


def test_remote_worker_runner_executes_json_executor_and_completes_job(tmp_path):
    control = ControlPlane(str(tmp_path / "runner.sqlite"), authorizer=_auth())
    queued = control.queue.enqueue({
        "handoff":{
            "repository":"dbrckk/runner-success",
            "task":"Implement runner protocol.",
        },
        "required_capabilities":["python"],
    })
    executor = tmp_path / "executor.py"
    executor.write_text(
        """
import json, sys
request = json.load(sys.stdin)
handoff = request["job"]["payload"]["payload"]["handoff"]
print(json.dumps({
    "status":"succeeded",
    "result":{
        "summary":"executed: " + handoff["task"],
        "validation":{"status":"passed","tests":["runner"]},
    },
}))
""".strip(),
        encoding="utf-8",
    )

    server, thread, base = _server(control)
    try:
        client = RemoteWorkerClient(
            base,
            "worker-secret",
            "runner-1",
            ["python"],
            timeout=5,
        )
        runner = RemoteWorkerRunner(
            client,
            [sys.executable, str(executor)],
            heartbeat_interval_seconds=0.1,
            executor_timeout_seconds=5,
        )

        outcomes = runner.run(cycles=1, idle_sleep_seconds=0)

        assert outcomes == [{
            "job_key":queued["key"],
            "status":"completed",
        }]
        assert control.queue.get(queued["key"])["status"] == "completed"
        execution = control.dashboard_store.latest_execution(queued["key"])
        assert execution["status"] == "succeeded"
        assert execution["result"]["summary"] == (
            "executed: Implement runner protocol."
        )
        assert execution["result"]["validation"]["status"] == "passed"
    finally:
        _stop(server, thread)


def test_remote_worker_runner_fails_job_on_invalid_executor_output(tmp_path):
    control = ControlPlane(str(tmp_path / "invalid-output.sqlite"), authorizer=_auth())
    queued = control.queue.enqueue({
        "handoff":{
            "repository":"dbrckk/runner-invalid",
            "task":"Return invalid output.",
        },
        "required_capabilities":[],
    })
    executor = tmp_path / "invalid.py"
    executor.write_text(
        "print('not-json')",
        encoding="utf-8",
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
            [sys.executable, str(executor)],
            heartbeat_interval_seconds=0.1,
            executor_timeout_seconds=5,
        )

        outcomes = runner.run(cycles=1, idle_sleep_seconds=0)

        assert outcomes == [{
            "job_key":queued["key"],
            "status":"failed",
            "reason":"executor_invalid_output",
        }]
        assert control.queue.get(queued["key"])["status"] == "failed"
        execution = control.dashboard_store.latest_execution(queued["key"])
        assert execution["status"] == "failed"
        assert execution["error_message"] == "executor_invalid_output"
    finally:
        _stop(server, thread)
