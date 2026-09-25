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
        {"name":"worker","role":"worker","sha256":token_digest("worker")},
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


@pytest.mark.e2e
def test_release41_live_status_tracks_one_tap_to_review_and_restart(tmp_path):
    database = str(tmp_path / "release41-live.sqlite")
    control = ControlPlane(database, authorizer=_auth())
    server, thread, base = _server(control)

    try:
        status, _ = _request(
            base,
            "/v1/workers/register",
            "operator",
            method="POST",
            body={"worker_id":"worker-live","capabilities":[],"max_concurrency":1},
        )
        assert status == 200

        status, launched = _request(
            base,
            "/v1/dashboard/launch",
            "operator",
            method="POST",
            body={
                "repository":"dbrckk/live-e2e",
                "instruction":"Implement and validate live tracking.",
            },
        )
        assert status == 201
        project_id = launched["project"]["project_id"]
        workflow_id = launched["project"]["current_workflow_id"]

        status, queued = _request(
            base,
            f"/v1/dashboard/production-status?project_id={project_id}",
            "viewer",
        )
        assert status == 200
        assert queued["runtime"]["phase"] == "queued"
        job_key = queued["runtime"]["job_key"]
        assert job_key
        assert queued["runtime"]["queue_position"] == 1

        worker = RemoteWorkerClient(base, "worker", "worker-live", [], timeout=5)
        claimed = worker.claim()
        assert claimed is not None
        assert claimed.key == job_key

        status, claimed_status = _request(
            base,
            f"/v1/dashboard/production-status?project_id={project_id}",
            "viewer",
        )
        assert status == 200
        assert claimed_status["runtime"]["phase"] == "claimed"
        assert claimed_status["runtime"]["worker_id"] == "worker-live"

        assert worker.ack(job_key)["status"] == "acked"

        status, _ = _request(
            base,
            f"/v1/jobs/{job_key}/telemetry",
            "worker",
            method="POST",
            body={
                "worker_id":"worker-live",
                "stage":"validation",
                "progress":67,
                "usage":{"total_tokens":1400},
            },
        )
        assert status == 200

        status, running = _request(
            base,
            f"/v1/dashboard/production-status?project_id={project_id}",
            "viewer",
        )
        assert status == 200
        assert running["runtime"]["phase"] == "running"
        assert running["runtime"]["worker_id"] == "worker-live"
        assert running["runtime"]["stage"] == "validation"
        assert running["runtime"]["progress_percent"] == 67.0
        assert running["runtime"]["attempt"] == 1
        assert running["runtime"]["last_telemetry_at"]

        assert worker.complete(
            job_key,
            result_payload={
                "summary":"Live tracking delivered.",
                "validation":{"status":"passed","tests":["unit","e2e"]},
                "usage":{"total_tokens":2300,"runs":1,"agents":{"auto":1}},
            },
            duration_seconds=11.0,
        )["status"] == "completed"

        status, reviewed = _request(
            base,
            f"/v1/dashboard/production-status?project_id={project_id}",
            "viewer",
        )
        assert status == 200
        assert reviewed["runtime"]["phase"] == "review_required"
        assert reviewed["project"]["current_workflow_id"] == workflow_id
        assert reviewed["project"]["outcome"]["summary"] == "Live tracking delivered."
        assert reviewed["project"]["outcome"]["validation_status"] == "passed"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

    restarted = ControlPlane(database, authorizer=_auth())
    restored = restarted.dashboard.production_status(project_id)
    assert restored["runtime"]["phase"] == "review_required"
    assert restored["project"]["current_workflow_id"] == workflow_id
    assert restored["project"]["outcome"]["summary"] == "Live tracking delivered."
    assert restored["project"]["outcome"]["validation_tests"] == ["unit", "e2e"]
