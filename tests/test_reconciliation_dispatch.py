from datetime import datetime, timedelta, timezone

from production_os.dispatch import dispatch_handoff
from production_os.reconciliation import reconcile_runtime_state
from production_os.runtime_state import RuntimeState


def test_reconcile_expired_running_lease(tmp_path):
    state = RuntimeState(tmp_path / "state.json")
    rec = state.get("o/a", "task")
    rec.status = "running"
    rec.lease_owner = "worker"
    rec.lease_expires_at = (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat()
    state.save()

    actions = reconcile_runtime_state(state)
    assert actions
    assert state.get("o/a", "task").status == "replan"


def test_dispatch_is_idempotent_guarded(tmp_path):
    state = RuntimeState(tmp_path / "state.json")
    result = dispatch_handoff(
        {"repository":"o/a","task":"task"},
        tmp_path / "queue",
        state,
    )
    assert result.queue_file.endswith(".json")

    try:
        dispatch_handoff({"repository":"o/a","task":"task"}, tmp_path / "queue", state)
    except RuntimeError:
        pass
    else:
        raise AssertionError("second dispatch should be blocked by lease")
