from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from typing import Any


_FINGERPRINT_SCHEMA = "production-os/autonomous-action-fingerprint/v1"
_PROJECT_ID_RE = re.compile(r"^controller-[0-9a-f]{32}$")


@dataclass(frozen=True, slots=True)
class AutonomousProjectRequest:
    repository: str
    task: str
    rationale: str
    acceptance_criteria: tuple[str, ...]
    priority: float
    token_budget: int
    agent_preference: str
    cooperative: bool
    action_fingerprint: str


@dataclass(frozen=True, slots=True)
class AutonomousProjectLaunch:
    project_id: str
    created: bool
    project: dict[str, Any]


def _validate_repository(repository: str) -> str:
    value = str(repository or "").strip()
    parts = value.split("/")
    if (
        len(parts) != 2
        or any(
            not part
            or part in {".", ".."}
            or "/" in part
            for part in parts
        )
    ):
        raise ValueError("repository must be owner/name")
    return value


def _normalized_items(values) -> list[str]:
    if values is None:
        return []
    return sorted({
        str(value).strip()
        for value in values
        if str(value).strip()
    })


def canonical_action_fingerprint_payload(
    *,
    repository: str,
    task: str,
    acceptance_criteria,
    trigger_evidence,
    risk_class: str,
) -> dict[str, Any]:
    return {
        "schema_version":_FINGERPRINT_SCHEMA,
        "repository":_validate_repository(repository),
        "task":str(task or "").strip(),
        "acceptance_criteria":_normalized_items(acceptance_criteria),
        "trigger_evidence":_normalized_items(trigger_evidence),
        "risk_class":str(risk_class or "").strip().lower(),
    }


def autonomous_action_fingerprint(
    *,
    repository: str,
    task: str,
    acceptance_criteria,
    trigger_evidence,
    risk_class: str,
    metadata: dict[str, Any] | None = None,
) -> str:
    del metadata
    payload = canonical_action_fingerprint_payload(
        repository=repository,
        task=task,
        acceptance_criteria=acceptance_criteria,
        trigger_evidence=trigger_evidence,
        risk_class=risk_class,
    )
    raw = json.dumps(
        payload,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def autonomous_project_id(
    *,
    repository: str,
    action_fingerprint: str,
) -> str:
    repository = _validate_repository(repository)
    fingerprint = str(action_fingerprint or "").strip()
    raw = (
        "production-os/autonomous-project/v1\0"
        + repository
        + "\0"
        + fingerprint
    ).encode("utf-8")
    project_id = "controller-" + hashlib.sha256(raw).hexdigest()[:32]
    if _PROJECT_ID_RE.fullmatch(project_id) is None:
        raise RuntimeError("autonomous project id generation failed")
    return project_id
