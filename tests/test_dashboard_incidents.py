from __future__ import annotations

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
    assert second["occurrence_count"] == 2
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
