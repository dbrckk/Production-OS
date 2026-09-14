from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ExternalReference:
    capability: str
    repository: str
    confidence: float
    rationale: str

    def to_dict(self) -> dict:
        return {
            "capability": self.capability,
            "repository": self.repository,
            "confidence": self.confidence,
            "rationale": self.rationale,
        }


REFERENCE_MAP: dict[str, tuple[str, ...]] = {
    "backtesting": ("QuantConnect/Lean", "nautechsystems/nautilus_trader", "polakowo/vectorbt"),
    "experiment-registry": ("mlflow/mlflow",),
    "queued-workers": ("celery/celery", "rq/rq"),
    "docker-compose-deployment": ("docker/compose",),
    "android-device-qa": ("android/android-test",),
    "release-automation": ("semantic-release/semantic-release",),
    "dependency-automation": ("dependabot/dependabot-core", "renovatebot/renovate"),
}


def suggest_external_references(
    capability: str,
    available_star_repositories: set[str] | None = None,
) -> list[ExternalReference]:
    candidates = REFERENCE_MAP.get(capability, ())
    refs: list[ExternalReference] = []

    for repository in candidates:
        if available_star_repositories is not None and repository not in available_star_repositories:
            continue
        refs.append(
            ExternalReference(
                capability=capability,
                repository=repository,
                confidence=0.80,
                rationale=f"Known reference implementation for capability '{capability}'.",
            )
        )

    return refs
