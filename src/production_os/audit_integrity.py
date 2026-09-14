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
    legacy = 0
    chain_started = False

    if not source.exists():
        return {
            "valid": True,
            "checked": 0,
            "legacy_unverified": 0,
            "head": previous,
        }

    for index, line in enumerate(
        source.read_text(encoding="utf-8").splitlines(),
        start=1,
    ):
        if not line.strip():
            continue
        row = json.loads(line)

        is_chained = (
            isinstance(row, dict)
            and "previous_hash" in row
            and "event_hash" in row
            and isinstance(row.get("event"), dict)
        )

        if not is_chained:
            if chain_started:
                return {
                    "valid": False,
                    "checked": checked,
                    "legacy_unverified": legacy,
                    "failed_line": index,
                    "reason": "legacy/unstructured row appears after hash chain started",
                }
            legacy += 1
            continue

        chain_started = True
        expected_previous = row.get("previous_hash")
        stored_hash = row.get("event_hash")
        event = row.get("event")

        if expected_previous != previous:
            return {
                "valid": False,
                "checked": checked,
                "legacy_unverified": legacy,
                "failed_line": index,
                "reason": "previous hash mismatch",
            }

        calculated = hash_event(previous, event)
        if stored_hash != calculated:
            return {
                "valid": False,
                "checked": checked,
                "legacy_unverified": legacy,
                "failed_line": index,
                "reason": "event hash mismatch",
            }

        previous = calculated
        checked += 1

    return {
        "valid": True,
        "checked": checked,
        "legacy_unverified": legacy,
        "head": previous,
    }
