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


def _store(tmp_path):
    return DashboardStore(SQLiteBackend(tmp_path / "incidents.sqlite"))


def test_incident_upsert_deduplicates_and_counts_occurrences(tmp_path):
    store = _store(tmp_path)
    first = store.upsert_dashboard_incident(
        code="queue_without_worker",
        severity="high",
        title="Queue sans worker",
        message="2 jobs en attente",
        target_type="control-plane",
        target_id="global",
    )
    second = store.upsert_dashboard_incident(
        code="queue_without_worker",
        severity="high",
        title="Queue sans worker",
        message="3 jobs en attente",
        target_type="control-plane",
        target_id="global",
    )
    assert second["id"] == first["id"]
    assert second["occurrence_count"] == 1
    assert second["message"] == "3 jobs en attente"
    rows = store.dashboard_incidents(limit=10)
    assert len(rows) == 1


def test_incident_acknowledgement_is_durable(tmp_path):
    store = _store(tmp_path)
    incident = store.upsert_dashboard_incident(
        code="stale_busy_workers",
        severity="medium",
        title="Worker stale",
        message="worker-a",
        target_type="worker",
        target_id="worker-a",
    )
    acknowledged = store.acknowledge_dashboard_incident(
        incident["id"],
        acknowledged_by="operator:dashboard",
    )
    assert acknowledged["status"] == "acknowledged"
    assert acknowledged["acknowledged_by"] == "operator:dashboard"
    assert acknowledged["acknowledged_at"] is not None


def test_incident_schema_has_no_freeform_secret_payload(tmp_path):
    store = _store(tmp_path)
    row = store.upsert_dashboard_incident(
        code="queue_without_worker",
        severity="high",
        title="Queue",
        message="No worker",
        target_type="control-plane",
        target_id="global",
    )
    forbidden = {"token", "authorization", "headers", "secret", "payload", "metadata"}
    assert forbidden.isdisjoint(row.keys())


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
        with urllib.request.urlopen(request, timeout=3) as response:
            raw = response.read()
            return response.status, json.loads(raw or b"{}")
    except urllib.error.HTTPError as exc:
        raw = exc.read()
        return exc.code, json.loads(raw or b"{}")


def test_incident_api_acknowledges_and_resolves_when_health_clears(tmp_path):
    control = ControlPlane(str(tmp_path / "api-incidents.sqlite"), authorizer=_auth())
    control.queue.enqueue({
        "handoff":{"repository":"dbrckk/example","task":"waiting"},
        "required_capabilities":["python"],
    })
    server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(control))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{server.server_port}"
    try:
        status, payload = _request(
            base,
            "/v1/dashboard/incidents?status=open",
            "viewer",
        )
        assert status == 200
        assert payload["health_status"] == "degraded"
        assert len(payload["incidents"]) == 1
        incident = payload["incidents"][0]
        assert incident["code"] == "queue_without_worker"
        assert incident["status"] == "open"

        status, _ = _request(
            base,
            f"/v1/dashboard/incidents/{incident['id']}/acknowledge",
            "viewer",
            method="POST",
            body={},
        )
        assert status == 403

        status, acknowledged = _request(
            base,
            f"/v1/dashboard/incidents/{incident['id']}/acknowledge",
            "operator",
            method="POST",
            body={},
        )
        assert status == 200
        assert acknowledged["incident"]["status"] == "acknowledged"
        assert acknowledged["incident"]["acknowledged_by"] == "operator:operator"

        status, _ = _request(
            base,
            "/v1/dashboard/incidents",
            "worker",
        )
        assert status == 403

        control.workers.register("worker-a", ["python"], 1)
        status, refreshed = _request(
            base,
            "/v1/dashboard/incidents?status=resolved",
            "viewer",
        )
        assert status == 200
        assert refreshed["health_status"] == "healthy"
        assert len(refreshed["incidents"]) == 1
        assert refreshed["incidents"][0]["id"] == incident["id"]
        assert refreshed["incidents"][0]["status"] == "resolved"
        assert refreshed["incidents"][0]["resolved_at"] is not None
    finally:
        server.shutdown()
        server.server_close()


