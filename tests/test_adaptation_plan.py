from production_os.adaptation_plan import build_adaptation_plan
from production_os.models import RepoAssessment, RepoEvidence, ScoreBreakdown


def assessment(name, profile, language):
    return RepoAssessment(
        evidence=RepoEvidence(
            name=name,
            full_name=f"owner/{name}",
            html_url=f"https://github.com/owner/{name}",
            language=language,
        ),
        score=ScoreBreakdown(0,0,0,0,0,0,0,0,0),
        actions=[],
        profile=profile,
    )


def test_plan_separates_reusable_and_coupled_components():
    source = assessment("source", "android-app", "Kotlin")
    target = assessment("target", "android-game", "Kotlin")

    components = [
        {
            "name": "BillingManager",
            "path": "core/BillingManager.kt",
            "language": "kotlin",
            "dependencies": ["BillingClient"],
            "adaptation_risk": 20,
            "linked_tests": [{"name": "BillingManagerTest", "path": "tests/BillingManagerTest.kt"}],
            "test_like": False,
        },
        {
            "name": "PremiumScreen",
            "path": "ui/PremiumScreen.kt",
            "language": "kotlin",
            "dependencies": [],
            "adaptation_risk": 35,
            "linked_tests": [],
            "test_like": False,
        },
    ]

    plan = build_adaptation_plan(source, target, "android-play-billing", components)
    assert [item["name"] for item in plan.copy_or_adapt] == ["BillingManager"]
    assert [item["name"] for item in plan.do_not_copy] == ["PremiumScreen"]
    assert "BillingClient" in plan.recreate
    assert plan.reuse_tests
    assert plan.strategy == "component-adaptation"


def test_plan_falls_back_to_architecture_pattern():
    source = assessment("source", "python-service", "Python")
    target = assessment("target", "automation-platform", "Python")
    components = [{
        "name": "DashboardView",
        "path": "ui/dashboard.py",
        "language": "python",
        "dependencies": [],
        "adaptation_risk": 80,
        "linked_tests": [],
        "test_like": False,
    }]
    plan = build_adaptation_plan(source, target, "audit-trail", components)
    assert plan.strategy == "architecture-pattern-only"
    assert not plan.copy_or_adapt
