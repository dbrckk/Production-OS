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
def test_release35_active_worker_survives_control_plane_restart_without_duplication(tmp_path):
    database = str(tmp_path / "restart-active.sqlite")
    first = ControlPlane(database, authorizer=_auth())
    server, thread, base = _server(first)

    try:
        status, _ = _request(
            base,
            "/v1/workers/register",
            "operator",
            method="POST",
            body={"worker_id":"worker-one","capabilities":[],"max_concurrency":1},
        )
        assert status == 200

        status, launched = _request(
            base,
            "/v1/dashboard/launch",
            "operator",
            method="POST",
            body={
                "repository":"dbrckk/restart-active-e2e",
                "instruction":"Complete this production safely across control-plane restart.",
            },
        )
        assert status == 201
        project = launched["project"]
        project_id = project["project_id"]
        workflow_id = project["current_workflow_id"]

        worker = RemoteWorkerClient(base, "worker-one", "worker-one", [], timeout=5)
        claimed = worker.claim()
        assert claimed is not None
        job_key = claimed.key
        assert worker.ack(job_key)["status"] == "acked"

        status, _ = _request(
            base,
            f"/v1/jobs/{job_key}/telemetry",
            "worker-one",
            method="POST",
            body={
                "worker_id":"worker-one",
                "stage":"implementation",
                "progress":35,
                "usage":{"total_tokens":700},
            },
        )
        assert status == 200
    finally:
        _stop(server, thread)

    second = ControlPlane(database, authorizer=_auth())
    restored_job = second.queue.get(job_key)
    restored_execution = second.dashboard_store.latest_execution(job_key)
    restored_project = second.managed_projects.get(project_id)

    assert restored_job["status"] == "acked"
    assert restored_job["claimed_by"] == "worker-one"
    assert restored_job["delivery_attempt"] == 1
    assert restored_execution["status"] == "running"
    assert restored_execution["worker_id"] == "worker-one"
    assert restored_execution["attempt"] == 1
    assert restored_project["status"] == "ACTIVE"
    assert restored_project["current_workflow_id"] == workflow_id

    server, thread, base = _server(second)
    try:
        reconnected = RemoteWorkerClient(
            base,
            "worker-one",
            "worker-one",
            [],
            timeout=5,
        )
        heartbeat = reconnected.heartbeat(
            active_tasks=1,
            active_job_keys=[job_key],
        )
        assert heartbeat["stale_job_keys"] == []

        status, _ = _request(
            base,
            f"/v1/jobs/{job_key}/telemetry",
            "worker-one",
            method="POST",
            body={
                "worker_id":"worker-one",
                "stage":"validation",
                "progress":80,
                "usage":{"total_tokens":1400},
            },
        )
        assert status == 200

        assert reconnected.complete(
            job_key,
            result_payload={
                "summary":"completed after control-plane restart",
                "usage":{
                    "total_tokens":2200,
                    "runs":1,
                    "agents":{"auto":1},
                },
                "validation":{"status":"passed"},
            },
            duration_seconds=15.0,
        )["status"] == "completed"

        final = second.managed_projects.get(project_id)
        assert final["status"] == "REVIEW_REQUIRED"
        assert final["current_workflow_id"] == workflow_id
        assert final["generation"] == 1
        assert final["usage"]["total_tokens"] == 2200
        assert second.dashboard_store.execution_count(job_key) == 1
        assert second.dashboard_store.latest_execution(job_key)["attempt"] == 1
    finally:
        _stop(server, thread)


@pytest.mark.e2e
def test_release35_abandoned_worker_is_recovered_after_restart_with_same_identity(tmp_path):
    database = str(tmp_path / "restart-abandoned.sqlite")
    first = ControlPlane(database, authorizer=_auth())
    server, thread, base = _server(first)

    try:
        for worker_id in ("worker-one", "worker-two"):
            status, _ = _request(
                base,
                "/v1/workers/register",
                "operator",
                method="POST",
                body={"worker_id":worker_id,"capabilities":[],"max_concurrency":1},
            )
            assert status == 200

        status, launched = _request(
            base,
            "/v1/dashboard/launch",
            "operator",
            method="POST",
            body={
                "repository":"dbrckk/restart-abandoned-e2e",
                "instruction":"Recover this production safely if the first worker disappears.",
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
                "progress":50,
                "usage":{"total_tokens":1000},
            },
        )
        assert status == 200

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
    assert second.queue.get(job_key)["status"] == "acked"
    assert second.managed_projects.get(project_id)["current_workflow_id"] == workflow_id

    server, thread, base = _server(second)
    try:
        worker_two = RemoteWorkerClient(
            base,
            "worker-two",
            "worker-two",
            [],
            timeout=5,
        )
        recovered = worker_two.claim()
        assert recovered is not None
        assert recovered.key == job_key
        assert recovered.payload["claimed_by"] == "worker-two"
        assert recovered.payload["delivery_attempt"] == 2

        assert worker_two.ack(job_key)["status"] == "acked"
        assert worker_two.complete(
            job_key,
            result_payload={
                "summary":"recovered after control-plane restart",
                "usage":{
                    "total_tokens":1800,
                    "runs":1,
                    "agents":{"auto":1},
                },
                "validation":{"status":"passed"},
            },
            duration_seconds=10.0,
        )["status"] == "completed"

        final = second.managed_projects.get(project_id)
        assert final["project_id"] == project_id
        assert final["current_workflow_id"] == workflow_id
        assert final["generation"] == 1
        assert final["status"] == "REVIEW_REQUIRED"

        assert second.dashboard_store.execution_count(job_key) == 2
        latest = second.dashboard_store.latest_execution(job_key)
        assert latest["attempt"] == 2
        assert latest["worker_id"] == "worker-two"
        assert latest["status"] == "succeeded"

        with second.backend.connect() as db:
            first_attempt = dict(
                db.execute(
                    """SELECT * FROM job_executions
                       WHERE job_key=? AND attempt=1""",
                    (job_key,),
                ).fetchone()
            )
        assert first_attempt["status"] == "failed"
        assert first_attempt["error_type"] == "worker_abandoned"
    finally:
        _stop(server, thread)
