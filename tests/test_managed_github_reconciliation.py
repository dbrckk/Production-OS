from unittest.mock import patch

from production_os.github_work_state import GitHubWorkState
from production_os.sqlite_backend import SQLiteBackend, SQLiteJobQueue
from production_os.workflow_engine import WorkflowEngine
from production_os.managed_projects import (
    ACTIVE,
    NEEDS_ATTENTION,
    REVIEW_REQUIRED,
    ManagedProjectService,
)


class FakeWorkflows:
    backend = object()


class FakeGitHub:
    def __init__(self, merge=None, error=None):
        self.merge = (
            {"merged":True, "sha":"b"*40, "message":"merged"}
            if merge is None
            else merge
        )
        self.error = error
        self.calls = []

    def merge_pull_request(
        self,
        repository,
        pr_number,
        *,
        head_sha,
        method,
        commit_title,
    ):
        self.calls.append({
            "repository":repository,
            "pr_number":pr_number,
            "head_sha":head_sha,
            "method":method,
            "commit_title":commit_title,
        })
        if self.error is not None:
            raise self.error
        return dict(self.merge)


def state(**overrides):
    values = {
        "repository":"o/a",
        "issue_number":None,
        "pr_number":12,
        "issue_state":None,
        "pr_state":"open",
        "merged":False,
        "draft":False,
        "review_state":"approved",
        "ci_state":"passed",
        "status_state":"passed",
        "ready_for_promotion":True,
        "promotion_blockers":(),
        "required_checks_missing":(),
        "sensitive_files":(),
        "change_categories":(),
        "human_review_required":False,
        "head_sha":"a"*40,
        "base_sha":"c"*40,
        "validation_sha":"a"*40,
    }
    values.update(overrides)
    return GitHubWorkState(**values)



def _complete_parallel_cooperative_workflow(
    service,
    workflow_id,
    *,
    review_result,
):
    service.workflows.record_result(
        workflow_id,
        "implementation-code",
        succeeded=True,
        result={
            "summary":"implemented",
            "commit_shas":["a"*40],
        },
    )
    service.workflows.record_result(
        workflow_id,
        "implementation-tests",
        succeeded=True,
        result={
            "summary":"tests implemented",
            "commit_shas":["b"*40],
        },
    )
    service.workflows.record_result(
        workflow_id,
        "integration",
        succeeded=True,
        result={
            "summary":"integrated",
            "commit_shas":["c"*40],
        },
    )
    service.workflows.record_result(
        workflow_id,
        "validation",
        succeeded=True,
        result={
            "summary":"validated",
            "validation":{"status":"passed","tests":["unit"]},
        },
    )
    service.workflows.record_result(
        workflow_id,
        "review",
        succeeded=True,
        result=review_result,
    )


def workflow_with_pr():
    return {
        "status":"succeeded",
        "updated_at":"2026-09-27T09:00:00+00:00",
        "artifacts":[],
        "tasks":[{
            "task_id":"review",
            "title":"Review",
            "dependencies":[],
            "result":{
                "summary":"review complete",
                "pull_request":{"number":12,"state":"open"},
            },
        }],
    }


def test_green_pull_request_is_sha_pinned_merged_then_waits_for_post_merge_ci():
    github = FakeGitHub()
    service = ManagedProjectService(
        FakeWorkflows(),
        github_client_factory=lambda: github,
    )
    with patch(
        "production_os.managed_projects.fetch_github_work_state",
        return_value=state(),
    ):
        resolution = service._github_resolution_for_succeeded_workflow(
            "o/a",
            workflow_with_pr(),
        )

    assert resolution["target"] == ACTIVE
    assert resolution["decision"] == "merged-awaiting-validation"
    assert resolution["merge"] == {
        "merged":True,
        "sha":"b"*40,
        "receipt":False,
    }
    assert github.calls == [{
        "repository":"o/a",
        "pr_number":12,
        "head_sha":"a"*40,
        "method":"squash",
        "commit_title":"Production-OS: managed project PR #12",
    }]


def test_pending_pull_request_keeps_project_active():
    service = ManagedProjectService(
        FakeWorkflows(),
        github_client_factory=lambda: object(),
    )
    pending = state(
        ci_state="running",
        ready_for_promotion=False,
        promotion_blockers=("actions-not-passed",),
    )
    with patch(
        "production_os.managed_projects.fetch_github_work_state",
        return_value=pending,
    ):
        target = service._github_target_for_succeeded_workflow(
            "o/a",
            workflow_with_pr(),
        )

    assert target == ACTIVE


