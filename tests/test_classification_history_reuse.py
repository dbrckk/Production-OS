from production_os.classification import classify_repository
from production_os.history import build_snapshot, detect_regressions
from production_os.models import RepoEvidence
from production_os.reuse import detect_reuse
from production_os.scoring import assess_repository


def ev(name="demo", **kwargs):
    base = dict(
        name=name,
        full_name=f"owner/{name}",
        html_url=f"https://github.com/owner/{name}",
        pushed_at="2099-01-01T00:00:00Z",
    )
    base.update(kwargs)
    return RepoEvidence(**base)


def test_android_game_classification():
    profile = classify_repository(
        ev(
            detected_files=["build.gradle.kts"],
            readme_text="Android action roguelite built with libGDX",
        )
    )
    assert profile.kind == "android-game"
    assert profile.confidence >= 0.9


def test_regression_detection():
    old = {"repositories": {"owner/demo": {"score": 80}}}
    assessment = assess_repository(ev())
    current = build_snapshot("owner", [assessment])
    regressions = detect_regressions(old, current, threshold=5)
    assert regressions
    assert regressions[0].repository == "owner/demo"


def test_cross_repo_reuse_detection():
    source = assess_repository(
        ev(
            "source",
            detected_files=["build.gradle.kts"],
            readme_text="Android app",
            has_ci=True,
            has_tests=True,
        )
    )
    target = assess_repository(
        ev(
            "target",
            detected_files=["build.gradle.kts"],
            readme_text="Android app",
            has_ci=False,
            has_tests=False,
        )
    )
    opportunities = detect_reuse([source, target])
    capabilities = {item.capability for item in opportunities}
    assert "github-actions-ci" in capabilities
    assert "automated-tests" in capabilities
