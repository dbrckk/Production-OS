from production_os.models import ActionCandidate, RepoAssessment, RepoEvidence, ScoreBreakdown
from production_os.resources import allocate_resources
from production_os.scheduler import build_schedule


def action(repo, task, priority, effort=1, release=5):
    return ActionCandidate(
        repository=repo,
        task=task,
        rationale="test",
        acceptance_criteria=[],
        evidence=[],
        impact=5,
        urgency=5,
        risk_reduction=5,
        release_proximity=release,
        effort=effort,
        priority=priority,
    )


def assessment(repo, score=50):
    return RepoAssessment(
        evidence=RepoEvidence(name=repo.split("/")[-1], full_name=repo, html_url="x", has_tests=True),
        score=ScoreBreakdown(score,0,0,0,0,0,0,0,0),
        actions=[],
    )


def test_schedule_respects_capacity_and_repo_focus():
    assessments = [assessment("o/a"), assessment("o/b"), assessment("o/c")]
    actions = [action("o/a","A",60), action("o/b","B",50), action("o/c","C",40)]
    schedule = build_schedule(assessments, actions, capacity=2)
    active = [x for x in schedule["work"] if x["lane"] in {"NOW","PARALLEL"}]
    assert len(active) == 2
    assert schedule["work"][0]["lane"] == "NOW"


def test_resource_allocation_never_exceeds_slots():
    schedule = {"work": [
        {"repository":"o/a","task":"A","lane":"NOW","score":80,"effort":1},
        {"repository":"o/b","task":"B","lane":"PARALLEL","score":60,"effort":2},
    ]}
    allocation = allocate_resources(schedule, total_slots=3)
    assert allocation["allocated_slots"] == 3
    assert sum(x["slots"] for x in allocation["allocations"]) == 3