def test_failed_pull_request_moves_project_to_needs_attention():
    service = ManagedProjectService(
        FakeWorkflows(),
        github_client_factory=lambda: object(),
    )
    failed = state(
        ci_state="failed",
        ready_for_promotion=False,
        promotion_blockers=("actions-not-passed",),
    )
    with patch(
        "production_os.managed_projects.fetch_github_work_state",
        return_value=failed,
    ):
        target = service._github_target_for_succeeded_workflow(
            "o/a",
            workflow_with_pr(),
        )

    assert target == NEEDS_ATTENTION


def test_sensitive_green_pull_request_requires_review():
    github = FakeGitHub()
    service = ManagedProjectService(
        FakeWorkflows(),
        github_client_factory=lambda: github,
    )
    sensitive = state(
        ready_for_promotion=False,
        human_review_required=True,
        promotion_blockers=("human-review-required",),
    )
    with patch(
        "production_os.managed_projects.fetch_github_work_state",
        return_value=sensitive,
    ):
        target = service._github_target_for_succeeded_workflow(
            "o/a",
            workflow_with_pr(),
        )

    assert target == REVIEW_REQUIRED
    assert github.calls == []


def test_automerge_receipt_prevents_duplicate_merge_during_github_staleness(tmp_path):
    backend = SQLiteBackend(tmp_path / "automerge-idempotent.sqlite")
    github = FakeGitHub()
    service = ManagedProjectService(
        WorkflowEngine(backend, SQLiteJobQueue(backend)),
        github_client_factory=lambda: github,
    )
    workflow = workflow_with_pr()
    workflow["id"] = "workflow-1234"
    workflow["metadata"] = {
        "managed_project_id":"project-1234",
    }

    with patch(
        "production_os.managed_projects.fetch_github_work_state",
        return_value=state(),
    ):
        first = service._github_resolution_for_succeeded_workflow(
            "o/a",
            workflow,
        )
        second = service._github_resolution_for_succeeded_workflow(
            "o/a",
            workflow,
        )

    assert first["target"] == ACTIVE
    assert first["decision"] == "merged-awaiting-validation"
    assert first["merge"]["receipt"] is True
    assert second["target"] == ACTIVE
    assert second["decision"] == "merged-awaiting-validation"
    assert second["merge"]["receipt"] is True
    assert second["merge"]["sha"] == "b"*40
    assert len(github.calls) == 1


def test_automerge_aborts_when_base_sha_changes_during_final_recheck():
    github = FakeGitHub()
    service = ManagedProjectService(
        FakeWorkflows(),
        github_client_factory=lambda: github,
    )
    initial = state()
    changed = state(
        base_sha="d"*40,
    )
    with patch(
        "production_os.managed_projects.fetch_github_work_state",
        side_effect=[initial, changed],
    ):
        resolution = service._github_resolution_for_succeeded_workflow(
            "o/a",
            workflow_with_pr(),
        )

    assert resolution["target"] == ACTIVE
    assert resolution["decision"] == "promotion-state-changed"
    assert resolution["state"].base_sha == "d"*40
    assert github.calls == []


def test_green_pull_request_merge_declined_requires_review():
    github = FakeGitHub(
        merge={
            "merged":False,
            "sha":None,
            "message":"Required approving review missing",
        },
    )
    service = ManagedProjectService(
        FakeWorkflows(),
        github_client_factory=lambda: github,
    )
    with patch(
        "production_os.managed_projects.fetch_github_work_state",
        return_value=state(),
    ):
        resolution = service._github_resolution_for_succeeded_workflow(
            "o/a",
            workflow_with_pr(),
        )

    assert resolution["target"] == REVIEW_REQUIRED
    assert resolution["decision"] == "merge-blocked"
    assert resolution["merge"]["merged"] is False
    assert "Required approving review" in resolution["merge"]["reason"]


def test_post_merge_green_resolution_completes_managed_project():
    service = ManagedProjectService(
        FakeWorkflows(),
        github_client_factory=lambda: FakeGitHub(),
    )
    merged_green = state(
        pr_state="closed",
        merged=True,
        ci_state="passed",
        status_state="passed",
        ready_for_promotion=False,
        validation_sha="b"*40,
        promotion_blockers=("already-merged","pr-not-open"),
    )
    with patch(
        "production_os.managed_projects.fetch_github_work_state",
        return_value=merged_green,
    ):
        resolution = service._github_resolution_for_succeeded_workflow(
            "o/a",
            workflow_with_pr(),
        )

    assert resolution["target"] == "DONE"
    assert resolution["decision"] == "promote"


def test_succeeded_workflow_without_pull_request_keeps_legacy_path():
    service = ManagedProjectService(
        FakeWorkflows(),
        github_client_factory=lambda: object(),
    )
    workflow = {
        "status":"succeeded",
        "updated_at":"2026-09-27T09:00:00+00:00",
        "artifacts":[],
        "tasks":[{
            "task_id":"implementation",
            "title":"Implement",
            "dependencies":[],
            "result":{"summary":"done"},
        }],
    }

    assert service._github_target_for_succeeded_workflow(
        "o/a",
        workflow,
    ) is None



