from production_os.workers import (
    WorkerRegistry,
    cooperative_worker_fleet_available,
    select_worker,
)


def test_selects_least_loaded_capable_worker(tmp_path):
    registry=WorkerRegistry(tmp_path/"workers.json")
    a=registry.register("a",["python","android"],2)
    b=registry.register("b",["python"],2)
    registry.heartbeat("a",active_tasks=1)
    registry.heartbeat("b",active_tasks=0)
    selected=select_worker(registry,["python"])
    assert selected.worker_id=="b"


def test_rejects_worker_without_required_capability(tmp_path):
    registry=WorkerRegistry(tmp_path/"workers.json")
    registry.register("a",["python"],1)
    assert select_worker(registry,["android"]) is None



def test_cooperative_worker_fleet_accepts_any_online_specialist(tmp_path):
    registry = WorkerRegistry(tmp_path / "workers.json")
    registry.register("code", ["code-implementation"], 1)

    assert cooperative_worker_fleet_available(registry) is True


def test_cooperative_worker_fleet_rejects_missing_specialist(tmp_path):
    registry = WorkerRegistry(tmp_path / "workers.json")
    registry.register("plain", ["python"], 1)

    assert cooperative_worker_fleet_available(registry) is False


def test_cooperative_worker_fleet_requires_browser_specialist(tmp_path):
    registry = WorkerRegistry(tmp_path / "workers.json")
    registry.register("code", ["code-implementation"], 1)

    assert cooperative_worker_fleet_available(
        registry,
        needs_browser=True,
    ) is False

    registry.register("browser", ["browser-ui-validation"], 1)
    assert cooperative_worker_fleet_available(
        registry,
        needs_browser=True,
    ) is True


def test_cooperative_worker_fleet_requires_mobile_specialist(tmp_path):
    registry = WorkerRegistry(tmp_path / "workers.json")
    registry.register("browser", ["browser-ui-validation"], 1)

    assert cooperative_worker_fleet_available(
        registry,
        needs_mobile=True,
    ) is False

    registry.register("mobile", ["mobile-ui-validation"], 1)
    assert cooperative_worker_fleet_available(
        registry,
        needs_mobile=True,
    ) is True


def test_cooperative_worker_fleet_excludes_dead_workers(tmp_path):
    registry = WorkerRegistry(tmp_path / "workers.json")
    worker = registry.register("browser", ["browser-ui-validation"], 1)
    worker.status = "dead"
    registry.save()

    assert cooperative_worker_fleet_available(
        registry,
        needs_browser=True,
    ) is False


def test_cooperative_worker_fleet_preserves_full_online_worker_semantics(tmp_path):
    registry = WorkerRegistry(tmp_path / "workers.json")
    registry.register("browser", ["browser-ui-validation"], 1)
    registry.heartbeat("browser", active_tasks=1)

    assert cooperative_worker_fleet_available(
        registry,
        needs_browser=True,
    ) is True
