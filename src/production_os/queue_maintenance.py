from __future__ import annotations

import json
import os
import re
import shutil
import stat
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from .claims import ClaimStore



def _publish_retry_exclusive(target: Path, payload: dict) -> bool:
    """Publish a fully written retry only if no queue entry has that name.

    Linking a temporary file within the same directory is atomic and refuses
    concurrent targets, unlike os.replace() used by ordinary atomic writes.
    """
    fd, temporary = tempfile.mkstemp(
        prefix=target.name + ".", suffix=".tmp", dir=str(target.parent),
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        try:
            os.link(temporary, target, follow_symlinks=False)
        except FileExistsError:
            return False
        return True
    finally:
        os.unlink(temporary)



def _archive_completed_exclusive(source: Path, target: Path) -> bool:
    """Copy to a temporary archive file, then atomically publish if absent.

    Keep the original queued file until its archived bytes are durable and
    publicly visible. A hard link is created *within* the archive filesystem,
    so an archive located on another filesystem is also supported.
    """
    fd, temporary = tempfile.mkstemp(
        prefix=target.name + ".", suffix=".tmp", dir=str(target.parent),
    )
    try:
        with os.fdopen(fd, "wb") as output, source.open("rb") as original:
            shutil.copyfileobj(original, output)
            output.flush()
            os.fsync(output.fileno())
        try:
            os.link(temporary, target, follow_symlinks=False)
        except FileExistsError:
            return False
        source.unlink()
        return True
    finally:
        os.unlink(temporary)


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
        # Malformed and symlinked queue rows are never safe to compact.
        if not isinstance(payload, dict) or source.is_symlink():
            continue
        key = str(payload.get("idempotency_key", ""))
        claim = claims.claims.get(key)
        if claim is None or claim.status != "completed":
            continue

        if archive is not None:
            target = archive / source.name
            if not _archive_completed_exclusive(source, target):
                actions.append({
                    "key": key,
                    "action": "archive-conflict",
                    "path": str(source),
                })
                continue
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
        # Open without following symlinks. An lstat/is_symlink check alone
        # races with a replacement of the directory entry before read_text.
        try:
            flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
            fd = os.open(source, flags)
            with os.fdopen(fd, "r", encoding="utf-8") as handle:
                if not stat.S_ISREG(os.fstat(handle.fileno()).st_mode):
                    actions.append({
                        "key": "",
                        "action": "dead-letter-unsafe-source",
                        "path": str(source),
                    })
                    continue
                payload = json.load(handle)
        except OSError:
            actions.append({
                "key": "",
                "action": "dead-letter-unsafe-source",
                "path": str(source),
            })
            continue
        except (ValueError, UnicodeError):
            continue

        # Dead letters are untrusted persisted data. Never derive a path
        # from a key that can escape the queue directory or overwrite a
        # neighboring queue item. Malformed rows stay available for diagnosis.
        if not isinstance(payload, dict):
            continue
        key = payload.get("idempotency_key")
        if not isinstance(key, str) or not re.fullmatch(
            r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}", key
        ) or key in {".", ".."}:
            actions.append({
                "key": str(key)[:128],
                "action": "dead-letter-invalid-key",
                "path": str(source),
            })
            continue
        raw_attempt = payload.get("delivery_attempt", 0)
        # bool is an int subclass; floats silently truncate on int(...).
        # Neither represents a trustworthy integer delivery count.
        try:
            if isinstance(raw_attempt, bool) or not (
                isinstance(raw_attempt, int)
                or (
                    isinstance(raw_attempt, str)
                    and re.fullmatch(r"[0-9]+", raw_attempt)
                )
            ):
                raise ValueError("invalid delivery attempt type")
            previous_attempt = int(raw_attempt)
        except (TypeError, ValueError):
            actions.append({
                "key": key,
                "action": "dead-letter-invalid-attempt",
                "path": str(source),
            })
            continue
        if previous_attempt < 0:
            actions.append({
                "key": key,
                "action": "dead-letter-invalid-attempt",
                "path": str(source),
            })
            continue
        attempt = previous_attempt + 1

        if attempt > max_attempts:
            actions.append({
                "key": key,
                "action": "dead-letter-retained",
                "attempt": attempt,
                "path": str(source),
            })
            continue

        target = queue / f"{key}.retry{attempt}.json"
        if target.exists() or target.is_symlink():
            actions.append({
                "key": key,
                "action": "dead-letter-queue-conflict",
                "attempt": attempt,
                "path": str(source),
            })
            continue

        payload["delivery_attempt"] = attempt
        payload["worker_id"] = None
        payload["redelivered_at"] = datetime.now(timezone.utc).isoformat()
        if not _publish_retry_exclusive(target, payload):
            actions.append({
                "key": key,
                "action": "dead-letter-queue-conflict",
                "attempt": attempt,
                "path": str(source),
            })
            continue
        source.unlink(missing_ok=True)
        actions.append({
            "key": key,
            "action": "requeued",
            "attempt": attempt,
            "path": str(target),
        })

    return actions
