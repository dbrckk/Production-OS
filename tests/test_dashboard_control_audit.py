from __future__ import annotations

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
