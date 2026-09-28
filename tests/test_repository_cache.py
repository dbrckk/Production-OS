from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from production_os.repository_cache import RepositoryCache, RepositoryCacheError


def _git(path: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(path), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    return result.stdout.strip()


def _remote_repo(tmp_path: Path) -> tuple[Path, Path]:
    source = tmp_path / "source"
    source.mkdir()
    subprocess.run(["git", "init", str(source)], check=True, stdout=subprocess.PIPE)
    _git(source, "config", "user.email", "test@example.invalid")
    _git(source, "config", "user.name", "Production OS Test")
    (source / "README.md").write_text("one\n", encoding="utf-8")
    _git(source, "add", "README.md")
    _git(source, "commit", "-m", "one")

    remote = tmp_path / "remote.git"
    subprocess.run(
        ["git", "clone", "--bare", str(source), str(remote)],
        check=True,
        stdout=subprocess.PIPE,
    )
    _git(source, "remote", "add", "origin", str(remote))
    return source, remote


def test_repository_cache_clones_fetches_and_updates_remote_refs(tmp_path, monkeypatch):
    source, remote = _remote_repo(tmp_path)
    cache = RepositoryCache(tmp_path / "cache")
    monkeypatch.setattr(cache, "remote_url", lambda _repository: str(remote))

    first = cache.ensure("owner/repo")

    assert first.created is True
    assert first.fetched is True
    checkout = Path(first.path)
    assert (checkout / ".git").is_dir()
    assert (checkout / ".git" / "production-os.lock").is_file()
    assert len(list((tmp_path / "cache" / ".locks").glob("*.lock"))) == 1
    first_sha = _git(checkout, "rev-parse", "refs/remotes/origin/master")

    (source / "README.md").write_text("two\n", encoding="utf-8")
    _git(source, "add", "README.md")
    _git(source, "commit", "-m", "two")
    _git(source, "push", "origin", "master")

    second = cache.ensure("owner/repo")
    second_sha = _git(checkout, "rev-parse", "refs/remotes/origin/master")

    assert second.created is False
    assert second.fetched is True
    assert second.path == first.path
    assert second_sha != first_sha
    assert second_sha == _git(source, "rev-parse", "HEAD")


def test_repository_cache_uses_stable_collision_resistant_path(tmp_path, monkeypatch):
    _, remote = _remote_repo(tmp_path)
    cache = RepositoryCache(tmp_path / "cache")
    monkeypatch.setattr(cache, "remote_url", lambda _repository: str(remote))

    first = cache.ensure("owner/repo")

    assert Path(first.path).parent == (tmp_path / "cache").resolve()
    assert "owner-repo-" in Path(first.path).name


@pytest.mark.parametrize(
    "repository",
    ["", "owner", "../repo", "owner/../repo", "owner/repo/extra", "owner/re po"],
)
def test_repository_cache_rejects_invalid_repository_names(tmp_path, repository):
    cache = RepositoryCache(tmp_path / "cache")
    with pytest.raises(RepositoryCacheError):
        cache.ensure(repository)


def test_repository_cache_rejects_origin_mismatch(tmp_path, monkeypatch):
    _, remote = _remote_repo(tmp_path)
    cache = RepositoryCache(tmp_path / "cache")
    monkeypatch.setattr(cache, "remote_url", lambda _repository: str(remote))
    first = cache.ensure("owner/repo")

    _git(Path(first.path), "remote", "set-url", "origin", str(tmp_path / "other.git"))

    with pytest.raises(RepositoryCacheError, match="origin mismatch"):
        cache.ensure("owner/repo")
