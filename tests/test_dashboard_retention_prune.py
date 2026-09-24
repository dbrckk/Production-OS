from __future__ import annotations

import json
import threading
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer

from production_os.api_auth import TokenAuthorizer, token_digest
from production_os.control_plane import ControlPlane, make_handler
from production_os.dashboard_maintenance import (
    RetentionCandidateConflict,
    prune_expired_history,
    storage_maintenance_snapshot,
)
from production_os.sqlite_backend import SQLiteBackend


OLD = "2020-01-01T00:00:00+00:00"
RECENT = "2099-01-01T00:00:00+00:00"


def _auth():
    return TokenAuthorizer([
        {"name":"viewer","role":"viewer","sha256":token_digest("viewer")},
        {"name":"operator","role":"operator","sha256":token_digest("operator")},
    ])


def _post(base, path, token, body):
    request = urllib.request.Request(
        base + path,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization":f"Bearer {token}",
            "Content-Type":"application/json",
        },
        method="POST",
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


def _seed_retention_rows(backend):
    with backend.transaction() as db:
        db.execute(
            """INSERT INTO worker_log_events(
                id, worker_id, level, message, created_at
            ) VALUES(?,?,?,?,?)""",
            ("old-log","worker-a","info","old",OLD),
        )
        db.execute(
            """INSERT INTO worker_log_events(
                id, worker_id, level, message, created_at
            ) VALUES(?,?,?,?,?)""",
            ("recent-log","worker-a","info","recent",RECENT),
        )
        db.execute(
            """INSERT INTO worker_log_events(
                id, worker_id, level, message, created_at
            ) VALUES(?,?,?,?,?)""",
            ("invalid-log","worker-a","info","invalid","not-a-time"),
        )
        db.execute(
            """INSERT INTO job_executions(
                id, job_key, repository, worker_id, status,
                started_at, created_at
            ) VALUES(?,?,?,?,?,?,?)""",
            (
                "old-running",
                "job-running",
                "dbrckk/example",
                "worker-a",
                "running",
                OLD,
                OLD,
            ),
        )
        db.execute(
            """INSERT INTO job_executions(
                id, job_key, repository, worker_id, status,
                started_at, finished_at, created_at
            ) VALUES(?,?,?,?,?,?,?,?)""",
            (
                "old-succeeded",
                "job-succeeded",
                "dbrckk/example",
                "worker-a",
                "succeeded",
                OLD,
                OLD,
                OLD,
            ),
        )


def _seed_old_remediation(control):
    incident = control.dashboard_store.upsert_dashboard_incident(
        code="queue_without_worker",
        severity="high",
        title="Queue",
        message="waiting",
        target_type="control-plane",
        target_id="global",
        at=OLD,
    )
    return control.dashboard_store.append_remediation_event(
        incident_id=incident["id"],
        action="kick",
        requested_by="operator:dashboard",
        at=OLD,
    )


def test_snapshot_separates_prunable_and_protected_candidates(tmp_path):
    backend = SQLiteBackend(tmp_path / "retention.sqlite")
    _seed_retention_rows(backend)
    control = ControlPlane(
        str(tmp_path / "control.sqlite"),
        authorizer=_auth(),
    )
    _seed_old_remediation(control)

    snapshot = storage_maintenance_snapshot(backend)
    logs = next(row for row in snapshot["tables"] if row["name"] == "worker_logs")
    executions = next(row for row in snapshot["tables"] if row["name"] == "executions")

    assert logs["prunable_candidate_rows"] == 1
    assert logs["invalid_timestamps"] == 1
    assert executions["prunable_candidate_rows"] == 1
    assert executions["protected_candidate_rows"] == 1


def test_prune_deletes_only_valid_old_prunable_rows(tmp_path):
    control = ControlPlane(
        str(tmp_path / "prune.sqlite"),
        authorizer=_auth(),
    )
    _seed_retention_rows(control.backend)
    remediation = _seed_old_remediation(control)

    before = storage_maintenance_snapshot(control.backend)
    assert before["prunable_candidate_rows"] == 2
    assert before["protected_candidate_rows"] >= 2

    result = prune_expired_history(
        control.backend,
        expected_candidate_rows=before["prunable_candidate_rows"],
    )
    assert result["deleted_rows"] == 2

    with control.backend.connect() as db:
        log_ids = {
            row["id"]
            for row in db.execute(
                "SELECT id FROM worker_log_events"
            ).fetchall()
        }
        executions = {
            row["id"]:row["status"]
            for row in db.execute(
                "SELECT id, status FROM job_executions"
            ).fetchall()
        }
        remediation_row = db.execute(
            "SELECT id FROM dashboard_remediation_events WHERE id=?",
            (remediation["id"],),
        ).fetchone()

    assert "old-log" not in log_ids
    assert "recent-log" in log_ids
    assert "invalid-log" in log_ids
    assert "old-succeeded" not in executions
    assert executions["old-running"] == "running"
    assert remediation_row["id"] == remediation["id"]


