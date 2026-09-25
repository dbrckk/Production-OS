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

        status, listed = _request(base, "/v1/managed-projects", "viewer")
        assert status == 200
        assert [item["workflow_id"] for item in listed["projects"]] == [
            project["workflow_id"]
        ]

        status, detail = _request(
            base,
            f"/v1/managed-projects/{project['workflow_id']}",
            "viewer",
        )
        assert status == 200
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


def test_managed_project_http_review_instruction_verify_and_complete(tmp_path):
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
        workflow_id = created["project"]["workflow_id"]

        status, _ = _request(
            base,
            f"/v1/managed-projects/{workflow_id}/complete",
            "operator",
            method="POST",
            body={},
        )
        assert status == 409

        control.workflows.record_result(
            workflow_id,
            "goal",
            succeeded=True,
            result={"usage":{"total_tokens":1234}},
        )

        status, resumed = _request(
            base,
            f"/v1/managed-projects/{workflow_id}/instructions",
            "operator",
            method="POST",
            body={"instruction":"Improve mobile controls"},
        )
        assert status == 200
        assert resumed["project"]["state"] == "RUNNING"

        control.workflows.record_result(
            workflow_id,
            "instruction-1",
            succeeded=True,
        )

        status, verifying = _request(
            base,
            f"/v1/managed-projects/{workflow_id}/verify",
            "operator",
            method="POST",
            body={},
        )
        assert status == 200
        assert verifying["project"]["state"] == "RUNNING"

        control.workflows.record_result(
            workflow_id,
            "verification-1",
            succeeded=True,
        )

        status, completed = _request(
            base,
            f"/v1/managed-projects/{workflow_id}/complete",
            "operator",
            method="POST",
            body={},
        )
        assert status == 200
        assert completed["project"]["state"] == "DONE"
        assert completed["project"]["approved_by"] == "operator:operator"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
