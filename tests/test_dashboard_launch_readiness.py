from production_os.control_plane import ControlPlane


def test_launch_readiness_distinguishes_immediate_execution_from_safe_queue(tmp_path):
    control = ControlPlane(str(tmp_path / "readiness.sqlite"))
    service = control.dashboard
    service.repositories = lambda: {
        "owner":"dbrckk",
        "source":"test",
        "repositories":[{"full_name":"dbrckk/example"}],
        "generated_at":"2026-09-25T19:00:00+00:00",
    }
    service.workers = lambda: {
        "workers":[],
        "generated_at":"2026-09-25T19:00:00+00:00",
    }

    queued = service.launch_readiness("dbrckk/example")

    assert queued["schema_version"] == "production-os/launch-readiness/v1"
    assert queued["repository"] == "dbrckk/example"
    assert queued["known_repository"] is True
    assert queued["can_launch"] is True
    assert queued["execution"] == "queued"
    assert queued["available_workers"] == 0
    assert queued["online_workers"] == 0
    assert queued["queued_jobs"] == 0

    service.workers = lambda: {
        "workers":[{
            "worker_id":"worker-a",
            "status":"online",
            "desired_state":"active",
            "active_tasks":0,
            "max_concurrency":2,
        }],
        "generated_at":"2026-09-25T19:00:00+00:00",
    }

    immediate = service.launch_readiness("dbrckk/example")

    assert immediate["execution"] == "immediate"
    assert immediate["available_workers"] == 1
    assert immediate["online_workers"] == 1


def test_launch_readiness_does_not_count_paused_or_saturated_workers(tmp_path):
    control = ControlPlane(str(tmp_path / "readiness-workers.sqlite"))
    service = control.dashboard
    service.repositories = lambda: {
        "owner":"dbrckk",
        "source":"test",
        "repositories":[{"full_name":"dbrckk/example"}],
        "generated_at":"2026-09-25T19:00:00+00:00",
    }
    service.workers = lambda: {
        "workers":[
            {
                "worker_id":"paused",
                "status":"online",
                "desired_state":"paused",
                "active_tasks":0,
                "max_concurrency":1,
            },
            {
                "worker_id":"full",
                "status":"online",
                "desired_state":"active",
                "active_tasks":1,
                "max_concurrency":1,
            },
        ],
        "generated_at":"2026-09-25T19:00:00+00:00",
    }

    result = service.launch_readiness("dbrckk/example")

    assert result["execution"] == "queued"
    assert result["online_workers"] == 2
    assert result["available_workers"] == 0


def test_launch_readiness_validates_repository_shape(tmp_path):
    control = ControlPlane(str(tmp_path / "readiness-invalid.sqlite"))

    try:
        control.dashboard.launch_readiness("../bad")
    except ValueError as exc:
        assert str(exc) == "repository must be owner/name"
    else:
        raise AssertionError("invalid repository should fail")
