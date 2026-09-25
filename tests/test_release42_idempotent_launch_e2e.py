from __future__ import annotations

import json
import threading
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer

import pytest

from production_os.api_auth import TokenAuthorizer, token_digest
from production_os.control_plane import ControlPlane, make_handler


def _auth():
    return TokenAuthorizer([
        {"name":"operator","role":"operator","sha256":token_digest("operator")},
        {"name":"viewer","role":"viewer","sha256":token_digest("viewer")},
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
def test_release42_retry_after_control_plane_restart_returns_same_launch(tmp_path):
    database = str(tmp_path / "release42-idempotent.sqlite")
    request_id = "mobile-retry-20260925-abcdef"
    body = {
        "repository":"dbrckk/idempotent-e2e",
        "instruction":"Implement this production exactly once.",
        "request_id":request_id,
    }

    first_control = ControlPlane(database, authorizer=_auth())
    server, thread, base = _server(first_control)
    try:
        status, first = _request(
            base,
            "/v1/dashboard/launch",
            "operator",
            method="POST",
            body=body,
        )
        assert status == 201
        project_id = first["project"]["project_id"]
        workflow_id = first["project"]["current_workflow_id"]
        assert first["launch"]["request_id"] == request_id
        assert first["launch"]["idempotent"] is True
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

    # Model an ambiguous network outcome: the first request committed but the
    # client retries after both browser/server recovery.
    second_control = ControlPlane(database, authorizer=_auth())
    server, thread, base = _server(second_control)
    try:
        status, replay = _request(
            base,
            "/v1/dashboard/launch",
            "operator",
            method="POST",
            body=body,
        )
        assert status == 201
        assert replay["project"]["project_id"] == project_id
        assert replay["project"]["current_workflow_id"] == workflow_id
        assert replay["project"]["generation"] == 1

        with second_control.backend.connect() as db:
            project_count = db.execute(
                "SELECT COUNT(*) AS count FROM managed_projects WHERE repository=?",
                ("dbrckk/idempotent-e2e",),
            ).fetchone()["count"]
            workflow_count = db.execute(
                "SELECT COUNT(*) AS count FROM workflows WHERE repository=?",
                ("dbrckk/idempotent-e2e",),
            ).fetchone()["count"]
            job_count = db.execute(
                "SELECT COUNT(*) AS count FROM jobs WHERE repository=?",
                ("dbrckk/idempotent-e2e",),
            ).fetchone()["count"]
        assert project_count == 1
        assert workflow_count == 1
        assert job_count == 1
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
