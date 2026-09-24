from __future__ import annotations

from datetime import datetime, timezone

CONSECUTIVE_FAILURE_THRESHOLD = 3
COST_SPIKE_RATIO = 2.0
BUSY_TELEMETRY_STALE_SECONDS = 180


def _parse_time(value):
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def derive_alerts(snapshot: dict) -> list[dict]:
    alerts = []
    workers = dict(snapshot.get("workers") or {})
    productions = dict(snapshot.get("productions") or {})
    performance = dict(snapshot.get("performance") or {})
    usage = dict(snapshot.get("usage") or {})

    queued = int(productions.get("queued") or 0)
    online = int(workers.get("online") or 0)
    if queued > 0 and online == 0:
        alerts.append({
            "code":"queue_without_worker",
            "severity":"high",
            "title":"Travail en attente sans worker",
            "message":f"{queued} productions sont en attente et aucun worker n'est en ligne.",
            "evidence":{"queued":queued,"online_workers":online},
        })

    consecutive_failures = int(performance.get("recent_failures") or 0)
    if consecutive_failures >= CONSECUTIVE_FAILURE_THRESHOLD:
        alerts.append({
            "code":"consecutive_failures",
            "severity":"high",
            "title":"Échecs consécutifs",
            "message":f"{consecutive_failures} exécutions récentes ont échoué consécutivement.",
            "evidence":{"consecutive_failures":consecutive_failures},
        })

    current_cost = usage.get("estimated_cost_usd")
    baseline = usage.get("cost_baseline_usd")
    if isinstance(current_cost, (int, float)) and not isinstance(current_cost, bool):
        if isinstance(baseline, (int, float)) and not isinstance(baseline, bool) and baseline > 0:
            ratio = float(current_cost) / float(baseline)
            if ratio > COST_SPIKE_RATIO:
                alerts.append({
                    "code":"cost_spike",
                    "severity":"medium",
                    "title":"Hausse du coût d'utilisation",
                    "message":"Le coût observé dépasse deux fois la référence disponible.",
                    "evidence":{
                        "estimated_cost_usd":float(current_cost),
                        "baseline_usd":float(baseline),
                        "ratio":ratio,
                    },
                })

    now = _parse_time(snapshot.get("generated_at")) or datetime.now(timezone.utc)
    stale_workers = []
    for worker in snapshot.get("busy_workers") or []:
        if not isinstance(worker, dict):
            continue
        if int(worker.get("active_tasks") or 0) <= 0:
            continue
        last = _parse_time(worker.get("last_heartbeat"))
        if last is None:
            continue
        age = max(0.0, (now - last).total_seconds())
        if age > BUSY_TELEMETRY_STALE_SECONDS:
            stale_workers.append({
                "worker_id":str(worker.get("worker_id") or ""),
                "age_seconds":round(age, 1),
            })
    if stale_workers:
        alerts.append({
            "code":"stale_busy_worker",
            "severity":"medium",
            "title":"Worker occupé sans télémétrie récente",
            "message":"Au moins un worker occupé ne remonte plus de heartbeat récent.",
            "evidence":{"workers":stale_workers},
        })

    severity_order = {"high":0, "medium":1, "low":2}
    alerts.sort(key=lambda item: (severity_order.get(item["severity"], 9), item["code"]))
    return alerts
