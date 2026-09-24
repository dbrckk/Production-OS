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


def test_release16_operator_path_survives_restart(tmp_path, monkeypatch):
    database = str(tmp_path / "production.sqlite")
    backup_dir = tmp_path / "backups"
    monkeypatch.setenv("PRODUCTION_OS_BACKUP_DIR", str(backup_dir))

    first = ControlPlane(database, authorizer=_auth())
    server, thread, base = _server(first)
    try:
        status, created = _request(
            base,
            "/v1/workflows",
            "operator",
            method="POST",
            body={
                "name":"E2E qualification",
                "repository":"dbrckk/e2e-qualification",
                "tasks":[{
                    "task_id":"implementation",
                    "title":"Qualify operations",
                    "priority":100,
                    "max_attempts":2,
                    "estimated_minutes":5,
                    "payload":{
                        "handoff":{
                            "repository":"dbrckk/e2e-qualification",
                            "task":"Qualify operations",
                            "final_goal":"Qualify operations",
                            "agent_preference":"codex",
                            "token_budget":30000,
                        }
                    },
                }],
            },
        )
        assert status == 201
        workflow_id = created["workflow"]["id"]

        status, dispatched = _request(
            base,
            f"/v1/workflows/{workflow_id}/dispatch",
            "operator",
            method="POST",
            body={"limit":1},
        )
        assert status == 200
        assert len(dispatched["jobs"]) == 1
        job_key = dispatched["jobs"][0]["key"]

        status, incident_payload = _request(
            base,
            "/v1/dashboard/incidents?limit=20",
            "viewer",
        )
        assert status == 200
        incident = next(
            row for row in incident_payload["incidents"]
            if row["code"] == "queue_without_worker"
        )
        kick = next(
            item for item in incident["playbook"]["suggestions"]
            if item["action"] == "kick"
        )
        assert kick["availability"] in {"available", "fallback"}

        status, remediation = _request(
            base,
            "/v1/dashboard/workers/github-actions-worker/control",
            "operator",
            method="POST",
            body={
                "action":"kick",
                "incident_id":incident["id"],
            },
        )
        assert status == 202
        assert remediation["status"] == "scheduled_fallback"

        first.workers.register("worker-a", ["python"], 1)
        for action, expected in (
            ("pause", "paused"),
            ("resume", "active"),
            ("drain", "draining"),
            ("resume", "active"),
        ):
            status, control_result = _request(
                base,
                "/v1/dashboard/workers/worker-a/control",
                "operator",
                method="POST",
                body={"action":action},
            )
            assert status == 202
            assert control_result["desired_state"] == expected

        status, backup = _request(
            base,
            "/v1/dashboard/backups/create",
            "operator",
            method="POST",
            body={"confirm":"CREATE_VERIFIED_BACKUP"},
        )
        assert status == 201
        assert backup["verified"] is True
        backup_id = backup["backup_id"]

        status, restore_readiness = _request(
            base,
            f"/v1/dashboard/backups/{backup_id}/verify",
            "operator",
            method="POST",
            body={"confirm":"VERIFY_BACKUP_FOR_RESTORE"},
        )
        assert status == 200
        assert restore_readiness["restorable"] is True
        assert restore_readiness["integrity"] == "ok"
        assert restore_readiness["restore_enabled"] is False

        assert first.queue.get(job_key)["status"] == "queued"
        remediation_rows = first.dashboard_store.remediation_events(limit=10)
        assert any(
            row["incident_id"] == incident["id"]
            and row["action"] == "kick"
            and row["outcome"] == "scheduled_fallback"
            for row in remediation_rows
        )
        audit = first.dashboard_store.control_audit_events(limit=50)
        actions = {row["action"] for row in audit}
        assert {
            "kick",
            "pause",
            "resume",
            "drain",
            "backup-create",
            "backup-verify",
        } <= actions
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

    second = ControlPlane(database, authorizer=_auth())
    assert second.workflows.get(workflow_id)["id"] == workflow_id
    assert second.queue.get(job_key)["status"] == "queued"
    assert second.dashboard_control.worker_state("worker-a")["desired_state"] == "active"
    assert any(
        row["incident_id"] == incident["id"] and row["action"] == "kick"
        for row in second.dashboard_store.remediation_events(limit=10)
    )
    catalog = second.dashboard.backups()
    assert any(row["backup_id"] == backup_id for row in catalog["backups"])
