from __future__ import annotations

from production_os.api_auth import TokenAuthorizer
from production_os.control_plane import ControlPlane


def _control(tmp_path):
    return ControlPlane(
        str(tmp_path / "playbooks.sqlite"),
        authorizer=TokenAuthorizer([]),
    )


def test_queue_incident_exposes_truthful_scheduled_kick_fallback(tmp_path):
    control = _control(tmp_path)
    control.queue.enqueue({
        "handoff":{"repository":"dbrckk/example","task":"waiting"},
        "required_capabilities":["python"],
    })
    incidents = control.dashboard.incidents()["incidents"]
    incident = next(x for x in incidents if x["code"] == "queue_without_worker")
    suggestion = incident["playbook"]["suggestions"][0]
    assert suggestion["action"] == "kick"
    assert suggestion["worker_id"] == "github-actions-worker"
    assert suggestion["availability"] == "fallback"
    assert suggestion["interrupting"] is False


def test_queue_incident_exposes_immediate_kick_only_when_dispatch_is_configured(tmp_path):
    control = _control(tmp_path)
    control.queue.enqueue({
        "handoff":{"repository":"dbrckk/example","task":"waiting"},
        "required_capabilities":["python"],
    })
    control.dashboard_control.github = object()
    control.dashboard_control.actions_repository = "dbrckk/ai-dev-server"
    control.dashboard_control.actions_workflow = "production-os-actions-worker.yml"
    incident = next(
        x for x in control.dashboard.incidents()["incidents"]
        if x["code"] == "queue_without_worker"
    )
    suggestion = incident["playbook"]["suggestions"][0]
    assert suggestion["availability"] == "available"


def test_stale_worker_playbook_only_offers_recovery_for_expired_claim(tmp_path):
    control = _control(tmp_path)
    control.workers.register("worker-a", ["python"], 1)
    job = control.queue.enqueue({
        "handoff":{"repository":"dbrckk/example","task":"expired"},
        "required_capabilities":["python"],
    })
    assert control.queue.claim_key(job["key"], "worker-a") is not None
    with control.backend.transaction() as db:
        db.execute(
            """UPDATE workers
               SET active_tasks=1, last_heartbeat=?
               WHERE worker_id=?""",
            ("2000-01-01T00:00:00+00:00", "worker-a"),
        )
        db.execute(
            "UPDATE jobs SET ack_deadline=? WHERE key=?",
            ("2000-01-01T00:00:00+00:00", job["key"]),
        )
    incident = next(
        x for x in control.dashboard.incidents()["incidents"]
        if x["code"] == "stale_busy_workers"
    )
    recovery = [
        x for x in incident["playbook"]["suggestions"]
        if x["action"] == "recover-stuck"
    ]
    assert len(recovery) == 1
    assert recovery[0]["job_key"] == job["key"]
    assert recovery[0]["worker_id"] == "worker-a"


def test_stale_execution_playbook_offers_cancel_only_for_active_owned_job(tmp_path):
    control = _control(tmp_path)
    control.workers.register("worker-a", ["python"], 1)
    job = control.queue.enqueue({
        "handoff":{"repository":"dbrckk/example","task":"stale execution"},
        "required_capabilities":["python"],
    })
    assert control.queue.claim_key(job["key"], "worker-a") is not None
    control.queue.ack(job["key"], "worker-a")
    control.dashboard_store.start_execution(
        control.queue.get(job["key"]),
        "worker-a",
        started_at="2000-01-01T00:00:00+00:00",
    )
    incident = next(
        x for x in control.dashboard.incidents()["incidents"]
        if x["code"] == "stale_running_executions"
    )
    cancel = next(
        x for x in incident["playbook"]["suggestions"]
        if x["action"] == "cancel-current"
    )
    assert cancel["availability"] == "available"
    assert cancel["worker_id"] == "worker-a"
    assert cancel["job_key"] == job["key"]
    assert cancel["interrupting"] is True
