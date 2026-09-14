from __future__ import annotations

from dataclasses import dataclass

from .runtime_state import RuntimeState
from .workers import WorkerRegistry


@dataclass(frozen=True, slots=True)
class PreemptionDecision:
    should_preempt: bool
    victim_repository: str | None
    victim_task: str | None
    victim_worker: str | None
    reason: str

    def to_dict(self) -> dict:
        return {
            "should_preempt": self.should_preempt,
            "victim_repository": self.victim_repository,
            "victim_task": self.victim_task,
            "victim_worker": self.victim_worker,
            "reason": self.reason,
        }


def choose_preemption_victim(
    runtime_state: RuntimeState,
    workers: WorkerRegistry,
    *,
    required_capabilities: list[str],
    incoming_priority: float,
    minimum_priority_gap: float = 20.0,
) -> PreemptionDecision:
    capable_workers = [
        worker for worker in workers.workers.values()
        if worker.status == "online"
        and set(required_capabilities).issubset(set(worker.capabilities))
    ]
    if not capable_workers:
        return PreemptionDecision(False, None, None, None, "no capable workers exist")

    candidates = []
    for record in runtime_state.records.values():
        if record.status != "running":
            continue
        if not record.interruptible:
            continue
        if not record.lease_owner:
            continue
        worker = workers.workers.get(record.lease_owner)
        if worker is None or worker not in capable_workers:
            continue
        current_priority = float(record.priority or 0.0)
        gap = incoming_priority - current_priority
        if gap < minimum_priority_gap:
            continue
        candidates.append(
            (current_priority, -gap, record.repository, record.task, record)
        )

    if not candidates:
        return PreemptionDecision(
            False, None, None, None, "no safe lower-priority victim"
        )

    candidates.sort(key=lambda row: (row[0], row[1], row[2], row[3]))
    victim = candidates[0][-1]
    return PreemptionDecision(
        True,
        victim.repository,
        victim.task,
        victim.lease_owner,
        "higher-priority task can safely preempt an interruptible lower-priority task",
    )


def request_preemption(
    runtime_state: RuntimeState,
    repository: str,
    task: str,
) -> dict:
    record = runtime_state.get(repository, task)
    if record.status != "running":
        raise RuntimeError("task is not running")
    if not record.interruptible:
        raise RuntimeError("task is not interruptible")
    record.preempt_requested = True
    record.status = "preempt-requested"
    runtime_state.save()
    return record.to_dict()


def confirm_checkpoint_and_release(
    runtime_state: RuntimeState,
    workers: WorkerRegistry,
    repository: str,
    task: str,
    worker_id: str,
    checkpoint_ref: str,
) -> dict:
    record = runtime_state.get(repository, task)
    if not record.preempt_requested:
        raise RuntimeError("no preemption requested")
    if record.lease_owner != worker_id:
        raise RuntimeError("worker does not own the task")
    if not checkpoint_ref:
        raise ValueError("checkpoint_ref is required")

    record.checkpoint_ref = checkpoint_ref
    record.status = "paused"
    record.preempt_requested = False
    record.lease_owner = None
    record.lease_expires_at = None
    runtime_state.save()

    if worker_id in workers.workers:
        workers.adjust_active_tasks(worker_id, -1)

    return runtime_state.get(repository, task).to_dict()
