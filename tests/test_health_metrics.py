from production_os.health import build_health
from production_os.metrics import MetricsStore
from production_os.runtime_state import RuntimeState


def test_health_degrades_with_open_circuit(tmp_path):
    state = RuntimeState(tmp_path / "state.json")
    rec = state.get("o/a","task")
    rec.status = "circuit-open"
    state.save()

    health = build_health(state, {"last_error":None})
    assert health["status"] == "degraded"


def test_metrics_persist(tmp_path):
    store = MetricsStore(tmp_path / "metrics.json")
    store.metrics.cycles = 2
    store.save()

    loaded = MetricsStore(tmp_path / "metrics.json")
    assert loaded.metrics.cycles == 2
