import sqlite3

from production_os.sqlite_backend import SQLiteBackend


REQUIRED_TABLES = {
    "worker_control_state",
    "job_control_state",
    "job_executions",
    "api_usage_events",
    "provider_quota_snapshots",
    "worker_log_events",
    "project_repository_snapshots",
    "project_progress_snapshots",
}

REQUIRED_EXECUTION_COLUMNS = {
    "id",
    "job_key",
    "workflow_id",
    "workflow_task_id",
    "repository",
    "worker_id",
    "attempt",
    "status",
    "started_at",
    "finished_at",
    "duration_seconds",
    "provider",
    "model",
    "api_calls",
    "input_tokens",
    "cached_input_tokens",
    "output_tokens",
    "reasoning_tokens",
    "total_tokens",
    "estimated_cost_usd",
    "pricing_catalog_version",
    "commit_count",
    "commit_shas_json",
    "retry_of_execution_id",
    "error_type",
    "error_message",
    "current_stage",
    "progress_percent",
    "live_usage_json",
    "last_telemetry_at",
    "result_summary_json",
    "created_at",
}


def _table_columns(db: sqlite3.Connection, table: str) -> set[str]:
    return {
        str(row["name"])
        for row in db.execute(f"PRAGMA table_info({table})").fetchall()
    }


def test_schema_v9_has_dashboard_tables_and_execution_columns(tmp_path):
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
        execution_columns = _table_columns(db, "job_executions")

    assert version == "9"
    assert REQUIRED_TABLES <= names
    assert REQUIRED_EXECUTION_COLUMNS <= execution_columns


def test_schema_v9_initialization_is_idempotent(tmp_path):
    path = tmp_path / "production.db"
    SQLiteBackend(path)
    SQLiteBackend(path)

    with SQLiteBackend(path).connect() as db:
        rows = db.execute(
            "SELECT key, value FROM schema_meta WHERE key='schema_version'"
        ).fetchall()

    assert [(row["key"], row["value"]) for row in rows] == [
        ("schema_version", "9")
    ]
