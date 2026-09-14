from datetime import datetime, timedelta, timezone

from production_os.runtime_state import RuntimeState


def test_lease_and_release(tmp_path):
    state = RuntimeState(tmp_path / "state.json")
    rec = state.acquire_lease("o/a", "task", "worker-1", minutes=5)
    assert rec.status == "running"
    assert state.is_leased(rec)

    rec = state.release_lease("o/a", "task")
    assert not state.is_leased(rec)


def test_circuit_breaker_opens_after_repeated_failures(tmp_path):
    state = RuntimeState(tmp_path / "state.json")
    state.record_outcome("o/a", "task", "rollback", retry_budget=10, circuit_breaker_failures=2)
    rec = state.record_outcome("o/a", "task", "rollback", retry_budget=10, circuit_breaker_failures=2, cooldown_minutes=30)
    assert rec.status == "circuit-open"
    assert state.in_cooldown(rec)
