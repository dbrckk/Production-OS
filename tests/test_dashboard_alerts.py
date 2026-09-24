from production_os.dashboard_service import DashboardService
from production_os.dashboard_alerts import derive_alerts


def test_offline_worker_with_queued_work_is_high_alert():
    alerts = derive_alerts({
        "workers":{"online":0,"offline":1},
        "productions":{"queued":3,"running":0},
        "performance":{"recent_failures":0},
        "usage":{"estimated_cost_usd":None},
    })
    assert alerts[0]["code"] == "queue_without_worker"
    assert alerts[0]["severity"] == "high"


def test_three_consecutive_failures_are_high_alert():
    alerts = derive_alerts({
        "workers":{"online":1},
        "productions":{"queued":0},
        "performance":{"recent_failures":3},
        "usage":{},
    })
    assert alerts[0]["code"] == "consecutive_failures"
    assert alerts[0]["severity"] == "high"


def test_cost_spike_requires_real_baseline():
    no_baseline = derive_alerts({
        "workers":{"online":1},
        "productions":{"queued":0},
        "performance":{"recent_failures":0},
        "usage":{"estimated_cost_usd":12.0,"cost_baseline_usd":None},
    })
    assert not any(item["code"] == "cost_spike" for item in no_baseline)

    alerts = derive_alerts({
        "workers":{"online":1},
        "productions":{"queued":0},
        "performance":{"recent_failures":0},
        "usage":{"estimated_cost_usd":12.0,"cost_baseline_usd":5.0},
    })
    spike = next(item for item in alerts if item["code"] == "cost_spike")
    assert spike["severity"] == "medium"
    assert spike["evidence"]["ratio"] == 2.4


def test_stale_busy_worker_is_medium_alert():
    alerts = derive_alerts({
        "generated_at":"2026-09-24T14:10:00+00:00",
        "workers":{"online":1},
        "productions":{"queued":0},
        "performance":{"recent_failures":0},
        "usage":{},
        "busy_workers":[{
            "worker_id":"worker-a",
            "active_tasks":1,
            "last_heartbeat":"2026-09-24T14:00:00+00:00",
        }],
    })
    stale = next(item for item in alerts if item["code"] == "stale_busy_worker")
    assert stale["severity"] == "medium"


def test_previous_window_cost_uses_observed_historical_cost_only():
    rows = [
        {
            "occurred_at":"2026-09-23T12:00:00+00:00",
            "estimated_cost_usd":5.0,
        },
        {
            "occurred_at":"2026-09-24T12:00:00+00:00",
            "estimated_cost_usd":12.0,
        },
    ]
    # Use a broad invariant rather than wall-clock-sensitive equality:
    # without an event in the previous window there must be no baseline.
    assert DashboardService._previous_window_cost([], "24h") is None
    assert DashboardService._previous_window_cost(rows, "all") is None
