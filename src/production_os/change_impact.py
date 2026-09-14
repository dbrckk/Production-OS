from __future__ import annotations

import fnmatch
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ImpactDecision:
    task_id: str
    affected: bool
    reason: str

    def to_dict(self) -> dict:
        return {
            "task_id":self.task_id,
            "affected":self.affected,
            "reason":self.reason,
        }


def _matches(path: str, patterns: list[str]) -> bool:
    normalized = path.replace("\\", "/")
    return any(
        fnmatch.fnmatch(normalized, pattern)
        for pattern in patterns
    )


def analyze_change_impact(
    tasks: list[dict],
    changed_paths: list[str],
) -> list[ImpactDecision]:
    """Fail-safe impact analysis with explicit opt-in skipping."""
    by_id = {
        str(task["task_id"]):task
        for task in tasks
    }
    children: dict[str, set[str]] = {
        task_id:set()
        for task_id in by_id
    }
    for task_id, task in by_id.items():
        for dependency in task.get("dependencies", []):
            children.setdefault(str(dependency), set()).add(task_id)

    affected: set[str] = set()
    reasons: dict[str, str] = {}

    for task_id, task in by_id.items():
        payload = dict(task.get("payload") or {})
        impact = dict(payload.get("impact") or {})

        if bool(payload.get("virtual_barrier", False)):
            continue

        if bool(impact.get("always_run", False)):
            affected.add(task_id)
            reasons[task_id] = "always_run"
            continue

        skip_when_unaffected = bool(
            impact.get("skip_when_unaffected", False)
        )
        patterns = [
            str(value)
            for value in impact.get("paths", [])
        ]

        if not skip_when_unaffected:
            affected.add(task_id)
            reasons[task_id] = "fail-safe: skipping not enabled"
            continue

        if not patterns:
            affected.add(task_id)
            reasons[task_id] = "fail-safe: no impact paths declared"
            continue

        matches = [
            path
            for path in changed_paths
            if _matches(path, patterns)
        ]
        if matches:
            affected.add(task_id)
            reasons[task_id] = (
                "matched changed paths: "
                + ", ".join(sorted(matches)[:5])
            )
        else:
            reasons[task_id] = "no changed path matched declared inputs"

    # Any directly affected task makes all downstream work affected.
    queue = list(affected)
    while queue:
        task_id = queue.pop(0)
        for child in children.get(task_id, set()):
            if child in affected:
                continue
            affected.add(child)
            reasons[child] = f"downstream of affected task {task_id}"
            queue.append(child)

    decisions = []
    for task_id in by_id:
        decisions.append(
            ImpactDecision(
                task_id=task_id,
                affected=task_id in affected,
                reason=reasons.get(
                    task_id,
                    "unaffected virtual/derived task",
                ),
            )
        )
    return decisions
