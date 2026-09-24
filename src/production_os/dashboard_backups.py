from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import sqlite3
from uuid import uuid4


class BackupError(RuntimeError):
    pass


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _backend_kind(backend) -> str:
    name = backend.__class__.__name__.lower()
    return "postgres" if "postgres" in name else "sqlite"


def _configured_dir() -> Path | None:
    raw = str(os.getenv("PRODUCTION_OS_BACKUP_DIR") or "").strip()
    return Path(raw) if raw else None


def _safe_manifest(path: Path) -> dict | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError):
        return None
    allowed = {
        "backup_id",
        "backend_kind",
        "created_at",
        "size_bytes",
        "sha256",
        "verified",
    }
    if not isinstance(data, dict):
        return None
    return {key:data.get(key) for key in allowed if key in data}


def backup_readiness(backend) -> dict:
    kind = _backend_kind(backend)
    directory = _configured_dir()
    if kind == "postgres":
        return {
            "backend_kind":"postgres",
            "status":"unsupported",
            "restore_enabled":False,
            "create_supported":False,
            "backup_directory_configured":directory is not None,
            "message":"PostgreSQL backup creation requires qualified external pg_dump tooling.",
            "backups":[],
        }
    if directory is None:
        return {
            "backend_kind":"sqlite",
            "status":"unconfigured",
            "restore_enabled":False,
            "create_supported":False,
            "backup_directory_configured":False,
            "message":"PRODUCTION_OS_BACKUP_DIR is not configured.",
            "backups":[],
        }
    try:
        directory.mkdir(parents=True, exist_ok=True)
        if not directory.is_dir():
            raise OSError("backup target is not a directory")
        manifests = []
        for path in sorted(directory.glob("*.json"), reverse=True):
            item = _safe_manifest(path)
            if item and item.get("verified") is True:
                manifests.append(item)
        return {
            "backend_kind":"sqlite",
            "status":"ready",
            "restore_enabled":False,
            "create_supported":True,
            "backup_directory_configured":True,
            "message":None,
            "backups":manifests[:100],
        }
    except OSError:
        return {
            "backend_kind":"sqlite",
            "status":"degraded",
            "restore_enabled":False,
            "create_supported":False,
            "backup_directory_configured":True,
            "message":"Configured backup directory is unavailable.",
            "backups":[],
        }


def create_verified_sqlite_backup(backend) -> dict:
    readiness = backup_readiness(backend)
    if readiness["backend_kind"] != "sqlite":
        raise BackupError("backup creation is unsupported for this backend")
    if not readiness["create_supported"]:
        raise BackupError("backup directory is not ready")

    directory = _configured_dir()
    assert directory is not None
    backup_id = (
        datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        + "-"
        + uuid4().hex[:12]
    )
    temp_path = directory / f".{backup_id}.sqlite.tmp"
    final_path = directory / f"{backup_id}.sqlite"
    manifest_path = directory / f"{backup_id}.json"
    temp_manifest = directory / f".{backup_id}.json.tmp"

    try:
        source = backend.connect()
        try:
            destination = sqlite3.connect(temp_path)
            try:
                source.backup(destination)
                row = destination.execute("PRAGMA integrity_check").fetchone()
                integrity = row[0] if row else None
                if integrity != "ok":
                    raise BackupError("backup integrity check failed")
                destination.commit()
            finally:
                destination.close()
        finally:
            source.close()

        digest = sha256()
        size = 0
        with temp_path.open("rb") as handle:
            while True:
                chunk = handle.read(1024 * 1024)
                if not chunk:
                    break
                size += len(chunk)
                digest.update(chunk)

        manifest = {
            "backup_id":backup_id,
            "backend_kind":"sqlite",
            "created_at":_now(),
            "size_bytes":size,
            "sha256":digest.hexdigest(),
            "verified":True,
        }
        temp_manifest.write_text(
            json.dumps(manifest, sort_keys=True, separators=(",", ":")),
            encoding="utf-8",
        )
        os.replace(temp_path, final_path)
        os.replace(temp_manifest, manifest_path)
        return manifest
    except Exception:
        for path in (temp_path, temp_manifest):
            try:
                path.unlink()
            except FileNotFoundError:
                pass
        raise
