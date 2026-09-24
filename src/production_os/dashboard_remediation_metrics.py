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


def _bucket(rows: list[dict], *, now: datetime) -> dict:
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
    watching = sum(
        str(row.get("recurrence_state") or "not_evaluated") == "watching"
        for row in rows
    )
    recurred = sum(
        str(row.get("recurrence_state") or "") == "recurred"
        for row in rows
    )
    recurrence_denominator = watching + recurred
    recurrence_rate = (
        round(recurred / recurrence_denominator * 100, 2)
        if recurrence_denominator
        else None
    )
    recurrence_durations = []
    watching_ages = []
    for row in rows:
        state = str(row.get("recurrence_state") or "not_evaluated")
        verified = _parse_time(row.get("verified_at"))
        if verified is None:
            continue
        if state == "recurred":
            recurred_at = _parse_time(row.get("recurred_at"))
            if recurred_at is None or recurred_at < verified:
                continue
            recurrence_durations.append(
                (recurred_at - verified).total_seconds()
            )
        elif state == "watching" and now >= verified:
            watching_ages.append((now - verified).total_seconds())
    return {
        "total":total,
        "resolved":resolved,
        "still_active":still_active,
        "pending":pending,
        "not_applicable":not_applicable,
        "effectiveness_denominator":denominator,
        "observed_resolution_rate":resolution_rate,
        "watching_recurrence":watching,
        "recurred":recurred,
        "recurrence_denominator":recurrence_denominator,
        "observed_recurrence_rate":recurrence_rate,
        "median_time_to_recurrence_seconds":(
            round(float(median(recurrence_durations)), 2)
            if recurrence_durations
            else None
        ),
        "min_time_to_recurrence_seconds":(
            round(float(min(recurrence_durations)), 2)
            if recurrence_durations
            else None
        ),
        "max_time_to_recurrence_seconds":(
            round(float(max(recurrence_durations)), 2)
            if recurrence_durations
            else None
        ),
        "median_watching_age_seconds":(
            round(float(median(watching_ages)), 2)
            if watching_ages
            else None
        ),
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
            {"name":name, **_bucket(items, now=current)}
            for name, items in sorted(groups.items())
        ]

    return {
        "window":window,
        "summary":_bucket(selected, now=current),
        "by_action":grouped("action"),
        "by_incident_code":grouped("incident_code"),
    }
