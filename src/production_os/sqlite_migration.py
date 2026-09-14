from __future__ import annotations

import json
from pathlib import Path

from .claims import ClaimRecord
from .runtime_state import RuntimeRecord
from .storage import claim_store_for, runtime_state_for, worker_registry_for
from .workers import Worker


def import_json_state(
    backend,
    *,
    runtime_state: str | None = None,
    workers: str | None = None,
    claims: str | None = None,
) -> dict:
    counts = {"runtime_records":0, "workers":0, "claims":0}

    if runtime_state:
        payload = json.loads(
            Path(runtime_state).read_text(encoding="utf-8")
        )
        store = runtime_state_for(backend)
        for key, row in payload.get("records", {}).items():
            normalized = {
                "key":row.get("key", key),
                "repository":row["repository"],
                "task":row["task"],
                "status":row.get("status","idle"),
                "attempts":int(row.get("attempts",0)),
                "consecutive_failures":int(
                    row.get("consecutive_failures",0)
                ),
                "lease_owner":row.get("lease_owner"),
                "lease_expires_at":row.get("lease_expires_at"),
                "cooldown_until":row.get("cooldown_until"),
                "last_decision":row.get("last_decision"),
                "updated_at":row.get("updated_at"),
                "priority":float(row.get("priority",0.0)),
                "interruptible":bool(row.get("interruptible",False)),
                "preempt_requested":bool(
                    row.get("preempt_requested",False)
                ),
                "checkpoint_ref":row.get("checkpoint_ref"),
                "started_at":row.get("started_at"),
            }
            record = RuntimeRecord(**normalized)
            store.records[record.key] = record
            counts["runtime_records"] += 1
        store.save()

    if workers:
        payload = json.loads(Path(workers).read_text(encoding="utf-8"))
        registry = worker_registry_for(backend)
        for row in payload.get("workers", []):
            worker = Worker(
                worker_id=row["worker_id"],
                capabilities=[
                    str(x) for x in row.get("capabilities", [])
                ],
                max_concurrency=int(row.get("max_concurrency",1)),
                active_tasks=int(row.get("active_tasks",0)),
                status=str(row.get("status","online")),
                last_heartbeat=row.get("last_heartbeat"),
            )
            registry.workers[worker.worker_id] = worker
            counts["workers"] += 1
        registry.save()

    if claims:
        payload = json.loads(Path(claims).read_text(encoding="utf-8"))
        store = claim_store_for(backend)
        for row in payload.get("claims", []):
            claim = ClaimRecord(
                key=row["key"],
                worker_id=row["worker_id"],
                repository=row["repository"],
                task=row["task"],
                status=row["status"],
                claimed_at=row["claimed_at"],
                ack_deadline=row["ack_deadline"],
                completed_at=row.get("completed_at"),
            )
            store.claims[claim.key] = claim
            counts["claims"] += 1
        store.save()

    with backend.transaction() as db:
        backend.append_event(
            db,
            "json-state-imported",
            counts,
        )

    return {
        "schema_version":"production-os/database-import/v2",
        "counts":counts,
    }
