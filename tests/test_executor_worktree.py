from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from production_os.executor_worktree import (
    WorktreeRuntimeError,
    prepare_isolated_worktree,
    remove_isolated_worktree,
)
from production_os.worktree_contract import build_worktree_contract


def _git(path: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(path), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    return result.stdout.strip()


def _repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", str(repo)], check=True, stdout=subprocess.PIPE)
    _git(repo, "config", "user.email", "test@example.invalid")
    _git(repo, "config", "user.name", "Production OS Test")
    (repo / "README.md").write_text("base\n", encoding="utf-8")
    _git(repo, "add", "README.md")
    _git(repo, "commit", "-m", "base")
    return repo


def test_prepare_isolated_worktree_creates_attempt_scoped_branch(tmp_path):
    repo = _repo(tmp_path)
    base = _git(repo, "rev-parse", "HEAD")
    contract = build_worktree_contract(
        repository="owner/repo",
        workflow_id="wf-1",
        task_id="implementation-code",
        attempt=1,
        base_ref=base,
    )

    prepared = prepare_isolated_worktree(
        repo,
        contract,
        worktree_root=tmp_path / "worktrees",
    )

    path = Path(prepared.worktree_path)
    assert prepared.created is True
    assert path.is_dir()
    assert _git(path, "branch", "--show-current") == contract["branch"]
    assert _git(path, "rev-parse", "HEAD") == base

    (path / "agent.txt").write_text("isolated\n", encoding="utf-8")
    assert not (repo / "agent.txt").exists()


def test_prepare_isolated_worktree_reuses_matching_existing_workspace(tmp_path):
    repo = _repo(tmp_path)
    contract = build_worktree_contract(
        repository="owner/repo",
        workflow_id="wf-1",
        task_id="implementation-tests",
        attempt=1,
        base_ref="HEAD",
    )
    first = prepare_isolated_worktree(
        repo,
        contract,
        worktree_root=tmp_path / "worktrees",
    )
    second = prepare_isolated_worktree(
        repo,
        contract,
        worktree_root=tmp_path / "worktrees",
    )

    assert first.created is True
    assert second.created is False
    assert second.worktree_path == first.worktree_path


def test_retry_contract_gets_distinct_worktree(tmp_path):
    repo = _repo(tmp_path)
    first_contract = build_worktree_contract(
        repository="owner/repo",
        workflow_id="wf-1",
        task_id="code",
        attempt=1,
    )
    retry_contract = build_worktree_contract(
        repository="owner/repo",
        workflow_id="wf-1",
        task_id="code",
        attempt=2,
    )

    first = prepare_isolated_worktree(
        repo,
        first_contract,
        worktree_root=tmp_path / "worktrees",
    )
    retry = prepare_isolated_worktree(
        repo,
        retry_contract,
        worktree_root=tmp_path / "worktrees",
    )

    assert first.worktree_path != retry.worktree_path
    assert first.branch != retry.branch


def test_remove_isolated_worktree_detaches_and_prunes(tmp_path):
    repo = _repo(tmp_path)
    contract = build_worktree_contract(
        repository="owner/repo",
        workflow_id="wf-1",
        task_id="review",
        attempt=1,
    )
    prepared = prepare_isolated_worktree(
        repo,
        contract,
        worktree_root=tmp_path / "worktrees",
    )

    remove_isolated_worktree(repo, prepared.worktree_path)

    assert not Path(prepared.worktree_path).exists()
    listing = _git(repo, "worktree", "list", "--porcelain")
    assert prepared.worktree_path not in listing


def test_prepare_rejects_non_repository_root(tmp_path):
    folder = tmp_path / "not-repo"
    folder.mkdir()
    contract = {
        "schema_version":"production-os/git-worktree-isolation/v1",
        "mode":"git-worktree",
        "branch":"production-os/test",
        "workspace_key":"test",
        "base_ref":"HEAD",
    }

    with pytest.raises(WorktreeRuntimeError):
        prepare_isolated_worktree(
            folder,
            contract,
            worktree_root=tmp_path / "worktrees",
        )



def test_remote_worker_cli_parses_repository_worktree_configuration():
    from production_os.cli import _parse_args, _repository_root_map

    args = _parse_args([
        "remote-worker-run",
        "--url", "http://example.invalid",
        "--worker-id", "worker-a",
        "--executor-command", "python executor.py",
        "--repository-root", "owner/repo=/srv/repos/repo",
        "--repository-root", "owner/other=/srv/repos/other",
        "--worktree-root", "/srv/worktrees",
    ])

    assert _repository_root_map(args.repository_root) == {
        "owner/repo":"/srv/repos/repo",
        "owner/other":"/srv/repos/other",
    }
    assert args.worktree_root == "/srv/worktrees"


def test_repository_root_mapping_rejects_ambiguous_values():
    from production_os.cli import _repository_root_map

    with pytest.raises(ValueError, match="OWNER/REPO=PATH"):
        _repository_root_map(["missing-path"])
    with pytest.raises(ValueError, match="duplicate repository root mapping"):
        _repository_root_map([
            "owner/repo=/one",
            "owner/repo=/two",
        ])



def test_runner_uses_repository_cache_when_no_explicit_mapping(tmp_path, monkeypatch):
    from types import SimpleNamespace

    from production_os.remote_worker import RemoteJob
    from production_os.remote_worker_runner import RemoteWorkerRunner

    repo = _repo(tmp_path)

    class DummyClient:
        worker_id = "worker-test"

    runner = RemoteWorkerRunner(
        DummyClient(),
        ["true"],
        repository_cache_root=str(tmp_path / "cache"),
        worktree_root=str(tmp_path / "worktrees"),
    )
    monkeypatch.setattr(
        runner.repository_cache,
        "ensure",
        lambda repository: SimpleNamespace(path=str(repo)),
    )
    contract = build_worktree_contract(
        repository="owner/repo",
        workflow_id="wf-cache",
        task_id="implementation-code",
        attempt=1,
    )
    job = RemoteJob(
        "job-cache",
        {
            "payload":{
                "handoff":{
                    "repository":"owner/repo",
                    "isolation":contract,
                },
            },
        },
    )

    prepared = runner._prepare_worktree(job)

    assert prepared is not None
    assert Path(prepared.worktree_path).is_dir()
    assert prepared.branch == contract["branch"]


def test_remote_worker_cli_exposes_repository_cache_root():
    from production_os.cli import _parse_args

    args = _parse_args([
        "remote-worker-run",
        "--url", "http://example.invalid",
        "--worker-id", "worker-a",
        "--executor-command", "python executor.py",
        "--repository-cache-root", "/srv/cache",
        "--worktree-root", "/srv/worktrees",
    ])

    assert args.repository_cache_root == "/srv/cache"
    assert args.worktree_root == "/srv/worktrees"
