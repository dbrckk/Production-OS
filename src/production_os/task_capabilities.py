from __future__ import annotations

import re

VISUAL_CAPABILITY = "visual-asset-production"
VISUAL_3D_CAPABILITY = "visual-asset-3d-production"

CODE_CAPABILITY = "code-implementation"
TEST_CAPABILITY = "test-debug"
REVIEW_CAPABILITY = "code-review"
BROWSER_CAPABILITY = "browser-ui-validation"
ASSET_FORGE_REQUEST_SCHEMA = "asset-forge/production-request/v1"
ASSET_FORGE_REPORT_SCHEMA = "asset-forge/production-report/v1"

_VISUAL_PATTERNS = (
    r"\basset(?:s)?\b",
    r"\bsprite(?:s|sheet| sheets)?\b",
    r"\bpixel[ -]?art\b",
    r"\bgraphic(?:s|al)?\b",
    r"\bartwork\b",
    r"\btexture(?:s)?\b",
    r"\bmaterial(?:s)?\b",
    r"\bicon(?:s)?\b",
    r"\billustration(?:s)?\b",
    r"\bvector(?:s)?\b",
    r"\bsvg\b",
    r"\bglb\b",
    r"\bgltf\b",
    r"\b3d\s+(?:asset|model|character|environment|prop)",
    r"\bmesh(?:es)?\b",
    r"\bvisual(?:s| design| quality| polish)?\b",
    r"\bui\s+(?:art|design|graphics|assets|icons)\b",
    r"\bgraphisme(?:s)?\b",
    r"\bgraphique(?:s)?\b",
    r"\bic[oô]ne(?:s)?\b",
    r"\bvecteur(?:s)?\b",
    r"\bvectoriel(?:le|les|s)?\b",
    r"\bmod[eè]le(?:s)?\s+3d\b",
    r"\bpersonnage(?:s)?\s+3d\b",
    r"\benvironnement(?:s)?\s+3d\b",
    r"\bobjet(?:s)?\s+3d\b",
    r"\bmaillage(?:s)?\b",
    r"\bvisuel(?:s|le|les)?\b",
)


def _handoff_text(handoff: dict) -> str:
    fields = [
        handoff.get("task"),
        handoff.get("final_goal"),
        handoff.get("rationale"),
    ]
    acceptance = handoff.get("acceptance_criteria")
    if isinstance(acceptance, list):
        fields.extend(acceptance)
    return " ".join(
        str(value)
        for value in fields
        if isinstance(value, (str, int, float))
    ).lower()


def is_visual_asset_task(handoff: dict) -> bool:
    if not isinstance(handoff, dict):
        return False
    text = _handoff_text(handoff)
    return any(re.search(pattern, text) for pattern in _VISUAL_PATTERNS)


def is_3d_generation_task(handoff: dict) -> bool:
    if not isinstance(handoff, dict):
        return False
    text = _handoff_text(handoff)
    has_3d = bool(
        re.search(r"\b(?:3d|glb|gltf|mesh(?:es)?)\b", text)
    )
    has_generation = bool(
        re.search(
            r"\b(?:create|generate|produce|build|make|design|model|"
            r"cr[eé]er|cr[eé]e|g[eé]n[eé]rer|g[eé]n[eè]re|produire|"
            r"construire|fabriquer|concevoir|mod[eé]liser|mod[eé]lise)\b",
            text,
        )
    )
    return has_3d and has_generation


def inferred_preferred_capabilities(handoff: dict) -> list[str]:
    if not isinstance(handoff, dict):
        return []
    explicit = handoff.get("preferred_capabilities", [])
    explicit_values = {
        str(item).strip()
        for item in explicit
        if isinstance(item, str) and str(item).strip()
    }
    if explicit_values:
        return sorted(explicit_values)

    text = _handoff_text(handoff)
    preferred = set()
    if re.search(r"\b(?:test|tests|pytest|unit|integration|debug|bug|failure|failing|regression|fix)\b", text):
        preferred.add(TEST_CAPABILITY)
    if re.search(r"\b(?:review|diff|audit|security review|code review)\b", text):
        preferred.add(REVIEW_CAPABILITY)
    if re.search(r"\b(?:browser|playwright|selenium|ui test|visual regression|screenshot|frontend)\b", text):
        preferred.add(BROWSER_CAPABILITY)
    if re.search(r"\b(?:implement|implementation|code|feature|refactor|build|develop|fix)\b", text):
        preferred.add(CODE_CAPABILITY)
    if is_visual_asset_task(handoff):
        preferred.add(VISUAL_CAPABILITY)
    return sorted(preferred)


def inferred_required_capabilities(handoff: dict) -> list[str]:
    explicit = handoff.get("required_capabilities", []) if isinstance(handoff, dict) else []
    explicit_values = {
        str(item).strip()
        for item in explicit
        if isinstance(item, str) and str(item).strip()
    }
    if (
        isinstance(handoff, dict)
        and handoff.get("required_capabilities_authoritative") is True
    ):
        return sorted(explicit_values)

    required = set(explicit_values)
    if is_visual_asset_task(handoff):
        required.add(VISUAL_CAPABILITY)
    if is_3d_generation_task(handoff):
        required.add(VISUAL_3D_CAPABILITY)
    return sorted(required)


def asset_forge_tool_contract(handoff: dict) -> dict | None:
    required = set(inferred_required_capabilities(handoff))
    if VISUAL_CAPABILITY not in required:
        return None
    return {
        "request_schema": ASSET_FORGE_REQUEST_SCHEMA,
        "report_schema": ASSET_FORGE_REPORT_SCHEMA,
        "command": "asset-forge fulfill",
        "required_capability": (
            VISUAL_3D_CAPABILITY
            if VISUAL_3D_CAPABILITY in required
            else VISUAL_CAPABILITY
        ),
    }
