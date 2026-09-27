from unittest.mock import patch

from production_os.github_work_state import GitHubWorkState
from production_os.managed_projects import (
    ACTIVE,
    NEEDS_ATTENTION,
    REVIEW_REQUIRED,
    ManagedProjectService,
)


class FakeWorkflows:
    backend = object()


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
        "validation_sha":"a"*40,
    }
    values.update(overrides)
    return GitHubWorkState(**values)


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


def test_green_pull_request_moves_succeeded_workflow_to_review_required():
    service = ManagedProjectService(
        FakeWorkflows(),
        github_client_factory=lambda: object(),
    )
    with patch(
        "production_os.managed_projects.fetch_github_work_state",
        return_value=state(),
    ):
        target = service._github_target_for_succeeded_workflow(
            "o/a",
            workflow_with_pr(),
        )

    assert target == REVIEW_REQUIRED


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
    service = ManagedProjectService(
        FakeWorkflows(),
        github_client_factory=lambda: object(),
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
