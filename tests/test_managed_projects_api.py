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
            return response.status, json.loads(response.read() or b"{}")
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read() or b"{}")


def _server(control):
    server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(control))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread, f"http://127.0.0.1:{server.server_port}"


def test_managed_project_reads_are_viewer_accessible_and_worker_forbidden(tmp_path):
    control = ControlPlane(str(tmp_path / "managed.sqlite"), authorizer=_auth())
    project = control.managed_projects.create(
        repository="dbrckk/api-managed",
        final_goal="Ship it",
        requested_by="operator:test",
    )
    server, thread, base = _server(control)
    try:
        status, payload = _request(
            base,
            "/v1/dashboard/managed-projects?limit=20",
            "viewer",
        )
        assert status == 200
        assert any(row["id"] == project["id"] for row in payload["projects"])

        status, detail = _request(
            base,
            f"/v1/dashboard/managed-projects/{project['id']}",
            "viewer",
        )
        assert status == 200
        assert detail["project"]["id"] == project["id"]
        assert detail["project"]["runs"][0]["generation"] == 1

        status, _ = _request(
            base,
            "/v1/dashboard/managed-projects",
            "worker",
        )
        assert status == 403
    finally:
        server.shutdown(); server.server_close(); thread.join(timeout=2)


def test_managed_project_creation_requires_operator(tmp_path):
    control = ControlPlane(str(tmp_path / "managed.sqlite"), authorizer=_auth())
    server, thread, base = _server(control)
    try:
        status, _ = _request(
            base,
            "/v1/dashboard/managed-projects",
            "viewer",
            method="POST",
            body={
                "repository":"dbrckk/api-managed",
                "final_goal":"Ship it",
            },
        )
        assert status == 403

        status, created = _request(
            base,
            "/v1/dashboard/managed-projects",
            "operator",
            method="POST",
            body={
                "repository":"dbrckk/api-managed",
                "final_goal":"Ship it",
            },
        )
        assert status == 201
        assert created["project"]["status"] == "ACTIVE"
        assert created["project"]["generation"] == 1
    finally:
        server.shutdown(); server.server_close(); thread.join(timeout=2)


def test_instruction_retest_and_completion_api(tmp_path):
    control = ControlPlane(str(tmp_path / "managed.sqlite"), authorizer=_auth())
    project = control.managed_projects.create(
        repository="dbrckk/api-managed",
        final_goal="Ship it",
        requested_by="operator:test",
    )
    control.workflows.record_result(
        project["current_workflow_id"],
        "implementation",
        succeeded=True,
        result={"summary":"done"},
    )
    server, thread, base = _server(control)
    try:
        status, follow = _request(
            base,
            f"/v1/dashboard/managed-projects/{project['id']}/instruction",
            "operator",
            method="POST",
            body={"instruction":"Improve UX"},
        )
        assert status == 200
        assert follow["project"]["generation"] == 2
        assert follow["project"]["runs"][-1]["kind"] == "instruction"

        current = follow["project"]["current_workflow_id"]
        control.workflows.record_result(
            current,
            "implementation",
            succeeded=True,
            result={"summary":"improved"},
        )
        status, retest = _request(
            base,
            f"/v1/dashboard/managed-projects/{project['id']}/retest",
            "operator",
            method="POST",
            body={},
        )
        assert status == 200
        assert retest["project"]["generation"] == 3
        assert retest["project"]["runs"][-1]["kind"] == "retest"

        control.workflows.record_result(
            retest["project"]["current_workflow_id"],
            "implementation",
            succeeded=True,
            result={"summary":"validated"},
        )
        status, _ = _request(
            base,
            f"/v1/dashboard/managed-projects/{project['id']}/complete",
            "operator",
            method="POST",
            body={"confirm":"wrong"},
        )
        assert status == 400

        status, completed = _request(
            base,
            f"/v1/dashboard/managed-projects/{project['id']}/complete",
            "operator",
            method="POST",
            body={"confirm":"MARK_PROJECT_DONE"},
        )
        assert status == 200
        assert completed["project"]["status"] == "DONE"
    finally:
        server.shutdown(); server.server_close(); thread.join(timeout=2)


def test_active_managed_project_rejects_follow_up_api(tmp_path):
    control = ControlPlane(str(tmp_path / "managed.sqlite"), authorizer=_auth())
    project = control.managed_projects.create(
        repository="dbrckk/api-managed",
        final_goal="Ship it",
        requested_by="operator:test",
    )
    server, thread, base = _server(control)
    try:
        status, payload = _request(
            base,
            f"/v1/dashboard/managed-projects/{project['id']}/instruction",
            "operator",
            method="POST",
            body={"instruction":"Too early"},
        )
        assert status == 409
        assert "require review or attention" in payload["error"]
        assert control.managed_projects.get(project["id"])["generation"] == 1
    finally:
        server.shutdown(); server.server_close(); thread.join(timeout=2)
