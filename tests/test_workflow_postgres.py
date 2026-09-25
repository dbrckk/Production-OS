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
            cur.execute("TRUNCATE managed_project_runs CASCADE")
            cur.execute("TRUNCATE managed_projects CASCADE")
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
        requested_by="operator:test",
    )
    assert project["state"]=="RUNNING"
    assert project["generation"]==1
    first_workflow=project["workflow_id"]

    engine.record_result(
        first_workflow,
        "implementation",
        succeeded=True,
        result={"usage":{"total_tokens":321}},
    )
    review=projects.get(project["project_id"])
    assert review["state"]=="REVIEW_REQUIRED"
    assert review["usage"]["total_tokens"]==321

    resumed=projects.add_instruction(
        project["project_id"],
        "Polish mobile controls",
        requested_by="operator:test",
    )
    assert resumed["state"]=="RUNNING"
    assert resumed["generation"]==2
    assert resumed["workflow_id"]!=first_workflow
    second_workflow=resumed["workflow_id"]

    engine.record_result(
        second_workflow,
        "implementation",
        succeeded=True,
    )

    done=projects.mark_done(
        project["project_id"],
        approved_by="operator:test",
    )
    assert done["state"]=="DONE"
    assert done["approved_by"]=="operator:test"
    assert [run["generation"] for run in done["runs"]]==[1,2]
