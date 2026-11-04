"""Tests exercise real loopback HTTP traffic, not a stubbed HTTP client."""
from __future__ import annotations

from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import importlib.util
import io
import json
import os
import threading
from unittest.mock import patch

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "verify-render-cutover.py"
SPEC = importlib.util.spec_from_file_location("verify_render_cutover", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


@contextmanager
def serve(*, ready=True, legacy=False, coldstart=False, redirect=False):
    requests = []

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_args):
            pass

        def send(self, code, data):
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(data).encode())

        def do_GET(self):
            requests.append((self.command, self.path, self.headers.get("Authorization")))
            if redirect:
                self.send_response(302)
                self.send_header("Location", "http://127.0.0.1:1/steal")
                self.end_headers()
                return
            if self.path == "/readyz":
                if legacy and not ready:
                    if coldstart and sum(p == "/readyz" for _, p, _ in requests) >= 2:
                        self.send(200, {"status": "ready", "database": "reachable"})
                    else:
                        self.send(503, {"status": "not_ready"})
                    return
                self.send(200 if ready else 503,
                          {"status": "ready" if ready else "not_ready", "database": "reachable"})
                return
            if self.path == "/healthz":
                self.send(200 if ready else 503, {"status": "healthy" if ready else "not_ready"})
                return
            if self.path == "/v1/workflows":
                self.send(401, {"error": "unauthorized"})
                return
            if self.path == "/v1/stats":
                if self.headers.get("Authorization") == "Bearer operator-value":
                    self.send(200, {"jobs": {"queued": 1}, "workflows": {}})
                else:
                    self.send(403, {"error": "forbidden"})
                return
            self.send(404, {"error": "not found"})

        def do_POST(self):
            requests.append((self.command, self.path, self.headers.get("Authorization")))
            length = int(self.headers.get("Content-Length", 0))
            json.loads(self.rfile.read(length))
            if self.path == "/v1/jobs/availability" and self.headers.get("Authorization") == "Bearer worker-value":
                self.send(200, {"schema_version": "production-os/job-availability/v1", "available": False})
            else:
                self.send(401, {"error": "unauthorized"})

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield "http://127.0.0.1:" + str(server.server_port), requests
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def run(new, old, *, public=False, worker="worker-value", operator="operator-value"):
    args = ["--new-url", new, "--legacy-url", old,
            "--attempts", "2", "--interval", "0", "--timeout", "1"]
    if public:
        args.append("--public-only")
    out = io.StringIO()
    with patch.dict(os.environ, {"PRODUCTION_OS_WORKER_TOKEN": worker,
                              "PRODUCTION_OS_OPERATOR_TOKEN": operator}), patch("sys.stdout", out):
        result = MODULE.main(args)
    output = out.getvalue()
    assert (not worker or worker not in output) and (not operator or operator not in output)
    return result, output


def test_good_credentialed_check_and_legacy_unavailable():
    with serve() as (new, new_requests), serve(ready=False, legacy=True) as (old, old_requests):
        result, output = run(new, old)
    assert result == 0, output
    assert "PASS protected API" in output
    assert "require independent Render suspension proof" in output
    assert any(method == "POST" and path == "/v1/jobs/availability" for method, path, _ in new_requests)
    assert any(path == "/v1/stats" for _, path, _ in new_requests)
    assert all(token is None for _, _, token in old_requests), "old host must never receive secrets"
    assert len(old_requests) == 2, "503 must be re-probed before isolation assessment"


def test_cold_start_legacy_is_detected_after_initial_503():
    with serve() as (new, _), serve(ready=False, legacy=True, coldstart=True) as (old, _):
        result, output = run(new, old)
    assert result == 1
    assert "legacy controller is responsive" in output


def test_new_unavailable_fails_without_sending_tokens():
    with serve(ready=False) as (new, requests), serve(ready=False, legacy=True) as (old, _):
        result, output = run(new, old)
    assert result == 1 and "new Render health" in output
    assert "auth not attempted" in output
    assert all(token is None for _, _, token in requests)


def test_missing_worker_or_operator_is_named_without_secret_values():
    with serve() as (new, _), serve(ready=False, legacy=True) as (old, _):
        result, output = run(new, old, worker="", operator="operator-value")
    assert result == 1 and "PRODUCTION_OS_WORKER_TOKEN" in output
    assert "operator-value" not in output


def test_distinct_token_roles_enforced():
    with serve() as (new, _), serve(ready=False, legacy=True) as (old, _):
        result, output = run(new, old, worker="operator-value", operator="operator-value")
    assert result == 1 and "must be distinct" in output


def test_wrong_worker_token_is_rejected():
    with serve() as (new, _), serve(ready=False, legacy=True) as (old, _):
        result, output = run(new, old, worker="incorrect-private-token")
    assert result == 1 and "worker role authentication failed" in output
    assert "incorrect-private-token" not in output


def test_redirect_is_rejected_without_forwarding_tokens():
    with serve(redirect=True) as (new, requests), serve(ready=False, legacy=True) as (old, _):
        result, output = run(new, old)
    assert result == 1 and "new Render health" in output
    assert all(token is None for _, _, token in requests)


def test_public_only_diagnostic_does_not_claim_authentication():
    with serve() as (new, _), serve(ready=False, legacy=True) as (old, _):
        result, output = run(new, old, public=True)
    assert result == 2
    assert "not a full acceptance test" in output
    assert "INCOMPLETE HTTP-only diagnostic" in output


@pytest.mark.parametrize("origin", [
    "http://example.com", "https://user:password@example.com",
    "https://example.com/path", "https://example.com/#fragment",
    "https://example.com/?key=secret", "https://example.com:bad-port",
])
def test_remote_origin_validation(origin):
    with pytest.raises(ValueError):
        MODULE.validated_origin(origin)


def test_legacy_unknown_network_error_blocks():
    with serve() as (new, _):
        result, output = run(new, "http://127.0.0.1:1")
    assert result == 1 and "isolation cannot be established" in output


def test_verified_auth_contract_against_real_production_os_handler(tmp_path):
    pytest.importorskip("production_os.api_auth")
    from production_os.api_auth import TokenAuthorizer, token_digest
    from production_os.control_plane import ControlPlane, make_handler

    controller = ControlPlane(
        str(tmp_path / "cutover-real.sqlite"),
        authorizer=TokenAuthorizer([
            {"name": "worker", "role": "worker", "sha256": token_digest("worker-value")},
            {"name": "operator", "role": "operator", "sha256": token_digest("operator-value")},
        ]),
    )
    server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(controller))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with serve(ready=False, legacy=True) as (old, _):
            result, output = run("http://127.0.0.1:" + str(server.server_port), old)
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
    assert result == 0, output
    assert "PASS protected API, worker token and operator token validated" in output
