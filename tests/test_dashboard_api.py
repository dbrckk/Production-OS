from __future__ import annotations

import json
import threading
from http.server import ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

from production_os.api_auth import TokenAuthorizer, token_digest
from production_os.control_plane import ControlPlane, make_handler


def _auth():
    return TokenAuthorizer([
        {"name":"operator","role":"operator","sha256":token_digest("operator-token")},
        {"name":"worker-a","role":"worker","sha256":token_digest("worker-a-token")},
        {"name":"worker-b","role":"worker","sha256":token_digest("worker-b-token")},
        {"name":"viewer","role":"viewer","sha256":token_digest("viewer-token")},
    ])


@pytest.fixture()
def running_control_plane(tmp_path):
    control = ControlPlane(str(tmp_path / "db.sqlite"), authorizer=_auth())
    server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(control))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}", control
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def api(base, path, token, body):
    data = json.dumps(body).encode()
    req = Request(base + path, data=data, method="POST", headers={
        "Content-Type":"application/json",
        **({"Authorization":f"Bearer {token}"} if token else {}),
    })
    try:
        with urlopen(req, timeout=3) as res:
            return res.status, json.loads(res.read())
    except HTTPError as exc:
        return exc.code, json.loads(exc.read())


def _owned_execution(control):
    control.workers.register("worker-a", ["python"], 1)
    job = control.queue.enqueue({"idempotency_key":"job-telemetry", "handoff":{"repository":"dbrckk/example","task":"ship"}, "workflow_id":"wf"})
    claimed = control.queue.claim_next("worker-a", capabilities=["python"])
    acked = control.queue.ack(claimed["key"], "worker-a")
    control.dashboard_store.start_execution(acked, "worker-a")
    return acked


def test_worker_can_publish_owned_job_telemetry(running_control_plane):
    base, control = running_control_plane
    job = _owned_execution(control)
    status, payload = api(base, f"/v1/jobs/{job['key']}/telemetry", "worker-a-token", {
        "worker_id":"worker-a", "stage":"implementation", "progress":42,
        "usage":{"total_tokens":1234},
        "logs":[{"level":"info","message":"Round 2 complete"}],
    })
    assert status == 200
    assert payload["execution"]["progress_percent"] == 42
    assert control.dashboard_store.logs_for_worker("worker-a")[0]["message"] == "Round 2 complete"


def test_other_worker_and_viewer_cannot_publish_telemetry(running_control_plane):
    base, control = running_control_plane
    job = _owned_execution(control)
    status, _ = api(base, f"/v1/jobs/{job['key']}/telemetry", "worker-b-token", {
        "worker_id":"worker-b", "progress":10,
    })
    assert status == 409
    status, _ = api(base, f"/v1/jobs/{job['key']}/telemetry", "viewer-token", {
        "worker_id":"worker-a", "progress":10,
    })
    assert status == 403
    status, _ = api(base, f"/v1/jobs/{job['key']}/telemetry", None, {
        "worker_id":"worker-a", "progress":10,
    })
    assert status == 401


def test_heartbeat_persists_only_authenticated_quota_values(running_control_plane):
    base, control = running_control_plane
    control.workers.register("worker-a", ["python"], 1)
    status, _ = api(base, "/v1/workers/heartbeat", "worker-a-token", {
        "worker_id":"worker-a",
        "capacity":{"source":"studio","status":"ok","authenticated_usage":True,
                    "used_this_month":100,"remaining_tokens":900},
    })
    assert status == 200
    quota = control.dashboard_store.latest_provider_quota_snapshots()[0]
    assert quota["remaining_value"] == 900
    assert quota["limit_value"] == 1000
    assert quota["source_status"] == "authenticated"
