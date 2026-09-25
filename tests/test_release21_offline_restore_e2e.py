from __future__ import annotations

import json
import sqlite3

from production_os.cli import _parse_args, run_restore_activate
from production_os.control_plane import ControlPlane
from production_os.dashboard_backups import (
    create_verified_sqlite_backup,
    stage_verified_sqlite_restore,
)
from production_os.sqlite_backend import SQLiteBackend


def test_release21_offline_restore_activation_survives_restart(
    tmp_path,
    monkeypatch,
    capsys,
):
    database = tmp_path / "production.sqlite"
    backup_dir = tmp_path / "backups"
    monkeypatch.setenv("PRODUCTION_OS_BACKUP_DIR", str(backup_dir))

    backend = SQLiteBackend(database)
    with backend.transaction() as db:
        db.execute(
            "INSERT INTO schema_meta(key,value) VALUES('release21_probe','backup-state') "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value"
        )
    backup = create_verified_sqlite_backup(backend)
    staged = stage_verified_sqlite_restore(backend, backup["backup_id"])

    with backend.transaction() as db:
        db.execute(
            "UPDATE schema_meta SET value='live-state' WHERE key='release21_probe'"
        )

    args = _parse_args([
        "restore-activate",
        "--database", str(database),
        "--candidate-id", staged["candidate_id"],
        "--confirm", "ACTIVATE_STAGED_RESTORE",
    ])
    assert run_restore_activate(args) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["activated"] is True
    assert payload["rollback_backup_id"]

    restarted = ControlPlane(str(database))
    with restarted.backend.connect() as db:
        value = db.execute(
            "SELECT value FROM schema_meta WHERE key='release21_probe'"
        ).fetchone()["value"]
    assert value == "backup-state"

    rollback = backup_dir / f"{payload['rollback_backup_id']}.sqlite"
    with sqlite3.connect(rollback) as db:
        rollback_value = db.execute(
            "SELECT value FROM schema_meta WHERE key='release21_probe'"
        ).fetchone()[0]
    assert rollback_value == "live-state"
