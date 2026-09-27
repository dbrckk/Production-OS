import pytest

from production_os.managed_projects import ManagedProjectService, _outcome_from_workflow
from production_os.sqlite_backend import SQLiteBackend, SQLiteJobQueue
from production_os.workflow_engine import WorkflowEngine


def service(tmp_path):
    backend = SQLiteBackend(tmp_path / "cooperative.sqlite")
    return ManagedProjectService(
        WorkflowEngine(backend, SQLiteJobQueue(backend))
    )


def _planner_config(managed, *, goal, instruction=None, budget=1000):
    tasks = managed._cooperative_workflow_specs(
        project_id="project-1234",
        repository="o/a",
        final_goal=goal,
        instruction=instruction or goal,
        generation=1,
        kind="initial",
        token_budget=budget,
        agent_preference="auto",
    )
    assert [task.task_id for task in tasks] == ["planner"]
    return tasks[0]


def test_cooperative_workflow_starts_with_bounded_adaptive_planner(tmp_path):
    managed = service(tmp_path)
    planner = _planner_config(
        managed,
        goal="Implement repository automation safely",
    )

    config = planner.payload["dynamic_agent_planner"]
    fallback = config["fallback_plan"]

    assert planner.dependencies == ()
    assert planner.payload["cooperative_stage"] == "planner"
    assert config["max_agents"] == 6
    assert config["integration_task_id"] == "integration"
    assert [row["task_id"] for row in fallback["tasks"]] == [
        "code",
        "tests",
    ]
    assert sum(row["token_budget"] for row in fallback["tasks"]) == (
        config["available_token_budget"]
    )
    assert config["post_integration_tasks"][-1]["task_id"] == "review"
    assert planner.payload["handoff"]["tool_contracts"]["dynamic_agent_plan"][
        "schema"
    ] == "production-os/dynamic-agent-plan/v1"


def test_cooperative_browser_goal_puts_browser_validation_after_review(tmp_path):
    managed = service(tmp_path)
    planner = _planner_config(
        managed,
        goal="Improve the dashboard UI and verify it in the browser",
        instruction="Improve the dashboard UI",
    )

    continuation = planner.payload["dynamic_agent_planner"][
        "post_integration_tasks"
    ]
    assert [row["task_id"] for row in continuation] == [
        "validation",
        "review",
        "ui-validation",
    ]
    browser = continuation[-1]
    assert browser["required_capabilities"] == ["browser-ui-validation"]
    assert browser["tool_contracts"]["browser_validation"]["runtime"] == (
        "python-playwright-chromium"
    )


def test_native_mobile_goal_puts_emulator_validation_after_review(tmp_path):
    managed = service(tmp_path)
    for goal in (
        "Improve the Android UI",
        "Polish the Flutter UI",
        "Fix the mobile UI layout",
    ):
        planner = _planner_config(managed, goal=goal)
        continuation = planner.payload["dynamic_agent_planner"][
            "post_integration_tasks"
        ]
        assert [row["task_id"] for row in continuation] == [
            "validation",
            "review",
            "mobile-ui-validation",
        ]
        mobile = continuation[-1]
        assert mobile["required_capabilities"] == [
            "mobile-ui-validation"
        ]
        assert mobile["tool_contracts"]["mobile_validation"]["runtime"] == (
            "android-adb-emulator"
        )


def test_create_cooperative_project_queues_only_planner_initially(tmp_path):
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
    assert [task["task_id"] for task in workflow["tasks"]] == ["planner"]
    assert workflow["tasks"][0]["status"] == "queued"


def test_planner_fallback_expands_code_tests_and_delivery_chain(tmp_path):
    managed = service(tmp_path)
    project = managed.create(
        repository="o/a",
        final_goal="Implement a tested backend change",
        token_budget=1000,
        cooperative=True,
        requested_by="operator:test",
    )
    workflow_id = project["current_workflow_id"]

    expanded = managed.workflows.record_result(
        workflow_id,
        "planner",
        succeeded=True,
        result={"summary":"no structured plan returned"},
    )
    by_id = {task["task_id"]:task for task in expanded["tasks"]}

    assert {
        "planner",
        "planner.agent.code",
        "planner.agent.tests",
        "integration",
        "validation",
        "review",
    } == set(by_id)
    assert by_id["planner.agent.code"]["status"] == "queued"
    assert by_id["planner.agent.tests"]["status"] == "queued"
    assert by_id["integration"]["dependencies"] == [
        "planner.agent.code",
        "planner.agent.tests",
    ]
    assert by_id["validation"]["dependencies"] == ["integration"]
    assert by_id["review"]["dependencies"] == ["validation"]


