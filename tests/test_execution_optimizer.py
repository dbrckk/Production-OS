from production_os.execution_optimizer import ExecutionOptimizer
from production_os.sqlite_backend import SQLiteBackend
from production_os.workers import Worker


def test_predictions_and_worker_placement(tmp_path):
    backend=SQLiteBackend(tmp_path/"db.sqlite")
    opt=ExecutionOptimizer(backend)
    for seconds in [60, 66, 72]:
        opt.record_execution(
            repository="o/a", task="Build", worker_id="fast",
            duration_seconds=seconds, succeeded=True,
            capabilities=["python"],
        )
    for seconds in [180, 190]:
        opt.record_execution(
            repository="o/a", task="Build", worker_id="slow",
            duration_seconds=seconds, succeeded=True,
            capabilities=["python"],
        )
    prediction=opt.task_prediction("o/a","Build")
    assert prediction["samples"]==5
    assert 1 < prediction["predicted_minutes"] < 3

    workers=[
        Worker("fast",["python"],1,0,"online",None),
        Worker("slow",["python"],1,0,"online",None),
    ]
    placement=opt.choose_worker(
        repository="o/a", task="Build", workers=workers,
        required_capabilities=["python"],
    )
    assert placement.worker_id=="fast"


def test_reliability_penalizes_flaky_worker(tmp_path):
    backend=SQLiteBackend(tmp_path/"db.sqlite")
    opt=ExecutionOptimizer(backend)
    for ok in [True,False,False,False]:
        opt.record_execution(
            repository="o/a",task="Test",worker_id="flaky",
            duration_seconds=30,succeeded=ok,
        )
    for _ in range(4):
        opt.record_execution(
            repository="o/a",task="Test",worker_id="stable",
            duration_seconds=60,succeeded=True,
        )
    workers=[
        Worker("flaky",[],1,0,"online",None),
        Worker("stable",[],1,0,"online",None),
    ]
    assert opt.choose_worker(
        repository="o/a",task="Test",workers=workers
    ).worker_id=="stable"
