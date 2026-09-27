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



class FakeMergeClient:
    def __init__(self, pr):
        self.pr = pr
        self.merge_calls = []

    def get_pull_request(self, repository, pr_number):
        return self.pr

    def merge_pull_request(
        self,
        repository,
        pr_number,
        *,
        expected_head_sha,
        merge_method,
    ):
        self.merge_calls.append({
            "repository":repository,
            "pr_number":pr_number,
            "expected_head_sha":expected_head_sha,
            "merge_method":merge_method,
        })
        return {"merged":True, "sha":"c"*40}


def managed_pr(*, head_ref="studio/mp-abc", head_sha="a"*40, draft=False):
    return {
        "number":12,
        "state":"open",
        "draft":draft,
        "head":{"ref":head_ref, "sha":head_sha},
        "base":{"ref":"main"},
    }


def test_green_exact_managed_pr_is_auto_merged_and_stays_active_for_post_merge_ci():
    client = FakeMergeClient(managed_pr())
    service = ManagedProjectService(
        FakeWorkflows(),
        github_client_factory=lambda: client,
    )
    with patch(
        "production_os.managed_projects.fetch_github_work_state",
        return_value=state(),
    ):
        target = service._github_target_for_succeeded_workflow(
            "o/a",
            workflow_with_pr(),
        )

    assert target == ACTIVE
    assert client.merge_calls == [{
        "repository":"o/a",
        "pr_number":12,
        "expected_head_sha":"a"*40,
        "merge_method":"squash",
    }]


def test_foreign_branch_is_never_auto_merged():
    client = FakeMergeClient(
        managed_pr(head_ref="feature/user-branch")
    )
    service = ManagedProjectService(
        FakeWorkflows(),
        github_client_factory=lambda: client,
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
    assert client.merge_calls == []


def test_managed_branch_head_sha_mismatch_blocks_auto_merge():
    client = FakeMergeClient(
        managed_pr(head_sha="b"*40)
    )
    service = ManagedProjectService(
        FakeWorkflows(),
        github_client_factory=lambda: client,
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
    assert client.merge_calls == []


def test_managed_draft_pr_is_never_auto_merged():
    client = FakeMergeClient(
        managed_pr(draft=True)
    )
    service = ManagedProjectService(
        FakeWorkflows(),
        github_client_factory=lambda: client,
    )
    with patch(
        "production_os.managed_projects.fetch_github_work_state",
        return_value=state(draft=True),
    ):
        target = service._github_target_for_succeeded_workflow(
            "o/a",
            workflow_with_pr(),
        )

    assert target == ACTIVE
    assert client.merge_calls == []
