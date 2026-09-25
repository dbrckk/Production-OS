import pytest

from production_os.managed_projects import ManagedProjectService
from production_os.sqlite_backend import SQLiteBackend, SQLiteJobQueue
from production_os.workflow_engine import WorkflowEngine, WorkflowTaskSpec


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
    assert created["state"] == "RUNNING"
    assert created["token_budget"] == 250_000

    workflows.record_result(
        created["workflow_id"],
        "goal",
        succeeded=True,
        result={
            "usage":{
                "total_tokens":12_345,
                "runs":2,
                "agents":{"codex":2},
            }
        },
    )
    review = projects.get(created["workflow_id"])
    assert review["state"] == "REVIEW_REQUIRED"
    assert review["usage"]["total_tokens"] == 12_345
    assert review["usage"]["runs"] == 2
    assert review["usage"]["agents"] == {"codex":2}

    done = projects.mark_done(created["workflow_id"], approved_by="operator")
    assert done["state"] == "DONE"
    assert done["approved_by"] == "operator"


def test_managed_project_rejects_done_before_review(tmp_path):
    projects, _ = service(tmp_path)
    created = projects.create(
        repository="dbrckk/example",
        final_goal="Finish",
        token_budget=1000,
    )
    with pytest.raises(RuntimeError, match="REVIEW_REQUIRED"):
        projects.mark_done(created["workflow_id"], approved_by="operator")


def test_managed_project_accepts_followup_instruction_after_review(tmp_path):
    projects, workflows = service(tmp_path)
    created = projects.create(
        repository="dbrckk/example",
        final_goal="Ship",
        token_budget=10_000,
    )
    workflows.record_result(created["workflow_id"], "goal", succeeded=True)

    resumed = projects.add_instruction(
        created["workflow_id"],
        "Polish mobile controls",
    )
    assert resumed["state"] == "RUNNING"
    workflow = workflows.get(created["workflow_id"])
    task = next(x for x in workflow["tasks"] if x["task_id"] == "instruction-1")
    assert task["status"] == "queued"
    assert task["dependencies"] == ["goal"]


def test_managed_project_retest_queues_verification_task(tmp_path):
    projects, workflows = service(tmp_path)
    created = projects.create(
        repository="dbrckk/example",
        final_goal="Ship",
        token_budget=10_000,
    )
    workflows.record_result(created["workflow_id"], "goal", succeeded=True)
    running = projects.request_verification(created["workflow_id"])
    assert running["state"] == "RUNNING"
    workflow = workflows.get(created["workflow_id"])
    task = next(x for x in workflow["tasks"] if x["task_id"] == "verification-1")
    assert task["payload"]["phase"] == "verification"
    assert task["status"] == "queued"


def test_managed_project_list_excludes_normal_workflows(tmp_path):
    projects, workflows = service(tmp_path)
    created = projects.create(
        repository="dbrckk/example",
        final_goal="Ship",
        token_budget=10_000,
    )
    workflows.create(
        name="ordinary",
        repository="dbrckk/other",
        tasks=[
            WorkflowTaskSpec(
                task_id="ordinary",
                title="Ordinary task",
                payload={},
            )
        ],
    )
    listed = projects.list()
    assert [item["workflow_id"] for item in listed] == [created["workflow_id"]]


def test_managed_project_rejects_invalid_budget(tmp_path):
    projects, _ = service(tmp_path)
    with pytest.raises(ValueError, match="token_budget"):
        projects.create(
            repository="dbrckk/example",
            final_goal="Ship",
            token_budget=0,
        )
