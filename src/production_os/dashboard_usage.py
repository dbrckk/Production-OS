"""Versioned pricing and safe historical API-usage aggregation."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

WINDOW_SECONDS = {
    "24h": 24 * 60 * 60,
    "7d": 7 * 24 * 60 * 60,
    "30d": 30 * 24 * 60 * 60,
    "all": None,
}
_TOKEN_FIELDS = (
    "input_tokens",
    "cached_input_tokens",
    "output_tokens",
    "reasoning_tokens",
)


def _dt(value):
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    raw = str(value or "").strip()
    if raw.endswith("Z"):
        raw = raw[:-1] + "+00:00"
    parsed = datetime.fromisoformat(raw)
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


class PricingCatalog:
    def __init__(self, version, rules):
        self.version = str(version)
        self.rules = tuple(dict(rule) for rule in rules)

    @classmethod
    def from_mapping(cls, payload):
        if not isinstance(payload, dict):
            raise ValueError("pricing catalog must be an object")
        rules = payload.get("rules", [])
        if not isinstance(rules, list):
            raise ValueError("pricing rules must be a list")
        return cls(payload.get("version") or "", rules)

    def estimate(self, provider, model, usage, at):
        if not isinstance(usage, dict) or any(
            field not in usage for field in _TOKEN_FIELDS
        ):
            return None, None
        when = _dt(at)
        for rule in self.rules:
            if rule.get("provider") != provider or rule.get("model") != model:
                continue
            start = _dt(rule["valid_from"])
            end = _dt(rule["valid_to"]) if rule.get("valid_to") else None
            if when < start or (end is not None and when >= end):
                continue
            rates = {
                "input_tokens": "input_per_million_usd",
                "cached_input_tokens": "cached_input_per_million_usd",
                "output_tokens": "output_per_million_usd",
                "reasoning_tokens": "reasoning_per_million_usd",
            }
            try:
                cost = sum(
                    max(0, int(usage[field])) * float(rule[rates[field]])
                    for field in _TOKEN_FIELDS
                ) / 1_000_000
            except (KeyError, TypeError, ValueError):
                return None, None
            return cost, self.version
        return None, None


def aggregate_usage(rows, *, window, quota_rows=None, now=None):
    if window not in WINDOW_SECONDS:
        raise ValueError("invalid window")
    now = _dt(now or datetime.now(timezone.utc))
    seconds = WINDOW_SECONDS[window]
    cutoff = None if seconds is None else now - timedelta(seconds=seconds)
    selected = []
    for row in rows or []:
        if not isinstance(row, dict):
            continue
        try:
            occurred = _dt(row.get("occurred_at"))
        except (TypeError, ValueError):
            continue
        if cutoff is None or occurred >= cutoff:
            selected.append((occurred, row))

    totals = {
        "api_calls": 0,
        "input_tokens": 0,
        "cached_input_tokens": 0,
        "output_tokens": 0,
        "reasoning_tokens": 0,
        "total_tokens": 0,
        "estimated_cost_usd": None,
    }
    breakdown = {}
    daily = {}
    known_cost = 0.0
    any_cost = False
    for occurred, row in selected:
        key = (str(row.get("provider") or "unknown"), str(row.get("model") or "unknown"))
        bucket = breakdown.setdefault(key, {
            "provider": key[0], "model": key[1], "api_calls": 0,
            "input_tokens": 0, "cached_input_tokens": 0, "output_tokens": 0,
            "reasoning_tokens": 0, "total_tokens": 0, "estimated_cost_usd": None,
        })
        day = daily.setdefault(occurred.date().isoformat(), {
            "date": occurred.date().isoformat(), "api_calls": 0,
            "total_tokens": 0, "estimated_cost_usd": None,
        })
        for field in ("api_calls",) + _TOKEN_FIELDS + ("total_tokens",):
            value = row.get(field)
            if isinstance(value, int) and not isinstance(value, bool):
                totals[field] += value
                bucket[field] += value
                if field in ("api_calls", "total_tokens"):
                    day[field] += value
        cost = row.get("estimated_cost_usd")
        if isinstance(cost, (int, float)) and not isinstance(cost, bool):
            any_cost = True
            known_cost += float(cost)
            bucket["estimated_cost_usd"] = (
                float(bucket["estimated_cost_usd"] or 0.0) + float(cost)
            )
            day["estimated_cost_usd"] = (
                float(day["estimated_cost_usd"] or 0.0) + float(cost)
            )
    totals["estimated_cost_usd"] = known_cost if any_cost else None

    latest = {}
    for row in quota_rows or []:
        if not isinstance(row, dict) or not row.get("provider"):
            continue
        try:
            captured = _dt(row.get("captured_at"))
        except (TypeError, ValueError):
            continue
        provider = str(row["provider"])
        if provider not in latest or captured > latest[provider][0]:
            latest[provider] = (captured, dict(row))
    quotas = []
    for provider in sorted(latest):
        row = latest[provider][1]
        if row.get("source_status") != "authenticated":
            for field in ("used_value", "limit_value", "remaining_value"):
                row[field] = None
        quotas.append(row)

    return {
        "window": window,
        "totals": totals,
        "providers": [breakdown[key] for key in sorted(breakdown)],
        "timeline": [daily[key] for key in sorted(daily)],
        "quotas": quotas,
    }
