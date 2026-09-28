from __future__ import annotations

import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True, slots=True)
class IntegrationPreflight:
    status: str
    starting_sha: str
    final_sha: str
    candidate_commits: tuple[str, ...]
    applied_commits: tuple[str, ...]
    skipped_commits: tuple[str, ...]
    conflicted_commit: str | None = None
    conflict_files: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "status":self.status,
            "starting_sha":self.starting_sha,
            "final_sha":self.final_sha,
            "candidate_commits":list(self.candidate_commits),
            "applied_commits":list(self.applied_commits),
            "skipped_commits":list(self.skipped_commits),
            **(
                {"conflicted_commit":self.conflicted_commit}
                if self.conflicted_commit
                else {}
            ),
            **(
                {"conflict_files":list(self.conflict_files)}
                if self.conflict_files
                else {}
            ),
        }


@dataclass(frozen=True, slots=True)
class PreparedWorktree:
    repository_root: str
    worktree_path: str
    branch: str
    base_ref: str
    created: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "repository_root":self.repository_root,
            "worktree_path":self.worktree_path,
            "branch":self.branch,
            "base_ref":self.base_ref,
            "created":self.created,
        }


class WorktreeRuntimeError(RuntimeError):
    pass


def _git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            ["git", "-C", str(repo), *args],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=check,
        )
    except FileNotFoundError as exc:
        raise WorktreeRuntimeError("git executable is unavailable") from exc
    except subprocess.CalledProcessError as exc:
        message = (exc.stderr or exc.stdout or "git command failed").strip()
        raise WorktreeRuntimeError(message[:2000]) from exc


def validate_repository_root(path: str | os.PathLike[str]) -> Path:
    root = Path(path).expanduser().resolve()
    if not root.is_dir():
        raise WorktreeRuntimeError("repository root does not exist")
    result = _git(root, "rev-parse", "--show-toplevel")
    top = Path(result.stdout.strip()).resolve()
    if top != root:
        raise WorktreeRuntimeError("repository root must be the git top-level directory")
    return root


def prepare_isolated_worktree(
    repository_root: str | os.PathLike[str],
    contract: dict[str, Any],
    *,
    worktree_root: str | os.PathLike[str],
) -> PreparedWorktree:
    root = validate_repository_root(repository_root)
    if str(contract.get("schema_version") or "") != (
        "production-os/git-worktree-isolation/v1"
    ):
        raise WorktreeRuntimeError("unsupported worktree contract schema")
    if str(contract.get("mode") or "") != "git-worktree":
        raise WorktreeRuntimeError("unsupported isolation mode")

    branch = str(contract.get("branch") or "").strip()
    workspace_key = str(contract.get("workspace_key") or "").strip()
    base_ref = str(contract.get("base_ref") or "HEAD").strip() or "HEAD"
    if not branch or not workspace_key:
        raise WorktreeRuntimeError("worktree contract is incomplete")

    base_check = _git(root, "rev-parse", "--verify", f"{base_ref}^{{commit}}")
    base_sha = base_check.stdout.strip()
    if not base_sha:
        raise WorktreeRuntimeError("base ref does not resolve to a commit")

    parent = Path(worktree_root).expanduser().resolve()
    parent.mkdir(parents=True, exist_ok=True)
    target = (parent / workspace_key).resolve()
    if target.parent != parent:
        raise WorktreeRuntimeError("invalid workspace key")

    if target.exists():
        result = _git(target, "rev-parse", "--show-toplevel")
        if Path(result.stdout.strip()).resolve() != target:
            raise WorktreeRuntimeError("existing workspace is not a git worktree")
        branch_result = _git(target, "branch", "--show-current")
        if branch_result.stdout.strip() != branch:
            raise WorktreeRuntimeError("existing worktree branch mismatch")
        return PreparedWorktree(
            repository_root=str(root),
            worktree_path=str(target),
            branch=branch,
            base_ref=base_sha,
            created=False,
        )

    branch_exists = _git(
        root,
        "show-ref",
        "--verify",
        "--quiet",
        f"refs/heads/{branch}",
        check=False,
    ).returncode == 0
    args = ["worktree", "add"]
    if not branch_exists:
        args.extend(["-b", branch])
    args.append(str(target))
    args.append(branch if branch_exists else base_sha)
    _git(root, *args)

    return PreparedWorktree(
        repository_root=str(root),
        worktree_path=str(target),
        branch=branch,
        base_ref=base_sha,
        created=True,
    )


