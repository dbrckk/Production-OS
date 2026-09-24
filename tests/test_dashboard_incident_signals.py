from production_os.dashboard_incidents import dedupe_key, signals_from_health


def test_health_signals_expand_to_targeted_incidents():
    signals = signals_from_health({
        "reasons":[
            {
                "code":"queue_without_worker",
                "severity":"high",
                "evidence":{"queued":2,"online_workers":0},
            },
            {
                "code":"stale_busy_workers",
                "severity":"medium",
                "evidence":{"workers":[
                    {"worker_id":"worker-a","age_seconds":250.0},
                    {"worker_id":"worker-b","age_seconds":300.0},
                ]},
            },
            {
                "code":"stale_running_executions",
                "severity":"high",
                "evidence":{"executions":[
                    {"job_key":"job-a","worker_id":"worker-a","age_seconds":500.0},
                ]},
            },
        ]
    })
    assert len(signals) == 4
    assert {item["target_type"] for item in signals} == {
        "control-plane","worker","job"
    }
    keys = {dedupe_key(item) for item in signals}
    assert "stale_busy_workers:worker:worker-a" in keys
    assert "stale_running_executions:job:job-a" in keys
