from __future__ import annotations

import json
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
        {"name":"worker","role":"worker","sha256":token_digest("worker")},
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
        with urllib.request.urlopen(request, timeout=3) as response:
            return response.status, json.loads(response.read() or b"{}")
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read() or b"{}")


def _server(control):
    server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(control))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread, f"http://127.0.0.1:{server.server_port}"


def test_backup_catalog_is_viewer_readable_and_worker_forbidden(tmp_path, monkeypatch):
    backup_dir = tmp_path / "backups"
    monkeypatch.setenv("PRODUCTION_OS_BACKUP_DIR", str(backup_dir))
    control = ControlPlane(str(tmp_path / "control.sqlite"), authorizer=_auth())
    server, thread, base = _server(control)
    try:
        status, payload = _request(
            base,
            "/v1/dashboard/backups",
            "viewer",
        )
        assert status == 200
        assert payload["backend_kind"] == "sqlite"
        assert payload["status"] == "ready"
        assert payload["create_supported"] is True
        assert payload["restore_enabled"] is False
        assert payload["backups"] == []

        status, _ = _request(
            base,
            "/v1/dashboard/backups",
            "worker",
        )
        assert status == 403
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_backup_creation_requires_operator_and_exact_confirmation(tmp_path, monkeypatch):
    monkeypatch.setenv("PRODUCTION_OS_BACKUP_DIR", str(tmp_path / "backups"))
    control = ControlPlane(str(tmp_path / "control.sqlite"), authorizer=_auth())
    server, thread, base = _server(control)
    try:
        status, _ = _request(
            base,
            "/v1/dashboard/backups/create",
            "viewer",
            method="POST",
            body={"confirm":"CREATE_VERIFIED_BACKUP"},
        )
        assert status == 403

        status, _ = _request(
            base,
            "/v1/dashboard/backups/create",
            "operator",
            method="POST",
            body={"confirm":"wrong"},
        )
        assert status == 400
        assert control.dashboard_store.control_audit_events(limit=10) == []

        status, payload = _request(
            base,
            "/v1/dashboard/backups/create",
            "operator",
            method="POST",
            body={"confirm":"CREATE_VERIFIED_BACKUP"},
        )
        assert status == 201
        assert payload["verified"] is True
        assert payload["backend_kind"] == "sqlite"
        assert payload["restore_enabled"] is False
        assert "path" not in payload
        assert "dsn" not in payload

        audit = control.dashboard_store.control_audit_events(limit=10)
        assert len(audit) == 1
        assert audit[0]["action"] == "backup-create"
        assert audit[0]["outcome"] == "succeeded"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_unconfigured_backup_returns_conflict_and_failed_audit(tmp_path, monkeypatch):
    monkeypatch.delenv("PRODUCTION_OS_BACKUP_DIR", raising=False)
    control = ControlPlane(str(tmp_path / "control.sqlite"), authorizer=_auth())
    server, thread, base = _server(control)
    try:
        status, payload = _request(
            base,
            "/v1/dashboard/backups/create",
            "operator",
            method="POST",
            body={"confirm":"CREATE_VERIFIED_BACKUP"},
        )
        assert status == 409
        assert "not ready" in payload["error"]
        audit = control.dashboard_store.control_audit_events(limit=10)
        assert len(audit) == 1
        assert audit[0]["action"] == "backup-create"
        assert audit[0]["outcome"] == "failed"
        assert audit[0]["error_code"] == "backup_unavailable"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_restore_readiness_api_requires_operator_and_exact_confirmation(
    tmp_path,
    monkeypatch,
):
    backup_dir = tmp_path / "backups"
    monkeypatch.setenv("PRODUCTION_OS_BACKUP_DIR", str(backup_dir))
    control = ControlPlane(str(tmp_path / "control.sqlite"), authorizer=_auth())
    created = control.dashboard.create_verified_backup()
    backup_id = created["backup_id"]
    server, thread, base = _server(control)
    try:
        path = f"/v1/dashboard/backups/{backup_id}/verify"
        status, _ = _request(
            base,
            path,
            "viewer",
            method="POST",
            body={"confirm":"VERIFY_BACKUP_FOR_RESTORE"},
        )
        assert status == 403

        status, _ = _request(
            base,
            path,
            "operator",
            method="POST",
            body={"confirm":"wrong"},
        )
        assert status == 400

        status, payload = _request(
            base,
            path,
            "operator",
            method="POST",
            body={"confirm":"VERIFY_BACKUP_FOR_RESTORE"},
        )
        assert status == 200
        assert payload["restorable"] is True
        assert payload["integrity"] == "ok"
        assert payload["restore_enabled"] is False
        assert payload["schema_version"] == str(control.backend.SCHEMA_VERSION)

        audit = control.dashboard_store.control_audit_events(limit=10)
        verify = next(row for row in audit if row["action"] == "backup-verify")
        assert verify["outcome"] == "succeeded"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_restore_readiness_api_rejects_tampered_backup_and_audits_failure(
    tmp_path,
    monkeypatch,
):
    backup_dir = tmp_path / "backups"
    monkeypatch.setenv("PRODUCTION_OS_BACKUP_DIR", str(backup_dir))
    control = ControlPlane(str(tmp_path / "control.sqlite"), authorizer=_auth())
    created = control.dashboard.create_verified_backup()
    backup_id = created["backup_id"]
    backup_file = backup_dir / f"{backup_id}.sqlite"
    backup_file.write_bytes(backup_file.read_bytes() + b"tamper")
    server, thread, base = _server(control)
    try:
        status, payload = _request(
            base,
            f"/v1/dashboard/backups/{backup_id}/verify",
            "operator",
            method="POST",
            body={"confirm":"VERIFY_BACKUP_FOR_RESTORE"},
        )
        assert status == 409
        assert "manifest" in payload["error"] or "hash" in payload["error"] or "size" in payload["error"]

        audit = control.dashboard_store.control_audit_events(limit=10)
        verify = next(row for row in audit if row["action"] == "backup-verify")
        assert verify["outcome"] == "failed"
        assert verify["error_code"] == "backup_verify_failed"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_restore_staging_requires_operator_and_exact_confirmation(
    tmp_path,
    monkeypatch,
):
    backup_dir = tmp_path / "backups"
    monkeypatch.setenv("PRODUCTION_OS_BACKUP_DIR", str(backup_dir))
    control = ControlPlane(str(tmp_path / "control.sqlite"), authorizer=_auth())
    created = control.dashboard.create_verified_backup()
    backup_id = created["backup_id"]
    server, thread, base = _server(control)
    try:
        path = f"/v1/dashboard/backups/{backup_id}/stage-restore"
        status, _ = _request(
            base,
            path,
            "viewer",
            method="POST",
            body={"confirm":"STAGE_VERIFIED_RESTORE"},
        )
        assert status == 403

        before = sorted(p.name for p in backup_dir.iterdir())
        status, payload = _request(
            base,
            path,
            "operator",
            method="POST",
            body={"confirm":"wrong"},
        )
        assert status == 400
        assert "confirmation" in payload["error"]
        assert sorted(p.name for p in backup_dir.iterdir()) == before

        status, staged = _request(
            base,
            path,
            "operator",
            method="POST",
            body={"confirm":"STAGE_VERIFIED_RESTORE"},
        )
        assert status == 201
        assert staged["verified"] is True
        assert staged["activation_enabled"] is False
        assert staged["source_backup_id"] == backup_id
        assert "path" not in staged

        audit = control.dashboard_store.control_audit_events(limit=20)
        event = next(
            row for row in audit
            if row["action"] == "backup-stage-restore"
        )
        assert event["outcome"] == "succeeded"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_restore_staging_rejects_tampered_backup_and_audits_failure(
    tmp_path,
    monkeypatch,
):
    backup_dir = tmp_path / "backups"
    monkeypatch.setenv("PRODUCTION_OS_BACKUP_DIR", str(backup_dir))
    control = ControlPlane(str(tmp_path / "control.sqlite"), authorizer=_auth())
    created = control.dashboard.create_verified_backup()
    backup_id = created["backup_id"]
    source = backup_dir / f"{backup_id}.sqlite"
    source.write_bytes(source.read_bytes() + b"tamper")
    server, thread, base = _server(control)
    try:
        status, payload = _request(
            base,
            f"/v1/dashboard/backups/{backup_id}/stage-restore",
            "operator",
            method="POST",
            body={"confirm":"STAGE_VERIFIED_RESTORE"},
        )
        assert status == 409
        assert payload["error"]
        assert list(backup_dir.glob("restore-*.sqlite")) == []

        audit = control.dashboard_store.control_audit_events(limit=20)
        event = next(
            row for row in audit
            if row["action"] == "backup-stage-restore"
        )
        assert event["outcome"] == "failed"
        assert event["error_code"] == "backup_stage_restore_failed"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_backup_catalog_exposes_restore_activation_history_to_viewer(
    tmp_path,
    monkeypatch,
):
    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    monkeypatch.setenv("PRODUCTION_OS_BACKUP_DIR", str(backup_dir))
    control = ControlPlane(str(tmp_path / "control.sqlite"), authorizer=_auth())
    receipt = {
        "candidate_id":"20260925T130000Z-aaaaaaaaaaaa",
        "source_backup_id":"20260925T120000Z-bbbbbbbbbbbb",
        "rollback_backup_id":"20260925T130100Z-cccccccccccc",
        "activated_at":"2026-09-25T13:00:00+00:00",
        "schema_version":str(control.backend.SCHEMA_VERSION),
        "sha256":"1" * 64,
    }
    (
        backup_dir
        / "restore-20260925T130000Z-aaaaaaaaaaaa.activation.json"
    ).write_text(json.dumps(receipt), encoding="utf-8")

    server, thread, base = _server(control)
    try:
        status, payload = _request(
            base,
            "/v1/dashboard/backups",
            "viewer",
        )
        assert status == 200
        assert payload["activations"] == [receipt]

        status, _ = _request(
            base,
            "/v1/dashboard/backups",
            "worker",
        )
        assert status == 403
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_backup_http_surface_has_no_restore_activation_route(tmp_path, monkeypatch):
    monkeypatch.setenv("PRODUCTION_OS_BACKUP_DIR", str(tmp_path / "backups"))
    control = ControlPlane(str(tmp_path / "control.sqlite"), authorizer=_auth())
    server, thread, base = _server(control)
    try:
        status, _ = _request(
            base,
            "/v1/dashboard/backups/restore-activate",
            "operator",
            method="POST",
            body={"confirm":"ACTIVATE_STAGED_RESTORE"},
        )
        assert status == 404
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_backup_catalog_exposes_aggregated_storage_inventory(
    tmp_path,
    monkeypatch,
):
    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    monkeypatch.setenv("PRODUCTION_OS_BACKUP_DIR", str(backup_dir))
    control = ControlPlane(str(tmp_path / "control.sqlite"), authorizer=_auth())
    backup_id = "20260925T120000Z-aaaaaaaaaaaa"
    (backup_dir / f"{backup_id}.sqlite").write_bytes(b"1234")
    (backup_dir / f"{backup_id}.json").write_bytes(b"12")
    (backup_dir / "unknown.bin").write_bytes(b"123")

    server, thread, base = _server(control)
    try:
        status, payload = _request(
            base,
            "/v1/dashboard/backups",
            "viewer",
        )
        assert status == 200
        storage = payload["storage"]
        assert storage["backend_kind"] == "sqlite"
        assert storage["backup_count"] == 1
        assert storage["backup_bytes"] == 6
        assert storage["unknown_file_count"] == 1
        assert storage["unknown_file_bytes"] == 3
        assert "path" not in storage
        assert "files" not in storage
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
