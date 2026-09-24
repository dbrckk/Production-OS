from __future__ import annotations

import json
import threading
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer

from production_os.api_auth import TokenAuthorizer, token_digest
from production_os.control_plane import ControlPlane, make_handler


def _post(base, path, token, payload):
    request = urllib.request.Request(
        base + path,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=3) as response:
            raw = response.read()
            return response.status, json.loads(raw or b"{}")
    except urllib.error.HTTPError as exc:
        raw = exc.read()
        return exc.code, json.loads(raw or b"{}")


def _fixture(tmp_path):
    auth = TokenAuthorizer([
        {"name":"viewer","role":"viewer","sha256":token_digest("viewer")},
        {"name":"operator","role":"operator","sha256":token_digest("operator")},
    ])
    control = ControlPlane(str(tmp_path / "db.sqlite"), authorizer=auth)
    control.workers.register("worker-a", ["python"], 1)
    server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(control))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return control, server, f"http://127.0.0.1:{server.server_port}"


def test_worker_control_requires_operator(tmp_path):
    control, server, base = _fixture(tmp_path)
    try:
        status, payload = _post(
            base,
            "/v1/dashboard/workers/worker-a/control",
            "viewer",
            {"action":"pause"},
        )
        assert status == 403
        assert payload["required_role"] == "operator"
    finally:
        server.shutdown(); server.server_close()


def test_pause_returns_requested_state_not_fake_remote_ack(tmp_path):
    control, server, base = _fixture(tmp_path)
    try:
        status, payload = _post(
            base,
            "/v1/dashboard/workers/worker-a/control",
            "operator",
            {"action":"pause","reason":"maintenance"},
        )
        assert status == 202
        assert payload["accepted"] is True
        assert payload["desired_state"] == "paused"
        assert payload["acknowledged"] is False
        assert control.dashboard_control.worker_state("worker-a")["desired_state"] == "paused"
    finally:
        server.shutdown(); server.server_close()


def test_resume_and_drain_map_to_durable_states(tmp_path):
    control, server, base = _fixture(tmp_path)
    try:
        status, resumed = _post(
            base,
            "/v1/dashboard/workers/worker-a/control",
            "operator",
            {"action":"resume"},
        )
        assert status == 202
        assert resumed["desired_state"] == "active"

        status, draining = _post(
            base,
            "/v1/dashboard/workers/worker-a/control",
            "operator",
            {"action":"drain"},
        )
        assert status == 202
        assert draining["desired_state"] == "draining"
    finally:
        server.shutdown(); server.server_close()


def test_invalid_worker_control_action_is_rejected(tmp_path):
    control, server, base = _fixture(tmp_path)
    try:
        status, payload = _post(
            base,
            "/v1/dashboard/workers/worker-a/control",
            "operator",
            {"action":"explode"},
        )
        assert status == 400
        assert payload["error"] == "invalid worker control action"
    finally:
        server.shutdown(); server.server_close()
