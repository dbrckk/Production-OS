from __future__ import annotations

import json
import threading
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer

from production_os.api_auth import TokenAuthorizer, token_digest
from production_os.control_plane import ControlPlane, make_handler


def _auth():
    return TokenAuthorizer([
        {"name":"viewer","role":"viewer","sha256":token_digest("viewer")},
        {"name":"operator","role":"operator","sha256":token_digest("operator")},
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


def test_release18_managed_project_generations_survive_restart(tmp_path):
    database = str(tmp_path / "managed-e2e.sqlite")
    first = ControlPlane(database, authorizer=_auth())
    server, thread, base = _server(first)
    try:
        status, created = _request(
            base,
            "/v1/managed-projects",
            "operator",
            method="POST",
            body={
                "repository":"dbrckk/e2e-managed",
                "final_goal":"Ship a verified mobile release",
                "token_budget":90000,
                "agent_preference":"codex",
            },
        )
        assert status == 201
        project = created["project"]
        project_id = project["project_id"]
        first_workflow_id = project["workflow_id"]
        assert project["generation"] == 1
        assert project["status"] == "ACTIVE"

        first.workflows.record_result(
            first_workflow_id,
            "implementation",
            succeeded=True,
            result={
                "usage":{
                    "total_tokens":1200,
                    "runs":1,
                    "agents":{"codex":1},
                }
            },
        )
        status, reviewed = _request(
            base,
            f"/v1/managed-projects/{project_id}",
            "viewer",
        )
        assert status == 200
        assert reviewed["project"]["status"] == "REVIEW_REQUIRED"
        first_snapshot = first.workflows.get(first_workflow_id)

        status, instructed = _request(
            base,
            f"/v1/managed-projects/{project_id}/instructions",
            "operator",
            method="POST",
            body={"instruction":"Polish onboarding and mobile controls"},
        )
        assert status == 200
        second = instructed["project"]
        second_workflow_id = second["workflow_id"]
        assert second["generation"] == 2
        assert second_workflow_id != first_workflow_id
        assert first.workflows.get(first_workflow_id) == first_snapshot

        first.workflows.record_result(
            second_workflow_id,
            "implementation",
            succeeded=True,
            result={
                "usage":{
                    "total_tokens":800,
                    "runs":1,
                    "agents":{"codex":1},
                }
            },
        )

        status, retested = _request(
            base,
            f"/v1/managed-projects/{project_id}/verify",
            "operator",
            method="POST",
            body={},
        )
        assert status == 200
        third = retested["project"]
        third_workflow_id = third["workflow_id"]
        assert third["generation"] == 3
        assert third_workflow_id not in {
            first_workflow_id,
            second_workflow_id,
        }

        first.workflows.record_result(
            third_workflow_id,
            "implementation",
            succeeded=True,
            result={
                "usage":{
                    "total_tokens":500,
                    "runs":1,
                    "agents":{"codex":1},
                }
            },
        )

        status, rejected = _request(
            base,
            f"/v1/managed-projects/{project_id}/complete",
            "operator",
            method="POST",
            body={"confirm":"wrong"},
        )
        assert status == 400
        assert "MARK_PROJECT_DONE" in rejected["error"]

        status, completed = _request(
            base,
            f"/v1/managed-projects/{project_id}/complete",
            "operator",
            method="POST",
            body={"confirm":"MARK_PROJECT_DONE"},
        )
        assert status == 200
        final = completed["project"]
        assert final["status"] == "DONE"
        assert final["generation"] == 3
        assert final["approved_by"] == "operator:operator"
        assert final["usage"]["total_tokens"] == 2500
        assert [run["generation"] for run in final["runs"]] == [1, 2, 3]
        assert [run["kind"] for run in final["runs"]] == [
            "initial",
            "instruction",
            "retest",
        ]
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

    second = ControlPlane(database, authorizer=_auth())
    restored = second.managed_projects.get(project_id)
    assert restored["status"] == "DONE"
    assert restored["generation"] == 3
    assert restored["workflow_id"] == third_workflow_id
    assert restored["usage"]["total_tokens"] == 2500
    assert second.workflows.get(first_workflow_id) == first_snapshot
    assert second.workflows.get(second_workflow_id)["status"] == "succeeded"
    assert second.workflows.get(third_workflow_id)["status"] == "succeeded"

    listed = second.managed_projects.list()
    assert [row["project_id"] for row in listed] == [project_id]
