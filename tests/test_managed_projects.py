import pytest

from production_os.managed_projects import ManagedProjectService
from production_os.sqlite_backend import SQLiteBackend, SQLiteJobQueue
from production_os.workflow_engine import WorkflowEngine


def service(tmp_path):
    backend = SQLiteBackend(tmp_path / "db.sqlite")
    queue = SQLiteJobQueue(backend)
    workflows = WorkflowEngine(backend, queue)
    return ManagedProjectService(workflows), workflows


def test_managed_project_requires_human_completion_after_execution(tmp_path):
    projects, workflows = service(tmp_path)
    created = projects.create(
        repository="dbrckk/example",
        final_goal="Ship a verified playable release",
        token_budget=250_000,
        agent_preference="codex",
    )

    assert created["repository"] == "dbrckk/example"
    assert created["final_goal"] == "Ship a verified playable release"
    assert created["token_budget"] == 250_000
    assert created["agent_preference"] == "codex"
    assert created["state"] == "RUNNING"

    workflow = workflows.get(created["workflow_id"])
    assert workflow["metadata"]["managed_project"]["final_goal"] == created["final_goal"]
    assert workflow["tasks"][0]["payload"]["handoff"]["task"] == created["final_goal"]

    workflows.dispatch_ready(created["workflow_id"])
    workflows.record_result(
        created["workflow_id"],
        "goal",
        succeeded=True,
        result={"usage": {"total_tokens": 12_345}},
    )

    review = projects.get(created["workflow_id"])
    assert review["state"] == "REVIEW_REQUIRED"
    assert review["usage"]["total_tokens"] == 12_345

    done = projects.mark_done(created["workflow_id"], approved_by="operator")
    assert done["state"] == "DONE"
    assert done["approved_by"] == "operator"


def test_managed_project_cannot_be_marked_done_before_execution_succeeds(tmp_path):
    projects, _ = service(tmp_path)
    created = projects.create(
        repository="dbrckk/example",
        final_goal="Finish the project",
        token_budget=10_000,
    )

    with pytest.raises(RuntimeError, match="REVIEW_REQUIRED"):
        projects.mark_done(created["workflow_id"], approved_by="operator")


def test_managed_project_rejects_invalid_budget(tmp_path):
    projects, _ = service(tmp_path)

    with pytest.raises(ValueError, match="token_budget"):
        projects.create(
            repository="dbrckk/example",
            final_goal="Finish the project",
            token_budget=0,
        )
