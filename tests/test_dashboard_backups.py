from __future__ import annotations

from datetime import datetime, timedelta, timezone
from hashlib import sha256
import os
import time
import json
import sqlite3

import pytest

from production_os.dashboard_backups import (
    BackupError,
    backup_readiness,
    backup_storage_inventory,
    BackupRetentionCandidateConflict,
    BackupTempCandidateConflict,
    prune_expired_verified_backups,
    prune_stale_backup_temps,
    activate_staged_sqlite_restore,
    create_verified_sqlite_backup,
    restore_activation_history,
    stage_verified_sqlite_restore,
    verify_backup_for_restore,
    verify_staged_restore_candidate,
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


def test_offline_restore_activation_replaces_live_state_and_creates_rollback(
    tmp_path,
    monkeypatch,
):
    backup_dir = tmp_path / "backups"
    monkeypatch.setenv("PRODUCTION_OS_BACKUP_DIR", str(backup_dir))
    db_path = tmp_path / "production.sqlite"
    backend = SQLiteBackend(db_path)
    with backend.transaction() as db:
        db.execute(
            "INSERT INTO schema_meta(key,value) VALUES('activate_probe','backup-state') "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value"
        )
    backup = create_verified_sqlite_backup(backend)
    staged = stage_verified_sqlite_restore(backend, backup["backup_id"])

    with backend.transaction() as db:
        db.execute(
            "UPDATE schema_meta SET value='live-state' WHERE key='activate_probe'"
        )

    result = activate_staged_sqlite_restore(
        backend,
        staged["candidate_id"],
        confirmation="ACTIVATE_STAGED_RESTORE",
    )
    assert result["activated"] is True
    assert result["activation_enabled"] is False
    assert result["activation_state"] == "activated"
    assert result["rollback_backup_id"]
    assert result["receipt_file"] == (
        f"restore-{staged['candidate_id']}.activation.json"
    )

    with SQLiteBackend(db_path).connect() as db:
        value = db.execute(
            "SELECT value FROM schema_meta WHERE key='activate_probe'"
        ).fetchone()["value"]
    assert value == "backup-state"

    rollback_path = backup_dir / f"{result['rollback_backup_id']}.sqlite"
    assert rollback_path.is_file()
    with sqlite3.connect(rollback_path) as db:
        rollback_value = db.execute(
            "SELECT value FROM schema_meta WHERE key='activate_probe'"
        ).fetchone()[0]
    assert rollback_value == "live-state"


def test_restore_activation_wrong_confirmation_changes_nothing(tmp_path, monkeypatch):
    backup_dir = tmp_path / "backups"
    monkeypatch.setenv("PRODUCTION_OS_BACKUP_DIR", str(backup_dir))
    db_path = tmp_path / "production.sqlite"
    backend = SQLiteBackend(db_path)
    backup = create_verified_sqlite_backup(backend)
    staged = stage_verified_sqlite_restore(backend, backup["backup_id"])
    before = db_path.read_bytes()

    with pytest.raises(BackupError, match="confirmation"):
        activate_staged_sqlite_restore(
            backend,
            staged["candidate_id"],
            confirmation="wrong",
        )

    assert db_path.read_bytes() == before


def test_restore_activation_rejects_tampered_candidate(tmp_path, monkeypatch):
    backup_dir = tmp_path / "backups"
    monkeypatch.setenv("PRODUCTION_OS_BACKUP_DIR", str(backup_dir))
    backend = SQLiteBackend(tmp_path / "production.sqlite")
    backup = create_verified_sqlite_backup(backend)
    staged = stage_verified_sqlite_restore(backend, backup["backup_id"])
    candidate = backup_dir / f"restore-{staged['candidate_id']}.sqlite"
    candidate.write_bytes(candidate.read_bytes() + b"tamper")

    with pytest.raises(BackupError):
        activate_staged_sqlite_restore(
            backend,
            staged["candidate_id"],
            confirmation="ACTIVATE_STAGED_RESTORE",
        )


def test_restore_activation_rejects_schema_mismatch(tmp_path, monkeypatch):
    backup_dir = tmp_path / "backups"
    monkeypatch.setenv("PRODUCTION_OS_BACKUP_DIR", str(backup_dir))
    backend = SQLiteBackend(tmp_path / "production.sqlite")
    backup = create_verified_sqlite_backup(backend)
    staged = stage_verified_sqlite_restore(backend, backup["backup_id"])
    candidate = backup_dir / f"restore-{staged['candidate_id']}.sqlite"
    with sqlite3.connect(candidate) as db:
        db.execute(
            "UPDATE schema_meta SET value='999' WHERE key='schema_version'"
        )
        db.commit()
    payload = candidate.read_bytes()
    manifest_path = backup_dir / f"restore-{staged['candidate_id']}.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["size_bytes"] = len(payload)
    manifest["sha256"] = sha256(payload).hexdigest()
    manifest_path.write_text(json.dumps(manifest))

    with pytest.raises(BackupError, match="schema version"):
        verify_staged_restore_candidate(backend, staged["candidate_id"])


def test_restore_activation_rolls_back_if_post_replace_verification_fails(
    tmp_path,
    monkeypatch,
):
    backup_dir = tmp_path / "backups"
    monkeypatch.setenv("PRODUCTION_OS_BACKUP_DIR", str(backup_dir))
    db_path = tmp_path / "production.sqlite"
    backend = SQLiteBackend(db_path)
    with backend.transaction() as db:
        db.execute(
            "INSERT INTO schema_meta(key,value) VALUES('rollback_probe','backup-state') "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value"
        )
    backup = create_verified_sqlite_backup(backend)
    staged = stage_verified_sqlite_restore(backend, backup["backup_id"])

    with backend.transaction() as db:
        db.execute(
            "UPDATE schema_meta SET value='live-state' WHERE key='rollback_probe'"
        )

    import production_os.dashboard_backups as backups_module

    real_connect = backups_module.sqlite3.connect
    live_verification_failed = {"done": False}

    def failing_connect(target, *args, **kwargs):
        if (
            not live_verification_failed["done"]
            and str(target) == str(db_path)
        ):
            live_verification_failed["done"] = True
            raise sqlite3.DatabaseError("simulated post-replace failure")
        return real_connect(target, *args, **kwargs)

    monkeypatch.setattr(
        backups_module.sqlite3,
        "connect",
        failing_connect,
    )

    with pytest.raises(sqlite3.DatabaseError, match="simulated"):
        activate_staged_sqlite_restore(
            backend,
            staged["candidate_id"],
            confirmation="ACTIVATE_STAGED_RESTORE",
        )

    with real_connect(db_path) as db:
        value = db.execute(
            "SELECT value FROM schema_meta WHERE key='rollback_probe'"
        ).fetchone()[0]
        integrity = db.execute("PRAGMA integrity_check").fetchone()[0]
    assert value == "live-state"
    assert integrity == "ok"


def test_successful_restore_candidate_cannot_be_replayed(tmp_path, monkeypatch):
    backup_dir = tmp_path / "backups"
    monkeypatch.setenv("PRODUCTION_OS_BACKUP_DIR", str(backup_dir))
    backend = SQLiteBackend(tmp_path / "production.sqlite")
    backup = create_verified_sqlite_backup(backend)
    staged = stage_verified_sqlite_restore(backend, backup["backup_id"])

    activate_staged_sqlite_restore(
        backend,
        staged["candidate_id"],
        confirmation="ACTIVATE_STAGED_RESTORE",
    )

    with pytest.raises(BackupError, match="already been activated"):
        activate_staged_sqlite_restore(
            backend,
            staged["candidate_id"],
            confirmation="ACTIVATE_STAGED_RESTORE",
        )


def test_restore_activation_receipt_contains_only_safe_structured_fields(
    tmp_path,
    monkeypatch,
):
    backup_dir = tmp_path / "backups"
    monkeypatch.setenv("PRODUCTION_OS_BACKUP_DIR", str(backup_dir))
    backend = SQLiteBackend(tmp_path / "production.sqlite")
    backup = create_verified_sqlite_backup(backend)
    staged = stage_verified_sqlite_restore(backend, backup["backup_id"])

    result = activate_staged_sqlite_restore(
        backend,
        staged["candidate_id"],
        confirmation="ACTIVATE_STAGED_RESTORE",
    )
    receipt = json.loads(
        (backup_dir / result["receipt_file"]).read_text(encoding="utf-8")
    )

    assert set(receipt) == {
        "candidate_id",
        "source_backup_id",
        "rollback_backup_id",
        "activated_at",
        "schema_version",
        "sha256",
    }
    assert receipt["candidate_id"] == staged["candidate_id"]
    assert receipt["rollback_backup_id"] == result["rollback_backup_id"]
    encoded = json.dumps(receipt).lower()
    for forbidden in (
        "token",
        "password",
        "secret",
        "authorization",
        "path",
        "dsn",
    ):
        assert forbidden not in encoded


def test_successful_activation_marks_candidate_manifest_consumed(
    tmp_path,
    monkeypatch,
):
    backup_dir = tmp_path / "backups"
    monkeypatch.setenv("PRODUCTION_OS_BACKUP_DIR", str(backup_dir))
    backend = SQLiteBackend(tmp_path / "production.sqlite")
    backup = create_verified_sqlite_backup(backend)
    staged = stage_verified_sqlite_restore(backend, backup["backup_id"])

    result = activate_staged_sqlite_restore(
        backend,
        staged["candidate_id"],
        confirmation="ACTIVATE_STAGED_RESTORE",
    )
    manifest = json.loads(
        (
            backup_dir
            / f"restore-{staged['candidate_id']}.json"
        ).read_text(encoding="utf-8")
    )

    assert manifest["activation_state"] == "activated"
    assert manifest["activated_at"] == result["activated_at"]
    assert manifest["rollback_backup_id"] == result["rollback_backup_id"]


def test_failed_activation_with_rollback_does_not_consume_candidate(
    tmp_path,
    monkeypatch,
):
    backup_dir = tmp_path / "backups"
    monkeypatch.setenv("PRODUCTION_OS_BACKUP_DIR", str(backup_dir))
    db_path = tmp_path / "production.sqlite"
    backend = SQLiteBackend(db_path)
    backup = create_verified_sqlite_backup(backend)
    staged = stage_verified_sqlite_restore(backend, backup["backup_id"])

    import production_os.dashboard_backups as backups_module

    real_connect = backups_module.sqlite3.connect
    failed = {"done":False}

    def failing_connect(target, *args, **kwargs):
        if not failed["done"] and str(target) == str(db_path):
            failed["done"] = True
            raise sqlite3.DatabaseError("simulated restore verification failure")
        return real_connect(target, *args, **kwargs)

    monkeypatch.setattr(backups_module.sqlite3, "connect", failing_connect)
    with pytest.raises(sqlite3.DatabaseError, match="simulated"):
        activate_staged_sqlite_restore(
            backend,
            staged["candidate_id"],
            confirmation="ACTIVATE_STAGED_RESTORE",
        )

    monkeypatch.setattr(backups_module.sqlite3, "connect", real_connect)
    verified = verify_staged_restore_candidate(
        backend,
        staged["candidate_id"],
    )
    assert verified["candidate_id"] == staged["candidate_id"]
    assert not (
        backup_dir
        / f"restore-{staged['candidate_id']}.activation.json"
    ).exists()


def test_restore_activation_history_lists_valid_receipts_newest_first(
    tmp_path,
    monkeypatch,
):
    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    monkeypatch.setenv("PRODUCTION_OS_BACKUP_DIR", str(backup_dir))
    backend = SQLiteBackend(tmp_path / "production.sqlite")

    older = {
        "candidate_id":"20260925T120000Z-aaaaaaaaaaaa",
        "source_backup_id":"20260925T110000Z-bbbbbbbbbbbb",
        "rollback_backup_id":"20260925T120100Z-cccccccccccc",
        "activated_at":"2026-09-25T12:00:00+00:00",
        "schema_version":str(backend.SCHEMA_VERSION),
        "sha256":"1" * 64,
    }
    newer = {
        "candidate_id":"20260925T130000Z-dddddddddddd",
        "source_backup_id":"20260925T125000Z-eeeeeeeeeeee",
        "rollback_backup_id":"20260925T130100Z-ffffffffffff",
        "activated_at":"2026-09-25T13:00:00+00:00",
        "schema_version":str(backend.SCHEMA_VERSION),
        "sha256":"2" * 64,
    }
    for row in (older, newer):
        (
            backup_dir
            / f"restore-{row['candidate_id']}.activation.json"
        ).write_text(json.dumps(row), encoding="utf-8")

    rows = restore_activation_history(backend)

    assert [row["candidate_id"] for row in rows] == [
        newer["candidate_id"],
        older["candidate_id"],
    ]


def test_restore_activation_history_ignores_malformed_receipts(
    tmp_path,
    monkeypatch,
):
    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    monkeypatch.setenv("PRODUCTION_OS_BACKUP_DIR", str(backup_dir))
    backend = SQLiteBackend(tmp_path / "production.sqlite")
    (
        backup_dir
        / "restore-20260925T120000Z-aaaaaaaaaaaa.activation.json"
    ).write_text(
        json.dumps({
            "candidate_id":"20260925T120000Z-aaaaaaaaaaaa",
            "source_backup_id":"../bad",
            "rollback_backup_id":"20260925T120100Z-cccccccccccc",
            "activated_at":"2026-09-25T12:00:00+00:00",
            "schema_version":"16",
            "sha256":"1" * 64,
        }),
        encoding="utf-8",
    )
    (
        backup_dir
        / "restore-20260925T130000Z-dddddddddddd.activation.json"
    ).write_text("{invalid", encoding="utf-8")

    assert restore_activation_history(backend) == []


def test_restore_activation_history_is_empty_when_unconfigured_or_postgres(
    tmp_path,
    monkeypatch,
):
    monkeypatch.delenv("PRODUCTION_OS_BACKUP_DIR", raising=False)
    backend = SQLiteBackend(tmp_path / "production.sqlite")
    assert restore_activation_history(backend) == []

    monkeypatch.setenv("PRODUCTION_OS_BACKUP_DIR", str(tmp_path / "backups"))
    assert restore_activation_history(_FakePostgres()) == []


def test_backup_storage_inventory_classifies_files_without_exposing_paths(
    tmp_path,
    monkeypatch,
):
    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    monkeypatch.setenv("PRODUCTION_OS_BACKUP_DIR", str(backup_dir))
    backend = SQLiteBackend(tmp_path / "production.sqlite")

    backup_id = "20260925T120000Z-aaaaaaaaaaaa"
    candidate_id = "20260925T130000Z-bbbbbbbbbbbb"
    files = {
        f"{backup_id}.sqlite":b"12345",
        f"{backup_id}.json":b"12",
        f"restore-{candidate_id}.sqlite":b"1234567",
        f"restore-{candidate_id}.json":b"123",
        f"restore-{candidate_id}.activation.json":b"1234",
        ".restore-temp.sqlite.tmp":b"123456",
        "notes.txt":b"12345678",
    }
    for name, payload in files.items():
        (backup_dir / name).write_bytes(payload)

    inventory = backup_storage_inventory(backend)

    assert inventory["status"] == "ready"
    assert inventory["backend_kind"] == "sqlite"
    assert inventory["total_size_bytes"] == 35
    assert inventory["backup_count"] == 1
    assert inventory["backup_bytes"] == 7
    assert inventory["restore_candidate_count"] == 1
    assert inventory["restore_candidate_bytes"] == 10
    assert inventory["activation_receipt_count"] == 1
    assert inventory["activation_receipt_bytes"] == 4
    assert inventory["temp_file_count"] == 1
    assert inventory["temp_file_bytes"] == 6
    assert inventory["stale_temp_count"] == 0
    assert inventory["stale_temp_bytes"] == 0
    assert inventory["unknown_file_count"] == 1
    assert inventory["unknown_file_bytes"] == 8
    assert inventory["filesystem"]["status"] in {"ok","warning","critical"}
    assert inventory["filesystem"]["total_bytes"] > 0
    assert inventory["filesystem"]["available_bytes"] >= 0
    encoded = json.dumps(inventory).lower()
    assert str(backup_dir).lower() not in encoded
    assert backup_id not in encoded
    assert candidate_id not in encoded


def test_backup_storage_inventory_missing_directory_is_zero_and_read_only(
    tmp_path,
    monkeypatch,
):
    backup_dir = tmp_path / "missing-backups"
    monkeypatch.setenv("PRODUCTION_OS_BACKUP_DIR", str(backup_dir))
    backend = SQLiteBackend(tmp_path / "production.sqlite")

    inventory = backup_storage_inventory(backend)

    assert inventory["status"] == "ready"
    assert inventory["total_size_bytes"] == 0
    assert inventory["backup_count"] == 0
    assert not backup_dir.exists()


def test_backup_storage_inventory_postgres_is_truthfully_unsupported(
    tmp_path,
    monkeypatch,
):
    monkeypatch.setenv("PRODUCTION_OS_BACKUP_DIR", str(tmp_path / "backups"))
    inventory = backup_storage_inventory(_FakePostgres())

    assert inventory["status"] == "unsupported"
    assert inventory["backend_kind"] == "postgres"
    assert inventory["total_size_bytes"] == 0
    assert inventory["backup_count"] == 0


def test_backup_storage_inventory_marks_only_old_temps_stale(
    tmp_path,
    monkeypatch,
):
    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    monkeypatch.setenv("PRODUCTION_OS_BACKUP_DIR", str(backup_dir))
    backend = SQLiteBackend(tmp_path / "production.sqlite")
    old_temp = backup_dir / ".old.sqlite.tmp"
    fresh_temp = backup_dir / ".fresh.sqlite.tmp"
    old_temp.write_bytes(b"1234")
    fresh_temp.write_bytes(b"12")
    old = time.time() - 90000
    os.utime(old_temp, (old, old))

    inventory = backup_storage_inventory(backend)

    assert inventory["temp_file_count"] == 2
    assert inventory["temp_file_bytes"] == 6
    assert inventory["stale_temp_count"] == 1
    assert inventory["stale_temp_bytes"] == 4


def test_prune_stale_backup_temps_deletes_only_stale_temp_files(
    tmp_path,
    monkeypatch,
):
    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    monkeypatch.setenv("PRODUCTION_OS_BACKUP_DIR", str(backup_dir))
    backend = SQLiteBackend(tmp_path / "production.sqlite")
    stale = backup_dir / ".stale.sqlite.tmp"
    fresh = backup_dir / ".fresh.sqlite.tmp"
    backup = backup_dir / "20260925T120000Z-aaaaaaaaaaaa.sqlite"
    candidate = backup_dir / "restore-20260925T130000Z-bbbbbbbbbbbb.sqlite"
    receipt = backup_dir / "restore-20260925T130000Z-bbbbbbbbbbbb.activation.json"
    unknown = backup_dir / "notes.txt"
    for path, payload in (
        (stale,b"1234"),
        (fresh,b"12"),
        (backup,b"backup"),
        (candidate,b"candidate"),
        (receipt,b"receipt"),
        (unknown,b"unknown"),
    ):
        path.write_bytes(payload)
    old = time.time() - 90000
    os.utime(stale, (old, old))

    result = prune_stale_backup_temps(
        backend,
        expected_candidate_count=1,
    )

    assert result["deleted_count"] == 1
    assert result["deleted_bytes"] == 4
    assert not stale.exists()
    for protected in (fresh, backup, candidate, receipt, unknown):
        assert protected.exists()


def test_prune_stale_backup_temps_count_mismatch_changes_nothing(
    tmp_path,
    monkeypatch,
):
    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    monkeypatch.setenv("PRODUCTION_OS_BACKUP_DIR", str(backup_dir))
    backend = SQLiteBackend(tmp_path / "production.sqlite")
    stale = backup_dir / ".stale.sqlite.tmp"
    stale.write_bytes(b"1234")
    old = time.time() - 90000
    os.utime(stale, (old, old))

    with pytest.raises(BackupTempCandidateConflict) as exc:
        prune_stale_backup_temps(
            backend,
            expected_candidate_count=2,
        )

    assert exc.value.expected == 2
    assert exc.value.actual == 1
    assert stale.exists()


def test_backup_filesystem_capacity_uses_existing_parent_for_missing_directory(
    tmp_path,
    monkeypatch,
):
    backup_dir = tmp_path / "nested" / "backups"
    monkeypatch.setenv("PRODUCTION_OS_BACKUP_DIR", str(backup_dir))
    backend = SQLiteBackend(tmp_path / "production.sqlite")

    inventory = backup_storage_inventory(backend)
    filesystem = inventory["filesystem"]

    assert inventory["status"] == "ready"
    assert filesystem["status"] in {"ok","warning","critical"}
    assert filesystem["total_bytes"] > 0
    assert filesystem["available_bytes"] >= 0
    assert 0 <= filesystem["used_percent"] <= 100
    assert 0 <= filesystem["available_percent"] <= 100
    assert not backup_dir.exists()


def test_backup_filesystem_capacity_is_unavailable_when_unconfigured(
    tmp_path,
    monkeypatch,
):
    monkeypatch.delenv("PRODUCTION_OS_BACKUP_DIR", raising=False)
    backend = SQLiteBackend(tmp_path / "production.sqlite")

    filesystem = backup_storage_inventory(backend)["filesystem"]

    assert filesystem["status"] == "unconfigured"
    assert filesystem["total_bytes"] is None
    assert filesystem["available_bytes"] is None


def test_backup_filesystem_capacity_postgres_is_unsupported(
    tmp_path,
    monkeypatch,
):
    monkeypatch.setenv("PRODUCTION_OS_BACKUP_DIR", str(tmp_path / "backups"))

    filesystem = backup_storage_inventory(_FakePostgres())["filesystem"]

    assert filesystem["status"] == "unsupported"
    assert filesystem["total_bytes"] is None
    assert filesystem["available_bytes"] is None


def test_backup_filesystem_capacity_converts_statvfs_and_thresholds(
    tmp_path,
    monkeypatch,
):
    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    monkeypatch.setenv("PRODUCTION_OS_BACKUP_DIR", str(backup_dir))
    backend = SQLiteBackend(tmp_path / "production.sqlite")

    class Stats:
        f_frsize = 4096
        f_bsize = 4096
        f_blocks = 1000
        f_bfree = 100
        f_bavail = 40

    monkeypatch.setattr("production_os.dashboard_backups.os.statvfs", lambda _: Stats())
    filesystem = backup_storage_inventory(backend)["filesystem"]

    assert filesystem["status"] == "critical"
    assert filesystem["total_bytes"] == 4096000
    assert filesystem["free_bytes"] == 409600
    assert filesystem["available_bytes"] == 163840
    assert filesystem["used_bytes"] == 3686400
    assert filesystem["used_percent"] == 90.0
    assert filesystem["available_percent"] == 4.0


def test_backup_filesystem_capacity_statvfs_error_is_unknown_not_zero(
    tmp_path,
    monkeypatch,
):
    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    monkeypatch.setenv("PRODUCTION_OS_BACKUP_DIR", str(backup_dir))
    backend = SQLiteBackend(tmp_path / "production.sqlite")

    def fail(_):
        raise OSError("unavailable")

    monkeypatch.setattr("production_os.dashboard_backups.os.statvfs", fail)
    filesystem = backup_storage_inventory(backend)["filesystem"]

    assert filesystem["status"] == "unknown"
    assert filesystem["total_bytes"] is None
    assert filesystem["available_bytes"] is None

def test_storage_inventory_keeps_filesystem_shape_when_directory_listing_fails(
    tmp_path,
    monkeypatch,
):
    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    monkeypatch.setenv("PRODUCTION_OS_BACKUP_DIR", str(backup_dir))
    backend = SQLiteBackend(tmp_path / "production.sqlite")

    path_type = type(backup_dir)
    original_iterdir = path_type.iterdir

    def failing_iterdir(path):
        if path == backup_dir:
            raise OSError("simulated directory listing failure")
        return original_iterdir(path)

    monkeypatch.setattr(path_type, "iterdir", failing_iterdir)

    inventory = backup_storage_inventory(backend)

    assert inventory["status"] == "degraded"
    assert inventory["backend_kind"] == "sqlite"
    assert "filesystem" in inventory
    assert set(inventory["filesystem"]) == {
        "status",
        "total_bytes",
        "free_bytes",
        "available_bytes",
        "used_bytes",
        "used_percent",
        "available_percent",
    }

def test_storage_inventory_reports_verified_backup_age_distribution(
    tmp_path,
    monkeypatch,
):
    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    monkeypatch.setenv("PRODUCTION_OS_BACKUP_DIR", str(backup_dir))
    backend = SQLiteBackend(tmp_path / "production.sqlite")
    now = datetime.now(timezone.utc)
    samples = [
        ("20260925T120000Z-000000000001", now - timedelta(hours=2)),
        ("20260924T120000Z-000000000002", now - timedelta(days=2)),
        ("20260915T120000Z-000000000003", now - timedelta(days=10)),
        ("20260816T120000Z-000000000004", now - timedelta(days=40)),
    ]
    for backup_id, created_at in samples:
        (backup_dir / f"{backup_id}.json").write_text(
            json.dumps(
                {
                    "backup_id":backup_id,
                    "backend_kind":"sqlite",
                    "created_at":created_at.isoformat(),
                    "size_bytes":1,
                    "sha256":"0" * 64,
                    "verified":True,
                }
            )
        )
    invalid_id = "20260901T120000Z-000000000005"
    (backup_dir / f"{invalid_id}.json").write_text(
        json.dumps(
            {
                "backup_id":invalid_id,
                "backend_kind":"sqlite",
                "created_at":"not-a-timestamp",
                "size_bytes":1,
                "sha256":"0" * 64,
                "verified":True,
            }
        )
    )

    age = backup_storage_inventory(backend)["backup_age"]

    assert age["verified_count"] == 5
    assert age["valid_timestamp_count"] == 4
    assert age["invalid_timestamp_count"] == 1
    assert age["buckets"] == {
        "under_24h":1,
        "one_to_seven_days":1,
        "seven_to_thirty_days":1,
        "over_thirty_days":1,
    }
    assert age["newest_created_at"] is not None
    assert age["oldest_created_at"] is not None

def test_storage_inventory_retention_preview_protects_restore_history_and_latest(
    tmp_path,
    monkeypatch,
):
    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    monkeypatch.setenv("PRODUCTION_OS_BACKUP_DIR", str(backup_dir))
    backend = SQLiteBackend(tmp_path / "production.sqlite")
    now = datetime.now(timezone.utc)
    rows = [
        ("20260925T120000Z-100000000001", now - timedelta(days=1)),
        ("20260924T120000Z-100000000002", now - timedelta(days=2)),
        ("20260816T120000Z-100000000003", now - timedelta(days=40)),
        ("20260806T120000Z-100000000004", now - timedelta(days=50)),
        ("20260727T120000Z-100000000005", now - timedelta(days=60)),
    ]
    for backup_id, created_at in rows:
        (backup_dir / f"{backup_id}.json").write_text(
            json.dumps(
                {
                    "backup_id":backup_id,
                    "backend_kind":"sqlite",
                    "created_at":created_at.isoformat(),
                    "size_bytes":100,
                    "sha256":"0" * 64,
                    "verified":True,
                }
            )
        )

    invalid_id = "20260717T120000Z-100000000006"
    (backup_dir / f"{invalid_id}.json").write_text(
        json.dumps(
            {
                "backup_id":invalid_id,
                "backend_kind":"sqlite",
                "created_at":"invalid",
                "size_bytes":100,
                "sha256":"0" * 64,
                "verified":True,
            }
        )
    )

    protected_id = rows[-1][0]
    candidate_id = "20260925T120000Z-200000000001"
    rollback_id = "20260925T120000Z-200000000002"
    (backup_dir / f"restore-{candidate_id}.activation.json").write_text(
        json.dumps(
            {
                "candidate_id":candidate_id,
                "source_backup_id":protected_id,
                "rollback_backup_id":rollback_id,
                "activated_at":now.isoformat(),
                "schema_version":"15",
                "sha256":"1" * 64,
            }
        )
    )

    preview = backup_storage_inventory(backend)["retention_preview"]

    assert preview["status"] == "preview"
    assert preview["retention_days"] == 30
    assert preview["min_keep_latest"] == 3
    assert preview["verified_count"] == 6
    assert preview["candidate_count"] == 1
    assert preview["candidate_bytes"] == 100
    assert preview["protected_count"] == 5
    assert preview["protected_reasons"] == {
        "recent":0,
        "latest_floor":3,
        "restore_history":1,
        "invalid_timestamp":1,
    }
    assert preview["deletion_enabled"] is False

def test_prune_expired_verified_backups_deletes_only_current_candidates(
    tmp_path,
    monkeypatch,
):
    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    monkeypatch.setenv("PRODUCTION_OS_BACKUP_DIR", str(backup_dir))
    backend = SQLiteBackend(tmp_path / "production.sqlite")
    now = datetime.now(timezone.utc)
    rows = [
        ("20260925T120000Z-300000000001", now - timedelta(days=1)),
        ("20260924T120000Z-300000000002", now - timedelta(days=2)),
        ("20260923T120000Z-300000000003", now - timedelta(days=3)),
        ("20260806T120000Z-300000000004", now - timedelta(days=50)),
        ("20260727T120000Z-300000000005", now - timedelta(days=60)),
    ]
    for backup_id, created_at in rows:
        (backup_dir / f"{backup_id}.sqlite").write_bytes(b"backup-bytes")
        (backup_dir / f"{backup_id}.json").write_text(
            json.dumps(
                {
                    "backup_id":backup_id,
                    "backend_kind":"sqlite",
                    "created_at":created_at.isoformat(),
                    "size_bytes":12,
                    "sha256":"0" * 64,
                    "verified":True,
                }
            )
        )

    protected_old = rows[-1][0]
    receipt_candidate = "20260925T120000Z-400000000001"
    rollback_id = "20260925T120000Z-400000000002"
    (backup_dir / f"restore-{receipt_candidate}.activation.json").write_text(
        json.dumps(
            {
                "candidate_id":receipt_candidate,
                "source_backup_id":protected_old,
                "rollback_backup_id":rollback_id,
                "activated_at":now.isoformat(),
                "schema_version":"15",
                "sha256":"1" * 64,
            }
        )
    )

    preview = backup_storage_inventory(backend)["retention_preview"]
    assert preview["candidate_count"] == 1
    candidate_id = rows[-2][0]

    result = prune_expired_verified_backups(
        backend,
        expected_candidate_count=preview["candidate_count"],
        expected_candidate_fingerprint=preview["candidate_fingerprint"],
    )

    assert result["deleted_count"] == 1
    assert result["deleted_bytes"] > 0
    assert not (backup_dir / f"{candidate_id}.sqlite").exists()
    assert not (backup_dir / f"{candidate_id}.json").exists()
    assert (backup_dir / f"{protected_old}.sqlite").exists()
    assert (backup_dir / f"{protected_old}.json").exists()
    for backup_id, _ in rows[:3]:
        assert (backup_dir / f"{backup_id}.sqlite").exists()
        assert (backup_dir / f"{backup_id}.json").exists()


def test_prune_expired_verified_backups_rejects_changed_fingerprint(
    tmp_path,
    monkeypatch,
):
    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    monkeypatch.setenv("PRODUCTION_OS_BACKUP_DIR", str(backup_dir))
    backend = SQLiteBackend(tmp_path / "production.sqlite")
    now = datetime.now(timezone.utc)
    rows = [
        ("20260925T120000Z-500000000001", now - timedelta(days=1)),
        ("20260924T120000Z-500000000002", now - timedelta(days=2)),
        ("20260923T120000Z-500000000003", now - timedelta(days=3)),
        ("20260727T120000Z-500000000004", now - timedelta(days=60)),
    ]
    for backup_id, created_at in rows:
        (backup_dir / f"{backup_id}.json").write_text(
            json.dumps(
                {
                    "backup_id":backup_id,
                    "backend_kind":"sqlite",
                    "created_at":created_at.isoformat(),
                    "size_bytes":12,
                    "sha256":"0" * 64,
                    "verified":True,
                }
            )
        )

    preview = backup_storage_inventory(backend)["retention_preview"]
    assert preview["candidate_count"] == 1

    with pytest.raises(BackupRetentionCandidateConflict) as exc:
        prune_expired_verified_backups(
            backend,
            expected_candidate_count=1,
            expected_candidate_fingerprint="f" * 64,
        )

    assert exc.value.expected_count == 1
    assert exc.value.actual_count == 1
    assert exc.value.fingerprint_changed is True
    assert (backup_dir / f"{rows[-1][0]}.json").exists()

