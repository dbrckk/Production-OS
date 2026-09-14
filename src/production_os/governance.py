from __future__ import annotations

from dataclasses import dataclass

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
        if threshold <= 0:
            continue

        failures = max(
            [int(r.consecutive_failures or 0) for r in records] or [0]
        )
        circuit_open = any(r.status == "circuit-open" for r in records)
        active, _ = quarantine_store.active(repository)

        if not active and (failures >= threshold or circuit_open):
            reason = (
                f"automatic quarantine after {failures} consecutive failures"
                if failures >= threshold
                else "automatic quarantine after circuit-open"
            )
            quarantine_store.set(repository, active=True, reason=reason)
            actions.append(
                GovernanceAction(repository, "quarantine", reason)
            )

    return actions
