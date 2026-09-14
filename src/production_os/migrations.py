from __future__ import annotations

import json
from pathlib import Path

from .atomic_io import atomic_write_json


def migrate_state_file(path: str | Path) -> dict:
    source = Path(path)
    if not source.exists():
        raise FileNotFoundError(source)

    payload = json.loads(source.read_text(encoding="utf-8"))
    schema = str(payload.get("schema_version", ""))

    if "runtime-state/v1" in schema:
        payload["schema_version"] = "production-os/runtime-state/v2"
        atomic_write_json(source, payload)
        return {"migrated": True, "from": schema, "to": payload["schema_version"]}

    if "workers/v1" in schema:
        payload["schema_version"] = "production-os/workers/v2"
        atomic_write_json(source, payload)
        return {"migrated": True, "from": schema, "to": payload["schema_version"]}

    if "claims/v1" in schema:
        payload["schema_version"] = "production-os/claims/v2"
        atomic_write_json(source, payload)
        return {"migrated": True, "from": schema, "to": payload["schema_version"]}

    return {"migrated": False, "from": schema, "to": schema}
