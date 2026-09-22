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
