from __future__ import annotations


def signals_from_health(health: dict) -> list[dict]:
    signals = []
    for reason in health.get("reasons") or []:
        code = str(reason.get("code") or "")
        severity = str(reason.get("severity") or "medium")
        evidence = dict(reason.get("evidence") or {})
        if code == "queue_without_worker":
            queued = int(evidence.get("queued") or 0)
            signals.append({
                "code":code,
                "severity":severity,
                "title":"Travail en attente sans worker",
                "message":f"{queued} jobs en attente sans worker en ligne",
                "target_type":"control-plane",
                "target_id":"global",
            })
        elif code == "backup_filesystem_capacity":
            status = str(evidence.get("status") or "warning")
            available = evidence.get("available_percent")
            signals.append({
                "code":code,
                "severity":severity,
                "title":"Capacité de stockage backup faible",
                "message":(
                    f"filesystem backup {status}, "
                    f"{available}% disponible"
                ),
                "target_type":"backup-storage",
                "target_id":"primary",
            })
        elif code == "stale_busy_workers":
            for worker in evidence.get("workers") or []:
                worker_id = str(worker.get("worker_id") or "")
                if not worker_id:
                    continue
                age = worker.get("age_seconds")
                signals.append({
                    "code":code,
                    "severity":severity,
                    "title":"Worker occupé sans heartbeat récent",
                    "message":f"{worker_id} stale depuis {age} s",
                    "target_type":"worker",
                    "target_id":worker_id,
                })
        elif code == "stale_running_executions":
            for execution in evidence.get("executions") or []:
                job_key = str(execution.get("job_key") or "")
                if not job_key:
                    continue
                age = execution.get("age_seconds")
                signals.append({
                    "code":code,
                    "severity":severity,
                    "title":"Exécution sans télémétrie récente",
                    "message":f"{job_key} stale depuis {age} s",
                    "target_type":"job",
                    "target_id":job_key,
                })
    return signals


def dedupe_key(signal: dict) -> str:
    return (
        f"{signal['code']}:{signal['target_type']}:{signal['target_id']}"
    )
