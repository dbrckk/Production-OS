from __future__ import annotations

import json
import threading
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer

from production_os.api_auth import TokenAuthorizer, token_digest
from production_os.control_plane import ControlPlane, make_handler
from production_os.workflow_engine import WorkflowTaskSpec


def _auth():
    return TokenAuthorizer([
        {"name":"operator","role":"operator","sha256":token_digest("operator")},
        {"name":"worker","role":"worker","sha256":token_digest("worker")},
    ])


def _post(base, path, token, payload):
    request = urllib.request.Request(
        base + path,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=3) as response:
            raw = response.read()
            return response.status, json.loads(raw or b"{}")
    except urllib.error.HTTPError as exc:
        raw = exc.read()
        return exc.code, json.loads(raw or b"{}")


def _server(control):
    server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(control))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, f"http://127.0.0.1:{server.server_port}"


def test_paused_state_survives_control_plane_restart(tmp_path):
    database = str(tmp_path / "production.db")
    first = ControlPlane(database, authorizer=_auth())
    first.dashboard_control.set_worker_state(
        "worker-a",
        "paused",
        requested_by="operator:dashboard",
    )

    second = ControlPlane(database, authorizer=_auth())
    assert second.dashboard_control.worker_state("worker-a")["desired_state"] == "paused"


def test_release2_control_flow_pause_drain_cancel_retry_complete(tmp_path):
    control = ControlPlane(str(tmp_path / "production.db"), authorizer=_auth())
    control.workers.register("worker-a", ["python"], 1)
    workflow = control.workflows.create(
        name="release2-e2e",
        repository="dbrckk/example",
        tasks=[
            WorkflowTaskSpec(
                "task-a",
                "Controlled task",
                {"required_capabilities":["python"]},
                max_attempts=2,
            )
        ],
    )
    first = control.workflows.dispatch_ready(workflow["id"])[0]
    server, base = _server(control)
    try:
        status, paused = _post(
            base,
            "/v1/dashboard/workers/worker-a/control",
            "operator",
            {"action":"pause"},
        )
        assert status == 202
        assert paused["desired_state"] == "paused"

        status, _ = _post(
            base,
            "/v1/jobs/claim",
            "worker",
            {"worker_id":"worker-a","capabilities":["python"]},
        )
        assert status == 204

        status, resumed = _post(
            base,
            "/v1/dashboard/workers/worker-a/control",
            "operator",
            {"action":"resume"},
        )
        assert status == 202
        assert resumed["desired_state"] == "active"

        status, claimed = _post(
            base,
            "/v1/jobs/claim",
            "worker",
            {"worker_id":"worker-a","capabilities":["python"]},
        )
        assert status == 200
        assert claimed["job"]["key"] == first["key"]
        status, _ = _post(
            base,
            "/v1/jobs/ack",
            "worker",
            {"key":first["key"],"worker_id":"worker-a"},
        )
        assert status == 200

        status, draining = _post(
            base,
            "/v1/dashboard/workers/worker-a/control",
            "operator",
            {"action":"drain"},
        )
        assert status == 202
        assert draining["desired_state"] == "draining"
        assert control.queue.get(first["key"])["status"] == "acked"

        status, _ = _post(
            base,
            "/v1/jobs/claim",
            "worker",
            {"worker_id":"worker-a","capabilities":["python"]},
        )
        assert status == 204

        status, _ = _post(
            base,
            "/v1/dashboard/workers/worker-a/control",
            "operator",
            {"action":"resume"},
        )
        assert status == 202

        control.dashboard_store.start_execution(control.queue.get(first["key"]), "worker-a")
        status, requested = _post(
            base,
            "/v1/dashboard/workers/worker-a/control",
            "operator",
            {"action":"cancel-current","job_key":first["key"]},
        )
        assert status == 202
        assert requested["desired_state"] == "cancel_requested"

        status, _ = _post(
            base,
            "/v1/workers/heartbeat",
            "worker",
            {
                "worker_id":"worker-a",
                "active_tasks":1,
                "active_job_keys":[first["key"]],
                "job_control_states":{first["key"]:"cancel_requested"},
            },
        )
        assert status == 200
        assert control.queue.get(first["key"])["status"] == "cancelled"
        assert control.dashboard_store.latest_execution(first["key"])["status"] == "cancelled"

        status, retried = _post(
            base,
            "/v1/dashboard/workers/worker-a/control",
            "operator",
            {"action":"retry","job_key":first["key"]},
        )
        assert status == 201
        second = retried["job"]
        assert second["key"] != first["key"]

        status, claimed_retry = _post(
            base,
            "/v1/jobs/claim",
            "worker",
            {"worker_id":"worker-a","capabilities":["python"]},
        )
        assert status == 200
        assert claimed_retry["job"]["key"] == second["key"]
        status, _ = _post(
            base,
            "/v1/jobs/ack",
            "worker",
            {"key":second["key"],"worker_id":"worker-a"},
        )
        assert status == 200
        control.dashboard_store.start_execution(control.queue.get(second["key"]), "worker-a")

        status, completed = _post(
            base,
            "/v1/jobs/complete",
            "worker",
            {
                "key":second["key"],
                "worker_id":"worker-a",
                "result":{"status":"complete"},
            },
        )
        assert status == 200
        assert completed["job"]["status"] == "completed"

        current = control.workflows.get(workflow["id"])
        task = current["tasks"][0]
        assert task["status"] == "succeeded"
        assert task["attempts"] == 2
        assert current["status"] == "succeeded"
        assert control.queue.get(first["key"])["status"] == "cancelled"
        assert control.queue.get(second["key"])["status"] == "completed"
    finally:
        server.shutdown()
        server.server_close()