def test_cooperative_outcome_uses_deepest_stage_and_aggregates_delivery_evidence():
    workflow = {
        "status":"succeeded",
        "updated_at":"2026-09-27T09:00:00+00:00",
        "artifacts":[],
        "tasks":[
            {
                "task_id":"planner.agent.code",
                "title":"Implement",
                "dependencies":["planner"],
                "updated_at":"2026-09-27T08:00:00+00:00",
                "result":{
                    "summary":"implemented feature",
                    "commit_shas":["a"*40],
                    "changed_files":["src/app.py"],
                    "pull_request":{"number":12,"state":"open"},
                },
            },
            {
                "task_id":"integration",
                "title":"Integrate",
                "dependencies":["planner.agent.code","planner.agent.tests"],
                "updated_at":"2026-09-27T08:10:00+00:00",
                "result":{
                    "summary":"integrated",
                    "commit_shas":["b"*40],
                    "changed_files":["src/app.py","tests/test_app.py"],
                    "ci":{
                        "provider":"github-actions",
                        "status":"passed",
                        "workflow":"CI",
                    },
                },
            },
            {
                "task_id":"validation",
                "title":"Validate",
                "dependencies":["integration"],
                "updated_at":"2026-09-27T08:15:00+00:00",
                "result":{
                    "summary":"tests passed",
                    "validation":{"status":"passed","tests":["unit"]},
                },
            },
            {
                "task_id":"review",
                "title":"Review",
                "dependencies":["validation"],
                "updated_at":"2026-09-27T08:20:00+00:00",
                "result":{
                    "summary":"review passed",
                    "validation":{"status":"passed","tests":["review"]},
                    "changed_files":["src/app.py","tests/test_app.py"],
                },
            },
        ],
    }

    outcome = _outcome_from_workflow(workflow)

    assert outcome["summary"] == "review passed"
    assert outcome["validation_status"] == "passed"
    assert outcome["validation_tests"] == ["review"]
    assert outcome["commit_shas"] == ["a"*40, "b"*40]
    assert outcome["changed_file_count"] == 2
    assert outcome["pull_request"] == {"number":12, "state":"open"}
    assert outcome["ci"]["workflow"] == "CI"


def test_cooperative_workflow_rejects_budget_smaller_than_stage_count(tmp_path):
    managed = service(tmp_path)
    with pytest.raises(
        ValueError,
        match="cooperative token_budget must cover every stage",
    ):
        managed._cooperative_workflow_specs(
            project_id="project-1234",
            repository="o/a",
            final_goal="Improve the dashboard UI in a browser",
            instruction="Improve the dashboard UI",
            generation=1,
            kind="initial",
            token_budget=3,
            agent_preference="auto",
        )


def test_retest_preserves_cooperative_dynamic_planner_mode(tmp_path):
    managed = service(tmp_path)
    project = managed.create(
        repository="o/a",
        final_goal="Implement a tested backend change",
        token_budget=1000,
        cooperative=True,
        requested_by="operator:test",
    )
    workflow_id = project["current_workflow_id"]

    managed.workflows.record_result(
        workflow_id,
        "planner",
        succeeded=True,
        result={"summary":"use fallback"},
    )
    for task_id, summary in (
        ("planner.agent.code", "implemented code"),
        ("planner.agent.tests", "implemented tests"),
        ("integration", "integrated"),
        ("validation", "validated"),
        ("review", "reviewed"),
    ):
        managed.workflows.record_result(
            workflow_id,
            task_id,
            succeeded=True,
            result={"summary":summary},
        )

    completed = managed.get(project["project_id"])
    assert completed["status"] == "REVIEW_REQUIRED"
    follow_up = managed.request_verification(
        project["project_id"],
        requested_by="operator:test",
    )

    assert follow_up["generation"] == 2
    assert follow_up["status"] == "ACTIVE"
    assert follow_up["current_workflow"]["metadata"]["cooperative"] is True
    assert [task["task_id"] for task in follow_up["current_workflow"]["tasks"]] == [
        "planner"
    ]
