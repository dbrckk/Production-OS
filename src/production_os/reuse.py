from __future__ import annotations

from dataclasses import dataclass

from .adaptation import score_adaptation_risk
from .adaptation_plan import build_adaptation_plan
from .models import RepoAssessment


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


def _component_candidates(
    source: RepoAssessment,
    target: RepoAssessment,
    capability: str,
) -> tuple[dict, ...]:
    matches = []

    for component in source.components:
        if capability not in component.capability_hints:
            continue

        adaptation = score_adaptation_risk(
            source,
            target,
            capability,
            component,
        )

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

            for capability in source.capabilities:
                if not capability.portable or capability.name in target_caps:
                    continue
                if capability.confidence < 0.75:
                    continue

                key = (
                    source.evidence.full_name,
                    target.evidence.full_name,
                    capability.name,
                )
                if key in seen:
                    continue
                seen.add(key)

                family_factor = 1.0 if source.profile == target.profile else 0.88
                components = _component_candidates(
                    source,
                    target,
                    capability.name,
                )

                risk_factor = 1.0
                if components:
                    best_risk = components[0]["adaptation_risk"]
                    risk_factor = max(0.55, 1.0 - (best_risk / 150.0))

                confidence = round(
                    capability.confidence * family_factor * risk_factor,
                    2,
                )

                plan = build_adaptation_plan(
                    source,
                    target,
                    capability.name,
                    list(components),
                ).to_dict()

                opportunities.append(
                    ReuseOpportunity(
                        source=source.evidence.full_name,
                        target=target.evidence.full_name,
                        capability=capability.name,
                        confidence=confidence,
                        rationale=(
                            f"{source.evidence.full_name} has evidence-backed capability "
                            f"'{capability.name}' that is absent from "
                            f"{target.evidence.full_name}. Component candidates are "
                            f"ranked by adaptation risk and test coverage."
                        ),
                        evidence=capability.evidence,
                        components=components,
                        adaptation_plan=plan,
                    )
                )

    opportunities.sort(
        key=lambda item: (
            -item.confidence,
            item.adaptation_plan.get("overall_risk", 101)
            if item.adaptation_plan else 101,
            item.components[0]["adaptation_risk"] if item.components else 101,
            -len(item.components),
            item.target,
            item.capability,
            item.source,
        )
    )
    return opportunities
