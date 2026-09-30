from __future__ import annotations

import json
import os
import sys
import threading
import time
from http.server import ThreadingHTTPServer

from production_os.api_auth import TokenAuthorizer, token_digest
from production_os.control_plane import ControlPlane, make_handler
from production_os.cli import _parse_args
from production_os.remote_worker import RemoteWorkerClient
from production_os.remote_worker_runner import RemoteWorkerRunner


def _server(control):
    server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(control))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread, f"http://127.0.0.1:{server.server_port}"


def _stop(server, thread):
    server.shutdown()
    server.server_close()
    thread.join(timeout=2)


def _auth():
    return TokenAuthorizer([
        {
            "name":"runner-1",
            "role":"worker",
            "sha256":token_digest("worker-secret"),
        },
        {
            "name":"other-worker",
            "role":"worker",
            "sha256":token_digest("other-secret"),
        },
    ])


def test_worker_session_self_registers_and_reconciles_previous_claim(tmp_path):
    control = ControlPlane(str(tmp_path / "session.sqlite"), authorizer=_auth())
    server, thread, base = _server(control)
    try:
        client = RemoteWorkerClient(
            base,
            "worker-secret",
            "runner-1",
            ["python"],
            timeout=5,
        )
        session = client.open_session(
            max_concurrency=1,
            active_job_keys=[],
        )
        assert session["worker"]["worker_id"] == "runner-1"
        assert session["worker"]["capabilities"] == ["python"]
        assert session["recovered_jobs"] == []

        queued = control.queue.enqueue({
            "handoff":{"repository":"dbrckk/runner","task":"execute"},
            "required_capabilities":["python"],
        })
        job = client.claim()
        assert job is not None
        assert job.key == queued["key"]
        assert client.ack(job.key)["status"] == "acked"

        restarted = RemoteWorkerClient(
            base,
            "worker-secret",
            "runner-1",
            ["python"],
            timeout=5,
        )
        reconciled = restarted.open_session(
            max_concurrency=1,
            active_job_keys=[],
        )
        assert reconciled["recovered_jobs"] == [{
            "key":job.key,
            "worker_id":"runner-1",
            "previous_status":"acked",
            "status":"queued",
        }]
        assert control.queue.get(job.key)["status"] == "queued"
    finally:
        _stop(server, thread)


def test_worker_session_rejects_token_identity_mismatch(tmp_path):
    control = ControlPlane(str(tmp_path / "identity.sqlite"), authorizer=_auth())
    server, thread, base = _server(control)
    try:
        client = RemoteWorkerClient(
            base,
            "other-secret",
            "runner-1",
            [],
            timeout=5,
        )
        try:
            client.open_session(max_concurrency=1, active_job_keys=[])
        except RuntimeError as exc:
            assert "worker identity mismatch" in str(exc)
        else:
            raise AssertionError("worker token must not open another worker session")
    finally:
        _stop(server, thread)


def test_remote_worker_runner_executes_json_executor_and_completes_job(tmp_path):
    control = ControlPlane(str(tmp_path / "runner.sqlite"), authorizer=_auth())
    queued = control.queue.enqueue({
        "handoff":{
            "repository":"dbrckk/runner-success",
            "task":"Implement runner protocol.",
        },
        "required_capabilities":["python"],
    })
    executor = tmp_path / "executor.py"
    executor.write_text(
        """
import json, sys
request = json.load(sys.stdin)
handoff = request["job"]["payload"]["payload"]["handoff"]
print(json.dumps({
    "status":"succeeded",
    "result":{
        "summary":"executed: " + handoff["task"],
        "validation":{"status":"passed","tests":["runner"]},
    },
}))
""".strip(),
        encoding="utf-8",
    )

    server, thread, base = _server(control)
    try:
        client = RemoteWorkerClient(
            base,
            "worker-secret",
            "runner-1",
            ["python"],
            timeout=5,
        )
        runner = RemoteWorkerRunner(
            client,
            [sys.executable, str(executor)],
            heartbeat_interval_seconds=0.1,
            executor_timeout_seconds=5,
        )

        outcomes = runner.run(cycles=1, idle_sleep_seconds=0)

        assert outcomes == [{
            "job_key":queued["key"],
            "status":"completed",
        }]
        assert control.queue.get(queued["key"])["status"] == "completed"
        execution = control.dashboard_store.latest_execution(queued["key"])
        assert execution["status"] == "succeeded"
        assert execution["result_summary"]["summary"] == (
            "executed: Implement runner protocol."
        )
        assert execution["result_summary"]["validation"]["status"] == "passed"
    finally:
        _stop(server, thread)


def test_remote_worker_runner_tolerates_transient_active_heartbeat_failure(tmp_path):
    control = ControlPlane(str(tmp_path / "heartbeat-retry.sqlite"), authorizer=_auth())
    queued = control.queue.enqueue({
        "handoff":{
            "repository":"dbrckk/runner-heartbeat",
            "task":"Survive one transient heartbeat failure.",
        },
        "required_capabilities":[],
    })
    executor = tmp_path / "slow_success.py"
    executor.write_text(
        """
import json, sys, time
json.load(sys.stdin)
time.sleep(0.15)
print(json.dumps({"status":"succeeded","result":{"summary":"ok"}}))
""".strip(),
        encoding="utf-8",
    )

    server, thread, base = _server(control)
    try:
        client = RemoteWorkerClient(
            base,
            "worker-secret",
            "runner-1",
            [],
            timeout=5,
        )
        runner = RemoteWorkerRunner(
            client,
            [sys.executable, str(executor)],
            heartbeat_interval_seconds=0.03,
            executor_timeout_seconds=3,
        )
        real_heartbeat = runner._heartbeat_active
        calls = {"count":0}

        def flaky_heartbeat(key):
            calls["count"] += 1
            if calls["count"] == 1:
                raise RuntimeError("transient control-plane hiccup")
            return real_heartbeat(key)

        runner._heartbeat_active = flaky_heartbeat
        outcomes = runner.run(cycles=1, idle_sleep_seconds=0)

        assert outcomes == [{"job_key":queued["key"], "status":"completed"}]
        assert calls["count"] >= 2
        assert control.queue.get(queued["key"])["status"] == "completed"
    finally:
        _stop(server, thread)


