from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .agent_benchmark import AutonomousBenchmark


def _is_postgres(backend) -> bool:
    return backend.__class__.__name__.startswith("Postgres")


def _sql(backend, statement: str) -> str:
    return statement.replace("?", "%s") if _is_postgres(backend) else statement


@dataclass(frozen=True, slots=True)
class AgentPlanningPolicy:
    source: str
    sample_size: int
    max_agents: int
    success_rate: float | None
    execution_failure_rate: float | None
    retries_per_workflow: float | None
    interventions_per_workflow: float | None
    guidance: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "source":self.source,
            "sample_size":self.sample_size,
            "max_agents":self.max_agents,
            "success_rate":self.success_rate,
            "execution_failure_rate":self.execution_failure_rate,
            "retries_per_workflow":self.retries_per_workflow,
            "interventions_per_workflow":self.interventions_per_workflow,
            "guidance":self.guidance,
        }


def planning_policy_for_repository(
    backend,
    repository: str,
    *,
    sample_limit: int = 20,
    min_samples: int = 3,
) -> AgentPlanningPolicy:
    value = str(repository or "").strip()
    if not value:
        raise ValueError("repository is required")
    if int(sample_limit) < 1:
        raise ValueError("sample_limit must be >= 1")
    if int(min_samples) < 1:
        raise ValueError("min_samples must be >= 1")

    with backend.connect() as db:
        rows = db.execute(
            _sql(
                backend,
                """
                SELECT id
                FROM workflows
                WHERE repository=?
                  AND status IN ('succeeded','failed','cancelled')
                ORDER BY updated_at DESC, id DESC
                LIMIT ?
                """,
            ),
            (value, int(sample_limit)),
        ).fetchall()
    workflow_ids = [str(row["id"]) for row in rows]
    if len(workflow_ids) < int(min_samples):
        return AgentPlanningPolicy(
            source="default",
            sample_size=len(workflow_ids),
            max_agents=6,
            success_rate=None,
            execution_failure_rate=None,
            retries_per_workflow=None,
            interventions_per_workflow=None,
            guidance=(
                "Historical evidence is insufficient. Use parallelism only "
                "when tasks are genuinely independent and keep the plan simple."
            ),
        )

    report = AutonomousBenchmark(backend).report(workflow_ids)
    sample_size = int(report["workflow_count"])
    success_rate = float(report["success_rate"])
    failure_rate_raw = report.get("execution_failure_rate")
    failure_rate = (
        float(failure_rate_raw)
        if isinstance(failure_rate_raw, (int, float))
        and not isinstance(failure_rate_raw, bool)
        else None
    )
    retries_per = float(report["retry_executions"]) / sample_size
    interventions_per = (
        float(report["operator_interventions"]) / sample_size
    )

    risky = (
        success_rate < 0.60
        or (failure_rate is not None and failure_rate > 0.25)
        or retries_per > 0.75
        or interventions_per > 0.50
    )
    strong = (
        success_rate >= 0.85
        and (failure_rate is None or failure_rate <= 0.10)
        and retries_per <= 0.25
        and interventions_per <= 0.10
    )

    if risky:
        max_agents = 3
        guidance = (
            "Recent repository history shows elevated execution risk. Prefer "
            "fewer, larger tasks with explicit dependencies; avoid speculative "
            "fan-out and isolate high-risk changes behind validation."
        )
    elif strong:
        max_agents = 6
        guidance = (
            "Recent repository history supports reliable parallel execution. "
            "Use parallel agents when work is independent, while preserving "
            "clear integration ownership and validation."
        )
    else:
        max_agents = 4
        guidance = (
            "Recent repository history is mixed. Use moderate parallelism, "
            "keep dependencies explicit, and avoid splitting tightly coupled "
            "changes across agents."
        )

    return AgentPlanningPolicy(
        source="historical-benchmark",
        sample_size=sample_size,
        max_agents=max_agents,
        success_rate=round(success_rate, 6),
        execution_failure_rate=(
            round(failure_rate, 6)
            if failure_rate is not None
            else None
        ),
        retries_per_workflow=round(retries_per, 6),
        interventions_per_workflow=round(interventions_per, 6),
        guidance=guidance,
    )
