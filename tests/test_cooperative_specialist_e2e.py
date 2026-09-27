import pytest

from production_os.managed_projects import ManagedProjectService
from production_os.sqlite_backend import SQLiteBackend, SQLiteJobQueue
from production_os.workflow_engine import WorkflowEngine


def build(tmp_path):
    backend = SQLiteBackend(tmp_path / "cooperative-specialists.sqlite")
    queue = SQLiteJobQueue(backend)
    workflows = WorkflowEngine(backend, queue)
    managed = ManagedProjectService(workflows)
    return managed, workflows, queue


def _task(workflow, task_id):
    return next(
        task for task in workflow["tasks"]
        if task["task_id"] == task_id
    )


@pytest.mark.e2e
def test_cooperative_project_routes_sequentially_across_specialists(tmp_path):
    managed, workflows, queue = build(tmp_path)
    project = managed.create(
        repository="owner/app",
        final_goal="Improve the dashboard UI and verify it in the browser",
        token_budget=1000,
        cooperative=True,
        requested_by="operator:test",
    )
    workflow_id = project["current_workflow_id"]

    workflow = workflows.get(workflow_id)
    implementation = _task(workflow, "implementation")
    assert implementation["status"] == "queued"

    code_job = queue.claim_next(
        "worker-code",
        capabilities=["code-implementation"],
    )
    assert code_job is not None
    assert code_job["key"] == implementation["claimed_job_key"]
    assert code_job["payload"]["preferred_capabilities"] == [
        "code-implementation"
    ]
    assert code_job["payload"]["required_capabilities"] == []

    workflows.record_result(
        workflow_id,
        "implementation",
        succeeded=True,
        result={
            "summary":"implemented dashboard change",
            "commit_shas":["a" * 40],
            "changed_files":["src/dashboard.py"],
            "validation":{"status":"passed","tests":["unit"]},
        },
    )

    workflow = workflows.get(workflow_id)
    validation = _task(workflow, "validation")
    assert validation["status"] == "queued"
    debug_job = queue.claim_next(
        "worker-debug",
        capabilities=["test-debug"],
    )
    assert debug_job is not None
    assert debug_job["key"] == validation["claimed_job_key"]
    assert debug_job["payload"]["preferred_capabilities"] == ["test-debug"]
    upstream = debug_job["payload"]["handoff"]["upstream_context"]
    assert upstream[0]["task_id"] == "implementation"
    assert upstream[0]["summary"] == "implemented dashboard change"
    assert upstream[0]["commit_shas"] == ["a" * 40]

    workflows.record_result(
        workflow_id,
        "validation",
        succeeded=True,
        result={
            "summary":"browser-facing tests passed",
            "commit_shas":["b" * 40],
            "changed_files":["tests/test_dashboard.py"],
            "validation":{"status":"passed","tests":["unit","integration"]},
        },
    )

    workflow = workflows.get(workflow_id)
    review = _task(workflow, "review")
    assert review["status"] == "queued"
    review_job = queue.claim_next(
        "worker-review",
        capabilities=["code-review"],
    )
    assert review_job is not None
    assert review_job["key"] == review["claimed_job_key"]
    assert review_job["payload"]["preferred_capabilities"] == ["code-review"]
    assert review_job["payload"]["handoff"]["upstream_context"][0]["task_id"] == "validation"

    workflows.record_result(
        workflow_id,
        "review",
        succeeded=True,
        result={
            "summary":"review passed",
            "validation":{"status":"passed","tests":["review"]},
        },
    )

    workflow = workflows.get(workflow_id)
    ui = _task(workflow, "ui-validation")
    assert ui["status"] == "queued"

    assert queue.claim_next(
        "worker-generic",
        capabilities=[],
    ) is None
    assert queue.claim_next(
        "worker-code-2",
        capabilities=["code-implementation"],
    ) is None

    browser_job = queue.claim_next(
        "worker-browser",
        capabilities=["browser-ui-validation"],
    )
    assert browser_job is not None
    assert browser_job["key"] == ui["claimed_job_key"]
    assert browser_job["payload"]["required_capabilities"] == [
        "browser-ui-validation"
    ]
    assert browser_job["payload"]["preferred_capabilities"] == [
        "browser-ui-validation"
    ]
    assert browser_job["payload"]["handoff"]["upstream_context"][0]["task_id"] == "review"

    workflows.record_result(
        workflow_id,
        "ui-validation",
        succeeded=True,
        result={
            "summary":"real browser validation passed",
            "validation":{"status":"passed","tests":["playwright-chromium"]},
        },
    )

    completed = workflows.get(workflow_id)
    assert completed["status"] == "succeeded"
    assert all(
        task["status"] == "succeeded"
        for task in completed["tasks"]
    )
