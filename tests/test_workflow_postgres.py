import os

import pytest

from production_os.postgres_backend import PostgresBackend, PostgresJobQueue
from production_os.workflow_engine import WorkflowEngine, WorkflowTaskSpec
from production_os.managed_projects import ManagedProjectService


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


def test_postgres_managed_project_review_lifecycle():
    backend=PostgresBackend(DSN)
    with backend.connect() as db:
        with db.cursor() as cur:
            cur.execute("TRUNCATE artifacts CASCADE")
            cur.execute("TRUNCATE workflow_tasks CASCADE")
            cur.execute("TRUNCATE workflows CASCADE")
            cur.execute("TRUNCATE jobs CASCADE")

    engine=WorkflowEngine(backend,PostgresJobQueue(backend))
    projects=ManagedProjectService(engine)
    project=projects.create(
        repository="o/managed",
        final_goal="Ship a verified release",
        token_budget=50000,
        agent_preference="codex",
    )
    assert project["state"]=="RUNNING"

    engine.record_result(
        project["workflow_id"],
        "goal",
        succeeded=True,
        result={"usage":{"total_tokens":321}},
    )
    review=projects.get(project["workflow_id"])
    assert review["state"]=="REVIEW_REQUIRED"
    assert review["usage"]["total_tokens"]==321

    resumed=projects.add_instruction(
        project["workflow_id"],
        "Polish mobile controls",
    )
    assert resumed["state"]=="RUNNING"
    engine.record_result(
        project["workflow_id"],
        "instruction-1",
        succeeded=True,
    )

    done=projects.mark_done(
        project["workflow_id"],
        approved_by="operator:test",
    )
    assert done["state"]=="DONE"
    assert done["approved_by"]=="operator:test"
