from __future__ import annotations

from datetime import datetime, timezone

PROFILES = {
    "visual_app":{"code":.25,"ui_ux":.15,"assets":.15,"tests":.15,"stability":.15,"release":.15},
    "backend":{"code":.35,"tests":.25,"stability":.20,"release":.20},
    "generic":{"code":.35,"ui_ux":.10,"assets":.10,"tests":.15,"stability":.15,"release":.15},
}
DIMENSIONS=("code","ui_ux","assets","tests","stability","release")
CALCULATION_VERSION="project-progress/v1"
CONFIDENCE_HIGH=.80
CONFIDENCE_MEDIUM=.50
_COMPLETE={"succeeded","impact_skipped"}


def workflow_progress(workflow: dict) -> dict:
    tasks=workflow.get("tasks") or []
    total=0.0; completed=0.0
    for task in tasks:
        try: weight=max(0.0,float(task.get("estimated_minutes") or 0))
        except (TypeError,ValueError): weight=0.0
        if weight<=0: continue
        total+=weight
        if str(task.get("status") or "") in _COMPLETE: completed+=weight
    return {"percent":round(completed/total*100,2) if total else None,
            "completed_weight":completed,"total_weight":total}


def _execution_summary(rows):
    total=len(rows); succeeded=sum(str(x.get("status"))=="succeeded" for x in rows)
    return {"count":total,"succeeded":succeeded,
            "success_rate":round(succeeded/total*100,2) if total else None}


def _relevant_progress_events(rows):
    return [dict(x) for x in rows[-50:] if isinstance(x,dict)]


def build_project_evidence(*,workflow,repository_snapshot,executions,events,visual_quality):
    out={"dimensions":{},"remaining_work":[],"blockers":[],
         "execution_summary":_execution_summary(executions or []),
         "recent_events":_relevant_progress_events(events or [])}
    if workflow: out["workflow"]=workflow_progress(workflow)
    if repository_snapshot:
        out["repository"]={k:repository_snapshot.get(k) for k in
          ("ci_status","latest_release","tests_detected","tests_passing","tests_failing")}
    if visual_quality: out["visual_quality"]=dict(visual_quality)
    return out


class ProjectProgressEngine:
    def calculate(self,repository: str,evidence: dict,*,captured_at: str|None=None)->dict:
        profile=str(evidence.get("profile") or "generic")
        weights=PROFILES.get(profile,PROFILES["generic"])
        supplied=evidence.get("dimensions") or {}
        components={}
        weighted=0.0; known_weight=0.0; fresh_weight=0.0
        stale_critical=False
        for name in DIMENSIONS:
            if name not in weights:
                components[name]={"status":"not_applicable","score":None}
                continue
            item=supplied.get(name)
            if not isinstance(item,dict) or not isinstance(item.get("score"),(int,float)):
                components[name]={"status":"unknown","score":None}
                continue
            score=max(0.0,min(100.0,float(item["score"])))
            fresh=item.get("fresh") is True
            components[name]={"status":"observed","score":score,"fresh":fresh,
                              "evidence":item.get("evidence")}
            w=weights[name]; weighted+=score*w; known_weight+=w
            if fresh: fresh_weight+=w
            elif name in {"code","tests","stability","release"}: stale_critical=True
        score=round(weighted/known_weight,2) if known_weight else None
        coverage=fresh_weight/sum(weights.values()) if weights else 0.0
        confidence=("high" if coverage>=CONFIDENCE_HIGH and not stale_critical
                    else "medium" if coverage>=CONFIDENCE_MEDIUM else "low")
        return {"repository":repository,"score":score,"confidence":confidence,
                "coverage":round(coverage,3),"components":components,"profile":profile,
                "calculation_version":CALCULATION_VERSION,
                "captured_at":captured_at or datetime.now(timezone.utc).isoformat()}
