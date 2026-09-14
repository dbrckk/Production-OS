import os

import pytest

from production_os.postgres_backend import PostgresBackend, PostgresJobQueue
from production_os.workflow_engine import WorkflowEngine, WorkflowTaskSpec


DSN=os.getenv("PRODUCTION_OS_TEST_POSTGRES")


pytestmark=pytest.mark.skipif(
    not DSN,
    reason="PRODUCTION_OS_TEST_POSTGRES not configured",
)


def test_postgres_workflow_engine():
    backend=PostgresBackend(DSN)
    with backend.connect() as db:
        with db.cursor() as cur:
            cur.execute("TRUNCATE artifacts CASCADE")
            cur.execute("TRUNCATE workflow_tasks CASCADE")
            cur.execute("TRUNCATE workflows CASCADE")
            cur.execute("TRUNCATE jobs CASCADE")

    engine=WorkflowEngine(backend,PostgresJobQueue(backend))
    workflow=engine.create(
        name="pg-workflow",
        repository="o/pg",
        tasks=[
            WorkflowTaskSpec("a","A",{},estimated_minutes=2),
            WorkflowTaskSpec("b","B",{},("a",),estimated_minutes=3),
        ],
    )
    assert workflow["status"]=="running"
    first=engine.dispatch_ready(workflow["id"])
    assert len(first)==1
    engine.record_result(workflow["id"],"a",succeeded=True)
    current=engine.get(workflow["id"])
    assert next(
        task for task in current["tasks"] if task["task_id"]=="b"
    )["status"]=="queued"
    engine.record_result(workflow["id"],"b",succeeded=True)
    assert engine.get(workflow["id"])["status"]=="succeeded"
    assert engine.critical_path(workflow["id"])["estimated_minutes"]==5
