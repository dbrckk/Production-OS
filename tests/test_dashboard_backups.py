from __future__ import annotations

from hashlib import sha256
import json
import sqlite3

import pytest

from production_os.dashboard_backups import (
    BackupError,
    backup_readiness,
    create_verified_sqlite_backup,
    stage_verified_sqlite_restore,
    verify_backup_for_restore,
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


def test_valid_backup_reports_restore_readiness_and_schema(tmp_path, monkeypatch):
    backup_dir = tmp_path / "backups"
    monkeypatch.setenv("PRODUCTION_OS_BACKUP_DIR", str(backup_dir))
    backend = SQLiteBackend(tmp_path / "production.sqlite")
    manifest = create_verified_sqlite_backup(backend)

    result = verify_backup_for_restore(backend, manifest["backup_id"])

    assert result["backup_id"] == manifest["backup_id"]
    assert result["verified"] is True
    assert result["restorable"] is True
    assert result["integrity"] == "ok"
    assert result["schema_version"] == str(backend.SCHEMA_VERSION)
    assert result["restore_enabled"] is False


def test_tampered_backup_file_is_rejected(tmp_path, monkeypatch):
    backup_dir = tmp_path / "backups"
    monkeypatch.setenv("PRODUCTION_OS_BACKUP_DIR", str(backup_dir))
    backend = SQLiteBackend(tmp_path / "production.sqlite")
    manifest = create_verified_sqlite_backup(backend)
    path = backup_dir / f"{manifest['backup_id']}.sqlite"
    path.write_bytes(path.read_bytes() + b"tamper")

    with pytest.raises(BackupError, match="size does not match manifest"):
        verify_backup_for_restore(backend, manifest["backup_id"])


def test_tampered_manifest_is_rejected(tmp_path, monkeypatch):
    backup_dir = tmp_path / "backups"
    monkeypatch.setenv("PRODUCTION_OS_BACKUP_DIR", str(backup_dir))
    backend = SQLiteBackend(tmp_path / "production.sqlite")
    manifest = create_verified_sqlite_backup(backend)
    manifest_path = backup_dir / f"{manifest['backup_id']}.json"
    payload = json.loads(manifest_path.read_text())
    payload["sha256"] = "0" * 64
    manifest_path.write_text(json.dumps(payload))

    with pytest.raises(BackupError, match="hash does not match manifest"):
        verify_backup_for_restore(backend, manifest["backup_id"])


@pytest.mark.parametrize(
    "backup_id",
    [
        "../production.sqlite",
        "..",
        "backup.sqlite",
        "20260924T120000Z-../../bad",
        "20260924T120000Z-ABCDEF123456",
    ],
)
def test_restore_verification_rejects_malformed_or_traversal_ids(
    tmp_path,
    monkeypatch,
    backup_id,
):
    monkeypatch.setenv("PRODUCTION_OS_BACKUP_DIR", str(tmp_path / "backups"))
    backend = SQLiteBackend(tmp_path / "production.sqlite")
    with pytest.raises(BackupError, match="invalid backup id"):
        verify_backup_for_restore(backend, backup_id)


def test_restore_verification_rejects_missing_backup_file(tmp_path, monkeypatch):
    backup_dir = tmp_path / "backups"
    monkeypatch.setenv("PRODUCTION_OS_BACKUP_DIR", str(backup_dir))
    backend = SQLiteBackend(tmp_path / "production.sqlite")
    manifest = create_verified_sqlite_backup(backend)
    (backup_dir / f"{manifest['backup_id']}.sqlite").unlink()

    with pytest.raises(BackupError, match="backup file is missing"):
        verify_backup_for_restore(backend, manifest["backup_id"])


def test_restore_verification_never_changes_live_database(tmp_path, monkeypatch):
    backup_dir = tmp_path / "backups"
    monkeypatch.setenv("PRODUCTION_OS_BACKUP_DIR", str(backup_dir))
    backend = SQLiteBackend(tmp_path / "production.sqlite")
    with backend.transaction() as db:
        db.execute(
            "INSERT INTO schema_meta(key,value) VALUES('live_probe','before') "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value"
        )
    manifest = create_verified_sqlite_backup(backend)
    with backend.transaction() as db:
        db.execute(
            "UPDATE schema_meta SET value='after' WHERE key='live_probe'"
        )

    verify_backup_for_restore(backend, manifest["backup_id"])

    with backend.connect() as db:
        value = db.execute(
            "SELECT value FROM schema_meta WHERE key='live_probe'"
        ).fetchone()["value"]
    assert value == "after"


def test_stage_verified_restore_creates_isolated_candidate(tmp_path, monkeypatch):
    backup_dir = tmp_path / "backups"
    monkeypatch.setenv("PRODUCTION_OS_BACKUP_DIR", str(backup_dir))
    db_path = tmp_path / "production.sqlite"
    backend = SQLiteBackend(db_path)
    with backend.transaction() as db:
        db.execute(
            "INSERT INTO schema_meta(key,value) VALUES('stage_probe','backup-value') "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value"
        )
    manifest = create_verified_sqlite_backup(backend)

    with backend.transaction() as db:
        db.execute(
            "UPDATE schema_meta SET value='live-value' WHERE key='stage_probe'"
        )
    live_before = db_path.read_bytes()

    staged = stage_verified_sqlite_restore(backend, manifest["backup_id"])

    assert staged["source_backup_id"] == manifest["backup_id"]
    assert staged["verified"] is True
    assert staged["integrity"] == "ok"
    assert staged["activation_enabled"] is False
    assert staged["schema_version"] == str(backend.SCHEMA_VERSION)
    assert "path" not in staged
    assert "dsn" not in staged
    assert db_path.read_bytes() == live_before

    candidate = backup_dir / f"restore-{staged['candidate_id']}.sqlite"
    assert candidate.is_file()
    with sqlite3.connect(candidate) as db:
        value = db.execute(
            "SELECT value FROM schema_meta WHERE key='stage_probe'"
        ).fetchone()[0]
        assert value == "backup-value"

    with backend.connect() as db:
        live_value = db.execute(
            "SELECT value FROM schema_meta WHERE key='stage_probe'"
        ).fetchone()["value"]
    assert live_value == "live-value"


def test_stage_restore_rejects_tampered_source_without_candidate(tmp_path, monkeypatch):
    backup_dir = tmp_path / "backups"
    monkeypatch.setenv("PRODUCTION_OS_BACKUP_DIR", str(backup_dir))
    backend = SQLiteBackend(tmp_path / "production.sqlite")
    manifest = create_verified_sqlite_backup(backend)
    source = backup_dir / f"{manifest['backup_id']}.sqlite"
    source.write_bytes(source.read_bytes() + b"tamper")

    with pytest.raises(BackupError):
        stage_verified_sqlite_restore(backend, manifest["backup_id"])

    assert list(backup_dir.glob("restore-*.sqlite")) == []
    assert list(backup_dir.glob("restore-*.json")) == []


def test_stage_restore_manifest_contains_only_safe_metadata(tmp_path, monkeypatch):
    backup_dir = tmp_path / "backups"
    monkeypatch.setenv("PRODUCTION_OS_BACKUP_DIR", str(backup_dir))
    backend = SQLiteBackend(tmp_path / "production.sqlite")
    manifest = create_verified_sqlite_backup(backend)

    staged = stage_verified_sqlite_restore(backend, manifest["backup_id"])
    on_disk = json.loads(
        (backup_dir / f"restore-{staged['candidate_id']}.json").read_text()
    )
    assert set(on_disk) == {
        "candidate_id",
        "source_backup_id",
        "backend_kind",
        "staged_at",
        "size_bytes",
        "sha256",
        "schema_version",
        "integrity",
        "verified",
        "activation_enabled",
    }
    encoded = json.dumps(on_disk).lower()
    for forbidden in ("path", "dsn", "token", "password"):
        assert forbidden not in encoded
