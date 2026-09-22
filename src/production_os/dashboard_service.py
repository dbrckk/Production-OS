from __future__ import annotations

from datetime import datetime, timezone

from .dashboard_usage import aggregate_usage


class DashboardNotFound(KeyError):
    pass


def _now():
    return datetime.now(timezone.utc).isoformat()


class DashboardService:
    def __init__(self, control):
        self.control=control
        self.store=control.dashboard_store

    def _worker_rows(self):
        with self.control.backend.connect() as db:
            rows=db.execute("SELECT * FROM workers ORDER BY worker_id").fetchall()
        return [dict(x) for x in rows]

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
          "commits":{"production_os":sum(int(x.get("commit_count") or 0) for x in executions),
                     "github_default_branch":0},
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
            for table in ("workflows","jobs","job_executions","project_repository_snapshots"):
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

    def project_progress(self,repository):
        self._require_project(repository)
        return {"repository":repository,"progress":self.store.latest_progress_snapshot(repository),
                "history":self.store.progress_history(repository),"generated_at":_now()}

    def project_commits(self,repository,window):
        self._require_project(repository)
        executions=self.store.executions_for_repository(repository,limit=500)
        return {"repository":repository,"window":window,
                "production_os":sum(int(x.get("commit_count") or 0) for x in executions),
                "github_default_branch":(self.store.latest_repository_snapshot(repository) or {}).get("github_commits"),
                "generated_at":_now()}

    def project_usage(self,repository,window):
        self._require_project(repository)
        return aggregate_usage(self.store.usage_events(repository=repository),window=window,
                               quota_rows=self.store.latest_provider_quota_snapshots())

    def project_workflows(self,repository):
        self._require_project(repository)
        with self.control.backend.connect() as db:
            rows=db.execute("SELECT id,name,status,created_at,updated_at FROM workflows WHERE repository=? ORDER BY created_at DESC LIMIT 100",(repository,)).fetchall()
        return {"repository":repository,"workflows":[dict(x) for x in rows],"generated_at":_now()}

    def project_history(self,repository):
        self._require_project(repository)
        return {"repository":repository,"executions":self.store.executions_for_repository(repository,limit=100),
                "progress":self.store.progress_history(repository,limit=100),"generated_at":_now()}

    def activity(self,*,repository=None,worker_id=None,event_type=None,after=0,limit=100):
        limit=max(1,min(500,int(limit)))
        rows=self.control.backend.events_after(int(after),limit)
        if repository: rows=[x for x in rows if x.get("repository")==repository]
        if event_type: rows=[x for x in rows if x.get("event_type")==event_type]
        return {"events":rows,"limit":limit,"generated_at":_now()}