def test_remote_worker_runner_fails_job_on_invalid_executor_output(tmp_path):
    control = ControlPlane(str(tmp_path / "invalid-output.sqlite"), authorizer=_auth())
    queued = control.queue.enqueue({
        "handoff":{
            "repository":"dbrckk/runner-invalid",
            "task":"Return invalid output.",
        },
        "required_capabilities":[],
    })
    executor = tmp_path / "invalid.py"
    executor.write_text(
        "print('not-json')",
        encoding="utf-8",
    )

    server, thread, base = _server(control)
    try:
        client = RemoteWorkerClient(
            base,
            "worker-secret",
            "runner-1",
            [],
            timeout=5,
        )
        runner = RemoteWorkerRunner(
            client,
            [sys.executable, str(executor)],
            heartbeat_interval_seconds=0.1,
            executor_timeout_seconds=5,
        )

        outcomes = runner.run(cycles=1, idle_sleep_seconds=0)

        assert outcomes == [{
            "job_key":queued["key"],
            "status":"failed",
            "reason":"executor_invalid_output",
        }]
        assert control.queue.get(queued["key"])["status"] == "failed"
        execution = control.dashboard_store.latest_execution(queued["key"])
        assert execution["status"] == "failed"
        assert execution["error_message"] == "executor_invalid_output"
    finally:
        _stop(server, thread)

def test_remote_worker_runner_acknowledges_cancel_and_terminates_executor(tmp_path):
    control = ControlPlane(str(tmp_path / "cancel.sqlite"), authorizer=_auth())
    queued = control.queue.enqueue({
        "handoff":{
            "repository":"dbrckk/runner-cancel",
            "task":"Sleep until cancelled.",
        },
        "required_capabilities":[],
    })
    executor = tmp_path / "slow.py"
    executor.write_text(
        """
import json, sys, time
json.load(sys.stdin)
time.sleep(30)
print(json.dumps({"status":"succeeded","result":{"summary":"too late"}}))
""".strip(),
        encoding="utf-8",
    )

    server, server_thread, base = _server(control)
    outcomes = []
    try:
        client = RemoteWorkerClient(
            base,
            "worker-secret",
            "runner-1",
            [],
            timeout=5,
        )
        runner = RemoteWorkerRunner(
            client,
            [sys.executable, str(executor)],
            heartbeat_interval_seconds=0.05,
            executor_timeout_seconds=10,
        )
        worker_thread = threading.Thread(
            target=lambda: outcomes.extend(
                runner.run(cycles=1, idle_sleep_seconds=0)
            ),
            daemon=True,
        )
        worker_thread.start()

        deadline = time.time() + 5
        while time.time() < deadline:
            if control.queue.get(queued["key"])["status"] == "acked":
                break
            time.sleep(0.02)
        assert control.queue.get(queued["key"])["status"] == "acked"

        control.dashboard_control.request_job_cancel(
            queued["key"],
            requested_by="operator:test",
        )
        worker_thread.join(timeout=5)

        assert not worker_thread.is_alive()
        assert outcomes == [{
            "job_key":queued["key"],
            "status":"cancelled",
        }]
        assert control.queue.get(queued["key"])["status"] == "cancelled"
        state = control.dashboard_control.job_state(queued["key"])
        assert state["acknowledged_at"] is not None
        execution = control.dashboard_store.latest_execution(queued["key"])
        assert execution["status"] == "cancelled"
    finally:
        _stop(server, server_thread)

def test_remote_worker_runner_does_not_expose_worker_token_to_executor(
    tmp_path,
    monkeypatch,
):
    control = ControlPlane(str(tmp_path / "secret-env.sqlite"), authorizer=_auth())
    queued = control.queue.enqueue({
        "handoff":{
            "repository":"dbrckk/runner-secret",
            "task":"Do not leak the worker token.",
        },
        "required_capabilities":[],
    })
    monkeypatch.setenv("PRODUCTION_OS_WORKER_TOKEN", "worker-secret")
    executor = tmp_path / "env_check.py"
    executor.write_text(
        """
import json, os, sys
json.load(sys.stdin)
print(json.dumps({
    "status":"succeeded",
    "result":{
        "summary":"checked environment",
        "worker_token_visible":bool(os.getenv("PRODUCTION_OS_WORKER_TOKEN")),
    },
}))
""".strip(),
        encoding="utf-8",
    )

    server, thread, base = _server(control)
    try:
        client = RemoteWorkerClient(
            base,
            "worker-secret",
            "runner-1",
            [],
            timeout=5,
        )
        runner = RemoteWorkerRunner(
            client,
            [sys.executable, str(executor)],
            secret_env_names=["PRODUCTION_OS_WORKER_TOKEN"],
            heartbeat_interval_seconds=0.1,
            executor_timeout_seconds=5,
        )

        outcomes = runner.run(cycles=1, idle_sleep_seconds=0)

        assert outcomes[0]["status"] == "completed"
        execution = control.dashboard_store.latest_execution(queued["key"])
        assert execution["result_summary"]["worker_token_visible"] is False
    finally:
        _stop(server, thread)

