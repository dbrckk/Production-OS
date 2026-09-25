from __future__ import annotations

import json
import threading
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer

import pytest

from production_os.api_auth import TokenAuthorizer, token_digest
from production_os.control_plane import ControlPlane, make_handler
from production_os.remote_worker import RemoteWorkerClient


def _auth():
    return TokenAuthorizer([
        {"name":"operator","role":"operator","sha256":token_digest("operator")},
        {"name":"viewer","role":"viewer","sha256":token_digest("viewer")},
        {"name":"worker-one","role":"worker","sha256":token_digest("worker-one")},
        {"name":"worker-two","role":"worker","sha256":token_digest("worker-two")},
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
        raw = exc.read()
        return exc.code, json.loads(raw or b"{}")


def _server(control):
    server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(control))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread, f"http://127.0.0.1:{server.server_port}"


@pytest.mark.e2e
def test_release34_running_one_tap_job_recovers_only_after_dual_staleness(tmp_path):
    database = str(tmp_path / "running-recovery.sqlite")
    control = ControlPlane(database, authorizer=_auth())
    server, thread, base = _server(control)

    try:
        for worker_id in ("worker-one", "worker-two"):
            status, _ = _request(
                base,
                "/v1/workers/register",
                "operator",
                method="POST",
                body={
                    "worker_id":worker_id,
                    "capabilities":[],
                    "max_concurrency":1,
                },
            )
            assert status == 200

        status, launched = _request(
            base,
            "/v1/dashboard/launch",
            "operator",
            method="POST",
            body={
                "repository":"dbrckk/running-recovery-e2e",
                "instruction":"Implement, validate, and preserve recovery safety.",
            },
        )
        assert status == 201
        project = launched["project"]
        project_id = project["project_id"]
        workflow_id = project["current_workflow_id"]

        worker_one = RemoteWorkerClient(
            base,
            "worker-one",
            "worker-one",
            [],
            timeout=5,
        )
        first_claim = worker_one.claim()
        assert first_claim is not None
        job_key = first_claim.key
        assert worker_one.ack(job_key)["status"] == "acked"

        status, _ = _request(
            base,
            f"/v1/jobs/{job_key}/telemetry",
            "worker-one",
            method="POST",
            body={
                "worker_id":"worker-one",
                "stage":"implementation",
                "progress":40,
                "usage":{"total_tokens":900},
            },
        )
        assert status == 200

        # Stale worker heartbeat alone is insufficient: fresh execution
        # telemetry must fence automatic recovery.
        with control.backend.transaction() as db:
            db.execute(
                "UPDATE workers SET last_heartbeat=? WHERE worker_id=?",
                ("2000-01-01T00:00:00+00:00", "worker-one"),
            )

        worker_two = RemoteWorkerClient(
            base,
            "worker-two",
            "worker-two",
            [],
            timeout=5,
        )
        assert worker_two.claim() is None
        assert control.queue.get(job_key)["status"] == "acked"

        # Once both heartbeat and execution telemetry are stale, the next
        # healthy worker may safely fence the old owner and resume the job.
        with control.backend.transaction() as db:
            db.execute(
                """UPDATE job_executions
                   SET last_telemetry_at=?, started_at=?
                   WHERE job_key=? AND status='running'""",
                (
                    "2000-01-01T00:00:00+00:00",
                    "2000-01-01T00:00:00+00:00",
                    job_key,
                ),
            )

        recovered = worker_two.claim()
        assert recovered is not None
        assert recovered.key == job_key
        assert recovered.payload["claimed_by"] == "worker-two"
        assert recovered.payload["delivery_attempt"] == 2

        with control.backend.connect() as db:
            old_execution = dict(
                db.execute(
                    """SELECT * FROM job_executions
                       WHERE job_key=? AND attempt=1""",
                    (job_key,),
                ).fetchone()
            )
        assert old_execution["status"] == "failed"
        assert old_execution["error_type"] == "worker_abandoned"

        assert worker_two.ack(job_key)["status"] == "acked"
        assert worker_two.complete(
            job_key,
            result_payload={
                "summary":"recovered safely",
                "usage":{
                    "total_tokens":1900,
                    "runs":1,
                    "agents":{"auto":1},
                },
                "validation":{"status":"passed"},
            },
            duration_seconds=8.0,
        )["status"] == "completed"

        status, refreshed = _request(
            base,
            f"/v1/managed-projects/{project_id}",
            "viewer",
        )
        assert status == 200
        final = refreshed["project"]
        assert final["project_id"] == project_id
        assert final["current_workflow_id"] == workflow_id
        assert final["generation"] == 1
        assert final["status"] == "REVIEW_REQUIRED"
        assert final["current_workflow"]["status"] == "succeeded"
        assert final["usage"]["total_tokens"] == 1900

        latest = control.dashboard_store.latest_execution(job_key)
        assert latest["attempt"] == 2
        assert latest["worker_id"] == "worker-two"
        assert latest["status"] == "succeeded"

        recovered_events = [
            event
            for event in control.backend.events_after(0, 1000)
            if event["event_type"] == "job-recovered"
            and event["task_key"] == job_key
            and event["payload"].get("reason") == "worker_abandoned_after_ack"
        ]
        assert len(recovered_events) == 1
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
