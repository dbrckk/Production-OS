from __future__ import annotations

from hashlib import sha256
import json
import sqlite3

import pytest

from production_os.dashboard_backups import (
    BackupError,
    backup_readiness,
    create_verified_sqlite_backup,
)
from production_os.sqlite_backend import SQLiteBackend


def test_sqlite_backup_contains_committed_durable_data(tmp_path, monkeypatch):
    db_path = tmp_path / "production.sqlite"
    backup_dir = tmp_path / "backups"
    monkeypatch.setenv("PRODUCTION_OS_BACKUP_DIR", str(backup_dir))
    backend = SQLiteBackend(db_path)
    with backend.transaction() as db:
        db.execute(
            "INSERT INTO schema_meta(key,value) VALUES('backup_probe','durable') "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value"
        )

    manifest = create_verified_sqlite_backup(backend)
    backup_file = backup_dir / f"{manifest['backup_id']}.sqlite"
    with sqlite3.connect(backup_file) as db:
        value = db.execute(
            "SELECT value FROM schema_meta WHERE key='backup_probe'"
        ).fetchone()[0]
        integrity = db.execute("PRAGMA integrity_check").fetchone()[0]

    assert value == "durable"
    assert integrity == "ok"
    assert manifest["verified"] is True


def test_backup_hash_and_size_match_file_bytes(tmp_path, monkeypatch):
    backup_dir = tmp_path / "backups"
    monkeypatch.setenv("PRODUCTION_OS_BACKUP_DIR", str(backup_dir))
    backend = SQLiteBackend(tmp_path / "production.sqlite")

    manifest = create_verified_sqlite_backup(backend)
    payload = (backup_dir / f"{manifest['backup_id']}.sqlite").read_bytes()

    assert manifest["size_bytes"] == len(payload)
    assert manifest["sha256"] == sha256(payload).hexdigest()


def test_manifest_contains_only_safe_metadata(tmp_path, monkeypatch):
    backup_dir = tmp_path / "backups"
    monkeypatch.setenv("PRODUCTION_OS_BACKUP_DIR", str(backup_dir))
    backend = SQLiteBackend(tmp_path / "secret-source.sqlite")

    manifest = create_verified_sqlite_backup(backend)
    on_disk = json.loads(
        (backup_dir / f"{manifest['backup_id']}.json").read_text()
    )
    assert set(on_disk) == {
        "backup_id",
        "backend_kind",
        "created_at",
        "size_bytes",
        "sha256",
        "verified",
    }
    encoded = json.dumps(on_disk).lower()
    for forbidden in ("path", "dsn", "token", "password", "secret-source"):
        assert forbidden not in encoded


def test_missing_backup_directory_configuration_writes_nothing(tmp_path, monkeypatch):
    monkeypatch.delenv("PRODUCTION_OS_BACKUP_DIR", raising=False)
    backend = SQLiteBackend(tmp_path / "production.sqlite")
    readiness = backup_readiness(backend)

    assert readiness["status"] == "unconfigured"
    assert readiness["create_supported"] is False
    with pytest.raises(BackupError, match="not ready"):
        create_verified_sqlite_backup(backend)
    assert not (tmp_path / "backups").exists()


class _FakePostgres:
    pass


_FakePostgres.__name__ = "PostgresBackend"


def test_postgres_readiness_is_truthfully_unsupported(tmp_path, monkeypatch):
    monkeypatch.setenv("PRODUCTION_OS_BACKUP_DIR", str(tmp_path / "backups"))
    readiness = backup_readiness(_FakePostgres())

    assert readiness["backend_kind"] == "postgres"
    assert readiness["status"] == "unsupported"
    assert readiness["create_supported"] is False
    assert readiness["restore_enabled"] is False
    assert readiness["backups"] == []


def test_backup_readiness_does_not_create_configured_directory(tmp_path, monkeypatch):
    backup_dir = tmp_path / "backups"
    monkeypatch.setenv("PRODUCTION_OS_BACKUP_DIR", str(backup_dir))
    backend = SQLiteBackend(tmp_path / "production.sqlite")

    readiness = backup_readiness(backend)

    assert readiness["status"] == "ready"
    assert readiness["create_supported"] is True
    assert not backup_dir.exists()
