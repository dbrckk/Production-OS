from production_os.workers import WorkerRegistry


def test_worker_heartbeat_persists_capacity_snapshot(tmp_path):
    registry = WorkerRegistry(tmp_path / "workers.json")
    registry.register(
        "ai-dev-server-1",
        ["software-development", "repo-analysis"],
        1,
    )

    worker = registry.heartbeat(
        "ai-dev-server-1",
        active_tasks=1,
        capacity={
            "source": "omniroute",
            "status": "ok",
            "authenticated_usage": True,
            "steady_recurring_tokens": 1_500_000_000,
            "used_this_month": 125_000_000,
            "remaining_tokens": 1_375_000_000,
        },
    )

    assert worker.capacity["source"] == "omniroute"
    assert worker.capacity["remaining_tokens"] == 1_375_000_000

    reloaded = WorkerRegistry(tmp_path / "workers.json")
    assert (
        reloaded.workers["ai-dev-server-1"].capacity["steady_recurring_tokens"]
        == 1_500_000_000
    )


def test_worker_heartbeat_rejects_invalid_capacity_snapshot(tmp_path):
    registry = WorkerRegistry(tmp_path / "workers.json")
    registry.register("ai-dev-server-1", [], 1)

    try:
        registry.heartbeat(
            "ai-dev-server-1",
            capacity={
                "source": "omniroute",
                "status": "ok",
                "authenticated_usage": True,
                "steady_recurring_tokens": -1,
                "used_this_month": 0,
                "remaining_tokens": 0,
            },
        )
        assert False, "negative token capacity must be rejected"
    except ValueError as exc:
        assert "capacity" in str(exc)
