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


def _stop(server, thread):
    server.shutdown()
    server.server_close()
    thread.join(timeout=2)


@pytest.mark.e2e
def test_release36_simultaneous_control_and_worker_restart_reconciles_two_projects(tmp_path):
    database = str(tmp_path / "simultaneous-restart.sqlite")
    first = ControlPlane(database, authorizer=_auth())
    server, thread, base = _server(first)

    try:
        status, registered = _request(
            base,
            "/v1/workers/register",
            "operator",
            method="POST",
            body={
                "worker_id":"worker-one",
                "capabilities":[],
                "max_concurrency":1,
            },
        )
        assert status == 200
        assert registered["reconciliation"] is None

        projects = []
        for index in (1, 2):
            status, launched = _request(
                base,
                "/v1/dashboard/launch",
                "operator",
                method="POST",
                body={
                    "repository":f"dbrckk/restart-concurrent-{index}",
                    "instruction":f"Complete concurrent production {index}.",
                },
            )
            assert status == 201
            projects.append(launched["project"])

        worker_one = RemoteWorkerClient(
            base,
            "worker-one",
            "worker-one",
            [],
            timeout=5,
        )
        first_claim = worker_one.claim()
        assert first_claim is not None
        abandoned_key = first_claim.key
        assert worker_one.ack(abandoned_key)["status"] == "acked"

        status, _ = _request(
            base,
            f"/v1/jobs/{abandoned_key}/telemetry",
            "worker-one",
            method="POST",
            body={
                "worker_id":"worker-one",
                "stage":"implementation",
                "progress":25,
                "usage":{"total_tokens":500},
            },
        )
        assert status == 200

        first_project_id = projects[0]["project_id"]
        second_project_id = projects[1]["project_id"]
        first_workflow_id = projects[0]["current_workflow_id"]
        second_workflow_id = projects[1]["current_workflow_id"]
    finally:
        _stop(server, thread)

    # Simulate both the Control Plane and worker process restarting. The new
    # worker process reports that it has no in-memory active jobs.
    second = ControlPlane(database, authorizer=_auth())
    server, thread, base = _server(second)

    try:
        status, reregistered = _request(
            base,
            "/v1/workers/register",
            "operator",
            method="POST",
            body={
                "worker_id":"worker-one",
                "capabilities":[],
                "max_concurrency":1,
                "active_job_keys":[],
            },
        )
        assert status == 200
        assert reregistered["worker"]["active_tasks"] == 0
        recovered = reregistered["reconciliation"]["recovered_jobs"]
        assert len(recovered) == 1
        assert recovered[0]["key"] == abandoned_key
        assert recovered[0]["previous_status"] == "acked"
        assert recovered[0]["status"] == "queued"

        old_execution = second.dashboard_store.latest_execution(abandoned_key)
        assert old_execution["status"] == "failed"
        assert old_execution["error_type"] == "worker_restarted"

        status, registered_two = _request(
            base,
            "/v1/workers/register",
            "operator",
            method="POST",
            body={
                "worker_id":"worker-two",
                "capabilities":[],
                "max_concurrency":1,
                "active_job_keys":[],
            },
        )
        assert status == 200
        assert registered_two["worker"]["active_tasks"] == 0

        restarted_one = RemoteWorkerClient(
            base,
            "worker-one",
            "worker-one",
            [],
            timeout=5,
        )
        worker_two = RemoteWorkerClient(
            base,
            "worker-two",
            "worker-two",
            [],
            timeout=5,
        )

        claim_one = restarted_one.claim()
        assert claim_one is not None
        restarted_one.heartbeat(
            active_tasks=1,
            active_job_keys=[claim_one.key],
        )

        claim_two = worker_two.claim()
        assert claim_two is not None
        assert claim_two.key != claim_one.key

        claimed_keys = {claim_one.key, claim_two.key}
        with second.backend.connect() as db:
            queued_rows = db.execute(
                "SELECT key FROM jobs WHERE repository IN (?, ?)",
                (
                    "dbrckk/restart-concurrent-1",
                    "dbrckk/restart-concurrent-2",
                ),
            ).fetchall()
        expected_keys = {row["key"] for row in queued_rows}
        assert claimed_keys == expected_keys

        assert restarted_one.ack(claim_one.key)["status"] == "acked"
        assert worker_two.ack(claim_two.key)["status"] == "acked"

        assert restarted_one.complete(
            claim_one.key,
            result_payload={
                "summary":"completed after simultaneous restart",
                "usage":{
                    "total_tokens":1200,
                    "runs":1,
                    "agents":{"auto":1},
                },
                "validation":{"status":"passed"},
            },
            duration_seconds=7.0,
        )["status"] == "completed"

        assert worker_two.complete(
            claim_two.key,
            result_payload={
                "summary":"completed concurrently after restart",
                "usage":{
                    "total_tokens":1300,
                    "runs":1,
                    "agents":{"auto":1},
                },
                "validation":{"status":"passed"},
            },
            duration_seconds=8.0,
        )["status"] == "completed"

        final_one = second.managed_projects.get(first_project_id)
        final_two = second.managed_projects.get(second_project_id)

        assert final_one["current_workflow_id"] == first_workflow_id
        assert final_two["current_workflow_id"] == second_workflow_id
        assert final_one["generation"] == 1
        assert final_two["generation"] == 1
        assert final_one["status"] == "REVIEW_REQUIRED"
        assert final_two["status"] == "REVIEW_REQUIRED"

        assert second.dashboard_store.execution_count(abandoned_key) == 2
        latest_abandoned = second.dashboard_store.latest_execution(abandoned_key)
        assert latest_abandoned["attempt"] == 2
        assert latest_abandoned["status"] == "succeeded"

        recovery_events = [
            event
            for event in second.backend.events_after(0, 2000)
            if event["event_type"] == "job-recovered"
            and event["task_key"] == abandoned_key
            and event["payload"].get("reason") == "worker_session_reconciled"
        ]
        assert len(recovery_events) == 1
    finally:
        _stop(server, thread)
