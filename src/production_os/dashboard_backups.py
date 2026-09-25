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


class BackupTempCandidateConflict(BackupError):
    def __init__(self, expected: int, actual: int):
        super().__init__(
            f"backup temp candidate count changed: expected {expected}, actual {actual}"
        )
        self.expected = expected
        self.actual = actual


class BackupRetentionCandidateConflict(BackupError):
    def __init__(
        self,
        expected_count: int,
        actual_count: int,
        *,
        fingerprint_changed: bool,
    ):
        super().__init__("backup retention candidate set changed")
        self.expected_count = expected_count
        self.actual_count = actual_count
        self.fingerprint_changed = fingerprint_changed


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


def _backup_filesystem_capacity(directory: Path | None) -> dict:
    unavailable = {
        "status":"unknown",
        "total_bytes":None,
        "free_bytes":None,
        "available_bytes":None,
        "used_bytes":None,
        "used_percent":None,
        "available_percent":None,
    }
    if directory is None:
        return {
            **unavailable,
            "status":"unconfigured",
        }

    target = directory
    while not target.exists() and target != target.parent:
        target = target.parent
    if not target.exists():
        return unavailable
    try:
        stats = os.statvfs(target)
    except OSError:
        return unavailable

    block_size = int(stats.f_frsize or stats.f_bsize or 0)
    if block_size <= 0:
        return unavailable
    total = max(0, int(stats.f_blocks) * block_size)
    free = max(0, int(stats.f_bfree) * block_size)
    available = max(0, int(stats.f_bavail) * block_size)
    if total <= 0:
        return unavailable
    used = max(0, total - free)
    available_percent = round(available / total * 100, 2)
    used_percent = round(used / total * 100, 2)
    if available_percent < 5:
        status = "critical"
    elif available_percent < 10:
        status = "warning"
    else:
        status = "ok"
    return {
        "status":status,
        "total_bytes":total,
        "free_bytes":free,
        "available_bytes":available,
        "used_bytes":used,
        "used_percent":used_percent,
        "available_percent":available_percent,
    }


def _backup_age_summary(created_values: list[str], *, now: datetime | None = None) -> dict:
    now = now or datetime.now(timezone.utc)
    valid: list[datetime] = []
    invalid = 0
    buckets = {
        "under_24h":0,
        "one_to_seven_days":0,
        "seven_to_thirty_days":0,
        "over_thirty_days":0,
    }
    for value in created_values:
        try:
            parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        except (TypeError, ValueError):
            invalid += 1
            continue
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        parsed = parsed.astimezone(timezone.utc)
        age_seconds = max(0.0, (now - parsed).total_seconds())
        valid.append(parsed)
        if age_seconds < 86400:
            buckets["under_24h"] += 1
        elif age_seconds < 7 * 86400:
            buckets["one_to_seven_days"] += 1
        elif age_seconds < 30 * 86400:
            buckets["seven_to_thirty_days"] += 1
        else:
            buckets["over_thirty_days"] += 1
    return {
        "verified_count":len(created_values),
        "valid_timestamp_count":len(valid),
        "invalid_timestamp_count":invalid,
        "newest_created_at":max(valid).isoformat() if valid else None,
        "oldest_created_at":min(valid).isoformat() if valid else None,
        "buckets":buckets,
    }



BACKUP_RETENTION_DAYS = 30
BACKUP_RETENTION_MIN_KEEP = 3


