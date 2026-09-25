from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import uuid4
import json
import os
import hashlib
import time

from .dashboard_usage import aggregate_usage
from .dashboard_alerts import derive_alerts
from .dashboard_health import derive_control_health
from .dashboard_incidents import dedupe_key, signals_from_health
from .dashboard_playbooks import derive_incident_playbook
from .dashboard_remediation_metrics import aggregate_remediation_analytics
from .dashboard_maintenance import prune_expired_history, storage_maintenance_snapshot
from .dashboard_backups import backup_readiness, backup_storage_inventory, create_verified_sqlite_backup, restore_activation_history, stage_verified_sqlite_restore, verify_backup_for_restore
from .project_progress import ProjectProgressEngine, build_project_evidence, workflow_progress
from .github_client import GitHubAPIError, GitHubClient


class DashboardNotFound(KeyError):
    pass


def _now():
    return datetime.now(timezone.utc).isoformat()


def _is_postgres(backend) -> bool:
    return backend.__class__.__name__.startswith("Postgres")


def _execute(db, backend, statement: str, params: tuple = ()):
    sql = statement.replace("?", "%s") if _is_postgres(backend) else statement
    return db.execute(sql, params)


class DashboardService:
    def __init__(self, control):
        self.control=control
        self.store=control.dashboard_store
        self._maintenance_cache=None
        self._maintenance_cache_at=0.0

    def _worker_rows(self):
        with self.control.backend.connect() as db:
            rows=db.execute("SELECT * FROM workers ORDER BY worker_id").fetchall()
        return [dict(x) for x in rows]

    @staticmethod
    def _distinct_commit_shas(executions: list[dict]) -> set[str]:
        shas: set[str] = set()
        for execution in executions:
            for sha in execution.get("commit_shas") or []:
                value = str(sha).strip().lower()
                if len(value) == 40 and all(ch in "0123456789abcdef" for ch in value):
                    shas.add(value)
        return shas

    @staticmethod
    def _window_cutoff(window: str):
        seconds={"24h":86400,"7d":604800,"30d":2592000,"all":None}
        if window not in seconds:
            raise ValueError("invalid window")
        value=seconds[window]
        return None if value is None else datetime.now(timezone.utc)-timedelta(seconds=value)

    def _executions_in_window(self, executions: list[dict], window: str) -> list[dict]:
        cutoff=self._window_cutoff(window)
        if cutoff is None:
            return executions
        selected=[]
        for row in executions:
            raw=row.get("finished_at") or row.get("started_at")
            if not raw:
                continue
            try:
                parsed=datetime.fromisoformat(str(raw).replace("Z","+00:00"))
                if parsed.tzinfo is None:
                    parsed=parsed.replace(tzinfo=timezone.utc)
            except ValueError:
                continue
            if parsed >= cutoff:
                selected.append(row)
        return selected

    @staticmethod
    def _previous_window_cost(rows: list[dict], window: str):
        seconds = {"24h":86400, "7d":604800, "30d":2592000}.get(window)
        if seconds is None:
            return None
        now = datetime.now(timezone.utc)
        start = now - timedelta(seconds=seconds * 2)
        end = now - timedelta(seconds=seconds)
        total = 0.0
        found = False
        for row in rows:
            raw = row.get("occurred_at")
            if not raw:
                continue
            try:
                occurred = datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
                if occurred.tzinfo is None:
                    occurred = occurred.replace(tzinfo=timezone.utc)
            except ValueError:
                continue
            if not (start <= occurred < end):
                continue
            cost = row.get("estimated_cost_usd")
            if isinstance(cost, (int, float)) and not isinstance(cost, bool):
                total += float(cost)
                found = True
        return total if found else None

    def overview(self, window: str) -> dict:
        usage_rows=self.store.usage_events()
        usage=aggregate_usage(usage_rows,window=window,
                              quota_rows=self.store.latest_provider_quota_snapshots())
        previous_cost=self._previous_window_cost(usage_rows, window)
        workers=self._worker_rows()
        executions=[]
        with self.control.backend.connect() as db:
            rows=db.execute("SELECT * FROM job_executions").fetchall()
            executions=[dict(x) for x in rows]
            jobs=db.execute("SELECT status,COUNT(*) AS count FROM jobs GROUP BY status").fetchall()
        states={str(x["status"]):int(x["count"]) for x in jobs}
        succeeded=sum(x.get("status")=="succeeded" for x in executions)
        finished=sum(x.get("status") in {"succeeded","failed","cancelled"} for x in executions)
        terminal = sorted(
            (
                row for row in executions
                if row.get("status") in {"succeeded","failed","cancelled"}
            ),
            key=lambda row: str(row.get("finished_at") or row.get("started_at") or ""),
            reverse=True,
        )
        recent_failures=0
        for row in terminal:
            if row.get("status") != "failed":
                break
            recent_failures += 1
        snapshot = {
          "schema_version":"production-os/dashboard-overview/v1","generated_at":_now(),
          "workers":{"total":len(workers),"online":sum(x.get("status")=="online" for x in workers),
                     "busy":sum(int(x.get("active_tasks") or 0)>0 for x in workers),
                     "paused":sum(
                         self.control.dashboard_control.worker_state(x["worker_id"])["desired_state"]=="paused"
                         for x in workers
                     ),
                     "offline":sum(x.get("status")!="online" for x in workers)},
          "productions":{"running":states.get("running",0),"queued":states.get("queued",0),
                         "succeeded":states.get("succeeded",0),"failed":states.get("failed",0)},
          "usage":{"api_calls":usage["totals"].get("api_calls"),
                   "tokens":usage["totals"].get("total_tokens"),
                   "estimated_cost_usd":usage["totals"].get("estimated_cost_usd"),
                   "cost_baseline_usd":previous_cost},
          "commits":{"production_os":len(self._distinct_commit_shas(self._executions_in_window(executions,window))),
                     "github_default_branch":None},
          "performance":{"success_rate":round(succeeded/finished*100,2) if finished else None,
                         "execution_seconds":sum(float(x.get("duration_seconds") or 0) for x in executions),
                         "recent_failures":recent_failures},
          "busy_workers":[x for x in workers if int(x.get("active_tasks") or 0)>0],
          "projects":self.projects()["projects"],"errors":[]}
        snapshot["alerts"]=derive_alerts(snapshot)
        snapshot.pop("busy_workers", None)
        return snapshot

    @staticmethod
    def _worker_capabilities(worker: dict) -> list[str]:
        value = worker.get("capabilities")
        if isinstance(value, list):
            return sorted({str(item) for item in value})
        raw = worker.get("capabilities_json")
        if isinstance(raw, str):
            try:
                parsed = json.loads(raw)
            except json.JSONDecodeError:
                parsed = []
            if isinstance(parsed, list):
                return sorted({str(item) for item in parsed})
        return []

    def autopilot_queue(self, limit: int = 50) -> dict:
        limit = max(1, min(200, int(limit)))
        queued = self.control.queue.peek_candidates(limit=limit)
        ranked = []
        for job in queued:
            try:
                ranked_item = self.control.portfolio.rank([job])[0]
                ranked_item["ranking_status"] = "ok"
                ranked_item["ranking_error"] = None
            except (KeyError, RuntimeError, ValueError):
                ranked_item = {
                    "job":job,
                    "score":float(job.get("priority") or 0.0),
                    "critical":False,
                    "descendants":0,
                    "predicted_minutes":None,
                    "age_minutes":None,
                    "ranking_status":"degraded",
                    "ranking_error":"workflow_unavailable",
                }
            ranked.append(ranked_item)
        ranked.sort(
            key=lambda item: (
                -float(item["score"]),
                str(item["job"].get("created_at") or ""),
                str(item["job"].get("key") or ""),
            )
        )
        workers = self._worker_rows()

        worker_views = []
        for worker in workers:
            worker_id = str(worker.get("worker_id") or "")
            desired = self.control.dashboard_control.worker_state(worker_id)
            item = {
                **worker,
                "worker_id":worker_id,
                "capabilities":self._worker_capabilities(worker),
                "desired_state":desired["desired_state"],
            }
            item["available"] = (
                item.get("status") == "online"
                and item["desired_state"] == "active"
                and int(item.get("active_tasks") or 0)
                    < int(item.get("max_concurrency") or 0)
            )
            worker_views.append(item)

        jobs = []
        for position, ranked_item in enumerate(ranked, start=1):
            job = ranked_item["job"]
            payload = dict(job.get("payload") or {})
            required = sorted({
                str(value)
                for value in payload.get("required_capabilities", [])
            })
            assigned = str(job.get("assigned_worker") or "").strip() or None

            scoped = [
                worker for worker in worker_views
                if assigned is None or worker["worker_id"] == assigned
            ]
            capable = [
                worker for worker in scoped
                if set(required).issubset(set(worker["capabilities"]))
            ]
            eligible = [
                worker for worker in capable
                if worker["available"]
            ]
            eligible.sort(
                key=lambda worker: (
                    int(worker.get("active_tasks") or 0)
                    / max(1, int(worker.get("max_concurrency") or 1)),
                    int(worker.get("active_tasks") or 0),
                    worker["worker_id"],
                )
            )

            wait_reason = None
            if not eligible:
                if assigned and not scoped:
                    wait_reason = "assigned_worker_unavailable"
                elif not scoped:
                    wait_reason = "no_worker"
                elif required and not capable:
                    wait_reason = "missing_capability"
                elif any(
                    worker.get("status") == "online"
                    and worker.get("desired_state") in {"paused", "draining"}
                    for worker in capable
                ):
                    wait_reason = "worker_controlled"
                elif any(
                    worker.get("status") == "online"
                    and int(worker.get("active_tasks") or 0)
                        >= int(worker.get("max_concurrency") or 0)
                    for worker in capable
                ):
                    wait_reason = "capacity_full"
                else:
                    wait_reason = "no_online_worker"

            jobs.append({
                "position":position,
                "job_key":job["key"],
                "repository":job["repository"],
                "task":job["task"],
                "priority":job.get("priority"),
                "score":ranked_item["score"],
                "ranking_status":ranked_item.get("ranking_status", "ok"),
                "ranking_error":ranked_item.get("ranking_error"),
                "critical":ranked_item["critical"],
                "descendants":ranked_item["descendants"],
                "predicted_minutes":ranked_item["predicted_minutes"],
                "age_minutes":ranked_item["age_minutes"],
                "required_capabilities":required,
                "assigned_worker":assigned,
                "eligible_workers":[worker["worker_id"] for worker in eligible],
                "preferred_worker":eligible[0]["worker_id"] if eligible else None,
                "wait_reason":wait_reason,
                "created_at":job.get("created_at"),
            })

        predicted = [
            float(job["predicted_minutes"])
            for job in jobs
            if isinstance(job.get("predicted_minutes"), (int, float))
            and not isinstance(job.get("predicted_minutes"), bool)
        ]
        free_slots = sum(
            max(
                0,
                int(worker.get("max_concurrency") or 0)
                - int(worker.get("active_tasks") or 0),
            )
            for worker in worker_views
            if worker.get("status") == "online"
            and worker.get("desired_state") == "active"
        )
        summary = {
            "ready_now":sum(1 for job in jobs if job.get("wait_reason") is None),
            "blocked":sum(1 for job in jobs if job.get("wait_reason") is not None),
            "free_slots":free_slots,
            "known_eta_minutes":round(sum(predicted), 2) if predicted else None,
            "eta_coverage_jobs":len(predicted),
            "eta_total_jobs":len(jobs),
        }
        return {
            "schema_version":"production-os/dashboard-autopilot/v1",
            "generated_at":_now(),
            "queued":len(jobs),
            "workers_available":sum(1 for worker in worker_views if worker["available"]),
            "summary":summary,
            "jobs":jobs,
        }

    def health(self) -> dict:
        workers = self._worker_rows()
        with self.control.backend.connect() as db:
            job_rows = db.execute(
                "SELECT status, COUNT(*) AS count FROM jobs GROUP BY status"
            ).fetchall()
            execution_rows = db.execute(
                """SELECT job_key, worker_id, started_at, last_telemetry_at
                   FROM job_executions
                   WHERE status='running'"""
            ).fetchall()
        states = {
            str(row["status"]):int(row["count"])
            for row in job_rows
        }
        snapshot = {
            "generated_at":_now(),
            "workers":{
                "online":sum(
                    row.get("status") == "online"
                    for row in workers
                ),
            },
            "productions":{
                "queued":states.get("queued", 0),
            },
            "worker_rows":workers,
            "running_executions":[dict(row) for row in execution_rows],
        }
        return derive_control_health(snapshot)

    def incidents(
        self,
        *,
        limit: int = 100,
        status: str | None = None,
    ) -> dict:
        health = self.health()
        signals = signals_from_health(health)
        active_keys: set[str] = set()
        for signal in signals:
            active_keys.add(dedupe_key(signal))
            self.store.upsert_dashboard_incident(**signal)
        self.store.resolve_dashboard_incidents_except(active_keys)
        self.store.verify_remediation_events()
        self.store.verify_remediation_recurrence()
        if status is not None and status not in {
            "open","acknowledged","resolved"
        }:
            raise ValueError("invalid incident status")
        rows = self.store.dashboard_incidents(
            limit=limit,
            status=status,
        )
        kick_mode = (
            "immediate"
            if (
                self.control.dashboard_control.github is not None
                and self.control.dashboard_control.actions_repository
                and self.control.dashboard_control.actions_workflow
            )
            else "scheduled_fallback"
        )
        enriched = []
        for incident in rows:
            item = dict(incident)
            recoverable_jobs = []
            job = None
            if (
                item.get("code") == "stale_busy_workers"
                and item.get("target_type") == "worker"
            ):
                with self.control.backend.connect() as db:
                    found = _execute(
                        db,
                        self.control.backend,
                        """SELECT key, repository, task, delivery_attempt, ack_deadline
                           FROM jobs
                           WHERE claimed_by=? AND status='claimed'
                             AND ack_deadline IS NOT NULL AND ack_deadline <= ?
                           ORDER BY ack_deadline ASC""",
                        (item.get("target_id"), _now()),
                    ).fetchall()
                recoverable_jobs = [dict(row) for row in found]
            elif (
                item.get("code") == "stale_running_executions"
                and item.get("target_type") == "job"
            ):
                try:
                    job = self.control.queue.get(str(item.get("target_id")))
                except KeyError:
                    job = None
            item["playbook"] = derive_incident_playbook(
                item,
                actions_kick_mode=kick_mode,
                recoverable_jobs=recoverable_jobs,
                job=job,
            )
            enriched.append(item)
        return {
            "incidents":enriched,
            "health_status":health["status"],
            "generated_at":_now(),
        }

    def remediation_history(
        self,
        *,
        limit: int = 100,
        incident_id: str | None = None,
    ) -> dict:
        # Refresh durable incident state first so verification reflects
        # current server facts rather than stale browser state.
        self.incidents(limit=500)
        return {
            "events":self.store.remediation_events(
                limit=limit,
                incident_id=incident_id,
            ),
            "generated_at":_now(),
        }

    def remediation_analytics(self, window: str) -> dict:
        self.incidents(limit=500)
        payload = aggregate_remediation_analytics(
            self.store.remediation_analytics_rows(),
            window=window,
        )
        return {
            **payload,
            "generated_at":_now(),
        }

    def backups(self) -> dict:
        return {
            **backup_readiness(self.control.backend),
            "storage":backup_storage_inventory(
                self.control.backend,
            ),
            "activations":restore_activation_history(
                self.control.backend,
                limit=50,
            ),
            "generated_at":_now(),
        }

    def create_verified_backup(self) -> dict:
        return {
            **create_verified_sqlite_backup(self.control.backend),
            "restore_enabled":False,
        }

    def verify_backup_restore_readiness(self, backup_id: str) -> dict:
        return verify_backup_for_restore(
            self.control.backend,
            backup_id,
        )

    def stage_backup_restore(self, backup_id: str) -> dict:
        return stage_verified_sqlite_restore(
            self.control.backend,
            backup_id,
        )

    def control_audit(self, limit: int = 100) -> dict:
        return {
            "events":self.store.control_audit_events(limit=limit),
            "generated_at":_now(),
        }

    def workers(self):
        rows=[]
        for worker in self._worker_rows():
            desired=self.control.dashboard_control.worker_state(worker["worker_id"])
            item=dict(worker)
            item["desired_state"]=desired["desired_state"]
            item["control_requested_at"]=desired.get("requested_at")
            item["control_reason"]=desired.get("reason")
            if desired["desired_state"] == "draining" and int(item.get("active_tasks") or 0) == 0:
                item["display_state"]="drained"
            rows.append(item)
        return {"workers":rows,"generated_at":_now()}

    def worker_detail(self, worker_id):
        rows=[x for x in self._worker_rows() if x.get("worker_id")==worker_id]
        if not rows: raise DashboardNotFound(worker_id)
        worker=dict(rows[0])
        desired=self.control.dashboard_control.worker_state(worker_id)
        worker["desired_state"]=desired["desired_state"]
        worker["control_requested_at"]=desired.get("requested_at")
        worker["control_reason"]=desired.get("reason")
        worker["control_acknowledged_at"]=desired.get("acknowledged_at")
        if desired["desired_state"] == "draining" and int(worker.get("active_tasks") or 0) == 0:
            worker["display_state"]="drained"
        with self.control.backend.connect() as db:
            recoverable_rows = _execute(
                db,
                self.control.backend,
                """SELECT key, repository, task, delivery_attempt, ack_deadline
                   FROM jobs
                   WHERE claimed_by=? AND status='claimed'
                     AND ack_deadline IS NOT NULL AND ack_deadline <= ?
                   ORDER BY ack_deadline ASC""",
                (worker_id, _now()),
            ).fetchall()
        return {
            "worker":worker,
            "executions":self.store.executions_for_worker(worker_id),
            "recoverable_jobs":[dict(row) for row in recoverable_rows],
            "generated_at":_now(),
        }

    def worker_logs(self,worker_id,after,limit):
        self.worker_detail(worker_id)
        limit=max(1,min(500,int(limit)))
        return {"logs":self.store.logs_for_worker(worker_id,after=after,limit=limit),"limit":limit,"generated_at":_now()}

    def worker_usage(self,worker_id,window):
        self.worker_detail(worker_id)
        return aggregate_usage(self.store.usage_events(worker_id=worker_id),window=window,
                               quota_rows=self.store.latest_provider_quota_snapshots())

    def _repositories(self):
        found=set()
        with self.control.backend.connect() as db:
            for table in ("workflows","jobs","job_executions","project_repository_snapshots","execution_history"):
                try:
                    rows=db.execute(f"SELECT DISTINCT repository FROM {table} WHERE repository IS NOT NULL").fetchall()
                    found.update(str(x["repository"]) for x in rows if x["repository"])
                except Exception:
                    continue
        return sorted(found)

    def maintenance(self, *, force: bool = False) -> dict:
        now = time.monotonic()
        cached = self._maintenance_cache
        if not force and cached is not None:
            ttl = 30.0 if cached.get("status") == "unknown" else 300.0
            if now - self._maintenance_cache_at < ttl:
                return {**cached, "cached":True}
        payload = storage_maintenance_snapshot(self.control.backend)
        self._maintenance_cache = dict(payload)
        self._maintenance_cache_at = now
        return {**payload, "cached":False}

    def prune_maintenance(self, expected_candidate_rows: int) -> dict:
        result = prune_expired_history(
            self.control.backend,
            expected_candidate_rows=expected_candidate_rows,
        )
        self._maintenance_cache = None
        self._maintenance_cache_at = 0.0
        return {
            **result,
            "maintenance":self.maintenance(force=True),
        }

    def repositories(self) -> dict:
        owner = str(
            os.getenv("PRODUCTION_OS_GITHUB_OWNER") or "dbrckk"
        ).strip() or "dbrckk"
        github = GitHubClient()
        source = "github"
        try:
            rows = github.list_accessible_repositories(owner)
        except GitHubAPIError:
            source = "observed-projects"
            rows = [
                {
                    "full_name":item.get("repository"),
                    "private":False,
                    "archived":False,
                    "default_branch":None,
                    "pushed_at":None,
                }
                for item in self.projects().get("projects", [])
            ]
        repositories = []
        for row in rows:
            if not isinstance(row, dict) or bool(row.get("archived", False)):
                continue
            full_name = str(row.get("full_name") or "").strip()
            if not full_name:
                continue
            repositories.append({
                "full_name":full_name,
                "private":bool(row.get("private", False)),
                "default_branch":row.get("default_branch"),
                "pushed_at":row.get("pushed_at"),
            })
        repositories.sort(key=lambda item: item["full_name"].lower())
        return {
            "owner":owner,
            "source":source,
            "repositories":repositories,
            "generated_at":_now(),
        }

    def projects(self):
        return {"projects":[{"repository":r,"snapshot":self.store.latest_repository_snapshot(r),
                             "progress":self.store.latest_progress_snapshot(r)} for r in self._repositories()],
                "generated_at":_now()}

    def _require_project(self,repository):
        if repository not in self._repositories(): raise DashboardNotFound(repository)

    def project_detail(self,repository):
        self._require_project(repository)
        return {"repository":repository,"snapshot":self.store.latest_repository_snapshot(repository),
                "progress":self.store.latest_progress_snapshot(repository),"generated_at":_now()}

    @staticmethod
    def _progress_snapshot_state(snapshot):
        if not snapshot:
            return None
        return {
            "current_workflow_id":snapshot.get("current_workflow_id"),
            "production_progress":snapshot.get("production_progress"),
            "project_progress":snapshot.get("project_progress"),
            "confidence":snapshot.get("confidence"),
            "code_score":snapshot.get("code_score"),
            "ui_ux_score":snapshot.get("ui_ux_score"),
            "assets_score":snapshot.get("assets_score"),
            "tests_score":snapshot.get("tests_score"),
            "stability_score":snapshot.get("stability_score"),
            "release_score":snapshot.get("release_score"),
            "evidence":snapshot.get("evidence") or snapshot.get("evidence_json") or {},
            "remaining_work":snapshot.get("remaining_work") or snapshot.get("remaining_work_json") or [],
            "blockers":snapshot.get("blockers") or snapshot.get("blockers_json") or [],
            "calculation_version":snapshot.get("calculation_version"),
        }

    def project_progress(self,repository):
        self._require_project(repository)
        with self.control.backend.connect() as db:
            rows=_execute(
                db, self.control.backend,
                "SELECT id FROM workflows WHERE repository=? ORDER BY updated_at DESC LIMIT 1",
                (repository,),
            ).fetchall()
        workflow=self.control.workflows.get(str(rows[0]["id"])) if rows else None
        production=workflow_progress(workflow) if workflow else {
            "percent":None,"completed_weight":0.0,"total_weight":0.0,
        }
        snapshot=self.store.latest_repository_snapshot(repository)
        executions=self.store.executions_for_repository(repository,limit=500)
        events=self.control.backend.events_after(0,500)
        evidence=build_project_evidence(
            workflow=workflow,
            repository_snapshot=snapshot,
            executions=executions,
            events=[x for x in events if x.get("repository")==repository],
            visual_quality=None,
        )
        calculated=ProjectProgressEngine().calculate(repository,evidence)
        calculated["evidence"]=evidence
        calculated["remaining_work"]=evidence.get("remaining_work") or []
        calculated["blockers"]=evidence.get("blockers") or []
        components=calculated.get("components") or {}
        candidate={
            "repository":repository,
            "current_workflow_id":workflow.get("id") if workflow else None,
            "production_progress":production.get("percent"),
            "project_progress":calculated.get("score"),
            "confidence":calculated.get("confidence"),
            "code_score":(components.get("code") or {}).get("score"),
            "ui_ux_score":(components.get("ui_ux") or {}).get("score"),
            "assets_score":(components.get("assets") or {}).get("score"),
            "tests_score":(components.get("tests") or {}).get("score"),
            "stability_score":(components.get("stability") or {}).get("score"),
            "release_score":(components.get("release") or {}).get("score"),
            "evidence_json":evidence,
            "remaining_work_json":calculated["remaining_work"],
            "blockers_json":calculated["blockers"],
            "calculation_version":calculated.get("calculation_version"),
            "captured_at":calculated.get("captured_at"),
        }
        candidate_state=self._progress_snapshot_state(candidate)
        fingerprint=hashlib.sha256(json.dumps(candidate_state,sort_keys=True,separators=(",",":"),default=str).encode()).hexdigest()
        candidate["id"]=repository+":"+fingerprint
        persisted=self.store.latest_progress_snapshot(repository)
        meaningful=self._progress_snapshot_state(persisted) != candidate_state
        if meaningful:
            persisted=self.store.save_progress_snapshot(candidate)
        if persisted:
            calculated["captured_at"]=persisted.get("captured_at")
        return {
            "repository":repository,
            "current_workflow_id":workflow.get("id") if workflow else None,
            "production":production,
            "estimate":calculated,
            "history":self.store.progress_history(repository),
            "generated_at":_now(),
        }

    def project_commits(self,repository,window):
        self._require_project(repository)
        executions=self._executions_in_window(self.store.executions_for_repository(repository,limit=500),window)
        return {"repository":repository,"window":window,
                "production_os":len(self._distinct_commit_shas(executions)),
                "github_default_branch":(self.store.latest_repository_snapshot(repository) or {}).get("github_commits"),
                "generated_at":_now()}

    def _legacy_workflow_usage_rows(self, repository):
        with self.control.backend.connect() as db:
            modern_rows=_execute(
                db,self.control.backend,
                "SELECT workflow_id,workflow_task_id FROM job_executions WHERE repository=?",
                (repository,),
            ).fetchall()
            modern_pairs={
                (str(row["workflow_id"]),str(row["workflow_task_id"]))
                for row in modern_rows
                if row["workflow_id"] is not None and row["workflow_task_id"] is not None
            }
            rows=_execute(
                db,self.control.backend,
                """SELECT wt.workflow_id,wt.task_id,wt.result_json,wt.updated_at
                   FROM workflow_tasks wt
                   JOIN workflows w ON w.id=wt.workflow_id
                   WHERE w.repository=? AND wt.result_json IS NOT NULL""",
                (repository,),
            ).fetchall()
        usage_rows=[]
        for row in rows:
            if (str(row["workflow_id"]),str(row["task_id"])) in modern_pairs:
                continue
            try:
                result=json.loads(row["result_json"]) if isinstance(row["result_json"],str) else row["result_json"]
            except (TypeError,ValueError,json.JSONDecodeError):
                continue
            usage=(result or {}).get("usage") if isinstance(result,dict) else None
            providers=usage.get("providers") if isinstance(usage,dict) else None
            if not isinstance(providers,list):
                continue
            for provider in providers:
                if not isinstance(provider,dict):
                    continue
                usage_rows.append({
                    "occurred_at":row["updated_at"],
                    "provider":provider.get("provider"),
                    "model":provider.get("model"),
                    "api_calls":provider.get("api_calls"),
                    "input_tokens":provider.get("input_tokens"),
                    "cached_input_tokens":provider.get("cached_input_tokens"),
                    "output_tokens":provider.get("output_tokens"),
                    "reasoning_tokens":provider.get("reasoning_tokens"),
                    "total_tokens":provider.get("total_tokens"),
                    "estimated_cost_usd":provider.get("estimated_cost_usd"),
                })
        return usage_rows

    def project_usage(self,repository,window):
        self._require_project(repository)
        current=self.store.usage_events(repository=repository)
        legacy=self._legacy_workflow_usage_rows(repository)
        payload=aggregate_usage(current+legacy,window=window,
                                quota_rows=self.store.latest_provider_quota_snapshots())
        payload["history_coverage"]="partial" if legacy else "complete"
        return payload

    def project_workflows(self,repository):
        self._require_project(repository)
        with self.control.backend.connect() as db:
            rows=_execute(db,self.control.backend,"SELECT id,name,status,created_at,updated_at FROM workflows WHERE repository=? ORDER BY created_at DESC LIMIT 100",(repository,)).fetchall()
        return {"repository":repository,"workflows":[dict(x) for x in rows],"generated_at":_now()}

    def project_history(self,repository):
        self._require_project(repository)
        executions=self.store.executions_for_repository(repository,limit=100)
        with self.control.backend.connect() as db:
            rows=_execute(
                db,self.control.backend,
                "SELECT repository,task,worker_id,duration_seconds,succeeded,created_at FROM execution_history WHERE repository=? ORDER BY created_at DESC LIMIT 100",
                (repository,),
            ).fetchall()
        legacy=[dict(x) for x in rows]
        coverage="complete"
        if legacy:
            coverage="partial"
        return {
            "repository":repository,
            "executions":executions,
            "legacy_executions":legacy,
            "history_coverage":coverage,
            "progress":self.store.progress_history(repository,limit=100),
            "generated_at":_now(),
        }

    def activity(self,*,repository=None,worker_id=None,event_type=None,after=0,limit=100):
        limit=max(1,min(500,int(limit)))
        rows=self.control.backend.events_after(int(after),limit)
        if repository: rows=[x for x in rows if x.get("repository")==repository]
        if worker_id:
            rows=[x for x in rows if str((x.get("payload") or {}).get("worker_id") or "")==worker_id]
        if event_type: rows=[x for x in rows if x.get("event_type")==event_type]
        return {"events":rows,"limit":limit,"generated_at":_now()}
