from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
import json
import os
import re
from pathlib import Path
import sqlite3
import shutil
from uuid import uuid4

from .database_maintenance_lock import database_server_lock


BACKUP_ID_RE = re.compile(r"^\d{8}T\d{6}Z-[0-9a-f]{12}$")


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


def _safe_activation_receipt(path: Path) -> dict | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError):
        return None
    if not isinstance(data, dict):
        return None
    required = {
        "candidate_id",
        "source_backup_id",
        "rollback_backup_id",
        "activated_at",
        "schema_version",
        "sha256",
    }
    if set(data) != required:
        return None
    candidate_id = str(data.get("candidate_id") or "")
    source_backup_id = str(data.get("source_backup_id") or "")
    rollback_backup_id = str(data.get("rollback_backup_id") or "")
    activated_at = str(data.get("activated_at") or "")
    schema_version = str(data.get("schema_version") or "")
    digest = str(data.get("sha256") or "").lower()
    if (
        not BACKUP_ID_RE.fullmatch(candidate_id)
        or not BACKUP_ID_RE.fullmatch(source_backup_id)
        or not BACKUP_ID_RE.fullmatch(rollback_backup_id)
        or not activated_at
        or not schema_version
        or len(digest) != 64
        or any(ch not in "0123456789abcdef" for ch in digest)
    ):
        return None
    return {
        "candidate_id":candidate_id,
        "source_backup_id":source_backup_id,
        "rollback_backup_id":rollback_backup_id,
        "activated_at":activated_at,
        "schema_version":schema_version,
        "sha256":digest,
    }


def restore_activation_history(
    backend,
    *,
    limit: int = 50,
) -> list[dict]:
    if _backend_kind(backend) != "sqlite":
        return []
    directory = _configured_dir()
    if directory is None or not directory.is_dir():
        return []
    bounded = max(1, min(200, int(limit)))
    rows = []
    for path in directory.glob("restore-*.activation.json"):
        item = _safe_activation_receipt(path)
        if item is not None:
            rows.append(item)
    rows.sort(
        key=lambda item: (
            str(item.get("activated_at") or ""),
            str(item.get("candidate_id") or ""),
        ),
        reverse=True,
    )
    return rows[:bounded]


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
        manifests = []
        if directory.exists():
            if not directory.is_dir():
                raise OSError("backup target is not a directory")
            for path in sorted(directory.glob("*.json"), reverse=True):
                item = _safe_manifest(path)
                if item and item.get("verified") is True:
                    manifests.append(item)
        else:
            parent = directory.parent
            if not parent.exists() or not parent.is_dir() or not os.access(parent, os.W_OK):
                raise OSError("backup parent directory is unavailable")
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


