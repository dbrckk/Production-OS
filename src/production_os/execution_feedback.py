from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ExecutionDecision:
    decision: str
    score_delta: int
    validation_status: str
    rationale: tuple[str, ...]

    def to_dict(self) -> dict:
        return {
            "decision": self.decision,
            "score_delta": self.score_delta,
            "validation_status": self.validation_status,
            "rationale": list(self.rationale),
        }


def decide_execution_outcome(
    before_score: int,
    after_score: int,
    validation_summary: dict,
    *,
    regression_threshold: int = 5,
) -> ExecutionDecision:
    delta = after_score - before_score
    status = str(validation_summary.get("status", "incomplete"))
    reasons: list[str] = []

    if status == "blocked":
        reasons.append("required validation failed")
        return ExecutionDecision("rollback", delta, status, tuple(reasons))

    if delta <= -abs(regression_threshold):
        reasons.append(f"maturity regressed by {delta} points")
        return ExecutionDecision("rollback", delta, status, tuple(reasons))

    if status == "incomplete":
        reasons.append("validation is incomplete")
        return ExecutionDecision("retry", delta, status, tuple(reasons))

    if delta > 0 and status == "passed":
        reasons.append(f"validated improvement of +{delta} maturity points")
        return ExecutionDecision("promote", delta, status, tuple(reasons))

    if delta == 0 and status == "passed":
        reasons.append("validation passed but portfolio score did not improve")
        return ExecutionDecision("replan", delta, status, tuple(reasons))

    reasons.append("execution produced no promotable evidence")
    return ExecutionDecision("replan", delta, status, tuple(reasons))
