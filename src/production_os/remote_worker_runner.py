from __future__ import annotations

import json
import os
import subprocess
import threading
import time
from collections.abc import Sequence
from concurrent.futures import FIRST_COMPLETED, Future, ThreadPoolExecutor, wait

from .agent_runtime import PersistentAgentRuntime
from .executor_worktree import (
    IntegrationPreflight,
    PreparedWorktree,
    WorktreeRuntimeError,
    inspect_worktree_result,
    preintegrate_upstream_commits,
    prepare_isolated_worktree,
    prune_integrated_workflow_branches,
    remove_isolated_worktree,
)
from .remote_worker import RemoteJob, RemoteWorkerClient
from .repository_cache import RepositoryCache


class RemoteWorkerRunner:
    def __init__(
        self,
        client: RemoteWorkerClient,
        executor_command: Sequence[str] | None,
        *,
        executor_mode: str = "auto",
        max_concurrency: int = 1,
        heartbeat_interval_seconds: float = 5.0,
        executor_timeout_seconds: float = 3600.0,
        secret_env_names: Sequence[str] | None = None,
        runtime_root: str | None = None,
        repository_roots: dict[str, str] | None = None,
        worktree_root: str | None = None,
        repository_cache_root: str | None = None,
    ):
        command = [
            str(part)
            for part in (executor_command or [])
            if str(part)
        ]
        mode = str(executor_mode or "").strip().lower()
        if mode not in {"auto", "native", "external"}:
            raise ValueError(
                "executor_mode must be auto, native, or external"
            )
        if mode == "external" and not command:
            raise ValueError("executor command is required in external mode")
        if int(max_concurrency) < 1:
            raise ValueError("max_concurrency must be >= 1")
        if float(heartbeat_interval_seconds) <= 0:
            raise ValueError("heartbeat_interval_seconds must be > 0")
        if float(executor_timeout_seconds) <= 0:
            raise ValueError("executor_timeout_seconds must be > 0")
        self.client = client
        self.executor_mode = mode
        self.executor_command = command
        self.max_concurrency = int(max_concurrency)
        self.heartbeat_interval_seconds = float(heartbeat_interval_seconds)
        self.executor_timeout_seconds = float(executor_timeout_seconds)
        self._active_job_keys: set[str] = set()
        self._active_lock = threading.RLock()
        self._stop_event = threading.Event()
        self.max_consecutive_heartbeat_failures = 3
        self.repository_roots = {
            str(name):str(path)
            for name, path in (repository_roots or {}).items()
            if str(name).strip() and str(path).strip()
        }
        self.worktree_root = (
            str(worktree_root)
            if worktree_root
            else os.getenv("PRODUCTION_OS_WORKTREE_DIR", "")
        )
        configured_repository_cache_root = (
            repository_cache_root
            or os.getenv("PRODUCTION_OS_REPOSITORY_CACHE_DIR")
        )
        self.repository_cache = (
            RepositoryCache(configured_repository_cache_root)
            if configured_repository_cache_root
            else None
        )
        configured_runtime_root = runtime_root or os.getenv("PRODUCTION_OS_RUNTIME_DIR")
        self.agent_runtime = (
            PersistentAgentRuntime(configured_runtime_root)
            if configured_runtime_root
            else None
        )
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

    def request_stop(self) -> None:
        """Stop claiming work and terminate active executors cooperatively."""
        self._stop_event.set()

    @property
    def stop_requested(self) -> bool:
        return self._stop_event.is_set()

    def _observe_checkpoint(self, key: str) -> dict:
        if self.agent_runtime is None:
            return {"valid":False, "reason":"runtime_disabled"}
        return self.agent_runtime.observe_checkpoint(key)

    def _checkpoint_ref(self, key: str) -> str:
        checkpoint = self._observe_checkpoint(key)
        if checkpoint.get("valid") and checkpoint.get("ref"):
            return str(checkpoint["ref"])
        return f"worker-runner://{self.client.worker_id}/{key}/stale"

    def _integration_preflight(
        self,
        job: RemoteJob,
        prepared_worktree: PreparedWorktree | None,
    ) -> IntegrationPreflight | None:
        if prepared_worktree is None:
            return None
        payload = dict(job.payload.get("payload") or {})
        handoff = dict(payload.get("handoff") or {})
        isolation = dict(handoff.get("isolation") or {})
        if not bool(isolation.get("integration_target", False)):
            return None
        upstream = handoff.get("upstream_context")
        if not isinstance(upstream, list):
            return None
        return preintegrate_upstream_commits(
            prepared_worktree.worktree_path,
            upstream,
        )

    def _prepare_worktree(self, job: RemoteJob) -> PreparedWorktree | None:
        payload = dict(job.payload.get("payload") or {})
        handoff = dict(payload.get("handoff") or {})
        isolation = dict(handoff.get("isolation") or {})
        if isolation.get("mode") != "git-worktree":
            return None

        repository = str(handoff.get("repository") or "").strip()
        root = self.repository_roots.get(repository)
        if not root and self.repository_cache is not None:
            root = self.repository_cache.ensure(repository).path
        if not root or not self.worktree_root:
            # Backwards compatibility: the external executor may implement the
            # isolation contract itself when no local checkout source exists.
            return None

        return prepare_isolated_worktree(
            root,
            isolation,
            worktree_root=self.worktree_root,
        )

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

    def _heartbeat_snapshot(
        self,
        *,
        job_control_states: dict[str, str] | None = None,
    ) -> dict:
        with self._active_lock:
            keys = sorted(self._active_job_keys)
            return self.client.heartbeat(
                active_tasks=len(keys),
                active_job_keys=keys,
                job_control_states=job_control_states,
            )

    def _activate(self, key: str) -> dict:
        with self._active_lock:
            self._active_job_keys.add(key)
            return self._heartbeat_snapshot()

    def _deactivate(
        self,
        key: str,
        *,
        job_control_state: str | None = None,
    ) -> None:
        with self._active_lock:
            self._active_job_keys.discard(key)
            states = (
                {key:job_control_state}
                if job_control_state is not None
                else None
            )
            try:
                self._heartbeat_snapshot(job_control_states=states)
            except RuntimeError:
                pass

    def _heartbeat_active(self, key: str) -> dict:
        with self._active_lock:
            if key not in self._active_job_keys:
                self._active_job_keys.add(key)
            return self._heartbeat_snapshot()

    def _execute(self, job: RemoteJob) -> dict:
        key = job.key
        runtime_context = (
            self.agent_runtime.prepare(key)
            if self.agent_runtime is not None
            else None
        )
        self.client.ack(key)
        active_registered = True
        heartbeat = self._activate(key)
        process: subprocess.Popen[str] | None = None
        try:
            if self._stop_event.is_set():
                return {
                    "job_key":key,
                    "status":"abandoned",
                    "reason":"worker_shutdown",
                }
            if key in heartbeat.get("stale_job_keys", []):
                self.client.checkpoint_stale(
                    key,
                    self._checkpoint_ref(key),
                )
                return {
                    "job_key":key,
                    "status":"stale",
                }

            request_payload = {
                "schema_version":
                    "production-os/worker-executor-request/v1",
                "job":job.to_dict(),
            }
            executor_env = self.executor_env.copy()
            prepared_worktree = self._prepare_worktree(job)
            integration_preflight = self._integration_preflight(
                job,
                prepared_worktree,
            )
            executor_cwd = None
            executor_start_sha = None
            if prepared_worktree is not None:
                request_payload["executor_workspace"] = (
                    prepared_worktree.to_dict()
                )
                executor_cwd = prepared_worktree.worktree_path
                before_execution = inspect_worktree_result(
                    prepared_worktree.worktree_path,
                    base_sha=prepared_worktree.base_ref,
                )
                executor_start_sha = str(
                    before_execution["final_sha"]
                )
                request_payload["executor_git_start"] = (
                    before_execution
                )
                executor_env.update({
                    "PRODUCTION_OS_REPOSITORY_ROOT":
                        prepared_worktree.repository_root,
                    "PRODUCTION_OS_WORKTREE":
                        prepared_worktree.worktree_path,
                    "PRODUCTION_OS_WORKTREE_BRANCH":
                        prepared_worktree.branch,
                    "PRODUCTION_OS_WORKTREE_BASE":
                        prepared_worktree.base_ref,
                })
            if integration_preflight is not None:
                request_payload["integration_preflight"] = (
                    integration_preflight.to_dict()
                )
                executor_env["PRODUCTION_OS_INTEGRATION_PREFLIGHT_STATUS"] = (
                    integration_preflight.status
                )
            if runtime_context is not None:
                request_payload["runtime"] = runtime_context.to_dict()
                executor_env.update({
                    "PRODUCTION_OS_RUNTIME_SESSION_ID":
                        runtime_context.session_id,
                    "PRODUCTION_OS_RUNTIME_WORKSPACE":
                        runtime_context.workspace,
                    "PRODUCTION_OS_RUNTIME_STATE":
                        runtime_context.state_path,
                    "PRODUCTION_OS_RUNTIME_CHECKPOINT":
                        runtime_context.checkpoint_path,
                    "PRODUCTION_OS_RUNTIME_RESUME":
                        "1" if runtime_context.resume else "0",
                    "PRODUCTION_OS_RUNTIME_ATTEMPT":
                        str(runtime_context.attempt),
                })
            request = json.dumps(
                request_payload,
                ensure_ascii=False,
            )
            started = time.monotonic()
            process = subprocess.Popen(
                self.executor_command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=executor_env,
                cwd=executor_cwd,
            )
            first_communicate = True
            stdout = ""
            heartbeat_failures = 0
            while True:
                if self._stop_event.is_set():
                    self._observe_checkpoint(key)
                    self._terminate(process)
                    return {
                        "job_key":key,
                        "status":"abandoned",
                        "reason":"worker_shutdown",
                    }
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
                    self._observe_checkpoint(key)
                    try:
                        heartbeat = self._heartbeat_active(key)
                        heartbeat_failures = 0
                    except RuntimeError:
                        heartbeat_failures += 1
                        if (
                            heartbeat_failures
                            >= self.max_consecutive_heartbeat_failures
                        ):
                            self._observe_checkpoint(key)
                            self._terminate(process)
                            return {
                                "job_key":key,
                                "status":"abandoned",
                                "reason":"control_plane_unavailable",
                            }
                        continue

                    if key in heartbeat.get("stale_job_keys", []):
                        self._terminate(process)
                        self.client.checkpoint_stale(
                            key,
                            self._checkpoint_ref(key),
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
                        self._deactivate(
                            key,
                            job_control_state="cancel_requested",
                        )
                        active_registered = False
                        return {
                            "job_key":key,
                            "status":"cancelled",
                        }

            duration = time.monotonic() - started
            self._observe_checkpoint(key)
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
                if prepared_worktree is not None:
                    git_result = inspect_worktree_result(
                        prepared_worktree.worktree_path,
                        base_sha=prepared_worktree.base_ref,
                        executor_start_sha=executor_start_sha,
                    )
                    result["executor_git"] = git_result
                    if not bool(git_result.get("clean")):
                        reason = "executor_worktree_dirty"
                        self.client.fail(
                            key,
                            reason,
                            result_payload={
                                **result,
                                "summary":(
                                    "executor reported success with "
                                    "uncommitted worktree changes"
                                ),
                            },
                            duration_seconds=duration,
                        )
                        return {
                            "job_key":key,
                            "status":"failed",
                            "reason":reason,
                        }
                    if not bool(git_result.get("base_is_ancestor")):
                        reason = "executor_worktree_history_diverged"
                        self.client.fail(
                            key,
                            reason,
                            result_payload={
                                **result,
                                "summary":(
                                    "executor reported success after "
                                    "rewriting worktree history"
                                ),
                            },
                            duration_seconds=duration,
                        )
                        return {
                            "job_key":key,
                            "status":"failed",
                            "reason":reason,
                        }
                    commits = list(
                        git_result.get("commits_since_base") or []
                    )
                    if not commits:
                        commits = [str(git_result["final_sha"])]
                    result["commit_shas"] = commits
                    result["changed_files"] = list(
                        git_result.get("changed_files") or []
                    )

                self.client.complete(
                    key,
                    result_payload=result,
                    duration_seconds=duration,
                )
                if prepared_worktree is not None:
                    try:
                        remove_isolated_worktree(
                            prepared_worktree.repository_root,
                            prepared_worktree.worktree_path,
                        )
                        payload = dict(job.payload.get("payload") or {})
                        handoff = dict(payload.get("handoff") or {})
                        isolation = dict(handoff.get("isolation") or {})
                        if bool(
                            isolation.get("integration_target", False)
                        ):
                            prune_integrated_workflow_branches(
                                prepared_worktree.repository_root,
                                prepared_worktree.branch,
                            )
                    except (WorktreeRuntimeError, OSError):
                        # Completion is already authoritative. Cleanup is
                        # best-effort and must not turn a completed job into
                        # a failure.
                        pass
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
        finally:
            if process is not None and process.poll() is None:
                self._terminate(process)
            if active_registered:
                self._deactivate(key)

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
        futures: dict[Future[dict], str] = {}
        index = 0

        def collect(done) -> None:
            for future in done:
                futures.pop(future, None)
                outcome = future.result()
                if self.agent_runtime is not None:
                    self.agent_runtime.mark_outcome(
                        str(outcome.get("job_key") or ""),
                        outcome,
                    )
                outcomes.append(outcome)

        with ThreadPoolExecutor(
            max_workers=self.max_concurrency,
            thread_name_prefix="production-os-runner",
        ) as pool:
            while (
                not self._stop_event.is_set()
                and (cycles == 0 or index < int(cycles))
            ):
                index += 1
                try:
                    self._heartbeat_snapshot()
                except RuntimeError:
                    if not futures:
                        raise

                while (
                    not self._stop_event.is_set()
                    and len(futures) < self.max_concurrency
                ):
                    job = self.client.claim(
                        ack_timeout_seconds=ack_timeout_seconds,
                    )
                    if job is None:
                        break
                    future = pool.submit(self._execute, job)
                    futures[future] = job.key

                if futures:
                    done, _pending = wait(
                        set(futures),
                        timeout=self.heartbeat_interval_seconds,
                        return_when=FIRST_COMPLETED,
                    )
                    collect(done)
                elif (
                    not self._stop_event.is_set()
                    and (cycles == 0 or index < int(cycles))
                    and idle_sleep_seconds
                ):
                    self._stop_event.wait(float(idle_sleep_seconds))

            if futures:
                done, _pending = wait(set(futures))
                collect(done)

        try:
            self._heartbeat_snapshot()
        except RuntimeError:
            pass
        return outcomes

