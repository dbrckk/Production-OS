from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from .runtime_state import RuntimeState


@dataclass(frozen=True, slots=True)
class HealingAction:
    repository: str
    task: str
    action: str
    reason: str

    def to_dict(self) -> dict:
        return {
            "repository": self.repository,
            "task": self.task,
            "action": self.action,
            "reason": self.reason,
        }


def apply_self_healing(state: RuntimeState) -> list[HealingAction]:
    now = datetime.now(timezone.utc)
    actions: list[HealingAction] = []

    for record in state.records.values():
        if record.status == "failed" and record.consecutive_failures >= 2:
            if not state.in_cooldown(record, now):
                record.status = "circuit-open"
                actions.append(
                    HealingAction(
                        record.repository,
                        record.task,
                        "open-circuit",
                        "repeated failures without active cooldown",
                    )
                )

        if record.status == "running" and not state.is_leased(record, now):
            record.status = "replan"
            record.lease_owner = None
            record.lease_expires_at = None
            actions.append(
                HealingAction(
                    record.repository,
                    record.task,
                    "replan",
                    "running task lost its lease",
                )
            )

        if record.status == "replan" and record.attempts >= 5:
            record.status = "circuit-open"
            actions.append(
                HealingAction(
                    record.repository,
                    record.task,
                    "open-circuit",
                    "replan loop exceeded safe attempt threshold",
                )
            )

    if actions:
        state.save()
    return actions
