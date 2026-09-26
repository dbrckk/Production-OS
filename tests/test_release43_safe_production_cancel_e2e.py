from __future__ import annotations

import json
import threading
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer

import pytest

from production_os.api_auth import TokenAuthorizer, token_digest
from production_os.control_plane import ControlPlane, make_handler
from production_os.remote_worker import RemoteWorkerClient


def _auth():
    return TokenAuthorizer([
        {"name":"operator","role":"operator","sha256":token_digest("operator")},
        {"name":"viewer","role":"viewer","sha256":token_digest("viewer")},
        {"name":"worker-one","role":"worker","sha256":token_digest("worker-one")},
        {"name":"worker-two","role":"worker","sha256":token_digest("worker-two")},
    ])


def _request(base, path, token, *, method="GET", body=None):
    data = None if body is None else json.dumps(body).encode("utf-8")
    request = urllib.request.Request(
        base + path,
        data=data,
        method=method,
        headers={
            "Authorization":f"Bearer {token}",
            **({"Content-Type":"application/json"} if data is not None else {}),
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            raw = response.read()
            return response.status, json.loads(raw or b"{}")
    except urllib.error.HTTPError as exc:
        raw = exc.read()
        return exc.code, json.loads(raw or b"{}")


def _server(control):
    server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(control))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread, f"http://127.0.0.1:{server.server_port}"


def _stop(server, thread):
    server.shutdown()
    server.server_close()
    thread.join(timeout=2)


@pytest.mark.e2e
def test_release43_cancel_request_survives_worker_and_control_restart_without_reexecution(
    tmp_path,
):
    database = str(tmp_path / "safe-cancel.sqlite")
    first = ControlPlane(database, authorizer=_auth())
    server, thread, base = _server(first)

    try:
        for worker_id in ("worker-one", "worker-two"):
            status, _ = _request(
                base,
                "/v1/workers/register",
                "operator",
                method="POST",
                body={
                    "worker_id":worker_id,
                    "capabilities":[],
                    "max_concurrency":1,
                },
            )
            assert status == 200

        status, launched = _request(
            base,
            "/v1/dashboard/launch",
            "operator",
            method="POST",
            body={
                "repository":"dbrckk/safe-cancel-e2e",
                "instruction":"Run until explicitly cancelled.",
                "request_id":"release43-safe-cancel",
            },
        )
        assert status == 201
        project = launched["project"]
        project_id = project["project_id"]
        workflow_id = project["current_workflow_id"]

        worker_one = RemoteWorkerClient(
            base,
            "worker-one",
            "worker-one",
            [],
            timeout=5,
        )
        claimed = worker_one.claim()
        assert claimed is not None
        job_key = claimed.key
        assert worker_one.ack(job_key)["status"] == "acked"

        status, _ = _request(
            base,
            f"/v1/jobs/{job_key}/telemetry",
            "worker-one",
            method="POST",
            body={
                "worker_id":"worker-one",
                "stage":"implementation",
                "progress":30,
                "usage":{"total_tokens":800},
            },
        )
        assert status == 200

        status, cancelled = _request(
            base,
            f"/v1/managed-projects/{project_id}/cancel",
            "operator",
            method="POST",
            body={"confirm":"CANCEL_ACTIVE_PRODUCTION"},
        )
        assert status == 202
        assert cancelled["status"] == "cancel_requested"

        status, live = _request(
            base,
            f"/v1/dashboard/production-status?project_id={project_id}",
            "viewer",
        )
        assert status == 200
        assert live["runtime"]["phase"] == "cancelling"
        assert live["runtime"]["cancel_requested"] is True

        # The worker disappears before acknowledging cancellation. Persist both
        # stale signals so normal abandoned-execution recovery will requeue it.
        with first.backend.transaction() as db:
            db.execute(
                "UPDATE workers SET last_heartbeat=? WHERE worker_id=?",
                ("2000-01-01T00:00:00+00:00", "worker-one"),
            )
            db.execute(
                """UPDATE job_executions
                   SET last_telemetry_at=?, started_at=?
                   WHERE job_key=? AND status='running'""",
                (
                    "2000-01-01T00:00:00+00:00",
                    "2000-01-01T00:00:00+00:00",
                    job_key,
                ),
            )
    finally:
        _stop(server, thread)

    second = ControlPlane(database, authorizer=_auth())
    server, thread, base = _server(second)
    try:
        worker_two = RemoteWorkerClient(
            base,
            "worker-two",
            "worker-two",
            [],
            timeout=5,
        )

        # Claim polling first recovers the abandoned ACKed job, then observes
        # the persisted cancel request and finalizes cancellation instead of
        # assigning the job to worker two.
        assert worker_two.claim() is None

        job = second.queue.get(job_key)
        assert job["status"] == "cancelled"
        assert job["delivery_attempt"] == 1
        assert job["claimed_by"] is None

        final = second.managed_projects.get(project_id)
        assert final["project_id"] == project_id
        assert final["current_workflow_id"] == workflow_id
        assert final["generation"] == 1
        assert final["status"] == "NEEDS_ATTENTION"
        assert final["current_workflow"]["status"] == "cancelled"

        status, live = _request(
            base,
            f"/v1/dashboard/production-status?project_id={project_id}",
            "viewer",
        )
        assert status == 200
        assert live["runtime"]["phase"] == "needs_attention"
        assert live["runtime"]["cancel_requested"] is False

        control_state = second.dashboard_control.job_state(job_key)
        assert control_state["desired_state"] == "cancel_requested"
        assert control_state["acknowledged_at"]

        events = second.backend.events_after(0, 2000)
        assert any(
            event["event_type"] == "job-recovered"
            and event["task_key"] == job_key
            for event in events
        )
        assert any(
            event["event_type"] == "job-cancelled"
            and event["task_key"] == job_key
            for event in events
        )
    finally:
        _stop(server, thread)
