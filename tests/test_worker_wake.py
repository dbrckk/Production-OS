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
