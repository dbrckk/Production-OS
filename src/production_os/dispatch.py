from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from .receipts import write_dispatch_receipt
from .runtime_state import RuntimeState
from .workers import WorkerRegistry, select_worker


@dataclass(frozen=True, slots=True)
class DispatchResult:
    repository: str
    task: str
    key: str
    queue_file: str
    lease_owner: str
    worker_id: str | None = None
    receipt_file: str | None = None

    def to_dict(self) -> dict:
        return {
            "repository": self.repository,
            "task": self.task,
            "key": self.key,
            "queue_file": self.queue_file,
            "lease_owner": self.lease_owner,
            "worker_id": self.worker_id,
            "receipt_file": self.receipt_file,
        }


def dispatch_handoff(
    handoff: dict,
    queue_dir: str | Path,
    runtime_state: RuntimeState,
    *,
    lease_owner: str = "production-os",
    lease_minutes: int = 30,
    worker_registry: WorkerRegistry | None = None,
    required_capabilities: list[str] | None = None,
    receipt_dir: str | Path | None = None,
) -> DispatchResult:
    repository = str(handoff.get("repository", ""))
    task = str(handoff.get("task", ""))
    if not repository or not task:
        raise ValueError("handoff requires repository and task")

    worker = None
    if worker_registry is not None:
        worker_registry.detect_dead()
        worker = select_worker(worker_registry, required_capabilities)
        if worker is None:
            raise RuntimeError("backpressure: no capable worker available")

    record = runtime_state.get(repository, task)
    if runtime_state.is_leased(record):
        raise RuntimeError("task already leased")
    if runtime_state.in_cooldown(record):
        raise RuntimeError("task is in cooldown")
    if record.status in {"circuit-open", "succeeded"}:
        raise RuntimeError(f"task not dispatchable: {record.status}")

    owner = worker.worker_id if worker is not None else lease_owner
    runtime_state.acquire_lease(
        repository,
        task,
        owner=owner,
        minutes=lease_minutes,
    )
    record = runtime_state.get(repository, task)

    if worker is not None:
        worker.active_tasks += 1
        worker_registry.save()

    queue = Path(queue_dir)
    queue.mkdir(parents=True, exist_ok=True)
    worker_suffix = f".{worker.worker_id}" if worker is not None else ""
    destination = queue / f"{record.key}{worker_suffix}.json"
    payload = {
        "schema_version": "production-os/dispatch/v2",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "idempotency_key": record.key,
        "worker_id": worker.worker_id if worker is not None else None,
        "required_capabilities": required_capabilities or [],
        "handoff": handoff,
    }
    destination.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    receipt_file = None
    if receipt_dir is not None and worker is not None:
        receipt_file = write_dispatch_receipt(
            receipt_dir,
            key=record.key,
            worker_id=worker.worker_id,
            repository=repository,
            task=task,
        )

    return DispatchResult(
        repository=repository,
        task=task,
        key=record.key,
        queue_file=str(destination),
        lease_owner=owner,
        worker_id=worker.worker_id if worker is not None else None,
        receipt_file=receipt_file,
    )
