"""Deterministic, fail-closed review of pull-request changed paths."""
from __future__ import annotations

from dataclasses import dataclass
import re


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


_HIGH_RISK_ADDITION_PATTERNS = (
    (
        "private-key-material-added",
        "credential-surface",
        re.compile(
            r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----",
            re.IGNORECASE,
        ),
    ),
    (
        "embedded-secret-added",
        "credential-surface",
        re.compile(
            r"\b(?:AWS_SECRET_ACCESS_KEY|GITHUB_TOKEN|API_KEY|SECRET_KEY|"
            r"CLIENT_SECRET|PRIVATE_KEY)\b\s*[:=]\s*['\"]?[^\s'\"]{12,}",
            re.IGNORECASE,
        ),
    ),
    (
        "dangerous-shell-execution-added",
        "dangerous-execution",
        re.compile(
            r"(?:\bos\.system\s*\(|\bsubprocess\."
            r"(?:run|Popen|call|check_call|check_output)\s*\([^\n]*"
            r"shell\s*=\s*True)",
            re.IGNORECASE,
        ),
    ),
    (
        "destructive-sql-added",
        "destructive-data",
        re.compile(
            r"\b(?:DROP\s+(?:TABLE|DATABASE|SCHEMA)|TRUNCATE\s+TABLE)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "tls-verification-disabled",
        "auth-or-transport-bypass",
        re.compile(
            r"\b(?:verify\s*=\s*False|ssl_verify\s*=\s*False|CERT_NONE)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "world-writable-permissions-added",
        "dangerous-execution",
        re.compile(
            r"\bchmod\s+(?:-R\s+)?777\b",
            re.IGNORECASE,
        ),
    ),
)

_BINARY_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico",
    ".pdf", ".zip", ".gz", ".tar", ".tgz", ".mp4", ".mov",
    ".woff", ".woff2", ".ttf", ".otf",
}


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


def _added_patch_lines(patch: str | None) -> tuple[str, ...]:
    if not isinstance(patch, str) or not patch:
        return ()
    lines = []
    for line in patch.splitlines():
        if line.startswith("+++") or not line.startswith("+"):
            continue
        lines.append(line[1:][:4000])
        if len(lines) >= 4000:
            break
    return tuple(lines)


def review_changed_files(files) -> DiffReview:
    details = [
        item for item in (files or [])
        if isinstance(item, dict)
        and str(item.get("filename") or "").strip()
    ]
    base = review_changed_paths(
        [item.get("filename") for item in details]
    )
    sensitive = set(base.sensitive_files)
    categories = set(base.categories)
    blockers = set(base.blockers)

    for item in details:
        filename = str(item.get("filename") or "").strip()
        low = filename.lower()
        patch = item.get("patch")
        changes = max(0, int(item.get("changes") or 0))

        if (
            patch is None
            and changes >= 500
            and not any(low.endswith(ext) for ext in _BINARY_EXTENSIONS)
        ):
            sensitive.add(filename)
            categories.add("unreviewable-large-diff")
            blockers.add("diff-content-unavailable")

        for line in _added_patch_lines(
            patch if isinstance(patch, str) else None
        ):
            for blocker, category, pattern in _HIGH_RISK_ADDITION_PATTERNS:
                if pattern.search(line):
                    sensitive.add(filename)
                    categories.add(category)
                    blockers.add(blocker)

    if sensitive:
        blockers.add("sensitive-files-changed")

    return DiffReview(
        changed_files=base.changed_files,
        sensitive_files=tuple(sorted(sensitive)),
        categories=tuple(sorted(categories)),
        requires_human_review=bool(blockers),
        blockers=tuple(sorted(blockers)),
    )


def review_pull_request(client, repository: str, pr_number: int) -> DiffReview:
    detailed = getattr(client, "get_pull_request_file_details", None)
    if callable(detailed):
        details = detailed(
            repository,
            pr_number,
        )
        return review_changed_files(details)
    files = client.list_pull_request_files(repository, pr_number)
    return review_changed_paths(files)
