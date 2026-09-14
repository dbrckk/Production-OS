from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

from .atomic_io import atomic_write_json
from .locks import sidecar_lock


@dataclass(slots=True)
class ClaimRecord:
    key: str
    worker_id: str
    repository: str
    task: str
    status: str
    claimed_at: str
    ack_deadline: str
    completed_at: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)


class ClaimStore:
    SCHEMA_VERSION = "production-os/claims/v2"

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.claims: dict[str, ClaimRecord] = {}
        self.load()

    def _load_unlocked(self) -> None:
        self.claims = {}
        if not self.path.exists():
            return
        payload = json.loads(self.path.read_text(encoding="utf-8"))
        for row in payload.get("claims", []):
            claim = ClaimRecord(**row)
            self.claims[claim.key] = claim

    def load(self) -> None:
        self._load_unlocked()

    def _save_unlocked(self) -> None:
        atomic_write_json(self.path, {
            "schema_version": self.SCHEMA_VERSION,
            "claims": [claim.to_dict() for claim in self.claims.values()],
        })

    def save(self) -> None:
        with sidecar_lock(self.path):
            self._save_unlocked()

    def claim(
        self,
        *,
        key: str,
        worker_id: str,
        repository: str,
        task: str,
        ack_timeout_seconds: int = 120,
    ) -> ClaimRecord:
        with sidecar_lock(self.path):
            self._load_unlocked()
            existing = self.claims.get(key)
            if existing and existing.status in {"claimed", "acked", "completed"}:
                raise RuntimeError(f"job already {existing.status}")

            now = datetime.now(timezone.utc)
            record = ClaimRecord(
                key=key,
                worker_id=worker_id,
                repository=repository,
                task=task,
                status="claimed",
                claimed_at=now.isoformat(),
                ack_deadline=(
                    now + timedelta(seconds=ack_timeout_seconds)
                ).isoformat(),
            )
            self.claims[key] = record
            self._save_unlocked()
            return record

    def ack(self, key: str, worker_id: str) -> ClaimRecord:
        with sidecar_lock(self.path):
            self._load_unlocked()
            record = self.claims[key]
            if record.worker_id != worker_id:
                raise RuntimeError("claim owner mismatch")
            if record.status != "completed":
                record.status = "acked"
                self._save_unlocked()
            return record

    def complete(self, key: str, worker_id: str) -> ClaimRecord:
        with sidecar_lock(self.path):
            self._load_unlocked()
            record = self.claims[key]
            if record.worker_id != worker_id:
                raise RuntimeError("claim owner mismatch")
            record.status = "completed"
            record.completed_at = datetime.now(timezone.utc).isoformat()
            self._save_unlocked()
            return record

    def expired_unacked(self) -> list[ClaimRecord]:
        self.load()
        now = datetime.now(timezone.utc)
        result = []
        for record in self.claims.values():
            if record.status != "claimed":
                continue
            deadline = datetime.fromisoformat(
                record.ack_deadline.replace("Z", "+00:00")
            )
            if deadline <= now:
                result.append(record)
        return result
