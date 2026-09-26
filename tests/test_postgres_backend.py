import os

import pytest

from production_os.postgres_backend import (
    PostgresBackend,
    PostgresJobQueue,
    PostgresRuntimeState,
    PostgresWorkerRegistry,
)


DSN=os.getenv("PRODUCTION_OS_TEST_POSTGRES")


pytestmark=pytest.mark.skipif(
    not DSN,
    reason="PRODUCTION_OS_TEST_POSTGRES not configured",
)


def reset(backend):
    with backend.connect() as db:
        with db.cursor() as cur:
            cur.execute("TRUNCATE events RESTART IDENTITY CASCADE")
            cur.execute("TRUNCATE jobs, claims, workers, runtime_records CASCADE")


def test_postgres_runtime_workers_and_queue():
    backend=PostgresBackend(DSN)
    reset(backend)

    state=PostgresRuntimeState(backend)
    lease=state.acquire_lease("o/a","task","worker-1")
    assert lease.status=="running"
    with pytest.raises(RuntimeError):
        PostgresRuntimeState(backend).acquire_lease(
            "o/a","task","worker-2"
        )

    workers=PostgresWorkerRegistry(backend)
    workers.register("worker-1",["python"],2)
    workers.adjust_active_tasks("worker-1",1)
    assert workers.available()[0].active_tasks==1

    queue=PostgresJobQueue(backend)
    queued=queue.enqueue({
        "handoff":{
            "repository":"o/b",
            "task":"job",
            "priority":10,
        },
        "required_capabilities":["python"],
    })
    claimed=queue.claim_next("worker-1",capabilities=["python"])
    assert claimed["key"]==queued["key"]
    assert queue.ack(queued["key"],"worker-1")["status"]=="acked"
    assert queue.complete(
        queued["key"],"worker-1"
    )["status"]=="completed"
    assert backend.events_after()

def test_postgres_queued_job_can_be_cancelled_without_worker():
    backend=PostgresBackend(DSN)
    reset(backend)
    queue=PostgresJobQueue(backend)
    queued=queue.enqueue({
        "handoff":{"repository":"o/cancel","task":"stop before claim"},
    })

    cancelled=queue.cancel_queued(queued["key"], reason="operator cancel")
    assert cancelled["status"]=="cancelled"
    assert cancelled["claimed_by"] is None
    assert cancelled["completed_at"]
    assert queue.peek_candidates()==[]

