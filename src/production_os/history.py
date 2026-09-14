from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from .models import RepoAssessment


@dataclass(frozen=True, slots=True)
class Regression:
    repository: str
    previous_score: int
    current_score: int
    delta: int


def build_snapshot(owner: str, assessments: Iterable[RepoAssessment]) -> dict:
    repos = {}
    for assessment in assessments:
        repos[assessment.evidence.full_name] = {
            "score": assessment.score.total,
            "profile": assessment.profile,
            "evidence": {
                "has_tests": assessment.evidence.has_tests,
                "has_ci": assessment.evidence.has_ci,
                "latest_ci_status": assessment.evidence.latest_ci_status,
                "latest_ci_conclusion": assessment.evidence.latest_ci_conclusion,
                "has_release_workflow": assessment.evidence.has_release_workflow,
                "has_security_policy": assessment.evidence.has_security_policy,
                "has_dependency_automation": assessment.evidence.has_dependency_automation,
            },
        }
    return {
        "schema_version": "production-os/snapshot/v1",
        "owner": owner,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "repositories": repos,
    }


def save_snapshot(snapshot: dict, path: str | Path) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def load_snapshot(path: str | Path) -> dict | None:
    source = Path(path)
    if not source.exists():
        return None
    return json.loads(source.read_text(encoding="utf-8"))


def detect_regressions(previous: dict | None, current: dict, threshold: int = 5) -> list[Regression]:
    if not previous:
        return []
    regressions: list[Regression] = []
    old_repos = previous.get("repositories", {})
    for name, now in current.get("repositories", {}).items():
        before = old_repos.get(name)
        if not before:
            continue
        old_score = int(before.get("score", 0))
        new_score = int(now.get("score", 0))
        delta = new_score - old_score
        if delta <= -abs(threshold):
            regressions.append(Regression(name, old_score, new_score, delta))
    return sorted(regressions, key=lambda item: item.delta)
