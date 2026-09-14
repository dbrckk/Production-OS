from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(slots=True)
class RepoEvidence:
    name: str
    full_name: str
    html_url: str
    default_branch: str = "main"
    archived: bool = False
    fork: bool = False
    private: bool = False
    language: str | None = None
    stars: int = 0
    forks: int = 0
    open_issues: int = 0
    pushed_at: str | None = None
    has_readme: bool = False
    has_tests: bool = False
    has_ci: bool = False
    has_release_workflow: bool = False
    has_manifest: bool = False
    has_license: bool = False
    has_security_policy: bool = False
    has_dependency_automation: bool = False
    has_roadmap: bool = False
    readme_text: str = ""
    detected_files: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class ScoreBreakdown:
    total: int
    documentation: int
    tests: int
    ci: int
    release: int
    build: int
    security: int
    license: int
    activity: int

    def to_dict(self) -> dict[str, int]:
        return asdict(self)


@dataclass(slots=True)
class ActionCandidate:
    repository: str
    task: str
    rationale: str
    acceptance_criteria: list[str]
    evidence: list[str]
    impact: int
    urgency: int
    risk_reduction: int
    release_proximity: int
    effort: int
    priority: float = 0.0

    def compute_priority(self) -> float:
        value = (
            self.impact * 0.35
            + self.urgency * 0.20
            + self.risk_reduction * 0.20
            + self.release_proximity * 0.25
        )
        self.priority = round(value / max(self.effort, 1) * 10, 2)
        return self.priority

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class RepoAssessment:
    evidence: RepoEvidence
    score: ScoreBreakdown
    actions: list[ActionCandidate]
    profile: str = "generic"
    profile_confidence: float = 0.0
    profile_signals: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "evidence": self.evidence.to_dict(),
            "score": self.score.to_dict(),
            "profile": {
                "kind": self.profile,
                "confidence": self.profile_confidence,
                "signals": self.profile_signals,
            },
            "actions": [action.to_dict() for action in self.actions],
        }
