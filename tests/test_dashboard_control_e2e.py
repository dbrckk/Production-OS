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


class _FakeGitHub:
    def __init__(self):
        self.calls = []

    def dispatch_workflow(self, repository, workflow, *, ref="main", inputs=None):
        self.calls.append((repository, workflow, ref))


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

        github = _FakeGitHub()
        control.dashboard_control.github = github
        control.dashboard_control.actions_repository = "dbrckk/ai-dev-server"
        control.dashboard_control.actions_workflow = "production-os-actions-worker.yml"
        control.dashboard_control.actions_ref = "main"
        status, kicked = _post(
            base,
            "/v1/dashboard/workers/worker-a/control",
            "operator",
            {"action":"kick"},
        )
        assert status == 202
        assert kicked["status"] == "dispatched"
        assert github.calls == [(
            "dbrckk/ai-dev-server",
            "production-os-actions-worker.yml",
            "main",
        )]
    finally:
        server.shutdown()
        server.server_close()


def test_release3_audit_and_recovery_survive_control_plane_restart(tmp_path):
    database = str(tmp_path / "release3.db")
    first = ControlPlane(database, authorizer=_auth())
    first.workers.register("worker-a", ["python"], 1)
    job = first.queue.enqueue({
        "handoff":{"repository":"dbrckk/example","task":"recover after restart"},
        "required_capabilities":["python"],
    })
    assert first.queue.claim_key(job["key"], "worker-a") is not None
    with first.backend.transaction() as db:
        db.execute(
            "UPDATE jobs SET ack_deadline=? WHERE key=?",
            ("2000-01-01T00:00:00+00:00", job["key"]),
        )
    server, base = _server(first)
    try:
        status, _ = _post(
            base,
            "/v1/dashboard/workers/worker-a/control",
            "operator",
            {"action":"pause"},
        )
        assert status == 202
    finally:
        server.shutdown()
        server.server_close()

    second = ControlPlane(database, authorizer=_auth())
    persisted = second.dashboard_store.control_audit_events(limit=10)
    assert any(
        row["action"] == "pause"
        and row["worker_id"] == "worker-a"
        and row["outcome"] == "accepted"
        for row in persisted
    )

    server, base = _server(second)
    try:
        status, recovered = _post(
            base,
            "/v1/dashboard/workers/worker-a/control",
            "operator",
            {"action":"recover-stuck","job_key":job["key"]},
        )
        assert status == 200
        assert recovered["job"]["status"] == "queued"
        assert second.queue.get(job["key"])["claimed_by"] is None
        latest = second.dashboard_store.control_audit_events(limit=1)[0]
        assert latest["action"] == "recover-stuck"
        assert latest["job_key"] == job["key"]
        assert latest["outcome"] == "queued"
    finally:
        server.shutdown()
        server.server_close()


def test_release4_incident_lifecycle_survives_restart(tmp_path):
    database = str(tmp_path / "release4-incidents.db")
    first = ControlPlane(database, authorizer=_auth())
    first.queue.enqueue({
        "handoff":{"repository":"dbrckk/example","task":"wait for worker"},
        "required_capabilities":["python"],
    })
    incident = first.dashboard.incidents()["incidents"][0]
    assert incident["status"] == "open"
    first.dashboard_store.acknowledge_dashboard_incident(
        incident["id"],
        acknowledged_by="operator:operator",
    )

    second = ControlPlane(database, authorizer=_auth())
    persisted = second.dashboard_store.dashboard_incidents(limit=10)
    assert persisted[0]["id"] == incident["id"]
    assert persisted[0]["status"] == "acknowledged"
    assert persisted[0]["acknowledged_by"] == "operator:operator"

    second.workers.register("worker-a", ["python"], 1)
    reconciled = second.dashboard.incidents()["incidents"]
    resolved = next(row for row in reconciled if row["id"] == incident["id"])
    assert resolved["status"] == "resolved"
    assert resolved["resolved_at"] is not None

    third = ControlPlane(database, authorizer=_auth())
    final = third.dashboard_store.dashboard_incidents(limit=10)
    assert final[0]["id"] == incident["id"]
    assert final[0]["status"] == "resolved"


def test_managed_project_review_and_done_survive_restart(tmp_path):
    database = str(tmp_path / "managed-restart.db")
    first = ControlPlane(database, authorizer=_auth())
    project = first.managed_projects.create(
        repository="dbrckk/example",
        final_goal="Ship a verified release",
        token_budget=50000,
        agent_preference="codex",
    )
    first.workflows.record_result(
        project["workflow_id"],
        "goal",
        succeeded=True,
        result={"usage":{"total_tokens":4321}},
    )
    review = first.managed_projects.get(project["workflow_id"])
    assert review["state"] == "REVIEW_REQUIRED"
    assert review["usage"]["total_tokens"] == 4321

    second = ControlPlane(database, authorizer=_auth())
    persisted = second.managed_projects.get(project["workflow_id"])
    assert persisted["state"] == "REVIEW_REQUIRED"
    assert persisted["final_goal"] == "Ship a verified release"

    done = second.managed_projects.mark_done(
        project["workflow_id"],
        approved_by="operator:test",
    )
    assert done["state"] == "DONE"

    third = ControlPlane(database, authorizer=_auth())
    final = third.managed_projects.get(project["workflow_id"])
    assert final["state"] == "DONE"
    assert final["approved_by"] == "operator:test"
