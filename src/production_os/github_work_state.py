from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .github_client import GitHubAPIError, GitHubClient


@dataclass(frozen=True, slots=True)
class GitHubWorkState:
    repository: str
    issue_number: int | None
    pr_number: int | None
    issue_state: str | None
    pr_state: str | None
    merged: bool
    draft: bool
    review_state: str | None
    ci_state: str | None
    status_state: str | None
    head_sha: str | None

    def to_dict(self) -> dict:
        return {
            "repository": self.repository,
            "issue_number": self.issue_number,
            "pr_number": self.pr_number,
            "issue_state": self.issue_state,
            "pr_state": self.pr_state,
            "merged": self.merged,
            "draft": self.draft,
            "review_state": self.review_state,
            "ci_state": self.ci_state,
            "status_state": self.status_state,
            "head_sha": self.head_sha,
        }


def _review_state(reviews: list[dict[str, Any]]) -> str | None:
    if not reviews:
        return None
    states = [str(r.get("state", "")).upper() for r in reviews]
    if "CHANGES_REQUESTED" in states:
        return "changes-requested"
    if "APPROVED" in states:
        return "approved"
    if any(states):
        return "reviewed"
    return None


def _ci_state(runs: list[dict[str, Any]]) -> str | None:
    if not runs:
        return None
    conclusions = [str(r.get("conclusion") or "").lower() for r in runs]
    statuses = [str(r.get("status") or "").lower() for r in runs]
    if any(c in {"failure","cancelled","timed_out","action_required","startup_failure"} for c in conclusions):
        return "failed"
    if any(s in {"queued","in_progress","pending","requested","waiting"} for s in statuses):
        return "running"
    if all(
        str(r.get("status") or "").lower() == "completed"
        and str(r.get("conclusion") or "").lower() == "success"
        for r in runs
    ):
        return "passed"
    return "unknown"


def _status_state(statuses: list[dict[str, Any]]) -> str | None:
    if not statuses:
        return None
    states = [str(item.get("state") or "").lower() for item in statuses if isinstance(item, dict)]
    if any(state in {"failure","error"} for state in states):
        return "failed"
    if any(state in {"pending","expected"} for state in states):
        return "running"
    if states and all(state == "success" for state in states):
        return "passed"
    return "unknown"


def fetch_github_work_state(
    client: GitHubClient,
    repository: str,
    *,
    issue_number: int | None = None,
    pr_number: int | None = None,
) -> GitHubWorkState:
    issue_state = None
    pr_state = None
    merged = False
    draft = False
    review_state = None
    ci_state = None
    status_state = None
    head_sha = None

    if issue_number is not None:
        issue = client.get_issue(repository, issue_number)
        issue_state = str(issue.get("state")) if issue else None

    if pr_number is not None:
        pr = client.get_pull_request(repository, pr_number)
        if pr:
            pr_state = str(pr.get("state")) if pr.get("state") is not None else None
            merged = bool(pr.get("merged") or pr.get("merged_at"))
            draft = bool(pr.get("draft"))
            head = pr.get("head") or {}
            head_sha = head.get("sha") if isinstance(head, dict) else None

        reviews = client.get_pull_request_reviews(repository, pr_number)
        review_state = _review_state(reviews)

        if head_sha:
            runs = client.get_commit_workflow_runs(repository, head_sha)
            ci_state = _ci_state(runs)
            statuses = client.get_commit_statuses(repository, head_sha)
            status_state = _status_state(statuses)

    return GitHubWorkState(
        repository=repository,
        issue_number=issue_number,
        pr_number=pr_number,
        issue_state=issue_state,
        pr_state=pr_state,
        merged=merged,
        draft=draft,
        review_state=review_state,
        ci_state=ci_state,
        status_state=status_state,
        head_sha=head_sha,
    )


def runtime_decision_from_github(state: GitHubWorkState) -> str:
    if state.merged:
        return "promote"
    if (
        state.ci_state == "failed"
        or state.status_state == "failed"
        or state.review_state == "changes-requested"
    ):
        return "retry"
    if state.pr_state == "closed" and not state.merged:
        return "replan"
    return "running"