def _backup_retention_classification(
    verified_backups: list[dict],
    protected_backup_ids: set[str],
    *,
    now: datetime | None = None,
) -> tuple[dict, list[str]]:
    now = now or datetime.now(timezone.utc)
    rows = []
    invalid_timestamp_count = 0
    for item in verified_backups:
        backup_id = str(item.get("backup_id") or "")
        created_at = str(item.get("created_at") or "")
        try:
            parsed = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        except ValueError:
            invalid_timestamp_count += 1
            continue
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        parsed = parsed.astimezone(timezone.utc)
        size = item.get("size_bytes")
        size_bytes = (
            int(size)
            if isinstance(size, int) and not isinstance(size, bool) and size >= 0
            else 0
        )
        rows.append({
            "backup_id":backup_id,
            "created_at":parsed,
            "size_bytes":size_bytes,
        })

    rows.sort(key=lambda item: item["created_at"], reverse=True)
    newest_ids = {
        item["backup_id"]
        for item in rows[:BACKUP_RETENTION_MIN_KEEP]
        if item["backup_id"]
    }
    cutoff_seconds = BACKUP_RETENTION_DAYS * 86400
    candidate_ids: list[str] = []
    candidate_count = 0
    candidate_bytes = 0
    protected_recent = 0
    protected_latest_floor = 0
    protected_restore_history = 0

    for item in rows:
        backup_id = item["backup_id"]
        age_seconds = max(0.0, (now - item["created_at"]).total_seconds())
        if backup_id in protected_backup_ids:
            protected_restore_history += 1
        elif backup_id in newest_ids:
            protected_latest_floor += 1
        elif age_seconds < cutoff_seconds:
            protected_recent += 1
        else:
            candidate_ids.append(backup_id)
            candidate_count += 1
            candidate_bytes += item["size_bytes"]

    candidate_fingerprint = sha256(
        "\n".join(sorted(candidate_ids)).encode("utf-8")
    ).hexdigest()
    preview = {
        "status":"preview",
        "retention_days":BACKUP_RETENTION_DAYS,
        "min_keep_latest":BACKUP_RETENTION_MIN_KEEP,
        "verified_count":len(verified_backups),
        "valid_timestamp_count":len(rows),
        "invalid_timestamp_count":invalid_timestamp_count,
        "candidate_count":candidate_count,
        "candidate_bytes":candidate_bytes,
        "candidate_fingerprint":candidate_fingerprint,
        "protected_count":(
            protected_recent
            + protected_latest_floor
            + protected_restore_history
            + invalid_timestamp_count
        ),
        "protected_reasons":{
            "recent":protected_recent,
            "latest_floor":protected_latest_floor,
            "restore_history":protected_restore_history,
            "invalid_timestamp":invalid_timestamp_count,
        },
        "deletion_enabled":False,
    }
    return preview, candidate_ids


def _backup_retention_preview(
    verified_backups: list[dict],
    protected_backup_ids: set[str],
    *,
    now: datetime | None = None,
) -> dict:
    return _backup_retention_classification(
        verified_backups,
        protected_backup_ids,
        now=now,
    )[0]


def _retention_source_state(directory: Path) -> tuple[list[dict], set[str]]:
    verified_backups: list[dict] = []
    protected_backup_ids: set[str] = set()
    backup_manifest = re.compile(
        r"^(\d{8}T\d{6}Z-[0-9a-f]{12})\.json$"
    )
    activation_receipt = re.compile(
        r"^restore-(\d{8}T\d{6}Z-[0-9a-f]{12})\.activation\.json$"
    )
    for path in directory.iterdir():
        if not path.is_file():
            continue
        if backup_manifest.fullmatch(path.name):
            manifest = _safe_manifest(path)
            if (
                manifest
                and manifest.get("verified") is True
                and manifest.get("backup_id")
                and BACKUP_ID_RE.fullmatch(str(manifest.get("backup_id")))
            ):
                verified_backups.append(manifest)
            continue
        if activation_receipt.fullmatch(path.name):
            receipt = _safe_activation_receipt(path)
            if receipt is not None:
                protected_backup_ids.add(receipt["source_backup_id"])
                protected_backup_ids.add(receipt["rollback_backup_id"])
    return verified_backups, protected_backup_ids


