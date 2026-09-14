from __future__ import annotations

import json
from pathlib import Path

from .sqlite_backend import SQLiteBackend


def import_json_state(
    backend: SQLiteBackend,
    *,
    runtime_state: str | None = None,
    workers: str | None = None,
    claims: str | None = None,
) -> dict:
    counts = {"runtime_records":0, "workers":0, "claims":0}

    with backend.transaction() as db:
        if runtime_state:
            payload=json.loads(Path(runtime_state).read_text(encoding="utf-8"))
            for row in payload.get("records", {}).values():
                db.execute(
                    """
                    INSERT INTO runtime_records(
                        key, repository, task, status, attempts,
                        consecutive_failures, lease_owner, lease_expires_at,
                        cooldown_until, last_decision, updated_at, priority,
                        interruptible, preempt_requested, checkpoint_ref,
                        started_at
                    )
                    VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                    ON CONFLICT(key) DO UPDATE SET
                        repository=excluded.repository,
                        task=excluded.task,
                        status=excluded.status,
                        attempts=excluded.attempts,
                        consecutive_failures=excluded.consecutive_failures,
                        lease_owner=excluded.lease_owner,
                        lease_expires_at=excluded.lease_expires_at,
                        cooldown_until=excluded.cooldown_until,
                        last_decision=excluded.last_decision,
                        updated_at=excluded.updated_at,
                        priority=excluded.priority,
                        interruptible=excluded.interruptible,
                        preempt_requested=excluded.preempt_requested,
                        checkpoint_ref=excluded.checkpoint_ref,
                        started_at=excluded.started_at
                    """,
                    (
                        row["key"],
                        row["repository"],
                        row["task"],
                        row.get("status","idle"),
                        int(row.get("attempts",0)),
                        int(row.get("consecutive_failures",0)),
                        row.get("lease_owner"),
                        row.get("lease_expires_at"),
                        row.get("cooldown_until"),
                        row.get("last_decision"),
                        row.get("updated_at"),
                        float(row.get("priority",0.0)),
                        int(bool(row.get("interruptible",False))),
                        int(bool(row.get("preempt_requested",False))),
                        row.get("checkpoint_ref"),
                        row.get("started_at"),
                    ),
                )
                counts["runtime_records"] += 1

        if workers:
            payload=json.loads(Path(workers).read_text(encoding="utf-8"))
            for row in payload.get("workers", []):
                db.execute(
                    """
                    INSERT INTO workers(
                        worker_id, capabilities_json, max_concurrency,
                        active_tasks, status, last_heartbeat
                    )
                    VALUES(?,?,?,?,?,?)
                    ON CONFLICT(worker_id) DO UPDATE SET
                        capabilities_json=excluded.capabilities_json,
                        max_concurrency=excluded.max_concurrency,
                        active_tasks=excluded.active_tasks,
                        status=excluded.status,
                        last_heartbeat=excluded.last_heartbeat
                    """,
                    (
                        row["worker_id"],
                        json.dumps(row.get("capabilities",[])),
                        int(row.get("max_concurrency",1)),
                        int(row.get("active_tasks",0)),
                        row.get("status","online"),
                        row.get("last_heartbeat"),
                    ),
                )
                counts["workers"] += 1

        if claims:
            payload=json.loads(Path(claims).read_text(encoding="utf-8"))
            for row in payload.get("claims", []):
                db.execute(
                    """
                    INSERT INTO claims(
                        key, worker_id, repository, task, status,
                        claimed_at, ack_deadline, completed_at
                    )
                    VALUES(?,?,?,?,?,?,?,?)
                    ON CONFLICT(key) DO UPDATE SET
                        worker_id=excluded.worker_id,
                        repository=excluded.repository,
                        task=excluded.task,
                        status=excluded.status,
                        claimed_at=excluded.claimed_at,
                        ack_deadline=excluded.ack_deadline,
                        completed_at=excluded.completed_at
                    """,
                    (
                        row["key"],
                        row["worker_id"],
                        row["repository"],
                        row["task"],
                        row["status"],
                        row["claimed_at"],
                        row["ack_deadline"],
                        row.get("completed_at"),
                    ),
                )
                counts["claims"] += 1

        backend.append_event(
            db,
            "json-state-imported",
            counts,
        )

    return {
        "schema_version":"production-os/sqlite-import/v1",
        "counts":counts,
    }
