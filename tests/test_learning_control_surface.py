from production_os.control_surface import render_control_surface
from production_os.learning import build_learning_signals, learning_weight


def test_learning_rewards_successful_history():
    events = [
        {"repository":"o/a","task":"A","decision":"promote","score_delta":10},
        {"repository":"o/a","task":"A","decision":"promote","score_delta":5},
        {"repository":"o/b","task":"B","decision":"rollback","score_delta":-10},
    ]
    signals = build_learning_signals(events)
    assert learning_weight(signals, "o/a", "A") > 0
    assert learning_weight(signals, "o/b", "B") < 0


def test_control_surface_contains_schedule():
    html = render_control_surface({
        "schedule":{"work":[{"lane":"NOW","repository":"o/a","task":"A","score":50,"blockers":[]}]},
        "resource_allocation":{"allocations":[{"repository":"o/a","task":"A","slots":1}]},
    })
    assert "Production-OS Control Surface" in html
    assert "o/a" in html
    assert "NOW" in html
