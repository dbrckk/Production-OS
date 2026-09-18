import json
import threading
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer

from production_os.api_auth import TokenAuthorizer, token_digest
from production_os.control_plane import ControlPlane, make_handler


def request(url, token, payload=None):
    data = None if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST" if payload is not None else "GET",
    )
    with urllib.request.urlopen(req, timeout=3) as response:
        return response.status, json.loads(response.read() or b"{}")


def test_managed_project_http_lifecycle_requires_operator_completion(tmp_path):
    auth = TokenAuthorizer([
        {"name": "viewer", "role": "viewer", "sha256": token_digest("viewer")},
        {"name": "operator", "role": "operator", "sha256": token_digest("operator")},
    ])
    control = ControlPlane(str(tmp_path / "db.sqlite"), authorizer=auth)
    server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(control))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{server.server_port}"
    try:
        status, created = request(base + "/v1/managed-projects", "operator", {
            "repository": "dbrckk/example",
            "final_goal": "Ship a verified playable release",
            "token_budget": 250000,
            "agent_preference": "codex",
        })
        assert status == 201
        project = created["project"]
        assert project["state"] == "RUNNING"

        status, listed = request(base + "/v1/managed-projects", "viewer")
        assert status == 200
        assert [row["workflow_id"] for row in listed["projects"]] == [project["workflow_id"]]

        req = urllib.request.Request(
            base + f"/v1/managed-projects/{project['workflow_id']}/complete",
            data=b"{}",
            headers={
                "Authorization": "Bearer operator",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            urllib.request.urlopen(req, timeout=3)
            assert False, "completion before review must fail"
        except urllib.error.HTTPError as exc:
            assert exc.code == 409

        control.workflows.dispatch_ready(project["workflow_id"])
        control.workflows.record_result(
            project["workflow_id"],
            "goal",
            succeeded=True,
            result={"usage": {"total_tokens": 12345}},
        )

        status, completed = request(
            base + f"/v1/managed-projects/{project['workflow_id']}/complete",
            "operator",
            {},
        )
        assert status == 200
        assert completed["project"]["state"] == "DONE"
        assert completed["project"]["approved_by"] == "operator"
    finally:
        server.shutdown()
        server.server_close()


def test_viewer_cannot_create_managed_project(tmp_path):
    auth = TokenAuthorizer([
        {"name": "viewer", "role": "viewer", "sha256": token_digest("viewer")},
    ])
    control = ControlPlane(str(tmp_path / "db.sqlite"), authorizer=auth)
    server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(control))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        req = urllib.request.Request(
            f"http://127.0.0.1:{server.server_port}/v1/managed-projects",
            data=json.dumps({
                "repository": "dbrckk/example",
                "final_goal": "Finish",
                "token_budget": 1000,
            }).encode(),
            headers={
                "Authorization": "Bearer viewer",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            urllib.request.urlopen(req, timeout=3)
            assert False, "viewer must not create managed projects"
        except urllib.error.HTTPError as exc:
            assert exc.code == 403
    finally:
        server.shutdown()
        server.server_close()
