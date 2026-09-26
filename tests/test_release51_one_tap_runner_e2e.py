from __future__ import annotations

import json
import sys
import threading
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer

import pytest

from production_os.api_auth import TokenAuthorizer, token_digest
from production_os.control_plane import ControlPlane, make_handler
from production_os.remote_worker import RemoteWorkerClient
from production_os.remote_worker_runner import RemoteWorkerRunner


def _auth():
    return TokenAuthorizer([
        {"name":"operator","role":"operator","sha256":token_digest("operator")},
        {"name":"viewer","role":"viewer","sha256":token_digest("viewer")},
        {"name":"runner","role":"worker","sha256":token_digest("runner")},
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
        return exc.code, json.loads(exc.read() or b"{}")


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
def test_release51_one_tap_launch_runs_through_real_runner_to_review_required(tmp_path):
    database = str(tmp_path / "one-tap-runner-success.sqlite")
    control = ControlPlane(database, authorizer=_auth())
    executor = tmp_path / "success_executor.py"
    executor.write_text(
        """
import json, sys
request = json.load(sys.stdin)
job = request["job"]["payload"]
handoff = job["payload"]["handoff"]
print(json.dumps({
    "status":"succeeded",
    "result":{
        "summary":"runner completed " + handoff["task"],
        "validation":{"status":"passed","tests":["unit","integration"]},
        "usage":{"total_tokens":2400,"runs":1,"agents":{"auto":1}},
        "commit_shas":["0123456789abcdef0123456789abcdef01234567"],
        "changed_files":["src/app.py","tests/test_app.py"],
    },
}))
""".strip(),
        encoding="utf-8",
    )
    server, thread, base = _server(control)
    try:
        status, launched = _request(
            base,
            "/v1/dashboard/launch",
            "operator",
            method="POST",
            body={
                "repository":"dbrckk/release51-success",
                "instruction":"Ship through the real remote runner.",
                "request_id":"release51-success",
            },
        )
        assert status == 201
        project_id = launched["project"]["project_id"]
        workflow_id = launched["project"]["current_workflow_id"]

        client = RemoteWorkerClient(base, "runner", "runner", [], timeout=5)
        runner = RemoteWorkerRunner(
            client,
            [sys.executable, str(executor)],
            heartbeat_interval_seconds=0.05,
            executor_timeout_seconds=5,
        )
        outcomes = runner.run(cycles=1, idle_sleep_seconds=0)

        assert len(outcomes) == 1
        assert outcomes[0]["status"] == "completed"

        status, detail = _request(
            base,
            f"/v1/dashboard/production-status?project_id={project_id}",
            "viewer",
        )
        assert status == 200
        assert detail["runtime"]["phase"] == "review_required"
        assert detail["project"]["project_id"] == project_id
        assert detail["project"]["current_workflow_id"] == workflow_id
        assert detail["project"]["generation"] == 1
        outcome = detail["project"]["outcome"]
        assert outcome["summary"] == (
            "runner completed Ship through the real remote runner."
        )
        assert outcome["validation_status"] == "passed"
        assert outcome["validation_tests"] == ["unit", "integration"]
        assert outcome["changed_file_count"] == 2
        assert outcome["commit_shas"] == [
            "0123456789abcdef0123456789abcdef01234567"
        ]

        status, inbox = _request(
            base,
            f"/v1/dashboard/productions?filter=review&q={project_id}",
            "viewer",
        )
        assert status == 200
        assert inbox["summary"]["matching"] == 1
        assert inbox["items"][0]["project_id"] == project_id
        assert inbox["items"][0]["runtime"]["phase"] == "review_required"
        assert inbox["items"][0]["outcome"]["validation_status"] == "passed"
    finally:
        _stop(server, thread)


@pytest.mark.e2e
def test_release51_executor_failure_surfaces_as_actionable_production(tmp_path):
    database = str(tmp_path / "one-tap-runner-failure.sqlite")
    control = ControlPlane(database, authorizer=_auth())
    executor = tmp_path / "failed_executor.py"
    executor.write_text(
        """
import json, sys
json.load(sys.stdin)
print(json.dumps({
    "status":"failed",
    "reason":"tests_failed",
    "result":{
        "summary":"integration tests failed",
        "validation":{"status":"failed","tests":["integration"]},
    },
}))
""".strip(),
        encoding="utf-8",
    )
    server, thread, base = _server(control)
    try:
        status, launched = _request(
            base,
            "/v1/dashboard/launch",
            "operator",
            method="POST",
            body={
                "repository":"dbrckk/release51-failure",
                "instruction":"Exercise executor failure propagation.",
                "request_id":"release51-failure",
            },
        )
        assert status == 201
        project_id = launched["project"]["project_id"]

        client = RemoteWorkerClient(base, "runner", "runner", [], timeout=5)
        runner = RemoteWorkerRunner(
            client,
            [sys.executable, str(executor)],
            heartbeat_interval_seconds=0.05,
            executor_timeout_seconds=5,
        )
        outcomes = runner.run(cycles=3, idle_sleep_seconds=0)

        # Managed Project implementation tasks have max_attempts=3. A worker
        # failure is automatically retried with a new job key until that
        # budget is exhausted; only then should operator attention be needed.
        assert len(outcomes) == 3
        assert len({row["job_key"] for row in outcomes}) == 3
        assert all(row["status"] == "failed" for row in outcomes)
        assert all(row["reason"] == "tests_failed" for row in outcomes)

        status, detail = _request(
            base,
            f"/v1/dashboard/production-status?project_id={project_id}",
            "viewer",
        )
        assert status == 200
        assert detail["runtime"]["phase"] == "needs_attention"
        assert detail["project"]["status"] == "NEEDS_ATTENTION"
        outcome = detail["project"]["outcome"]
        assert outcome["summary"] == "integration tests failed"
        assert outcome["validation_status"] == "failed"

        status, inbox = _request(
            base,
            f"/v1/dashboard/productions?filter=problems&q={project_id}",
            "viewer",
        )
        assert status == 200
        assert inbox["summary"]["matching"] == 1
        assert inbox["items"][0]["project_id"] == project_id
        assert inbox["items"][0]["runtime"]["phase"] == "needs_attention"

        status, attention = _request(
            base,
            "/v1/dashboard/attention?limit=50",
            "viewer",
        )
        assert status == 200
        item = next(
            row for row in attention["items"]
            if row.get("target_id") == project_id
        )
        assert item["kind"] == "validation_failed"
        assert item["summary"] == "integration tests failed"
        assert {action["name"] for action in item["actions"]} >= {
            "instructions",
            "verify",
        }
    finally:
        _stop(server, thread)