def test_remote_worker_runner_honors_max_concurrency_with_full_active_set(tmp_path):
    control = ControlPlane(str(tmp_path / "concurrent-runner.sqlite"), authorizer=_auth())
    queued = [
        control.queue.enqueue({
            "handoff":{
                "repository":f"dbrckk/runner-concurrent-{index}",
                "task":f"Concurrent task {index}.",
            },
            "required_capabilities":[],
        })
        for index in (1, 2)
    ]
    markers = tmp_path / "markers"
    markers.mkdir()
    executor = tmp_path / "concurrent_executor.py"
    executor.write_text(
        f"""
import json, pathlib, sys, time
request = json.load(sys.stdin)
key = request["job"]["key"]
markers = pathlib.Path({str(markers)!r})
(markers / (key + ".started")).write_text("started", encoding="utf-8")
deadline = time.time() + 1.5
while len(list(markers.glob("*.started"))) < 2 and time.time() < deadline:
    time.sleep(0.02)
if len(list(markers.glob("*.started"))) < 2:
    raise SystemExit(7)
time.sleep(0.25)
print(json.dumps({{
    "status":"succeeded",
    "result":{{"summary":"concurrent executor completed"}},
}}))
""".strip(),
        encoding="utf-8",
    )

    server, server_thread, base = _server(control)
    outcomes = []
    try:
        client = RemoteWorkerClient(
            base,
            "worker-secret",
            "runner-1",
            [],
            timeout=5,
        )
        runner = RemoteWorkerRunner(
            client,
            [sys.executable, str(executor)],
            max_concurrency=2,
            heartbeat_interval_seconds=0.05,
            executor_timeout_seconds=2,
        )
        worker_thread = threading.Thread(
            target=lambda: outcomes.extend(
                runner.run(cycles=1, idle_sleep_seconds=0)
            ),
            daemon=True,
        )
        worker_thread.start()

        deadline = time.time() + 1.0
        saw_two_markers = False
        saw_two_active = False
        while time.time() < deadline:
            if len(list(markers.glob("*.started"))) >= 2:
                saw_two_markers = True
            control.workers.load()
            worker = control.workers.workers.get("runner-1")
            if worker is not None and int(worker.active_tasks) == 2:
                saw_two_active = True
            if saw_two_markers and saw_two_active:
                break
            time.sleep(0.02)

        worker_thread.join(timeout=5)

        assert saw_two_markers is True
        assert saw_two_active is True
        assert not worker_thread.is_alive()
        assert len(outcomes) == 2
        assert {row["job_key"] for row in outcomes} == {
            row["key"] for row in queued
        }
        assert all(row["status"] == "completed" for row in outcomes)
        assert all(control.queue.get(row["key"])["status"] == "completed" for row in queued)

        control.workers.load()
        assert control.workers.workers["runner-1"].active_tasks == 0
    finally:
        _stop(server, server_thread)

def test_remote_worker_runner_graceful_stop_terminates_children_and_restart_recovers(
    tmp_path,
):
    control = ControlPlane(
        str(tmp_path / "graceful-stop.sqlite"),
        authorizer=_auth(),
    )
    queued = [
        control.queue.enqueue({
            "handoff":{
                "repository":f"dbrckk/runner-stop-{index}",
                "task":f"Long running task {index}.",
            },
            "required_capabilities":[],
        })
        for index in (1, 2)
    ]
    markers = tmp_path / "stop-markers"
    markers.mkdir()
    executor = tmp_path / "stop_executor.py"
    executor.write_text(
        f"""
import json, os, pathlib, sys, time
request = json.load(sys.stdin)
key = request["job"]["key"]
markers = pathlib.Path({str(markers)!r})
(markers / (key + ".pid")).write_text(str(os.getpid()), encoding="utf-8")
time.sleep(30)
print(json.dumps({{"status":"succeeded","result":{{"summary":"too late"}}}}))
""".strip(),
        encoding="utf-8",
    )

    server, server_thread, base = _server(control)
    outcomes = []
    runner_thread = None
    runner = None
    try:
        client = RemoteWorkerClient(
            base,
            "worker-secret",
            "runner-1",
            [],
            timeout=5,
        )
        runner = RemoteWorkerRunner(
            client,
            [sys.executable, str(executor)],
            max_concurrency=2,
            heartbeat_interval_seconds=0.05,
            executor_timeout_seconds=60,
        )
        runner_thread = threading.Thread(
            target=lambda: outcomes.extend(
                runner.run(cycles=0, idle_sleep_seconds=0.02)
            ),
            daemon=True,
        )
        runner_thread.start()

        deadline = time.time() + 3
        while time.time() < deadline:
            if len(list(markers.glob("*.pid"))) >= 2:
                break
            time.sleep(0.02)
        assert len(list(markers.glob("*.pid"))) == 2
        assert all(
            control.queue.get(row["key"])["status"] == "acked"
            for row in queued
        )

        runner.request_stop()
        runner_thread.join(timeout=5)

        assert not runner_thread.is_alive()
        assert len(outcomes) == 2
        assert {row["job_key"] for row in outcomes} == {
            row["key"] for row in queued
        }
        assert all(row["status"] == "abandoned" for row in outcomes)
        assert all(row["reason"] == "worker_shutdown" for row in outcomes)

        for marker in markers.glob("*.pid"):
            pid = int(marker.read_text(encoding="utf-8"))
            try:
                os.kill(pid, 0)
            except ProcessLookupError:
                pass
            else:
                raise AssertionError(f"executor process {pid} survived runner stop")

        # The stopped worker never lies by marking unfinished work failed or
        # completed. A fresh session for the same worker is authoritative and
        # immediately recovers both abandoned ACKed jobs.
        assert all(
            control.queue.get(row["key"])["status"] == "acked"
            for row in queued
        )
        restarted = RemoteWorkerClient(
            base,
            "worker-secret",
            "runner-1",
            [],
            timeout=5,
        )
        session = restarted.open_session(
            max_concurrency=2,
            active_job_keys=[],
        )
        recovered = session["recovered_jobs"]
        assert {row["key"] for row in recovered} == {
            row["key"] for row in queued
        }
        assert all(row["previous_status"] == "acked" for row in recovered)
        assert all(row["status"] == "queued" for row in recovered)
        assert all(
            control.queue.get(row["key"])["status"] == "queued"
            for row in queued
        )
    finally:
        if runner_thread is not None and runner_thread.is_alive():
            for row in queued:
                try:
                    control.dashboard_control.request_job_cancel(
                        row["key"],
                        requested_by="operator:test-cleanup",
                    )
                except (KeyError, RuntimeError):
                    pass
            runner_thread.join(timeout=5)
        _stop(server, server_thread)