def verify_backup_for_restore(backend, backup_id: str) -> dict:
    backup_id = str(backup_id or "").strip()
    if not BACKUP_ID_RE.fullmatch(backup_id):
        raise BackupError("invalid backup id")

    readiness = backup_readiness(backend)
    if readiness["backend_kind"] != "sqlite":
        raise BackupError("restore verification is unsupported for this backend")
    if not readiness["backup_directory_configured"]:
        raise BackupError("backup directory is not configured")

    directory = _configured_dir()
    assert directory is not None
    manifest_path = directory / f"{backup_id}.json"
    backup_path = directory / f"{backup_id}.sqlite"
    manifest = _safe_manifest(manifest_path)
    if manifest is None:
        raise BackupError("backup manifest is missing or invalid")
    if (
        manifest.get("backup_id") != backup_id
        or manifest.get("backend_kind") != "sqlite"
        or manifest.get("verified") is not True
    ):
        raise BackupError("backup manifest does not match backup")
    if not backup_path.is_file():
        raise BackupError("backup file is missing")

    digest = sha256()
    size = 0
    with backup_path.open("rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            size += len(chunk)
            digest.update(chunk)
    actual_sha = digest.hexdigest()

    expected_size = manifest.get("size_bytes")
    expected_sha = str(manifest.get("sha256") or "")
    if (
        isinstance(expected_size, bool)
        or not isinstance(expected_size, int)
        or expected_size < 0
        or size != expected_size
    ):
        raise BackupError("backup size does not match manifest")
    if actual_sha != expected_sha:
        raise BackupError("backup hash does not match manifest")

    connection = sqlite3.connect(
        f"file:{backup_path.as_posix()}?mode=ro",
        uri=True,
    )
    try:
        integrity_row = connection.execute(
            "PRAGMA integrity_check"
        ).fetchone()
        integrity = integrity_row[0] if integrity_row else None
        if integrity != "ok":
            raise BackupError("backup integrity check failed")
        schema_row = connection.execute(
            "SELECT value FROM schema_meta WHERE key='schema_version'"
        ).fetchone()
        if schema_row is None:
            raise BackupError("backup schema version is unavailable")
        schema_version = str(schema_row[0])
    except sqlite3.DatabaseError as exc:
        raise BackupError("backup database is unreadable") from exc
    finally:
        connection.close()

    return {
        "backup_id":backup_id,
        "backend_kind":"sqlite",
        "verified":True,
        "restorable":True,
        "size_bytes":size,
        "sha256":actual_sha,
        "schema_version":schema_version,
        "integrity":"ok",
        "checked_at":_now(),
        "restore_enabled":False,
    }


def stage_verified_sqlite_restore(backend, backup_id: str) -> dict:
    verified = verify_backup_for_restore(backend, backup_id)
    if verified["backend_kind"] != "sqlite":
        raise BackupError("restore staging is unsupported for this backend")

    directory = _configured_dir()
    if directory is None:
        raise BackupError("backup directory is not configured")
    if not directory.is_dir():
        raise BackupError("backup directory is not ready")

    source_path = directory / f"{backup_id}.sqlite"
    candidate_id = (
        datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        + "-"
        + uuid4().hex[:12]
    )
    temp_path = directory / f".restore-{candidate_id}.sqlite.tmp"
    final_path = directory / f"restore-{candidate_id}.sqlite"
    manifest_path = directory / f"restore-{candidate_id}.json"
    temp_manifest = directory / f".restore-{candidate_id}.json.tmp"

    try:
        source = sqlite3.connect(
            f"file:{source_path.as_posix()}?mode=ro",
            uri=True,
        )
        try:
            destination = sqlite3.connect(temp_path)
            try:
                source.backup(destination)
                integrity_row = destination.execute(
                    "PRAGMA integrity_check"
                ).fetchone()
                integrity = integrity_row[0] if integrity_row else None
                if integrity != "ok":
                    raise BackupError(
                        "staged restore integrity check failed"
                    )
                schema_row = destination.execute(
                    "SELECT value FROM schema_meta "
                    "WHERE key='schema_version'"
                ).fetchone()
                if schema_row is None:
                    raise BackupError(
                        "staged restore schema version is unavailable"
                    )
                schema_version = str(schema_row[0])
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

        staged_at = _now()
        manifest = {
            "candidate_id":candidate_id,
            "source_backup_id":backup_id,
            "backend_kind":"sqlite",
            "staged_at":staged_at,
            "size_bytes":size,
            "sha256":digest.hexdigest(),
            "schema_version":schema_version,
            "integrity":"ok",
            "verified":True,
            "activation_enabled":False,
        }
        temp_manifest.write_text(
            json.dumps(
                manifest,
                sort_keys=True,
                separators=(",", ":"),
            ),
            encoding="utf-8",
        )
        os.replace(temp_path, final_path)
        os.replace(temp_manifest, manifest_path)
        return manifest
    except Exception:
        for path in (
            temp_path,
            temp_manifest,
            final_path,
            manifest_path,
        ):
            try:
                path.unlink()
            except FileNotFoundError:
                pass
        raise


def verify_staged_restore_candidate(backend, candidate_id: str) -> dict:
    candidate_id = str(candidate_id or "").strip()
    if not BACKUP_ID_RE.fullmatch(candidate_id):
        raise BackupError("invalid restore candidate id")
    if _backend_kind(backend) != "sqlite":
        raise BackupError("restore activation is unsupported for this backend")

    directory = _configured_dir()
    if directory is None:
        raise BackupError("backup directory is not configured")
    manifest_path = directory / f"restore-{candidate_id}.json"
    candidate_path = directory / f"restore-{candidate_id}.sqlite"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError) as exc:
        raise BackupError("restore candidate manifest is missing or invalid") from exc
    if not isinstance(manifest, dict):
        raise BackupError("restore candidate manifest is missing or invalid")
    if (
        manifest.get("candidate_id") != candidate_id
        or manifest.get("backend_kind") != "sqlite"
        or manifest.get("verified") is not True
        or manifest.get("activation_enabled") is not False
    ):
        raise BackupError("restore candidate manifest does not match candidate")
    if (
        manifest.get("activation_state") == "activated"
        or manifest.get("activated_at")
    ):
        raise BackupError("restore candidate has already been activated")
    if not candidate_path.is_file():
        raise BackupError("restore candidate file is missing")

    digest = sha256()
    size = 0
    with candidate_path.open("rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            size += len(chunk)
            digest.update(chunk)
    actual_sha = digest.hexdigest()
    if size != manifest.get("size_bytes"):
        raise BackupError("restore candidate size does not match manifest")
    if actual_sha != str(manifest.get("sha256") or ""):
        raise BackupError("restore candidate hash does not match manifest")

    connection = sqlite3.connect(
        f"file:{candidate_path.as_posix()}?mode=ro",
        uri=True,
    )
    try:
        integrity_row = connection.execute("PRAGMA integrity_check").fetchone()
        if not integrity_row or integrity_row[0] != "ok":
            raise BackupError("restore candidate integrity check failed")
        schema_row = connection.execute(
            "SELECT value FROM schema_meta WHERE key='schema_version'"
        ).fetchone()
        if schema_row is None:
            raise BackupError("restore candidate schema version is unavailable")
        schema_version = str(schema_row[0])
    except sqlite3.DatabaseError as exc:
        raise BackupError("restore candidate database is unreadable") from exc
    finally:
        connection.close()

    expected_schema = str(getattr(backend, "SCHEMA_VERSION", ""))
    if schema_version != expected_schema:
        raise BackupError(
            "restore candidate schema version does not match current schema"
        )
    return {
        "candidate_id":candidate_id,
        "source_backup_id":manifest.get("source_backup_id"),
        "backend_kind":"sqlite",
        "verified":True,
        "integrity":"ok",
        "schema_version":schema_version,
        "size_bytes":size,
        "sha256":actual_sha,
        "activation_enabled":False,
    }


def activate_staged_sqlite_restore(
    backend,
    candidate_id: str,
    *,
    confirmation: str,
) -> dict:
    if confirmation != "ACTIVATE_STAGED_RESTORE":
        raise BackupError("exact restore activation confirmation required")
    if _backend_kind(backend) != "sqlite":
        raise BackupError("restore activation is unsupported for this backend")

    candidate = verify_staged_restore_candidate(backend, candidate_id)
    database_path = Path(getattr(backend, "path", ""))
    if not str(database_path):
        raise BackupError("SQLite database path is unavailable")
    directory = _configured_dir()
    if directory is None:
        raise BackupError("backup directory is not configured")
    candidate_path = directory / f"restore-{candidate_id}.sqlite"
    manifest_path = directory / f"restore-{candidate_id}.json"
    receipt_path = directory / f"restore-{candidate_id}.activation.json"

    with database_server_lock(str(database_path)):
        # Revalidate after acquiring the exclusive lock so the activation
        # decision is based on the exact bytes we will install.
        candidate = verify_staged_restore_candidate(backend, candidate_id)
        rollback = create_verified_sqlite_backup(backend)
        rollback_path = directory / f"{rollback['backup_id']}.sqlite"

        temp_target = database_path.with_name(
            f".{database_path.name}.restore-{uuid4().hex}.tmp"
        )
        rollback_temp = database_path.with_name(
            f".{database_path.name}.rollback-{uuid4().hex}.tmp"
        )
        receipt_temp = directory / (
            f".restore-{candidate_id}.activation-{uuid4().hex}.json.tmp"
        )
        manifest_temp = directory / (
            f".restore-{candidate_id}.manifest-{uuid4().hex}.json.tmp"
        )
        sidecars = [
            Path(str(database_path) + "-wal"),
            Path(str(database_path) + "-shm"),
        ]
        replaced = False
        try:
            shutil.copyfile(candidate_path, temp_target)
            with sqlite3.connect(temp_target) as staged:
                row = staged.execute("PRAGMA integrity_check").fetchone()
                if not row or row[0] != "ok":
                    raise BackupError("temporary restore integrity check failed")
            for sidecar in sidecars:
                try:
                    sidecar.unlink()
                except FileNotFoundError:
                    pass
            os.replace(temp_target, database_path)
            replaced = True

            restored = sqlite3.connect(database_path)
            try:
                row = restored.execute("PRAGMA integrity_check").fetchone()
                if not row or row[0] != "ok":
                    raise BackupError("restored database integrity check failed")
                schema_row = restored.execute(
                    "SELECT value FROM schema_meta WHERE key='schema_version'"
                ).fetchone()
                if (
                    schema_row is None
                    or str(schema_row[0]) != candidate["schema_version"]
                ):
                    raise BackupError("restored database schema verification failed")
            finally:
                restored.close()

            activated_at = _now()
            receipt = {
                "candidate_id":candidate_id,
                "source_backup_id":candidate.get("source_backup_id"),
                "rollback_backup_id":rollback["backup_id"],
                "activated_at":activated_at,
                "schema_version":candidate["schema_version"],
                "sha256":candidate["sha256"],
            }
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            if not isinstance(manifest, dict):
                raise BackupError(
                    "restore candidate manifest is missing or invalid"
                )
            manifest.update({
                "activation_state":"activated",
                "activated_at":activated_at,
                "rollback_backup_id":rollback["backup_id"],
            })
            receipt_temp.write_text(
                json.dumps(
                    receipt,
                    sort_keys=True,
                    separators=(",", ":"),
                ),
                encoding="utf-8",
            )
            manifest_temp.write_text(
                json.dumps(
                    manifest,
                    sort_keys=True,
                    separators=(",", ":"),
                ),
                encoding="utf-8",
            )
            os.replace(receipt_temp, receipt_path)
            os.replace(manifest_temp, manifest_path)
        except Exception:
            for path in (
                temp_target,
                receipt_temp,
                manifest_temp,
            ):
                try:
                    path.unlink()
                except FileNotFoundError:
                    pass
            try:
                receipt_path.unlink()
            except FileNotFoundError:
                pass
            if replaced:
                shutil.copyfile(rollback_path, rollback_temp)
                for sidecar in sidecars:
                    try:
                        sidecar.unlink()
                    except FileNotFoundError:
                        pass
                os.replace(rollback_temp, database_path)
                rollback_db = sqlite3.connect(database_path)
                try:
                    rollback_row = rollback_db.execute(
                        "PRAGMA integrity_check"
                    ).fetchone()
                    if not rollback_row or rollback_row[0] != "ok":
                        raise BackupError(
                            "rollback database integrity check failed"
                        )
                finally:
                    rollback_db.close()
            else:
                try:
                    rollback_temp.unlink()
                except FileNotFoundError:
                    pass
            raise

    return {
        **candidate,
        "activated":True,
        "activation_enabled":False,
        "activation_state":"activated",
        "rollback_backup_id":rollback["backup_id"],
        "activated_at":activated_at,
        "receipt_file":receipt_path.name,
    }


def create_verified_sqlite_backup(backend) -> dict:
    readiness = backup_readiness(backend)
    if readiness["backend_kind"] != "sqlite":
        raise BackupError("backup creation is unsupported for this backend")
    if not readiness["create_supported"]:
        raise BackupError("backup directory is not ready")

    directory = _configured_dir()
    assert directory is not None
    directory.mkdir(parents=True, exist_ok=True)
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
        for path in (temp_path, temp_manifest, final_path, manifest_path):
            try:
                path.unlink()
            except FileNotFoundError:
                pass
        raise
