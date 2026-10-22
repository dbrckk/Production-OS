from __future__ import annotations

from dataclasses import dataclass
import math
import re
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
    "model-routing": ("model-routing", "llm-gateway", "provider routing", "litellm"),
    "agent-observability": ("observability", "tracing", "monitoring", "langfuse"),
    "sandboxed-code-execution": ("sandbox", "code-execution", "isolated code", "microvm"),
    "browser-e2e": ("browser e2e", "cross-browser", "playwright"),
    "autonomous-coding": ("autonomous coding", "repo-level changes", "agentic repository", "opencode", "openhands"),
}


def _haystack(item: dict[str, Any]) -> str:
    parts: list[str] = []
    for key in ("repo", "category", "domain", "tier", "resourceLevel", "integrationComplexity"):
        value = item.get(key)
        if value is not None:
            parts.append(str(value))
    for key in ("capabilities", "bestFor", "languages", "platforms", "runtime"):
        value = item.get(key)
        if isinstance(value, list):
            parts.extend(str(entry) for entry in value)
    return " ".join(parts).lower()


def _eligible_catalog_entry(item: dict[str, Any]) -> bool:
    # Match star-list's default production recommendations: audit/reference
    # entries and inactive GitHub repositories are not deployable choices.
    if str(item.get("tier") or "").casefold() == "audit":
        return False
    if str(item.get("lifecycle") or "").casefold() in {
        "legacy", "reference", "inactive", "deprecated"
    }:
        return False
    github = item.get("github")
    if isinstance(github, dict) and (github.get("archived") or github.get("disabled")):
        return False
    return True


def rank_catalog(
    capability: str,
    catalog: dict[str, Any] | None,
    *,
    limit: int = 5,
    min_score: float = 8.0,
) -> list[ExternalReference]:
    if not isinstance(catalog, dict):
        return []
    repositories = catalog.get("repositories")
    if not isinstance(repositories, list):
        return []

    terms = CAPABILITY_TERMS.get(capability, (capability.replace("-", " "),))
    # Word/phrase boundaries prevent e.g. "ci" matching "specialized".
    patterns = [
        re.compile(r"(?<!\w)" + re.escape(term) + r"(?!\w)")
        for term in terms
    ]
    ranked: list[tuple[float, ExternalReference]] = []

    for item in repositories:
        if not isinstance(item, dict) or not item.get("repo"):
            continue
        if not _eligible_catalog_entry(item):
            continue
        try:
            score = float(item.get("score") or 0)
        except (TypeError, ValueError, OverflowError):
            continue
        # JSON catalogs may contain invalid scores. NaN passes ordinary
        # numeric comparisons and would otherwise pollute ranking results.
        if not math.isfinite(score) or score < min_score:
            continue

        haystack = _haystack(item)
        matches = sum(1 for pattern in patterns if pattern.search(haystack))
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


_WEBSITE_STOPWORDS = frozenset({
    "add", "all", "and", "are", "create", "every", "for", "from", "harden",
    "into", "of", "on", "our", "the", "to", "with",
})


def rank_website_catalog(
    query: str,
    catalog: dict[str, Any] | None,
    *,
    limit: int = 5,
) -> list[dict[str, Any]]:
    """Rank *references* from star-list's independent websites.json catalog.

    These entries are not Git repositories, dependencies or executable agent
    instructions. No website is fetched, installed, or authorized for use by
    returning it. Unrelated references are not proposed.
    """
    if not isinstance(catalog, dict) or not isinstance(catalog.get("websites"), list):
        return []
    if limit <= 0:
        return []
    query_terms = set(re.findall(r"[a-z0-9]+", str(query).casefold()))
    query_terms -= _WEBSITE_STOPWORDS
    if not query_terms:
        return []

    from urllib.parse import urlsplit

    ranked: list[tuple[float, dict[str, Any]]] = []
    seen: set[str] = set()
    for item in catalog["websites"]:
        if not isinstance(item, dict):
            continue
        url = str(item.get("url") or "").strip()
        try:
            parsed = urlsplit(url)
            if (
                parsed.scheme != "https"
                or not parsed.hostname
                or parsed.username is not None
                or parsed.password is not None
            ):
                continue
        except ValueError:
            continue
        normalized_url = url.rstrip("/").casefold()
        if normalized_url in seen:
            continue

        def words(fields: tuple[str, ...]) -> set[str]:
            values: list[str] = []
            for field in fields:
                value = item.get(field)
                if isinstance(value, list):
                    values.extend(str(v) for v in value if isinstance(v, str))
                elif isinstance(value, str):
                    values.append(value)
            return set(re.findall(r"[a-z0-9]+", " ".join(values).casefold()))

        tag_hits = query_terms & words(("tags",))
        purpose_hits = query_terms & words(("bestFor", "name", "type"))
        domain_hits = query_terms & words(("domains",))
        hits = tag_hits | purpose_hits | domain_hits
        # One generic keyword (e.g. "mobile") cannot justify recommending
        # a graphics gallery for an Android release/QA task.
        if len(hits) < 2:
            continue

        relevance = round(min(
            0.45
            + 0.10 * min(len(tag_hits), 3)
            + 0.06 * min(len(purpose_hits), 3)
            + 0.03 * min(len(domain_hits), 2),
            0.95,
        ), 2)
        reference = {
            "kind": "website-reference",
            "name": str(item.get("name") or parsed.hostname),
            "url": url,
            "type": str(item.get("type") or "unknown"),
            "access": str(item.get("access") or "unknown"),
            "reuse": str(item.get("reuse") or "reference-only"),
            "caution": str(item.get("caution") or "Check licensing and access terms."),
            "confidence": relevance,
            "match_terms": sorted(hits),
            "integrationEligible": False,
            "reviewRequired": True,
        }
        seen.add(normalized_url)
        ranked.append((relevance, reference))
    ranked.sort(key=lambda pair: (-pair[0], pair[1]["url"]))
    return [reference for _, reference in ranked[:limit]]
