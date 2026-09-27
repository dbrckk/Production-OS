from __future__ import annotations

import json
import sys

from production_os.agent_runtime import PersistentAgentRuntime
from production_os.remote_worker import RemoteJob
from production_os.remote_worker_runner import RemoteWorkerRunner


class FakeClient:
    worker_id = "worker-test"

    def __init__(self, jobs):
        self.jobs = list(jobs)
        self.completed = []
        self.failed = []
        self.control_state = "active"

    def open_session(self, **_kwargs):
        return {"recovered_jobs":[]}

    def heartbeat(self, **_kwargs):
        return {"worker":{}, "stale_job_keys":[], "control":{"jobs":{}}}

    def claim(self, **_kwargs):
        return self.jobs.pop(0) if self.jobs else None

    def ack(self, key):
        return {"key":key, "status":"acked"}

    def complete(self, key, *, result_payload=None, duration_seconds=None):
        self.completed.append((key, result_payload or {}, duration_seconds))
        return {"key":key, "status":"completed"}

    def fail(self, key, reason, *, result_payload=None, duration_seconds=None):
        self.failed.append((key, reason, result_payload or {}, duration_seconds))
        return {"key":key, "status":"failed"}

    def checkpoint_stale(self, key, checkpoint_ref):
        return {"key":key, "checkpoint_ref":checkpoint_ref}


def test_persistent_runtime_reuses_session_and_marks_resume(tmp_path):
    runtime = PersistentAgentRuntime(tmp_path / "runtime")
    first = runtime.prepare("job/unsafe/../key")
    assert first.attempt == 1
    assert first.resume is False
    assert "job/unsafe" not in first.workspace

    checkpoint = tmp_path / "runtime" / runtime._job_dir_name("job/unsafe/../key") / "checkpoint.json"
    checkpoint.write_text('{"step": 4}', encoding="utf-8")
    runtime.mark_outcome("job/unsafe/../key", {
        "job_key":"job/unsafe/../key",
        "status":"abandoned",
        "reason":"worker_shutdown",
    })

    second = runtime.prepare("job/unsafe/../key")
    assert second.session_id == first.session_id
    assert second.attempt == 2
    assert second.resume is True
    assert second.checkpoint_available is True
    assert second.checkpoint_path == str(checkpoint)


def test_remote_runner_passes_durable_runtime_context_to_executor(tmp_path):
    executor = tmp_path / "executor.py"
    executor.write_text(
        """
import json, os, sys
request = json.load(sys.stdin)
runtime = request["runtime"]
print(json.dumps({
    "status":"succeeded",
    "result":{
        "session_id":runtime["session_id"],
        "workspace":runtime["workspace"],
        "resume":runtime["resume"],
        "attempt":runtime["attempt"],
        "env_workspace":os.environ["PRODUCTION_OS_RUNTIME_WORKSPACE"],
        "env_resume":os.environ["PRODUCTION_OS_RUNTIME_RESUME"],
    },
}))
""".strip(),
        encoding="utf-8",
    )
    client = FakeClient([RemoteJob("job-1", {"payload":{"task":"x"}})])
    runner = RemoteWorkerRunner(
        client,
        [sys.executable, str(executor)],
        runtime_root=str(tmp_path / "durable"),
        heartbeat_interval_seconds=0.05,
        executor_timeout_seconds=5,
    )

    outcomes = runner.run(cycles=1, idle_sleep_seconds=0)

    assert outcomes == [{"job_key":"job-1", "status":"completed"}]
    result = client.completed[0][1]
    assert result["resume"] is False
    assert result["attempt"] == 1
    assert result["workspace"] == result["env_workspace"]
    assert result["env_resume"] == "0"
    state = runner.agent_runtime.inspect("job-1")
    assert state["status"] == "completed"
    assert state["attempt"] == 1


def test_worker_compose_mounts_shared_durable_runtime():
    compose = open("compose.worker.yaml", encoding="utf-8").read()
    assert "PRODUCTION_OS_RUNTIME_DIR: /var/lib/production-os/runtime" in compose
    assert "production-worker-runtime:/var/lib/production-os/runtime" in compose
    assert "production-worker-runtime:" in compose


def test_remote_worker_cli_exposes_runtime_root():
    from production_os.cli import _parse_args

    args = _parse_args([
        "remote-worker-run",
        "--url", "http://example.invalid",
        "--worker-id", "worker-a",
        "--executor-command", "python executor.py",
        "--runtime-root", "/tmp/runtime",
    ])
    assert args.runtime_root == "/tmp/runtime"
