from production_os.github_work_state import GitHubWorkState, runtime_decision_from_github


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
