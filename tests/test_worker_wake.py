from production_os.control_plane import ControlPlane
from production_os.worker_wake import request_automatic_worker_wake


def test_shared_wake_dispatches_and_audits_when_no_worker_is_registered(
    tmp_path,
    monkeypatch,
):
    control = ControlPlane(str(tmp_path / "wake.sqlite"))
    calls = []
    monkeypatch.setattr(
        control.dashboard_control,
        "kick_worker",
        lambda worker_id: (
            calls.append(worker_id)
            or {"status":"dispatched"}
        ),
    )

    result = request_automatic_worker_wake(
        workers=control.workers,
        dashboard_control=control.dashboard_control,
        store=control.dashboard_store,
        requested_by="controller:auto",
    )

    assert result == {"status":"dispatched"}
    assert calls == ["automatic-launch"]
    audit = control.dashboard_store.control_audit_events(limit=5)
    assert audit[0]["requested_by"] == "controller:auto"
    assert audit[0]["outcome"] == "dispatched"


def test_shared_wake_respects_online_worker_and_operator_pause(
    tmp_path,
    monkeypatch,
):
    control = ControlPlane(str(tmp_path / "wake-policy.sqlite"))
    worker = control.workers.register("worker-a", ["python"], 1)
    monkeypatch.setattr(control.workers, "detect_dead", lambda *args, **kwargs: [])

    assert request_automatic_worker_wake(
        workers=control.workers,
        dashboard_control=control.dashboard_control,
        store=control.dashboard_store,
        requested_by="controller:auto",
    ) == {"status":"not_needed"}

    control.workers.load()
    control.workers.workers[worker.worker_id].status = "dead"
    control.workers.save()
    control.dashboard_control.set_worker_state(
        worker.worker_id,
        "paused",
        requested_by="operator:test",
    )

    assert request_automatic_worker_wake(
        workers=control.workers,
        dashboard_control=control.dashboard_control,
        store=control.dashboard_store,
        requested_by="controller:auto",
    ) == {"status":"not_needed"}


def test_shared_wake_uses_durable_cooldown(tmp_path, monkeypatch):
    control = ControlPlane(str(tmp_path / "wake-cooldown.sqlite"))
    control.dashboard_store.append_control_audit(
        action="kick",
        worker_id="automatic-launch",
        requested_by="controller:auto",
        outcome="dispatched",
    )
    calls = []
    monkeypatch.setattr(
        control.dashboard_control,
        "kick_worker",
        lambda worker_id: calls.append(worker_id) or {"status":"dispatched"},
    )

    result = request_automatic_worker_wake(
        workers=control.workers,
        dashboard_control=control.dashboard_control,
        store=control.dashboard_store,
        requested_by="controller:auto",
    )

    assert result == {
        "status":"cooldown",
        "cooldown_seconds":60,
    }
    assert calls == []


def test_shared_wake_does_not_fail_durable_work_when_audit_write_fails(
    tmp_path,
    monkeypatch,
):
    control = ControlPlane(str(tmp_path / "wake-audit.sqlite"))
    monkeypatch.setattr(
        control.dashboard_control,
        "kick_worker",
        lambda _worker_id: {"status":"dispatched"},
    )
    monkeypatch.setattr(
        control.dashboard_store,
        "append_control_audit",
        lambda **_kwargs: (_ for _ in ()).throw(RuntimeError("audit unavailable")),
    )

    result = request_automatic_worker_wake(
        workers=control.workers,
        dashboard_control=control.dashboard_control,
        store=control.dashboard_store,
        requested_by="controller:auto",
    )

    assert result == {
        "status":"dispatched",
        "audit_recorded":False,
    }



def test_shared_wake_dispatches_when_online_worker_lacks_required_capability(
    tmp_path,
    monkeypatch,
):
    control = ControlPlane(str(tmp_path / "wake-capability-gap.sqlite"))
    control.workers.register("worker-python", ["python"], 1)
    monkeypatch.setattr(control.workers, "detect_dead", lambda *args, **kwargs: [])
    queued = [{
        "key":"job-visual",
        "assigned_worker":None,
        "payload":{"required_capabilities":["visual-asset-production"]},
    }]
    calls = []
    monkeypatch.setattr(
        control.dashboard_control,
        "kick_worker",
        lambda worker_id: calls.append(worker_id) or {"status":"dispatched"},
    )

    result = request_automatic_worker_wake(
        workers=control.workers,
        dashboard_control=control.dashboard_control,
        store=control.dashboard_store,
        requested_by="controller:auto",
        queued_jobs=queued,
    )

    assert result == {"status":"dispatched"}
    assert calls == ["automatic-launch"]


