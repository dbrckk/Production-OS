from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .models import ActionCandidate, RepoAssessment


@dataclass(frozen=True, slots=True)
class ScheduledWork:
    repository: str
    task: str
    lane: str
    score: float
    effort: int
    rationale: str
    blockers: tuple[str, ...] = ()

    def to_dict(self) -> dict:
        return {
            "repository": self.repository,
            "task": self.task,
            "lane": self.lane,
            "score": self.score,
            "effort": self.effort,
            "rationale": self.rationale,
            "blockers": list(self.blockers),
        }


def _repo_map(assessments: Iterable[RepoAssessment]) -> dict[str, RepoAssessment]:
    return {a.evidence.full_name: a for a in assessments}


def _blockers(action: ActionCandidate, assessment: RepoAssessment | None) -> tuple[str, ...]:
    if assessment is None:
        return ("missing-assessment",)

    blockers: list[str] = []
    evidence = assessment.evidence
    if evidence.has_ci and (
        str(evidence.latest_ci_status).lower() in {"failure", "failed", "error"}
        or str(evidence.latest_ci_conclusion).lower() in {"failure", "failed", "error"}
    ):
        blockers.append("ci-failing")

    if action.task != "Add an executable automated test baseline" and not evidence.has_tests:
        blockers.append("no-test-baseline")

    return tuple(blockers)


def _schedule_score(action: ActionCandidate, assessment: RepoAssessment | None) -> float:
    maturity = assessment.score.total if assessment else 0
    blocker_bonus = 0.0
    if assessment:
        conclusion = str(assessment.evidence.latest_ci_conclusion).lower()
        if conclusion in {"failure", "failed", "error"}:
            blocker_bonus += 20.0

    release_bonus = action.release_proximity * 2.0
    maturity_gap_bonus = max(0, 70 - maturity) * 0.15
    effort_penalty = max(action.effort - 1, 0) * 2.5
    return round(action.priority + blocker_bonus + release_bonus + maturity_gap_bonus - effort_penalty, 2)


def build_schedule(
    assessments: list[RepoAssessment],
    actions: list[ActionCandidate],
    capacity: int = 3,
) -> dict:
    if capacity < 1:
        raise ValueError("capacity must be >= 1")

    repos = _repo_map(assessments)
    ranked: list[tuple[ActionCandidate, RepoAssessment | None, float, tuple[str, ...]]] = []
    for action in actions:
        assessment = repos.get(action.repository)
        ranked.append((action, assessment, _schedule_score(action, assessment), _blockers(action, assessment)))

    ranked.sort(key=lambda row: (-row[2], row[0].effort, row[0].repository, row[0].task))

    selected_repos: set[str] = set()
    active = 0
    work: list[ScheduledWork] = []

    for action, assessment, score, blockers in ranked:
        if action.repository in selected_repos:
            lane = "NEXT"
        elif active < capacity:
            lane = "NOW" if active == 0 else "PARALLEL"
            active += 1
            selected_repos.add(action.repository)
        elif score >= 35:
            lane = "NEXT"
        elif score >= 20:
            lane = "PAUSE"
        else:
            lane = "IGNORE"

        work.append(
            ScheduledWork(
                repository=action.repository,
                task=action.task,
                lane=lane,
                score=score,
                effort=action.effort,
                rationale=action.rationale,
                blockers=blockers,
            )
        )

    counts = {lane: sum(1 for item in work if item.lane == lane) for lane in ("NOW","PARALLEL","NEXT","PAUSE","IGNORE")}
    return {
        "schema_version": "production-os/schedule/v1",
        "capacity": capacity,
        "counts": counts,
        "work": [item.to_dict() for item in work],
    }
