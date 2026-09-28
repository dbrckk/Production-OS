"""Build safe compensating rollback instructions for a failed merged change."""
from __future__ import annotations

import re


_SHA40 = re.compile(r"^[0-9a-f]{40}$")


def build_rollback_plan(
    *,
    repository: str,
    merge_sha: str,
    failure_summary: str | None = None,
    ci: dict | None = None,
    known_good_sha: str | None = None,
) -> dict:
    repo = str(repository or "").strip()
    parts = repo.split("/")
    if len(parts) != 2 or any(not part for part in parts):
        raise ValueError("repository must be owner/name")

    sha = str(merge_sha or "").strip().lower()
    if not _SHA40.fullmatch(sha):
        raise ValueError("merge_sha must be a full commit sha")

    good_sha = None
    if known_good_sha is not None:
        candidate = str(known_good_sha or "").strip().lower()
        if not _SHA40.fullmatch(candidate):
            raise ValueError("known_good_sha must be a full commit sha")
        if candidate == sha:
            raise ValueError("known_good_sha must differ from merge_sha")
        good_sha = candidate

    summary = str(failure_summary or "").strip()[:4000]
    ci = ci if isinstance(ci, dict) else {}
    ci_bits = [
        str(ci.get(key) or "").strip()[:300]
        for key in ("workflow", "job", "step")
        if str(ci.get(key) or "").strip()
    ]
    excerpt = str(ci.get("log_excerpt") or "").strip()[:6000]

    instruction = [
        f"Create a compensating rollback for merge commit {sha} in {repo}.",
        "Do not reset, force-push, rewrite history, or remove unrelated changes made after that merge.",
        "Identify the exact effects introduced by the merge and revert only those effects.",
        "Preserve later compatible changes whenever possible.",
    ]
    if summary:
        instruction.append("Observed regression: " + summary)
    if ci_bits:
        instruction.append("Failing CI location: " + " / ".join(ci_bits) + ".")
    if excerpt:
        instruction.append("Relevant CI evidence:\n" + excerpt + "\nEnd CI evidence.")
    if good_sha is not None:
        instruction.append(
            "Diagnostic range available: known-good "
            f"{good_sha}, known-bad {sha}. If a deterministic reproduction "
            "command is available, use production-os regression-bisect inside "
            "an isolated clean worktree to locate the first bad commit. "
            "Do not delay an urgent compensating rollback solely to obtain "
            "bisect evidence."
        )
    instruction.extend([
        "Run the smallest relevant tests first, then the full required validation.",
        "Commit the compensating change on a dedicated rollback branch and open a pull request.",
        "Do not merge until all required GitHub Actions and external commit statuses are green.",
    ])

    return {
        "schema_version": "production-os/rollback-plan/v1",
        "repository": repo,
        "merge_sha": sha,
        "strategy": "compensating-pr",
        "history_rewrite_allowed": False,
        "force_push_allowed": False,
        "requires_green_ci": True,
        "diagnostic":(
            {
                "schema_version":"production-os/regression-bisect-request/v1",
                "strategy":"regression-bisect",
                "known_good_sha":good_sha,
                "known_bad_sha":sha,
                "requires_reproduction_command":True,
                "blocking":False,
            }
            if good_sha is not None
            else None
        ),
        "instruction": "\n\n".join(instruction),
    }
