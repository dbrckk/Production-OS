#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile


def _required(name: str) -> str:
    value = str(os.environ.get(name) or "").strip()
    if not value:
        raise SystemExit(f"missing required environment variable: {name}")
    return value


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


def main() -> None:
    database_url = _required("DATABASE_URL")
    worker_token = _required("PRODUCTION_OS_WORKER_TOKEN")
    worker_name = str(
        os.environ.get("PRODUCTION_OS_WORKER_ID") or "github-actions-worker"
    ).strip()
    if not worker_name:
        raise SystemExit("PRODUCTION_OS_WORKER_ID must not be empty")
    operator_token = _required("PRODUCTION_OS_OPERATOR_TOKEN")
    port = str(os.environ.get("PORT") or "8787").strip()
    if not port.isdigit() or not (1 <= int(port) <= 65535):
        raise SystemExit("PORT must be an integer between 1 and 65535")

    runtime_dir = Path(os.environ.get("PRODUCTION_OS_RUNTIME_DIR") or "/tmp/production-os")
    runtime_dir.mkdir(parents=True, exist_ok=True)
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
        "--database",
        database_url,
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
