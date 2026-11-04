"""Real HTTP transport checks for the opt-in GitHub Actions exchange route."""
import json
import threading
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer

from production_os.api_auth import Principal, TokenAuthorizer
from production_os.control_plane import ControlPlane, make_handler
from production_os.github_actions_oidc import OIDCRejected


def call(url, *, bearer=None, payload=None):
    headers = {"Content-Type": "application/json"}
    if bearer is not None:
        headers["Authorization"] = "Bearer " + bearer
    request = urllib.request.Request(
        url, method="POST" if payload is not None else "GET",
        data=None if payload is None else json.dumps(payload).encode(),
        headers=headers,
    )
    try:
        with urllib.request.urlopen(request, timeout=3) as response:
            return response.status, json.loads(response.read())
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read())


def test_oidc_http_exchange_is_opt_in_and_authorizes_only_scoped_roles(tmp_path, monkeypatch):
    monkeypatch.delenv("PRODUCTION_OS_GITHUB_OIDC_ENABLED", raising=False)
    disabled = ControlPlane(str(tmp_path / "disabled.sqlite"), authorizer=TokenAuthorizer([]))
    assert disabled.github_actions_oidc.enabled is False
    # Opt in affects only newly started services; no implicit role grant.
    monkeypatch.setenv("PRODUCTION_OS_GITHUB_OIDC_ENABLED", "true")
    control = ControlPlane(str(tmp_path / "enabled.sqlite"), authorizer=TokenAuthorizer([]))
    assert control.github_actions_oidc.enabled is True
    exchanged = []
    def issue(assertion, *, requested_role=None):
        exchanged.append((assertion, requested_role))
        if assertion != "signed-test-jwt":
            raise OIDCRejected("should never leak validation internals")
        if requested_role not in {"worker", "operator"}:
            raise OIDCRejected("invalid scope")
        return {
            "access_token": "pos-gha-test-session-" + requested_role,
            "token_type": "Bearer",
            "role": requested_role,
            "expires_in": 6300,
        }
    control.github_actions_oidc.exchange = issue
    control.github_actions_oidc.authenticate = lambda token: (
        Principal(name="github-actions", role="worker")
        if token == "pos-gha-test-session-worker" else
        Principal(name="github-actions", role="operator")
        if token == "pos-gha-test-session-operator" else None
    )
    server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(control))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{server.server_port}"
    try:
        status, payload = call(base + "/v1/auth/github-actions", payload={
            "id_token": "signed-test-jwt", "role": "worker",
        })
        assert status == 200 and payload["role"] == "worker"
        assert exchanged == [("signed-test-jwt", "worker")]
        status, stats = call(base + "/v1/stats", bearer=payload["access_token"])
        assert status == 200 and isinstance(stats["jobs"], dict)
        status, denied = call(base + "/v1/dashboard/workers", bearer=payload["access_token"])
        assert status == 403 and denied["error"] == "forbidden"
        status, operator = call(base + "/v1/auth/github-actions", payload={
            "id_token": "signed-test-jwt", "role": "operator",
        })
        assert status == 200
        status, workers = call(base + "/v1/dashboard/workers", bearer=operator["access_token"])
        assert status == 200 and isinstance(workers["workers"], list)
        status, missing = call(base + "/v1/stats")
        assert status == 401 and missing["error"] == "unauthorized"
        status, refused = call(base + "/v1/auth/github-actions", payload={
            "id_token": "attacker-controlled", "role": "operator",
        })
        assert status == 401 and refused == {"error": "unauthorized"}
        status, invalid = call(base + "/v1/auth/github-actions", payload={
            "id_token": "signed-test-jwt", "role": "admin",
        })
        assert status == 400 and invalid["error"] == "invalid request"
    finally:
        server.shutdown()
        server.server_close()
