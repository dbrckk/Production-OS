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


def test_postgres_worker_capacity_round_trip():
    backend=PostgresBackend(DSN)
    reset(backend)
    workers=PostgresWorkerRegistry(backend)
    workers.register("ai-dev",["software-development"],1)
    updated=workers.heartbeat(
        "ai-dev",
        capacity={
            "source":"omniroute",
            "status":"ok",
            "authenticated_usage":True,
            "steady_recurring_tokens":1_500_000_000,
            "used_this_month":125_000_000,
            "remaining_tokens":1_375_000_000,
            "catalog_updated_at":"2026-09-18",
            "catalog_source":"free-tier-catalog",
        },
    )
    assert updated.capacity["remaining_tokens"]==1_375_000_000
    reloaded=PostgresWorkerRegistry(backend)
    assert reloaded.workers["ai-dev"].capacity["source"]=="omniroute"
