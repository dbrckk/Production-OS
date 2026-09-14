from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

from .atomic_io import atomic_write_json
from .locks import sidecar_lock


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
    priority: float = 0.0
    interruptible: bool = False
    preempt_requested: bool = False
    checkpoint_ref: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)


def task_key(repository: str, task: str) -> str:
    raw = f"{repository}\n{task}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:24]


class RuntimeState:
    SCHEMA_VERSION = "production-os/runtime-state/v2"

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.records: dict[str, RuntimeRecord] = {}
        self.load()

    def _load_unlocked(self) -> None:
        self.records = {}
        if not self.path.exists():
            return
        payload = json.loads(self.path.read_text(encoding="utf-8"))
        for key, row in payload.get("records", {}).items():
            self.records[key] = RuntimeRecord(**row)

    def load(self) -> None:
        self._load_unlocked()

    def _save_unlocked(self) -> None:
        atomic_write_json(self.path, {
            "schema_version": self.SCHEMA_VERSION,
            "records": {k: v.to_dict() for k, v in self.records.items()},
        })

    def save(self) -> None:
        with sidecar_lock(self.path):
            self._save_unlocked()

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

    def acquire_lease(
        self,
        repository: str,
        task: str,
        owner: str,
        minutes: int = 30,
        *,
        priority: float = 0.0,
        interruptible: bool = False,
    ) -> RuntimeRecord:
        with sidecar_lock(self.path):
            self._load_unlocked()
            record = self.get(repository, task)
            now = datetime.now(timezone.utc)
            if self.is_leased(record, now):
                raise RuntimeError("task already leased")
            record.lease_owner = owner
            record.lease_expires_at = (now + timedelta(minutes=minutes)).isoformat()
            record.status = "running"
            record.priority = float(priority)
            record.interruptible = bool(interruptible)
            record.preempt_requested = False
            record.updated_at = now.isoformat()
            self._save_unlocked()
            return record

    def heartbeat_lease(
        self,
        repository: str,
        task: str,
        owner: str,
        minutes: int = 30,
    ) -> RuntimeRecord:
        with sidecar_lock(self.path):
            self._load_unlocked()
            record = self.get(repository, task)
            now = datetime.now(timezone.utc)
            if not self.is_leased(record, now):
                raise RuntimeError("task has no active lease")
            if record.lease_owner != owner:
                raise RuntimeError("lease owner mismatch")
            record.lease_expires_at = (now + timedelta(minutes=minutes)).isoformat()
            record.updated_at = now.isoformat()
            self._save_unlocked()
            return record

    def release_lease(self, repository: str, task: str) -> RuntimeRecord:
        with sidecar_lock(self.path):
            self._load_unlocked()
            record = self.get(repository, task)
            record.lease_owner = None
            record.lease_expires_at = None
            if record.status in {"running", "preempt-requested"}:
                record.status = "idle"
            record.updated_at = datetime.now(timezone.utc).isoformat()
            self._save_unlocked()
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
        with sidecar_lock(self.path):
            self._load_unlocked()
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
                if (
                    record.attempts >= retry_budget
                    or record.consecutive_failures >= circuit_breaker_failures
                ):
                    record.status = "circuit-open"
                    record.cooldown_until = (
                        now + timedelta(minutes=cooldown_minutes)
                    ).isoformat()
            elif decision == "replan":
                record.status = "replan"
                record.cooldown_until = (
                    now + timedelta(minutes=max(10, cooldown_minutes // 2))
                ).isoformat()
            else:
                record.status = "idle"

            record.updated_at = now.isoformat()
            self._save_unlocked()
            return record
