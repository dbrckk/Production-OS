from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta, timezone
from pathlib import Path


@dataclass(slots=True)
class RuntimeRecord:
    key: str
    repository: str
    task: str
    status: str
    attempts: int = 0
    consecutive_failures: int = 0
    lease_owner: str | None = None
    lease_expires_at: str | None = None
    cooldown_until: str | None = None
    last_decision: str | None = None
    updated_at: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)


def task_key(repository: str, task: str) -> str:
    raw = f"{repository}\n{task}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:24]


class RuntimeState:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.records: dict[str, RuntimeRecord] = {}
        self.load()

    def load(self) -> None:
        if not self.path.exists():
            return
        payload = json.loads(self.path.read_text(encoding="utf-8"))
        for key, row in payload.get("records", {}).items():
            self.records[key] = RuntimeRecord(**row)

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "schema_version": "production-os/runtime-state/v1",
            "records": {k: v.to_dict() for k, v in self.records.items()},
        }
        self.path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    def get(self, repository: str, task: str) -> RuntimeRecord:
        key = task_key(repository, task)
        if key not in self.records:
            self.records[key] = RuntimeRecord(
                key=key,
                repository=repository,
                task=task,
                status="idle",
            )
        return self.records[key]

    @staticmethod
    def _parse(ts: str | None) -> datetime | None:
        if not ts:
            return None
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))

    def is_leased(self, record: RuntimeRecord, now: datetime | None = None) -> bool:
        now = now or datetime.now(timezone.utc)
        expires = self._parse(record.lease_expires_at)
        return bool(expires and expires > now and record.lease_owner)

    def in_cooldown(self, record: RuntimeRecord, now: datetime | None = None) -> bool:
        now = now or datetime.now(timezone.utc)
        until = self._parse(record.cooldown_until)
        return bool(until and until > now)

    def acquire_lease(self, repository: str, task: str, owner: str, minutes: int = 30) -> RuntimeRecord:
        record = self.get(repository, task)
        now = datetime.now(timezone.utc)
        if self.is_leased(record, now):
            raise RuntimeError("task already leased")
        record.lease_owner = owner
        record.lease_expires_at = (now + timedelta(minutes=minutes)).isoformat()
        record.status = "running"
        record.updated_at = now.isoformat()
        self.save()
        return record

    def heartbeat_lease(
        self,
        repository: str,
        task: str,
        owner: str,
        minutes: int = 30,
    ) -> RuntimeRecord:
        record = self.get(repository, task)
        now = datetime.now(timezone.utc)
        if not self.is_leased(record, now):
            raise RuntimeError("task has no active lease")
        if record.lease_owner != owner:
            raise RuntimeError("lease owner mismatch")
        record.lease_expires_at = (now + timedelta(minutes=minutes)).isoformat()
        record.updated_at = now.isoformat()
        self.save()
        return record

    def release_lease(self, repository: str, task: str) -> RuntimeRecord:
        record = self.get(repository, task)
        record.lease_owner = None
        record.lease_expires_at = None
        if record.status == "running":
            record.status = "idle"
        record.updated_at = datetime.now(timezone.utc).isoformat()
        self.save()
        return record

    def record_outcome(
        self,
        repository: str,
        task: str,
        decision: str,
        *,
        retry_budget: int = 3,
        cooldown_minutes: int = 60,
        circuit_breaker_failures: int = 3,
    ) -> RuntimeRecord:
        record = self.get(repository, task)
        now = datetime.now(timezone.utc)
        record.attempts += 1
        record.last_decision = decision
        record.lease_owner = None
        record.lease_expires_at = None

        if decision == "promote":
            record.status = "succeeded"
            record.consecutive_failures = 0
            record.cooldown_until = None
        elif decision in {"rollback", "retry"}:
            record.consecutive_failures += 1
            record.status = "failed"
            if record.attempts >= retry_budget or record.consecutive_failures >= circuit_breaker_failures:
                record.status = "circuit-open"
                record.cooldown_until = (now + timedelta(minutes=cooldown_minutes)).isoformat()
        elif decision == "replan":
            record.status = "replan"
            record.cooldown_until = (now + timedelta(minutes=max(10, cooldown_minutes // 2))).isoformat()
        else:
            record.status = "idle"

        record.updated_at = now.isoformat()
        self.save()
        return record
