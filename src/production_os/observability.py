from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


def build_observability_payload(
    *,
    health: dict,
    metrics: dict,
    runtime_records: list[dict],
) -> dict:
    return {
        "schema_version":"production-os/observability/v1",
        "timestamp":datetime.now(timezone.utc).isoformat(),
        "health":health,
        "metrics":metrics,
        "runtime_records":runtime_records,
    }


def write_observability(payload: dict, path: str | Path) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
