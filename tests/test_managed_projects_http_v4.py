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
    req = urllib.request.Request(
        base + path,
        data=data,
        headers={
            "Authorization":f"Bearer {token}",
            **({"Content-Type":"application/json"} if data is not None else {}),
        },
        method=method,
    )
    try:
        with urllib.request.urlopen(req, timeout=3) as response:
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


def test_operator_can_create_and_viewer_can_list_managed_projects(tmp_path):
    control = ControlPlane(str(tmp_path / "db.sqlite"), authorizer=_auth())
    server, thread, base = _server(control)
    try:
        status, created = _request(
            base,
            "/v1/managed-projects",
            "operator",
            method="POST",
            body={
                "repository":"dbrckk/example",
                "final_goal":"Ship a verified release",
                "token_budget":250000,
                "agent_preference":"codex",
            },
        )
        assert status == 201
        project = created["project"]
        assert project["state"] == "RUNNING"
        assert project["status"] == "ACTIVE"
        assert project["generation"] == 1

        status, listed = _request(base, "/v1/managed-projects", "viewer")
        assert status == 200
        assert [item["project_id"] for item in listed["projects"]] == [
            project["project_id"]
        ]

        status, detail = _request(
            base,
            f"/v1/managed-projects/{project['workflow_id']}",
            "viewer",
        )
        assert status == 200
        assert detail["project"]["project_id"] == project["project_id"]
        assert detail["project"]["final_goal"] == "Ship a verified release"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_viewer_cannot_create_managed_project(tmp_path):
    control = ControlPlane(str(tmp_path / "db.sqlite"), authorizer=_auth())
    server, thread, base = _server(control)
    try:
        status, payload = _request(
            base,
            "/v1/managed-projects",
            "viewer",
            method="POST",
            body={
                "repository":"dbrckk/example",
                "final_goal":"Ship",
                "token_budget":1000,
            },
        )
        assert status == 403
        assert payload["error"] == "forbidden"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_managed_project_http_generations_and_explicit_completion(tmp_path):
    control = ControlPlane(str(tmp_path / "db.sqlite"), authorizer=_auth())
    server, thread, base = _server(control)
    try:
        status, created = _request(
            base,
            "/v1/managed-projects",
            "operator",
            method="POST",
            body={
                "repository":"dbrckk/example",
                "final_goal":"Ship",
                "token_budget":10000,
            },
        )
        assert status == 201
        project = created["project"]
        project_id = project["project_id"]
        first_workflow = project["workflow_id"]

        status, payload = _request(
            base,
            f"/v1/managed-projects/{project_id}/complete",
            "operator",
            method="POST",
            body={"confirm":"MARK_PROJECT_DONE"},
        )
        assert status == 409
        assert "REVIEW_REQUIRED" in payload["error"]

        control.workflows.record_result(
            first_workflow,
            "implementation",
            succeeded=True,
            result={"usage":{"total_tokens":1234}},
        )

        status, resumed = _request(
            base,
            f"/v1/managed-projects/{project_id}/instructions",
            "operator",
            method="POST",
            body={"instruction":"Improve mobile controls"},
        )
        assert status == 200
        assert resumed["project"]["generation"] == 2
        second_workflow = resumed["project"]["workflow_id"]
        assert second_workflow != first_workflow

        control.workflows.record_result(
            second_workflow,
            "implementation",
            succeeded=True,
        )

        status, verifying = _request(
            base,
            f"/v1/managed-projects/{project_id}/verify",
            "operator",
            method="POST",
            body={},
        )
        assert status == 200
        assert verifying["project"]["generation"] == 3
        third_workflow = verifying["project"]["workflow_id"]
        assert third_workflow not in {first_workflow, second_workflow}

        control.workflows.record_result(
            third_workflow,
            "implementation",
            succeeded=True,
        )

        status, payload = _request(
            base,
            f"/v1/managed-projects/{project_id}/complete",
            "operator",
            method="POST",
            body={},
        )
        assert status == 400
        assert "MARK_PROJECT_DONE" in payload["error"]

        status, completed = _request(
            base,
            f"/v1/managed-projects/{project_id}/complete",
            "operator",
            method="POST",
            body={"confirm":"MARK_PROJECT_DONE"},
        )
        assert status == 200
        assert completed["project"]["state"] == "DONE"
        assert completed["project"]["generation"] == 3
        assert completed["project"]["approved_by"] == "operator:operator"
        assert [run["generation"] for run in completed["project"]["runs"]] == [
            1, 2, 3
        ]
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_managed_project_persists_across_control_plane_restart(tmp_path):
    database = str(tmp_path / "managed-restart.sqlite")
    first = ControlPlane(database, authorizer=_auth())
    created = first.managed_projects.create(
        repository="dbrckk/example",
        final_goal="Persist across restart",
        token_budget=5000,
        requested_by="operator:first",
    )
    first_workflow = created["workflow_id"]
    first.workflows.record_result(
        first_workflow,
        "implementation",
        succeeded=True,
        result={"usage":{"total_tokens":77}},
    )
    assert first.managed_projects.get(created["project_id"])["state"] == (
        "REVIEW_REQUIRED"
    )

    second = ControlPlane(database, authorizer=_auth())
    restored = second.managed_projects.get(created["project_id"])
    assert restored["state"] == "REVIEW_REQUIRED"
    assert restored["final_goal"] == "Persist across restart"
    assert restored["usage"]["total_tokens"] == 77

    resumed = second.managed_projects.add_instruction(
        created["project_id"],
        "Continue after restart",
        requested_by="operator:restart",
    )
    assert resumed["generation"] == 2
    assert resumed["workflow_id"] != first_workflow


def test_worker_cannot_read_managed_projects(tmp_path):
    control = ControlPlane(str(tmp_path / "worker-read.sqlite"), authorizer=_auth())
    control.managed_projects.create(
        repository="dbrckk/example",
        final_goal="Ship",
        token_budget=1000,
    )
    server, thread, base = _server(control)
    try:
        status, payload = _request(
            base,
            "/v1/managed-projects",
            "worker",
        )
        assert status == 403
        assert payload["role"] == "worker"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
