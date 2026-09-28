from __future__ import annotations

from contextlib import nullcontext

import production_os.controller as controller
from production_os.cli import _parse_args


class FakeStopEvent:
    def __init__(self, stop_after_waits: int):
        self.stop_after_waits = stop_after_waits
        self.waits: list[int] = []

    def is_set(self) -> bool:
        return len(self.waits) >= self.stop_after_waits

    def wait(self, seconds: int) -> bool:
        self.waits.append(int(seconds))
        return self.is_set()


def test_controller_daemon_runs_until_cooperative_stop(monkeypatch):
    calls = {"count":0}

    def fake_cycle(**_kwargs):
        calls["count"] += 1
        return {"cycle":calls["count"]}

    monkeypatch.setattr(controller, "run_control_cycle", fake_cycle)
    monkeypatch.setattr(
        controller,
        "controller_leader_lock",
        lambda **_kwargs: nullcontext(),
    )
    stop = FakeStopEvent(3)

    summary = controller.run_controller_daemon(
        interval_seconds=5,
        stop_event=stop,
        result_history_limit=2,
    )

    assert calls["count"] == 3
    assert stop.waits == [5, 5, 5]
    assert summary["successful_cycles"] == 3
    assert summary["failed_cycles"] == 0
    assert summary["last_error"] is None
    assert summary["recent_results"] == [
        {"cycle":2},
        {"cycle":3},
    ]


def test_controller_daemon_retries_failures_with_bounded_backoff(monkeypatch):
    attempts = {"count":0}
    recorded = []

    def flaky_cycle(**_kwargs):
        attempts["count"] += 1
        if attempts["count"] <= 2:
            raise RuntimeError(f"boom-{attempts['count']}")
        return {"cycle":"recovered"}

    monkeypatch.setattr(controller, "run_control_cycle", flaky_cycle)
    monkeypatch.setattr(
        controller,
        "_record_controller_error",
        lambda exc, kwargs: recorded.append(str(exc)),
    )
    monkeypatch.setattr(
        controller,
        "controller_leader_lock",
        lambda **_kwargs: nullcontext(),
    )
    stop = FakeStopEvent(3)

    summary = controller.run_controller_daemon(
        interval_seconds=2,
        stop_event=stop,
        max_error_backoff_seconds=3,
    )

    assert attempts["count"] == 3
    assert recorded == ["boom-1", "boom-2"]
    assert stop.waits == [2, 3, 2]
    assert summary["successful_cycles"] == 1
    assert summary["failed_cycles"] == 2
    assert summary["last_error"] is None
    assert summary["recent_results"] == [{"cycle":"recovered"}]


def test_bounded_controller_behavior_is_unchanged(monkeypatch):
    calls = {"count":0}

    def fake_cycle(**_kwargs):
        calls["count"] += 1
        return {"cycle":calls["count"]}

    monkeypatch.setattr(controller, "run_control_cycle", fake_cycle)
    monkeypatch.setattr(controller.time, "sleep", lambda _seconds: None)

    results = controller.run_controller(
        cycles=2,
        interval_seconds=1,
    )

    assert results == [{"cycle":1}, {"cycle":2}]


def test_controller_cli_exposes_daemon_controls():
    args = _parse_args([
        "controller",
        "--owner", "owner",
        "--queue-dir", "/tmp/queue",
        "--snapshot-dir", "/tmp/snapshots",
        "--metrics", "/tmp/metrics.json",
        "--health", "/tmp/health.json",
        "--journal", "/tmp/journal.jsonl",
        "--daemon",
        "--max-error-backoff-seconds", "42",
        "--result-history-limit", "7",
    ])

    assert args.daemon is True
    assert args.max_error_backoff_seconds == 42
    assert args.result_history_limit == 7
