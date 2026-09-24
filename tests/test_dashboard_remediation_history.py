from __future__ import annotations

from production_os.dashboard_store import DashboardStore
from production_os.sqlite_backend import SQLiteBackend


def _store(path):
    return DashboardStore(SQLiteBackend(path))


def _incident(store):
    return store.upsert_dashboard_incident(
        code="queue_without_worker",
        severity="high",
        title="Queue sans worker",
        message="1 job en attente",
        target_type="control-plane",
        target_id="global",
    )


def test_remediation_event_is_durable_across_restart(tmp_path):
    path = tmp_path / "remediation.sqlite"
    first = _store(path)
    incident = _incident(first)
    event = first.append_remediation_event(
        incident_id=incident["id"],
        action="kick",
        worker_id="github-actions-worker",
        requested_by="operator:dashboard",
    )
    assert event["outcome"] == "requested"
    assert event["completed_at"] is None

    second = _store(path)
    rows = second.remediation_events(limit=10)
    assert len(rows) == 1
    assert rows[0]["id"] == event["id"]
    assert rows[0]["incident_id"] == incident["id"]
    assert rows[0]["action"] == "kick"


def test_remediation_event_outcome_can_be_finalized(tmp_path):
    store = _store(tmp_path / "remediation.sqlite")
    incident = _incident(store)
    event = store.append_remediation_event(
        incident_id=incident["id"],
        action="kick",
        worker_id="github-actions-worker",
        requested_by="operator:dashboard",
    )
    done = store.update_remediation_event(
        event["id"],
        outcome="scheduled_fallback",
    )
    assert done["outcome"] == "scheduled_fallback"
    assert done["completed_at"] is not None
    assert done["error_code"] is None


def test_remediation_history_filters_by_incident(tmp_path):
    store = _store(tmp_path / "remediation.sqlite")
    first = _incident(store)
    second = store.upsert_dashboard_incident(
        code="stale_busy_workers",
        severity="medium",
        title="Worker stale",
        message="worker-a",
        target_type="worker",
        target_id="worker-a",
    )
    store.append_remediation_event(
        incident_id=first["id"],
        action="kick",
        requested_by="operator:dashboard",
    )
    store.append_remediation_event(
        incident_id=second["id"],
        action="inspect-worker",
        worker_id="worker-a",
        requested_by="operator:dashboard",
    )
    rows = store.remediation_events(limit=10, incident_id=second["id"])
    assert len(rows) == 1
    assert rows[0]["incident_id"] == second["id"]
    assert rows[0]["action"] == "inspect-worker"


def test_remediation_ledger_has_no_freeform_secret_payload(tmp_path):
    store = _store(tmp_path / "remediation.sqlite")
    incident = _incident(store)
    row = store.append_remediation_event(
        incident_id=incident["id"],
        action="kick",
        worker_id="github-actions-worker",
        requested_by="operator:dashboard",
    )
    forbidden = {
        "token", "authorization", "headers", "secret",
        "payload", "metadata", "reason",
    }
    assert forbidden.isdisjoint(row.keys())
