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


def _client(base):
    return RemoteWorkerClient(
        base,
        "worker-secret",
        "runner-1",
        [],
        timeout=5,
    )


def test_paused_runner_acknowledges_control_and_does_not_claim(tmp_path):
    control = ControlPlane(str(tmp_path / "paused.sqlite"), authorizer=_auth())
    queued = control.queue.enqueue({
        "handoff":{"repository":"dbrckk/paused","task":"stay queued"},
        "required_capabilities":[],
    })
    control.dashboard_control.set_worker_state(
        "runner-1",
        "paused",
        requested_by="operator:test",
    )
    executor = tmp_path / "executor.py"
    executor.write_text(
        "raise SystemExit('paused runner must not execute')",
        encoding="utf-8",
    )
    server, thread, base = _server(control)
    try:
        runner = RemoteWorkerRunner(
            _client(base),
            [sys.executable, str(executor)],
            heartbeat_interval_seconds=0.05,
        )
        assert runner.run(cycles=2, idle_sleep_seconds=0) == []
        assert control.queue.get(queued["key"])["status"] == "queued"
        state = control.dashboard_control.worker_state("runner-1")
        assert state["desired_state"] == "paused"
        assert state["acknowledged_at"] is not None
    finally:
        _stop(server, thread)


def test_draining_runner_finishes_active_job_without_claiming_replacement(tmp_path):
    control = ControlPlane(str(tmp_path / "draining.sqlite"), authorizer=_auth())
    first = control.queue.enqueue({
        "handoff":{"repository":"dbrckk/drain-1","task":"finish me"},
        "required_capabilities":[],
    })
    second = control.queue.enqueue({
        "handoff":{"repository":"dbrckk/drain-2","task":"leave queued"},
        "required_capabilities":[],
    })
    marker = tmp_path / "started"
    executor = tmp_path / "executor.py"
    executor.write_text(
        f"""
import json, pathlib, sys, time
json.load(sys.stdin)
pathlib.Path({str(marker)!r}).write_text("started", encoding="utf-8")
time.sleep(0.25)
print(json.dumps({{"status":"succeeded","result":{{"summary":"drained"}}}}))
""".strip(),
        encoding="utf-8",
    )
    server, server_thread, base = _server(control)
    outcomes = []
    try:
        runner = RemoteWorkerRunner(
            _client(base),
            [sys.executable, str(executor)],
            max_concurrency=1,
            heartbeat_interval_seconds=0.03,
            executor_timeout_seconds=3,
        )
        runner_thread = threading.Thread(
            target=lambda: outcomes.extend(
                runner.run(cycles=3, idle_sleep_seconds=0)
            ),
            daemon=True,
        )
        runner_thread.start()
        deadline = time.time() + 2
        while time.time() < deadline and not marker.exists():
            time.sleep(0.01)
        assert marker.exists()
        control.dashboard_control.set_worker_state(
            "runner-1",
            "draining",
            requested_by="operator:test",
        )
        runner_thread.join(timeout=5)
        assert not runner_thread.is_alive()
        assert outcomes == [{"job_key":first["key"], "status":"completed"}]
        assert control.queue.get(first["key"])["status"] == "completed"
        assert control.queue.get(second["key"])["status"] == "queued"
        state = control.dashboard_control.worker_state("runner-1")
        assert state["desired_state"] == "draining"
        assert state["acknowledged_at"] is not None
    finally:
        _stop(server, server_thread)


def test_resumed_runner_claims_after_pause_acknowledgement(tmp_path):
    control = ControlPlane(str(tmp_path / "resume.sqlite"), authorizer=_auth())
    queued = control.queue.enqueue({
        "handoff":{"repository":"dbrckk/resume","task":"run after resume"},
        "required_capabilities":[],
    })
    control.dashboard_control.set_worker_state(
        "runner-1",
        "paused",
        requested_by="operator:test",
    )
    executor = tmp_path / "executor.py"
    executor.write_text(
        "import json,sys; json.load(sys.stdin); print(json.dumps({'status':'succeeded','result':{'summary':'resumed'}}))",
        encoding="utf-8",
    )
    server, thread, base = _server(control)
    try:
        runner = RemoteWorkerRunner(
            _client(base),
            [sys.executable, str(executor)],
            heartbeat_interval_seconds=0.03,
            executor_timeout_seconds=3,
        )
        assert runner.run(cycles=2, idle_sleep_seconds=0) == []
        assert control.dashboard_control.worker_state("runner-1")["acknowledged_at"] is not None

        control.dashboard_control.set_worker_state(
            "runner-1",
            "active",
            requested_by="operator:test",
        )
        outcomes = runner.run(cycles=2, idle_sleep_seconds=0)
        assert outcomes == [{"job_key":queued["key"], "status":"completed"}]
        state = control.dashboard_control.worker_state("runner-1")
        assert state["desired_state"] == "active"
        assert state["acknowledged_at"] is not None
    finally:
        _stop(server, thread)
