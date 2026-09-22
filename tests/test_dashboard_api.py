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


def get_api(base, path, token):
    req = Request(base + path, method="GET", headers=(
        {"Authorization":f"Bearer {token}"} if token else {}
    ))
    try:
        with urlopen(req, timeout=3) as res:
            return res.status, json.loads(res.read())
    except HTTPError as exc:
        return exc.code, json.loads(exc.read())


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


def test_dashboard_overview_requires_viewer_and_has_stable_envelope(running_control_plane):
    base, _ = running_control_plane
    status, payload = get_api(base, "/v1/dashboard/overview?window=7d", "viewer-token")
    assert status == 200
    assert payload["schema_version"] == "production-os/dashboard-overview/v1"
    assert set(("workers","productions","usage","commits","performance","projects","errors")) <= set(payload)
    assert get_api(base, "/v1/dashboard/overview?window=7d", "worker-a-token")[0] == 403
    assert get_api(base, "/v1/dashboard/overview?window=7d", None)[0] == 401


def test_dashboard_rejects_invalid_window(running_control_plane):
    base, _ = running_control_plane
    assert get_api(base, "/v1/dashboard/overview?window=2h", "viewer-token")[0] == 400


def test_dashboard_worker_routes_and_unknown_worker(running_control_plane):
    base, control = running_control_plane
    control.workers.register("worker-a", ["python"], 1)
    assert get_api(base, "/v1/dashboard/workers", "viewer-token")[0] == 200
    status, payload = get_api(base, "/v1/dashboard/workers/worker-a", "viewer-token")
    assert status == 200 and payload["worker"]["worker_id"] == "worker-a"
    assert get_api(base, "/v1/dashboard/workers/missing", "viewer-token")[0] == 404
    status, payload = get_api(base, "/v1/dashboard/workers/worker-a/logs?limit=999999", "viewer-token")
    assert status == 200
    assert payload["limit"] == 500
    assert get_api(base, "/v1/dashboard/workers/worker-a/usage?window=30d", "viewer-token")[0] == 200


def test_dashboard_project_and_activity_routes(running_control_plane):
    base, control = running_control_plane
    assert get_api(base, "/v1/dashboard/projects", "viewer-token")[0] == 200
    assert get_api(base, "/v1/dashboard/projects/dbrckk/missing", "viewer-token")[0] == 404
    assert get_api(base, "/v1/dashboard/activity?limit=999999", "viewer-token")[0] == 200
    for suffix in ("progress","commits?window=30d","usage?window=30d","workflows","history"):
        status, _ = get_api(base, "/v1/dashboard/projects/dbrckk/missing/" + suffix, "viewer-token")
        assert status == 404
