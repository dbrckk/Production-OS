"""Deterministic, fail-closed review of pull-request changed paths."""
from __future__ import annotations

from dataclasses import dataclass


_SECURITY_PREFIXES = (
    ".github/workflows/",
    "infra/",
    "deploy/",
    "docker/",
    "scripts/deploy",
    "src/production_os/api_auth.py",
    "src/production_os/control_plane.py",
    "src/production_os/github_client.py",
)
_DATA_PREFIXES = (
    "migrations/",
    "alembic/",
    "schema/",
    "src/production_os/sqlite_backend.py",
    "src/production_os/postgres_backend.py",
)
_RUNTIME_PREFIXES = (
    "src/production_os/remote_worker",
    "src/production_os/workflow_engine.py",
    "src/production_os/managed_projects.py",
)
_SECRET_NAMES = (
    ".env",
    ".env.",
    "credentials",
    "secret",
    "private_key",
    "id_rsa",
)


@dataclass(frozen=True, slots=True)
class DiffReview:
    changed_files: tuple[str, ...]
    sensitive_files: tuple[str, ...]
    categories: tuple[str, ...]
    requires_human_review: bool
    blockers: tuple[str, ...]

    def to_dict(self) -> dict:
        return {
            "changed_files": list(self.changed_files),
            "sensitive_files": list(self.sensitive_files),
            "categories": list(self.categories),
            "requires_human_review": self.requires_human_review,
            "blockers": list(self.blockers),
        }


def _normalized(paths) -> tuple[str, ...]:
    values = []
    for raw in paths or ():
        path = str(raw or "").strip().replace("\\", "/")
        while path.startswith("./"):
            path = path[2:]
        if path and path not in values:
            values.append(path)
    return tuple(sorted(values))


def review_changed_paths(paths) -> DiffReview:
    changed = _normalized(paths)
    sensitive = []
    categories = set()
    blockers = []

    if not changed:
        blockers.append("changed-files-unavailable")

    for path in changed:
        low = path.lower()
        name = low.rsplit("/", 1)[-1]

        if any(low.startswith(prefix.lower()) for prefix in _SECURITY_PREFIXES):
            categories.add("security-or-deployment")
            sensitive.append(path)
        if any(low.startswith(prefix.lower()) for prefix in _DATA_PREFIXES):
            categories.add("data-or-schema")
            sensitive.append(path)
        if any(low.startswith(prefix.lower()) for prefix in _RUNTIME_PREFIXES):
            categories.add("execution-runtime")
            sensitive.append(path)
        if any(token in name for token in _SECRET_NAMES):
            categories.add("credential-surface")
            sensitive.append(path)
            blockers.append("credential-surface-changed")

        if low.endswith((".pem", ".key", ".p12", ".pfx")):
            categories.add("credential-surface")
            sensitive.append(path)
            blockers.append("credential-material-file")

    sensitive = tuple(sorted(set(sensitive)))
    if sensitive:
        blockers.append("sensitive-files-changed")

    requires_human_review = bool(blockers)
    return DiffReview(
        changed_files=changed,
        sensitive_files=sensitive,
        categories=tuple(sorted(categories)),
        requires_human_review=requires_human_review,
        blockers=tuple(sorted(set(blockers))),
    )


def review_pull_request(client, repository: str, pr_number: int) -> DiffReview:
    files = client.list_pull_request_files(repository, pr_number)
    return review_changed_paths(files)
