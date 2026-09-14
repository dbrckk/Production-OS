from production_os.execution_feedback import decide_execution_outcome
from production_os.trends import build_trends


def test_blocked_validation_rolls_back():
    decision = decide_execution_outcome(70, 75, {"status":"blocked"})
    assert decision.decision == "rollback"


def test_validated_improvement_promotes():
    decision = decide_execution_outcome(70, 80, {"status":"passed"})
    assert decision.decision == "promote"
    assert decision.score_delta == 10


def test_trend_detects_regression():
    snapshots = [
        {"repositories":{"o/a":{"score":80}}},
        {"repositories":{"o/a":{"score":70}}},
    ]
    trends = build_trends(snapshots)
    assert trends[0].direction == "regressing"
    assert trends[0].delta == -10
