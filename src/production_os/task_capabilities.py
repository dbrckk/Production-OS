from __future__ import annotations

import re

VISUAL_CAPABILITY = "visual-asset-production"

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


def inferred_required_capabilities(handoff: dict) -> list[str]:
    explicit = handoff.get("required_capabilities", []) if isinstance(handoff, dict) else []
    required = {
        str(item).strip()
        for item in explicit
        if isinstance(item, str) and str(item).strip()
    }
    if is_visual_asset_task(handoff):
        required.add(VISUAL_CAPABILITY)
    return sorted(required)
