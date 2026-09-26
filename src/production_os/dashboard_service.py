from __future__ import annotations
import threading
from .dashboard_service_legacy import *
from .dashboard_service_legacy import DashboardService as _BaseDashboardService
from .dashboard_service_legacy import _now

_request_state = threading.local()
def set_request_production_filter(value):
    _request_state.production_filter = value
def _take_request_production_filter():
    value = getattr(_request_state, "production_filter", None)
    _request_state.production_filter = None
    return value

class DashboardService(_BaseDashboardService):
    def production_inbox(self, *, limit: int = 50, category: str | None = None) -> dict:
        if category is None:
            category = _take_request_production_filter()
        bounded = max(1, min(200, int(limit)))
        selected_filter = str(category or "all").strip().lower()
        allowed = {"all", "active", "review", "problems", "completed"}
        if selected_filter not in allowed:
            raise ValueError("invalid production inbox filter")
        managed = self.control.managed_projects.list(limit=500)
        allowed_statuses = {"ACTIVE", "REVIEW_REQUIRED", "NEEDS_ATTENTION", "DONE"}
        candidates = [p for p in managed if str(p.get("status") or "") in allowed_statuses]
        items = []
        phase_counts = {}
        live_phases = {"preparing", "queued", "claimed", "running", "cancelling"}
        for project in candidates:
            project_id = str(project.get("project_id") or project.get("id") or "")
            if not project_id:
                continue
            status = self.production_status(project_id)
            current = status.get("project") or project
            runtime = status.get("runtime") or {}
            phase = str(runtime.get("phase") or "preparing")
            phase_counts[phase] = phase_counts.get(phase, 0) + 1
            items.append({"project_id":project_id,"repository":current.get("repository"),"final_goal":current.get("final_goal"),"generation":current.get("generation"),"status":current.get("status"),"updated_at":current.get("updated_at"),"outcome":current.get("outcome") or {},"runtime":runtime})
        def group(item):
            phase = str((item.get("runtime") or {}).get("phase") or "preparing")
            if phase == "needs_attention": return "problems"
            if phase == "review_required": return "review"
            if phase == "done": return "completed"
            return "active"
        priority = {"problems":0,"review":1,"active":2,"completed":3}
        items.sort(key=lambda item:(priority[group(item)],str(item.get("updated_at") or ""),str(item.get("project_id") or "")))
        filtered = items if selected_filter == "all" else [item for item in items if group(item) == selected_filter]
        visible = filtered[:bounded]
        summary = {"visible":len(visible),"total":len(items),"active":sum(count for phase,count in phase_counts.items() if phase in live_phases),"preparing":phase_counts.get("preparing",0),"queued":phase_counts.get("queued",0),"claimed":phase_counts.get("claimed",0),"running":phase_counts.get("running",0),"cancelling":phase_counts.get("cancelling",0),"review_required":phase_counts.get("review_required",0),"needs_attention":phase_counts.get("needs_attention",0),"done":phase_counts.get("done",0)}
        return {"schema_version":"production-os/production-inbox/v1","generated_at":_now(),"filter":selected_filter,"summary":summary,"items":visible}
