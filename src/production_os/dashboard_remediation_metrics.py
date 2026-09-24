from __future__ import annotations

from datetime import datetime, timedelta, timezone
from statistics import median


WINDOW_SECONDS = {
    "24h": 86400,
    "7d": 604800,
    "30d": 2592000,
    "all": None,
}


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


def _bucket(rows: list[dict]) -> dict:
    total = len(rows)
    resolved = sum(
        str(row.get("verification_state") or "") == "resolved"
        for row in rows
    )
    still_active = sum(
        str(row.get("verification_state") or "") == "still_active"
        for row in rows
    )
    pending = sum(
        str(row.get("verification_state") or "pending") == "pending"
        for row in rows
    )
    not_applicable = sum(
        str(row.get("verification_state") or "") == "not_applicable"
        for row in rows
    )
    denominator = resolved + still_active
    resolution_rate = (
        round(resolved / denominator * 100, 2)
        if denominator
        else None
    )
    durations = []
    for row in rows:
        if str(row.get("verification_state") or "") != "resolved":
            continue
        completed = _parse_time(row.get("completed_at"))
        verified = _parse_time(row.get("verified_at"))
        if completed is None or verified is None or verified < completed:
            continue
        durations.append((verified - completed).total_seconds())
    return {
        "total":total,
        "resolved":resolved,
        "still_active":still_active,
        "pending":pending,
        "not_applicable":not_applicable,
        "effectiveness_denominator":denominator,
        "observed_resolution_rate":resolution_rate,
        "median_resolution_detection_seconds":(
            round(float(median(durations)), 2)
            if durations
            else None
        ),
    }


def aggregate_remediation_analytics(
    rows: list[dict],
    *,
    window: str,
    now: datetime | None = None,
) -> dict:
    if window not in WINDOW_SECONDS:
        raise ValueError("invalid window")
    current = now or datetime.now(timezone.utc)
    if current.tzinfo is None:
        current = current.replace(tzinfo=timezone.utc)
    seconds = WINDOW_SECONDS[window]
    cutoff = (
        None
        if seconds is None
        else current - timedelta(seconds=seconds)
    )
    selected = []
    for row in rows:
        requested = _parse_time(row.get("requested_at"))
        if requested is None:
            continue
        if cutoff is not None and requested < cutoff:
            continue
        selected.append(dict(row))

    def grouped(key: str) -> list[dict]:
        groups: dict[str, list[dict]] = {}
        for row in selected:
            value = str(row.get(key) or "unknown")
            groups.setdefault(value, []).append(row)
        return [
            {"name":name, **_bucket(items)}
            for name, items in sorted(groups.items())
        ]

    return {
        "window":window,
        "summary":_bucket(selected),
        "by_action":grouped("action"),
        "by_incident_code":grouped("incident_code"),
    }