def backup_storage_inventory(backend) -> dict:
    backup_age = _backup_age_summary([])
    retention_preview = _backup_retention_preview([], set())
    zero = {
        "total_size_bytes":0,
        "backup_count":0,
        "backup_bytes":0,
        "restore_candidate_count":0,
        "restore_candidate_bytes":0,
        "activation_receipt_count":0,
        "activation_receipt_bytes":0,
        "temp_file_count":0,
        "temp_file_bytes":0,
        "stale_temp_count":0,
        "stale_temp_bytes":0,
        "unknown_file_count":0,
        "unknown_file_bytes":0,
    }
    if _backend_kind(backend) != "sqlite":
        return {
            "status":"unsupported",
            "backend_kind":"postgres",
            **zero,
            "filesystem":{
                "status":"unsupported",
                "total_bytes":None,
                "free_bytes":None,
                "available_bytes":None,
                "used_bytes":None,
                "used_percent":None,
                "available_percent":None,
            },
            "backup_age":backup_age,
            "retention_preview":retention_preview,
        }
    directory = _configured_dir()
    if directory is None:
        return {
            "status":"unconfigured",
            "backend_kind":"sqlite",
            **zero,
            "filesystem":_backup_filesystem_capacity(None),
            "backup_age":backup_age,
            "retention_preview":retention_preview,
        }
    if not directory.exists():
        return {
            "status":"ready",
            "backend_kind":"sqlite",
            **zero,
            "filesystem":_backup_filesystem_capacity(directory),
            "backup_age":backup_age,
            "retention_preview":retention_preview,
        }
    if not directory.is_dir():
        return {
            "status":"degraded",
            "backend_kind":"sqlite",
            **zero,
            "filesystem":_backup_filesystem_capacity(directory),
            "backup_age":backup_age,
            "retention_preview":retention_preview,
        }

    backup_ids: set[str] = set()
    candidate_ids: set[str] = set()
    metrics = dict(zero)
    verified_backup_created_at: list[str] = []
    verified_backups: list[dict] = []
    protected_backup_ids: set[str] = set()
    backup_sqlite = re.compile(
        r"^(\d{8}T\d{6}Z-[0-9a-f]{12})\.sqlite$"
    )
    backup_manifest = re.compile(
        r"^(\d{8}T\d{6}Z-[0-9a-f]{12})\.json$"
    )
    candidate_sqlite = re.compile(
        r"^restore-(\d{8}T\d{6}Z-[0-9a-f]{12})\.sqlite$"
    )
    candidate_manifest = re.compile(
        r"^restore-(\d{8}T\d{6}Z-[0-9a-f]{12})\.json$"
    )
    activation_receipt = re.compile(
        r"^restore-(\d{8}T\d{6}Z-[0-9a-f]{12})\.activation\.json$"
    )

    try:
        paths = list(directory.iterdir())
    except OSError:
        return {
            "status":"degraded",
            "backend_kind":"sqlite",
            **zero,
            "filesystem":_backup_filesystem_capacity(directory),
            "backup_age":backup_age,
            "retention_preview":retention_preview,
        }

    for path in paths:
        if not path.is_file():
            continue
        try:
            size = int(path.stat().st_size)
        except OSError:
            continue
        size = max(0, size)
        metrics["total_size_bytes"] += size
        name = path.name
        if name.startswith(".") or name.endswith(".tmp"):
            metrics["temp_file_count"] += 1
            metrics["temp_file_bytes"] += size
            try:
                age_seconds = max(
                    0.0,
                    datetime.now(timezone.utc).timestamp()
                    - path.stat().st_mtime,
                )
            except OSError:
                age_seconds = 0.0
            if age_seconds >= 86400:
                metrics["stale_temp_count"] += 1
                metrics["stale_temp_bytes"] += size
            continue
        match = activation_receipt.fullmatch(name)
        if match:
            metrics["activation_receipt_count"] += 1
            metrics["activation_receipt_bytes"] += size
            receipt = _safe_activation_receipt(path)
            if receipt is not None:
                protected_backup_ids.add(receipt["source_backup_id"])
                protected_backup_ids.add(receipt["rollback_backup_id"])
            continue
        match = candidate_sqlite.fullmatch(name) or candidate_manifest.fullmatch(name)
        if match:
            candidate_ids.add(match.group(1))
            metrics["restore_candidate_bytes"] += size
            continue
        sqlite_match = backup_sqlite.fullmatch(name)
        manifest_match = backup_manifest.fullmatch(name)
        match = sqlite_match or manifest_match
        if match:
            backup_ids.add(match.group(1))
            metrics["backup_bytes"] += size
            if manifest_match:
                manifest = _safe_manifest(path)
                if manifest and manifest.get("verified") is True:
                    verified_backup_created_at.append(
                        str(manifest.get("created_at") or "")
                    )
                    verified_backups.append(manifest)
            continue
        metrics["unknown_file_count"] += 1
        metrics["unknown_file_bytes"] += size

    metrics["backup_count"] = len(backup_ids)
    metrics["restore_candidate_count"] = len(candidate_ids)
    return {
        "status":"ready",
        "backend_kind":"sqlite",
        **metrics,
        "filesystem":_backup_filesystem_capacity(directory),
        "backup_age":_backup_age_summary(verified_backup_created_at),
        "retention_preview":_backup_retention_preview(
            verified_backups,
            protected_backup_ids,
        ),
    }


