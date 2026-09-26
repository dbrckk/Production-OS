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
def test_release45_server_inbox_tracks_multiple_productions_across_restart(tmp_path):
    database = str(tmp_path / "production-inbox-e2e.sqlite")
    first = ControlPlane(database, authorizer=_auth())
    server, thread, base = _server(first)

    try:
        project_ids = []
        for index in (1, 2):
            status, launched = _request(
                base,
                "/v1/dashboard/launch",
                "operator",
                method="POST",
                body={
                    "repository":f"dbrckk/inbox-e2e-{index}",
                    "instruction":f"Execute production {index}.",
                    "request_id":f"release45-inbox-{index}",
                },
            )
            assert status == 201
            project_ids.append(launched["project"]["project_id"])

        status, initial = _request(
            base,
            "/v1/dashboard/productions?limit=50",
            "viewer",
        )
        assert status == 200
        assert initial["summary"]["queued"] == 2
        assert {item["project_id"] for item in initial["items"]} == set(project_ids)

        status, _ = _request(
            base,
            "/v1/workers/register",
            "operator",
            method="POST",
            body={
                "worker_id":"worker",
                "capabilities":[],
                "max_concurrency":1,
            },
        )
        assert status == 200

        worker = RemoteWorkerClient(base, "worker", "worker", [], timeout=5)
        claimed = worker.claim()
        assert claimed is not None
        assert worker.ack(claimed.key)["status"] == "acked"
        status, _ = _request(
            base,
            f"/v1/jobs/{claimed.key}/telemetry",
            "worker",
            method="POST",
            body={
                "worker_id":"worker",
                "stage":"implementation",
                "progress":45,
                "usage":{"total_tokens":700},
            },
        )
        assert status == 200

        status, live = _request(
            base,
            "/v1/dashboard/productions?limit=50",
            "viewer",
        )
        assert status == 200
        assert live["summary"]["running"] == 1
        assert live["summary"]["queued"] == 1
        running = next(
            item for item in live["items"]
            if item["runtime"]["phase"] == "running"
        )
        assert running["runtime"]["worker_id"] == "worker"
        assert running["runtime"]["progress_percent"] == 45.0
        assert running["project_id"] in project_ids
    finally:
        _stop(server, thread)

    second = ControlPlane(database, authorizer=_auth())
    server, thread, base = _server(second)
    try:
        # A fresh browser/device only needs viewer access. No local last-project
        # state is required to reconstruct all current productions.
        status, restored = _request(
            base,
            "/v1/dashboard/productions?limit=50",
            "viewer",
        )
        assert status == 200
        assert restored["summary"]["running"] == 1
        assert restored["summary"]["queued"] == 1
        assert {item["project_id"] for item in restored["items"]} == set(project_ids)
        running = next(
            item for item in restored["items"]
            if item["runtime"]["phase"] == "running"
        )
        assert running["runtime"]["progress_percent"] == 45.0
        assert running["runtime"]["stage"] == "implementation"
    finally:
        _stop(server, thread)
