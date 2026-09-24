from __future__ import annotations

from .dashboard_store import DashboardStore

WORKER_STATES = {"active", "paused", "draining"}
JOB_STATES = {"active", "cancel_requested"}


class DashboardControlError(RuntimeError):
    pass


class DashboardControl:
    def __init__(
        self,
        store: DashboardStore,
        queue,
        workflows,
        *,
        github=None,
        actions_repository: str | None = None,
        actions_workflow: str | None = None,
        actions_ref: str = "main",
    ):
        self.store = store
        self.queue = queue
        self.workflows = workflows
        self.github = github
        self.actions_repository = actions_repository
        self.actions_workflow = actions_workflow
        self.actions_ref = actions_ref

    @staticmethod
    def _worker_view(row: dict | None, worker_id: str) -> dict:
        if row is None:
            return {
                "worker_id": worker_id,
                "desired_state": "active",
                "persisted": False,
                "reason": None,
                "requested_by": None,
                "requested_at": None,
                "updated_at": None,
                "acknowledged_at": None,
            }
        value = dict(row)
        value["persisted"] = True
        requested = value.get("requested_at")
        updated = value.get("updated_at")
        value["acknowledged_at"] = updated if requested and updated and updated != requested else None
        return value

    @staticmethod
    def _job_view(row: dict | None, job_key: str) -> dict:
        if row is None:
            return {
                "job_key": job_key,
                "desired_state": "active",
                "persisted": False,
                "reason": None,
                "requested_by": None,
                "requested_at": None,
                "updated_at": None,
                "acknowledged_at": None,
            }
        value = dict(row)
        value["persisted"] = True
        return value

    def worker_state(self, worker_id: str) -> dict:
        return self._worker_view(self.store.get_worker_control(worker_id), worker_id)

    def set_worker_state(
        self,
        worker_id: str,
        desired_state: str,
        *,
        requested_by: str,
        reason: str | None = None,
    ) -> dict:
        if desired_state not in WORKER_STATES:
            raise ValueError("invalid worker desired state")
        row = self.store.set_worker_control(
            worker_id,
            desired_state,
            requested_by=requested_by,
            reason=reason,
        )
        return self._worker_view(row, worker_id)

    def acknowledge_worker_state(
        self,
        worker_id: str,
        desired_state: str,
        *,
        at: str | None = None,
    ) -> dict:
        current = self.store.get_worker_control(worker_id)
        if current is None:
            if desired_state != "active":
                raise ValueError("stale worker desired state")
            return self.worker_state(worker_id)
        if current.get("desired_state") != desired_state:
            raise ValueError("stale worker desired state")
        row = self.store.acknowledge_worker_control(worker_id, desired_state, at=at)
        return self._worker_view(row, worker_id)

    def job_state(self, job_key: str) -> dict:
        return self._job_view(self.store.get_job_control(job_key), job_key)

    def request_job_cancel(
        self,
        job_key: str,
        *,
        requested_by: str,
        reason: str | None = None,
    ) -> dict:
        row = self.store.set_job_control(
            job_key,
            "cancel_requested",
            requested_by=requested_by,
            reason=reason,
        )
        return self._job_view(row, job_key)

    def acknowledge_job_cancel(self, job_key: str, *, at: str | None = None) -> dict:
        row = self.store.acknowledge_job_control(job_key, at=at)
        return self._job_view(row, job_key)

    def kick_worker(self, worker_id: str) -> dict:
        del worker_id
        if (
            self.github is None
            or not self.actions_repository
            or not self.actions_workflow
        ):
            return {
                "status":"scheduled_fallback",
                "poll_interval_seconds":300,
            }
        try:
            self.github.dispatch_workflow(
                self.actions_repository,
                self.actions_workflow,
                ref=self.actions_ref,
            )
        except Exception:
            return {
                "status":"failed",
                "error":"github_dispatch_failed",
            }
        return {
            "status":"dispatched",
        }

    def retry_job(self, job_key: str, *, requested_by: str) -> dict:
        job = self.queue.get(job_key)
        payload = job.get("payload") or {}
        workflow_id = str(payload.get("workflow_id") or "").strip()
        task_id = str(payload.get("workflow_task_id") or "").strip()
        if not workflow_id or not task_id:
            raise DashboardControlError("job is not linked to a workflow task")
        current = self.job_state(job_key)
        if (
            current["desired_state"] == "cancel_requested"
            and current.get("acknowledged_at") is None
        ):
            raise DashboardControlError("job cancellation is not acknowledged")
        try:
            replacement = self.workflows.retry_task(
                workflow_id,
                task_id,
                source_revision=(
                    str(payload.get("source_revision"))
                    if payload.get("source_revision") is not None
                    else None
                ),
                workflow_generation=(
                    int(payload.get("workflow_generation"))
                    if payload.get("workflow_generation") is not None
                    else None
                ),
            )
        except (KeyError, RuntimeError) as exc:
            raise DashboardControlError(str(exc)) from exc
        return {
            "requested_by":requested_by,
            "source_job_key":job_key,
            "replacement_job":replacement,
            "workflow_id":workflow_id,
            "workflow_task_id":task_id,
        }
