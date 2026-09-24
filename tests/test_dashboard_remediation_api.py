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
        {"name":"operator","role":"operator","sha256":token_digest("operator")},
        {"name":"viewer","role":"viewer","sha256":token_digest("viewer")},
        {"name":"worker","role":"worker","sha256":token_digest("worker")},
    ])


def _request(base, path, token, *, method="POST", body=None):
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


def _server(control):
    server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(control))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread, f"http://127.0.0.1:{server.server_port}"


def _queue_incident(control):
    control.queue.enqueue({
        "handoff":{"repository":"dbrckk/example","task":"waiting"},
        "required_capabilities":["python"],
    })
    return next(
        row for row in control.dashboard.incidents()["incidents"]
        if row["code"] == "queue_without_worker"
    )


def test_valid_incident_linked_kick_is_traced(tmp_path):
    control = ControlPlane(str(tmp_path / "remediation-api.sqlite"), authorizer=_auth())
    incident = _queue_incident(control)
    server, thread, base = _server(control)
    try:
        status, payload = _request(
            base,
            "/v1/dashboard/workers/github-actions-worker/control",
            "operator",
            body={"action":"kick","incident_id":incident["id"]},
        )
        assert status == 202
        assert payload["status"] == "scheduled_fallback"
        rows = control.dashboard_store.remediation_events(limit=10)
        assert len(rows) == 1
        assert rows[0]["incident_id"] == incident["id"]
        assert rows[0]["action"] == "kick"
        assert rows[0]["worker_id"] == "github-actions-worker"
        assert rows[0]["outcome"] == "scheduled_fallback"
        assert rows[0]["completed_at"] is not None
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_incident_link_rejects_unsuggested_control_before_mutation(tmp_path):
    control = ControlPlane(str(tmp_path / "remediation-reject.sqlite"), authorizer=_auth())
    incident = _queue_incident(control)
    server, thread, base = _server(control)
    try:
        status, payload = _request(
            base,
            "/v1/dashboard/workers/github-actions-worker/control",
            "operator",
            body={"action":"pause","incident_id":incident["id"]},
        )
        assert status == 409
        assert payload["error"] == "incident remediation is stale or unavailable"
        assert control.dashboard_store.remediation_events(limit=10) == []
        assert control.dashboard_store.control_audit_events(limit=10) == []
        assert (
            control.dashboard_store.get_worker_control("github-actions-worker")
            is None
        )
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_incident_link_rejects_wrong_worker_target(tmp_path):
    control = ControlPlane(str(tmp_path / "remediation-target.sqlite"), authorizer=_auth())
    incident = _queue_incident(control)
    server, thread, base = _server(control)
    try:
        status, _ = _request(
            base,
            "/v1/dashboard/workers/worker-a/control",
            "operator",
            body={"action":"kick","incident_id":incident["id"]},
        )
        assert status == 409
        assert control.dashboard_store.remediation_events(limit=10) == []
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_direct_control_without_incident_remains_compatible(tmp_path):
    control = ControlPlane(str(tmp_path / "direct-control.sqlite"), authorizer=_auth())
    server, thread, base = _server(control)
    try:
        status, payload = _request(
            base,
            "/v1/dashboard/workers/github-actions-worker/control",
            "operator",
            body={"action":"kick"},
        )
        assert status == 202
        assert payload["status"] == "scheduled_fallback"
        assert control.dashboard_store.remediation_events(limit=10) == []
        audit = control.dashboard_store.control_audit_events(limit=10)
        assert len(audit) == 1
        assert audit[0]["action"] == "kick"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_remediation_history_is_viewer_readable_and_worker_forbidden(tmp_path):
    control = ControlPlane(str(tmp_path / "remediation-read.sqlite"), authorizer=_auth())
    incident = _queue_incident(control)
    control.dashboard_store.append_remediation_event(
        incident_id=incident["id"],
        action="kick",
        worker_id="github-actions-worker",
        requested_by="operator:dashboard",
        outcome="scheduled_fallback",
    )
    server, thread, base = _server(control)
    try:
        status, payload = _request(
            base,
            "/v1/dashboard/remediations?limit=10",
            "viewer",
            method="GET",
        )
        assert status == 200
        assert len(payload["events"]) == 1
        assert payload["events"][0]["incident_id"] == incident["id"]

        status, _ = _request(
            base,
            "/v1/dashboard/remediations?limit=10",
            "worker",
            method="GET",
        )
        assert status == 403
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_remediation_history_filters_by_incident_query(tmp_path):
    control = ControlPlane(str(tmp_path / "remediation-filter.sqlite"), authorizer=_auth())
    first = _queue_incident(control)
    control.workers.register("worker-a", ["python"], 1)
    second = control.dashboard_store.upsert_dashboard_incident(
        code="stale_busy_workers",
        severity="medium",
        title="Worker stale",
        message="worker-a",
        target_type="worker",
        target_id="worker-a",
    )
    control.dashboard_store.append_remediation_event(
        incident_id=first["id"],
        action="kick",
        requested_by="operator:dashboard",
    )
    control.dashboard_store.append_remediation_event(
        incident_id=second["id"],
        action="inspect-worker",
        worker_id="worker-a",
        requested_by="operator:dashboard",
    )
    server, thread, base = _server(control)
    try:
        status, payload = _request(
            base,
            "/v1/dashboard/remediations?limit=10&incident_id="+second["id"],
            "viewer",
            method="GET",
        )
        assert status == 200
        assert len(payload["events"]) == 1
        assert payload["events"][0]["incident_id"] == second["id"]
        assert payload["events"][0]["action"] == "inspect-worker"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_remediation_history_verifies_active_then_resolved_incident(tmp_path):
    control = ControlPlane(
        str(tmp_path / "remediation-verification.sqlite"),
        authorizer=_auth(),
    )
    incident = _queue_incident(control)
    event = control.dashboard_store.append_remediation_event(
        incident_id=incident["id"],
        action="kick",
        worker_id="github-actions-worker",
        requested_by="operator:dashboard",
    )
    control.dashboard_store.update_remediation_event(
        event["id"],
        outcome="scheduled_fallback",
    )

    active = control.dashboard.remediation_history(limit=10)["events"][0]
    assert active["verification_state"] == "still_active"
    assert active["verification_checks"] == 1

    control.workers.register("worker-a", ["python"], 1)
    resolved = control.dashboard.remediation_history(limit=10)["events"][0]
    assert resolved["verification_state"] == "resolved"
    assert resolved["verification_checks"] == 2
    assert resolved["verified_at"] is not None


def test_remediation_history_does_not_verify_incomplete_request(tmp_path):
    control = ControlPlane(
        str(tmp_path / "remediation-pending.sqlite"),
        authorizer=_auth(),
    )
    incident = _queue_incident(control)
    event = control.dashboard_store.append_remediation_event(
        incident_id=incident["id"],
        action="kick",
        worker_id="github-actions-worker",
        requested_by="operator:dashboard",
    )
    payload = control.dashboard.remediation_history(limit=10)
    row = next(item for item in payload["events"] if item["id"] == event["id"])
    assert row["verification_state"] == "pending"
    assert row["verification_checks"] == 0
    assert row["verified_at"] is None
