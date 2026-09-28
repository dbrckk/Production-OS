from __future__ import annotations

import json
import statistics
from dataclasses import dataclass
from datetime import datetime
from typing import Any


BENCHMARK_SCHEMA = "production-os/autonomous-benchmark/v1"


def _is_postgres(backend) -> bool:
    return backend.__class__.__name__.startswith("Postgres")


def _sql(backend, statement: str) -> str:
    return statement.replace("?", "%s") if _is_postgres(backend) else statement


def _execute(db, backend, statement: str, params: tuple = ()):
    return db.execute(_sql(backend, statement), params)


def _dt(value: Any) -> datetime | None:
    if value is None:
        return None
    raw = str(value).strip()
    if not raw:
        return None
    if raw.endswith("Z"):
        raw = raw[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(raw)
    except ValueError:
        return None


def _validation_status(result: dict[str, Any]) -> str | None:
    validation = result.get("validation")
    if not isinstance(validation, dict):
        evidence = result.get("evidence")
        validation = (
            evidence.get("validation")
            if isinstance(evidence, dict)
            else None
        )
    if not isinstance(validation, dict):
        return None
    value = str(validation.get("status") or "").strip().lower()
    return value or None


@dataclass(frozen=True, slots=True)
class WorkflowBenchmark:
    workflow_id: str
    repository: str
    status: str
    succeeded: bool
    task_count: int
    succeeded_tasks: int
    failed_tasks: int
    cancelled_tasks: int
    execution_count: int
    failed_executions: int
    retry_executions: int
    validation_failures: int
    validation_passes: int
    operator_interventions: int
    cumulative_execution_seconds: float
    wall_clock_seconds: float | None
    observed_cost_usd: float
    unknown_cost_executions: int
    providers: tuple[str, ...]
    models: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "workflow_id":self.workflow_id,
            "repository":self.repository,
            "status":self.status,
            "succeeded":self.succeeded,
            "task_count":self.task_count,
            "succeeded_tasks":self.succeeded_tasks,
            "failed_tasks":self.failed_tasks,
            "cancelled_tasks":self.cancelled_tasks,
            "execution_count":self.execution_count,
            "failed_executions":self.failed_executions,
            "retry_executions":self.retry_executions,
            "validation_failures":self.validation_failures,
            "validation_passes":self.validation_passes,
            "operator_interventions":self.operator_interventions,
            "cumulative_execution_seconds":self.cumulative_execution_seconds,
            "wall_clock_seconds":self.wall_clock_seconds,
            "observed_cost_usd":self.observed_cost_usd,
            "unknown_cost_executions":self.unknown_cost_executions,
            "providers":list(self.providers),
            "models":list(self.models),
        }


