from __future__ import annotations

import pytest

from production_os.control_plane import ControlPlane
from production_os.dashboard_service import DashboardNotFound


def test_production_status_tracks_queue_claim_ack_and_live_telemetry(tmp_path):
    control = ControlPlane(str(tmp_path / "live-status.sqlite"))
    project = control.managed_projects.create(
        repository="dbrckk/live-status",
        final_goal="Implement live production tracking.",
        token_budget=30000,
        agent_preference="auto",
    )
    project_id = project["project_id"]

    queued = control.dashboard.production_status(project_id)
    assert queued["schema_version"] == "production-os/production-status/v1"
    assert queued["project"]["project_id"] == project_id
    assert queued["runtime"]["phase"] == "queued"
    assert queued["runtime"]["job_key"]
    assert queued["runtime"]["job_status"] == "queued"
    assert queued["runtime"]["queue_position"] == 1
    assert queued["runtime"]["worker_id"] is None
    assert queued["runtime"]["progress_percent"] is None

    control.workers.register("worker-a", [], 1)
    job = control.queue.claim_next("worker-a", capabilities=[])
    assert job is not None

    claimed = control.dashboard.production_status(project_id)
    assert claimed["runtime"]["phase"] == "claimed"
    assert claimed["runtime"]["worker_id"] == "worker-a"
    assert claimed["runtime"]["job_status"] == "claimed"
    assert claimed["runtime"]["attempt"] == 1

    acked = control.queue.ack(job["key"], "worker-a")
    control.dashboard_store.start_execution(acked, "worker-a")
    control.dashboard_store.update_live_execution(
        job["key"],
        "worker-a",
        {
            "stage":"implementation",
            "progress":42,
            "usage":{"total_tokens":500},
        },
    )

    running = control.dashboard.production_status(project_id)
    assert running["runtime"]["phase"] == "running"
    assert running["runtime"]["worker_id"] == "worker-a"
    assert running["runtime"]["stage"] == "implementation"
    assert running["runtime"]["progress_percent"] == 42.0
    assert running["runtime"]["attempt"] == 1
    assert running["runtime"]["last_telemetry_at"]
    assert "42" in running["runtime"]["message"]


def test_production_status_validates_and_reports_missing_project(tmp_path):
    control = ControlPlane(str(tmp_path / "live-status-errors.sqlite"))

    with pytest.raises(ValueError, match="project_id is required"):
        control.dashboard.production_status("")

    with pytest.raises(DashboardNotFound):
        control.dashboard.production_status("missing-project")

def test_production_status_reports_cancelling_until_worker_acknowledges(tmp_path):
    control = ControlPlane(str(tmp_path / "cancel-status.sqlite"))
    project = control.managed_projects.create(
        repository="dbrckk/cancel-status",
        final_goal="Stop safely.",
        token_budget=30000,
        agent_preference="auto",
    )
    project_id = project["project_id"]
    control.workers.register("worker-a", [], 1)
    job = control.queue.claim_next("worker-a", capabilities=[])
    assert job is not None
    acked = control.queue.ack(job["key"], "worker-a")
    control.dashboard_store.start_execution(acked, "worker-a")

    result = control.dashboard.cancel_production(
        project_id,
        requested_by="operator:test",
    )
    assert result["status"] == "cancel_requested"

    status = control.dashboard.production_status(project_id)
    assert status["runtime"]["phase"] == "cancelling"
    assert status["runtime"]["cancel_requested"] is True
    assert "Annulation demandée" in status["runtime"]["message"]

    cancelled = control.queue.cancel(job["key"], "worker-a")
    control.dashboard_control.acknowledge_job_cancel(job["key"])
    control.dashboard_store.finish_execution(
        job["key"],
        "worker-a",
        status="cancelled",
        duration_seconds=None,
        result={"reason":"operator cancel"},
    )
    control.workflows.record_cancelled(
        cancelled["payload"]["workflow_id"],
        cancelled["payload"]["workflow_task_id"],
        result={"reason":"operator cancel"},
    )

    final = control.dashboard.production_status(project_id)
    assert final["runtime"]["phase"] == "needs_attention"
    assert final["runtime"]["cancel_requested"] is False
    assert final["project"]["current_workflow"]["status"] == "cancelled"

