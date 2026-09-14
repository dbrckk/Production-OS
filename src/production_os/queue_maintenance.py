from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from .atomic_io import atomic_write_json
from .claims import ClaimStore


def compact_queue(
    *,
    queue_dir: str | Path,
    claims: ClaimStore,
    archive_dir: str | Path | None = None,
) -> list[dict]:
    queue = Path(queue_dir)
    archive = Path(archive_dir) if archive_dir else None
    if archive is not None:
        archive.mkdir(parents=True, exist_ok=True)

    claims.load()
    actions: list[dict] = []
    if not queue.exists():
        return actions

    for source in sorted(queue.glob("*.json")):
        try:
            payload = json.loads(source.read_text(encoding="utf-8"))
        except Exception:
            continue
        key = str(payload.get("idempotency_key", ""))
        claim = claims.claims.get(key)
        if claim is None or claim.status != "completed":
            continue

        if archive is not None:
            target = archive / source.name
            source.replace(target)
            actions.append({
                "key": key,
                "action": "archive-completed",
                "path": str(target),
            })
        else:
            source.unlink(missing_ok=True)
            actions.append({
                "key": key,
                "action": "delete-completed",
                "path": str(source),
            })
    return actions


def retry_dead_letters(
    *,
    dead_letter_dir: str | Path,
    queue_dir: str | Path,
    max_attempts: int = 3,
) -> list[dict]:
    dead = Path(dead_letter_dir)
    queue = Path(queue_dir)
    queue.mkdir(parents=True, exist_ok=True)
    actions: list[dict] = []

    if not dead.exists():
        return actions

    for source in sorted(dead.glob("*.json")):
        try:
            payload = json.loads(source.read_text(encoding="utf-8"))
        except Exception:
            continue

        attempt = int(payload.get("delivery_attempt", 0)) + 1
        key = str(payload.get("idempotency_key", ""))
        if not key:
            continue

        if attempt > max_attempts:
            actions.append({
                "key": key,
                "action": "dead-letter-retained",
                "attempt": attempt,
                "path": str(source),
            })
            continue

        payload["delivery_attempt"] = attempt
        payload["worker_id"] = None
        payload["redelivered_at"] = datetime.now(timezone.utc).isoformat()
        target = queue / f"{key}.retry{attempt}.json"
        atomic_write_json(target, payload)
        source.unlink(missing_ok=True)
        actions.append({
            "key": key,
            "action": "requeued",
            "attempt": attempt,
            "path": str(target),
        })

    return actions
