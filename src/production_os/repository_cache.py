from __future__ import annotations

import hashlib
import os
import re
import subprocess
import threading
from dataclasses import dataclass
from pathlib import Path

from .filesystem_lock import filesystem_lock


class RepositoryCacheError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class CachedRepository:
    repository: str
    path: str
    remote_url: str
    created: bool
    fetched: bool

    def to_dict(self) -> dict:
        return {
            "repository":self.repository,
            "path":self.path,
            "remote_url":self.remote_url,
            "created":self.created,
            "fetched":self.fetched,
        }


def _validate_repository(repository: str) -> str:
    value = str(repository or "").strip()
    parts = value.split("/")
    allowed = re.compile(r"^[A-Za-z0-9_.-]+$")
    if (
        len(parts) != 2
        or any(
            not part
            or part in {".", ".."}
            or allowed.fullmatch(part) is None
            for part in parts
        )
    ):
        raise RepositoryCacheError("repository must be owner/name")
    return value


def _run_git(
    args: list[str],
    *,
    cwd: Path | None = None,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            ["git", *args],
            cwd=str(cwd) if cwd is not None else None,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=check,
        )
    except FileNotFoundError as exc:
        raise RepositoryCacheError("git executable is unavailable") from exc
    except subprocess.CalledProcessError as exc:
        message = (exc.stderr or exc.stdout or "git command failed").strip()
        raise RepositoryCacheError(message[:2000]) from exc


class RepositoryCache:
    """Local checkout cache used as the parent repository for agent worktrees."""

    def __init__(
        self,
        root: str | os.PathLike[str],
        *,
        github_base_url: str = "https://github.com",
    ):
        self.root = Path(root).expanduser().resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self.github_base_url = str(github_base_url).rstrip("/")
        if self.github_base_url != "https://github.com":
            raise ValueError("github_base_url must be https://github.com")
        self._locks_guard = threading.Lock()
        self._locks: dict[str, threading.Lock] = {}

    def _lock_for(self, repository: str) -> threading.Lock:
        with self._locks_guard:
            return self._locks.setdefault(repository, threading.Lock())

    def _path_for(self, repository: str) -> Path:
        digest = hashlib.sha256(repository.encode("utf-8")).hexdigest()[:12]
        owner, name = repository.split("/", 1)
        safe = f"{owner}-{name}-{digest}"
        path = (self.root / safe).resolve()
        if path.parent != self.root:
            raise RepositoryCacheError("invalid repository cache path")
        return path

    def remote_url(self, repository: str) -> str:
        value = _validate_repository(repository)
        return f"{self.github_base_url}/{value}.git"

    def ensure(self, repository: str) -> CachedRepository:
        value = _validate_repository(repository)
        target = self._path_for(value)
        remote = self.remote_url(value)

        cache_lock = self.root / ".locks" / (
            hashlib.sha256(value.encode("utf-8")).hexdigest() + ".lock"
        )
        with self._lock_for(value), filesystem_lock(cache_lock):
            created = False
            fetched = False
            if not target.exists():
                _run_git([
                    "clone",
                    "--no-checkout",
                    "--origin",
                    "origin",
                    remote,
                    str(target),
                ])
                created = True
            else:
                if not (target / ".git").exists():
                    raise RepositoryCacheError(
                        "repository cache path exists but is not a git checkout"
                    )

            git_lock = target / ".git" / "production-os.lock"
            with filesystem_lock(git_lock):
                actual = _run_git(
                    ["remote", "get-url", "origin"],
                    cwd=target,
                ).stdout.strip()
                if actual != remote:
                    raise RepositoryCacheError(
                        "cached repository origin mismatch"
                    )

                # Fetch every time before worktree preparation so a one-tap
                # launch sees current remote refs. Authentication remains the
                # worker's normal Git credential responsibility.
                _run_git(
                    [
                        "fetch",
                        "--prune",
                        "--no-tags",
                        "origin",
                        "+refs/heads/*:refs/remotes/origin/*",
                    ],
                    cwd=target,
                )
                fetched = True

                # Make origin's default branch addressable as HEAD.
                remote_head_result = _run_git(
                    ["symbolic-ref", "--quiet", "refs/remotes/origin/HEAD"],
                    cwd=target,
                    check=False,
                )
                remote_head = remote_head_result.stdout.strip()
                branch = ""
                if remote_head.startswith("refs/remotes/origin/"):
                    branch = remote_head.removeprefix("refs/remotes/origin/")
                else:
                    local_head = _run_git(
                        ["symbolic-ref", "--quiet", "--short", "HEAD"],
                        cwd=target,
                        check=False,
                    ).stdout.strip()
                    if local_head:
                        branch = local_head
                if branch:
                    remote_ref = f"refs/remotes/origin/{branch}"
                    exists = _run_git(
                        ["show-ref", "--verify", "--quiet", remote_ref],
                        cwd=target,
                        check=False,
                    ).returncode == 0
                    if exists:
                        _run_git(
                            ["checkout", "-B", branch, remote_ref],
                            cwd=target,
                        )

            return CachedRepository(
                repository=value,
                path=str(target),
                remote_url=remote,
                created=created,
                fetched=fetched,
            )
