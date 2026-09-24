from __future__ import annotations

import json
import threading
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer

from production_os.api_auth import TokenAuthorizer, token_digest
from production_os.control_plane import ControlPlane, make_handler

from production_os.dashboard_store import DashboardStore
from production_os.sqlite_backend import SQLiteBackend


def test_control_audit_is_durable_and_newest_first(tmp_path):
    store = DashboardStore(SQLiteBackend(tmp_path / "db.sqlite"))
    first = store.append_control_audit(
        action="pause",
        worker_id="worker-a",
        requested_by="operator:dashboard",
        outcome="accepted",
        job_key=None,
    )
    second = store.append_control_audit(
        action="cancel-current",
        worker_id="worker-a",
        requested_by="operator:dashboard",
        outcome="failed",
        job_key="job-1",
        error_code="job_not_active",
    )
    rows = store.control_audit_events(limit=10)
    assert rows[0]["id"] == second["id"]
    assert rows[1]["id"] == first["id"]
    assert rows[0]["job_key"] == "job-1"
    assert rows[0]["error_code"] == "job_not_active"


def test_control_audit_schema_cannot_store_credentials(tmp_path):
    store = DashboardStore(SQLiteBackend(tmp_path / "db.sqlite"))
    row = store.append_control_audit(
        action="kick",
        worker_id="github-actions-worker",
        requested_by="operator:dashboard",
        outcome="scheduled_fallback",
        job_key=None,
    )
    forbidden = {"token", "authorization", "headers", "secret", "github_token"}
    assert forbidden.isdisjoint(row.keys())


def test_control_audit_limit_is_bounded(tmp_path):
    store = DashboardStore(SQLiteBackend(tmp_path / "db.sqlite"))
    for index in range(5):
        store.append_control_audit(
            action="resume",
            worker_id=f"worker-{index}",
            requested_by="operator:dashboard",
            outcome="accepted",
            job_key=None,
        )
    assert len(store.control_audit_events(limit=2)) == 2
    assert len(store.control_audit_events(limit=100000)) == 5


def _auth():
    return TokenAuthorizer([
        {"name":"operator","role":"operator","sha256":token_digest("operator")},
        {"name":"viewer","role":"viewer","sha256":token_digest("viewer")},
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
        with urllib.request.urlopen(request, timeout=3) as response:
            raw = response.read()
            return response.status, json.loads(raw or b"{}")
    except urllib.error.HTTPError as exc:
        raw = exc.read()
        return exc.code, json.loads(raw or b"{}")


def test_operator_control_api_writes_success_and_failure_audit(tmp_path):
    control = ControlPlane(str(tmp_path / "api.sqlite"), authorizer=_auth())
    control.workers.register("worker-a", ["python"], 1)
    server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(control))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{server.server_port}"
    try:
        status, _ = _request(
            base,
            "/v1/dashboard/workers/worker-a/control",
            "operator",
            method="POST",
            body={"action":"pause"},
        )
        assert status == 202

        status, _ = _request(
            base,
            "/v1/dashboard/workers/worker-a/control",
            "operator",
            method="POST",
            body={"action":"cancel-current","job_key":"missing-job"},
        )
        assert status == 404

        status, payload = _request(
            base,
            "/v1/dashboard/control-audit?limit=10",
            "viewer",
        )
        assert status == 200
        events = payload["events"]
        assert events[0]["action"] == "cancel-current"
        assert events[0]["outcome"] == "failed"
        assert events[0]["error_code"] == "job_not_found"
        assert events[1]["action"] == "pause"
        assert events[1]["outcome"] == "accepted"
        assert events[1]["requested_by"] == "operator:operator"

        status, _ = _request(
            base,
            "/v1/dashboard/control-audit",
            "worker",
        )
        assert status == 403
    finally:
        server.shutdown()
        server.server_close()


def test_release7_schema_is_v13_and_contains_control_audit_and_remediation(tmp_path):
    backend = SQLiteBackend(tmp_path / "schema.sqlite")
    with backend.connect() as db:
        version = db.execute(
            "SELECT value FROM schema_meta WHERE key='schema_version'"
        ).fetchone()["value"]
        table = db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='control_audit_events'"
        ).fetchone()
        remediation = db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='dashboard_remediation_events'"
        ).fetchone()
    assert version == "13"
    assert table["name"] == "control_audit_events"
    assert remediation["name"] == "dashboard_remediation_events"


def test_control_action_remains_traced_if_audit_finalization_fails(tmp_path):
    control = ControlPlane(str(tmp_path / "audit-failure.sqlite"), authorizer=_auth())
    control.workers.register("worker-a", ["python"], 1)
    original = control.dashboard_store.update_control_audit

    def fail_finalize(*args, **kwargs):
        raise RuntimeError("audit finalize unavailable")

    control.dashboard_store.update_control_audit = fail_finalize
    server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(control))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{server.server_port}"
    try:
        status, _ = _request(
            base,
            "/v1/dashboard/workers/worker-a/control",
            "operator",
            method="POST",
            body={"action":"pause"},
        )
        assert status == 202
        assert control.dashboard_control.worker_state("worker-a")["desired_state"] == "paused"
        rows = control.dashboard_store.control_audit_events(limit=1)
        assert rows[0]["action"] == "pause"
        assert rows[0]["outcome"] == "requested"
    finally:
        control.dashboard_store.update_control_audit = original
        server.shutdown()
        server.server_close()


def test_control_audit_does_not_echo_reason_or_credentials(tmp_path):
    control = ControlPlane(str(tmp_path / "secret-audit.sqlite"), authorizer=_auth())
    control.workers.register("worker-a", ["python"], 1)
    server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(control))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{server.server_port}"
    secret = "Bearer super-secret-token"
    try:
        status, _ = _request(
            base,
            "/v1/dashboard/workers/worker-a/control",
            "operator",
            method="POST",
            body={"action":"pause","reason":secret},
        )
        assert status == 202
        status, payload = _request(
            base,
            "/v1/dashboard/control-audit?limit=10",
            "viewer",
        )
        assert status == 200
        serialized = json.dumps(payload, sort_keys=True)
        assert secret not in serialized
        assert "authorization" not in serialized.lower()
        assert "github_token" not in serialized.lower()
    finally:
        server.shutdown()
        server.server_close()