def test_succeeded_pull_request_without_ci_moves_to_review_instead_of_stalling():
    service = ManagedProjectService(
        FakeWorkflows(),
        github_client_factory=lambda: object(),
    )
    no_ci = state(
        ci_state=None,
        status_state=None,
        ready_for_promotion=False,
        promotion_blockers=("actions-not-passed",),
    )
    with patch(
        "production_os.managed_projects.fetch_github_work_state",
        return_value=no_ci,
    ):
        target = service._github_target_for_succeeded_workflow(
            "o/a",
            workflow_with_pr(),
        )

    assert target == REVIEW_REQUIRED



def test_post_merge_failure_resolution_builds_compensating_rollback_plan():
    service = ManagedProjectService(
        FakeWorkflows(),
        github_client_factory=lambda: object(),
    )
    merged_failed = state(
        pr_state="closed",
        merged=True,
        ci_state="failed",
        status_state="passed",
        ready_for_promotion=False,
        validation_sha="b"*40,
        promotion_blockers=("actions-not-passed",),
    )
    with patch(
        "production_os.managed_projects.fetch_github_work_state",
        return_value=merged_failed,
    ):
        resolution = service._github_resolution_for_succeeded_workflow(
            "o/a",
            workflow_with_pr(),
        )

    assert resolution["target"] == NEEDS_ATTENTION
    assert resolution["decision"] == "rollback"
    plan = resolution["rollback_plan"]
    assert plan["strategy"] == "compensating-pr"
    assert plan["merge_sha"] == "b"*40
    assert plan["history_rewrite_allowed"] is False
    assert plan["force_push_allowed"] is False
    assert "Do not reset" in plan["instruction"]
    assert "open a pull request" in plan["instruction"]


def test_reconcile_marks_project_done_after_post_merge_green_ci(tmp_path):
    backend = SQLiteBackend(tmp_path / "automerge-complete.sqlite")
    service = ManagedProjectService(
        WorkflowEngine(backend, SQLiteJobQueue(backend)),
        github_client_factory=lambda: FakeGitHub(),
    )
    project = service.create(
        repository="o/a",
        final_goal="Ship a verified backend change",
        token_budget=1000,
        cooperative=True,
        requested_by="operator:test",
    )
    workflow_id = project["current_workflow_id"]
    _complete_parallel_cooperative_workflow(
        service,
        workflow_id,
        review_result={
            "summary":"reviewed",
            "pull_request":{"number":12,"state":"merged"},
        },
    )

    merged_green = state(
        pr_state="closed",
        merged=True,
        ci_state="passed",
        status_state="passed",
        ready_for_promotion=False,
        validation_sha="b"*40,
        promotion_blockers=("already-merged","pr-not-open"),
    )
    with patch(
        "production_os.managed_projects.fetch_github_work_state",
        return_value=merged_green,
    ):
        completed = service.get(project["project_id"])

    assert completed["status"] == "DONE"
    assert completed["approved_by"] == "system:github-promotion"
    assert completed["completed_at"]


def test_reconcile_launches_exactly_one_automatic_rollback_generation(tmp_path):
    backend = SQLiteBackend(tmp_path / "rollback.sqlite")
    service = ManagedProjectService(
        WorkflowEngine(backend, SQLiteJobQueue(backend)),
        github_client_factory=lambda: object(),
    )
    project = service.create(
        repository="o/a",
        final_goal="Ship a verified backend change",
        token_budget=1000,
        cooperative=True,
        requested_by="operator:test",
    )
    workflow_id = project["current_workflow_id"]
    _complete_parallel_cooperative_workflow(
        service,
        workflow_id,
        review_result={
            "summary":"reviewed",
            "pull_request":{"number":12,"state":"open"},
        },
    )

    merged_failed = state(
        pr_state="closed",
        merged=True,
        ci_state="failed",
        status_state="passed",
        ready_for_promotion=False,
        validation_sha="b"*40,
        promotion_blockers=("actions-not-passed",),
    )
    with patch(
        "production_os.managed_projects.fetch_github_work_state",
        return_value=merged_failed,
    ):
        recovered = service.get(project["project_id"])
        polled_again = service.get(project["project_id"])

    assert recovered["status"] == ACTIVE
    assert recovered["generation"] == 2
    assert recovered["current_workflow"]["metadata"]["cooperative"] is True
    assert recovered["runs"][-1]["kind"] == "rollback"
    assert recovered["runs"][-1]["requested_by"] == "system:github-rollback"
    assert "Do not reset" in recovered["runs"][-1]["instruction"]
    assert "open a pull request" in recovered["runs"][-1]["instruction"]
    assert polled_again["generation"] == 2
    assert len([
        run for run in polled_again["runs"]
        if run["kind"] == "rollback"
    ]) == 1
