from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .github_client import GitHubAPIError, GitHubClient
from .github_change_review import review_changed_paths


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
    ready_for_promotion: bool
    promotion_blockers: tuple[str, ...]
    required_checks_missing: tuple[str, ...]
    sensitive_files: tuple[str, ...]
    change_categories: tuple[str, ...]
    human_review_required: bool
    head_sha: str | None
    validation_sha: str | None

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
            "ready_for_promotion": self.ready_for_promotion,
            "promotion_blockers": list(self.promotion_blockers),
            "required_checks_missing": list(self.required_checks_missing),
            "sensitive_files": list(self.sensitive_files),
            "change_categories": list(self.change_categories),
            "human_review_required": self.human_review_required,
            "head_sha": self.head_sha,
            "validation_sha": self.validation_sha,
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


def _missing_required_checks(
    required: list[str] | None,
    *,
    workflow_runs: list[dict[str, Any]],
    statuses: list[dict[str, Any]],
    check_runs: list[dict[str, Any]],
) -> tuple[str, ...]:
    if required is None:
        return ("required-checks-unknown",)
    if not required:
        return ()
    observed = set()
    for run in workflow_runs:
        if isinstance(run, dict):
            name = str(run.get("name") or "").strip()
            if name:
                observed.add(name)
    for item in statuses:
        if isinstance(item, dict):
            name = str(item.get("context") or "").strip()
            if name:
                observed.add(name)
    for item in check_runs:
        if isinstance(item, dict):
            name = str(item.get("name") or "").strip()
            if name:
                observed.add(name)
    return tuple(name for name in required if name not in observed)


def _promotion_readiness(
    *,
    pr_state: str | None,
    merged: bool,
    draft: bool,
    review_state: str | None,
    ci_state: str | None,
    status_state: str | None,
    required_checks_missing: tuple[str, ...] = (),
    human_review_required: bool = False,
) -> tuple[bool, tuple[str, ...]]:
    blockers = []
    if merged:
        blockers.append("already-merged")
    if pr_state != "open":
        blockers.append("pr-not-open")
    if draft:
        blockers.append("draft")
    if review_state == "changes-requested":
        blockers.append("changes-requested")
    if ci_state != "passed":
        blockers.append("actions-not-passed")
    if status_state not in {None, "passed"}:
        blockers.append("external-statuses-not-passed")
    if required_checks_missing:
        blockers.append("required-checks-missing")
    if human_review_required:
        blockers.append("human-review-required")
    return (not blockers, tuple(blockers))


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
    required_checks_missing: tuple[str, ...] = ()
    sensitive_files: tuple[str, ...] = ()
    change_categories: tuple[str, ...] = ()
    human_review_required = False
    head_sha = None
    validation_sha = None

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
            merge_sha = str(pr.get("merge_commit_sha") or "").strip()
            validation_sha = merge_sha if merged and merge_sha else head_sha
            base = pr.get("base") or {}
            base_ref = (
                str(base.get("ref") or "").strip()
                if isinstance(base, dict)
                else ""
            )

        reviews = client.get_pull_request_reviews(repository, pr_number)
        review_state = _review_state(reviews)

        try:
            changed_paths = client.list_pull_request_files(repository, pr_number)
            change_review = review_changed_paths(changed_paths)
        except GitHubAPIError:
            change_review = review_changed_paths(())
        sensitive_files = change_review.sensitive_files
        change_categories = change_review.categories
        human_review_required = change_review.requires_human_review

        if validation_sha:
            runs = client.get_commit_workflow_runs(repository, validation_sha)
            ci_state = _ci_state(runs)
            statuses = client.get_commit_statuses(repository, validation_sha)
            status_state = _status_state(statuses)
            check_runs = client.get_commit_check_runs(repository, validation_sha)
            required = (
                client.get_branch_required_checks(repository, base_ref)
                if base_ref
                else []
            )
            required_checks_missing = _missing_required_checks(
                required,
                workflow_runs=runs,
                statuses=statuses,
                check_runs=check_runs,
            )

    ready_for_promotion, promotion_blockers = _promotion_readiness(
        pr_state=pr_state,
        merged=merged,
        draft=draft,
        review_state=review_state,
        ci_state=ci_state,
        status_state=status_state,
        required_checks_missing=required_checks_missing,
        human_review_required=human_review_required,
    )

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
        ready_for_promotion=ready_for_promotion,
        promotion_blockers=promotion_blockers,
        required_checks_missing=required_checks_missing,
        sensitive_files=sensitive_files,
        change_categories=change_categories,
        human_review_required=human_review_required,
        head_sha=head_sha,
        validation_sha=validation_sha,
    )


def runtime_decision_from_github(state: GitHubWorkState) -> str:
    if state.merged:
        if state.ci_state == "failed" or state.status_state == "failed":
            return "rollback"
        if state.ci_state == "passed" and state.status_state in {None, "passed"}:
            return "promote"
        return "running"
    if (
        state.ci_state == "failed"
        or state.status_state == "failed"
        or state.review_state == "changes-requested"
    ):
        return "retry"
    if state.pr_state == "closed":
        return "replan"
    return "running"
