from datetime import datetime, timedelta, timezone

from production_os.claims import ClaimStore
from production_os.delivery import recover_unacked_jobs
from production_os.runtime_state import RuntimeState
from production_os.workers import WorkerRegistry


def test_claim_ack_complete(tmp_path):
    store=ClaimStore(tmp_path/"claims.json")
    claim=store.claim(
        key="k1",
        worker_id="w1",
        repository="o/a",
        task="t",
        ack_timeout_seconds=10,
    )
    assert claim.status=="claimed"
    assert store.ack("k1","w1").status=="acked"
    assert store.complete("k1","w1").status=="completed"


def test_recover_unacked_job_releases_capacity(tmp_path):
    claims=ClaimStore(tmp_path/"claims.json")
    runtime=RuntimeState(tmp_path/"runtime.json")
    workers=WorkerRegistry(tmp_path/"workers.json")
    workers.register("w1",["python"],1)
    workers.workers["w1"].active_tasks=1
    workers.save()
    runtime.acquire_lease("o/a","t","w1",minutes=30)

    claim=claims.claim(
        key=runtime.get("o/a","t").key,
        worker_id="w1",
        repository="o/a",
        task="t",
        ack_timeout_seconds=1,
    )
    claim.ack_deadline=(datetime.now(timezone.utc)-timedelta(seconds=1)).isoformat()
    claims.save()

    queue=tmp_path/"queue"
    queue.mkdir()
    (queue/f"{claim.key}.w1.json").write_text("{}",encoding="utf-8")

    rows=recover_unacked_jobs(
        claims=claims,
        runtime_state=runtime,
        workers=workers,
        queue_dir=queue,
    )
    assert rows
    assert workers.workers["w1"].active_tasks==0
