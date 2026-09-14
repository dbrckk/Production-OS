from production_os.adaptation import link_tests, score_adaptation_risk
from production_os.components import Component
from production_os.models import RepoAssessment, RepoEvidence, ScoreBreakdown


def assessment(name, profile, language, components):
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
        components=components,
    )


def test_links_component_to_matching_test():
    component = Component(
        name="BillingManager",
        kind="class",
        path="src/BillingManager.kt",
        language="kotlin",
        confidence=0.97,
        dependencies=("BillingClient",),
        capability_hints=("android-play-billing",),
    )
    test = Component(
        name="BillingManagerTest",
        kind="class",
        path="src/test/BillingManagerTest.kt",
        language="kotlin",
        confidence=0.97,
        dependencies=("BillingClient",),
        capability_hints=("android-play-billing",),
        test_like=True,
    )
    src = assessment("source", "android-app", "Kotlin", [component, test])
    links = link_tests(src, component)
    assert links
    assert links[0]["name"] == "BillingManagerTest"


def test_tests_reduce_adaptation_risk():
    component = Component(
        name="BillingManager",
        kind="class",
        path="src/BillingManager.kt",
        language="kotlin",
        confidence=0.97,
        dependencies=("BillingClient",),
        capability_hints=("android-play-billing",),
    )
    test = Component(
        name="BillingManagerTest",
        kind="class",
        path="src/test/BillingManagerTest.kt",
        language="kotlin",
        confidence=0.97,
        dependencies=("BillingClient",),
        capability_hints=("android-play-billing",),
        test_like=True,
    )
    source = assessment("source", "android-app", "Kotlin", [component, test])
    target = assessment("target", "android-game", "Kotlin", [])
    scored = score_adaptation_risk(source, target, "android-play-billing", component)
    assert scored.risk_score < 40
    assert scored.linked_tests
