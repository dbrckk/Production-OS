import json
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

from production_os.api_auth import TokenAuthorizer, token_digest
import production_os.control_plane as control_plane
from production_os.control_plane import ControlPlane, make_handler
from production_os.remote_worker import RemoteWorkerClient


def test_remote_worker_claim_ack_complete(tmp_path):
    auth=TokenAuthorizer([
        {"name":"op","role":"operator","sha256":token_digest("op")},
        {"name":"worker","role":"worker","sha256":token_digest("worker")},
    ])
    control=ControlPlane(str(tmp_path/"db.sqlite"),authorizer=auth)
    control.workers.register("w1",["python"],1)
    control.queue.enqueue({
        "handoff":{"repository":"o/a","task":"x"},
        "required_capabilities":["python"],
    })

    server=ThreadingHTTPServer(("127.0.0.1",0),make_handler(control))
    thread=threading.Thread(target=server.serve_forever,daemon=True)
    thread.start()
    try:
        client=RemoteWorkerClient(
            f"http://127.0.0.1:{server.server_port}",
            "worker",
            "w1",
            ["python"],
        )
        job=client.claim()
        assert job is not None
        assert client.ack(job.key)["status"]=="acked"
        assert client.complete(job.key)["status"]=="completed"
    finally:
        server.shutdown()
        server.server_close()

    # Exercise the actual HTTP transport: a redirect must neither forward
    # the worker credential nor turn a mutation into a successful GET.
    redirected_requests = []

    class Destination(BaseHTTPRequestHandler):
        def do_GET(self):
            redirected_requests.append(self.command)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"{}")

        do_POST = do_GET

        def log_message(self, *_args):
            pass

    destination = ThreadingHTTPServer(("127.0.0.1", 0), Destination)

    class Gateway(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.command == "POST":
                self.rfile.read(int(self.headers.get("Content-Length", "0")))
            if self.path.startswith("/redirect/"):
                self.send_response(int(self.path.rsplit("/", 1)[1]))
                self.send_header("Location", f"http://127.0.0.1:{destination.server_port}/received")
                self.end_headers()
                return
            success_bodies = {
                "/ok/html": b"<html>private-proxy-page</html>",
                "/ok/list": b"[]",
                "/ok/null": b"null",
                "/ok/invalid-encoding": b"\xff",
                "/ok/oversized": b"x" * 1_000_001,
                "/ok/truncated": b"{}",
                "/ok/slow": b"{}",
                "/slow-error": b"{}",
            }
            if self.path in success_bodies:
                body = success_bodies[self.path]
                self.send_response(502 if self.path == "/slow-error" else 200)
                self.send_header("Content-Length", str(len(body) + (10 if self.path == "/ok/truncated" else 0)))
                self.end_headers()
                if self.path in {"/ok/slow", "/slow-error"}:
                    time.sleep(0.1)
                try:
                    self.wfile.write(body)
                except (BrokenPipeError, ConnectionResetError):
                    pass
                return
            bodies = {
                "/html": b"<html>Bad Gateway</html>",
                "/empty": b"",
                "/list": b"[]",
                "/null": b"null",
                "/invalid-encoding": b"\xff",
                "/api": b'{"error":"temporarily unavailable"}',
            }
            self.send_response(502)
            self.end_headers()
            self.wfile.write(bodies[self.path])

        do_POST = do_GET

        def log_message(self, *_args):
            pass

    gateway = ThreadingHTTPServer(("127.0.0.1", 0), Gateway)
    threads = [threading.Thread(target=item.serve_forever, daemon=True)
               for item in (destination, gateway)]
    for thread in threads:
        thread.start()
    try:
        client = RemoteWorkerClient(f"http://127.0.0.1:{gateway.server_port}", "worker", "w1", [])
        for payload in (None, {"worker_id": "w1"}):
            for status in (301, 302, 303, 307, 308):
                with pytest.raises(RuntimeError, match=f"^control-plane HTTP {status}$"):
                    client._request(f"/redirect/{status}", payload)
        assert redirected_requests == []
        for path in ("/html", "/empty", "/list", "/null", "/invalid-encoding"):
            with pytest.raises(RuntimeError, match="^control-plane HTTP 502$"):
                client._request(path)
        with pytest.raises(RuntimeError, match="^control-plane HTTP 502: temporarily unavailable$"):
            client._request("/api")
        for path, reason in (
            ("/ok/html", "control-plane returned invalid JSON"),
            ("/ok/invalid-encoding", "control-plane returned invalid JSON"),
            ("/ok/list", "control-plane response must be a JSON object"),
            ("/ok/null", "control-plane response must be a JSON object"),
            ("/ok/oversized", "control-plane response too large"),
            ("/ok/truncated", "control-plane unavailable: IncompleteRead"),
        ):
            with pytest.raises(RuntimeError, match=f"^{reason}$") as error:
                client._request(path, {"worker_id": "w1"})
            assert "private-proxy-page" not in str(error.value)
        client.timeout = 0.02
        with pytest.raises(RuntimeError, match="^control-plane unavailable: TimeoutError$"):
            client._request("/ok/slow", {"worker_id": "w1"})
        with pytest.raises(RuntimeError, match="^control-plane HTTP 502$"):
            client._request("/slow-error", {"worker_id": "w1"})
    finally:
        for item in (gateway, destination):
            item.shutdown()
            item.server_close()
        for thread in threads:
            thread.join(timeout=2)


def test_remote_worker_detects_superseded_generation(tmp_path):
    auth=TokenAuthorizer([
        {"name":"worker","role":"worker","sha256":token_digest("worker")},
    ])
    control=ControlPlane(str(tmp_path/"db.sqlite"),authorizer=auth)
    control.workers.register("w1",["python"],1)

    original=control.workflows.create(
        name="pr-build",
        repository="o/a",
        metadata={
            "github_pr_number":12,
            "github_pr_head_sha":"sha-1",
            "github_pr_generation":1,
        },
        tasks=[
            control_plane.WorkflowTaskSpec(
                "tests",
                "Tests",
                {"required_capabilities":["python"]},
            ),
        ],
    )
    jobs=control.workflows.dispatch_ready(original["id"])
    assert len(jobs)==1

    server=ThreadingHTTPServer(
        ("127.0.0.1",0),
        make_handler(control),
    )
    thread=threading.Thread(target=server.serve_forever,daemon=True)
    thread.start()
    try:
        client=RemoteWorkerClient(
            f"http://127.0.0.1:{server.server_port}",
            "worker",
            "w1",
            ["python"],
        )
        job=client.claim()
        assert job is not None
        assert job.key==jobs[0]["key"]
        client.ack(job.key)

        generation,_=control.workflows.ensure_pr_generation(
            "o/a",
            12,
            "sha-2",
        )
        assert generation is not None
        assert generation["id"]!=original["id"]

        heartbeat=client.heartbeat(
            active_tasks=1,
            active_job_keys=[job.key],
        )
        assert heartbeat["stale_job_keys"]==[job.key]

        checkpoint=client.checkpoint_stale(
            job.key,
            "checkpoint://worker/w1/job-1",
        )
        assert checkpoint["status"]=="checkpointed"
        events=control.backend.events_after(0,1000)
        checkpoint_events=[
            event
            for event in events
            if event["event_type"]=="stale-job-checkpointed"
        ]
        assert len(checkpoint_events)==1
        assert checkpoint_events[0]["payload"][
            "checkpoint_ref"
        ]=="checkpoint://worker/w1/job-1"

        try:
            client.complete(job.key)
        except RuntimeError as exc:
            assert "stale workflow generation" in str(exc)
        else:
            raise AssertionError("expected stale-generation rejection")
    finally:
        server.shutdown()
        server.server_close()




def test_worker_heartbeat_catalog_drives_automatic_model_route(tmp_path):
    auth=TokenAuthorizer([
        {"name":"worker","role":"worker","sha256":token_digest("worker")},
    ])
    control=ControlPlane(str(tmp_path/"catalog.sqlite"),authorizer=auth)
    control.workers.register("w1",["code-implementation"],1)

    server=ThreadingHTTPServer(
        ("127.0.0.1",0),
        make_handler(control),
    )
    thread=threading.Thread(target=server.serve_forever,daemon=True)
    thread.start()
    try:
        client=RemoteWorkerClient(
            f"http://127.0.0.1:{server.server_port}",
            "worker",
            "w1",
            ["code-implementation"],
        )
        capacity={
            "model_candidates":[
                {
                    "provider":"local",
                    "model":"qwen-code",
                    "capabilities":["code-implementation"],
                    "free":True,
                    "priority":90,
                },
            ],
        }
        client.heartbeat(capacity=capacity)
        client.heartbeat(capacity=capacity)

        events=[
            event
            for event in control.backend.events_after(0,1000)
            if event["event_type"]=="worker-model-catalog"
        ]
        assert len(events)==1
        assert events[0]["task_key"]=="w1"
        assert events[0]["payload"]["model_candidates"][0]["model"]=="qwen-code"

        workflow=control.workflows.create(
            name="catalog-auto-route",
            repository="o/a",
            tasks=[
                control_plane.WorkflowTaskSpec(
                    "code",
                    "Code",
                    {
                        "handoff":{
                            "repository":"o/a",
                            "task":"Implement feature",
                            "required_capabilities":["code-implementation"],
                        },
                    },
                ),
            ],
        )
        job=control.workflows.dispatch_ready(workflow["id"],limit=1)[0]
        route=job["payload"]["handoff"]["model_route"]
        assert route["provider"]=="local"
        assert route["model"]=="qwen-code"
    finally:
        server.shutdown()
        server.server_close()


def test_worker_heartbeat_rejects_invalid_model_catalog(tmp_path):
    auth=TokenAuthorizer([
        {"name":"worker","role":"worker","sha256":token_digest("worker")},
    ])
    control=ControlPlane(str(tmp_path/"bad-catalog.sqlite"),authorizer=auth)
    control.workers.register("w1",["python"],1)

    server=ThreadingHTTPServer(
        ("127.0.0.1",0),
        make_handler(control),
    )
    thread=threading.Thread(target=server.serve_forever,daemon=True)
    thread.start()
    try:
        client=RemoteWorkerClient(
            f"http://127.0.0.1:{server.server_port}",
            "worker",
            "w1",
            ["python"],
        )
        try:
            client.heartbeat(capacity={
                "model_candidates":[
                    {
                        "provider":"",
                        "model":"bad",
                    },
                ],
            })
        except RuntimeError as exc:
            assert "provider and model" in str(exc)
        else:
            raise AssertionError("invalid model catalog must be rejected")
    finally:
        server.shutdown()
        server.server_close()
