from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

from .atomic_io import atomic_write_json
from .locks import sidecar_lock


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


class RateLimitStore:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.events: dict[str, list[str]] = {}
        self.load()

    def _load_unlocked(self) -> None:
        self.events = {}
        if not self.path.exists():
            return
        payload = json.loads(self.path.read_text(encoding="utf-8"))
        raw = payload.get("events", {})
        if isinstance(raw, dict):
            self.events = {
                str(key): [str(ts) for ts in value if isinstance(ts, str)]
                for key, value in raw.items()
                if isinstance(value, list)
            }

    def load(self) -> None:
        self._load_unlocked()

    def _save_unlocked(self) -> None:
        atomic_write_json(self.path, {
            "schema_version": "production-os/rate-limit/v1",
            "events": self.events,
        })

    def check_and_record(
        self,
        key: str,
        *,
        limit: int,
        window_seconds: int,
    ) -> RateLimitDecision:
        with sidecar_lock(self.path):
            self._load_unlocked()
            now = datetime.now(timezone.utc)
            cutoff = now - timedelta(seconds=window_seconds)
            timestamps = []
            for raw in self.events.get(key, []):
                try:
                    ts = datetime.fromisoformat(raw.replace("Z", "+00:00"))
                except ValueError:
                    continue
                if ts >= cutoff:
                    timestamps.append(ts.isoformat())

            decision = RateLimitDecision(
                allowed=len(timestamps) < limit,
                count=len(timestamps),
                limit=limit,
                window_seconds=window_seconds,
            )
            if decision.allowed:
                timestamps.append(now.isoformat())
            self.events[key] = timestamps
            self._save_unlocked()
            return decision
