import threading

import pytest

import production_os.controller as controller


def _kwargs(tmp_path):
    return {
        "owner":"owner",
        "runtime_state_path":str(tmp_path / "runtime.json"),
        "queue_dir":str(tmp_path / "queue"),
        "snapshot_dir":str(tmp_path / "snapshots"),
        "metrics_path":str(tmp_path / "metrics.json"),
        "health_path":str(tmp_path / "health.json"),
        "journal_path":str(tmp_path / "journal.jsonl"),
    }


def test_controller_cycles_zero_runs_until_stop_event(tmp_path, monkeypatch):
    stop = threading.Event()
    calls = []

    def fake_cycle(**_kwargs):
        calls.append(len(calls) + 1)
        if len(calls) == 3:
            stop.set()
        return {"cycle":len(calls)}

    monkeypatch.setattr(controller, "run_control_cycle", fake_cycle)

    results = controller.run_controller(
        cycles=0,
        interval_seconds=0,
        stop_event=stop,
        **_kwargs(tmp_path),
    )

    assert calls == [1, 2, 3]
    assert results == [{"cycle":1}, {"cycle":2}, {"cycle":3}]


def test_controller_stop_event_can_prevent_first_cycle(tmp_path, monkeypatch):
    stop = threading.Event()
    stop.set()

    def unexpected_cycle(**_kwargs):
        raise AssertionError("controller cycle should not run")

    monkeypatch.setattr(controller, "run_control_cycle", unexpected_cycle)

    assert controller.run_controller(
        cycles=0,
        interval_seconds=1,
        stop_event=stop,
        **_kwargs(tmp_path),
    ) == []


def test_controller_bounded_cycles_keep_existing_behavior(tmp_path, monkeypatch):
    calls = []

    def fake_cycle(**_kwargs):
        calls.append(1)
        return {"ok":True}

    monkeypatch.setattr(controller, "run_control_cycle", fake_cycle)
    monkeypatch.setattr(controller.time, "sleep", lambda _seconds: None)

    results = controller.run_controller(
        cycles=2,
        interval_seconds=1,
        **_kwargs(tmp_path),
    )

    assert len(calls) == 2
    assert results == [{"ok":True}, {"ok":True}]


@pytest.mark.parametrize("cycles", [-1, -10])
def test_controller_rejects_negative_cycles(tmp_path, cycles):
    with pytest.raises(ValueError, match="cycles must be >= 0"):
        controller.run_controller(
            cycles=cycles,
            interval_seconds=1,
            **_kwargs(tmp_path),
        )


def test_controller_rejects_negative_interval(tmp_path):
    with pytest.raises(ValueError, match="interval_seconds must be >= 0"):
        controller.run_controller(
            cycles=1,
            interval_seconds=-1,
            **_kwargs(tmp_path),
        )