def test_incident_polling_does_not_inflate_unchanged_occurrence_count(tmp_path):
    control = ControlPlane(str(tmp_path / "polling-incidents.sqlite"), authorizer=_auth())
    control.queue.enqueue({
        "handoff":{"repository":"dbrckk/example","task":"waiting"},
        "required_capabilities":["python"],
    })
    first = control.dashboard.incidents()["incidents"][0]
    second = control.dashboard.incidents()["incidents"][0]
    assert first["id"] == second["id"]
    assert first["occurrence_count"] == 1
    assert second["occurrence_count"] == 1


def test_resolved_incident_reopens_without_stale_acknowledgement(tmp_path):
    store = _store(tmp_path)
    incident = store.upsert_dashboard_incident(
        code="queue_without_worker",
        severity="high",
        title="Queue",
        message="2 jobs",
        target_type="control-plane",
        target_id="global",
    )
    acknowledged = store.acknowledge_dashboard_incident(
        incident["id"],
        acknowledged_by="operator:dashboard",
    )
    assert acknowledged["status"] == "acknowledged"
    store.resolve_dashboard_incidents_except(set())
    resolved = store.dashboard_incidents(limit=1)[0]
    assert resolved["status"] == "resolved"

    reopened = store.upsert_dashboard_incident(
        code="queue_without_worker",
        severity="high",
        title="Queue",
        message="3 jobs",
        target_type="control-plane",
        target_id="global",
    )
    assert reopened["status"] == "open"
    assert reopened["occurrence_count"] == 2
    assert reopened["acknowledged_by"] is None
    assert reopened["acknowledged_at"] is None
    assert reopened["resolved_at"] is None


def test_incident_api_rejects_invalid_status_filter(tmp_path):
    control = ControlPlane(str(tmp_path / "bad-status.sqlite"), authorizer=_auth())
    server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(control))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{server.server_port}"
    try:
        status, payload = _request(
            base,
            "/v1/dashboard/incidents?status=bogus",
            "viewer",
        )
        assert status == 400
        assert payload["error"] == "invalid dashboard query"
    finally:
        server.shutdown()
        server.server_close()


def test_resolved_incident_cannot_be_acknowledged(tmp_path):
    control = ControlPlane(str(tmp_path / "resolved-ack.sqlite"), authorizer=_auth())
    control.queue.enqueue({
        "handoff":{"repository":"dbrckk/example","task":"waiting"},
        "required_capabilities":["python"],
    })
    incident = control.dashboard.incidents()["incidents"][0]
    control.workers.register("worker-a", ["python"], 1)
    resolved = control.dashboard.incidents(status="resolved")["incidents"][0]
    assert resolved["id"] == incident["id"]
    assert resolved["status"] == "resolved"

    server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(control))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{server.server_port}"
    try:
        status, payload = _request(
            base,
            f"/v1/dashboard/incidents/{incident['id']}/acknowledge",
            "operator",
            method="POST",
            body={},
        )
        assert status == 409
        assert "resolved incident cannot be acknowledged" in payload["error"]
        current = control.dashboard_store.dashboard_incidents(limit=1)[0]
        assert current["status"] == "resolved"
    finally:
        server.shutdown()
        server.server_close()


def test_stale_incident_age_updates_do_not_create_new_occurrences(tmp_path):
    store = _store(tmp_path)
    first = store.upsert_dashboard_incident(
        code="stale_busy_workers",
        severity="medium",
        title="Worker stale",
        message="worker-a stale depuis 200.0 s",
        target_type="worker",
        target_id="worker-a",
    )
    second = store.upsert_dashboard_incident(
        code="stale_busy_workers",
        severity="medium",
        title="Worker stale",
        message="worker-a stale depuis 205.0 s",
        target_type="worker",
        target_id="worker-a",
    )
    assert second["id"] == first["id"]
    assert second["occurrence_count"] == 1
    assert second["message"] == "worker-a stale depuis 205.0 s"