def prune_expired_verified_backups(
    backend,
    *,
    expected_candidate_count: int,
    expected_candidate_fingerprint: str,
) -> dict:
    if isinstance(expected_candidate_count, bool) or not isinstance(
        expected_candidate_count,
        int,
    ) or expected_candidate_count < 0:
        raise ValueError(
            "expected_candidate_count must be a non-negative integer"
        )
    expected_candidate_fingerprint = str(
        expected_candidate_fingerprint or ""
    ).strip().lower()
    if (
        len(expected_candidate_fingerprint) != 64
        or any(
            ch not in "0123456789abcdef"
            for ch in expected_candidate_fingerprint
        )
    ):
        raise ValueError("expected_candidate_fingerprint must be a SHA-256 hex digest")
    if _backend_kind(backend) != "sqlite":
        raise BackupError("backup retention cleanup is unsupported for this backend")
    directory = _configured_dir()
    if directory is None:
        raise BackupError("backup directory is not configured")
    if not directory.is_dir():
        raise BackupError("backup directory is unavailable")

    try:
        verified_backups, protected_backup_ids = _retention_source_state(directory)
    except OSError as exc:
        raise BackupError("backup directory is unavailable") from exc
    preview, candidate_ids = _backup_retention_classification(
        verified_backups,
        protected_backup_ids,
    )
    actual_count = int(preview["candidate_count"])
    actual_fingerprint = str(preview["candidate_fingerprint"])
    if (
        actual_count != expected_candidate_count
        or actual_fingerprint != expected_candidate_fingerprint
    ):
        raise BackupRetentionCandidateConflict(
            expected_candidate_count,
            actual_count,
            fingerprint_changed=(
                actual_fingerprint != expected_candidate_fingerprint
            ),
        )

    deleted_count = 0
    deleted_bytes = 0
    for backup_id in candidate_ids:
        if not BACKUP_ID_RE.fullmatch(backup_id):
            continue
        manifest_path = directory / f"{backup_id}.json"
        backup_path = directory / f"{backup_id}.sqlite"
        manifest = _safe_manifest(manifest_path)
        if (
            manifest is None
            or manifest.get("verified") is not True
            or str(manifest.get("backup_id") or "") != backup_id
        ):
            raise BackupError("backup retention candidate changed during cleanup")
        paths = [path for path in (backup_path, manifest_path) if path.is_file()]
        sizes = []
        for path in paths:
            try:
                sizes.append((path, max(0, int(path.stat().st_size))))
            except OSError as exc:
                raise BackupError("backup retention candidate became unavailable") from exc
        for path, size in sizes:
            try:
                path.unlink()
            except OSError as exc:
                raise BackupError("backup retention deletion failed") from exc
            deleted_bytes += size
        deleted_count += 1

    return {
        "deleted_count":deleted_count,
        "deleted_bytes":deleted_bytes,
        "remaining":backup_storage_inventory(backend),
    }


def prune_stale_backup_temps(
    backend,
    *,
    expected_candidate_count: int,
) -> dict:
    if isinstance(expected_candidate_count, bool) or not isinstance(
        expected_candidate_count,
        int,
    ) or expected_candidate_count < 0:
        raise ValueError(
            "expected_candidate_count must be a non-negative integer"
        )
    inventory = backup_storage_inventory(backend)
    if inventory["backend_kind"] != "sqlite":
        raise BackupError("backup temp cleanup is unsupported for this backend")
    if inventory["status"] == "unconfigured":
        raise BackupError("backup directory is not configured")
    if inventory["status"] != "ready":
        raise BackupError("backup directory is unavailable")

    actual = int(inventory.get("stale_temp_count") or 0)
    if actual != expected_candidate_count:
        raise BackupTempCandidateConflict(expected_candidate_count, actual)

    directory = _configured_dir()
    assert directory is not None
    deleted_count = 0
    deleted_bytes = 0
    now_ts = datetime.now(timezone.utc).timestamp()
    for path in list(directory.iterdir()):
        if not path.is_file():
            continue
        name = path.name
        if not (name.startswith(".") or name.endswith(".tmp")):
            continue
        try:
            stat = path.stat()
        except OSError:
            continue
        age_seconds = max(0.0, now_ts - stat.st_mtime)
        if age_seconds < 86400:
            continue
        size = max(0, int(stat.st_size))
        try:
            path.unlink()
        except FileNotFoundError:
            continue
        deleted_count += 1
        deleted_bytes += size

    return {
        "deleted_count":deleted_count,
        "deleted_bytes":deleted_bytes,
        "remaining":backup_storage_inventory(backend),
    }


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
