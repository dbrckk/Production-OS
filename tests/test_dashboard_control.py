from __future__ import annotations

import pytest

from production_os.dashboard_control import DashboardControl
from production_os.dashboard_store import DashboardStore
from production_os.sqlite_backend import SQLiteBackend


def _store(tmp_path):
    return DashboardStore(SQLiteBackend(tmp_path / "db.sqlite"))


def test_missing_worker_control_row_defaults_to_active(tmp_path):
    control = DashboardControl(_store(tmp_path), None, None)
    state = control.worker_state("worker-a")
    assert state["desired_state"] == "active"
    assert state["persisted"] is False
    assert state["acknowledged_at"] is None


def test_pause_and_drain_are_durable(tmp_path):
    control = DashboardControl(_store(tmp_path), None, None)
    paused = control.set_worker_state(
        "worker-a", "paused", requested_by="operator:dashboard"
    )
    assert paused["desired_state"] == "paused"
    assert paused["persisted"] is True
    assert paused["acknowledged_at"] is None

    drained = control.set_worker_state(
        "worker-a", "draining", requested_by="operator:dashboard"
    )
    assert drained["desired_state"] == "draining"
    assert control.worker_state("worker-a")["desired_state"] == "draining"


def test_invalid_worker_desired_state_is_rejected(tmp_path):
    control = DashboardControl(_store(tmp_path), None, None)
    with pytest.raises(ValueError, match="invalid worker desired state"):
        control.set_worker_state("worker-a", "offline", requested_by="operator")


def test_worker_acknowledgement_requires_current_desired_state(tmp_path):
    control = DashboardControl(_store(tmp_path), None, None)
    control.set_worker_state("worker-a", "paused", requested_by="operator")
    with pytest.raises(ValueError, match="stale worker desired state"):
        control.acknowledge_worker_state("worker-a", "active")
    ack = control.acknowledge_worker_state("worker-a", "paused")
    assert ack["acknowledged_at"] is not None


def test_missing_job_control_row_defaults_to_active(tmp_path):
    control = DashboardControl(_store(tmp_path), None, None)
    state = control.job_state("job-a")
    assert state["desired_state"] == "active"
    assert state["persisted"] is False


def test_job_cancel_request_and_acknowledgement_are_durable(tmp_path):
    control = DashboardControl(_store(tmp_path), None, None)
    requested = control.request_job_cancel(
        "job-a", requested_by="operator:dashboard", reason="stop"
    )
    assert requested["desired_state"] == "cancel_requested"
    assert requested["acknowledged_at"] is None
    acknowledged = control.acknowledge_job_cancel("job-a")
    assert acknowledged["acknowledged_at"] is not None
