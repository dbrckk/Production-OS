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


def _normalize_path(path: str) -> str:
    normalized = path.replace("\\", "/")
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized


def _matches(path: str, patterns: list[str]) -> bool:
    normalized = _normalize_path(path)
    return any(
        fnmatch.fnmatch(normalized, pattern)
        for pattern in patterns
    )


def _direct_match(
    changed_paths: list[str],
    include_patterns: list[str],
    exclude_patterns: list[str],
) -> list[str]:
    matches: list[str] = []
    for raw_path in changed_paths:
        path = _normalize_path(raw_path)
        if not _matches(path, include_patterns):
            continue
        if exclude_patterns and _matches(path, exclude_patterns):
            continue
        matches.append(path)
    return sorted(set(matches))


def analyze_change_impact(
    tasks: list[dict],
    changed_paths: list[str],
) -> list[ImpactDecision]:
    """Fail-safe impact analysis with explicit opt-in skipping.

    Empty or unknown change sets execute by default. A task may explicitly
    opt into empty-change skipping with allow_empty_changes.
    """
    normalized_changes = [
        _normalize_path(str(path))
        for path in changed_paths
        if str(path).strip()
    ]

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
            if str(value).strip()
        ]
        exclude_patterns = [
            str(value)
            for value in impact.get("exclude_paths", [])
            if str(value).strip()
        ]

        if not skip_when_unaffected:
            affected.add(task_id)
            reasons[task_id] = "fail-safe: skipping not enabled"
            continue

        if not patterns:
            affected.add(task_id)
            reasons[task_id] = "fail-safe: no impact paths declared"
            continue

        if (
            not normalized_changes
            and not bool(impact.get("allow_empty_changes", False))
        ):
            affected.add(task_id)
            reasons[task_id] = "fail-safe: no changed paths supplied"
            continue

        matches = _direct_match(
            normalized_changes,
            patterns,
            exclude_patterns,
        )
        if matches:
            affected.add(task_id)
            reasons[task_id] = (
                "matched changed paths: "
                + ", ".join(matches[:5])
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
