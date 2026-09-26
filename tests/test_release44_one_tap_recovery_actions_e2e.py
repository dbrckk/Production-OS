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
def test_release44_cancel_retest_complete_keeps_same_managed_project(tmp_path):
    control = ControlPlane(
        str(tmp_path / "one-tap-recovery.sqlite"),
        authorizer=_auth(),
    )
    server, thread, base = _server(control)

    try:
        status, launched = _request(
            base,
            "/v1/dashboard/launch",
            "operator",
            method="POST",
            body={
                "repository":"dbrckk/recovery-actions-e2e",
                "instruction":"Build the requested production.",
                "request_id":"release44-recovery-actions",
            },
        )
        assert status == 201
        first = launched["project"]
        project_id = first["project_id"]
        first_workflow = first["current_workflow_id"]
        first_job_key = first["current_workflow"]["tasks"][0]["claimed_job_key"]

        status, cancelled = _request(
            base,
            f"/v1/managed-projects/{project_id}/cancel",
            "operator",
            method="POST",
            body={"confirm":"CANCEL_ACTIVE_PRODUCTION"},
        )
        assert status == 200
        assert cancelled["status"] == "cancelled"
        assert cancelled["project"]["project_id"] == project_id
        assert cancelled["project"]["generation"] == 1
        assert cancelled["project"]["status"] == "NEEDS_ATTENTION"
        assert control.queue.get(first_job_key)["status"] == "cancelled"

        status, retried = _request(
            base,
            f"/v1/managed-projects/{project_id}/verify",
            "operator",
            method="POST",
            body={},
        )
        assert status == 200
        second = retried["project"]
        second_workflow = second["current_workflow_id"]
        assert second["project_id"] == project_id
        assert second["generation"] == 2
        assert second["status"] == "ACTIVE"
        assert second_workflow != first_workflow
        assert [run["generation"] for run in second["runs"]] == [1, 2]
        assert second["runs"][-1]["kind"] == "retest"

        status, _ = _request(
            base,
            "/v1/workers/register",
            "operator",
            method="POST",
            body={
                "worker_id":"worker",
                "capabilities":[],
                "max_concurrency":1,
            },
        )
        assert status == 200

        worker = RemoteWorkerClient(base, "worker", "worker", [], timeout=5)
        job = worker.claim()
        assert job is not None
        assert job.payload["payload"]["workflow_id"] == second_workflow
        assert job.key != first_job_key
        assert worker.ack(job.key)["status"] == "acked"
        assert worker.complete(
            job.key,
            result_payload={
                "summary":"retest passed",
                "usage":{
                    "total_tokens":1500,
                    "runs":1,
                    "agents":{"auto":1},
                },
                "validation":{
                    "status":"passed",
                    "tests":["unit","integration"],
                },
            },
            duration_seconds=6.0,
        )["status"] == "completed"

        status, live = _request(
            base,
            f"/v1/dashboard/production-status?project_id={project_id}",
            "viewer",
        )
        assert status == 200
        assert live["runtime"]["phase"] == "review_required"
        assert live["project"]["project_id"] == project_id
        assert live["project"]["generation"] == 2
        assert live["project"]["outcome"]["validation_status"] == "passed"

        status, done = _request(
            base,
            f"/v1/managed-projects/{project_id}/complete",
            "operator",
            method="POST",
            body={"confirm":"MARK_PROJECT_DONE"},
        )
        assert status == 200
        assert done["project"]["project_id"] == project_id
        assert done["project"]["generation"] == 2
        assert done["project"]["status"] == "DONE"

        status, final = _request(
            base,
            f"/v1/dashboard/production-status?project_id={project_id}",
            "viewer",
        )
        assert status == 200
        assert final["runtime"]["phase"] == "done"
        assert final["project"]["current_workflow_id"] == second_workflow
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
