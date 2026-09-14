from __future__ import annotations

from dataclasses import dataclass

from .adaptation import score_adaptation_risk
from .adaptation_plan import build_adaptation_plan
from .compatibility import check_dependency_compatibility
from .models import RepoAssessment
from .validation import build_validation_plan
from .versioning import compare_dependency_versions


@dataclass(frozen=True, slots=True)
class ReuseOpportunity:
    source: str
    target: str
    capability: str
    confidence: float
    rationale: str
    evidence: tuple[str, ...] = ()
    components: tuple[dict, ...] = ()
    adaptation_plan: dict | None = None

    def to_dict(self) -> dict:
        return {
            "source": self.source,
            "target": self.target,
            "capability": self.capability,
            "confidence": self.confidence,
            "rationale": self.rationale,
            "evidence": list(self.evidence),
            "components": list(self.components),
            "adaptation_plan": self.adaptation_plan,
        }


def _compatible(source: RepoAssessment, target: RepoAssessment) -> bool:
    if source.profile == target.profile:
        return True
    if {source.profile, target.profile} <= {"android-app", "android-game"}:
        return True
    if {source.profile, target.profile} <= {"automation-platform", "python-service"}:
        return True
    return False


def _component_candidates(source: RepoAssessment, target: RepoAssessment, capability: str) -> tuple[dict, ...]:
    matches = []
    for component in source.components:
        if capability not in component.capability_hints:
            continue
        adaptation = score_adaptation_risk(source, target, capability, component)
        matches.append({
            "name": component.name,
            "kind": component.kind,
            "path": component.path,
            "language": component.language,
            "dependencies": list(component.dependencies),
            "confidence": component.confidence,
            "test_like": component.test_like,
            "adaptation_risk": adaptation.risk_score,
            "adaptation_risk_level": adaptation.risk_level,
            "adaptation_reasons": list(adaptation.reasons),
            "linked_tests": list(adaptation.linked_tests),
        })

    matches.sort(
        key=lambda item: (
            item["adaptation_risk"],
            -item["confidence"],
            -len(item["linked_tests"]),
            item["path"],
            item["name"],
        )
    )
    return tuple(matches[:8])


def detect_reuse(assessments: list[RepoAssessment]) -> list[ReuseOpportunity]:
    opportunities: list[ReuseOpportunity] = []
    seen: set[tuple[str, str, str]] = set()

    for target in assessments:
        target_caps = {cap.name for cap in target.capabilities}

        for source in assessments:
            if source.evidence.full_name == target.evidence.full_name:
                continue
            if not _compatible(source, target):
                continue

            version_checks = [
                row.to_dict()
                for row in compare_dependency_versions(source, target)
            ]

            for capability in source.capabilities:
                if not capability.portable or capability.name in target_caps:
                    continue
                if capability.confidence < 0.75:
                    continue

                key = (source.evidence.full_name, target.evidence.full_name, capability.name)
                if key in seen:
                    continue
                seen.add(key)

                family_factor = 1.0 if source.profile == target.profile else 0.88
                components = _component_candidates(source, target, capability.name)

                risk_factor = 1.0
                if components:
                    best_risk = components[0]["adaptation_risk"]
                    risk_factor = max(0.55, 1.0 - (best_risk / 150.0))

                confidence = round(capability.confidence * family_factor * risk_factor, 2)

                plan = build_adaptation_plan(
                    source,
                    target,
                    capability.name,
                    list(components),
                ).to_dict()

                dependency_checks = [
                    item.to_dict()
                    for item in check_dependency_compatibility(
                        target,
                        plan.get("recreate", []),
                    )
                ]

                relevant_versions = [
                    item for item in version_checks
                    if (
                        item["status"] in {"major-version-mismatch", "same-major-review-required"}
                        or item["dependency"].split(":")[-1].lower()
                        in {dep.lower() for dep in plan.get("recreate", [])}
                    )
                ]

                validation_plan = [
                    step.to_dict()
                    for step in build_validation_plan(
                        target,
                        capability.name,
                        plan,
                        dependency_checks,
                    )
                ]

                missing = [
                    item["dependency"]
                    for item in dependency_checks
                    if item["status"] != "available"
                ]
                major_mismatches = [
                    item["dependency"]
                    for item in relevant_versions
                    if item["status"] == "major-version-mismatch"
                ]

                plan["dependency_compatibility"] = dependency_checks
                plan["dependency_version_compatibility"] = relevant_versions
                plan["missing_dependencies"] = missing
                plan["major_version_mismatches"] = major_mismatches
                plan["compatible_for_adaptation"] = (
                    plan.get("overall_risk", 101) <= 50
                    and len(missing) <= 3
                    and not major_mismatches
                )
                plan["validation_plan"] = validation_plan

                opportunities.append(
                    ReuseOpportunity(
                        source=source.evidence.full_name,
                        target=target.evidence.full_name,
                        capability=capability.name,
                        confidence=confidence,
                        rationale=(
                            f"{source.evidence.full_name} has evidence-backed capability "
                            f"'{capability.name}' that is absent from {target.evidence.full_name}. "
                            f"Compatibility, versions and validation requirements were evaluated."
                        ),
                        evidence=capability.evidence,
                        components=components,
                        adaptation_plan=plan,
                    )
                )

    opportunities.sort(
        key=lambda item: (
            not bool(item.adaptation_plan and item.adaptation_plan.get("compatible_for_adaptation")),
            item.adaptation_plan.get("overall_risk", 101) if item.adaptation_plan else 101,
            len(item.adaptation_plan.get("major_version_mismatches", [])) if item.adaptation_plan else 999,
            len(item.adaptation_plan.get("missing_dependencies", [])) if item.adaptation_plan else 999,
            -item.confidence,
            item.target,
            item.capability,
            item.source,
        )
    )
    return opportunities
