from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ValidationSummary:
    status: str
    passed: int
    failed: int
    pending: int
    blocking_failures: tuple[str, ...]

    def to_dict(self) -> dict:
        return {
            "status": self.status,
            "passed": self.passed,
            "failed": self.failed,
            "pending": self.pending,
            "blocking_failures": list(self.blocking_failures),
        }


def summarize_validation_results(
    validation_plan: list[dict],
    results: list[dict] | None,
) -> ValidationSummary:
    by_kind = {
        str(item.get("kind")): str(item.get("status", "")).lower()
        for item in (results or [])
        if item.get("kind")
    }

    passed = 0
    failed = 0
    pending = 0
    blocking: list[str] = []

    for step in validation_plan:
        kind = str(step.get("kind"))
        required = bool(step.get("required", True))
        status = by_kind.get(kind)

        if status in {"pass", "passed", "success", "green"}:
            passed += 1
        elif status in {"fail", "failed", "error", "red"}:
            failed += 1
            if required:
                blocking.append(kind)
        else:
            pending += 1

    if blocking:
        overall = "blocked"
    elif pending:
        overall = "incomplete"
    else:
        overall = "passed"

    return ValidationSummary(
        status=overall,
        passed=passed,
        failed=failed,
        pending=pending,
        blocking_failures=tuple(sorted(set(blocking))),
    )
