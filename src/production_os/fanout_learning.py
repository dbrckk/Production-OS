from __future__ import annotations

import statistics
from dataclasses import dataclass
from typing import Any

from .agent_benchmark import AutonomousBenchmark


def _is_postgres(backend) -> bool:
    return backend.__class__.__name__.startswith("Postgres")


def _sql(backend, statement: str) -> str:
    return statement.replace("?", "%s") if _is_postgres(backend) else statement


@dataclass(frozen=True, slots=True)
class FanoutBucket:
    max_agents: int
    sample_size: int
    success_rate: float
    retries_per_workflow: float
    interventions_per_workflow: float
    execution_failure_rate: float | None
    median_wall_clock_seconds: float | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "max_agents":self.max_agents,
            "sample_size":self.sample_size,
            "success_rate":self.success_rate,
            "retries_per_workflow":self.retries_per_workflow,
            "interventions_per_workflow":self.interventions_per_workflow,
            "execution_failure_rate":self.execution_failure_rate,
            "median_wall_clock_seconds":self.median_wall_clock_seconds,
        }


@dataclass(frozen=True, slots=True)
class LearnedFanout:
    recommended_max_agents: int
    sample_size: int
    compared_buckets: int
    evidence: tuple[FanoutBucket, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "recommended_max_agents":self.recommended_max_agents,
            "sample_size":self.sample_size,
            "compared_buckets":self.compared_buckets,
            "evidence":[bucket.to_dict() for bucket in self.evidence],
        }


def learn_repository_fanout(
    backend,
    repository: str,
    *,
    sample_limit: int = 60,
    min_samples_per_bucket: int = 3,
) -> LearnedFanout | None:
    value = str(repository or "").strip()
    if not value:
        raise ValueError("repository is required")
    if int(sample_limit) < 1:
        raise ValueError("sample_limit must be >= 1")
    if int(min_samples_per_bucket) < 2:
        raise ValueError("min_samples_per_bucket must be >= 2")

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

    benchmark = AutonomousBenchmark(backend)
    groups: dict[int, list] = {}
    for row in rows:
        item = benchmark.workflow(str(row["id"]))
        fanout = item.planner_max_agents
        if fanout is None or fanout < 2 or fanout > 8:
            continue
        groups.setdefault(int(fanout), []).append(item)

    buckets: list[FanoutBucket] = []
    for fanout, items in sorted(groups.items()):
        if len(items) < int(min_samples_per_bucket):
            continue
        successes = sum(1 for item in items if item.succeeded)
        executions = sum(item.execution_count for item in items)
        failed_executions = sum(item.failed_executions for item in items)
        wall_clocks = [
            item.wall_clock_seconds
            for item in items
            if item.wall_clock_seconds is not None
        ]
        buckets.append(
            FanoutBucket(
                max_agents=fanout,
                sample_size=len(items),
                success_rate=round(successes / len(items), 6),
                retries_per_workflow=round(
                    sum(item.retry_executions for item in items) / len(items),
                    6,
                ),
                interventions_per_workflow=round(
                    sum(item.operator_interventions for item in items) / len(items),
                    6,
                ),
                execution_failure_rate=(
                    round(failed_executions / executions, 6)
                    if executions
                    else None
                ),
                median_wall_clock_seconds=(
                    round(statistics.median(wall_clocks), 6)
                    if wall_clocks
                    else None
                ),
            )
        )

    if len(buckets) < 2:
        return None

    def rank(bucket: FanoutBucket):
        failure_rate = (
            bucket.execution_failure_rate
            if bucket.execution_failure_rate is not None
            else 0.0
        )
        wall_clock = (
            bucket.median_wall_clock_seconds
            if bucket.median_wall_clock_seconds is not None
            else float("inf")
        )
        return (
            -bucket.success_rate,
            bucket.interventions_per_workflow,
            bucket.retries_per_workflow,
            failure_rate,
            wall_clock,
            bucket.max_agents,
        )

    ordered = tuple(sorted(buckets, key=rank))
    winner = ordered[0]
    return LearnedFanout(
        recommended_max_agents=winner.max_agents,
        sample_size=sum(bucket.sample_size for bucket in ordered),
        compared_buckets=len(ordered),
        evidence=ordered,
    )
