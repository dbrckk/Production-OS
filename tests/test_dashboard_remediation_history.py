from __future__ import annotations

import sqlite3

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


def test_failed_remediation_is_not_applicable_for_verification(tmp_path):
    store = _store(tmp_path / "failed.sqlite")
    incident = _incident(store)
    event = store.append_remediation_event(
        incident_id=incident["id"],
        action="kick",
        requested_by="operator:dashboard",
    )
    failed = store.update_remediation_event(
        event["id"],
        outcome="failed",
        error_code="github_dispatch_failed",
    )
    assert failed["verification_state"] == "not_applicable"
    assert failed["verified_at"] is not None
    assert failed["verification_checks"] == 0


def test_completed_remediation_tracks_active_then_resolved_incident(tmp_path):
    store = _store(tmp_path / "verification.sqlite")
    incident = _incident(store)
    event = store.append_remediation_event(
        incident_id=incident["id"],
        action="kick",
        requested_by="operator:dashboard",
    )
    store.update_remediation_event(
        event["id"],
        outcome="scheduled_fallback",
    )

    active = store.verify_remediation_events()
    assert active[0]["verification_state"] == "still_active"
    assert active[0]["verification_checks"] == 1
    assert active[0]["verified_at"] is not None

    store.resolve_dashboard_incidents_except(set())
    resolved = store.verify_remediation_events()
    assert resolved[0]["verification_state"] == "resolved"
    assert resolved[0]["verification_checks"] == 2


def test_resolved_verification_never_regresses_after_incident_reopens(tmp_path):
    store = _store(tmp_path / "terminal.sqlite")
    incident = _incident(store)
    event = store.append_remediation_event(
        incident_id=incident["id"],
        action="kick",
        requested_by="operator:dashboard",
    )
    store.update_remediation_event(
        event["id"],
        outcome="scheduled_fallback",
    )
    store.resolve_dashboard_incidents_except(set())
    store.verify_remediation_events()
    before = store.remediation_events(limit=1)[0]
    assert before["verification_state"] == "resolved"

    reopened = store.upsert_dashboard_incident(
        code="queue_without_worker",
        severity="high",
        title="Queue sans worker",
        message="2 jobs en attente",
        target_type="control-plane",
        target_id="global",
    )
    assert reopened["id"] == incident["id"]
    store.verify_remediation_events()
    after = store.remediation_events(limit=1)[0]
    assert after["verification_state"] == "resolved"
    assert after["verification_checks"] == before["verification_checks"]


def test_sqlite_v13_database_is_migrated_additively_to_v15(tmp_path):
    path = tmp_path / "migration.sqlite"
    db = sqlite3.connect(path)
    db.executescript(
        """
        CREATE TABLE schema_meta (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );
        INSERT INTO schema_meta(key, value) VALUES('schema_version', '13');
        CREATE TABLE dashboard_incidents (
            id TEXT PRIMARY KEY,
            dedupe_key TEXT NOT NULL UNIQUE,
            code TEXT NOT NULL,
            severity TEXT NOT NULL,
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            target_type TEXT NOT NULL,
            target_id TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'open',
            occurrence_count INTEGER NOT NULL DEFAULT 1,
            first_seen_at TEXT NOT NULL,
            last_seen_at TEXT NOT NULL,
            acknowledged_by TEXT,
            acknowledged_at TEXT,
            resolved_at TEXT
        );
        CREATE TABLE dashboard_remediation_events (
            id TEXT PRIMARY KEY,
            incident_id TEXT NOT NULL,
            action TEXT NOT NULL,
            worker_id TEXT,
            job_key TEXT,
            requested_by TEXT NOT NULL,
            outcome TEXT NOT NULL,
            error_code TEXT,
            requested_at TEXT NOT NULL,
            completed_at TEXT,
            verification_state TEXT NOT NULL DEFAULT 'pending',
            verification_checks INTEGER NOT NULL DEFAULT 0,
            verified_at TEXT
        );
        INSERT INTO dashboard_incidents(
            id,dedupe_key,code,severity,title,message,
            target_type,target_id,status,occurrence_count,
            first_seen_at,last_seen_at
        ) VALUES(
            'incident-1','queue_without_worker:control-plane:global',
            'queue_without_worker','high','Queue','Waiting',
            'control-plane','global','open',1,
            '2026-09-24T00:00:00+00:00','2026-09-24T00:00:00+00:00'
        );
        INSERT INTO dashboard_remediation_events(
            id,incident_id,action,requested_by,outcome,requested_at,completed_at
        ) VALUES(
            'remediation-1','incident-1','kick','operator:dashboard',
            'scheduled_fallback','2026-09-24T00:01:00+00:00',
            '2026-09-24T00:01:01+00:00'
        );
        """
    )
    db.commit()
    db.close()

    backend = SQLiteBackend(path)
    with backend.connect() as conn:
        version = conn.execute(
            "SELECT value FROM schema_meta WHERE key='schema_version'"
        ).fetchone()["value"]
        columns = {
            row["name"]
            for row in conn.execute(
                "PRAGMA table_info(dashboard_remediation_events)"
            ).fetchall()
        }
        row = conn.execute(
            "SELECT * FROM dashboard_remediation_events WHERE id='remediation-1'"
        ).fetchone()
        managed = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='managed_projects'"
        ).fetchone()
        managed_runs = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='managed_project_runs'"
        ).fetchone()
    assert version == "15"
    assert {
        "verification_state",
        "verification_checks",
        "verified_at",
        "resolved_occurrence_count",
        "recurrence_state",
        "recurred_at",
    } <= columns
    assert row["verification_state"] == "pending"
    assert row["verification_checks"] == 0
    assert row["recurrence_state"] == "not_evaluated"
    assert managed["name"] == "managed_projects"
    assert managed_runs["name"] == "managed_project_runs"


