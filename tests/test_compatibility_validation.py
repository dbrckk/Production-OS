from production_os.compatibility import check_dependency_compatibility
from production_os.models import RepoAssessment, RepoEvidence, ScoreBreakdown
from production_os.validation import build_validation_plan


def assessment(name, language="Kotlin", docs=None, signals=None):
    return RepoAssessment(
        evidence=RepoEvidence(
            name=name,
            full_name=f"owner/{name}",
            html_url=f"https://github.com/owner/{name}",
            language=language,
            has_ci=True,
            source_documents=docs or {},
        ),
        score=ScoreBreakdown(0,0,0,0,0,0,0,0,0),
        actions=[],
        source_signals=signals or [],
    )


def test_dependency_compatibility_detects_target_dependency():
    target = assessment(
        "target",
        docs={"build.gradle.kts": 'implementation("com.android.billingclient:billing:7.1.1")'},
    )
    checks = check_dependency_compatibility(target, ["BillingClient", "UnknownDep"])
    by_name = {item.dependency: item.status for item in checks}
    assert by_name["BillingClient"] == "available"
    assert by_name["UnknownDep"] == "missing-or-unverified"


def test_android_validation_plan_is_complete():
    target = assessment("target")
    plan = {
        "copy_or_adapt": [{"name": "BillingManager"}],
        "reuse_tests": [{"name": "BillingManagerTest"}],
    }
    checks = [{"dependency": "BillingClient", "status": "available"}]
    steps = build_validation_plan(target, "android-play-billing", plan, checks)
    kinds = [step.kind for step in steps]
    assert "compile" in kinds
    assert "unit-tests" in kinds
    assert "device-smoke" in kinds
    assert "billing" in kinds
    assert "ci" in kinds
    assert "regression" in kinds
