from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path


@dataclass(slots=True)
class ControlMetrics:
    cycles: int = 0
    scans: int = 0
    dispatched: int = 0
    dispatch_failures: int = 0
    reconciliations: int = 0
    last_cycle_at: str | None = None
    last_error: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)


class MetricsStore:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.metrics = ControlMetrics()
        self.load()

    def load(self) -> None:
        if not self.path.exists():
            return
        payload = json.loads(self.path.read_text(encoding="utf-8"))
        data = payload.get("metrics", payload)
        self.metrics = ControlMetrics(**{
            key: data.get(key, getattr(ControlMetrics(), key))
            for key in ControlMetrics.__dataclass_fields__
        })

    def save(self) -> None:
        self.metrics.last_cycle_at = datetime.now(timezone.utc).isoformat()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps({
            "schema_version":"production-os/metrics/v1",
            "metrics":self.metrics.to_dict(),
        }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