def test_shared_wake_skips_when_online_worker_can_claim_all_queued_work(
    tmp_path,
    monkeypatch,
):
    control = ControlPlane(str(tmp_path / "wake-compatible.sqlite"))
    control.workers.register(
        "worker-visual",
        ["python", "visual-asset-production"],
        1,
    )
    monkeypatch.setattr(control.workers, "detect_dead", lambda *args, **kwargs: [])
    queued = [{
        "key":"job-visual",
        "assigned_worker":None,
        "payload":{"required_capabilities":["visual-asset-production"]},
    }]
    calls = []
    monkeypatch.setattr(
        control.dashboard_control,
        "kick_worker",
        lambda worker_id: calls.append(worker_id) or {"status":"dispatched"},
    )

    result = request_automatic_worker_wake(
        workers=control.workers,
        dashboard_control=control.dashboard_control,
        store=control.dashboard_store,
        requested_by="controller:auto",
        queued_jobs=queued,
    )

    assert result == {"status":"not_needed"}
    assert calls == []


def test_shared_wake_respects_assigned_worker_when_evaluating_compatibility(
    tmp_path,
    monkeypatch,
):
    control = ControlPlane(str(tmp_path / "wake-assigned.sqlite"))
    control.workers.register(
        "worker-a",
        ["python", "visual-asset-production"],
        1,
    )
    control.workers.register(
        "worker-b",
        ["python", "visual-asset-production"],
        1,
    )
    monkeypatch.setattr(control.workers, "detect_dead", lambda *args, **kwargs: [])
    control.workers.load()
    control.workers.workers["worker-b"].status = "dead"
    control.workers.save()
    queued = [{
        "key":"job-assigned",
        "assigned_worker":"worker-b",
        "payload":{"required_capabilities":["visual-asset-production"]},
    }]
    calls = []
    monkeypatch.setattr(
        control.dashboard_control,
        "kick_worker",
        lambda worker_id: calls.append(worker_id) or {"status":"dispatched"},
    )

    result = request_automatic_worker_wake(
        workers=control.workers,
        dashboard_control=control.dashboard_control,
        store=control.dashboard_store,
        requested_by="controller:auto",
        queued_jobs=queued,
    )

    assert result == {"status":"dispatched"}
    assert calls == ["automatic-launch"]


def test_control_plane_wake_checks_all_queued_capability_requirements(
    tmp_path,
    monkeypatch,
):
    control = ControlPlane(str(tmp_path / "wake-control-plane.sqlite"))
    control.workers.register("worker-python", ["python"], 1)
    monkeypatch.setattr(control.workers, "detect_dead", lambda *args, **kwargs: [])
    control.queue.enqueue({
        "idempotency_key":"job-basic",
        "handoff":{"repository":"owner/repo", "task":"basic", "priority":100},
        "required_capabilities":["python"],
    })
    control.queue.enqueue({
        "idempotency_key":"job-visual",
        "handoff":{"repository":"owner/repo", "task":"visual", "priority":10},
        "required_capabilities":["visual-asset-production"],
    })
    calls = []
    monkeypatch.setattr(
        control.dashboard_control,
        "kick_worker",
        lambda worker_id: calls.append(worker_id) or {"status":"dispatched"},
    )

    result = control.ensure_worker_for_queued_work(requested_by="operator:test")

    assert result == {"status":"dispatched"}
    assert calls == ["automatic-launch"]



def test_control_plane_wake_ignores_cancel_requested_jobs(
    tmp_path,
    monkeypatch,
):
    control = ControlPlane(str(tmp_path / "wake-cancel-requested.sqlite"))
    control.queue.enqueue({
        "idempotency_key":"job-cancelled-logically",
        "handoff":{"repository":"owner/repo", "task":"visual", "priority":10},
        "required_capabilities":["visual-asset-production"],
    })
    monkeypatch.setattr(
        control.dashboard_control,
        "job_state",
        lambda _key: {"desired_state":"cancel_requested"},
    )
    calls = []
    monkeypatch.setattr(
        control.dashboard_control,
        "kick_worker",
        lambda worker_id: calls.append(worker_id) or {"status":"dispatched"},
    )

    result = control.ensure_worker_for_queued_work(requested_by="operator:test")

    assert result == {
        "status":"not_needed",
        "reason":"no_actionable_queued_work",
    }
    assert calls == []


def test_control_plane_wake_ignores_stale_workflow_generation(
    tmp_path,
    monkeypatch,
):
    control = ControlPlane(str(tmp_path / "wake-stale-generation.sqlite"))
    control.queue.enqueue({
        "idempotency_key":"job-stale-generation",
        "handoff":{"repository":"owner/repo", "task":"visual", "priority":10},
        "required_capabilities":["visual-asset-production"],
    })
    monkeypatch.setattr(
        control.workflows,
        "job_generation_current",
        lambda _job: False,
    )
    calls = []
    monkeypatch.setattr(
        control.dashboard_control,
        "kick_worker",
        lambda worker_id: calls.append(worker_id) or {"status":"dispatched"},
    )

    result = control.ensure_worker_for_queued_work(requested_by="operator:test")

    assert result == {
        "status":"not_needed",
        "reason":"no_actionable_queued_work",
    }
    assert calls == []


