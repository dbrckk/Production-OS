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
def test_release32_one_tap_launch_worker_completion_survives_restart(tmp_path):
    database = str(tmp_path / "one-tap-e2e.sqlite")
    first = ControlPlane(database, authorizer=_auth())
    server, thread, base = _server(first)

    repository = "dbrckk/one-tap-e2e"
    instruction = "Implement the requested change, run validation, and report evidence."

    try:
        status, registered = _request(
            base,
            "/v1/workers/register",
            "operator",
            method="POST",
            body={
                "worker_id":"worker-one-tap",
                "capabilities":[],
                "max_concurrency":1,
            },
        )
        assert status == 200
        assert registered["worker"]["worker_id"] == "worker-one-tap"

        status, launched = _request(
            base,
            "/v1/dashboard/launch",
            "operator",
            method="POST",
            body={
                "repository":repository,
                "instruction":instruction,
            },
        )
        assert status == 201
        assert launched["launch"] == {
            "mode":"managed-project",
            "persistent":True,
            "token_budget":30000,
            "agent_preference":"auto",
        }
        project = launched["project"]
        project_id = project["project_id"]
        workflow_id = project["current_workflow_id"]
        assert project["repository"] == repository
        assert project["final_goal"] == instruction
        assert project["status"] == "ACTIVE"
        assert project["generation"] == 1

        worker = RemoteWorkerClient(
            base,
            "worker",
            "worker-one-tap",
            [],
            timeout=5,
        )
        job = worker.claim()
        assert job is not None
        handoff = job.payload["payload"]["handoff"]
        assert handoff["repository"] == repository
        assert handoff["task"] == instruction
        assert handoff["final_goal"] == instruction
        assert handoff["agent_preference"] == "auto"
        assert handoff["token_budget"] == 30000

        assert worker.ack(job.key)["status"] == "acked"
        completed = worker.complete(
            job.key,
            result_payload={
                "summary":"implemented and validated",
                "usage":{
                    "total_tokens":3210,
                    "runs":1,
                    "agents":{"auto":1},
                },
                "validation":{
                    "status":"passed",
                    "tests":["unit","integration"],
                },
            },
            duration_seconds=12.5,
        )
        assert completed["status"] == "completed"

        status, refreshed = _request(
            base,
            f"/v1/managed-projects/{project_id}",
            "viewer",
        )
        assert status == 200
        project_after_worker = refreshed["project"]
        assert project_after_worker["status"] == "REVIEW_REQUIRED"
        assert project_after_worker["state"] == "REVIEW_REQUIRED"
        assert project_after_worker["current_workflow"]["status"] == "succeeded"
        assert project_after_worker["current_workflow_id"] == workflow_id
        assert project_after_worker["usage"]["total_tokens"] == 3210

        status, listed = _request(
            base,
            "/v1/managed-projects",
            "viewer",
        )
        assert status == 200
        assert any(
            row["project_id"] == project_id
            and row["status"] == "REVIEW_REQUIRED"
            for row in listed["projects"]
        )
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

    restarted = ControlPlane(database, authorizer=_auth())
    restored = restarted.managed_projects.get(project_id)
    assert restored["project_id"] == project_id
    assert restored["repository"] == repository
    assert restored["final_goal"] == instruction
    assert restored["status"] == "REVIEW_REQUIRED"
    assert restored["current_workflow_id"] == workflow_id
    assert restored["current_workflow"]["status"] == "succeeded"
    assert restored["usage"]["total_tokens"] == 3210
    assert restored["runs"][0]["kind"] == "initial"
    assert restored["runs"][0]["workflow_id"] == workflow_id
