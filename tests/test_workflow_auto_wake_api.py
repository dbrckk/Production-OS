"""End-to-end verification that workflow transitions wake bounded workers."""
from __future__ import annotations

import json
import threading
import urllib.request
from http.server import ThreadingHTTPServer

import pytest

from production_os.api_auth import TokenAuthorizer, token_digest
from production_os.control_plane import ControlPlane, make_handler


def _post(base, path, token, payload):
    request = urllib.request.Request(
        base + path,
        method="POST",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(request, timeout=6) as response:
        return json.loads(response.read())


@pytest.fixture
def running_control(tmp_path, monkeypatch):
    auth = TokenAuthorizer([
        {"name": "op", "role": "operator", "sha256": token_digest("op")},
        {"name": "worker", "role": "worker", "sha256": token_digest("worker")},
    ])
    control = ControlPlane(str(tmp_path / "wake-api.sqlite"), authorizer=auth)
    control.workers.register("github-actions-worker", ["python"], 1)
    # Keep the short-lived runner's registry heartbeat online, as it would be
    # briefly after its process exited.
    monkeypatch.setattr(control.workers, "detect_dead", lambda *a, **kw: [])
    dispatches = []
    monkeypatch.setattr(
        control.dashboard_control,
        "kick_worker",
        lambda worker_id: dispatches.append(worker_id) or {"status": "dispatched"},
    )
    server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(control))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield control, f"http://127.0.0.1:{server.server_port}", dispatches
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def _create_and_claim(base, *, task_attempts=2, downstream=False):
    tasks = [{
        "task_id": "build",
        "title": "Build",
        "payload": {"required_capabilities": ["python"]},
        "max_attempts": task_attempts,
    }]
    if downstream:
        tasks.append({
            "task_id": "review",
            "title": "Review",
            "dependencies": ["build"],
            "payload": {"required_capabilities": ["python"]},
        })
    created = _post(base, "/v1/workflows", "op", {
        "name": "retry-aware build",
        "repository": "dbrckk/example",
        "tasks": tasks,
    })
    workflow_id = created["workflow"]["id"]
    dispatched = _post(base, f"/v1/workflows/{workflow_id}/dispatch", "op", {})
    assert len(dispatched["jobs"]) == 1
    claimed = _post(base, "/v1/jobs/claim", "worker", {
        "worker_id": "github-actions-worker",
        "capabilities": ["python"],
    })
    job = claimed["job"]
    _post(base, "/v1/jobs/ack", "worker", {
        "worker_id": "github-actions-worker",
        "key": job["key"],
    })
    return workflow_id, job


def test_failure_automatically_wakes_next_workflow_attempt(running_control):
    control, base, dispatches = running_control
    workflow_id, job = _create_and_claim(base, task_attempts=2)
    result = _post(base, "/v1/jobs/fail", "worker", {
        "worker_id": "github-actions-worker",
        "key": job["key"],
        "reason": "continuation_limit: retry",
        "result": {"ai_dev_server_status": "continuation_limit"},
    })
    assert result["worker_wake"]["status"] == "dispatched"
    assert dispatches == ["automatic-launch"]
    workflow = control.workflows.get(workflow_id)
    task = next(t for t in workflow["tasks"] if t["task_id"] == "build")
    assert task["attempts"] == 2
    assert task["status"] == "queued"
    retry_job = control.queue.get(task["claimed_job_key"])
    assert retry_job["key"] != job["key"]
    assert retry_job["payload"]["workflow_attempt"] == 2


def test_downstream_task_wakes_after_success(running_control):
    control, base, dispatches = running_control
    workflow_id, job = _create_and_claim(base, task_attempts=1, downstream=True)
    result = _post(base, "/v1/jobs/complete", "worker", {
        "worker_id": "github-actions-worker",
        "key": job["key"],
        "result": {"ok": True},
    })
    assert result["worker_wake"]["status"] == "dispatched"
    assert dispatches == ["automatic-launch"]
    workflow = control.workflows.get(workflow_id)
    review = next(t for t in workflow["tasks"] if t["task_id"] == "review")
    assert review["status"] == "queued"
    assert control.queue.get(review["claimed_job_key"])["status"] == "queued"


def test_terminal_failure_without_new_work_does_not_dispatch(running_control):
    _control, base, dispatches = running_control
    _workflow_id, job = _create_and_claim(base, task_attempts=1)
    result = _post(base, "/v1/jobs/fail", "worker", {
        "worker_id": "github-actions-worker",
        "key": job["key"],
        "reason": "unrecoverable",
    })
    assert result["worker_wake"]["status"] == "not_needed"
    assert dispatches == []


def test_wake_dispatch_error_does_not_erase_durable_retry(running_control, monkeypatch):
    control, base, _dispatches = running_control
    monkeypatch.setattr(
        control.dashboard_control, "kick_worker",
        lambda worker_id: {"status": "failed", "error": "github_dispatch_failed"},
    )
    workflow_id, job = _create_and_claim(base, task_attempts=2)
    result = _post(base, "/v1/jobs/fail", "worker", {
        "worker_id": "github-actions-worker",
        "key": job["key"],
        "reason": "transient",
    })
    assert result["worker_wake"]["status"] == "failed"
    workflow = control.workflows.get(workflow_id)
    task = next(t for t in workflow["tasks"] if t["task_id"] == "build")
    assert task["status"] == "queued"
    assert control.queue.get(task["claimed_job_key"])["status"] == "queued"
