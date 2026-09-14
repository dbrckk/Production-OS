from __future__ import annotations

from dataclasses import dataclass

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

    def to_dict(self) -> dict:
        return {
            "source": self.source,
            "target": self.target,
            "capability": self.capability,
            "confidence": self.confidence,
            "rationale": self.rationale,
            "evidence": list(self.evidence),
            "components": list(self.components),
        }


def _compatible(source: RepoAssessment, target: RepoAssessment) -> bool:
    if source.profile == target.profile:
        return True
    if {source.profile, target.profile} <= {"android-app", "android-game"}:
        return True
    if {source.profile, target.profile} <= {"automation-platform", "python-service"}:
        return True
    return False


def _component_candidates(source: RepoAssessment, capability: str) -> tuple[dict, ...]:
    matches = []
    for component in source.components:
        if capability not in component.capability_hints:
            continue
        matches.append({
            "name": component.name,
            "kind": component.kind,
            "path": component.path,
            "language": component.language,
            "dependencies": list(component.dependencies),
            "confidence": component.confidence,
            "test_like": component.test_like,
        })
    matches.sort(key=lambda item: (-item["confidence"], item["path"], item["name"]))
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

                key = (source.evidence.full_name, target.evidence.full_name, capability.name)
                if key in seen:
                    continue
                seen.add(key)

                family_factor = 1.0 if source.profile == target.profile else 0.88
                confidence = round(capability.confidence * family_factor, 2)
                components = _component_candidates(source, capability.name)
                opportunities.append(
                    ReuseOpportunity(
                        source=source.evidence.full_name,
                        target=target.evidence.full_name,
                        capability=capability.name,
                        confidence=confidence,
                        rationale=(
                            f"{source.evidence.full_name} has evidence-backed capability "
                            f"'{capability.name}' that is absent from {target.evidence.full_name}."
                        ),
                        evidence=capability.evidence,
                        components=components,
                    )
                )

    opportunities.sort(
        key=lambda item: (
            -item.confidence,
            -len(item.components),
            item.target,
            item.capability,
            item.source,
        )
    )
    return opportunities
