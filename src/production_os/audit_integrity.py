from __future__ import annotations

import hashlib
import json
from pathlib import Path


def hash_event(previous_hash: str, event: dict) -> str:
    canonical = json.dumps(
        event,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(previous_hash.encode("ascii") + canonical).hexdigest()


def verify_hash_chain(path: str | Path) -> dict:
    source = Path(path)
    previous = "0" * 64
    checked = 0

    if not source.exists():
        return {"valid": True, "checked": 0}

    for index, line in enumerate(source.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        row = json.loads(line)
        expected_previous = row.get("previous_hash")
        stored_hash = row.get("event_hash")
        event = row.get("event")
        if expected_previous != previous or not isinstance(event, dict):
            return {"valid": False, "checked": checked, "failed_line": index}
        calculated = hash_event(previous, event)
        if stored_hash != calculated:
            return {"valid": False, "checked": checked, "failed_line": index}
        previous = calculated
        checked += 1

    return {"valid": True, "checked": checked, "head": previous}
