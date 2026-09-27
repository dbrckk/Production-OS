from __future__ import annotations

import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any


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
