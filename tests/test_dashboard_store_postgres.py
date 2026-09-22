import os

import pytest

from production_os.postgres_backend import PostgresBackend


DSN = os.getenv("PRODUCTION_OS_TEST_POSTGRES")

pytestmark = pytest.mark.skipif(
    not DSN,
    reason="PRODUCTION_OS_TEST_POSTGRES not configured",
)

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


def test_postgres_schema_v9_matches_dashboard_contract():
    backend = PostgresBackend(DSN)

    with backend.connect() as db:
        with db.cursor() as cur:
            cur.execute(
                "SELECT value FROM schema_meta WHERE key='schema_version'"
            )
            version = cur.fetchone()["value"]
            cur.execute(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema='public'
                """
            )
            tables = {row["table_name"] for row in cur.fetchall()}
            cur.execute(
                """
                SELECT column_name
                FROM information_schema.columns
                WHERE table_schema='public'
                  AND table_name='job_executions'
                """
            )
            execution_columns = {
                row["column_name"] for row in cur.fetchall()
            }

    assert version == "9"
    assert REQUIRED_TABLES <= tables
    assert REQUIRED_EXECUTION_COLUMNS <= execution_columns


def test_postgres_schema_v9_initialization_is_idempotent():
    backend = PostgresBackend(DSN)
    PostgresBackend(DSN)

    with backend.connect() as db:
        with db.cursor() as cur:
            cur.execute(
                "SELECT key, value FROM schema_meta WHERE key='schema_version'"
            )
            rows = cur.fetchall()

    assert rows == [{"key": "schema_version", "value": "9"}]
