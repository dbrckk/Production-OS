from __future__ import annotations

import json
import threading
import urllib.error
import urllib.request
from datetime import datetime, timezone
from http.server import ThreadingHTTPServer

from production_os.api_auth import TokenAuthorizer, token_digest
from production_os.control_plane import ControlPlane, make_handler
from production_os.dashboard_maintenance import storage_maintenance_snapshot
from production_os.sqlite_backend import SQLiteBackend


NOW = datetime(2026, 9, 24, 18, 0, tzinfo=timezone.utc)


def _auth():
    return TokenAuthorizer([
        {"name":"viewer","role":"viewer","sha256":token_digest("viewer")},
        {"name":"worker","role":"worker","sha256":token_digest("worker")},
    ])


def _get(base, path, token):
    request = urllib.request.Request(
        base + path,
        headers={"Authorization":f"Bearer {token}"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=3) as response:
            return response.status, json.loads(response.read() or b"{}")
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read() or b"{}")


def test_sqlite_maintenance_counts_only_valid_old_rows(tmp_path):
    backend = SQLiteBackend(tmp_path / "maintenance.sqlite")
    with backend.transaction() as db:
        db.execute(
            """INSERT INTO worker_log_events(
                id, worker_id, level, message, created_at
            ) VALUES(?,?,?,?,?)""",
            ("old","worker-a","info","old","2026-08-01T00:00:00+00:00"),
        )
        db.execute(
            """INSERT INTO worker_log_events(
                id, worker_id, level, message, created_at
            ) VALUES(?,?,?,?,?)""",
            ("recent","worker-a","info","recent","2026-09-20T00:00:00+00:00"),
        )
        db.execute(
            """INSERT INTO worker_log_events(
                id, worker_id, level, message, created_at
            ) VALUES(?,?,?,?,?)""",
            ("invalid","worker-a","info","invalid","not-a-time"),
        )

    payload = storage_maintenance_snapshot(backend, now=NOW)
    logs = next(row for row in payload["tables"] if row["name"] == "worker_logs")
    assert logs["rows"] == 3
    assert logs["valid_timestamps"] == 2
    assert logs["invalid_timestamps"] == 1
    assert logs["candidate_rows"] == 1
    assert logs["retention_days"] == 30
    assert payload["candidate_rows"] == 1
    assert payload["status"] == "attention"
    assert payload["backend_kind"] == "sqlite"
    assert isinstance(payload["database_size_bytes"], int)
    assert payload["database_size_bytes"] > 0

    serialized = json.dumps(payload)
    assert str(tmp_path) not in serialized
    assert "dsn" not in payload
    assert "path" not in payload


def test_retention_window_can_be_overridden_without_invalid_values(
    tmp_path,
    monkeypatch,
):
    backend = SQLiteBackend(tmp_path / "retention.sqlite")
    with backend.transaction() as db:
        db.execute(
            """INSERT INTO worker_log_events(
                id, worker_id, level, message, created_at
            ) VALUES(?,?,?,?,?)""",
            ("row","worker-a","info","row","2026-09-10T00:00:00+00:00"),
        )

    monkeypatch.setenv("PRODUCTION_OS_RETENTION_WORKER_LOG_DAYS", "10")
    payload = storage_maintenance_snapshot(backend, now=NOW)
    logs = next(row for row in payload["tables"] if row["name"] == "worker_logs")
    assert logs["retention_days"] == 10
    assert logs["candidate_rows"] == 1

    monkeypatch.setenv("PRODUCTION_OS_RETENTION_WORKER_LOG_DAYS", "invalid")
    payload = storage_maintenance_snapshot(backend, now=NOW)
    logs = next(row for row in payload["tables"] if row["name"] == "worker_logs")
    assert logs["retention_days"] == 30
    assert logs["candidate_rows"] == 0


def test_maintenance_api_is_viewer_readable_and_worker_forbidden(tmp_path):
    control = ControlPlane(
        str(tmp_path / "maintenance-api.sqlite"),
        authorizer=_auth(),
    )
    server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(control))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{server.server_port}"
    try:
        status, payload = _get(
            base,
            "/v1/dashboard/maintenance",
            "viewer",
        )
        assert status == 200
        assert payload["backend_kind"] == "sqlite"
        assert "tables" in payload
        assert "candidate_rows" in payload

        status, payload = _get(
            base,
            "/v1/dashboard/maintenance",
            "worker",
        )
        assert status == 403
        assert payload["error"] == "forbidden"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
