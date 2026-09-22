from __future__ import annotations

import json

import pytest

from production_os.dashboard_github import (
    RepositorySnapshotter,
    RepositorySnapshotUnavailable,
)
from production_os.dashboard_store import DashboardStore
from production_os.sqlite_backend import SQLiteBackend


class FakeGitHub:
    def __init__(self):
        self.fail = False
    def repository(self, repository):
        if self.fail: raise RuntimeError("github unavailable")
        return {"default_branch":"main"}
    def default_branch_commit_count(self, repository, branch):
        if self.fail: raise RuntimeError("github unavailable")
        return 7
    def open_pull_request_count(self, repository):
        return 2
    def latest_release(self, repository):
        return {"tag_name":"v1.0.0"}
    def latest_commit(self, repository, branch):
        return {"sha":"a"*40}
    def latest_ci_status(self, repository, branch):
        return "success"


def test_snapshotter_returns_cached_snapshot_as_degraded_on_github_failure(tmp_path):
    store = DashboardStore(SQLiteBackend(tmp_path / "production.db"))
    github = FakeGitHub()
    snapshotter = RepositorySnapshotter(github, store)
    cached = snapshotter.refresh("dbrckk/example")
    github.fail = True
    result = snapshotter.get("dbrckk/example", max_age_seconds=0)
    assert result["degraded"] is True
    assert result["latest_commit_sha"] == cached["latest_commit_sha"]
    assert result["captured_at"] == cached["captured_at"]


def test_snapshotter_raises_typed_error_without_cache(tmp_path):
    store = DashboardStore(SQLiteBackend(tmp_path / "production.db"))
    github = FakeGitHub(); github.fail = True
    with pytest.raises(RepositorySnapshotUnavailable):
        RepositorySnapshotter(github, store).get("dbrckk/example", max_age_seconds=0)


def test_snapshotter_rejects_invalid_repository(tmp_path):
    store = DashboardStore(SQLiteBackend(tmp_path / "production.db"))
    with pytest.raises(ValueError):
        RepositorySnapshotter(FakeGitHub(), store).refresh("../bad")
