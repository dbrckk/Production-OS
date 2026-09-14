from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class LearningSignal:
    repository: str
    task: str
    executions: int
    promotions: int
    retries: int
    rollbacks: int
    replans: int
    cumulative_delta: int
    average_delta: float
    success_rate: float
    weight: float

    def to_dict(self) -> dict:
        return {
            "repository": self.repository,
            "task": self.task,
            "executions": self.executions,
            "promotions": self.promotions,
            "retries": self.retries,
            "rollbacks": self.rollbacks,
            "replans": self.replans,
            "cumulative_delta": self.cumulative_delta,
            "average_delta": self.average_delta,
            "success_rate": self.success_rate,
            "weight": self.weight,
        }


def build_learning_signals(events: list[dict]) -> list[LearningSignal]:
    grouped: dict[tuple[str, str], list[dict]] = {}
    for event in events:
        repo = str(event.get("repository", ""))
        task = str(event.get("task", ""))
        if not repo:
            continue
        grouped.setdefault((repo, task), []).append(event)

    signals: list[LearningSignal] = []
    for (repo, task), rows in grouped.items():
        promotions = sum(1 for r in rows if r.get("decision") == "promote")
        retries = sum(1 for r in rows if r.get("decision") == "retry")
        rollbacks = sum(1 for r in rows if r.get("decision") == "rollback")
        replans = sum(1 for r in rows if r.get("decision") == "replan")
        deltas = [int(r.get("score_delta", 0)) for r in rows]
        executions = len(rows)
        cumulative = sum(deltas)
        avg = round(cumulative / executions, 2) if executions else 0.0
        success = round(promotions / executions, 3) if executions else 0.0

        weight = (
            success * 20.0
            + max(min(avg, 20), -20) * 0.8
            - retries * 1.5
            - rollbacks * 4.0
            - replans * 1.0
        )
        weight = round(max(-25.0, min(25.0, weight)), 2)

        signals.append(
            LearningSignal(
                repository=repo,
                task=task,
                executions=executions,
                promotions=promotions,
                retries=retries,
                rollbacks=rollbacks,
                replans=replans,
                cumulative_delta=cumulative,
                average_delta=avg,
                success_rate=success,
                weight=weight,
            )
        )

    return sorted(signals, key=lambda s: (-s.weight, -s.executions, s.repository, s.task))


def learning_weight(signals: list[LearningSignal], repository: str, task: str) -> float:
    exact = next((s for s in signals if s.repository == repository and s.task == task), None)
    if exact:
        return exact.weight

    repo_rows = [s for s in signals if s.repository == repository]
    if not repo_rows:
        return 0.0
    return round(sum(s.weight for s in repo_rows) / len(repo_rows), 2)
