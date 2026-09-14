from __future__ import annotations

from datetime import datetime, timezone

from .capabilities import extract_capabilities
from .classification import classify_repository
from .components import extract_components
from .deep_fingerprint import analyze_source_evidence
from .models import ActionCandidate, RepoAssessment, RepoEvidence, ScoreBreakdown


def _recent_activity_points(pushed_at: str | None) -> int:
    if not pushed_at:
        return 0
    try:
        pushed = datetime.fromisoformat(pushed_at.replace("Z", "+00:00"))
    except ValueError:
        return 0
    days = (datetime.now(timezone.utc) - pushed).days
    if days <= 30:
        return 10
    if days <= 90:
        return 7
    if days <= 365:
        return 3
    return 0


def score_repository(e: RepoEvidence) -> ScoreBreakdown:
    documentation = 10 if e.has_readme else 0
    tests = 15 if e.has_tests else 0
    ci = 15 if e.has_ci else 0
    if e.has_ci and e.latest_ci_conclusion in {"failure", "cancelled", "timed_out", "action_required"}:
        ci = 5
    release = 15 if e.has_release_workflow else 0
    build = 10 if e.has_manifest else 0
    security = (5 if e.has_security_policy else 0) + (5 if e.has_dependency_automation else 0)
    license_points = 5 if e.has_license else 0
    activity = _recent_activity_points(e.pushed_at)

    total = documentation + tests + ci + release + build + security + license_points + activity
    return ScoreBreakdown(
        total=min(total, 100),
        documentation=documentation,
        tests=tests,
        ci=ci,
        release=release,
        build=build,
        security=security,
        license=license_points,
        activity=activity,
    )


def generate_actions(e: RepoEvidence, score: ScoreBreakdown, profile: str) -> list[ActionCandidate]:
    actions: list[ActionCandidate] = []

    def add(task, rationale, criteria, evidence, *, impact, urgency, risk, release, effort):
        action = ActionCandidate(
            repository=e.full_name,
            task=task,
            rationale=rationale,
            acceptance_criteria=criteria,
            evidence=evidence,
            impact=impact,
            urgency=urgency,
            risk_reduction=risk,
            release_proximity=release,
            effort=effort,
        )
        action.compute_priority()
        actions.append(action)

    release_weight = 10 if profile in {"android-app", "android-game"} else 8

    if e.has_ci and e.latest_ci_conclusion in {"failure", "cancelled", "timed_out", "action_required"}:
        add(
            "Restore the default branch CI to green",
            "The latest GitHub Actions run on the default branch is not successful. Broken verification blocks trustworthy autonomous production.",
            ["Latest required CI run succeeds", "Root cause is fixed rather than bypassed", "No verification gate is weakened"],
            [f"latest_ci_status={e.latest_ci_status}", f"latest_ci_conclusion={e.latest_ci_conclusion}", f"latest_ci_url={e.latest_ci_url}"],
            impact=10, urgency=10, risk=10, release=10, effort=2,
        )

    if not e.has_tests:
        add(
            "Add an executable automated test baseline",
            "No automated test evidence was detected. Autonomous changes cannot be promoted safely without a verification gate.",
            ["At least one meaningful automated test executes", "Test command exits non-zero on failure", "Test command is documented"],
            ["has_tests=false", f"profile={profile}"],
            impact=9, urgency=9, risk=10, release=release_weight, effort=3,
        )

    if not e.has_ci:
        add(
            "Add continuous integration for every change",
            "No GitHub Actions workflow was detected, so repository health is not automatically verified.",
            ["CI runs on pull requests and main", "Build/test failures block the workflow", "Workflow is reproducible"],
            ["has_ci=false", f"profile={profile}"],
            impact=9, urgency=8, risk=10, release=release_weight, effort=3,
        )

    if not e.has_release_workflow and score.total >= 45:
        add(
            "Create a deterministic release pipeline",
            "The repository has development foundations but no release workflow was detected.",
            ["Release artifacts are built by CI", "Artifacts are versioned", "Release remains non-destructive by default"],
            ["has_release_workflow=false", f"maturity_score={score.total}", f"profile={profile}"],
            impact=8, urgency=6, risk=7, release=10, effort=5,
        )

    if profile in {"android-app", "android-game"} and e.has_ci and not e.has_release_workflow:
        add(
            "Add Android release-readiness gate",
            "Android project detected with CI but without a release workflow.",
            ["Release AAB/APK is built in CI", "Signing remains outside untrusted workspaces", "Release artifact can be traced to a commit"],
            ["android_profile=true", "has_ci=true", "has_release_workflow=false"],
            impact=9, urgency=7, risk=8, release=10, effort=4,
        )

    if not e.has_security_policy or not e.has_dependency_automation:
        missing = []
        if not e.has_security_policy:
            missing.append("security policy")
        if not e.has_dependency_automation:
            missing.append("dependency automation")
        add(
            "Harden repository maintenance and supply-chain hygiene",
            f"Missing: {', '.join(missing)}.",
            ["Security reporting policy exists", "Dependency updates are automated or explicitly governed"],
            [f"has_security_policy={e.has_security_policy}", f"has_dependency_automation={e.has_dependency_automation}"],
            impact=6, urgency=5, risk=8, release=5, effort=3,
        )

    if not e.has_readme:
        add(
            "Document project purpose, runbook and definition of done",
            "The repository has no detected README, which increases coordination cost for humans and agents.",
            ["README explains purpose", "Local run/test commands are documented", "Definition of done is explicit"],
            ["has_readme=false"],
            impact=6, urgency=6, risk=5, release=5, effort=2,
        )

    if not e.has_manifest:
        add(
            "Add a reproducible project/build manifest",
            "No supported dependency/build manifest was detected.",
            ["Toolchain/version requirements are explicit", "Dependencies can be installed reproducibly", "Build/test entrypoint is documented"],
            ["has_manifest=false"],
            impact=8, urgency=8, risk=8, release=7, effort=3,
        )

    actions.sort(key=lambda item: item.priority, reverse=True)
    return actions


def assess_repository(evidence: RepoEvidence) -> RepoAssessment:
    score = score_repository(evidence)
    profile = classify_repository(evidence)
    capabilities = extract_capabilities(evidence)
    source_signals = analyze_source_evidence(evidence)
    components = extract_components(evidence)
    return RepoAssessment(
        evidence=evidence,
        score=score,
        actions=generate_actions(evidence, score, profile.kind),
        profile=profile.kind,
        profile_confidence=profile.confidence,
        profile_signals=list(profile.signals),
        capabilities=capabilities,
        source_signals=source_signals,
        components=components,
    )
