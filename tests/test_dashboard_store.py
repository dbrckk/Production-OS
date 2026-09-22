from production_os.sqlite_backend import SQLiteBackend


DASHBOARD_TABLES = {
    "worker_control_state",
    "job_control_state",
    "job_executions",
    "api_usage_events",
    "provider_quota_snapshots",
    "worker_log_events",
    "project_repository_snapshots",
    "project_progress_snapshots",
}


def test_schema_v9_has_dashboard_tables(tmp_path):
    backend = SQLiteBackend(tmp_path / "production.db")
    with backend.connect() as db:
        version = db.execute(
            "SELECT value FROM schema_meta WHERE key='schema_version'"
        ).fetchone()["value"]
        names = {
            row["name"]
            for row in db.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }

    assert version == "9"
    assert DASHBOARD_TABLES <= names


def test_schema_v9_initialization_is_idempotent(tmp_path):
    path = tmp_path / "production.db"
    SQLiteBackend(path)
    SQLiteBackend(path)
    with SQLiteBackend(path).connect() as db:
        count = db.execute(
            "SELECT COUNT(*) AS n FROM schema_meta WHERE key='schema_version'"
        ).fetchone()["n"]
    assert count == 1


def _sample_job():
    return {
        "key": "job-1",
        "repository": "dbrckk/example",
        "task": "ship",
        "delivery_attempt": 2,
        "payload": {"workflow_id": "wf-1", "workflow_task_id": "build"},
    }


def test_start_execution_is_idempotent_for_same_delivery_attempt(tmp_path):
    from production_os.dashboard_store import DashboardStore

    store = DashboardStore(SQLiteBackend(tmp_path / "production.db"))
    first = store.start_execution(
        _sample_job(), "worker-a", started_at="2026-09-22T10:00:00+00:00"
    )
    second = store.start_execution(
        _sample_job(), "worker-a", started_at="2026-09-22T10:00:10+00:00"
    )

    assert first["id"] == second["id"]
    assert first["attempt"] == 2
    assert store.execution_count("job-1") == 1


def test_live_usage_replaces_cumulative_snapshot_instead_of_summing(tmp_path):
    from production_os.dashboard_store import DashboardStore

    store = DashboardStore(SQLiteBackend(tmp_path / "production.db"))
    store.start_execution(_sample_job(), "worker-a")
    store.update_live_execution(
        "job-1", "worker-a", {"progress": 30, "usage": {"total_tokens": 100}}
    )
    row = store.update_live_execution(
        "job-1", "worker-a", {"progress": 45, "usage": {"total_tokens": 130}}
    )

    assert row["progress_percent"] == 45
    assert row["live_usage"]["total_tokens"] == 130


def test_live_execution_rejects_wrong_worker_invalid_and_backward_progress(tmp_path):
    from production_os.dashboard_store import DashboardStore

    store = DashboardStore(SQLiteBackend(tmp_path / "production.db"))
    store.start_execution(_sample_job(), "worker-a")
    with __import__("pytest").raises(PermissionError):
        store.update_live_execution("job-1", "worker-b", {"progress": 10})
    with __import__("pytest").raises(ValueError):
        store.update_live_execution("job-1", "worker-a", {"progress": 101})
    store.update_live_execution("job-1", "worker-a", {"progress": 40})
    with __import__("pytest").raises(ValueError):
        store.update_live_execution("job-1", "worker-a", {"progress": 39})


def test_finish_execution_is_idempotent_and_deduplicates_commits(tmp_path):
    from production_os.dashboard_store import DashboardStore

    store = DashboardStore(SQLiteBackend(tmp_path / "production.db"))
    store.start_execution(_sample_job(), "worker-a")
    result = {
        "usage": {"total_tokens": 25},
        "commits": {"count": 3, "shas": ["a", "a", "b"]},
    }
    first = store.finish_execution(
        "job-1", "worker-a", status="completed", duration_seconds=12.5, result=result
    )
    second = store.finish_execution(
        "job-1", "worker-a", status="completed", duration_seconds=99, result=result
    )
    assert first["id"] == second["id"]
    assert second["commit_count"] == 2
    assert second["commit_shas"] == ["a", "b"]
    assert second["total_tokens"] == 25
