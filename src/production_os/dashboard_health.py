from __future__ import annotations

from datetime import datetime, timezone

STALE_BUSY_WORKER_SECONDS = 180
STALE_RUNNING_EXECUTION_SECONDS = 300


def _dt(value):
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def derive_control_health(snapshot: dict) -> dict:
    now = _dt(snapshot.get("generated_at")) or datetime.now(timezone.utc)
    reasons = []

    queued = int((snapshot.get("productions") or {}).get("queued") or 0)
    online = int((snapshot.get("workers") or {}).get("online") or 0)
    if queued > 0 and online == 0:
        reasons.append({
            "code":"queue_without_worker",
            "severity":"high",
            "evidence":{"queued":queued,"online_workers":online},
        })

    stale_workers = []
    for worker in snapshot.get("worker_rows") or []:
        if int(worker.get("active_tasks") or 0) <= 0:
            continue
        last = _dt(worker.get("last_heartbeat"))
        if last is None:
            continue
        age = max(0.0, (now - last).total_seconds())
        if age > STALE_BUSY_WORKER_SECONDS:
            stale_workers.append({
                "worker_id":str(worker.get("worker_id") or ""),
                "age_seconds":round(age, 1),
            })
    if stale_workers:
        reasons.append({
            "code":"stale_busy_workers",
            "severity":"medium",
            "evidence":{"workers":stale_workers},
        })

    stale_executions = []
    for execution in snapshot.get("running_executions") or []:
        last = _dt(
            execution.get("last_telemetry_at")
            or execution.get("started_at")
        )
        if last is None:
            continue
        age = max(0.0, (now - last).total_seconds())
        if age > STALE_RUNNING_EXECUTION_SECONDS:
            stale_executions.append({
                "job_key":str(execution.get("job_key") or ""),
                "worker_id":str(execution.get("worker_id") or ""),
                "age_seconds":round(age, 1),
            })
    if stale_executions:
        reasons.append({
            "code":"stale_running_executions",
            "severity":"high",
            "evidence":{"executions":stale_executions},
        })

    filesystem = (
        (snapshot.get("backup_storage") or {}).get("filesystem") or {}
    )
    filesystem_status = str(filesystem.get("status") or "")
    if filesystem_status in {"warning","critical"}:
        available_percent = filesystem.get("available_percent")
        reasons.append({
            "code":"backup_filesystem_capacity",
            "severity":"high" if filesystem_status == "critical" else "medium",
            "evidence":{
                "status":filesystem_status,
                "available_percent":available_percent,
            },
        })

    return {
        "status":"degraded" if reasons else "healthy",
        "reasons":reasons,
        "generated_at":now.isoformat(),
    }
