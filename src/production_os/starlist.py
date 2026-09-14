from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class ExternalReference:
    capability: str
    repository: str
    confidence: float
    rationale: str
    star_score: float | None = None
    tier: str | None = None
    domain: str | None = None

    def to_dict(self) -> dict:
        return {
            "capability": self.capability,
            "repository": self.repository,
            "confidence": self.confidence,
            "rationale": self.rationale,
            "star_score": self.star_score,
            "tier": self.tier,
            "domain": self.domain,
        }


CAPABILITY_TERMS: dict[str, tuple[str, ...]] = {
    "automated-tests": ("test", "testing", "qa", "pytest"),
    "github-actions-ci": ("ci", "github actions", "automation"),
    "release-automation": ("release", "deploy", "deployment", "publishing"),
    "android-device-qa": ("android", "testing", "device", "emulator"),
    "dependency-automation": ("dependency", "dependencies", "renovate", "dependabot"),
    "backtesting": ("backtest", "backtesting", "quant", "trading"),
    "experiment-registry": ("experiment", "mlops", "tracking"),
    "queued-workers": ("queue", "worker", "celery", "task"),
    "docker-compose-deployment": ("docker", "compose", "container"),
}


def _haystack(item: dict[str, Any]) -> str:
    parts: list[str] = []
    for key in ("repo", "category", "domain", "tier", "resourceLevel", "integrationComplexity"):
        value = item.get(key)
        if value is not None:
            parts.append(str(value))
    for key in ("capabilities", "bestFor", "avoidWhen", "languages", "platforms", "runtime"):
        value = item.get(key)
        if isinstance(value, list):
            parts.extend(str(entry) for entry in value)
    return " ".join(parts).lower()


def rank_catalog(
    capability: str,
    catalog: dict[str, Any] | None,
    *,
    limit: int = 5,
    min_score: float = 8.0,
) -> list[ExternalReference]:
    if not catalog:
        return []

    terms = CAPABILITY_TERMS.get(capability, (capability.replace("-", " "),))
    ranked: list[tuple[float, ExternalReference]] = []

    for item in catalog.get("repositories", []):
        if not isinstance(item, dict) or not item.get("repo"):
            continue
        score = float(item.get("score") or 0)
        if score < min_score:
            continue

        haystack = _haystack(item)
        matches = sum(1 for term in terms if term in haystack)
        if not matches:
            continue

        semantic = min(matches / max(len(terms), 1), 1.0)
        quality = min(score / 10.0, 1.0)
        confidence = round(0.55 * quality + 0.45 * semantic, 2)
        ref = ExternalReference(
            capability=capability,
            repository=str(item["repo"]),
            confidence=confidence,
            rationale=(
                f"star-list match for '{capability}': score={score:g}, "
                f"tier={item.get('tier', 'unknown')}, matches={matches}/{len(terms)}."
            ),
            star_score=score,
            tier=item.get("tier"),
            domain=item.get("domain"),
        )
        ranked.append((confidence, ref))

    ranked.sort(
        key=lambda pair: (
            -pair[0],
            -(pair[1].star_score or 0),
            pair[1].repository.lower(),
        )
    )
    return [ref for _, ref in ranked[:limit]]


def suggest_external_references(
    capability: str,
    catalog: dict[str, Any] | None = None,
    *,
    limit: int = 5,
) -> list[ExternalReference]:
    return rank_catalog(capability, catalog, limit=limit)
