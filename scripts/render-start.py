#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import sys


def _required(name: str) -> str:
    value = str(os.environ.get(name) or "").strip()
    if not value:
        raise SystemExit(f"missing required environment variable: {name}")
    return value


def _auth_payload(worker_token: str, operator_token: str) -> dict:
    def digest(value: str) -> str:
        return hashlib.sha256(value.encode("utf-8")).hexdigest()

    return {
        "tokens": [
            {
                "name": "ai-dev-server-worker",
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
    operator_token = _required("PRODUCTION_OS_OPERATOR_TOKEN")
    port = str(os.environ.get("PORT") or "8787").strip()
    if not port.isdigit() or not (1 <= int(port) <= 65535):
        raise SystemExit("PORT must be an integer between 1 and 65535")

    runtime_dir = Path(os.environ.get("PRODUCTION_OS_RUNTIME_DIR") or "/tmp/production-os")
    runtime_dir.mkdir(parents=True, exist_ok=True)
    auth_path = runtime_dir / "auth.json"
    auth_path.write_text(
        json.dumps(_auth_payload(worker_token, operator_token), separators=(",", ":")),
        encoding="utf-8",
    )
    try:
        auth_path.chmod(0o600)
    except OSError:
        pass

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
