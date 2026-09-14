from production_os.models import RepoEvidence
from production_os.scoring import assess_repository, score_repository


def evidence(**overrides):
    data = dict(
        name="demo",
        full_name="owner/demo",
        html_url="https://github.com/owner/demo",
        pushed_at="2099-01-01T00:00:00Z",
    )
    data.update(overrides)
    return RepoEvidence(**data)


def test_empty_repository_generates_foundational_actions():
    assessment = assess_repository(evidence())
    tasks = {action.task for action in assessment.actions}

    assert assessment.score.total == 10  # future timestamp counts as recent activity
    assert "Add an executable automated test baseline" in tasks
    assert "Add continuous integration for every change" in tasks
    assert "Add a reproducible project/build manifest" in tasks


def test_mature_repository_scores_full_points():
    repo = evidence(
        has_readme=True,
        has_tests=True,
        has_ci=True,
        has_release_workflow=True,
        has_manifest=True,
        has_license=True,
        has_security_policy=True,
        has_dependency_automation=True,
    )

    score = score_repository(repo)

    assert score.total == 90
    assert score.tests == 15
    assert score.ci == 15
    assert score.release == 15


def test_priority_is_effort_adjusted():
    assessment = assess_repository(evidence(has_readme=True, has_manifest=True))
    assert assessment.actions == sorted(
        assessment.actions,
        key=lambda action: action.priority,
        reverse=True,
    )
    assert all(action.priority > 0 for action in assessment.actions)
