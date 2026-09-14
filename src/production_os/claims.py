from __future__ import annotations

import json
import os
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta, timezone
from pathlib import Path


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
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.claims: dict[str, ClaimRecord] = {}
        self.load()

    def load(self) -> None:
        if not self.path.exists():
            return
        payload = json.loads(self.path.read_text(encoding="utf-8"))
        for row in payload.get("claims", []):
            claim = ClaimRecord(**row)
            self.claims[claim.key] = claim

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temp = self.path.with_suffix(self.path.suffix + ".tmp")
        temp.write_text(json.dumps({
            "schema_version":"production-os/claims/v1",
            "claims":[claim.to_dict() for claim in self.claims.values()],
        }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        os.replace(temp, self.path)

    def claim(
        self,
        *,
        key: str,
        worker_id: str,
        repository: str,
        task: str,
        ack_timeout_seconds: int = 120,
    ) -> ClaimRecord:
        existing = self.claims.get(key)
        if existing and existing.status in {"claimed","acked","completed"}:
            raise RuntimeError(f"job already {existing.status}")

        now = datetime.now(timezone.utc)
        record = ClaimRecord(
            key=key,
            worker_id=worker_id,
            repository=repository,
            task=task,
            status="claimed",
            claimed_at=now.isoformat(),
            ack_deadline=(now + timedelta(seconds=ack_timeout_seconds)).isoformat(),
        )
        self.claims[key] = record
        self.save()
        return record

    def ack(self, key: str, worker_id: str) -> ClaimRecord:
        record = self.claims[key]
        if record.worker_id != worker_id:
            raise RuntimeError("claim owner mismatch")
        if record.status == "completed":
            return record
        record.status = "acked"
        self.save()
        return record

    def complete(self, key: str, worker_id: str) -> ClaimRecord:
        record = self.claims[key]
        if record.worker_id != worker_id:
            raise RuntimeError("claim owner mismatch")
        record.status = "completed"
        record.completed_at = datetime.now(timezone.utc).isoformat()
        self.save()
        return record

    def expired_unacked(self) -> list[ClaimRecord]:
        now = datetime.now(timezone.utc)
        result=[]
        for record in self.claims.values():
            if record.status != "claimed":
                continue
            deadline = datetime.fromisoformat(record.ack_deadline.replace("Z","+00:00"))
            if deadline <= now:
                result.append(record)
        return result
