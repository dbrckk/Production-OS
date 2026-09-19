from __future__ import annotations

from dataclasses import dataclass

from .models import RepoEvidence


@dataclass(frozen=True, slots=True)
class ProjectProfile:
    kind: str
    confidence: float
    signals: tuple[str, ...]


def classify_repository(e: RepoEvidence) -> ProjectProfile:
    names = {name.lower() for name in e.detected_files}
    text = e.readme_text.lower()
    signals: list[str] = []

    if "build.gradle.kts" in names or "build.gradle" in names:
        if any(term in text for term in ("android", "jetpack compose", "libgdx", "play store")):
            signals.append("gradle+android")
            if any(term in text for term in ("game", "roguelite", "libgdx", "godot")):
                signals.append("game")
                return ProjectProfile("android-game", 0.95, tuple(signals))
            return ProjectProfile("android-app", 0.92, tuple(signals))

    if any(term in text for term in ("visual-asset production", "visual asset production", "asset-forge")):
        signals.append("visual-assets")
        if any(term in text for term in ("sprite", "gltf", "svg", "godot", "atlas")):
            signals.append("multi-format")
            return ProjectProfile("asset-production-platform", 0.96, tuple(signals))
        return ProjectProfile("asset-production-platform", 0.88, tuple(signals))

    if "pyproject.toml" in names or "requirements.txt" in names:
        signals.append("python")
        if any(term in text for term in ("trading", "backtest", "walk-forward", "market data")):
            signals.append("quant-research")
            return ProjectProfile("quant-research", 0.92, tuple(signals))
        if any(term in text for term in ("agent", "orchestration", "autonomous", "control plane")):
            signals.append("automation")
            return ProjectProfile("automation-platform", 0.88, tuple(signals))
        return ProjectProfile("python-service", 0.72, tuple(signals))

    if "package.json" in names:
        signals.append("node")
        return ProjectProfile("node-project", 0.70, tuple(signals))

    if any(term in text for term in ("curated", "catalog", "awesome list", "star-list")):
        signals.append("knowledge-base")
        return ProjectProfile("knowledge-base", 0.78, tuple(signals))

    return ProjectProfile("generic", 0.30, tuple(signals))