def test_repeated_active_verification_is_idempotent(tmp_path):
    store = _store(tmp_path / "idempotent.sqlite")
    incident = _incident(store)
    event = store.append_remediation_event(
        incident_id=incident["id"],
        action="kick",
        requested_by="operator:dashboard",
    )
    store.update_remediation_event(
        event["id"],
        outcome="scheduled_fallback",
    )

    first = store.verify_remediation_events()
    assert len(first) == 1
    row = store.remediation_events(limit=1)[0]
    assert row["verification_state"] == "still_active"
    assert row["verification_checks"] == 1
    verified_at = row["verified_at"]

    second = store.verify_remediation_events()
    assert second == []
    row = store.remediation_events(limit=1)[0]
    assert row["verification_state"] == "still_active"
    assert row["verification_checks"] == 1
    assert row["verified_at"] == verified_at


def test_resolved_remediation_snapshots_occurrence_and_watches_recurrence(tmp_path):
    store = _store(tmp_path / "recurrence-watch.sqlite")
    incident = _incident(store)
    event = store.append_remediation_event(
        incident_id=incident["id"],
        action="kick",
        requested_by="operator:dashboard",
    )
    store.update_remediation_event(
        event["id"],
        outcome="scheduled_fallback",
    )
    store.resolve_dashboard_incidents_except(set())
    resolved = store.verify_remediation_events()[0]
    assert resolved["verification_state"] == "resolved"
    assert resolved["resolved_occurrence_count"] == 1
    assert resolved["recurrence_state"] == "watching"
    assert resolved["recurred_at"] is None


def test_reopened_incident_marks_resolved_remediation_recurred(tmp_path):
    store = _store(tmp_path / "recurrence-reopen.sqlite")
    incident = _incident(store)
    event = store.append_remediation_event(
        incident_id=incident["id"],
        action="kick",
        requested_by="operator:dashboard",
    )
    store.update_remediation_event(
        event["id"],
        outcome="scheduled_fallback",
    )
    store.resolve_dashboard_incidents_except(set())
    store.verify_remediation_events()

    reopened = store.upsert_dashboard_incident(
        code="queue_without_worker",
        severity="high",
        title="Queue sans worker",
        message="2 jobs en attente",
        target_type="control-plane",
        target_id="global",
    )
    assert reopened["occurrence_count"] == 2
    updated = store.verify_remediation_recurrence()
    assert len(updated) == 1
    assert updated[0]["recurrence_state"] == "recurred"
    assert updated[0]["recurred_at"] is not None


def test_recurrence_watching_is_idempotent_until_reopen(tmp_path):
    store = _store(tmp_path / "recurrence-idempotent.sqlite")
    incident = _incident(store)
    event = store.append_remediation_event(
        incident_id=incident["id"],
        action="kick",
        requested_by="operator:dashboard",
    )
    store.update_remediation_event(
        event["id"],
        outcome="scheduled_fallback",
    )
    store.resolve_dashboard_incidents_except(set())
    store.verify_remediation_events()
    before = store.remediation_events(limit=1)[0]

    assert store.verify_remediation_recurrence() == []
    after = store.remediation_events(limit=1)[0]
    assert after["recurrence_state"] == "watching"
    assert after["recurred_at"] == before["recurred_at"]


def test_recurred_state_is_terminal(tmp_path):
    store = _store(tmp_path / "recurrence-terminal.sqlite")
    incident = _incident(store)
    event = store.append_remediation_event(
        incident_id=incident["id"],
        action="kick",
        requested_by="operator:dashboard",
    )
    store.update_remediation_event(
        event["id"],
        outcome="scheduled_fallback",
    )
    store.resolve_dashboard_incidents_except(set())
    store.verify_remediation_events()
    store.upsert_dashboard_incident(
        code="queue_without_worker",
        severity="high",
        title="Queue sans worker",
        message="2 jobs en attente",
        target_type="control-plane",
        target_id="global",
    )
    first = store.verify_remediation_recurrence()[0]
    assert first["recurrence_state"] == "recurred"
    recurred_at = first["recurred_at"]

    assert store.verify_remediation_recurrence() == []
    after = store.remediation_events(limit=1)[0]
    assert after["recurrence_state"] == "recurred"
    assert after["recurred_at"] == recurred_at
