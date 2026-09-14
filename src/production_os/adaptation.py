from __future__ import annotations

from dataclasses import dataclass

from .models import RepoAssessment


@dataclass(frozen=True, slots=True)
class ComponentAdaptation:
    source_repository: str
    target_repository: str
    capability: str
    component_name: str
    path: str
    language: str
    risk_score: int
    risk_level: str
    reasons: tuple[str, ...]
    linked_tests: tuple[dict, ...]

    def to_dict(self) -> dict:
        return {
            "source_repository": self.source_repository,
            "target_repository": self.target_repository,
            "capability": self.capability,
            "component_name": self.component_name,
            "path": self.path,
            "language": self.language,
            "risk_score": self.risk_score,
            "risk_level": self.risk_level,
            "reasons": list(self.reasons),
            "linked_tests": list(self.linked_tests),
        }


def _normalize(name: str) -> str:
    return "".join(ch.lower() for ch in name if ch.isalnum())


def link_tests(source: RepoAssessment, component) -> tuple[dict, ...]:
    target = _normalize(component.name)
    matches = []

    for candidate in source.components:
        if not candidate.test_like:
            continue
        cname = _normalize(candidate.name)
        path = candidate.path.lower()

        score = 0
        reasons = []
        if target and target in cname:
            score += 5
            reasons.append("test symbol references component name")
        if target and target in _normalize(path):
            score += 4
            reasons.append("test path references component name")
        if set(candidate.capability_hints) & set(component.capability_hints):
            score += 2
            reasons.append("shares capability hint")
        if set(candidate.dependencies) & set(component.dependencies):
            score += 1
            reasons.append("shares dependencies")

        if score:
            matches.append({
                "name": candidate.name,
                "path": candidate.path,
                "language": candidate.language,
                "link_score": score,
                "reasons": reasons,
            })

    matches.sort(key=lambda item: (-item["link_score"], item["path"], item["name"]))
    return tuple(matches[:6])


def score_adaptation_risk(
    source: RepoAssessment,
    target: RepoAssessment,
    capability: str,
    component,
) -> ComponentAdaptation:
    risk = 10
    reasons: list[str] = []

    if source.profile != target.profile:
        risk += 14
        reasons.append(f"profile mismatch: {source.profile} -> {target.profile}")

    if component.language and target.evidence.language:
        target_lang = target.evidence.language.lower()
        comp_lang = component.language.lower()
        compatible = (
            comp_lang in target_lang
            or (comp_lang in {"kotlin", "java"} and target_lang in {"kotlin", "java"})
        )
        if not compatible:
            risk += 22
            reasons.append(
                f"language mismatch: component={component.language}, target={target.evidence.language}"
            )

    dep_count = len(component.dependencies)
    if dep_count >= 8:
        risk += 20
        reasons.append(f"high dependency count: {dep_count}")
    elif dep_count >= 4:
        risk += 10
        reasons.append(f"moderate dependency count: {dep_count}")
    elif dep_count:
        risk += 4
        reasons.append(f"dependency count: {dep_count}")

    linked_tests = link_tests(source, component)
    if linked_tests:
        risk -= 12
        reasons.append(f"linked tests found: {len(linked_tests)}")
    else:
        risk += 12
        reasons.append("no linked tests found")

    if capability in component.capability_hints:
        risk -= 10
        reasons.append("component directly matches required capability")

    if component.test_like:
        risk += 25
        reasons.append("candidate is itself test-like")

    if "ui" in component.path.lower() or "screen" in component.name.lower():
        risk += 8
        reasons.append("UI-coupled component")

    risk = max(0, min(100, risk))
    if risk <= 25:
        level = "low"
    elif risk <= 50:
        level = "medium"
    elif risk <= 75:
        level = "high"
    else:
        level = "very-high"

    return ComponentAdaptation(
        source_repository=source.evidence.full_name,
        target_repository=target.evidence.full_name,
        capability=capability,
        component_name=component.name,
        path=component.path,
        language=component.language,
        risk_score=risk,
        risk_level=level,
        reasons=tuple(reasons),
        linked_tests=linked_tests,
    )