def test_remote_worker_runner_executes_in_configured_isolated_worktree(tmp_path):
    import pathlib
    import subprocess

    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", str(repo)], check=True, stdout=subprocess.PIPE)
    subprocess.run(
        ["git", "-C", str(repo), "config", "user.email", "test@example.invalid"],
        check=True,
    )
    subprocess.run(
        ["git", "-C", str(repo), "config", "user.name", "Production OS Test"],
        check=True,
    )
    (repo / "README.md").write_text("base\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(repo), "add", "README.md"], check=True)
    subprocess.run(
        ["git", "-C", str(repo), "commit", "-m", "base"],
        check=True,
        stdout=subprocess.PIPE,
    )
    base_sha = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD"],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    ).stdout.strip()

    control = ControlPlane(str(tmp_path / "worktree-runner.sqlite"), authorizer=_auth())
    queued = control.queue.enqueue({
        "handoff":{
            "repository":"dbrckk/worktree-target",
            "task":"Write inside the isolated worktree.",
            "isolation":{
                "schema_version":"production-os/git-worktree-isolation/v1",
                "mode":"git-worktree",
                "repository":"dbrckk/worktree-target",
                "workflow_id":"wf-1",
                "task_id":"implementation-code",
                "attempt":1,
                "branch":"production-os/wf-1/implementation-code-a1-test",
                "workspace_key":"implementation-code-test",
                "base_ref":base_sha,
                "integration_target":False,
                "requirements":{
                    "exclusive_workspace":True,
                    "no_shared_working_tree_writes":True,
                    "commit_changes_before_success":True,
                    "report_commit_shas":True,
                },
            },
        },
        "required_capabilities":[],
    })
    executor = tmp_path / "worktree_executor.py"
    executor.write_text(
        """
import json, os, pathlib, subprocess, sys
request = json.load(sys.stdin)
cwd = pathlib.Path.cwd()
(cwd / "agent.txt").write_text("isolated", encoding="utf-8")
subprocess.run(["git", "add", "."], check=True)
subprocess.run([
    "git",
    "-c", "user.name=Executor Test",
    "-c", "user.email=executor@example.invalid",
    "commit", "-m", "agent change",
], check=True, stdout=subprocess.PIPE)
print(json.dumps({
    "status":"succeeded",
    "result":{
        "summary":"isolated",
        "cwd":str(cwd),
        "env_worktree":os.environ.get("PRODUCTION_OS_WORKTREE"),
        "branch":os.environ.get("PRODUCTION_OS_WORKTREE_BRANCH"),
        "workspace":request.get("executor_workspace"),
    },
}))
""".strip(),
        encoding="utf-8",
    )

    server, thread, base = _server(control)
    try:
        client = RemoteWorkerClient(
            base,
            "worker-secret",
            "runner-1",
            [],
            timeout=5,
        )
        runner = RemoteWorkerRunner(
            client,
            [sys.executable, str(executor)],
            repository_roots={
                "dbrckk/worktree-target":str(repo),
            },
            worktree_root=str(tmp_path / "worktrees"),
            heartbeat_interval_seconds=0.1,
            executor_timeout_seconds=5,
        )

        outcomes = runner.run(cycles=1, idle_sleep_seconds=0)

        assert outcomes == [{
            "job_key":queued["key"],
            "status":"completed",
        }]
        execution = control.dashboard_store.latest_execution(queued["key"])
        result = execution["result_summary"]
        assert result["cwd"] == result["env_worktree"]
        assert result["workspace"]["branch"] == (
            "production-os/wf-1/implementation-code-a1-test"
        )
        assert result["workspace"]["created"] is True
        assert (repo / "agent.txt").exists() is False
        assert pathlib.Path(result["cwd"]).exists() is False
        branch_file = subprocess.run(
            [
                "git", "-C", str(repo), "show",
                f"{result['branch']}:agent.txt",
            ],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
        ).stdout
        assert branch_file == "isolated"
        assert result["executor_git"]["clean"] is True
        assert result["executor_git"]["base_is_ancestor"] is True
        assert result["changed_files"] == ["agent.txt"]
        assert result["commit_shas"][-1] == result["executor_git"]["final_sha"]
    finally:
        _stop(server, thread)



def test_remote_worker_runner_preintegrates_multi_parent_commits(tmp_path):
    import pathlib
    import subprocess

    repo = tmp_path / "integration-repo"
    repo.mkdir()
    subprocess.run(["git", "init", str(repo)], check=True, stdout=subprocess.PIPE)
    subprocess.run(
        ["git", "-C", str(repo), "config", "user.email", "test@example.invalid"],
        check=True,
    )
    subprocess.run(
        ["git", "-C", str(repo), "config", "user.name", "Production OS Test"],
        check=True,
    )
    (repo / "README.md").write_text("base\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(repo), "add", "."], check=True)
    subprocess.run(
        ["git", "-C", str(repo), "commit", "-m", "base"],
        check=True,
        stdout=subprocess.PIPE,
    )
    base_branch = subprocess.run(
        ["git", "-C", str(repo), "branch", "--show-current"],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    ).stdout.strip()
    base_sha = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD"],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    ).stdout.strip()

    subprocess.run(
        [
            "git", "-C", str(repo), "checkout", "-b",
            "production-os/wf-integration/agent-a",
        ],
        check=True,
        stdout=subprocess.PIPE,
    )
    (repo / "a.txt").write_text("a\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(repo), "add", "."], check=True)
    subprocess.run(
        ["git", "-C", str(repo), "commit", "-m", "agent a"],
        check=True,
        stdout=subprocess.PIPE,
    )
    commit_a = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD"],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    ).stdout.strip()

    subprocess.run(
        ["git", "-C", str(repo), "checkout", base_branch],
        check=True,
        stdout=subprocess.PIPE,
    )
    subprocess.run(
        [
            "git", "-C", str(repo), "checkout", "-b",
            "production-os/wf-integration/agent-b",
        ],
        check=True,
        stdout=subprocess.PIPE,
    )
    (repo / "b.txt").write_text("b\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(repo), "add", "."], check=True)
    subprocess.run(
        ["git", "-C", str(repo), "commit", "-m", "agent b"],
        check=True,
        stdout=subprocess.PIPE,
    )
    commit_b = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD"],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    ).stdout.strip()
    subprocess.run(
        ["git", "-C", str(repo), "checkout", base_branch],
        check=True,
        stdout=subprocess.PIPE,
    )

    control = ControlPlane(
        str(tmp_path / "integration-preflight.sqlite"),
        authorizer=_auth(),
    )
    queued = control.queue.enqueue({
        "handoff":{
            "repository":"dbrckk/integration-target",
            "task":"Integrate agent branches.",
            "upstream_context":[
                {"task_id":"agent-a", "commit_shas":[commit_a]},
                {"task_id":"agent-b", "commit_shas":[commit_b]},
            ],
            "isolation":{
                "schema_version":"production-os/git-worktree-isolation/v1",
                "mode":"git-worktree",
                "repository":"dbrckk/integration-target",
                "workflow_id":"wf-integration",
                "task_id":"integration",
                "attempt":1,
                "branch":"production-os/wf-integration/integration-a1-test",
                "workspace_key":"integration-preflight-test",
                "base_ref":base_sha,
                "integration_target":True,
                "requirements":{
                    "exclusive_workspace":True,
                    "no_shared_working_tree_writes":True,
                    "commit_changes_before_success":True,
                    "report_commit_shas":True,
                },
            },
        },
        "required_capabilities":[],
    })
    executor = tmp_path / "integration_executor.py"
    executor.write_text(
        """
import json, pathlib, sys
request = json.load(sys.stdin)
cwd = pathlib.Path.cwd()
preflight = request.get("integration_preflight") or {}
ok = (
    preflight.get("status") == "integrated"
    and (cwd / "a.txt").read_text(encoding="utf-8") == "a\\n"
    and (cwd / "b.txt").read_text(encoding="utf-8") == "b\\n"
)
print(json.dumps({
    "status":"succeeded" if ok else "failed",
    "reason":None if ok else "preflight_missing",
    "result":{
        "summary":"preintegrated" if ok else "not preintegrated",
        "preflight":preflight,
    },
}))
""".strip(),
        encoding="utf-8",
    )

    server, thread, base = _server(control)
    try:
        client = RemoteWorkerClient(
            base,
            "worker-secret",
            "runner-1",
            [],
            timeout=5,
        )
        runner = RemoteWorkerRunner(
            client,
            [sys.executable, str(executor)],
            repository_roots={
                "dbrckk/integration-target":str(repo),
            },
            worktree_root=str(tmp_path / "worktrees"),
            heartbeat_interval_seconds=0.1,
            executor_timeout_seconds=5,
        )

        outcomes = runner.run(cycles=1, idle_sleep_seconds=0)

        assert outcomes == [{
            "job_key":queued["key"],
            "status":"completed",
        }]
        execution = control.dashboard_store.latest_execution(queued["key"])
        preflight = execution["result_summary"]["preflight"]
        assert preflight["status"] == "integrated"
        assert preflight["applied_commits"] == [commit_a, commit_b]
        assert len(preflight["final_sha"]) == 40
        branches = subprocess.run(
            [
                "git", "-C", str(repo), "branch",
                "--format=%(refname:short)",
            ],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
        ).stdout.splitlines()
        assert "production-os/wf-integration/agent-a" not in branches
        assert "production-os/wf-integration/agent-b" not in branches
        assert (
            "production-os/wf-integration/integration-a1-test"
            in branches
        )
    finally:
        _stop(server, thread)



def test_remote_worker_runner_rejects_success_with_dirty_worktree(tmp_path):
    import subprocess

    repo = tmp_path / "dirty-repo"
    repo.mkdir()
    subprocess.run(["git", "init", str(repo)], check=True, stdout=subprocess.PIPE)
    subprocess.run(
        ["git", "-C", str(repo), "config", "user.email", "test@example.invalid"],
        check=True,
    )
    subprocess.run(
        ["git", "-C", str(repo), "config", "user.name", "Production OS Test"],
        check=True,
    )
    (repo / "README.md").write_text("base\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(repo), "add", "."], check=True)
    subprocess.run(
        ["git", "-C", str(repo), "commit", "-m", "base"],
        check=True,
        stdout=subprocess.PIPE,
    )
    base_sha = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD"],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    ).stdout.strip()

    control = ControlPlane(
        str(tmp_path / "dirty-worktree.sqlite"),
        authorizer=_auth(),
    )
    queued = control.queue.enqueue({
        "handoff":{
            "repository":"dbrckk/dirty-target",
            "task":"Leave a dirty worktree.",
            "isolation":{
                "schema_version":"production-os/git-worktree-isolation/v1",
                "mode":"git-worktree",
                "repository":"dbrckk/dirty-target",
                "workflow_id":"wf-dirty",
                "task_id":"code",
                "attempt":1,
                "branch":"production-os/wf-dirty/code-a1-test",
                "workspace_key":"dirty-result-test",
                "base_ref":base_sha,
                "integration_target":False,
                "requirements":{
                    "exclusive_workspace":True,
                    "no_shared_working_tree_writes":True,
                    "commit_changes_before_success":True,
                    "report_commit_shas":True,
                },
            },
        },
        "required_capabilities":[],
    })
    executor = tmp_path / "dirty_executor.py"
    executor.write_text(
        """
import json, pathlib, sys
json.load(sys.stdin)
(pathlib.Path.cwd() / "uncommitted.txt").write_text(
    "dirty", encoding="utf-8"
)
print(json.dumps({
    "status":"succeeded",
    "result":{"summary":"claimed success"},
}))
""".strip(),
        encoding="utf-8",
    )

    server, thread, base = _server(control)
    try:
        client = RemoteWorkerClient(
            base,
            "worker-secret",
            "runner-1",
            [],
            timeout=5,
        )
        runner = RemoteWorkerRunner(
            client,
            [sys.executable, str(executor)],
            repository_roots={
                "dbrckk/dirty-target":str(repo),
            },
            worktree_root=str(tmp_path / "worktrees"),
            heartbeat_interval_seconds=0.1,
            executor_timeout_seconds=5,
        )

        outcomes = runner.run(cycles=1, idle_sleep_seconds=0)

        assert outcomes == [{
            "job_key":queued["key"],
            "status":"failed",
            "reason":"executor_worktree_dirty",
        }]
        assert control.queue.get(queued["key"])["status"] == "failed"
        execution = control.dashboard_store.latest_execution(queued["key"])
        assert execution["error_message"] == "executor_worktree_dirty"
        assert execution["result_summary"]["executor_git"]["clean"] is False
    finally:
        _stop(server, thread)



def test_remote_worker_run_defaults_executor_mode_to_auto():
    args = _parse_args([
        "remote-worker-run",
        "--url", "http://example.invalid",
        "--worker-id", "worker-a",
    ])

    assert args.executor_mode == "auto"
    assert args.executor_command == ""


def test_remote_worker_run_allows_auto_without_executor_command():
    args = _parse_args([
        "remote-worker-run",
        "--url", "http://example.invalid",
        "--worker-id", "worker-a",
        "--executor-mode", "auto",
    ])

    runner = RemoteWorkerRunner(
        object(),
        [],
        executor_mode=args.executor_mode,
    )

    assert runner.executor_mode == "auto"
    assert runner.executor_command == []


def test_remote_worker_run_rejects_external_mode_without_executor_command():
    args = _parse_args([
        "remote-worker-run",
        "--url", "http://example.invalid",
        "--worker-id", "worker-a",
        "--executor-mode", "external",
    ])

    try:
        RemoteWorkerRunner(
            object(),
            [],
            executor_mode=args.executor_mode,
        )
    except ValueError as exc:
        assert "executor command is required" in str(exc)
    else:
        raise AssertionError("external mode must require an executor command")


def test_remote_worker_run_accepts_native_without_executor_command():
    args = _parse_args([
        "remote-worker-run",
        "--url", "http://example.invalid",
        "--worker-id", "worker-a",
        "--executor-mode", "native",
    ])

    runner = RemoteWorkerRunner(
        object(),
        None,
        executor_mode=args.executor_mode,
    )

    assert runner.executor_mode == "native"
    assert runner.executor_command == []



def _native_browser_handoff_for_runner():
    return {
        "repository":"dbrckk/native-browser",
        "task":"Inspect the frontend in the browser.",
        "tool_contracts":{
            "browser_computer":{
                "schema_version":"production-os/browser-computer-tool/v1",
            },
        },
        "browser":{
            "config":{
                "schema_version":"production-os/browser-computer-loop/v1",
                "allowed_hosts":["example.com"],
                "persist_session":False,
                "allow_private_network":False,
                "max_turns":1,
            },
            "turns":[{
                "schema_version":"production-os/browser-computer-turn/v1",
                "turn_id":"observe",
                "actions":[{"action":"snapshot","name":"page"}],
            }],
        },
    }


def test_auto_mode_prefers_native_browser_over_external_executor(
    tmp_path,
    monkeypatch,
):
    control = ControlPlane(str(tmp_path / "native-preferred.sqlite"), authorizer=_auth())
    queued = control.queue.enqueue({
        "handoff":_native_browser_handoff_for_runner(),
        "required_capabilities":[],
    })
    marker = tmp_path / "external-ran"
    executor = tmp_path / "external.py"
    executor.write_text(
        f"""
import json, pathlib, sys
json.load(sys.stdin)
pathlib.Path({str(marker)!r}).write_text("ran", encoding="utf-8")
print(json.dumps({{"status":"succeeded","result":{{"summary":"external"}}}}))
""".strip(),
        encoding="utf-8",
    )
    calls = []

    def fake_native(context):
        calls.append(context.job_key)
        return {"status":"succeeded","result":{"summary":"native"}}

    monkeypatch.setattr(
        "production_os.remote_worker_runner.execute_native",
        fake_native,
    )

    server, thread, base = _server(control)
    try:
        client = RemoteWorkerClient(base, "worker-secret", "runner-1", [], timeout=5)
        runner = RemoteWorkerRunner(
            client,
            [sys.executable, str(executor)],
            executor_mode="auto",
            heartbeat_interval_seconds=0.05,
            executor_timeout_seconds=5,
        )

        outcomes = runner.run(cycles=1, idle_sleep_seconds=0)

        assert outcomes == [{"job_key":queued["key"], "status":"completed"}]
        assert calls == [queued["key"]]
        assert marker.exists() is False
    finally:
        _stop(server, thread)


def test_auto_mode_falls_back_to_external_when_native_is_unsupported(tmp_path):
    control = ControlPlane(str(tmp_path / "native-fallback.sqlite"), authorizer=_auth())
    queued = control.queue.enqueue({
        "handoff":{
            "repository":"dbrckk/external-only",
            "task":"Run an unsupported native task.",
        },
        "required_capabilities":[],
    })
    marker = tmp_path / "external-ran"
    executor = tmp_path / "external.py"
    executor.write_text(
        f"""
import json, pathlib, sys
json.load(sys.stdin)
pathlib.Path({str(marker)!r}).write_text("ran", encoding="utf-8")
print(json.dumps({{"status":"succeeded","result":{{"summary":"external"}}}}))
""".strip(),
        encoding="utf-8",
    )

    server, thread, base = _server(control)
    try:
        client = RemoteWorkerClient(base, "worker-secret", "runner-1", [], timeout=5)
        runner = RemoteWorkerRunner(
            client,
            [sys.executable, str(executor)],
            executor_mode="auto",
            heartbeat_interval_seconds=0.05,
            executor_timeout_seconds=5,
        )

        outcomes = runner.run(cycles=1, idle_sleep_seconds=0)

        assert outcomes == [{"job_key":queued["key"], "status":"completed"}]
        assert marker.is_file()
    finally:
        _stop(server, thread)


def test_native_mode_rejects_unsupported_job(tmp_path):
    control = ControlPlane(str(tmp_path / "native-unsupported.sqlite"), authorizer=_auth())
    queued = control.queue.enqueue({
        "handoff":{
            "repository":"dbrckk/native-unsupported",
            "task":"Unsupported native task.",
        },
        "required_capabilities":[],
    })

    server, thread, base = _server(control)
    try:
        client = RemoteWorkerClient(base, "worker-secret", "runner-1", [], timeout=5)
        runner = RemoteWorkerRunner(
            client,
            [],
            executor_mode="native",
            heartbeat_interval_seconds=0.05,
            executor_timeout_seconds=5,
        )

        outcomes = runner.run(cycles=1, idle_sleep_seconds=0)

        assert outcomes == [{
            "job_key":queued["key"],
            "status":"failed",
            "reason":"native_executor_unsupported",
        }]
        assert control.queue.get(queued["key"])["status"] == "failed"
    finally:
        _stop(server, thread)


def test_auto_mode_without_any_executor_fails_executor_unavailable(tmp_path):
    control = ControlPlane(str(tmp_path / "executor-unavailable.sqlite"), authorizer=_auth())
    queued = control.queue.enqueue({
        "handoff":{
            "repository":"dbrckk/no-executor",
            "task":"Unsupported task without fallback.",
        },
        "required_capabilities":[],
    })

    server, thread, base = _server(control)
    try:
        client = RemoteWorkerClient(base, "worker-secret", "runner-1", [], timeout=5)
        runner = RemoteWorkerRunner(
            client,
            [],
            executor_mode="auto",
            heartbeat_interval_seconds=0.05,
            executor_timeout_seconds=5,
        )

        outcomes = runner.run(cycles=1, idle_sleep_seconds=0)

        assert outcomes == [{
            "job_key":queued["key"],
            "status":"failed",
            "reason":"executor_unavailable",
        }]
    finally:
        _stop(server, thread)


def test_native_runtime_failure_never_falls_back_external(
    tmp_path,
    monkeypatch,
):
    control = ControlPlane(str(tmp_path / "native-no-fallback.sqlite"), authorizer=_auth())
    queued = control.queue.enqueue({
        "handoff":_native_browser_handoff_for_runner(),
        "required_capabilities":[],
    })
    marker = tmp_path / "external-ran"
    executor = tmp_path / "external.py"
    executor.write_text(
        f"""
import json, pathlib, sys
json.load(sys.stdin)
pathlib.Path({str(marker)!r}).write_text("ran", encoding="utf-8")
print(json.dumps({{"status":"succeeded","result":{{"summary":"external"}}}}))
""".strip(),
        encoding="utf-8",
    )

    def fail_native(_context):
        return {
            "status":"failed",
            "reason":"native_executor_failed",
            "result":{"summary":"native failed after starting"},
        }

    monkeypatch.setattr(
        "production_os.remote_worker_runner.execute_native",
        fail_native,
    )

    server, thread, base = _server(control)
    try:
        client = RemoteWorkerClient(base, "worker-secret", "runner-1", [], timeout=5)
        runner = RemoteWorkerRunner(
            client,
            [sys.executable, str(executor)],
            executor_mode="auto",
            heartbeat_interval_seconds=0.05,
            executor_timeout_seconds=5,
        )

        outcomes = runner.run(cycles=1, idle_sleep_seconds=0)

        assert outcomes == [{
            "job_key":queued["key"],
            "status":"failed",
            "reason":"native_executor_failed",
        }]
        assert marker.exists() is False
    finally:
        _stop(server, thread)



def test_native_execution_heartbeats_while_future_is_running(
    tmp_path,
    monkeypatch,
):
    control = ControlPlane(str(tmp_path / "native-heartbeat.sqlite"), authorizer=_auth())
    queued = control.queue.enqueue({
        "handoff":_native_browser_handoff_for_runner(),
        "required_capabilities":[],
    })

    def slow_native(_context):
        time.sleep(0.14)
        return {"status":"succeeded","result":{"summary":"native ok"}}

    monkeypatch.setattr(
        "production_os.remote_worker_runner.execute_native",
        slow_native,
    )
    server, thread, base = _server(control)
    try:
        client = RemoteWorkerClient(base, "worker-secret", "runner-1", [], timeout=5)
        runner = RemoteWorkerRunner(
            client,
            [],
            executor_mode="native",
            heartbeat_interval_seconds=0.02,
            executor_timeout_seconds=2,
        )
        real_heartbeat = runner._heartbeat_active
        calls = {"count":0}

        def counted(key):
            calls["count"] += 1
            return real_heartbeat(key)

        runner._heartbeat_active = counted
        outcomes = runner.run(cycles=1, idle_sleep_seconds=0)

        assert outcomes == [{"job_key":queued["key"], "status":"completed"}]
        assert calls["count"] >= 2
    finally:
        _stop(server, thread)


def test_native_execution_timeout_sets_cancel_event_and_fails_once(
    tmp_path,
    monkeypatch,
):
    control = ControlPlane(str(tmp_path / "native-timeout.sqlite"), authorizer=_auth())
    queued = control.queue.enqueue({
        "handoff":_native_browser_handoff_for_runner(),
        "required_capabilities":[],
    })
    seen = {}

    def slow_native(context):
        seen["event"] = context.cancellation_event
        time.sleep(0.16)
        return {"status":"succeeded","result":{"summary":"too late"}}

    monkeypatch.setattr(
        "production_os.remote_worker_runner.execute_native",
        slow_native,
    )
    server, thread, base = _server(control)
    try:
        client = RemoteWorkerClient(base, "worker-secret", "runner-1", [], timeout=5)
        fail_calls = []
        real_fail = client.fail

        def counted_fail(*args, **kwargs):
            fail_calls.append((args, kwargs))
            return real_fail(*args, **kwargs)

        client.fail = counted_fail
        runner = RemoteWorkerRunner(
            client,
            [],
            executor_mode="native",
            heartbeat_interval_seconds=0.02,
            executor_timeout_seconds=0.05,
        )

        outcomes = runner.run(cycles=1, idle_sleep_seconds=0)

        assert outcomes == [{
            "job_key":queued["key"],
            "status":"failed",
            "reason":"executor_timeout",
        }]
        assert seen["event"].is_set()
        assert len(fail_calls) == 1
    finally:
        _stop(server, thread)


def test_native_execution_cancel_request_sets_event_and_does_not_complete(
    tmp_path,
    monkeypatch,
):
    control = ControlPlane(str(tmp_path / "native-cancel.sqlite"), authorizer=_auth())
    queued = control.queue.enqueue({
        "handoff":_native_browser_handoff_for_runner(),
        "required_capabilities":[],
    })
    seen = {}

    def cancellable_native(context):
        seen["event"] = context.cancellation_event
        deadline = time.time() + 0.5
        while not context.cancellation_event.is_set() and time.time() < deadline:
            time.sleep(0.01)
        return {"status":"succeeded","result":{"summary":"stopped"}}

    monkeypatch.setattr(
        "production_os.remote_worker_runner.execute_native",
        cancellable_native,
    )
    server, server_thread, base = _server(control)
    outcomes = []
    try:
        client = RemoteWorkerClient(base, "worker-secret", "runner-1", [], timeout=5)
        runner = RemoteWorkerRunner(
            client,
            [],
            executor_mode="native",
            heartbeat_interval_seconds=0.02,
            executor_timeout_seconds=2,
        )
        worker_thread = threading.Thread(
            target=lambda: outcomes.extend(
                runner.run(cycles=1, idle_sleep_seconds=0)
            ),
            daemon=True,
        )
        worker_thread.start()
        deadline = time.time() + 2
        while time.time() < deadline:
            if control.queue.get(queued["key"])["status"] == "acked":
                break
            time.sleep(0.01)
        control.dashboard_control.request_job_cancel(
            queued["key"],
            requested_by="operator:test",
        )
        worker_thread.join(timeout=2)

        assert outcomes == [{
            "job_key":queued["key"],
            "status":"cancelled",
        }]
        assert seen["event"].is_set()
        assert control.queue.get(queued["key"])["status"] == "cancelled"
    finally:
        _stop(server, server_thread)


def test_native_execution_stale_generation_sets_event_and_checkpoints_stale(
    tmp_path,
    monkeypatch,
):
    control = ControlPlane(str(tmp_path / "native-stale.sqlite"), authorizer=_auth())
    queued = control.queue.enqueue({
        "handoff":_native_browser_handoff_for_runner(),
        "required_capabilities":[],
    })
    seen = {}

    def cancellable_native(context):
        seen["event"] = context.cancellation_event
        deadline = time.time() + 0.3
        while not context.cancellation_event.is_set() and time.time() < deadline:
            time.sleep(0.01)
        return {"status":"succeeded","result":{"summary":"stopped"}}

    monkeypatch.setattr(
        "production_os.remote_worker_runner.execute_native",
        cancellable_native,
    )
    server, thread, base = _server(control)
    try:
        client = RemoteWorkerClient(base, "worker-secret", "runner-1", [], timeout=5)
        runner = RemoteWorkerRunner(
            client,
            [],
            executor_mode="native",
            heartbeat_interval_seconds=0.02,
            executor_timeout_seconds=2,
        )
        real_heartbeat = runner._heartbeat_active
        beats = {"count":0}

        def stale_after_start(key):
            beats["count"] += 1
            snapshot = real_heartbeat(key)
            if beats["count"] >= 1:
                snapshot["stale_job_keys"] = [key]
            return snapshot

        checkpoint_calls = []
        client.checkpoint_stale = lambda key, ref: checkpoint_calls.append((key, ref))
        runner._heartbeat_active = stale_after_start

        outcomes = runner.run(cycles=1, idle_sleep_seconds=0)

        assert outcomes == [{"job_key":queued["key"], "status":"stale"}]
        assert seen["event"].is_set()
        assert checkpoint_calls and checkpoint_calls[0][0] == queued["key"]
    finally:
        _stop(server, thread)


def test_native_execution_worker_shutdown_sets_event_and_abandons(
    tmp_path,
    monkeypatch,
):
    control = ControlPlane(str(tmp_path / "native-shutdown.sqlite"), authorizer=_auth())
    queued = control.queue.enqueue({
        "handoff":_native_browser_handoff_for_runner(),
        "required_capabilities":[],
    })
    seen = {}

    def cancellable_native(context):
        seen["event"] = context.cancellation_event
        deadline = time.time() + 0.5
        while not context.cancellation_event.is_set() and time.time() < deadline:
            time.sleep(0.01)
        return {"status":"succeeded","result":{"summary":"stopped"}}

    monkeypatch.setattr(
        "production_os.remote_worker_runner.execute_native",
        cancellable_native,
    )
    server, server_thread, base = _server(control)
    outcomes = []
    try:
        client = RemoteWorkerClient(base, "worker-secret", "runner-1", [], timeout=5)
        runner = RemoteWorkerRunner(
            client,
            [],
            executor_mode="native",
            heartbeat_interval_seconds=0.02,
            executor_timeout_seconds=2,
        )
        worker_thread = threading.Thread(
            target=lambda: outcomes.extend(
                runner.run(cycles=1, idle_sleep_seconds=0)
            ),
            daemon=True,
        )
        worker_thread.start()
        deadline = time.time() + 2
        while time.time() < deadline:
            if control.queue.get(queued["key"])["status"] == "acked":
                break
            time.sleep(0.01)
        runner.request_stop()
        worker_thread.join(timeout=2)

        assert outcomes == [{
            "job_key":queued["key"],
            "status":"abandoned",
            "reason":"worker_shutdown",
        }]
        assert seen["event"].is_set()
    finally:
        _stop(server, server_thread)


def test_native_execution_control_plane_outage_abandons_after_existing_failure_threshold(
    tmp_path,
    monkeypatch,
):
    control = ControlPlane(str(tmp_path / "native-outage.sqlite"), authorizer=_auth())
    queued = control.queue.enqueue({
        "handoff":_native_browser_handoff_for_runner(),
        "required_capabilities":[],
    })
    seen = {}

    def cancellable_native(context):
        seen["event"] = context.cancellation_event
        deadline = time.time() + 0.4
        while not context.cancellation_event.is_set() and time.time() < deadline:
            time.sleep(0.01)
        return {"status":"succeeded","result":{"summary":"stopped"}}

    monkeypatch.setattr(
        "production_os.remote_worker_runner.execute_native",
        cancellable_native,
    )
    server, thread, base = _server(control)
    try:
        client = RemoteWorkerClient(base, "worker-secret", "runner-1", [], timeout=5)
        runner = RemoteWorkerRunner(
            client,
            [],
            executor_mode="native",
            heartbeat_interval_seconds=0.02,
            executor_timeout_seconds=2,
        )
        runner.max_consecutive_heartbeat_failures = 2
        calls = {"count":0}

        def unavailable(_key):
            calls["count"] += 1
            raise RuntimeError("control plane unavailable")

        runner._heartbeat_active = unavailable
        outcomes = runner.run(cycles=1, idle_sleep_seconds=0)

        assert outcomes == [{
            "job_key":queued["key"],
            "status":"abandoned",
            "reason":"control_plane_unavailable",
        }]
        assert calls["count"] == 2
        assert seen["event"].is_set()
    finally:
        _stop(server, thread)
