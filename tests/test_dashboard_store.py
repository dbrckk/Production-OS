import sqlite3

import pytest

from production_os.dashboard_store import DashboardStore
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



@pytest.fixture
def backend(tmp_path):
    return SQLiteBackend(tmp_path / "dashboard-store.db")


def sample_job(*, attempt=1):
    return {
        "key": "job-1",
        "repository": "dbrckk/example",
        "task": "ship",
        "delivery_attempt": attempt,
        "payload": {
            "workflow_id": "wf-1",
            "workflow_task_id": "build",
        },
    }


def test_start_execution_is_idempotent_for_same_delivery_attempt(backend):
    store = DashboardStore(backend)
    job = sample_job(attempt=2)

    first = store.start_execution(
        job,
        "worker-a",
        started_at="2026-09-22T10:00:00+00:00",
    )
    second = store.start_execution(
        job,
        "worker-a",
        started_at="2026-09-22T10:00:10+00:00",
    )

    assert first["id"] == second["id"]
    assert first["attempt"] == 2
    assert first["started_at"] == "2026-09-22T10:00:00+00:00"
    assert store.execution_count("job-1") == 1


def test_live_usage_replaces_cumulative_snapshot_instead_of_summing(backend):
    store = DashboardStore(backend)
    store.start_execution(sample_job(), "worker-a")

    store.update_live_execution(
        "job-1",
        "worker-a",
        {
            "stage": "implementation",
            "progress": 30,
            "usage": {"total_tokens": 100},
        },
    )
    row = store.update_live_execution(
        "job-1",
        "worker-a",
        {
            "stage": "implementation",
            "progress": 45,
            "usage": {"total_tokens": 130},
        },
    )

    assert row["progress_percent"] == 45
    assert row["live_usage"] == {"total_tokens": 130}


def test_live_execution_rejects_wrong_worker_and_invalid_progress(backend):
    store = DashboardStore(backend)
    store.start_execution(sample_job(), "worker-a")

    with pytest.raises(RuntimeError, match="worker mismatch"):
        store.update_live_execution(
            "job-1",
            "worker-b",
            {"progress": 20},
        )

    with pytest.raises(
        ValueError,
        match="progress must be between 0 and 100",
    ):
        store.update_live_execution(
            "job-1",
            "worker-a",
            {"progress": 101},
        )


def test_live_progress_does_not_move_backward_within_stage(backend):
    store = DashboardStore(backend)
    store.start_execution(sample_job(), "worker-a")
    store.update_live_execution(
        "job-1",
        "worker-a",
        {"stage": "implementation", "progress": 60},
    )

    with pytest.raises(ValueError, match="progress cannot move backward"):
        store.update_live_execution(
            "job-1",
            "worker-a",
            {"stage": "implementation", "progress": 40},
        )


def test_live_missing_usage_stays_empty(backend):
    store = DashboardStore(backend)
    store.start_execution(sample_job(), "worker-a")

    row = store.update_live_execution(
        "job-1",
        "worker-a",
        {"stage": "verification", "progress": 10},
    )

    assert row["live_usage"] == {}


def test_finish_execution_is_idempotent_and_deduplicates_commits(backend):
    store = DashboardStore(backend)
    store.start_execution(sample_job(), "worker-a")
    result = {
        "usage": {
            "total_tokens": 900,
            "providers": [
                {
                    "provider": "studio",
                    "model": "model-a",
                    "api_calls": 1,
                    "input_tokens": 700,
                    "cached_input_tokens": 0,
                    "output_tokens": 200,
                    "reasoning_tokens": 0,
                    "total_tokens": 900,
                }
            ],
        },
        "commits": {
            "count": 3,
            "shas": ["a" * 40, "a" * 40, "b" * 40],
        },
        "evidence": {"pipeline_status": "passed"},
    }

    first = store.finish_execution(
        "job-1",
        "worker-a",
        status="succeeded",
        duration_seconds=12.5,
        result=result,
        finished_at="2026-09-22T10:05:00+00:00",
    )
    second = store.finish_execution(
        "job-1",
        "worker-a",
        status="succeeded",
        duration_seconds=12.5,
        result=result,
        finished_at="2026-09-22T10:06:00+00:00",
    )

    assert first["status"] == "succeeded"
    assert second["id"] == first["id"]
    assert second["finished_at"] == first["finished_at"]
    assert first["commit_count"] == 2
    assert first["commit_shas"] == ["a" * 40, "b" * 40]
    events = store.usage_events(repository="dbrckk/example")
    assert len(events) == 1
    assert events[0]["total_tokens"] == 900


def test_store_queries_logs_snapshots_progress_and_quota(backend):
    store = DashboardStore(backend)
    store.start_execution(sample_job(), "worker-a")
    assert store.latest_execution("job-1")["job_key"] == "job-1"
    assert len(store.executions_for_worker("worker-a")) == 1
    assert len(store.executions_for_repository("dbrckk/example")) == 1

    logs = store.append_logs(
        "worker-a",
        [
            {
                "id": "log-1",
                "repository": "dbrckk/example",
                "job_key": "job-1",
                "level": "info",
                "message": "Authorization: Bearer top-secret-token",
                "metadata": {"api_key": "secret-value", "safe": "ok"},
                "created_at": "2026-09-22T10:01:00+00:00",
            }
        ],
    )
    assert logs[0]["message"] == "Authorization: Bearer [REDACTED]"
    assert logs[0]["metadata"]["api_key"] == "[REDACTED]"
    assert store.logs_for_worker("worker-a")[0]["id"] == "log-1"

    repo_snapshot = store.save_repository_snapshot(
        {
            "id": "repo-1",
            "repository": "dbrckk/example",
            "default_branch": "main",
            "production_os_commits": 2,
            "github_commits": 10,
            "captured_at": "2026-09-22T10:02:00+00:00",
        }
    )
    assert repo_snapshot["github_commits"] == 10
    assert store.latest_repository_snapshot(
        "dbrckk/example"
    )["id"] == "repo-1"

    progress = store.save_progress_snapshot(
        {
            "id": "progress-1",
            "repository": "dbrckk/example",
            "production_progress": 50,
            "project_progress": 40,
            "confidence": "medium",
            "calculation_version": "project-progress/v1",
            "captured_at": "2026-09-22T10:03:00+00:00",
        }
    )
    assert progress["confidence"] == "medium"
    assert store.latest_progress_snapshot(
        "dbrckk/example"
    )["id"] == "progress-1"
    assert store.progress_history("dbrckk/example")[0]["id"] == "progress-1"

    quota = store.save_provider_quota_snapshot(
        {
            "id": "quota-1",
            "provider": "omniroute",
            "quota_type": "monthly_tokens",
            "used_value": 100,
            "limit_value": 1000,
            "remaining_value": 900,
            "unit": "tokens",
            "source_status": "authenticated",
            "captured_at": "2026-09-22T10:04:00+00:00",
        }
    )
    assert quota["remaining_value"] == 900
    latest = store.latest_provider_quota_snapshots()
    assert latest == [quota]
