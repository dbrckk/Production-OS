from __future__ import annotations

from dataclasses import dataclass

from .models import RepoAssessment


@dataclass(frozen=True, slots=True)
class DependencyCompatibility:
    dependency: str
    status: str
    confidence: float
    evidence: tuple[str, ...]

    def to_dict(self) -> dict:
        return {
            "dependency": self.dependency,
            "status": self.status,
            "confidence": self.confidence,
            "evidence": list(self.evidence),
        }


def _target_tokens(target: RepoAssessment) -> set[str]:
    tokens: set[str] = set()
    for signal in target.source_signals:
        tokens.add(str(signal.value).lower())
        tokens.add(str(signal.kind).lower())
    for component in target.components:
        tokens.add(component.name.lower())
        tokens.update(dep.lower() for dep in component.dependencies)
    for path, text in target.evidence.source_documents.items():
        tokens.add(path.lower())
        for word in text.lower().replace('"', " ").replace("'", " ").split():
            if 2 <= len(word) <= 80:
                tokens.add(word.strip(",()[]{}:;"))
    return tokens


ALIASES: dict[str, tuple[str, ...]] = {
    "billingclient": ("billingclient", "com.android.billingclient", "play-billing"),
    "redis": ("redis",),
    "celery": ("celery",),
    "fastapi": ("fastapi",),
    "pytest": ("pytest",),
    "optuna": ("optuna",),
}


def check_dependency_compatibility(
    target: RepoAssessment,
    dependencies: list[str] | tuple[str, ...],
) -> list[DependencyCompatibility]:
    tokens = _target_tokens(target)
    source_text = "\n".join(
        target.evidence.source_documents.values()
    ).lower()
    results: list[DependencyCompatibility] = []

    for dependency in dependencies:
        dep = str(dependency).strip()
        if not dep:
            continue
        key = dep.lower()
        aliases = ALIASES.get(key, (key,))
        matched = [
            alias
            for alias in aliases
            if alias in tokens or alias in source_text
        ]

        if matched:
            results.append(
                DependencyCompatibility(
                    dependency=dep,
                    status="available",
                    confidence=0.92,
                    evidence=tuple(f"target contains {alias}" for alias in matched),
                )
            )
        else:
            results.append(
                DependencyCompatibility(
                    dependency=dep,
                    status="missing-or-unverified",
                    confidence=0.70,
                    evidence=("no matching target dependency evidence found",),
                )
            )

    return results