def test_stale_candidate_count_rolls_back_without_deletion(tmp_path):
    backend = SQLiteBackend(tmp_path / "conflict.sqlite")
    _seed_retention_rows(backend)
    before = storage_maintenance_snapshot(backend)
    expected = before["prunable_candidate_rows"]

    with backend.transaction() as db:
        db.execute(
            """INSERT INTO worker_log_events(
                id, worker_id, level, message, created_at
            ) VALUES(?,?,?,?,?)""",
            ("another-old","worker-a","info","old",OLD),
        )

    try:
        prune_expired_history(
            backend,
            expected_candidate_rows=expected,
        )
        assert False, "stale expected count must conflict"
    except RetentionCandidateConflict as exc:
        assert exc.expected == expected
        assert exc.actual == expected + 1

    with backend.connect() as db:
        assert db.execute(
            "SELECT COUNT(*) AS n FROM worker_log_events"
        ).fetchone()["n"] == 4
        assert db.execute(
            "SELECT COUNT(*) AS n FROM job_executions"
        ).fetchone()["n"] == 2


def test_prune_api_requires_operator_exact_phrase_and_audits_success(tmp_path):
    control = ControlPlane(
        str(tmp_path / "api.sqlite"),
        authorizer=_auth(),
    )
    _seed_retention_rows(control.backend)
    snapshot = storage_maintenance_snapshot(control.backend)
    expected = snapshot["prunable_candidate_rows"]

    server, thread, base = _server(control)
    try:
        status, _ = _post(
            base,
            "/v1/dashboard/maintenance/prune",
            "viewer",
            {
                "confirm":"PRUNE_EXPIRED_HISTORY",
                "expected_candidate_rows":expected,
            },
        )
        assert status == 403

        status, _ = _post(
            base,
            "/v1/dashboard/maintenance/prune",
            "operator",
            {
                "confirm":"wrong",
                "expected_candidate_rows":expected,
            },
        )
        assert status == 400
        assert control.dashboard_store.control_audit_events(limit=10) == []

        status, payload = _post(
            base,
            "/v1/dashboard/maintenance/prune",
            "operator",
            {
                "confirm":"PRUNE_EXPIRED_HISTORY",
                "expected_candidate_rows":expected,
            },
        )
        assert status == 200
        assert payload["deleted_rows"] == expected
        audit = control.dashboard_store.control_audit_events(limit=10)
        assert len(audit) == 1
        assert audit[0]["action"] == "retention-prune"
        assert audit[0]["worker_id"] == "control-plane"
        assert audit[0]["outcome"] == "succeeded"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_prune_api_stale_expected_count_returns_409_and_zero_deletion(tmp_path):
    control = ControlPlane(
        str(tmp_path / "api-conflict.sqlite"),
        authorizer=_auth(),
    )
    _seed_retention_rows(control.backend)
    expected = storage_maintenance_snapshot(
        control.backend
    )["prunable_candidate_rows"]

    with control.backend.transaction() as db:
        db.execute(
            """INSERT INTO worker_log_events(
                id, worker_id, level, message, created_at
            ) VALUES(?,?,?,?,?)""",
            ("late-old","worker-a","info","old",OLD),
        )

    server, thread, base = _server(control)
    try:
        status, payload = _post(
            base,
            "/v1/dashboard/maintenance/prune",
            "operator",
            {
                "confirm":"PRUNE_EXPIRED_HISTORY",
                "expected_candidate_rows":expected,
            },
        )
        assert status == 409
        assert payload["deleted_rows"] == 0
        assert payload["actual_candidate_rows"] == expected + 1

        audit = control.dashboard_store.control_audit_events(limit=10)
        assert len(audit) == 1
        assert audit[0]["outcome"] == "conflict"
        assert audit[0]["error_code"] == "candidate_count_mismatch"

        with control.backend.connect() as db:
            ids = {
                row["id"]
                for row in db.execute(
                    "SELECT id FROM worker_log_events"
                ).fetchall()
            }
        assert {"old-log","recent-log","invalid-log","late-old"} <= ids
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
