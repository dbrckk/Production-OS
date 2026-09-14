from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from .approvals import ApprovalStore
from .atomic_io import atomic_write_json
from .emergency import emergency_stop_active
from .rate_limit import RateLimitStore
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
    emergency_stop_path: str | Path | None = None,
    rate_limit_store: RateLimitStore | None = None,
    approval_store: ApprovalStore | None = None,
    repo_rate_limit: int = 20,
    worker_rate_limit: int = 60,
    rate_window_seconds: int = 3600,
) -> DispatchResult:
    repository = str(handoff.get("repository", ""))
    task = str(handoff.get("task", ""))
    if not repository or not task:
        raise ValueError("handoff requires repository and task")
    if emergency_stop_active(emergency_stop_path):
        raise RuntimeError("emergency stop active")

    worker = None
    if worker_registry is not None:
        worker_registry.detect_dead()
        worker = select_worker(worker_registry, required_capabilities)
        if worker is None:
            raise RuntimeError("backpressure: no capable worker available")

    if rate_limit_store is not None:
        repo_decision = rate_limit_store.check_and_record(
            f"repo:{repository}",
            limit=repo_rate_limit,
            window_seconds=rate_window_seconds,
        )
        if not repo_decision.allowed:
            raise RuntimeError("rate limit exceeded for repository")
        if worker is not None:
            worker_decision = rate_limit_store.check_and_record(
                f"worker:{worker.worker_id}",
                limit=worker_rate_limit,
                window_seconds=rate_window_seconds,
            )
            if not worker_decision.allowed:
                raise RuntimeError("rate limit exceeded for worker")

    record = runtime_state.get(repository, task)
    requires_approval = bool(
        handoff.get("constraints", {}).get("requires_human_approval", False)
    )
    if requires_approval:
        if approval_store is None or not approval_store.is_approved(record.key):
            raise RuntimeError("human approval required")
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
        priority=float(handoff.get("priority", 0.0)),
        interruptible=bool(
            handoff.get("constraints", {}).get("interruptible", False)
        ),
    )
    record = runtime_state.get(repository, task)

    worker_incremented = False
    destination: Path | None = None
    try:
        if worker is not None:
            worker_registry.adjust_active_tasks(worker.worker_id, +1)
            worker_incremented = True

        queue = Path(queue_dir)
        queue.mkdir(parents=True, exist_ok=True)
        worker_suffix = f".{worker.worker_id}" if worker is not None else ""
        destination = queue / f"{record.key}{worker_suffix}.json"
        payload = {
            "schema_version": "production-os/dispatch/v3",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "idempotency_key": record.key,
            "worker_id": worker.worker_id if worker is not None else None,
            "required_capabilities": required_capabilities or [],
            "handoff": handoff,
        }
        atomic_write_json(destination, payload)

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
    except Exception:
        if destination is not None:
            destination.unlink(missing_ok=True)
        if worker is not None and worker_incremented:
            worker_registry.adjust_active_tasks(worker.worker_id, -1)
        latest = runtime_state.get(repository, task)
        if latest.lease_owner == owner:
            runtime_state.release_lease(repository, task)
        raise
