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
def test_cooperative_project_routes_parallel_agents_then_specialists(tmp_path):
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
    code_task = _task(workflow, "implementation-code")
    tests_task = _task(workflow, "implementation-tests")
    assert code_task["status"] == "queued"
    assert tests_task["status"] == "queued"

    code_job = queue.claim_next(
        "worker-code",
        capabilities=["code-implementation"],
    )
    assert code_job is not None
    assert code_job["payload"]["handoff"]["isolation"]["mode"] == "git-worktree"
    code_branch = code_job["payload"]["handoff"]["isolation"]["branch"]

    tests_job = queue.claim_next(
        "worker-debug",
        capabilities=["test-debug"],
    )
    assert tests_job is not None
    assert tests_job["payload"]["handoff"]["isolation"]["mode"] == "git-worktree"
    tests_branch = tests_job["payload"]["handoff"]["isolation"]["branch"]
    assert tests_branch != code_branch

    workflows.record_result(
        workflow_id,
        "implementation-code",
        succeeded=True,
        result={
            "summary":"implemented dashboard change",
            "commit_shas":["a" * 40],
            "changed_files":["src/dashboard.py"],
        },
    )
    workflows.record_result(
        workflow_id,
        "implementation-tests",
        succeeded=True,
        result={
            "summary":"added dashboard tests",
            "commit_shas":["b" * 40],
            "changed_files":["tests/test_dashboard.py"],
        },
    )

    workflow = workflows.get(workflow_id)
    integration = _task(workflow, "integration")
    assert integration["status"] == "queued"
    integration_job = queue.claim_next(
        "worker-code-2",
        capabilities=["code-implementation"],
    )
    assert integration_job is not None
    upstream = integration_job["payload"]["handoff"]["upstream_context"]
    assert {row["task_id"] for row in upstream} == {
        "implementation-code",
        "implementation-tests",
    }
    commits = {
        row["task_id"]:row["commit_shas"][0]
        for row in upstream
    }
    assert commits["implementation-code"] == "a" * 40
    assert commits["implementation-tests"] == "b" * 40
    assert (
        integration_job["payload"]["handoff"]["isolation"][
            "integration_target"
        ]
        is True
    )

    workflows.record_result(
        workflow_id,
        "integration",
        succeeded=True,
        result={
            "summary":"integrated branches",
            "commit_shas":["c" * 40],
            "changed_files":[
                "src/dashboard.py",
                "tests/test_dashboard.py",
            ],
        },
    )

    workflow = workflows.get(workflow_id)
    validation = _task(workflow, "validation")
    assert validation["status"] == "queued"
    debug_job = queue.claim_next(
        "worker-debug-2",
        capabilities=["test-debug"],
    )
    assert debug_job is not None
    assert debug_job["payload"]["handoff"]["upstream_context"][0]["task_id"] == (
        "integration"
    )

    workflows.record_result(
        workflow_id,
        "validation",
        succeeded=True,
        result={
            "summary":"browser-facing tests passed",
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

    browser_job = queue.claim_next(
        "worker-browser",
        capabilities=["browser-ui-validation"],
    )
    assert browser_job is not None
    assert browser_job["payload"]["required_capabilities"] == [
        "browser-ui-validation"
    ]
    assert browser_job["payload"]["handoff"]["upstream_context"][0]["task_id"] == (
        "review"
    )

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
