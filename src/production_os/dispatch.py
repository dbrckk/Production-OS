from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from .runtime_state import RuntimeState


@dataclass(frozen=True, slots=True)
class DispatchResult:
    repository: str
    task: str
    key: str
    queue_file: str
    lease_owner: str

    def to_dict(self) -> dict:
        return {
            "repository": self.repository,
            "task": self.task,
            "key": self.key,
            "queue_file": self.queue_file,
            "lease_owner": self.lease_owner,
        }


def dispatch_handoff(
    handoff: dict,
    queue_dir: str | Path,
    runtime_state: RuntimeState,
    *,
    lease_owner: str = "production-os",
    lease_minutes: int = 30,
) -> DispatchResult:
    repository = str(handoff.get("repository", ""))
    task = str(handoff.get("task", ""))
    if not repository or not task:
        raise ValueError("handoff requires repository and task")

    record = runtime_state.get(repository, task)
    if runtime_state.is_leased(record):
        raise RuntimeError("task already leased")
    if runtime_state.in_cooldown(record):
        raise RuntimeError("task is in cooldown")
    if record.status in {"circuit-open", "succeeded"}:
        raise RuntimeError(f"task not dispatchable: {record.status}")

    runtime_state.acquire_lease(
        repository,
        task,
        owner=lease_owner,
        minutes=lease_minutes,
    )
    record = runtime_state.get(repository, task)

    queue = Path(queue_dir)
    queue.mkdir(parents=True, exist_ok=True)
    destination = queue / f"{record.key}.json"
    payload = {
        "schema_version": "production-os/dispatch/v1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "idempotency_key": record.key,
        "handoff": handoff,
    }
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    return DispatchResult(
        repository=repository,
        task=task,
        key=record.key,
        queue_file=str(destination),
        lease_owner=lease_owner,
    )
