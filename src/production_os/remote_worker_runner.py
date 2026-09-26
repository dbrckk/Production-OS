from __future__ import annotations

import json
import os
import subprocess
import time
from collections.abc import Sequence

from .remote_worker import RemoteJob, RemoteWorkerClient


class RemoteWorkerRunner:
    def __init__(
        self,
        client: RemoteWorkerClient,
        executor_command: Sequence[str],
        *,
        max_concurrency: int = 1,
        heartbeat_interval_seconds: float = 5.0,
        executor_timeout_seconds: float = 3600.0,
        secret_env_names: Sequence[str] | None = None,
    ):
        command = [str(part) for part in executor_command if str(part)]
        if not command:
            raise ValueError("executor command is required")
        if int(max_concurrency) < 1:
            raise ValueError("max_concurrency must be >= 1")
        if float(heartbeat_interval_seconds) <= 0:
            raise ValueError("heartbeat_interval_seconds must be > 0")
        if float(executor_timeout_seconds) <= 0:
            raise ValueError("executor_timeout_seconds must be > 0")
        self.client = client
        self.executor_command = command
        self.max_concurrency = int(max_concurrency)
        self.heartbeat_interval_seconds = float(heartbeat_interval_seconds)
        self.executor_timeout_seconds = float(executor_timeout_seconds)
        secret_names = {
            "PRODUCTION_OS_WORKER_TOKEN",
            *(
                str(name)
                for name in (secret_env_names or [])
                if str(name)
            ),
        }
        self.executor_env = os.environ.copy()
        for name in secret_names:
            self.executor_env.pop(name, None)

    @staticmethod
    def _terminate(process: subprocess.Popen[str]) -> None:
        if process.poll() is not None:
            return
        process.terminate()
        try:
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=2)

    def _heartbeat_active(self, key: str) -> dict:
        return self.client.heartbeat(
            active_tasks=1,
            active_job_keys=[key],
        )

    def _acknowledge_cancel(self, key: str) -> None:
        self.client.heartbeat(
            active_tasks=0,
            active_job_keys=[],
            job_control_states={key:"cancel_requested"},
        )

    def _execute(self, job: RemoteJob) -> dict:
        key = job.key
        self.client.ack(key)
        heartbeat = self._heartbeat_active(key)
        if key in heartbeat.get("stale_job_keys", []):
            self.client.checkpoint_stale(
                key,
                f"worker-runner://{self.client.worker_id}/{key}/stale",
            )
            return {
                "job_key":key,
                "status":"stale",
            }

        request = json.dumps(
            {
                "schema_version":
                    "production-os/worker-executor-request/v1",
                "job":job.to_dict(),
            },
            ensure_ascii=False,
        )
        started = time.monotonic()
        process = subprocess.Popen(
            self.executor_command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=self.executor_env,
        )
        first_communicate = True
        stdout = ""
        try:
            while True:
                elapsed = time.monotonic() - started
                remaining = self.executor_timeout_seconds - elapsed
                if remaining <= 0:
                    self._terminate(process)
                    duration = time.monotonic() - started
                    self.client.fail(
                        key,
                        "executor_timeout",
                        result_payload={
                            "summary":"executor exceeded its timeout",
                        },
                        duration_seconds=duration,
                    )
                    return {
                        "job_key":key,
                        "status":"failed",
                        "reason":"executor_timeout",
                    }

                try:
                    stdout, _stderr = process.communicate(
                        input=request if first_communicate else None,
                        timeout=min(
                            self.heartbeat_interval_seconds,
                            remaining,
                        ),
                    )
                    break
                except subprocess.TimeoutExpired:
                    first_communicate = False
                    try:
                        heartbeat = self._heartbeat_active(key)
                    except RuntimeError:
                        self._terminate(process)
                        return {
                            "job_key":key,
                            "status":"abandoned",
                            "reason":"control_plane_unavailable",
                        }

                    if key in heartbeat.get("stale_job_keys", []):
                        self._terminate(process)
                        self.client.checkpoint_stale(
                            key,
                            (
                                "worker-runner://"
                                f"{self.client.worker_id}/{key}/stale"
                            ),
                        )
                        return {
                            "job_key":key,
                            "status":"stale",
                        }

                    controls = (
                        heartbeat.get("control", {})
                        .get("jobs", {})
                    )
                    desired = str(
                        (controls.get(key) or {}).get("desired_state")
                        or ""
                    )
                    if desired == "cancel_requested":
                        self._terminate(process)
                        self._acknowledge_cancel(key)
                        return {
                            "job_key":key,
                            "status":"cancelled",
                        }
        finally:
            if process.poll() is None:
                self._terminate(process)

        duration = time.monotonic() - started
        if process.returncode != 0:
            reason = f"executor_exit_{process.returncode}"
            self.client.fail(
                key,
                reason,
                result_payload={
                    "summary":"executor process failed",
                },
                duration_seconds=duration,
            )
            return {
                "job_key":key,
                "status":"failed",
                "reason":reason,
            }

        try:
            payload = json.loads(stdout)
        except (TypeError, json.JSONDecodeError):
            payload = None
        if not isinstance(payload, dict):
            self.client.fail(
                key,
                "executor_invalid_output",
                result_payload={
                    "summary":"executor returned invalid JSON output",
                },
                duration_seconds=duration,
            )
            return {
                "job_key":key,
                "status":"failed",
                "reason":"executor_invalid_output",
            }

        status = str(payload.get("status") or "")
        result = payload.get("result", {})
        if not isinstance(result, dict):
            status = ""

        if status == "succeeded":
            self.client.complete(
                key,
                result_payload=result,
                duration_seconds=duration,
            )
            return {
                "job_key":key,
                "status":"completed",
            }

        if status == "failed":
            reason = str(
                payload.get("reason")
                or "executor_reported_failure"
            )[:512]
            self.client.fail(
                key,
                reason,
                result_payload=result,
                duration_seconds=duration,
            )
            return {
                "job_key":key,
                "status":"failed",
                "reason":reason,
            }

        self.client.fail(
            key,
            "executor_invalid_output",
            result_payload={
                "summary":"executor output schema is invalid",
            },
            duration_seconds=duration,
        )
        return {
            "job_key":key,
            "status":"failed",
            "reason":"executor_invalid_output",
        }

    def run(
        self,
        *,
        cycles: int = 0,
        idle_sleep_seconds: float = 5.0,
        ack_timeout_seconds: int = 120,
    ) -> list[dict]:
        if int(cycles) < 0:
            raise ValueError("cycles must be >= 0")
        if float(idle_sleep_seconds) < 0:
            raise ValueError("idle_sleep_seconds must be >= 0")

        self.client.open_session(
            max_concurrency=self.max_concurrency,
            active_job_keys=[],
        )
        outcomes: list[dict] = []
        index = 0
        while cycles == 0 or index < int(cycles):
            index += 1
            self.client.heartbeat(
                active_tasks=0,
                active_job_keys=[],
            )
            job = self.client.claim(
                ack_timeout_seconds=ack_timeout_seconds,
            )
            if job is not None:
                outcome = self._execute(job)
                outcomes.append(outcome)
                try:
                    self.client.heartbeat(
                        active_tasks=0,
                        active_job_keys=[],
                    )
                except RuntimeError:
                    pass
            elif (cycles == 0 or index < int(cycles)) and idle_sleep_seconds:
                time.sleep(float(idle_sleep_seconds))
        return outcomes
