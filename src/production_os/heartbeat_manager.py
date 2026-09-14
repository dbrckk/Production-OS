from __future__ import annotations

from dataclasses import dataclass

from .runtime_state import RuntimeState


@dataclass(frozen=True, slots=True)
class HeartbeatResult:
    repository: str
    task: str
    renewed: bool
    owner: str | None

    def to_dict(self) -> dict:
        return {
            "repository": self.repository,
            "task": self.task,
            "renewed": self.renewed,
            "owner": self.owner,
        }


def renew_active_leases(
    state: RuntimeState,
    *,
    owner: str,
    minutes: int = 30,
) -> list[HeartbeatResult]:
    results: list[HeartbeatResult] = []
    for record in state.records.values():
        if record.status != "running":
            continue
        if record.lease_owner != owner:
            continue
        try:
            state.heartbeat_lease(
                record.repository,
                record.task,
                owner=owner,
                minutes=minutes,
            )
            results.append(
                HeartbeatResult(record.repository, record.task, True, owner)
            )
        except RuntimeError:
            results.append(
                HeartbeatResult(
                    record.repository,
                    record.task,
                    False,
                    record.lease_owner,
                )
            )
    return results
