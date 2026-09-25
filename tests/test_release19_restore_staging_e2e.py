from __future__ import annotations

import json
import sqlite3
import threading
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer

from production_os.api_auth import TokenAuthorizer, token_digest
from production_os.control_plane import ControlPlane, make_handler


def _auth():
    return TokenAuthorizer([
        {"name":"viewer","role":"viewer","sha256":token_digest("viewer")},
        {"name":"operator","role":"operator","sha256":token_digest("operator")},
    ])


def _request(base, path, token, *, method="GET", body=None):
    data = None if body is None else json.dumps(body).encode("utf-8")
    request = urllib.request.Request(
        base + path,
        data=data,
        method=method,
        headers={
            "Authorization":f"Bearer {token}",
            **({"Content-Type":"application/json"} if data is not None else {}),
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            raw = response.read()
            return response.status, json.loads(raw or b"{}")
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read() or b"{}")


def _server(control):
    server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(control))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread, f"http://127.0.0.1:{server.server_port}"


def test_release19_restore_staging_never_mutates_live_database(
    tmp_path,
    monkeypatch,
):
    database = tmp_path / "production.sqlite"
    backup_dir = tmp_path / "backups"
    monkeypatch.setenv("PRODUCTION_OS_BACKUP_DIR", str(backup_dir))

    first = ControlPlane(str(database), authorizer=_auth())
    with first.backend.transaction() as db:
        db.execute(
            "INSERT INTO schema_meta(key,value) VALUES('release19_probe','backup-state') "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value"
        )

    server, thread, base = _server(first)
    try:
        status, backup = _request(
            base,
            "/v1/dashboard/backups/create",
            "operator",
            method="POST",
            body={"confirm":"CREATE_VERIFIED_BACKUP"},
        )
        assert status == 201
        backup_id = backup["backup_id"]

        with first.backend.transaction() as db:
            db.execute(
                "UPDATE schema_meta SET value='live-state' "
                "WHERE key='release19_probe'"
            )

        status, staged = _request(
            base,
            f"/v1/dashboard/backups/{backup_id}/stage-restore",
            "operator",
            method="POST",
            body={"confirm":"STAGE_VERIFIED_RESTORE"},
        )
        assert status == 201
        assert staged["verified"] is True
        assert staged["integrity"] == "ok"
        assert staged["activation_enabled"] is False
        assert staged["source_backup_id"] == backup_id

        candidate = (
            backup_dir
            / f"restore-{staged['candidate_id']}.sqlite"
        )
        assert candidate.is_file()
        with sqlite3.connect(candidate) as db:
            candidate_probe = db.execute(
                "SELECT value FROM schema_meta "
                "WHERE key='release19_probe'"
            ).fetchone()[0]
        assert candidate_probe == "backup-state"

        with first.backend.connect() as db:
            live_probe = db.execute(
                "SELECT value FROM schema_meta "
                "WHERE key='release19_probe'"
            ).fetchone()["value"]
        assert live_probe == "live-state"

        audit = first.dashboard_store.control_audit_events(limit=20)
        stage_event = next(
            row for row in audit
            if row["action"] == "backup-stage-restore"
        )
        assert stage_event["outcome"] == "succeeded"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

    second = ControlPlane(str(database), authorizer=_auth())
    with second.backend.connect() as db:
        restarted_probe = db.execute(
            "SELECT value FROM schema_meta "
            "WHERE key='release19_probe'"
        ).fetchone()["value"]
    assert restarted_probe == "live-state"