def remove_isolated_worktree(
    repository_root: str | os.PathLike[str],
    worktree_path: str | os.PathLike[str],
    *,
    force: bool = False,
) -> None:
    root = validate_repository_root(repository_root)
    target = Path(worktree_path).expanduser().resolve()
    if not target.exists():
        _git(root, "worktree", "prune")
        return
    args = ["worktree", "remove"]
    if force:
        args.append("--force")
    args.append(str(target))
    _git(root, *args)
    if target.exists():
        shutil.rmtree(target, ignore_errors=True)
    _git(root, "worktree", "prune")



def _validated_commit_candidates(upstream_context: list[dict[str, Any]]) -> list[str]:
    candidates: list[str] = []
    for row in upstream_context:
        if not isinstance(row, dict):
            continue
        commits = row.get("commit_shas")
        if not isinstance(commits, list):
            continue
        for raw in commits:
            commit = str(raw or "").strip().lower()
            if len(commit) not in {40, 64}:
                continue
            if any(char not in "0123456789abcdef" for char in commit):
                continue
            if commit not in candidates:
                candidates.append(commit)
    return candidates


def preintegrate_upstream_commits(
    worktree_path: str | os.PathLike[str],
    upstream_context: list[dict[str, Any]],
) -> IntegrationPreflight:
    target = Path(worktree_path).expanduser().resolve()
    if not target.is_dir():
        raise WorktreeRuntimeError("integration worktree does not exist")

    top = _git(target, "rev-parse", "--show-toplevel").stdout.strip()
    if Path(top).resolve() != target:
        raise WorktreeRuntimeError(
            "integration worktree path must be the git top-level directory"
        )

    starting_sha = _git(target, "rev-parse", "HEAD").stdout.strip()
    candidates = _validated_commit_candidates(upstream_context)
    if not candidates:
        return IntegrationPreflight(
            status="noop",
            starting_sha=starting_sha,
            final_sha=starting_sha,
            candidate_commits=(),
            applied_commits=(),
            skipped_commits=(),
        )

    dirty = _git(target, "status", "--porcelain").stdout.strip()
    if dirty:
        return IntegrationPreflight(
            status="deferred_dirty_workspace",
            starting_sha=starting_sha,
            final_sha=starting_sha,
            candidate_commits=tuple(candidates),
            applied_commits=(),
            skipped_commits=(),
        )

    applied: list[str] = []
    skipped: list[str] = []
    for commit in candidates:
        exists = _git(
            target,
            "cat-file",
            "-e",
            f"{commit}^{{commit}}",
            check=False,
        )
        if exists.returncode != 0:
            _git(target, "reset", "--hard", starting_sha)
            return IntegrationPreflight(
                status="missing_commit",
                starting_sha=starting_sha,
                final_sha=starting_sha,
                candidate_commits=tuple(candidates),
                applied_commits=(),
                skipped_commits=tuple(skipped),
                conflicted_commit=commit,
            )

        ancestor = _git(
            target,
            "merge-base",
            "--is-ancestor",
            commit,
            "HEAD",
            check=False,
        )
        if ancestor.returncode == 0:
            skipped.append(commit)
            continue

        picked = _git(
            target,
            "-c",
            "user.name=Production OS",
            "-c",
            "user.email=production-os@localhost",
            "cherry-pick",
            commit,
            check=False,
        )
        if picked.returncode != 0:
            conflicts = tuple(
                item.strip()
                for item in _git(
                    target,
                    "diff",
                    "--name-only",
                    "--diff-filter=U",
                    check=False,
                ).stdout.splitlines()
                if item.strip()
            )
            _git(target, "cherry-pick", "--abort", check=False)
            _git(target, "reset", "--hard", starting_sha)
            return IntegrationPreflight(
                status="conflict",
                starting_sha=starting_sha,
                final_sha=starting_sha,
                candidate_commits=tuple(candidates),
                applied_commits=(),
                skipped_commits=tuple(skipped),
                conflicted_commit=commit,
                conflict_files=conflicts,
            )
        applied.append(commit)

    final_sha = _git(target, "rev-parse", "HEAD").stdout.strip()
    return IntegrationPreflight(
        status="integrated",
        starting_sha=starting_sha,
        final_sha=final_sha,
        candidate_commits=tuple(candidates),
        applied_commits=tuple(applied),
        skipped_commits=tuple(skipped),
    )



