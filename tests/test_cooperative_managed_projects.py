from production_os.managed_projects import ManagedProjectService
from production_os.sqlite_backend import SQLiteBackend, SQLiteJobQueue
from production_os.workflow_engine import WorkflowEngine


def service(tmp_path):
    backend = SQLiteBackend(tmp_path / "cooperative.sqlite")
    return ManagedProjectService(
        WorkflowEngine(backend, SQLiteJobQueue(backend))
    )


def test_cooperative_workflow_builds_code_debug_review_chain_with_bounded_budget(tmp_path):
    managed = service(tmp_path)
    tasks = managed._cooperative_workflow_specs(
        project_id="project-1234",
        repository="o/a",
        final_goal="Implement repository automation safely",
        instruction="Implement repository automation safely",
        generation=1,
        kind="initial",
        token_budget=1000,
        agent_preference="auto",
    )

    assert [task.task_id for task in tasks] == [
        "implementation",
        "validation",
        "review",
    ]
    assert tasks[1].dependencies == ("implementation",)
    assert tasks[2].dependencies == ("validation",)
    budgets = [
        task.payload["handoff"]["token_budget"]
        for task in tasks
    ]
    assert sum(budgets) == 1000
    assert budgets == [550, 250, 200]


def test_cooperative_workflow_adds_ui_stage_only_for_ui_goal(tmp_path):
    managed = service(tmp_path)
    tasks = managed._cooperative_workflow_specs(
        project_id="project-1234",
        repository="o/a",
        final_goal="Improve the dashboard UI and verify it in the browser",
        instruction="Improve the dashboard UI",
        generation=1,
        kind="initial",
        token_budget=1000,
        agent_preference="auto",
    )

    assert [task.task_id for task in tasks] == [
        "implementation",
        "validation",
        "review",
        "ui-validation",
    ]
    assert tasks[-1].dependencies == ("review",)
    assert sum(
        task.payload["handoff"]["token_budget"]
        for task in tasks
    ) == 1000
    assert tasks[-1].payload["handoff"]["token_budget"] > 0


def test_create_cooperative_project_keeps_mode_in_workflow_metadata(tmp_path):
    managed = service(tmp_path)
    project = managed.create(
        repository="o/a",
        final_goal="Implement a tested backend change",
        token_budget=1000,
        cooperative=True,
        requested_by="operator:test",
    )

    workflow = managed.workflows.get(project["current_workflow_id"])
    assert workflow["metadata"]["cooperative"] is True
    assert [task["task_id"] for task in workflow["tasks"]] == [
        "implementation",
        "validation",
        "review",
    ]
