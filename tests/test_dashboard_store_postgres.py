from uuid import uuid4
import os

import pytest

from production_os.postgres_backend import PostgresBackend
from production_os.dashboard_maintenance import storage_maintenance_snapshot


DSN = os.getenv("PRODUCTION_OS_TEST_POSTGRES")

pytestmark = pytest.mark.skipif(
    not DSN,
    reason="PRODUCTION_OS_TEST_POSTGRES not configured",
)

REQUIRED_EXECUTION_COLUMNS = {
    "id", "job_key", "workflow_id", "workflow_task_id", "repository",
    "worker_id", "attempt", "status", "started_at", "finished_at",
    "duration_seconds", "provider", "model", "api_calls",
    "input_tokens", "cached_input_tokens", "output_tokens",
    "reasoning_tokens", "total_tokens", "estimated_cost_usd",
    "pricing_catalog_version", "commit_count", "commit_shas_json",
    "retry_of_execution_id", "error_type", "error_message",
    "current_stage", "progress_percent", "live_usage_json",
    "last_telemetry_at", "result_summary_json", "created_at",
}


def test_postgres_schema_v15_has_execution_columns_control_audit_incidents_remediation_and_managed_projects():
    backend = PostgresBackend(DSN)
    with backend.connect() as db:
        with db.cursor() as cur:
            cur.execute(
                """
                SELECT column_name
                FROM information_schema.columns
                WHERE table_schema = current_schema()
                  AND table_name = 'job_executions'
                """
            )
            columns = {row["column_name"] for row in cur.fetchall()}

    assert backend.SCHEMA_VERSION == 15
    assert REQUIRED_EXECUTION_COLUMNS <= columns
    with backend.connect() as db:
        with db.cursor() as cur:
            cur.execute(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = current_schema()
                  AND table_name = 'control_audit_events'
                """
            )
            audit_table = cur.fetchone()
    assert audit_table["table_name"] == "control_audit_events"
    with backend.connect() as db:
        with db.cursor() as cur:
            cur.execute(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = current_schema()
                  AND table_name = 'dashboard_incidents'
                """
            )
            incident_table = cur.fetchone()
    assert incident_table["table_name"] == "dashboard_incidents"
    with backend.connect() as db:
        with db.cursor() as cur:
            cur.execute(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = current_schema()
                  AND table_name = 'dashboard_remediation_events'
                """
            )
            remediation_table = cur.fetchone()
    assert remediation_table["table_name"] == "dashboard_remediation_events"
    with backend.connect() as db:
        with db.cursor() as cur:
            cur.execute(
                """
                SELECT column_name
                FROM information_schema.columns
                WHERE table_schema = current_schema()
                  AND table_name = 'dashboard_remediation_events'
                """
            )
            remediation_columns = {
                row["column_name"]
                for row in cur.fetchall()
            }
    assert {
        "verification_state",
        "verification_checks",
        "verified_at",
        "resolved_occurrence_count",
        "recurrence_state",
        "recurred_at",
    } <= remediation_columns
    with backend.connect() as db:
        with db.cursor() as cur:
            cur.execute(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = current_schema()
                  AND table_name IN ('managed_projects','managed_project_runs')
                """
            )
            managed_tables = {
                row["table_name"]
                for row in cur.fetchall()
            }
    assert managed_tables == {"managed_projects","managed_project_runs"}


def test_dashboard_service_project_queries_work_on_postgres():
    from production_os.control_plane import ControlPlane
    from production_os.workflow_engine import WorkflowTaskSpec

    control = ControlPlane(DSN)
    repository = "dbrckk/postgres-dashboard"
    workflow = control.workflows.create(
        name="postgres-dashboard",
        repository=repository,
        tasks=[
            WorkflowTaskSpec(
                task_id="build",
                title="Build",
                payload={},
                estimated_minutes=5,
            )
        ],
    )
    payload = control.dashboard.project_workflows(repository)
    assert any(row["id"] == workflow["id"] for row in payload["workflows"])
    progress = control.dashboard.project_progress(repository)
    assert progress["current_workflow_id"] == workflow["id"]


def test_postgres_storage_maintenance_snapshot_has_size_and_no_dsn():
    backend = PostgresBackend(DSN)
    payload = storage_maintenance_snapshot(backend)
    assert payload["backend_kind"] == "postgres"
    assert isinstance(payload["database_size_bytes"], int)
    assert payload["database_size_bytes"] > 0
    names = {row["name"] for row in payload["tables"]}
    assert {
        "worker_logs",
        "api_usage",
        "executions",
        "control_audit",
        "remediations",
        "repository_snapshots",
        "progress_snapshots",
        "events",
    } <= names
    assert "dsn" not in payload
    assert str(DSN) not in str(payload)


def test_postgres_retention_classifies_terminal_and_running_executions_safely():
    backend = PostgresBackend(DSN)
    suffix = uuid4().hex
    old = "2020-01-01T00:00:00+00:00"
    running_id = "retention-running-" + suffix
    terminal_id = "retention-terminal-" + suffix
    with backend.transaction() as db:
        db.execute(
            """INSERT INTO job_executions(
                id, job_key, repository, worker_id, status,
                started_at, finished_at, created_at
            ) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)""",
            (
                running_id,
                "job-running-" + suffix,
                "dbrckk/retention-parity",
                "worker-a",
                "running",
                old,
                None,
                old,
            ),
        )
        db.execute(
            """INSERT INTO job_executions(
                id, job_key, repository, worker_id, status,
                started_at, finished_at, created_at
            ) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)""",
            (
                terminal_id,
                "job-terminal-" + suffix,
                "dbrckk/retention-parity",
                "worker-a",
                "succeeded",
                old,
                old,
                old,
            ),
        )
    try:
        payload = storage_maintenance_snapshot(backend)
        executions = next(
            row for row in payload["tables"]
            if row["name"] == "executions"
        )
        assert executions["prunable_candidate_rows"] >= 1
        assert executions["protected_candidate_rows"] >= 1
    finally:
        with backend.transaction() as db:
            db.execute(
                "DELETE FROM job_executions WHERE id IN (%s,%s)",
                (running_id, terminal_id),
            )