def inspect_worktree_result(
    worktree_path: str | os.PathLike[str],
    *,
    base_sha: str,
    executor_start_sha: str | None = None,
) -> dict[str, Any]:
    target = Path(worktree_path).expanduser().resolve()
    if not target.is_dir():
        raise WorktreeRuntimeError("worktree does not exist")

    top = _git(target, "rev-parse", "--show-toplevel").stdout.strip()
    if Path(top).resolve() != target:
        raise WorktreeRuntimeError(
            "worktree path must be the git top-level directory"
        )

    final_sha = _git(target, "rev-parse", "HEAD").stdout.strip()
    status_lines = tuple(
        line
        for line in _git(
            target,
            "status",
            "--porcelain",
            "--untracked-files=normal",
        ).stdout.splitlines()
        if line
    )

    resolved_base = _git(
        target,
        "rev-parse",
        "--verify",
        f"{base_sha}^{{commit}}",
    ).stdout.strip()
    base_is_ancestor = (
        _git(
            target,
            "merge-base",
            "--is-ancestor",
            resolved_base,
            final_sha,
            check=False,
        ).returncode
        == 0
    )
    commits_since_base: tuple[str, ...] = ()
    changed_files: tuple[str, ...] = ()
    if base_is_ancestor:
        commits_since_base = tuple(
            line.strip()
            for line in _git(
                target,
                "rev-list",
                "--reverse",
                f"{resolved_base}..{final_sha}",
            ).stdout.splitlines()
            if line.strip()
        )
        changed_files = tuple(
            line.strip()
            for line in _git(
                target,
                "diff",
                "--name-only",
                f"{resolved_base}..{final_sha}",
            ).stdout.splitlines()
            if line.strip()
        )

    start_sha = str(executor_start_sha or final_sha).strip()
    commits_since_start: tuple[str, ...] = ()
    if start_sha:
        start_exists = _git(
            target,
            "cat-file",
            "-e",
            f"{start_sha}^{{commit}}",
            check=False,
        ).returncode == 0
        start_ancestor = (
            start_exists
            and _git(
                target,
                "merge-base",
                "--is-ancestor",
                start_sha,
                final_sha,
                check=False,
            ).returncode
            == 0
        )
        if start_ancestor:
            commits_since_start = tuple(
                line.strip()
                for line in _git(
                    target,
                    "rev-list",
                    "--reverse",
                    f"{start_sha}..{final_sha}",
                ).stdout.splitlines()
                if line.strip()
            )

    return {
        "schema_version":"production-os/worktree-result/v1",
        "base_sha":resolved_base,
        "executor_start_sha":start_sha,
        "final_sha":final_sha,
        "clean":not bool(status_lines),
        "status_lines":list(status_lines)[:100],
        "base_is_ancestor":base_is_ancestor,
        "commits_since_base":list(commits_since_base),
        "commits_since_start":list(commits_since_start),
        "changed_files":list(changed_files)[:500],
    }
