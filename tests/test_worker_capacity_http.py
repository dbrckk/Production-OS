import json
import threading
import urllib.request
from http.server import ThreadingHTTPServer

from production_os.api_auth import TokenAuthorizer, token_digest
from production_os.control_plane import ControlPlane, make_handler


def post_json(url, token, payload):
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=3) as response:
        return response.status, json.loads(response.read() or b"{}")


def get_json(url, token):
    request = urllib.request.Request(
        url,
        headers={"Authorization": f"Bearer {token}"},
        method="GET",
    )
    with urllib.request.urlopen(request, timeout=3) as response:
        return response.status, json.loads(response.read() or b"{}")


def test_worker_heartbeat_exposes_omniroute_capacity(tmp_path):
    auth = TokenAuthorizer([
        {"name": "operator", "role": "operator", "sha256": token_digest("operator")},
        {"name": "worker", "role": "worker", "sha256": token_digest("worker")},
        {"name": "viewer", "role": "viewer", "sha256": token_digest("viewer")},
    ])
    control = ControlPlane(str(tmp_path / "db.sqlite"), authorizer=auth)
    server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(control))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{server.server_port}"
    try:
        post_json(
            base + "/v1/workers/register",
            "operator",
            {
                "worker_id": "ai-dev-server-1",
                "capabilities": ["software-development", "repo-analysis"],
                "max_concurrency": 1,
            },
        )
        status, heartbeat = post_json(
            base + "/v1/workers/heartbeat",
            "worker",
            {
                "worker_id": "ai-dev-server-1",
                "active_tasks": 0,
                "capacity": {
                    "source": "omniroute",
                    "status": "ok",
                    "authenticated_usage": True,
                    "steady_recurring_tokens": 1_500_000_000,
                    "used_this_month": 125_000_000,
                    "remaining_tokens": 1_375_000_000,
                    "catalog_updated_at": "2026-09-18",
                    "catalog_source": "free-tier-catalog",
                },
            },
        )
        assert status == 200
        assert heartbeat["worker"]["capacity"]["remaining_tokens"] == 1_375_000_000

        status, workers = get_json(base + "/v1/workers", "viewer")
        assert status == 200
        worker = next(
            item for item in workers["workers"]
            if item["worker_id"] == "ai-dev-server-1"
        )
        assert worker["capacity"]["source"] == "omniroute"
        assert worker["capacity"]["steady_recurring_tokens"] == 1_500_000_000
    finally:
        server.shutdown()
        server.server_close()
