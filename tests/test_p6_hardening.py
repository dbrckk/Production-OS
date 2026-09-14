from production_os.atomic_io import atomic_write_json
from production_os.audit_integrity import hash_event, verify_hash_chain
from production_os.emergency import clear_emergency_stop, emergency_stop_active, set_emergency_stop
from production_os.locks import sidecar_lock
from production_os.rate_limit import check_rate_limit


def test_atomic_write_and_lock(tmp_path):
    path = tmp_path / "state.json"
    with sidecar_lock(path):
        atomic_write_json(path, {"ok": True})
    assert path.read_text(encoding="utf-8").strip().startswith("{")


def test_emergency_stop(tmp_path):
    path = tmp_path / "stop.json"
    set_emergency_stop(path, reason="test")
    assert emergency_stop_active(path)
    clear_emergency_stop(path)
    assert not emergency_stop_active(path)


def test_audit_hash_chain(tmp_path):
    path = tmp_path / "audit.jsonl"
    prev = "0" * 64
    event = {"x": 1}
    h = hash_event(prev, event)
    path.write_text(
        '{"previous_hash":"' + prev + '","event_hash":"' + h + '","event":{"x":1}}\n',
        encoding="utf-8",
    )
    assert verify_hash_chain(path)["valid"] is True


def test_rate_limit():
    result = check_rate_limit([], limit=2, window_seconds=60)
    assert result.allowed is True
