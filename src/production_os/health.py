from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from .runtime_state import RuntimeState


def build_health(runtime_state: RuntimeState, metrics: dict) -> dict:
    records = list(runtime_state.records.values())
    running = sum(1 for r in records if r.status == "running")
    circuits = sum(1 for r in records if r.status == "circuit-open")
    failed = sum(1 for r in records if r.status == "failed")
    status = "healthy"
    if circuits:
        status = "degraded"
    if metrics.get("last_error"):
        status = "degraded"

    return {
        "schema_version":"production-os/health/v1",
        "status":status,
        "timestamp":datetime.now(timezone.utc).isoformat(),
        "runtime":{
            "records":len(records),
            "running":running,
            "circuit_open":circuits,
            "failed":failed,
        },
        "metrics":metrics,
    }


def write_health(payload: dict, path: str | Path) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
