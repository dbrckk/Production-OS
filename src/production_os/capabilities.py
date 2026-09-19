from __future__ import annotations

from dataclasses import dataclass

from .models import RepoEvidence


@dataclass(frozen=True, slots=True)
class Capability:
    name: str
    confidence: float
    evidence: tuple[str, ...]
    portable: bool = True

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "confidence": self.confidence,
            "evidence": list(self.evidence),
            "portable": self.portable,
        }


def _contains(text: str, *terms: str) -> bool:
    return any(term in text for term in terms)


def extract_capabilities(e: RepoEvidence) -> list[Capability]:
    text = e.readme_text.lower()
    files = {name.lower() for name in e.detected_files}
    workflows = {name.lower() for name in e.workflow_names}
    caps: dict[str, Capability] = {}

    def add(name: str, confidence: float, evidence: list[str], portable: bool = True) -> None:
        current = caps.get(name)
        candidate = Capability(name, round(confidence, 2), tuple(evidence), portable)
        if current is None or candidate.confidence > current.confidence:
            caps[name] = candidate

    if e.has_ci:
        add("github-actions-ci", 0.98, ["github workflows detected"])
    if e.has_tests:
        add("automated-tests", 0.95, ["test evidence detected"])
    if e.has_release_workflow:
        add("release-automation", 0.92, ["release/publish workflow detected"])
    if e.has_security_policy:
        add("security-policy", 0.99, ["SECURITY.md detected"])
    if e.has_dependency_automation:
        add("dependency-automation", 0.99, ["Dependabot/Renovate detected"])

    if _contains(text, "google play billing", "play billing", "billingclient"):
        add("android-play-billing", 0.94, ["README mentions Google Play Billing"])
    if _contains(text, "admob", "google mobile ads"):
        add("android-admob", 0.94, ["README mentions AdMob/Google Mobile Ads"])
    if _contains(text, "ump", "user messaging platform", "consent"):
        add("android-consent", 0.78, ["README mentions consent/UMP"])
    if _contains(text, "android publisher", "play release", "play store", "publishing tooling"):
        add("android-play-release", 0.90, ["README mentions Play publishing/release"])
    if _contains(text, "device testing", "device qa", "emulator", "instrumentation"):
        add("android-device-qa", 0.88, ["README mentions device/emulator validation"])
    if _contains(text, "aab", "apk"):
        add("android-artifact-build", 0.86, ["README mentions APK/AAB build"])
    if _contains(text, "jetpack compose"):
        add("jetpack-compose", 0.98, ["README mentions Jetpack Compose"], portable=False)
    if _contains(text, "libgdx"):
        add("libgdx", 0.99, ["README mentions libGDX"], portable=False)
    if _contains(text, "godot"):
        add("godot", 0.99, ["README mentions Godot"], portable=False)
    if _contains(text, "flutter"):
        add("flutter", 0.99, ["README mentions Flutter"], portable=False)

    if _contains(text, "visual-asset production", "visual asset production", "sprite atlas", "asset-forge"):
        add("visual-asset-pipeline", 0.97, ["README describes visual asset production"])
    if _contains(text, "sprite sheets", "sprite atlas", "atlas packing", "runtime atlas"):
        add("sprite-atlas-pipeline", 0.95, ["README describes sprite atlas tooling"])
    if _contains(text, "gltf", "glb", "3d quality", "blender export"):
        add("gltf-asset-pipeline", 0.93, ["README describes glTF/GLB asset tooling"])
    if _contains(text, "svg", "vector", "sanitize-svg"):
        add("vector-asset-pipeline", 0.90, ["README describes SVG/vector tooling"])
    if _contains(text, "godot handoff", "godot 4 handoff", "export-godot"):
        add("godot-asset-handoff", 0.94, ["README describes Godot asset handoff"])

    if _contains(text, "multi-agent", "multi-agent", "agent router", "meta-router"):
        add("multi-agent-orchestration", 0.91, ["README mentions multi-agent routing"])
    if _contains(text, "autonomous", "autonomy"):
        add("autonomous-execution", 0.82, ["README describes autonomous execution"])
    if _contains(text, "checkpoint", "resume", "recovery"):
        add("checkpoint-recovery", 0.80, ["README mentions checkpoints/recovery"])
    if _contains(text, "audit log", "audit trail", "audit"):
        add("audit-trail", 0.82, ["README mentions audit records"])
    if _contains(text, "redis", "celery", "queue", "queued workers"):
        add("queued-workers", 0.82, ["README mentions queue/worker infrastructure"])
    if _contains(text, "fastapi"):
        add("fastapi-control-plane", 0.92, ["README mentions FastAPI"], portable=False)
    if _contains(text, "docker compose"):
        add("docker-compose-deployment", 0.90, ["README mentions Docker Compose"])

    if _contains(text, "walk-forward", "walk forward"):
        add("walk-forward-validation", 0.98, ["README mentions walk-forward validation"])
    if _contains(text, "risk engine", "risk-aware"):
        add("independent-risk-engine", 0.93, ["README mentions independent risk engine"])
    if _contains(text, "paper broker", "paper trading"):
        add("paper-broker", 0.95, ["README mentions paper broker"])
    if _contains(text, "backtest", "backtesting"):
        add("backtesting", 0.88, ["README mentions backtesting"])
    if _contains(text, "experiment registry"):
        add("experiment-registry", 0.95, ["README mentions experiment registry"])
    if _contains(text, "monte carlo", "bootstrap robustness"):
        add("robustness-testing", 0.78, ["README mentions Monte Carlo/bootstrap"])

    if any("release" in workflow or "publish" in workflow for workflow in workflows):
        add("release-automation", 0.98, ["release/publish workflow filename"])
    if "docker-compose.yml" in files or "compose.yml" in files or "compose.yaml" in files:
        add("docker-compose-deployment", 0.98, ["Compose file detected"])

    return sorted(caps.values(), key=lambda item: (-item.confidence, item.name))
