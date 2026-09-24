from __future__ import annotations

import re
from datetime import datetime, timezone

_REPOSITORY = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")


class RepositorySnapshotUnavailable(RuntimeError):
    pass


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class RepositorySnapshotter:
    def __init__(self, github, store):
        self.github = github
        self.store = store

    @staticmethod
    def _validate(repository: str) -> str:
        value = str(repository or "").strip()
        if not _REPOSITORY.fullmatch(value):
            raise ValueError("invalid repository")
        owner, name = value.split("/", 1)
        if owner in {".", ".."} or name in {".", ".."}:
            raise ValueError("invalid repository")
        return value

    def refresh(self, repository: str) -> dict:
        repository = self._validate(repository)
        meta = self.github.repository(repository)
        branch = str(meta.get("default_branch") or "")
        if not branch:
            raise RepositorySnapshotUnavailable("default branch unavailable")
        latest = self.github.latest_commit(repository, branch) or {}
        release = self.github.latest_release(repository)
        captured = _now()
        commit_shas = set()
        for execution in self.store.executions_for_repository(repository, limit=500):
            for raw_sha in execution.get("commit_shas") or []:
                sha = str(raw_sha).strip().lower()
                if len(sha) == 40 and all(ch in "0123456789abcdef" for ch in sha):
                    commit_shas.add(sha)
        snapshot = {
            "id": f"{repository}:{captured}",
            "repository": repository,
            "default_branch": branch,
            "production_os_commits": len(commit_shas),
            "github_commits": self.github.default_branch_commit_count(repository, branch),
            "open_issues": None,
            "open_pull_requests": self.github.open_pull_request_count(repository),
            "ci_status": self.github.latest_ci_status(repository, branch),
            "latest_commit_sha": latest.get("sha"),
            "latest_release": release.get("tag_name") if isinstance(release, dict) else None,
            "tests_detected": None, "tests_passing": None, "tests_failing": None,
            "snapshot_json": {"source":"github","repository":repository},
            "captured_at": captured,
        }
        stored = self.store.save_repository_snapshot(snapshot)
        stored["degraded"] = False; stored["fresh"] = True
        return stored

    def get(self, repository: str, *, max_age_seconds: int = 300) -> dict:
        repository = self._validate(repository)
        cached = self.store.latest_repository_snapshot(repository)
        if cached is not None and max_age_seconds > 0:
            try:
                captured = datetime.fromisoformat(str(cached["captured_at"]).replace("Z","+00:00"))
                if (datetime.now(timezone.utc)-captured).total_seconds() <= max_age_seconds:
                    cached["degraded"] = False; cached["fresh"] = True
                    return cached
            except (TypeError, ValueError):
                pass
        try:
            return self.refresh(repository)
        except Exception as exc:
            cached = self.store.latest_repository_snapshot(repository)
            if cached is None:
                raise RepositorySnapshotUnavailable(str(exc)) from exc
            cached["degraded"] = True; cached["fresh"] = False
            return cached
