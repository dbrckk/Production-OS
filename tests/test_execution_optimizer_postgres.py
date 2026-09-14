import os

import pytest

from production_os.execution_optimizer import ExecutionOptimizer
from production_os.postgres_backend import PostgresBackend
from production_os.workers import Worker


DSN=os.getenv("PRODUCTION_OS_TEST_POSTGRES")
pytestmark=pytest.mark.skipif(not DSN,reason="postgres not configured")


def test_optimizer_postgres():
    backend=PostgresBackend(DSN)
    with backend.connect() as db:
        with db.cursor() as cur:
            cur.execute("TRUNCATE execution_history RESTART IDENTITY")
    opt=ExecutionOptimizer(backend)
    opt.record_execution(
        repository="o/a",task="Build",worker_id="w1",
        duration_seconds=60,succeeded=True,capabilities=["python"],
    )
    opt.record_execution(
        repository="o/a",task="Build",worker_id="w2",
        duration_seconds=120,succeeded=True,capabilities=["python"],
    )
    assert opt.task_prediction("o/a","Build")["samples"]==2
    placement=opt.choose_worker(
        repository="o/a",task="Build",
        workers=[
            Worker("w1",["python"],1,0,"online",None),
            Worker("w2",["python"],1,0,"online",None),
        ],
        required_capabilities=["python"],
    )
    assert placement.worker_id=="w1"
