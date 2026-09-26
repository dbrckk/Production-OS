from __future__ import annotations

import json
import sys
import threading
import time
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
        assert execution["result_summary"]["summary"] == (
            "executed: Implement runner protocol."
        )
        assert execution["result_summary"]["validation"]["status"] == "passed"
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

def test_remote_worker_runner_acknowledges_cancel_and_terminates_executor(tmp_path):
    control = ControlPlane(str(tmp_path / "cancel.sqlite"), authorizer=_auth())
    queued = control.queue.enqueue({
        "handoff":{
            "repository":"dbrckk/runner-cancel",
            "task":"Sleep until cancelled.",
        },
        "required_capabilities":[],
    })
    executor = tmp_path / "slow.py"
    executor.write_text(
        """
import json, sys, time
json.load(sys.stdin)
time.sleep(30)
print(json.dumps({"status":"succeeded","result":{"summary":"too late"}}))
""".strip(),
        encoding="utf-8",
    )

    server, server_thread, base = _server(control)
    outcomes = []
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
            heartbeat_interval_seconds=0.05,
            executor_timeout_seconds=10,
        )
        worker_thread = threading.Thread(
            target=lambda: outcomes.extend(
                runner.run(cycles=1, idle_sleep_seconds=0)
            ),
            daemon=True,
        )
        worker_thread.start()

        deadline = time.time() + 5
        while time.time() < deadline:
            if control.queue.get(queued["key"])["status"] == "acked":
                break
            time.sleep(0.02)
        assert control.queue.get(queued["key"])["status"] == "acked"

        control.dashboard_control.request_job_cancel(
            queued["key"],
            requested_by="operator:test",
        )
        worker_thread.join(timeout=5)

        assert not worker_thread.is_alive()
        assert outcomes == [{
            "job_key":queued["key"],
            "status":"cancelled",
        }]
        assert control.queue.get(queued["key"])["status"] == "cancelled"
        state = control.dashboard_control.job_state(queued["key"])
        assert state["acknowledged_at"] is not None
        execution = control.dashboard_store.latest_execution(queued["key"])
        assert execution["status"] == "cancelled"
    finally:
        _stop(server, server_thread)

def test_remote_worker_runner_does_not_expose_worker_token_to_executor(
    tmp_path,
    monkeypatch,
):
    control = ControlPlane(str(tmp_path / "secret-env.sqlite"), authorizer=_auth())
    queued = control.queue.enqueue({
        "handoff":{
            "repository":"dbrckk/runner-secret",
            "task":"Do not leak the worker token.",
        },
        "required_capabilities":[],
    })
    monkeypatch.setenv("PRODUCTION_OS_WORKER_TOKEN", "worker-secret")
    executor = tmp_path / "env_check.py"
    executor.write_text(
        """
import json, os, sys
json.load(sys.stdin)
print(json.dumps({
    "status":"succeeded",
    "result":{
        "summary":"checked environment",
        "worker_token_visible":bool(os.getenv("PRODUCTION_OS_WORKER_TOKEN")),
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
            [],
            timeout=5,
        )
        runner = RemoteWorkerRunner(
            client,
            [sys.executable, str(executor)],
            secret_env_names=["PRODUCTION_OS_WORKER_TOKEN"],
            heartbeat_interval_seconds=0.1,
            executor_timeout_seconds=5,
        )

        outcomes = runner.run(cycles=1, idle_sleep_seconds=0)

        assert outcomes[0]["status"] == "completed"
        execution = control.dashboard_store.latest_execution(queued["key"])
        assert execution["result_summary"]["worker_token_visible"] is False
    finally:
        _stop(server, thread)

def test_remote_worker_runner_honors_max_concurrency_with_full_active_set(tmp_path):
    control = ControlPlane(str(tmp_path / "concurrent-runner.sqlite"), authorizer=_auth())
    queued = [
        control.queue.enqueue({
            "handoff":{
                "repository":f"dbrckk/runner-concurrent-{index}",
                "task":f"Concurrent task {index}.",
            },
            "required_capabilities":[],
        })
        for index in (1, 2)
    ]
    markers = tmp_path / "markers"
    markers.mkdir()
    executor = tmp_path / "concurrent_executor.py"
    executor.write_text(
        f"""
import json, pathlib, sys, time
request = json.load(sys.stdin)
key = request["job"]["key"]
markers = pathlib.Path({str(markers)!r})
(markers / (key + ".started")).write_text("started", encoding="utf-8")
deadline = time.time() + 1.5
while len(list(markers.glob("*.started"))) < 2 and time.time() < deadline:
    time.sleep(0.02)
if len(list(markers.glob("*.started"))) < 2:
    raise SystemExit(7)
time.sleep(0.25)
print(json.dumps({{
    "status":"succeeded",
    "result":{{"summary":"concurrent executor completed"}},
}}))
""".strip(),
        encoding="utf-8",
    )

    server, server_thread, base = _server(control)
    outcomes = []
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
            max_concurrency=2,
            heartbeat_interval_seconds=0.05,
            executor_timeout_seconds=2,
        )
        worker_thread = threading.Thread(
            target=lambda: outcomes.extend(
                runner.run(cycles=1, idle_sleep_seconds=0)
            ),
            daemon=True,
        )
        worker_thread.start()

        deadline = time.time() + 1.0
        saw_two_markers = False
        saw_two_active = False
        while time.time() < deadline:
            if len(list(markers.glob("*.started"))) >= 2:
                saw_two_markers = True
            control.workers.load()
            worker = control.workers.workers.get("runner-1")
            if worker is not None and int(worker.active_tasks) == 2:
                saw_two_active = True
            if saw_two_markers and saw_two_active:
                break
            time.sleep(0.02)

        worker_thread.join(timeout=5)

        assert saw_two_markers is True
        assert saw_two_active is True
        assert not worker_thread.is_alive()
        assert len(outcomes) == 2
        assert {row["job_key"] for row in outcomes} == {
            row["key"] for row in queued
        }
        assert all(row["status"] == "completed" for row in outcomes)
        assert all(control.queue.get(row["key"])["status"] == "completed" for row in queued)

        control.workers.load()
        assert control.workers.workers["runner-1"].active_tasks == 0
    finally:
        _stop(server, server_thread)

