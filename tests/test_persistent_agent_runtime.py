from __future__ import annotations

import json
import sys

from production_os.agent_runtime import PersistentAgentRuntime, write_agent_checkpoint
from production_os.remote_worker import RemoteJob
from production_os.remote_worker_runner import RemoteWorkerRunner


class FakeClient:
    worker_id = "worker-test"

    def __init__(self, jobs, *, stale=False):
        self.jobs = list(jobs)
        self.completed = []
        self.failed = []
        self.checkpoints = []
        self.stale = bool(stale)
        self.control_state = "active"

    def open_session(self, **_kwargs):
        return {"recovered_jobs":[]}

    def heartbeat(self, **kwargs):
        active = [str(key) for key in kwargs.get("active_job_keys") or []]
        return {
            "worker":{},
            "stale_job_keys":active if self.stale else [],
            "control":{"jobs":{}},
        }

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
        self.checkpoints.append((key, checkpoint_ref))
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



def test_active_checkpoint_protocol_is_atomic_validated_and_observed(tmp_path):
    runtime = PersistentAgentRuntime(tmp_path / "runtime")
    context = runtime.prepare("job-checkpoint")
    write_agent_checkpoint(
        context.checkpoint_path,
        job_key=context.job_key,
        session_id=context.session_id,
        sequence=3,
        state={"phase":"tests", "completed":["unit"]},
        resume_token="cursor-3",
    )

    observed = runtime.observe_checkpoint(context.job_key)

    assert observed["valid"] is True
    assert observed["schema_version"] == "production-os/agent-checkpoint/v1"
    assert observed["sequence"] == 3
    assert observed["ref"].startswith("runtime-checkpoint://")
    assert len(observed["sha256"]) == 64
    state = runtime.inspect(context.job_key)
    assert state["checkpoint_available"] is True
    assert state["checkpoint"]["sequence"] == 3
    assert state["checkpoint"]["ref"] == observed["ref"]


def test_checkpoint_with_wrong_session_is_not_resumable(tmp_path):
    runtime = PersistentAgentRuntime(tmp_path / "runtime")
    context = runtime.prepare("job-session-bound")
    write_agent_checkpoint(
        context.checkpoint_path,
        job_key=context.job_key,
        session_id="different-session",
        sequence=1,
        state={"phase":"unsafe"},
    )

    observed = runtime.observe_checkpoint(context.job_key)

    assert observed == {"valid":False, "reason":"session_mismatch"}
    assert runtime.inspect(context.job_key)["checkpoint_available"] is False


def test_stale_job_reports_real_durable_checkpoint_reference(tmp_path):
    client = FakeClient(
        [RemoteJob("job-stale", {"payload":{"task":"x"}})],
        stale=True,
    )
    runner = RemoteWorkerRunner(
        client,
        [sys.executable, "-c", "raise SystemExit(99)"],
        runtime_root=str(tmp_path / "durable"),
        heartbeat_interval_seconds=0.05,
        executor_timeout_seconds=5,
    )
    seeded = runner.agent_runtime.prepare("job-stale")
    write_agent_checkpoint(
        seeded.checkpoint_path,
        job_key=seeded.job_key,
        session_id=seeded.session_id,
        sequence=2,
        state={"phase":"implementation"},
    )
    runner.agent_runtime.mark_outcome("job-stale", {
        "job_key":"job-stale",
        "status":"abandoned",
        "reason":"seed",
    })

    outcomes = runner.run(cycles=1, idle_sleep_seconds=0)

    assert outcomes == [{"job_key":"job-stale", "status":"stale"}]
    assert len(client.checkpoints) == 1
    key, checkpoint_ref = client.checkpoints[0]
    assert key == "job-stale"
    assert checkpoint_ref.startswith("runtime-checkpoint://")
    state = runner.agent_runtime.inspect("job-stale")
    assert state["checkpoint"]["sequence"] == 2
    assert state["status"] == "stale"


def test_invalid_checkpoint_does_not_replace_runtime_resume_contract(tmp_path):
    runtime = PersistentAgentRuntime(tmp_path / "runtime")
    first = runtime.prepare("job-invalid")
    checkpoint = runtime.workspace_for("job-invalid") / "checkpoint.json"
    checkpoint.write_text("{not-json", encoding="utf-8")
    runtime.mark_outcome("job-invalid", {
        "job_key":"job-invalid",
        "status":"abandoned",
        "reason":"restart",
    })

    second = runtime.prepare("job-invalid")

    assert second.session_id == first.session_id
    assert second.attempt == 2
    assert second.resume is True
    assert second.checkpoint_available is False
