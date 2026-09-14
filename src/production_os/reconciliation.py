from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from .runtime_state import RuntimeState


@dataclass(frozen=True, slots=True)
class ReconciliationAction:
    key: str
    repository: str
    task: str
    action: str
    reason: str

    def to_dict(self) -> dict:
        return {
            "key": self.key,
            "repository": self.repository,
            "task": self.task,
            "action": self.action,
            "reason": self.reason,
        }


def reconcile_runtime_state(state: RuntimeState) -> list[ReconciliationAction]:
    now = datetime.now(timezone.utc)
    actions: list[ReconciliationAction] = []

    for record in state.records.values():
        lease_expired = False
        cooldown_expired = False

        if record.lease_expires_at:
            lease_expired = not state.is_leased(record, now)
        if record.cooldown_until:
            cooldown_expired = not state.in_cooldown(record, now)

        if record.status == "running" and lease_expired:
            record.status = "replan"
            record.lease_owner = None
            record.lease_expires_at = None
            record.updated_at = now.isoformat()
            actions.append(
                ReconciliationAction(
                    record.key,
                    record.repository,
                    record.task,
                    "replan",
                    "orphaned running task had an expired lease",
                )
            )

        if record.status == "circuit-open" and cooldown_expired:
            record.status = "idle"
            record.cooldown_until = None
            record.consecutive_failures = 0
            record.updated_at = now.isoformat()
            actions.append(
                ReconciliationAction(
                    record.key,
                    record.repository,
                    record.task,
                    "close-circuit",
                    "cooldown expired",
                )
            )

    if actions:
        state.save()

    return actions
