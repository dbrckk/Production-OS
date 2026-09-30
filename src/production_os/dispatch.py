from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from .approvals import ApprovalStore
from .atomic_io import atomic_write_json
from .autonomous_admission import (
    AutonomousAdmissionRequest,
    commit_autonomous_admission,
    evaluate_autonomous_admission,
)
from .budgets import BudgetLedger
from .policy import PolicySet
from .quarantine import QuarantineStore
from .rate_limit import RateLimitStore
from .receipts import write_dispatch_receipt
from .runtime_state import RuntimeState
from .sqlite_backend import SQLiteJobQueue
from .workers import WorkerRegistry


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
    policy_set: PolicySet | None = None,
    budget_ledger: BudgetLedger | None = None,
    quarantine_store: QuarantineStore | None = None,
    durable_queue: SQLiteJobQueue | None = None,
    repo_rate_limit: int = 20,
    worker_rate_limit: int = 60,
    rate_window_seconds: int = 3600,
) -> DispatchResult:
    admission = evaluate_autonomous_admission(
        AutonomousAdmissionRequest(
            handoff=dict(handoff or {}),
            required_capabilities=tuple(required_capabilities or ()),
            repo_rate_limit=int(repo_rate_limit),
            worker_rate_limit=int(worker_rate_limit),
            rate_window_seconds=int(rate_window_seconds),
        ),
        runtime_state,
        worker_registry=worker_registry,
        emergency_stop_path=emergency_stop_path,
        rate_limit_store=rate_limit_store,
        approval_store=approval_store,
        policy_set=policy_set,
        budget_ledger=budget_ledger,
        quarantine_store=quarantine_store,
    )
    repository = admission.repository
    task = admission.task
    handoff = admission.handoff

    worker = None
    if worker_registry is not None and admission.worker_id is not None:
        worker = worker_registry.workers.get(admission.worker_id)
        if worker is None:
            raise RuntimeError("selected worker disappeared before dispatch")

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

        payload = {
            "schema_version": "production-os/dispatch/v4",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "idempotency_key": record.key,
            "worker_id": worker.worker_id if worker is not None else None,
            "required_capabilities": required_capabilities or [],
            "handoff": handoff,
        }
        if durable_queue is not None:
            durable_queue.enqueue(payload)
            destination = Path(f"sqlite-{record.key}")
        else:
            queue = Path(queue_dir)
            queue.mkdir(parents=True, exist_ok=True)
            worker_suffix = (
                f".{worker.worker_id}" if worker is not None else ""
            )
            destination = queue / f"{record.key}{worker_suffix}.json"
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

        commit_autonomous_admission(
            admission,
            rate_limit_store=rate_limit_store,
            budget_ledger=budget_ledger,
            include_worker_rate_limit=True,
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
        if destination is not None and durable_queue is None:
            destination.unlink(missing_ok=True)
        if worker is not None and worker_incremented:
            worker_registry.adjust_active_tasks(worker.worker_id, -1)
        latest = runtime_state.get(repository, task)
        if latest.lease_owner == owner:
            runtime_state.release_lease(repository, task)
        raise
