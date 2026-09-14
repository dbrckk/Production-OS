from __future__ import annotations

import json
from pathlib import Path

from .claims import ClaimStore
from .runtime_state import RuntimeState
from .workers import WorkerRegistry


def recover_unacked_jobs(
    *,
    claims: ClaimStore,
    runtime_state: RuntimeState,
    workers: WorkerRegistry,
    queue_dir: str | Path,
    dead_letter_dir: str | Path | None = None,
) -> list[dict]:
    recovered=[]
    queue=Path(queue_dir)
    dead=Path(dead_letter_dir) if dead_letter_dir else None
    if dead is not None:
        dead.mkdir(parents=True,exist_ok=True)

    for claim in claims.expired_unacked():
        source_candidates=list(queue.glob(f"{claim.key}*.json"))
        for source in source_candidates:
            try:
                payload=json.loads(source.read_text(encoding="utf-8"))
            except Exception:
                continue

            worker=workers.workers.get(claim.worker_id)
            if worker is not None and worker.active_tasks > 0:
                worker.active_tasks -= 1

            record=runtime_state.get(claim.repository,claim.task)
            if record.lease_owner == claim.worker_id:
                runtime_state.release_lease(claim.repository,claim.task)

            claim.status="expired"

            if dead is not None:
                target=dead/source.name
                source.replace(target)
                recovered.append({
                    "key":claim.key,
                    "action":"dead-letter",
                    "path":str(target),
                })
            else:
                recovered.append({
                    "key":claim.key,
                    "action":"released-for-redelivery",
                    "path":str(source),
                })

    if recovered:
        claims.save()
        workers.save()
    return recovered
