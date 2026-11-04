#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
from urllib.parse import urlsplit


def _required(*names: str) -> tuple[str, ...]:
    values = tuple(str(os.environ.get(name) or "").strip() for name in names)
    missing = [name for name, value in zip(names, values) if not value]
    if missing:
        # Report every absent setting in one failed deployment, never values.
        raise SystemExit(
            "missing required environment variables: " + ", ".join(missing)
        )
    return values


def _auth_payload(
    worker_token: str,
    operator_token: str,
    worker_name: str = "github-actions-worker",
) -> dict:
    def digest(value: str) -> str:
        return hashlib.sha256(value.encode("utf-8")).hexdigest()

    return {
        "tokens": [
            {
                "name": worker_name,
                "role": "worker",
                "sha256": digest(worker_token),
            },
            {
                "name": "production-os-operator",
                "role": "operator",
                "sha256": digest(operator_token),
            },
        ]
    }


# The owner permanently relocated Production-OS to the studycall12 Render account.
# These three manually created controllers share the same Neon database and must
# never restart as concurrent writers after the original account's quota reset.
# Render supplies RENDER_SERVICE_ID at runtime for both Docker and Python.
_RETIRED_RENDER_SERVICE_IDS = frozenset({
    "srv-dancka740ujc73bgdddg",  # production-os1
    "srv-dancjugae00c73earbe0",  # Production-OS
    "srv-dancfm3tqb8s73bek920",  # production-os
})
_PRIMARY_RENDER_SERVICE_ID = "srv-dbj1hiuc6qcc73b7afvg"


def main() -> None:
    service_id = str(os.environ.get("RENDER_SERVICE_ID") or "").strip()
    if service_id in _RETIRED_RENDER_SERVICE_IDS:
        raise SystemExit("retired Render Production-OS service: use studycall12")
    if service_id and service_id != _PRIMARY_RENDER_SERVICE_ID:
        raise SystemExit("unapproved Render service: only studycall12 is authorized")
    if service_id == _PRIMARY_RENDER_SERVICE_ID and (
        str(os.environ.get("PRODUCTION_OS_PRIMARY_WRITER_ENABLED") or "").strip().lower()
        != "true"
    ):
        # Prevent a second controller from activating when secrets are set.
        # Enable only after independently suspending the legacy writer.
        raise SystemExit(
            "primary writer activation blocked: "
            "PRODUCTION_OS_PRIMARY_WRITER_ENABLED must be true after legacy suspension"
        )

    database_url, worker_token, operator_token = _required(
        "DATABASE_URL",
        "PRODUCTION_OS_WORKER_TOKEN",
        "PRODUCTION_OS_OPERATOR_TOKEN",
    )
    # The existing Actions schedule can poll without a GitHub dispatch PAT.
    # Do not reject a valid database + worker/operator configuration merely
    # because the faster, optional immediate wake is unavailable.
    if not str(os.environ.get("GITHUB_TOKEN") or "").strip():
        print(
            "GITHUB_TOKEN is unset: using scheduled Actions worker fallback "
            "(immediate wake disabled)",
            file=sys.stderr,
        )
    worker_name = str(
        os.environ.get("PRODUCTION_OS_WORKER_ID") or "github-actions-worker"
    ).strip()
    if not worker_name:
        raise SystemExit("PRODUCTION_OS_WORKER_ID must not be empty")
    # Duplicate secrets collapse the operator/worker role boundary. Refuse
    # to start rather than choosing an arbitrary role for the same digest.
    if worker_token == operator_token:
        raise SystemExit("worker and operator tokens must be distinct")

    # render.yaml does not configure an already manually created Render service.
    # Missing dispatch routing otherwise yields a healthy API with no worker wake.
    for name, value in (
        ("PRODUCTION_OS_ACTIONS_REPOSITORY", "dbrckk/ai-dev-server"),
        ("PRODUCTION_OS_ACTIONS_WORKFLOW", "production-os-actions-worker.yml"),
        ("PRODUCTION_OS_ACTIONS_REF", "main"),
    ):
        if not str(os.environ.get(name) or "").strip():
            os.environ[name] = value

    # Render has no durable local disk. A hostless PostgreSQL URI may fall
    # back to a Unix socket or PGHOST; an omitted database may select a
    # default database. Neither is the existing persistent Neon store.
    database_url_error = (
        "DATABASE_URL must be a PostgreSQL connection URL "
        "with an explicit host and database"
    )
    try:
        parsed_database_url = urlsplit(database_url)
        database_host = parsed_database_url.hostname
        database_port = parsed_database_url.port
    except ValueError:
        raise SystemExit(database_url_error) from None
    if (
        parsed_database_url.scheme not in ("postgresql", "postgres")
        or not database_host
        or not parsed_database_url.path.lstrip("/")
        or parsed_database_url.fragment
        or database_port == 0
    ):
        raise SystemExit(database_url_error)
    port = str(os.environ.get("PORT") or "8787").strip()
    if not port.isdigit() or not (1 <= int(port) <= 65535):
        raise SystemExit("PORT must be an integer between 1 and 65535")

    runtime_dir = Path(os.environ.get("PRODUCTION_OS_RUNTIME_DIR") or "/tmp/production-os")
    # Reject a symlink before touching the directory: a redirected runtime
    # location must not receive even hashed authentication material.
    if runtime_dir.is_symlink():
        raise SystemExit("PRODUCTION_OS_RUNTIME_DIR must not be a symlink")
    runtime_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
    runtime_dir.chmod(0o700)
    auth_path = runtime_dir / "auth.json"
    payload = json.dumps(
        _auth_payload(worker_token, operator_token, worker_name),
        separators=(",", ":"),
    )
    # Publish the credential hashes through an atomic, owner-only file.
    # Writing directly to auth.json first can follow an existing symlink
    # and expose/truncate another file before chmod has run.
    pending_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=runtime_dir,
            prefix=".auth-",
            suffix=".tmp",
            delete=False,
        ) as pending:
            pending_path = Path(pending.name)
            pending.write(payload)
            pending.flush()
            os.fsync(pending.fileno())
        os.replace(pending_path, auth_path)
    finally:
        if pending_path is not None:
            pending_path.unlink(missing_ok=True)

    argv = [
        "production-os",
        "control-plane",
        "--database-env",
        "DATABASE_URL",
        "--auth-config",
        str(auth_path),
        "--host",
        "0.0.0.0",
        "--port",
        port,
    ]
    os.execvp(argv[0], argv)


if __name__ == "__main__":
    main()
