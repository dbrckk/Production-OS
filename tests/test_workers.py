from production_os.workers import WorkerRegistry, select_worker


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
