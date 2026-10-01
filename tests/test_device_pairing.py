from __future__ import annotations

import json
import threading
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from http.server import ThreadingHTTPServer

import pytest

from production_os.api_auth import TokenAuthorizer, token_digest
from production_os.control_plane import ControlPlane, make_handler


def _auth():
    return TokenAuthorizer([
        {"name":"viewer","role":"viewer","sha256":token_digest("viewer")},
        {"name":"operator","role":"operator","sha256":token_digest("operator")},
    ])


def _server(control):
    server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(control))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread, f"http://127.0.0.1:{server.server_port}"


def _request(base, path, *, token=None, method="GET", body=None):
    data = None if body is None else json.dumps(body).encode("utf-8")
    headers = {}
    if token is not None:
        headers["Authorization"] = "Bearer " + token
    if data is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(
        base + path,
        data=data,
        headers=headers,
        method=method,
    )
    try:
        with urllib.request.urlopen(req, timeout=3) as response:
            return response.status, json.loads(response.read() or b"{}")
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read() or b"{}")


def test_pairing_code_is_single_use_and_creates_revocable_device_session(tmp_path):
    control = ControlPlane(str(tmp_path / "pairing.sqlite"), authorizer=_auth())

    issued = control.device_pairing.issue_pairing_code(
        requested_by="operator:test",
    )
    assert issued["code"].startswith("posp_")
    assert issued["ttl_seconds"] == 600

    exchanged = control.device_pairing.exchange(
        issued["code"],
        device_name="android-phone",
    )
    token = exchanged["session_token"]
    assert token.startswith("posd_")
    principal = control.device_pairing.authenticate(token)
    assert principal is not None
    assert principal.role == "operator"

    with pytest.raises(ValueError, match="invalid or expired"):
        control.device_pairing.exchange(issued["code"])

    sessions = control.device_pairing.sessions()
    assert len(sessions) == 1
    assert sessions[0]["name"] == "android-phone"
    assert "token_sha256" not in sessions[0]

    assert control.device_pairing.revoke(token) is True
    assert control.device_pairing.authenticate(token) is None
    assert control.device_pairing.revoke(token) is False


def test_expired_pairing_code_is_rejected(tmp_path):
    control = ControlPlane(str(tmp_path / "pairing-expired.sqlite"), authorizer=_auth())
    now = datetime(2026, 10, 1, 12, 0, tzinfo=timezone.utc)
    issued = control.device_pairing.issue_pairing_code(
        requested_by="operator:test",
        now=now,
    )

    with pytest.raises(ValueError, match="invalid or expired"):
        control.device_pairing.exchange(
            issued["code"],
            now=now + timedelta(seconds=601),
        )


def test_pairing_storage_never_contains_plaintext_code_or_session_token(tmp_path):
    control = ControlPlane(str(tmp_path / "pairing-hash.sqlite"), authorizer=_auth())
    issued = control.device_pairing.issue_pairing_code(
        requested_by="operator:test",
    )
    exchanged = control.device_pairing.exchange(issued["code"])

    with control.backend.connect() as db:
        code = db.execute(
            "SELECT code_sha256 FROM device_pairing_codes"
        ).fetchone()["code_sha256"]
        session = db.execute(
            "SELECT token_sha256 FROM device_sessions"
        ).fetchone()["token_sha256"]

    assert issued["code"] not in code
    assert exchanged["session_token"] not in session
    assert code == token_digest(issued["code"])
    assert session == token_digest(exchanged["session_token"])


def test_http_pairing_exchange_authenticates_device_and_revokes_current_session(tmp_path):
    control = ControlPlane(str(tmp_path / "pairing-http.sqlite"), authorizer=_auth())
    server, thread, base = _server(control)
    try:
        status, issued = _request(
            base,
            "/v1/dashboard/pairing-codes",
            token="operator",
            method="POST",
        )
        assert status == 201
        assert issued["schema_version"] == "production-os/pairing-code/v1"
        code = issued["code"]

        status, exchanged = _request(
            base,
            "/v1/dashboard/pair",
            method="POST",
            body={"code":code, "device_name":"android-phone"},
        )
        assert status == 201
        assert exchanged["schema_version"] == "production-os/device-session/v1"
        device_token = exchanged["session_token"]

        status, sessions = _request(
            base,
            "/v1/dashboard/device-sessions",
            token=device_token,
        )
        assert status == 200
        assert sessions["sessions"][0]["name"] == "android-phone"
        assert "token_sha256" not in sessions["sessions"][0]

        status, reused = _request(
            base,
            "/v1/dashboard/pair",
            method="POST",
            body={"code":code},
        )
        assert status == 400
        assert reused["error"] == "pairing code invalid or expired"

        status, revoked = _request(
            base,
            "/v1/dashboard/session/revoke",
            token=device_token,
            method="POST",
        )
        assert status == 200
        assert revoked["revoked"] is True

        status, denied = _request(
            base,
            "/v1/dashboard/device-sessions",
            token=device_token,
        )
        assert status == 401
        assert denied["error"] == "unauthorized"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_viewer_cannot_issue_pairing_code_and_unknown_fields_are_rejected(tmp_path):
    control = ControlPlane(str(tmp_path / "pairing-permissions.sqlite"), authorizer=_auth())
    server, thread, base = _server(control)
    try:
        status, denied = _request(
            base,
            "/v1/dashboard/pairing-codes",
            token="viewer",
            method="POST",
        )
        assert status == 403
        assert denied["error"] == "forbidden"

        status, invalid = _request(
            base,
            "/v1/dashboard/pair",
            method="POST",
            body={"code":"posp_invalid", "unexpected":"value"},
        )
        assert status == 400
        assert invalid["error"] == "unknown pairing fields"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
