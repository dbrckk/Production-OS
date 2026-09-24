from __future__ import annotations


ACTIVE_JOB_STATUSES = {"claimed", "acked", "running"}


def derive_incident_playbook(
    incident: dict,
    *,
    actions_kick_mode: str = "scheduled_fallback",
    recoverable_jobs: list[dict] | None = None,
    job: dict | None = None,
) -> dict:
    code = str(incident.get("code") or "")
    target_type = str(incident.get("target_type") or "")
    target_id = str(incident.get("target_id") or "")
    suggestions: list[dict] = []

    if str(incident.get("status") or "") == "resolved":
        return {
            "incident_id":incident.get("id"),
            "code":code,
            "suggestions":[],
        }

    if code == "queue_without_worker":
        availability = (
            "available"
            if actions_kick_mode == "immediate"
            else "fallback"
        )
        suggestions.append({
            "action":"kick",
            "worker_id":"github-actions-worker",
            "job_key":None,
            "availability":availability,
            "reason":(
                "Réveil GitHub Actions immédiat configuré."
                if availability == "available"
                else "Réveil immédiat non configuré; le worker planifié reste disponible."
            ),
            "interrupting":False,
        })

    elif code == "stale_busy_workers" and target_type == "worker":
        suggestions.append({
            "action":"inspect-worker",
            "worker_id":target_id,
            "job_key":None,
            "availability":"available",
            "reason":"Inspecter le worker et ses tâches avant toute récupération.",
            "interrupting":False,
        })
        for row in recoverable_jobs or []:
            key = str(row.get("key") or "")
            if not key:
                continue
            suggestions.append({
                "action":"recover-stuck",
                "worker_id":target_id,
                "job_key":key,
                "availability":"available",
                "reason":"Le claim est expiré et peut être récupéré de façon ciblée.",
                "interrupting":True,
            })

    elif code == "stale_running_executions" and target_type == "job":
        owner = str((job or {}).get("claimed_by") or "")
        status = str((job or {}).get("status") or "")
        suggestions.append({
            "action":"inspect-job",
            "worker_id":owner or None,
            "job_key":target_id,
            "availability":"available",
            "reason":"Inspecter l'exécution et sa télémétrie avant intervention.",
            "interrupting":False,
        })
        if owner and status in ACTIVE_JOB_STATUSES:
            suggestions.append({
                "action":"cancel-current",
                "worker_id":owner,
                "job_key":target_id,
                "availability":"available",
                "reason":"Le job est encore actif et appartient explicitement à ce worker.",
                "interrupting":True,
            })
        else:
            suggestions.append({
                "action":"cancel-current",
                "worker_id":owner or None,
                "job_key":target_id,
                "availability":"unavailable",
                "reason":"Le job n'est plus actif ou son propriétaire n'est pas établi.",
                "interrupting":True,
            })

    return {
        "incident_id":incident.get("id"),
        "code":code,
        "suggestions":suggestions,
    }
