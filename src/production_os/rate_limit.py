from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone


@dataclass(frozen=True, slots=True)
class RateLimitDecision:
    allowed: bool
    count: int
    limit: int
    window_seconds: int

    def to_dict(self) -> dict:
        return {
            "allowed": self.allowed,
            "count": self.count,
            "limit": self.limit,
            "window_seconds": self.window_seconds,
        }


def check_rate_limit(
    timestamps: list[str],
    *,
    limit: int,
    window_seconds: int,
) -> RateLimitDecision:
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(seconds=window_seconds)
    count = 0
    for raw in timestamps:
        try:
            ts = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        except ValueError:
            continue
        if ts >= cutoff:
            count += 1
    return RateLimitDecision(
        allowed=count < limit,
        count=count,
        limit=limit,
        window_seconds=window_seconds,
    )
