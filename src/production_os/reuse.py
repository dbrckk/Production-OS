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

    def to_dict(self) -> dict:
        return {
            "source": self.source,
            "target": self.target,
            "capability": self.capability,
            "confidence": self.confidence,
            "rationale": self.rationale,
        }


def detect_reuse(assessments: list[RepoAssessment]) -> list[ReuseOpportunity]:
    opportunities: list[ReuseOpportunity] = []

    for target in assessments:
        for source in assessments:
            if source.evidence.full_name == target.evidence.full_name:
                continue

            same_family = (
                source.profile == target.profile
                or {source.profile, target.profile} <= {"android-app", "android-game"}
            )
            if not same_family:
                continue

            pairs = [
                ("CI workflow", source.evidence.has_ci, target.evidence.has_ci),
                ("release workflow", source.evidence.has_release_workflow, target.evidence.has_release_workflow),
                ("security policy", source.evidence.has_security_policy, target.evidence.has_security_policy),
                ("dependency automation", source.evidence.has_dependency_automation, target.evidence.has_dependency_automation),
                ("test baseline", source.evidence.has_tests, target.evidence.has_tests),
            ]

            for capability, source_has, target_has in pairs:
                if source_has and not target_has:
                    confidence = 0.90 if source.profile == target.profile else 0.78
                    opportunities.append(
                        ReuseOpportunity(
                            source=source.evidence.full_name,
                            target=target.evidence.full_name,
                            capability=capability,
                            confidence=confidence,
                            rationale=(
                                f"{source.evidence.full_name} already exposes evidence for {capability} "
                                f"while {target.evidence.full_name} does not."
                            ),
                        )
                    )

    opportunities.sort(key=lambda item: item.confidence, reverse=True)
    return opportunities
