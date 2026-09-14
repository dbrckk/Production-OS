from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from .policy import PolicySet
from .quarantine import QuarantineStore
from .runtime_state import RuntimeState


@dataclass(frozen=True, slots=True)
class GovernanceAction:
    repository: str
    action: str
    reason: str

    def to_dict(self) -> dict:
        return {
            "repository": self.repository,
            "action": self.action,
            "reason": self.reason,
        }


def apply_governance(
    runtime_state: RuntimeState,
    policy_set: PolicySet,
    quarantine_store: QuarantineStore,
) -> list[GovernanceAction]:
    by_repo: dict[str, list] = {}
    for record in runtime_state.records.values():
        by_repo.setdefault(record.repository, []).append(record)

    actions: list[GovernanceAction] = []
    for repository, records in by_repo.items():
        policy = policy_set.merged_for(repository)
        threshold = int(policy.get("auto_quarantine_after_failures", 0) or 0)
        slo = policy.get("slo", {}) or {}

        failures = max(
            [int(r.consecutive_failures or 0) for r in records] or [0]
        )
        circuit_open = any(r.status == "circuit-open" for r in records)
        active, _ = quarantine_store.active(repository)

        violations: list[str] = []
        if threshold > 0 and failures >= threshold:
            violations.append(
                f"automatic quarantine after {failures} consecutive failures"
            )
        if circuit_open:
            violations.append("automatic quarantine after circuit-open")

        max_attempts = int(slo.get("max_attempts", 0) or 0)
        if max_attempts > 0:
            attempts = max([int(r.attempts or 0) for r in records] or [0])
            if attempts > max_attempts:
                violations.append(
                    f"SLO max_attempts exceeded: {attempts}>{max_attempts}"
                )

        max_failures = int(slo.get("max_consecutive_failures", 0) or 0)
        if max_failures > 0 and failures > max_failures:
            violations.append(
                f"SLO max_consecutive_failures exceeded: {failures}>{max_failures}"
            )

        max_runtime = float(slo.get("max_runtime_minutes", 0) or 0)
        if max_runtime > 0:
            now = datetime.now(timezone.utc)
            for record in records:
                if record.status not in {"running", "preempt-requested"}:
                    continue
                if not record.started_at:
                    continue
                started = datetime.fromisoformat(
                    record.started_at.replace("Z", "+00:00")
                )
                runtime_minutes = (now - started).total_seconds() / 60.0
                if runtime_minutes > max_runtime:
                    violations.append(
                        f"SLO max_runtime_minutes exceeded: "
                        f"{runtime_minutes:.1f}>{max_runtime}"
                    )
                    break

        if not active and violations:
            reason = "; ".join(violations)
            quarantine_store.set(repository, active=True, reason=reason)
            actions.append(
                GovernanceAction(repository, "quarantine", reason)
            )

    return actions
