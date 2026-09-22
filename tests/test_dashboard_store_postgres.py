import os

import pytest

from production_os.dashboard_store import DashboardStore
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



def _reset_dashboard_tables(backend):
    with backend.connect() as db:
        with db.cursor() as cur:
            cur.execute(
                """
                TRUNCATE api_usage_events, worker_log_events,
                    provider_quota_snapshots, project_progress_snapshots,
                    project_repository_snapshots, job_executions
                CASCADE
                """
            )


def test_postgres_dashboard_store_execution_lifecycle_parity():
    backend = PostgresBackend(DSN)
    _reset_dashboard_tables(backend)
    store = DashboardStore(backend)
    job = {
        "key": "pg-job-1",
        "repository": "dbrckk/example",
        "task": "ship",
        "delivery_attempt": 1,
        "payload": {
            "workflow_id": "wf-pg",
            "workflow_task_id": "build",
        },
    }

    started = store.start_execution(job, "worker-pg")
    live = store.update_live_execution(
        "pg-job-1",
        "worker-pg",
        {"stage": "implementation", "progress": 25},
    )
    finished = store.finish_execution(
        "pg-job-1",
        "worker-pg",
        status="succeeded",
        duration_seconds=4.5,
        result={
            "commits": {"shas": ["c" * 40]},
            "usage": {
                "providers": [
                    {
                        "provider": "studio",
                        "model": "model-a",
                        "total_tokens": 50,
                    }
                ]
            },
        },
    )

    assert started["status"] == "running"
    assert live["progress_percent"] == 25
    assert finished["status"] == "succeeded"
    assert finished["commit_shas"] == ["c" * 40]
    assert store.usage_events(repository="dbrckk/example")[0][
        "total_tokens"
    ] == 50
