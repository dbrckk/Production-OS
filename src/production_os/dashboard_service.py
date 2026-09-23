from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import uuid4
import json
import hashlib

from .dashboard_usage import aggregate_usage
from .project_progress import ProjectProgressEngine, build_project_evidence, workflow_progress


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

    def overview(self, window: str) -> dict:
        usage=aggregate_usage(self.store.usage_events(),window=window,
                              quota_rows=self.store.latest_provider_quota_snapshots())
        workers=self._worker_rows()
        executions=[]
        with self.control.backend.connect() as db:
            rows=db.execute("SELECT * FROM job_executions").fetchall()
            executions=[dict(x) for x in rows]
            jobs=db.execute("SELECT status,COUNT(*) AS count FROM jobs GROUP BY status").fetchall()
        states={str(x["status"]):int(x["count"]) for x in jobs}
        succeeded=sum(x.get("status")=="succeeded" for x in executions)
        finished=sum(x.get("status") in {"succeeded","failed","cancelled"} for x in executions)
        return {
          "schema_version":"production-os/dashboard-overview/v1","generated_at":_now(),
          "workers":{"total":len(workers),"online":sum(x.get("status")=="online" for x in workers),
                     "busy":sum(int(x.get("active_tasks") or 0)>0 for x in workers),
                     "paused":0,"offline":sum(x.get("status")!="online" for x in workers)},
          "productions":{"running":states.get("running",0),"queued":states.get("queued",0),
                         "succeeded":states.get("succeeded",0),"failed":states.get("failed",0)},
          "usage":{"api_calls":usage["totals"].get("api_calls"),
                   "tokens":usage["totals"].get("total_tokens"),
                   "estimated_cost_usd":usage["totals"].get("estimated_cost_usd")},
          "commits":{"production_os":len(self._distinct_commit_shas(self._executions_in_window(executions,window))),
                     "github_default_branch":None},
          "performance":{"success_rate":round(succeeded/finished*100,2) if finished else None,
                         "execution_seconds":sum(float(x.get("duration_seconds") or 0) for x in executions)},
          "projects":self.projects()["projects"],"errors":[]}

    def workers(self): return {"workers":self._worker_rows(),"generated_at":_now()}

    def worker_detail(self, worker_id):
        rows=[x for x in self._worker_rows() if x.get("worker_id")==worker_id]
        if not rows: raise DashboardNotFound(worker_id)
        return {"worker":rows[0],"executions":self.store.executions_for_worker(worker_id),"generated_at":_now()}

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
            "evidence":snapshot.get("evidence") or {},
            "remaining_work":snapshot.get("remaining_work") or [],
            "blockers":snapshot.get("blockers") or [],
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
        repository_snapshot=self.store.latest_repository_snapshot(repository)
        executions=self.store.executions_for_repository(repository,limit=500)
        events=self.control.backend.events_after(0,500)
        evidence=build_project_evidence(
            workflow=workflow,
            repository_snapshot=repository_snapshot,
            executions=executions,
            events=[x for x in events if x.get("repository")==repository],
            visual_quality=None,
        )
        calculated=ProjectProgressEngine().calculate(repository,evidence)
        calculated["evidence"]=evidence
        calculated["remaining_work"]=evidence.get("remaining_work") or []
        calculated["blockers"]=evidence.get("blockers") or []

        latest=self.store.latest_progress_snapshot(repository)
        workflow_id=workflow.get("id") if workflow else None
        meaningful=(
            latest is None
            or latest.get("current_workflow_id") != workflow_id
            or latest.get("production_progress") != production.get("percent")
            or latest.get("project_progress") != calculated.get("score")
            or latest.get("confidence") != calculated.get("confidence")
            or latest.get("calculation_version") != calculated.get("calculation_version")
        )
        if meaningful:
            components=calculated.get("components") or {}
            captured_at=calculated.get("captured_at") or _now()
            snapshot={
                "id":f"{repository}:{captured_at}",
                "repository":repository,
                "current_workflow_id":workflow_id,
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
                "captured_at":captured_at,
            }
            self.store.save_progress_snapshot(snapshot)
            latest=self.store.latest_progress_snapshot(repository)

        if latest:
            estimate={
                "repository":repository,
                "score":latest.get("project_progress"),
                "confidence":latest.get("confidence"),
                "calculation_version":latest.get("calculation_version"),
                "captured_at":latest.get("captured_at"),
                "evidence":latest.get("evidence"),
                "remaining_work":latest.get("remaining_work"),
                "blockers":latest.get("blockers"),
                "components":calculated.get("components") or {},
            }
        else:
            estimate=calculated
        return {
            "repository":repository,
            "current_workflow_id":workflow_id,
            "production":production,
            "estimate":estimate,
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