def test_queued_job_wakes_short_lived_actions_worker_despite_online_heartbeat(
    tmp_path, monkeypatch,
):
    control = ControlPlane(str(tmp_path / "ephemeral-online.sqlite"))
    control.workers.register("github-actions-worker", ["python"], 1)
    monkeypatch.setattr(control.workers, "detect_dead", lambda *a, **kw: [])
    calls = []
    monkeypatch.setattr(
        control.dashboard_control, "kick_worker",
        lambda worker_id: calls.append(worker_id) or {"status": "dispatched"},
    )
    queued = [{
        "key": "new-task",
        "payload": {"required_capabilities": ["python"]},
    }]

    response = request_automatic_worker_wake(
        workers=control.workers,
        dashboard_control=control.dashboard_control,
        store=control.dashboard_store,
        requested_by="dashboard:launch",
        queued_jobs=queued,
    )

    assert response == {"status": "dispatched"}
    assert calls == ["automatic-launch"]


def test_actions_worker_with_no_queued_work_needs_no_wake(tmp_path, monkeypatch):
    control = ControlPlane(str(tmp_path / "ephemeral-idle.sqlite"))
    control.workers.register("github-actions-worker", ["python"], 1)
    monkeypatch.setattr(control.workers, "detect_dead", lambda *a, **kw: [])
    calls = []
    monkeypatch.setattr(
        control.dashboard_control, "kick_worker",
        lambda worker_id: calls.append(worker_id) or {"status": "dispatched"},
    )

    response = request_automatic_worker_wake(
        workers=control.workers,
        dashboard_control=control.dashboard_control,
        store=control.dashboard_store,
        requested_by="controller:auto",
        queued_jobs=[],
    )

    assert response == {"status": "not_needed"}
    assert calls == []


def test_busy_persistent_worker_cannot_suppress_queued_work_wake(
    tmp_path, monkeypatch,
):
    control = ControlPlane(str(tmp_path / "busy-worker.sqlite"))
    control.workers.register("worker-persistent", ["python"], 1)
    control.workers.heartbeat("worker-persistent", active_tasks=1)
    monkeypatch.setattr(control.workers, "detect_dead", lambda *a, **kw: [])
    calls = []
    monkeypatch.setattr(
        control.dashboard_control, "kick_worker",
        lambda worker_id: calls.append(worker_id) or {"status": "dispatched"},
    )

    result = request_automatic_worker_wake(
        workers=control.workers,
        dashboard_control=control.dashboard_control,
        store=control.dashboard_store,
        requested_by="controller:auto",
        queued_jobs=[{
            "key": "queued",
            "payload": {"required_capabilities": ["python"]},
        }],
    )

    assert result == {"status": "dispatched"}
    assert calls == ["automatic-launch"]


def test_available_persistent_worker_prevents_unnecessary_actions_dispatch(
    tmp_path, monkeypatch,
):
    control = ControlPlane(str(tmp_path / "persistent-available.sqlite"))
    control.workers.register("github-actions-worker", ["python"], 1)
    control.workers.register("worker-persistent", ["python"], 1)
    monkeypatch.setattr(control.workers, "detect_dead", lambda *a, **kw: [])
    calls = []
    monkeypatch.setattr(
        control.dashboard_control, "kick_worker",
        lambda worker_id: calls.append(worker_id) or {"status": "dispatched"},
    )

    result = request_automatic_worker_wake(
        workers=control.workers,
        dashboard_control=control.dashboard_control,
        store=control.dashboard_store,
        requested_by="controller:auto",
        queued_jobs=[{
            "key": "queued",
            "payload": {"required_capabilities": ["python"]},
        }],
    )

    assert result == {"status": "not_needed"}
    assert calls == []


def test_custom_ephemeral_worker_ids_are_configurable(tmp_path, monkeypatch):
    control = ControlPlane(str(tmp_path / "custom-ephemeral.sqlite"))
    control.workers.register("actions-custom", ["python"], 1)
    monkeypatch.setenv("PRODUCTION_OS_EPHEMERAL_WORKER_IDS", "actions-custom")
    monkeypatch.setattr(control.workers, "detect_dead", lambda *a, **kw: [])
    calls = []
    monkeypatch.setattr(
        control.dashboard_control, "kick_worker",
        lambda worker_id: calls.append(worker_id) or {"status": "dispatched"},
    )

    result = request_automatic_worker_wake(
        workers=control.workers,
        dashboard_control=control.dashboard_control,
        store=control.dashboard_store,
        requested_by="controller:auto",
        queued_jobs=[{
            "key": "queued",
            "payload": {"required_capabilities": ["python"]},
        }],
    )

    assert result == {"status": "dispatched"}
    assert calls == ["automatic-launch"]
