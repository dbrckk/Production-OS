from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from production_os.regression_bisect import (
    BISECT_SCHEMA,
    RegressionBisectError,
    run_regression_bisect,
)


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    return result.stdout.strip()


def _history(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", str(repo)], check=True, stdout=subprocess.PIPE)
    _git(repo, "config", "user.email", "test@example.invalid")
    _git(repo, "config", "user.name", "Production OS Test")

    script = repo / "bisect_test.py"
    script.write_text(
        """
from pathlib import Path
raise SystemExit(
    0 if Path("state.txt").read_text(encoding="utf-8").strip() == "good" else 1
)
""".strip()
        + "\n",
        encoding="utf-8",
    )
    (repo / "state.txt").write_text("good\n", encoding="utf-8")
    _git(repo, "add", "bisect_test.py", "state.txt")
    _git(repo, "commit", "-m", "good-1")
    good = _git(repo, "rev-parse", "HEAD")

    (repo / "note.txt").write_text("still good\n", encoding="utf-8")
    _git(repo, "add", "note.txt")
    _git(repo, "commit", "-m", "good-2")

    (repo / "state.txt").write_text("bad\n", encoding="utf-8")
    _git(repo, "add", "state.txt")
    _git(repo, "commit", "-m", "introduce regression")
    culprit = _git(repo, "rev-parse", "HEAD")

    (repo / "note.txt").write_text("after regression\n", encoding="utf-8")
    _git(repo, "add", "note.txt")
    _git(repo, "commit", "-m", "later change")
    bad = _git(repo, "rev-parse", "HEAD")
    return repo, good, culprit, bad


def test_regression_bisect_finds_first_bad_commit_and_resets_repo(tmp_path):
    repo, good, culprit, bad = _history(tmp_path)
    original_head = _git(repo, "rev-parse", "HEAD")

    result = run_regression_bisect(
        repo,
        good_sha=good,
        bad_sha=bad,
        test_command=[sys.executable, "bisect_test.py"],
        timeout_seconds=30,
    )

    assert result.culprit_sha == culprit
    assert result.good_sha == good
    assert result.bad_sha == bad
    assert result.to_dict()["schema_version"] == BISECT_SCHEMA
    assert _git(repo, "rev-parse", "HEAD") == original_head
    assert _git(repo, "status", "--porcelain") == ""


def test_regression_bisect_rejects_dirty_worktree(tmp_path):
    repo, good, _culprit, bad = _history(tmp_path)
    (repo / "dirty.txt").write_text("dirty\n", encoding="utf-8")

    with pytest.raises(
        RegressionBisectError,
        match="clean working tree",
    ):
        run_regression_bisect(
            repo,
            good_sha=good,
            bad_sha=bad,
            test_command=[sys.executable, "bisect_test.py"],
        )


def test_regression_bisect_rejects_reversed_ancestry(tmp_path):
    repo, good, _culprit, bad = _history(tmp_path)

    with pytest.raises(
        RegressionBisectError,
        match="good_sha must be an ancestor",
    ):
        run_regression_bisect(
            repo,
            good_sha=bad,
            bad_sha=good,
            test_command=[sys.executable, "bisect_test.py"],
        )


def test_regression_bisect_requires_full_shas(tmp_path):
    repo, good, _culprit, bad = _history(tmp_path)

    with pytest.raises(ValueError, match="full commit sha"):
        run_regression_bisect(
            repo,
            good_sha=good[:8],
            bad_sha=bad,
            test_command=[sys.executable, "bisect_test.py"],
        )



def test_regression_bisect_cli_parses_bounded_runtime_options():
    from production_os.cli import _parse_args

    args = _parse_args([
        "regression-bisect",
        "--repository-root", "/tmp/repo",
        "--good-sha", "a" * 40,
        "--bad-sha", "b" * 40,
        "--test-command", "python -m pytest tests/test_target.py",
        "--timeout-seconds", "120",
    ])

    assert args.repository_root == "/tmp/repo"
    assert args.good_sha == "a" * 40
    assert args.bad_sha == "b" * 40
    assert args.test_command == "python -m pytest tests/test_target.py"
    assert args.timeout_seconds == 120.0
