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
        result={
            "usage": {
                "total_tokens": 12_345,
                "runs": 2,
                "agents": {"codex": 2},
            }
        },
    )

    review = projects.get(created["workflow_id"])
    assert review["state"] == "REVIEW_REQUIRED"
    assert review["usage"]["total_tokens"] == 12_345
    assert review["usage"]["runs"] == 2
    assert review["usage"]["agents"] == {"codex": 2}

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


def test_managed_project_starts_dispatch_and_accepts_follow_up_instruction(tmp_path):
    projects, workflows = service(tmp_path)
    created = projects.create(
        repository="dbrckk/example",
        final_goal="Ship the release",
        token_budget=50_000,
        agent_preference="codex",
    )

    first = workflows.get(created["workflow_id"])["tasks"][0]
    assert first["task_id"] == "goal"
    assert first["status"] == "queued"

    workflows.record_result(
        created["workflow_id"],
        "goal",
        succeeded=True,
        result={"usage": {"total_tokens": 100}},
    )
    assert projects.get(created["workflow_id"])["state"] == "REVIEW_REQUIRED"

    resumed = projects.add_instruction(
        created["workflow_id"],
        "Improve the mobile controls before final approval",
    )
    assert resumed["state"] == "RUNNING"

    workflow = workflows.get(created["workflow_id"])
    follow_up = next(
        task for task in workflow["tasks"]
        if task["task_id"] == "instruction-1"
    )
    assert follow_up["status"] == "queued"
    assert follow_up["payload"]["handoff"]["task"] == (
        "Improve the mobile controls before final approval"
    )
    assert "goal" in follow_up["dependencies"]


def test_managed_project_retest_adds_real_verification_task(tmp_path):
    projects, workflows = service(tmp_path)
    created = projects.create(
        repository="dbrckk/example",
        final_goal="Ship the release",
        token_budget=50_000,
    )
    workflows.record_result(created["workflow_id"], "goal", succeeded=True)

    running = projects.request_verification(created["workflow_id"])
    assert running["state"] == "RUNNING"

    workflow = workflows.get(created["workflow_id"])
    verification = next(
        task for task in workflow["tasks"]
        if task["task_id"] == "verification-1"
    )
    assert verification["status"] == "queued"
    assert verification["payload"]["phase"] == "verification"
    assert verification["payload"]["handoff"]["final_goal"] == "Ship the release"
