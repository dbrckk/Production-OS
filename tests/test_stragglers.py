from datetime import datetime, timedelta, timezone

from production_os.execution_optimizer import ExecutionOptimizer
from production_os.sqlite_backend import SQLiteBackend, SQLiteJobQueue
from production_os.workers import Worker


def test_straggler_detection_with_alternate_worker(tmp_path):
    backend=SQLiteBackend(tmp_path/"db.sqlite")
    opt=ExecutionOptimizer(backend)
    for _ in range(3):
        opt.record_execution(
            repository="o/a",
            task="Build",
            worker_id="fast",
            duration_seconds=60,
            succeeded=True,
            capabilities=["python"],
        )
    queue=SQLiteJobQueue(backend)
    job=queue.enqueue({
        "handoff":{"repository":"o/a","task":"Build"},
        "required_capabilities":["python"],
    })
    queue.claim_next("slow",capabilities=["python"])
    old=(datetime.now(timezone.utc)-timedelta(minutes=4)).isoformat()
    with backend.transaction() as db:
        db.execute(
            "UPDATE jobs SET claimed_at=? WHERE key=?",
            (old,job["key"]),
        )

    rows=opt.stragglers(
        threshold_factor=1.5,
        min_runtime_seconds=1,
        min_samples=2,
        workers=[
            Worker("slow",["python"],1,1,"online",None),
            Worker("fast",["python"],1,0,"online",None),
        ],
    )
    assert len(rows)==1
    assert rows[0]["slowdown_ratio"] > 3
    assert rows[0]["alternate_worker"]["worker_id"]=="fast"
