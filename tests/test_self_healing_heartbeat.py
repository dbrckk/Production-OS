from datetime import datetime, timedelta, timezone

from production_os.heartbeat_manager import renew_active_leases
from production_os.runtime_state import RuntimeState
from production_os.self_healing import apply_self_healing


def test_self_healing_replans_lost_lease(tmp_path):
    state = RuntimeState(tmp_path / "state.json")
    rec = state.get("o/a", "task")
    rec.status = "running"
    rec.lease_owner = "worker"
    rec.lease_expires_at = (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat()
    state.save()

    actions = apply_self_healing(state)
    assert actions
    assert state.get("o/a","task").status == "replan"


def test_heartbeat_manager_renews_matching_owner(tmp_path):
    state = RuntimeState(tmp_path / "state.json")
    state.acquire_lease("o/a","task","controller",minutes=1)
    results = renew_active_leases(state, owner="controller", minutes=10)
    assert results[0].renewed is True
