import json
import threading
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer

from production_os.api_auth import TokenAuthorizer, token_digest
from production_os.control_plane import ControlPlane, make_handler


def _auth():
    return TokenAuthorizer([
        {"name":"worker","role":"worker","sha256":token_digest("worker")},
        {"name":"viewer","role":"viewer","sha256":token_digest("viewer")},
    ])


def _server(control):
    server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(control))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread, f"http://127.0.0.1:{server.server_port}"


def _post(base, token, payload):
    req = urllib.request.Request(
        base + "/v1/jobs/availability",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization":"Bearer " + token,
            "Content-Type":"application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=3) as response:
            return response.status, json.loads(response.read() or b"{}")
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read() or b"{}")


def test_worker_availability_is_non_destructive_and_capability_aware(tmp_path):
    control = ControlPlane(str(tmp_path / "availability.sqlite"), authorizer=_auth())
    queued = control.queue.enqueue({
        "handoff":{
            "repository":"owner/repo",
            "task":"Validate mobile UI",
            "priority":50,
        },
        "required_capabilities":["python", "mobile-ui-validation"],
    })

    server, thread, base = _server(control)
    try:
        status, base_only = _post(
            base,
            "worker",
            {
                "worker_id":"github-actions-worker",
                "capabilities":["python"],
            },
        )
        assert status == 200
        assert base_only == {
            "schema_version":"production-os/job-availability/v1",
            "available":False,
            "compatible_jobs":0,
            "mobile_jobs":0,
            "browser_jobs":0,
            "worker_state":"active",
        }

        status, mobile = _post(
            base,
            "worker",
            {
                "worker_id":"github-actions-worker",
                "capabilities":["python", "mobile-ui-validation"],
            },
        )
        assert status == 200
        assert mobile["available"] is True
        assert mobile["compatible_jobs"] == 1
        assert mobile["mobile_jobs"] == 1
        assert mobile["browser_jobs"] == 0
        assert mobile["worker_state"] == "active"

        # Availability must never claim or mutate queued work.
        persisted = control.queue.get(queued["key"])
        assert persisted["status"] == "queued"
        assert persisted["claimed_by"] is None
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_worker_availability_skips_cancelled_and_stale_work(tmp_path):
    control = ControlPlane(str(tmp_path / "availability-filter.sqlite"), authorizer=_auth())
    cancelled = control.queue.enqueue({
        "handoff":{
            "repository":"owner/repo",
            "task":"Cancelled",
            "priority":20,
        },
        "required_capabilities":["python"],
    })
    control.dashboard_control.request_job_cancel(
        cancelled["key"],
        requested_by="operator:test",
    )

    server, thread, base = _server(control)
    try:
        status, payload = _post(
            base,
            "worker",
            {
                "worker_id":"worker-a",
                "capabilities":["python"],
            },
        )
        assert status == 200
        assert payload["available"] is False
        assert payload["compatible_jobs"] == 0
        assert control.queue.get(cancelled["key"])["status"] == "queued"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_worker_availability_respects_pause_and_drain(tmp_path):
    control = ControlPlane(str(tmp_path / "availability-pause.sqlite"), authorizer=_auth())
    control.workers.register("worker-a", ["python"], 1)
    control.queue.enqueue({
        "handoff":{
            "repository":"owner/repo",
            "task":"Queued",
            "priority":10,
        },
        "required_capabilities":["python"],
    })

    server, thread, base = _server(control)
    try:
        for state in ("paused", "draining"):
            control.dashboard_control.set_worker_state(
                "worker-a",
                state,
                requested_by="operator:test",
            )
            status, payload = _post(
                base,
                "worker",
                {
                    "worker_id":"worker-a",
                    "capabilities":["python"],
                },
            )
            assert status == 200
            assert payload["available"] is False
            assert payload["worker_state"] == state
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_worker_availability_requires_worker_auth_and_valid_shape(tmp_path):
    control = ControlPlane(str(tmp_path / "availability-auth.sqlite"), authorizer=_auth())
    server, thread, base = _server(control)
    try:
        status, payload = _post(
            base,
            "viewer",
            {
                "worker_id":"worker-a",
                "capabilities":["python"],
            },
        )
        assert status == 403
        assert payload["error"] == "forbidden"

        status, payload = _post(
            base,
            "worker",
            {
                "worker_id":"worker-a",
                "capabilities":"python",
            },
        )
        assert status == 400
        assert payload["error"] == "capabilities must be a list"

        status, payload = _post(
            base,
            "worker",
            {
                "worker_id":"worker-a",
                "capabilities":["python"],
                "unexpected":True,
            },
        )
        assert status == 400
        assert payload["error"] == "unknown availability fields"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
