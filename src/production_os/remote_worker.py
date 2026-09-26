from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RemoteJob:
    key: str
    payload: dict

    def to_dict(self) -> dict:
        return {"key": self.key, "payload": self.payload}


class RemoteWorkerClient:
    def __init__(
        self,
        base_url: str,
        token: str,
        worker_id: str,
        capabilities: list[str],
        *,
        timeout: float = 15.0,
    ):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.worker_id = worker_id
        self.capabilities = sorted(set(capabilities))
        self.timeout = timeout

    def _request(self, path: str, payload: dict | None = None) -> tuple[int, dict]:
        body = None if payload is None else json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            self.base_url + path,
            data=body,
            headers={
                "Authorization":f"Bearer {self.token}",
                "Content-Type":"application/json",
                "Accept":"application/json",
            },
            method="POST" if payload is not None else "GET",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                raw = response.read()
                return response.status, json.loads(raw or b"{}")
        except urllib.error.HTTPError as exc:
            raw = exc.read()
            payload = json.loads(raw or b"{}")
            raise RuntimeError(
                f"control-plane HTTP {exc.code}: {payload.get('error', payload)}"
            ) from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"control-plane unavailable: {exc}") from exc

    def open_session(
        self,
        *,
        max_concurrency: int = 1,
        active_job_keys: list[str] | None = None,
    ) -> dict:
        _, result = self._request(
            "/v1/workers/session",
            {
                "worker_id":self.worker_id,
                "capabilities":self.capabilities,
                "max_concurrency":int(max_concurrency),
                "active_job_keys":[
                    str(key)
                    for key in (active_job_keys or [])
                ],
            },
        )
        return result

    def heartbeat(
        self,
        active_tasks: int | None = None,
        *,
        active_job_keys: list[str] | None = None,
        control_state: str | None = None,
        job_control_states: dict[str, str] | None = None,
    ) -> dict:
        payload = {"worker_id":self.worker_id}
        if active_tasks is not None:
            payload["active_tasks"] = active_tasks
        if active_job_keys is not None:
            payload["active_job_keys"] = [
                str(key)
                for key in active_job_keys
            ]
        if control_state is not None:
            payload["control_state"] = str(control_state)
        if job_control_states is not None:
            payload["job_control_states"] = {
                str(key):str(value)
                for key, value in job_control_states.items()
            }
        _, result = self._request("/v1/workers/heartbeat", payload)
        return {
            "worker":result["worker"],
            "stale_job_keys":[
                str(key)
                for key in result.get("stale_job_keys", [])
            ],
            "control":dict(result.get("control") or {}),
        }

    def claim(self, ack_timeout_seconds: int = 120) -> RemoteJob | None:
        status, result = self._request(
            "/v1/jobs/claim",
            {
                "worker_id":self.worker_id,
                "capabilities":self.capabilities,
                "ack_timeout_seconds":ack_timeout_seconds,
            },
        )
        if status == 204 or not result.get("job"):
            return None
        job = result["job"]
        return RemoteJob(job["key"], job)

    def ack(self, key: str) -> dict:
        _, result = self._request(
            "/v1/jobs/ack",
            {"key":key,"worker_id":self.worker_id},
        )
        return result["job"]

    def checkpoint_stale(
        self,
        key: str,
        checkpoint_ref: str,
    ) -> dict:
        _, result = self._request(
            "/v1/jobs/stale-checkpoint",
            {
                "key":key,
                "worker_id":self.worker_id,
                "checkpoint_ref":checkpoint_ref,
            },
        )
        return result

    def complete(
        self,
        key: str,
        *,
        result_payload: dict | None = None,
        duration_seconds: float | None = None,
    ) -> dict:
        _, result = self._request(
            "/v1/jobs/complete",
            {
                "key":key,
                "worker_id":self.worker_id,
                "result":result_payload or {},
                **(
                    {"duration_seconds":float(duration_seconds)}
                    if duration_seconds is not None else {}
                ),
                "capabilities":self.capabilities,
            },
        )
        return result["job"]

    def fail(
        self,
        key: str,
        reason: str,
        *,
        result_payload: dict | None = None,
        duration_seconds: float | None = None,
    ) -> dict:
        _, result = self._request(
            "/v1/jobs/fail",
            {
                "key":key,
                "worker_id":self.worker_id,
                "reason":reason,
                "result":result_payload or {},
                **(
                    {"duration_seconds":float(duration_seconds)}
                    if duration_seconds is not None else {}
                ),
                "capabilities":self.capabilities,
            },
        )
        return result["job"]

    def poll(
        self,
        *,
        cycles: int = 1,
        interval_seconds: int = 5,
        ack_timeout_seconds: int = 120,
    ) -> list[RemoteJob]:
        if cycles < 1:
            raise ValueError("cycles must be >= 1")
        jobs: list[RemoteJob] = []
        for index in range(cycles):
            self.heartbeat()
            job = self.claim(ack_timeout_seconds=ack_timeout_seconds)
            if job is not None:
                jobs.append(job)
            if index + 1 < cycles and job is None:
                time.sleep(max(1, interval_seconds))
        return jobs
