from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from .atomic_io import atomic_write_json


def set_emergency_stop(path: str | Path, *, reason: str) -> dict:
    payload = {
        "schema_version": "production-os/emergency-stop/v1",
        "active": True,
        "reason": reason,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    atomic_write_json(path, payload)
    return payload


def clear_emergency_stop(path: str | Path) -> dict:
    payload = {
        "schema_version": "production-os/emergency-stop/v1",
        "active": False,
        "reason": None,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    atomic_write_json(path, payload)
    return payload


def emergency_stop_active(path: str | Path | None) -> bool:
    if not path:
        return False
    source = Path(path)
    if not source.exists():
        return False
    try:
        payload = json.loads(source.read_text(encoding="utf-8"))
    except Exception:
        return True
    return bool(payload.get("active", True))