class AutonomousBenchmark:
    def __init__(self, backend):
        self.backend = backend

    def workflow(self, workflow_id: str) -> WorkflowBenchmark:
        with self.backend.connect() as db:
            workflow = _execute(
                db,
                self.backend,
                """
                SELECT id, repository, status, created_at, updated_at
                FROM workflows WHERE id=?
                """,
                (workflow_id,),
            ).fetchone()
            if workflow is None:
                raise KeyError(workflow_id)

            tasks = _execute(
                db,
                self.backend,
                """
                SELECT task_id, status, result_json
                FROM workflow_tasks
                WHERE workflow_id=?
                ORDER BY task_id
                """,
                (workflow_id,),
            ).fetchall()

            executions = _execute(
                db,
                self.backend,
                """
                SELECT job_key, workflow_task_id, status, duration_seconds,
                       provider, model, estimated_cost_usd
                FROM job_executions
                WHERE workflow_id=?
                ORDER BY started_at, id
                """,
                (workflow_id,),
            ).fetchall()

            audit_rows = _execute(
                db,
                self.backend,
                """
                SELECT requested_by
                FROM control_audit_events
                WHERE job_key IN (
                    SELECT DISTINCT job_key
                    FROM job_executions
                    WHERE workflow_id=?
                )
                """,
                (workflow_id,),
            ).fetchall()

        status_counts: dict[str, int] = {}
        validation_failures = 0
        validation_passes = 0
        for row in tasks:
            status = str(row["status"])
            status_counts[status] = status_counts.get(status, 0) + 1
            try:
                result = json.loads(row["result_json"] or "{}")
            except (TypeError, json.JSONDecodeError):
                result = {}
            if not isinstance(result, dict):
                result = {}
            validation = _validation_status(result)
            if validation in {"passed", "pass", "success", "green"}:
                validation_passes += 1
            elif validation in {"failed", "fail", "error", "red"}:
                validation_failures += 1

        execution_count = len(executions)
        task_execution_counts: dict[str, int] = {}
        failed_executions = 0
        cumulative_seconds = 0.0
        observed_cost = 0.0
        unknown_cost = 0
        providers: set[str] = set()
        models: set[str] = set()

        for row in executions:
            task_id = str(row["workflow_task_id"] or "")
            task_execution_counts[task_id] = (
                task_execution_counts.get(task_id, 0) + 1
            )
            if str(row["status"]) != "succeeded":
                failed_executions += 1
            duration = row["duration_seconds"]
            if isinstance(duration, (int, float)) and not isinstance(duration, bool):
                cumulative_seconds += max(0.0, float(duration))
            cost = row["estimated_cost_usd"]
            if isinstance(cost, (int, float)) and not isinstance(cost, bool):
                observed_cost += max(0.0, float(cost))
            else:
                unknown_cost += 1
            if row["provider"]:
                providers.add(str(row["provider"]))
            if row["model"]:
                models.add(str(row["model"]))

        retry_executions = sum(
            max(0, count - 1)
            for task_id, count in task_execution_counts.items()
            if task_id
        )

        operator_interventions = sum(
            1
            for row in audit_rows
            if not str(row["requested_by"] or "").startswith("system:")
        )

        created = _dt(workflow["created_at"])
        updated = _dt(workflow["updated_at"])
        wall_clock = None
        if created is not None and updated is not None:
            try:
                wall_clock = max(0.0, (updated - created).total_seconds())
            except TypeError:
                wall_clock = None

        return WorkflowBenchmark(
            workflow_id=str(workflow["id"]),
            repository=str(workflow["repository"]),
            status=str(workflow["status"]),
            succeeded=str(workflow["status"]) == "succeeded",
            task_count=len(tasks),
            succeeded_tasks=status_counts.get("succeeded", 0),
            failed_tasks=status_counts.get("failed", 0),
            cancelled_tasks=status_counts.get("cancelled", 0),
            execution_count=execution_count,
            failed_executions=failed_executions,
            retry_executions=retry_executions,
            validation_failures=validation_failures,
            validation_passes=validation_passes,
            operator_interventions=operator_interventions,
            cumulative_execution_seconds=round(cumulative_seconds, 6),
            wall_clock_seconds=(
                round(wall_clock, 6)
                if wall_clock is not None
                else None
            ),
            observed_cost_usd=round(observed_cost, 8),
            unknown_cost_executions=unknown_cost,
            providers=tuple(sorted(providers)),
            models=tuple(sorted(models)),
        )

    def report(self, workflow_ids: list[str] | tuple[str, ...]) -> dict[str, Any]:
        ids = list(dict.fromkeys(
            str(value or "").strip()
            for value in workflow_ids
            if str(value or "").strip()
        ))
        if not ids:
            raise ValueError("at least one workflow_id is required")
        rows = [self.workflow(workflow_id) for workflow_id in ids]

        successes = sum(1 for row in rows if row.succeeded)
        total = len(rows)
        wall_clocks = [
            row.wall_clock_seconds
            for row in rows
            if row.wall_clock_seconds is not None
        ]
        costs = [row.observed_cost_usd for row in rows]
        total_executions = sum(row.execution_count for row in rows)
        failed_executions = sum(row.failed_executions for row in rows)

        return {
            "schema_version":BENCHMARK_SCHEMA,
            "workflow_count":total,
            "success_count":successes,
            "success_rate":successes / total,
            "operator_interventions":sum(
                row.operator_interventions
                for row in rows
            ),
            "retry_executions":sum(row.retry_executions for row in rows),
            "validation_failures":sum(
                row.validation_failures
                for row in rows
            ),
            "execution_count":total_executions,
            "failed_executions":failed_executions,
            "execution_failure_rate":(
                failed_executions / total_executions
                if total_executions
                else None
            ),
            "cumulative_execution_seconds":round(sum(
                row.cumulative_execution_seconds
                for row in rows
            ), 6),
            "median_wall_clock_seconds":(
                round(statistics.median(wall_clocks), 6)
                if wall_clocks
                else None
            ),
            "observed_cost_usd":round(sum(costs), 8),
            "unknown_cost_executions":sum(
                row.unknown_cost_executions
                for row in rows
            ),
            "workflows":[row.to_dict() for row in rows],
        }


def compare_reports(
    candidate: dict[str, Any],
    baseline: dict[str, Any],
) -> dict[str, Any]:
    if candidate.get("schema_version") != BENCHMARK_SCHEMA:
        raise ValueError("candidate benchmark schema is invalid")
    if baseline.get("schema_version") != BENCHMARK_SCHEMA:
        raise ValueError("baseline benchmark schema is invalid")

    def delta(name: str):
        left = candidate.get(name)
        right = baseline.get(name)
        if (
            isinstance(left, (int, float))
            and not isinstance(left, bool)
            and isinstance(right, (int, float))
            and not isinstance(right, bool)
        ):
            return round(float(left) - float(right), 12)
        return None

    return {
        "schema_version":"production-os/autonomous-benchmark-comparison/v1",
        "candidate_workflow_count":candidate.get("workflow_count"),
        "baseline_workflow_count":baseline.get("workflow_count"),
        "deltas":{
            "success_rate":delta("success_rate"),
            "operator_interventions":delta("operator_interventions"),
            "retry_executions":delta("retry_executions"),
            "validation_failures":delta("validation_failures"),
            "execution_failure_rate":delta("execution_failure_rate"),
            "cumulative_execution_seconds":delta(
                "cumulative_execution_seconds"
            ),
            "median_wall_clock_seconds":delta(
                "median_wall_clock_seconds"
            ),
            "observed_cost_usd":delta("observed_cost_usd"),
        },
    }
