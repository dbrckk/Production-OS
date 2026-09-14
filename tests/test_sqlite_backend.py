from production_os.sqlite_backend import (
    SQLiteBackend,
    SQLiteJobQueue,
    SQLiteRuntimeState,
    SQLiteWorkerRegistry,
)


def test_sqlite_runtime_lease_is_transactional(tmp_path):
    backend=SQLiteBackend(tmp_path/"production.db")
    state=SQLiteRuntimeState(backend)
    first=state.acquire_lease("o/a","task","w1")
    assert first.status=="running"
    other=SQLiteRuntimeState(backend)
    try:
        other.acquire_lease("o/a","task","w2")
        assert False, "second lease must fail"
    except RuntimeError:
        pass


def test_sqlite_worker_registry(tmp_path):
    backend=SQLiteBackend(tmp_path/"production.db")
    workers=SQLiteWorkerRegistry(backend)
    worker=workers.register("python-1",["python"],2)
    assert worker.worker_id=="python-1"
    workers.adjust_active_tasks("python-1",1)
    assert workers.available()[0].active_tasks==1


def test_durable_queue_claim_and_complete(tmp_path):
    backend=SQLiteBackend(tmp_path/"production.db")
    queue=SQLiteJobQueue(backend)
    queued=queue.enqueue({
        "handoff":{
            "repository":"o/a",
            "task":"test",
            "priority":42,
        },
        "required_capabilities":["python"],
    })
    claimed=queue.claim_next("w1",capabilities=["python"])
    assert claimed["key"]==queued["key"]
    assert claimed["status"]=="claimed"
    assert queue.ack(queued["key"],"w1")["status"]=="acked"
    assert queue.complete(queued["key"],"w1")["status"]=="completed"
    assert backend.events_after()
