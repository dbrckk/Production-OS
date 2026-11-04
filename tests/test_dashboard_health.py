from datetime import datetime, timezone
from production_os.dashboard_health import derive_control_health, is_worker_fresh


def test_health_is_healthy_without_operational_problems():
    result = derive_control_health({
        "generated_at":"2026-09-24T15:00:00+00:00",
        "workers":{"online":1},
        "productions":{"queued":0},
        "worker_rows":[],
        "running_executions":[],
    })
    assert result["status"] == "healthy"
    assert result["reasons"] == []


def test_queue_without_worker_degrades_health():
    result = derive_control_health({
        "generated_at":"2026-09-24T15:00:00+00:00",
        "workers":{"online":0},
        "productions":{"queued":2},
        "worker_rows":[],
        "running_executions":[],
    })
    assert result["status"] == "degraded"
    assert result["reasons"][0]["code"] == "queue_without_worker"


def test_stale_busy_worker_and_running_execution_are_explained():
    result = derive_control_health({
        "generated_at":"2026-09-24T15:10:00+00:00",
        "workers":{"online":1},
        "productions":{"queued":0},
        "worker_rows":[{
            "worker_id":"worker-a",
            "active_tasks":1,
            "last_heartbeat":"2026-09-24T15:00:00+00:00",
        }],
        "running_executions":[{
            "job_key":"job-a",
            "worker_id":"worker-a",
            "started_at":"2026-09-24T14:50:00+00:00",
            "last_telemetry_at":"2026-09-24T15:00:00+00:00",
        }],
    })
    codes = {item["code"] for item in result["reasons"]}
    assert codes == {"stale_busy_workers","stale_running_executions"}

def test_backup_filesystem_pressure_degrades_health_with_severity():
    warning = derive_control_health({
        "generated_at":"2026-09-24T15:00:00+00:00",
        "workers":{"online":1},
        "productions":{"queued":0},
        "worker_rows":[],
        "running_executions":[],
        "backup_storage":{
            "filesystem":{
                "status":"warning",
                "available_percent":8.5,
            }
        },
    })
    assert warning["status"] == "degraded"
    assert warning["reasons"] == [{
        "code":"backup_filesystem_capacity",
        "severity":"medium",
        "evidence":{"status":"warning","available_percent":8.5},
    }]

    critical = derive_control_health({
        "generated_at":"2026-09-24T15:00:00+00:00",
        "workers":{"online":1},
        "productions":{"queued":0},
        "worker_rows":[],
        "running_executions":[],
        "backup_storage":{
            "filesystem":{
                "status":"critical",
                "available_percent":4.0,
            }
        },
    })
    assert critical["status"] == "degraded"
    assert critical["reasons"][0]["severity"] == "high"



def test_worker_freshness_requires_recent_valid_heartbeat_and_online_status():
    now = datetime(2026, 11, 4, 10, 0, tzinfo=timezone.utc)
    fresh = {"status":"online", "last_heartbeat":"2026-11-04T09:59:00+00:00"}
    assert is_worker_fresh(fresh, now=now)
    assert not is_worker_fresh(
        {"status":"online", "last_heartbeat":"2026-10-26T15:59:42Z"},
        now=now,
    )
    assert not is_worker_fresh(
        {"status":"online", "last_heartbeat":"2026-11-04T10:05:00+00:00"},
        now=now,
    )
    assert not is_worker_fresh({"status":"online"}, now=now)
    assert not is_worker_fresh({**fresh, "status":"dead"}, now=now)
