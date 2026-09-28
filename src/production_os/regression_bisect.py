from __future__ import annotations

import re
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence


_SHA40 = re.compile(r"^[0-9a-f]{40}$")
BISECT_SCHEMA = "production-os/regression-bisect/v1"


class RegressionBisectError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class RegressionBisectResult:
    repository_root: str
    good_sha: str
    bad_sha: str
    culprit_sha: str
    duration_seconds: float
    test_command: tuple[str, ...]
    output_excerpt: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version":BISECT_SCHEMA,
            "repository_root":self.repository_root,
            "good_sha":self.good_sha,
            "bad_sha":self.bad_sha,
            "culprit_sha":self.culprit_sha,
            "duration_seconds":round(self.duration_seconds, 6),
            "test_command":list(self.test_command),
            "output_excerpt":self.output_excerpt,
        }


def _git(
    root: Path,
    *args: str,
    check: bool = True,
    timeout: float | None = None,
) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            ["git", "-C", str(root), *args],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=check,
            timeout=timeout,
        )
    except FileNotFoundError as exc:
        raise RegressionBisectError("git executable is unavailable") from exc
    except subprocess.TimeoutExpired as exc:
        raise RegressionBisectError("git bisect command timed out") from exc
    except subprocess.CalledProcessError as exc:
        message = (exc.stderr or exc.stdout or "git command failed").strip()
        raise RegressionBisectError(message[-4000:]) from exc


def _validate_sha(value: str, *, field: str) -> str:
    sha = str(value or "").strip().lower()
    if _SHA40.fullmatch(sha) is None:
        raise ValueError(f"{field} must be a full commit sha")
    return sha


def _validate_command(command: Sequence[str]) -> tuple[str, ...]:
    parts = tuple(str(part) for part in command if str(part))
    if not parts:
        raise ValueError("test command is required")
    if len(parts) > 32:
        raise ValueError("test command has too many arguments")
    if any(len(part) > 2000 for part in parts):
        raise ValueError("test command argument is too long")
    return parts


def run_regression_bisect(
    repository_root: str | Path,
    *,
    good_sha: str,
    bad_sha: str,
    test_command: Sequence[str],
    timeout_seconds: float = 900.0,
) -> RegressionBisectResult:
    root = Path(repository_root).expanduser().resolve()
    if not root.is_dir():
        raise RegressionBisectError("repository root does not exist")
    if float(timeout_seconds) <= 0:
        raise ValueError("timeout_seconds must be > 0")

    good = _validate_sha(good_sha, field="good_sha")
    bad = _validate_sha(bad_sha, field="bad_sha")
    if good == bad:
        raise ValueError("good_sha and bad_sha must differ")
    command = _validate_command(test_command)

    top = _git(root, "rev-parse", "--show-toplevel").stdout.strip()
    if Path(top).resolve() != root:
        raise RegressionBisectError(
            "repository root must be the git top-level directory"
        )
    if _git(root, "status", "--porcelain").stdout.strip():
        raise RegressionBisectError(
            "regression bisect requires a clean working tree"
        )
    for sha, field in ((good, "good_sha"), (bad, "bad_sha")):
        verified = _git(
            root,
            "rev-parse",
            "--verify",
            f"{sha}^{{commit}}",
        ).stdout.strip().lower()
        if verified != sha:
            raise RegressionBisectError(f"{field} does not resolve exactly")
    ancestor = _git(
        root,
        "merge-base",
        "--is-ancestor",
        good,
        bad,
        check=False,
    )
    if ancestor.returncode != 0:
        raise RegressionBisectError(
            "good_sha must be an ancestor of bad_sha"
        )

    started = time.monotonic()
    output = ""
    bisect_started = False
    try:
        _git(root, "bisect", "start", bad, good)
        bisect_started = True
        try:
            run = subprocess.run(
                ["git", "-C", str(root), "bisect", "run", *command],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
                timeout=float(timeout_seconds),
            )
        except FileNotFoundError as exc:
            raise RegressionBisectError(
                "git executable is unavailable"
            ) from exc
        except subprocess.TimeoutExpired as exc:
            raise RegressionBisectError(
                "regression bisect timed out"
            ) from exc
        output = ((run.stdout or "") + "\n" + (run.stderr or "")).strip()
        if run.returncode != 0:
            raise RegressionBisectError(
                ("git bisect run failed: " + output)[-4000:]
            )

        culprit = _git(
            root,
            "rev-parse",
            "refs/bisect/bad",
        ).stdout.strip().lower()
        if _SHA40.fullmatch(culprit) is None:
            raise RegressionBisectError(
                "git bisect did not resolve a culprit commit"
            )
        duration = time.monotonic() - started
        return RegressionBisectResult(
            repository_root=str(root),
            good_sha=good,
            bad_sha=bad,
            culprit_sha=culprit,
            duration_seconds=duration,
            test_command=command,
            output_excerpt=output[-8000:],
        )
    finally:
        if bisect_started:
            _git(root, "bisect", "reset", check=False)
