import json
from contextlib import nullcontext
from pathlib import Path

import pytest

import production_os.controller as controller
from production_os.journal import ExecutionJournal
from production_os.metrics import MetricsStore
from production_os.runtime_state import RuntimeState


class StopAfterWaits:
    def __init__(self, count):
        self.count = count
        self.waits = []

    def is_set(self):
        return len(self.waits) >= self.count

    def wait(self, seconds):
        self.waits.append(seconds)
        return self.is_set()


def paths(tmp_path):
    return {
        "runtime_state_path": str(tmp_path / "runtime.json"),
        "metrics_path": str(tmp_path / "metrics.json"),
        "health_path": str(tmp_path / "health.json"),
        "journal_path": str(tmp_path / "journal.jsonl"),
    }


@pytest.mark.parametrize("state_source", ["database", "runtime-file"])
def test_unavailable_state_still_publishes_degraded_health(tmp_path, monkeypatch, state_source):
    config = paths(tmp_path)
    if state_source == "database":
        config["database_path"] = str(tmp_path / "production.db")

        def unavailable(_path):
            raise OSError("backend unavailable")

        monkeypatch.setattr(controller, "open_backend", unavailable)
    else:
        (tmp_path / "runtime.json").write_text("broken-json")

    controller._record_controller_error(RuntimeError("cycle failed"), config)

    health = json.loads((tmp_path / "health.json").read_text())
    assert health["status"] == "degraded"
    assert health["runtime"]["records"] is None
    assert health["runtime_status"] == "unavailable"
    assert health["metrics"]["last_error"] == "cycle failed"
    assert MetricsStore(config["metrics_path"]).metrics.cycles == 1


@pytest.mark.parametrize("metrics_failure", ["corrupt", "unwritable", "missing-config"])
def test_metrics_failure_does_not_prevent_health_publication(tmp_path, metrics_failure):
    config = paths(tmp_path)
    if metrics_failure == "corrupt":
        (tmp_path / "metrics.json").write_text("broken-json")
    elif metrics_failure == "unwritable":
        (tmp_path / "metrics.json").mkdir()
    else:
        config.pop("metrics_path")
    RuntimeState(config["runtime_state_path"]).save()

    controller._record_controller_error(RuntimeError("primary failure"), config)

    health = json.loads((tmp_path / "health.json").read_text())
    assert health["status"] == "degraded"
    assert health["runtime"]["records"] == 0
    assert health["metrics"]["last_error"] == "primary failure"
    if metrics_failure == "corrupt":
        assert (tmp_path / "metrics.json").read_text() == "broken-json"


@pytest.mark.parametrize("failed_output", ["metrics_path", "health_path", "journal_path", "all"])
def test_daemon_recovers_when_error_reporting_storage_fails(tmp_path, monkeypatch, failed_output):
    config = paths(tmp_path)
    for key in ("metrics_path", "health_path", "journal_path"):
        if failed_output in {key, "all"}:
            # A directory at a file destination fails even when tests run as root.
            Path(config[key]).mkdir()
    attempts = []

    def cycle(**_kwargs):
        attempts.append(len(attempts) + 1)
        if len(attempts) < 3:
            raise RuntimeError("cycle unavailable")
        return {"cycle": "recovered"}

    monkeypatch.setattr(controller, "run_control_cycle", cycle)
    monkeypatch.setattr(controller, "controller_leader_lock", lambda **_kwargs: nullcontext())
    stop = StopAfterWaits(3)

    summary = controller.run_controller_daemon(
        interval_seconds=2, max_error_backoff_seconds=3, stop_event=stop, **config,
    )

    assert attempts == [1, 2, 3]
    assert stop.waits == [2, 3, 2]
    assert summary["successful_cycles"] == 1
    assert summary["failed_cycles"] == 2
    assert summary["last_error"] is None
    if failed_output not in {"journal_path", "all"}:
        assert [event["consecutive_failures"] for event in ExecutionJournal(config["journal_path"]).read()] == [1, 2]


def test_bounded_controller_preserves_original_error_when_reporting_fails(tmp_path, monkeypatch):
    config = paths(tmp_path)
    (tmp_path / "metrics.json").write_text("broken-json")
    primary = RuntimeError("primary cycle failure")

    def cycle(**_kwargs):
        raise primary

    monkeypatch.setattr(controller, "run_control_cycle", cycle)

    with pytest.raises(RuntimeError) as caught:
        controller.run_controller(cycles=1, interval_seconds=1, **config)

    assert caught.value is primary


def test_metrics_can_be_recorded_without_runtime_configuration(tmp_path):
    config = {"metrics_path": str(tmp_path / "metrics.json")}

    controller._record_controller_error(RuntimeError("cycle failed"), config)

    assert MetricsStore(config["metrics_path"]).metrics.last_error == "cycle failed"


def test_readable_state_preserves_metrics_and_runtime_counts(tmp_path):
    config = paths(tmp_path)
    metrics = MetricsStore(config["metrics_path"])
    metrics.metrics.cycles = 7
    metrics.metrics.dispatched = 3
    metrics.save()
    state = RuntimeState(config["runtime_state_path"])
    state.get("owner/repo", "active task").status = "running"
    state.save()

    controller._record_controller_error(RuntimeError("cycle failed"), config)

    health = json.loads((tmp_path / "health.json").read_text())
    stored_metrics = MetricsStore(config["metrics_path"]).metrics.to_dict()
    assert health["metrics"] == stored_metrics
    assert health["metrics"]["cycles"] == 8
    assert health["metrics"]["dispatched"] == 3
    assert health["status"] == "degraded"
    assert health["runtime"]["running"] == 1


def test_metrics_save_failure_keeps_health_and_redacts_secondary_exception(tmp_path, monkeypatch, caplog):
    config = paths(tmp_path)

    def fail_save(_self):
        raise OSError("sensitive backend connection detail")

    monkeypatch.setattr(MetricsStore, "save", fail_save)

    controller._record_controller_error(RuntimeError("cycle failed"), config)

    health = json.loads((tmp_path / "health.json").read_text())
    assert health["metrics"]["cycles"] == 1
    assert health["status"] == "degraded"
    assert "OSError" in caplog.text
    assert "sensitive backend connection detail" not in caplog.text


def test_daemon_stops_cooperatively_during_persistent_reporting_failure(tmp_path, monkeypatch):
    config = paths(tmp_path)
    (tmp_path / "metrics.json").mkdir()

    def cycle(**_kwargs):
        raise RuntimeError("original cycle error")

    monkeypatch.setattr(controller, "run_control_cycle", cycle)
    monkeypatch.setattr(controller, "controller_leader_lock", lambda **_kwargs: nullcontext())
    stop = StopAfterWaits(2)

    summary = controller.run_controller_daemon(interval_seconds=1, stop_event=stop, **config)

    assert stop.waits == [1, 2]
    assert summary["failed_cycles"] == 2
    assert summary["successful_cycles"] == 0
    assert summary["last_error"] == "original cycle error"
