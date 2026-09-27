from production_os.github_work_state import (
    GitHubWorkState,
    _ci_state,
    _status_state,
    runtime_decision_from_github,
)


def state(**kwargs):
    base = dict(
        repository="o/a",
        issue_number=None,
        pr_number=1,
        issue_state=None,
        pr_state="open",
        merged=False,
        draft=False,
        review_state=None,
        ci_state="running",
        status_state=None,
        ready_for_promotion=False,
        promotion_blockers=(),
        head_sha="abc",
    )
    base.update(kwargs)
    return GitHubWorkState(**base)


def test_merged_pr_promotes():
    assert runtime_decision_from_github(state(merged=True, pr_state="closed")) == "promote"


def test_failed_ci_retries():
    assert runtime_decision_from_github(state(ci_state="failed")) == "retry"


def test_closed_unmerged_pr_replans():
    assert runtime_decision_from_github(state(pr_state="closed", merged=False, ci_state="passed")) == "replan"


def test_ci_state_does_not_pass_while_any_workflow_is_running():
    runs = [
        {"status":"completed","conclusion":"success"},
        {"status":"in_progress","conclusion":None},
    ]
    assert _ci_state(runs) == "running"


def test_ci_state_passes_only_when_all_workflows_complete_successfully():
    assert _ci_state([
        {"status":"completed","conclusion":"success"},
        {"status":"completed","conclusion":"success"},
    ]) == "passed"
    assert _ci_state([
        {"status":"completed","conclusion":"success"},
        {"status":"completed","conclusion":"failure"},
    ]) == "failed"


def test_external_commit_statuses_fail_closed():
    assert _status_state([
        {"context":"circleci/validate","state":"success"},
        {"context":"circleci/smoke","state":"pending"},
    ]) == "running"
    assert _status_state([
        {"context":"circleci/validate","state":"success"},
        {"context":"circleci/smoke","state":"failure"},
    ]) == "failed"
    assert _status_state([
        {"context":"circleci/validate","state":"success"},
        {"context":"circleci/smoke","state":"success"},
    ]) == "passed"


def test_external_failed_status_retries():
    assert runtime_decision_from_github(
        state(ci_state="passed", status_state="failed")
    ) == "retry"


def test_pending_external_status_remains_running():
    assert runtime_decision_from_github(
        state(ci_state="passed", status_state="running")
    ) == "running"


def test_promotion_readiness_requires_open_non_draft_green_pr():
    from production_os.github_work_state import _promotion_readiness

    ready, blockers = _promotion_readiness(
        pr_state="open",
        merged=False,
        draft=False,
        review_state="approved",
        ci_state="passed",
        status_state="passed",
    )
    assert ready is True
    assert blockers == ()

    ready, blockers = _promotion_readiness(
        pr_state="open",
        merged=False,
        draft=False,
        review_state=None,
        ci_state="running",
        status_state="passed",
    )
    assert ready is False
    assert "actions-not-passed" in blockers

    ready, blockers = _promotion_readiness(
        pr_state="open",
        merged=False,
        draft=True,
        review_state=None,
        ci_state="passed",
        status_state="passed",
    )
    assert ready is False
    assert "draft" in blockers
