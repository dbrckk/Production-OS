from __future__ import annotations

from datetime import datetime, timezone

AUTOMATIC_WAKE_WORKER_ID = "automatic-launch"
DEFAULT_WAKE_COOLDOWN_SECONDS = 60


def _parse_timestamp(value):
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def automatic_worker_wake_allowed(
    store,
    *,
    cooldown_seconds: int = DEFAULT_WAKE_COOLDOWN_SECONDS,
    worker_id: str = AUTOMATIC_WAKE_WORKER_ID,
) -> bool:
    latest = store.latest_control_audit(
        action="kick",
        worker_id=worker_id,
    )
    if latest is None:
        return True
    if str(latest.get("outcome") or "") == "failed":
        return True
    requested_at = _parse_timestamp(latest.get("requested_at"))
    if requested_at is None:
        return True
    age = (datetime.now(timezone.utc) - requested_at).total_seconds()
    return age >= max(1, int(cooldown_seconds))


def automatic_worker_wake_needed(
    workers,
    dashboard_control,
    *,
    queued_jobs: list[dict] | None = None,
) -> bool:
    try:
        workers.detect_dead()
        workers.load()
    except Exception:
        return True

    if not workers.workers:
        return True

    active_workers = []
    for worker in workers.workers.values():
        worker_id = str(getattr(worker, "worker_id", "") or "").strip()
        desired = dashboard_control.worker_state(worker_id)
        if desired.get("desired_state") == "active":
            active_workers.append(worker)

    # Respect an intentional fleet-wide pause/drain.
    if not active_workers:
        return False

    online_workers = [
        worker for worker in active_workers
        if str(getattr(worker, "status", "") or "").lower() == "online"
    ]
    if not online_workers:
        return True

    if queued_jobs is None:
        return False

    for job in queued_jobs:
        payload = job.get("payload") if isinstance(job, dict) else None
        if not isinstance(payload, dict):
            payload = {}
        required = {
            str(item).strip()
            for item in payload.get("required_capabilities", [])
            if str(item).strip()
        }
        assigned_worker = str(
            (job.get("assigned_worker") if isinstance(job, dict) else "") or ""
        ).strip()
        compatible = False
        for worker in online_workers:
            worker_id = str(getattr(worker, "worker_id", "") or "").strip()
            if assigned_worker and worker_id != assigned_worker:
                continue
            capabilities = {
                str(item).strip()
                for item in getattr(worker, "capabilities", [])
                if str(item).strip()
            }
            if required.issubset(capabilities):
                compatible = True
                break
        if not compatible:
            return True

    return False


def request_automatic_worker_wake(
    *,
    workers,
    dashboard_control,
    store,
    requested_by: str,
    worker_id: str = AUTOMATIC_WAKE_WORKER_ID,
    cooldown_seconds: int = DEFAULT_WAKE_COOLDOWN_SECONDS,
    queued_jobs: list[dict] | None = None,
) -> dict:
    if not automatic_worker_wake_needed(
        workers,
        dashboard_control,
        queued_jobs=queued_jobs,
    ):
        return {"status":"not_needed"}

    if not automatic_worker_wake_allowed(
        store,
        cooldown_seconds=cooldown_seconds,
        worker_id=worker_id,
    ):
        return {
            "status":"cooldown",
            "cooldown_seconds":int(cooldown_seconds),
        }

    wake = dashboard_control.kick_worker(worker_id)
    try:
        store.append_control_audit(
            action="kick",
            worker_id=worker_id,
            requested_by=str(requested_by),
            outcome=str(wake.get("status") or "failed"),
            error_code=(
                str(wake.get("error"))
                if wake.get("status") == "failed"
                else None
            ),
        )
    except Exception:
        # Waking a worker is a best-effort recovery path. Never turn an
        # already-created durable production into an HTTP/controller failure
        # merely because the auxiliary audit write could not be persisted.
        return {
            **wake,
            "audit_recorded":False,
        }

    return wake
