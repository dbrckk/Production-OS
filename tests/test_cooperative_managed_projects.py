import pytest

from production_os.managed_projects import ManagedProjectService, _outcome_from_workflow
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
    assert tasks[0].dependencies == ()
    assert tasks[1].dependencies == ()
    assert tasks[2].dependencies == ("implementation-code", "implementation-tests")
    assert tasks[3].dependencies == ("integration",)
    assert tasks[4].dependencies == ("validation",)
    assert tasks[0].payload["handoff"]["preferred_capabilities"] == [
        "code-implementation"
    ]
    assert tasks[1].payload["handoff"]["preferred_capabilities"] == [
        "test-debug"
    ]
    assert tasks[2].payload["handoff"]["preferred_capabilities"] == [
        "code-implementation"
    ]
    assert tasks[4].payload["handoff"]["preferred_capabilities"] == [
        "code-review"
    ]
    assert all(task.priority == 100 for task in tasks)
    assert tasks[0].payload["isolation"]["mode"] == "git-worktree"
    assert tasks[1].payload["isolation"]["mode"] == "git-worktree"
    assert tasks[2].payload["isolation"]["integration_target"] is True
    budgets = [
        task.payload["handoff"]["token_budget"]
        for task in tasks
    ]
    assert sum(budgets) == 1000
    assert len(budgets) == 5
    assert all(value > 0 for value in budgets)


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
    assert [task.priority for task in tasks] == [100, 100, 100, 100]
    assert tasks[-1].payload["handoff"]["preferred_capabilities"] == [
        "browser-ui-validation"
    ]
    assert tasks[-1].payload["handoff"]["required_capabilities"] == [
        "browser-ui-validation"
    ]
    assert tasks[-1].payload["handoff"]["tool_contracts"]["browser_validation"] == {
        "schema":"production-os/browser-validation/v1",
        "report_schema":"production-os/browser-validation-report/v1",
        "script":".production-os/browser_validate.py",
        "artifacts_dir":".production-os/browser-artifacts",
        "runtime":"python-playwright-chromium",
    }
    assert sum(
        task.payload["handoff"]["token_budget"]
        for task in tasks
    ) == 1000
    assert tasks[-1].payload["handoff"]["token_budget"] > 0


def test_native_mobile_ui_uses_dedicated_emulator_stage(tmp_path):
    managed = service(tmp_path)

    for final_goal in (
        "Improve the Android UI",
        "Polish the Flutter UI",
        "Fix the mobile UI layout",
    ):
        tasks = managed._cooperative_workflow_specs(
            project_id="project-1234",
            repository="o/a",
            final_goal=final_goal,
            instruction=final_goal,
            generation=1,
            kind="initial",
            token_budget=1000,
            agent_preference="auto",
        )
        assert [task.task_id for task in tasks] == [
            "implementation",
            "validation",
            "review",
            "mobile-ui-validation",
        ]
        mobile = tasks[-1]
        assert mobile.dependencies == ("review",)
        assert mobile.payload["handoff"]["required_capabilities"] == [
            "mobile-ui-validation"
        ]
        assert (
            mobile.payload["handoff"]["required_capabilities_authoritative"]
            is True
        )
        assert mobile.payload["handoff"]["tool_contracts"]["mobile_validation"] == {
            "schema":"production-os/mobile-validation/v1",
            "report_schema":"production-os/mobile-validation-report/v1",
            "script":".production-os/mobile_validate.py",
            "artifacts_dir":".production-os/mobile-artifacts",
            "runtime":"android-adb-emulator",
        }
        assert "browser_validation" not in mobile.payload["handoff"]["tool_contracts"]
        assert sum(
            task.payload["handoff"]["token_budget"]
            for task in tasks
        ) == 1000


def test_web_ui_still_uses_playwright_browser_stage(tmp_path):
    managed = service(tmp_path)
    tasks = managed._cooperative_workflow_specs(
        project_id="project-1234",
        repository="o/a",
        final_goal="Improve the website frontend",
        instruction="Improve the website frontend",
        generation=1,
        kind="initial",
        token_budget=1000,
        agent_preference="auto",
    )

    assert tasks[-1].task_id == "ui-validation"


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
    by_id = {
        task["task_id"]:task
        for task in workflow["tasks"]
    }
    assert set(by_id) == {
        "implementation-code",
        "implementation-tests",
        "integration",
        "validation",
        "review",
    }
    assert by_id["implementation-code"]["dependencies"] == []
    assert by_id["implementation-tests"]["dependencies"] == []
    assert by_id["integration"]["dependencies"] == [
        "implementation-code",
        "implementation-tests",
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
                "task_id":"implementation",
                "title":"Implement",
                "dependencies":[],
                "updated_at":"2026-09-27T08:00:00+00:00",
                "result":{
                    "summary":"implemented feature",
                    "commit_shas":["a"*40],
                    "changed_files":["src/app.py"],
                    "pull_request":{"number":12,"state":"open"},
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
            {
                "task_id":"validation",
                "title":"Validate",
                "dependencies":["implementation"],
                "updated_at":"2026-09-27T08:10:00+00:00",
                "result":{
                    "summary":"tests passed",
                    "validation":{"status":"passed","tests":["unit"]},
                    "commit_shas":["b"*40],
                    "ci":{
                        "provider":"github-actions",
                        "status":"passed",
                        "workflow":"CI",
                    },
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



def test_retest_preserves_cooperative_mode_across_generations(tmp_path):
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
        "implementation-code",
        succeeded=True,
        result={"summary":"implemented code"},
    )
    managed.workflows.record_result(
        workflow_id,
        "implementation-tests",
        succeeded=True,
        result={"summary":"implemented tests"},
    )
    managed.workflows.record_result(
        workflow_id,
        "integration",
        succeeded=True,
        result={"summary":"integrated"},
    )
    managed.workflows.record_result(
        workflow_id,
        "validation",
        succeeded=True,
        result={"summary":"validated"},
    )
    managed.workflows.record_result(
        workflow_id,
        "review",
        succeeded=True,
        result={"summary":"reviewed"},
    )

    completed = managed.get(project["project_id"])
    assert completed["status"] == "REVIEW_REQUIRED"
    assert completed["current_workflow"]["metadata"]["cooperative"] is True

    follow_up = managed.request_verification(
        project["project_id"],
        requested_by="operator:test",
    )

    assert follow_up["generation"] == 2
    assert follow_up["status"] == "ACTIVE"
    assert follow_up["current_workflow"]["metadata"]["cooperative"] is True
    assert {
        task["task_id"]
        for task in follow_up["current_workflow"]["tasks"]
    } == {"implementation-code", "implementation-tests", "integration", "validation", "review"}
