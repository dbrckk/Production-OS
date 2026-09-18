from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

from .atomic_io import atomic_write_json
from .locks import sidecar_lock


@dataclass(slots=True)
class Worker:
    worker_id: str
    capabilities: list[str]
    max_concurrency: int
    active_tasks: int = 0
    status: str = "online"
    last_heartbeat: str | None = None
    capacity: dict | None = None

    def to_dict(self) -> dict:
        return asdict(self)


CAPACITY_KEYS = {
    "source",
    "status",
    "authenticated_usage",
    "steady_recurring_tokens",
    "used_this_month",
    "remaining_tokens",
    "catalog_updated_at",
    "catalog_source",
}


def _capacity_snapshot(value: dict) -> dict:
    if not isinstance(value, dict):
        raise ValueError("capacity must be an object")
    unknown = set(value) - CAPACITY_KEYS
    if unknown:
        raise ValueError("capacity contains unknown fields")

    source = str(value.get("source") or "").strip()
    status = str(value.get("status") or "").strip()
    authenticated = value.get("authenticated_usage")
    if not source or not status or type(authenticated) is not bool:
        raise ValueError("capacity source/status/authenticated_usage are required")

    normalized = {
        "source": source,
        "status": status,
        "authenticated_usage": authenticated,
    }
    for key in (
        "steady_recurring_tokens",
        "used_this_month",
        "remaining_tokens",
    ):
        raw = value.get(key)
        if raw is None:
            normalized[key] = None
            continue
        if isinstance(raw, bool) or not isinstance(raw, int) or raw < 0:
            raise ValueError("capacity token values must be non-negative integers or null")
        normalized[key] = raw

    for key in ("catalog_updated_at", "catalog_source"):
        raw = value.get(key)
        if raw is not None and not isinstance(raw, str):
            raise ValueError("capacity catalog fields must be strings or null")
        normalized[key] = raw
    return normalized


class WorkerRegistry:
    SCHEMA_VERSION = "production-os/workers/v3"

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.workers: dict[str, Worker] = {}
        self.load()

    def _load_unlocked(self) -> None:
        self.workers = {}
        if not self.path.exists():
            return
        payload = json.loads(self.path.read_text(encoding="utf-8"))
        for row in payload.get("workers", []):
            worker = Worker(**row)
            self.workers[worker.worker_id] = worker

    def load(self) -> None:
        self._load_unlocked()

    def _save_unlocked(self) -> None:
        atomic_write_json(self.path, {
            "schema_version": self.SCHEMA_VERSION,
            "workers": [w.to_dict() for w in self.workers.values()],
        })

    def save(self) -> None:
        with sidecar_lock(self.path):
            self._save_unlocked()

    def register(
        self,
        worker_id: str,
        capabilities: list[str],
        max_concurrency: int,
    ) -> Worker:
        if max_concurrency < 1:
            raise ValueError("max_concurrency must be >= 1")
        with sidecar_lock(self.path):
            self._load_unlocked()
            worker = self.workers.get(worker_id)
            if worker is None:
                worker = Worker(
                    worker_id,
                    sorted(set(capabilities)),
                    max_concurrency,
                )
                self.workers[worker_id] = worker
            else:
                worker.capabilities = sorted(set(capabilities))
                worker.max_concurrency = max_concurrency
                worker.status = "online"
            worker.last_heartbeat = datetime.now(timezone.utc).isoformat()
            self._save_unlocked()
            return worker

    def heartbeat(
        self,
        worker_id: str,
        active_tasks: int | None = None,
        *,
        capacity: dict | None = None,
    ) -> Worker:
        normalized_capacity = (
            _capacity_snapshot(capacity)
            if capacity is not None
            else None
        )
        with sidecar_lock(self.path):
            self._load_unlocked()
            worker = self.workers[worker_id]
            if active_tasks is not None:
                worker.active_tasks = max(0, active_tasks)
            if normalized_capacity is not None:
                worker.capacity = normalized_capacity
            worker.status = "online"
            worker.last_heartbeat = datetime.now(timezone.utc).isoformat()
            self._save_unlocked()
            return worker

    def adjust_active_tasks(self, worker_id: str, delta: int) -> Worker:
        with sidecar_lock(self.path):
            self._load_unlocked()
            worker = self.workers[worker_id]
            worker.active_tasks = max(0, worker.active_tasks + delta)
            self._save_unlocked()
            return worker

    def detect_dead(self, timeout_seconds: int = 120) -> list[Worker]:
        with sidecar_lock(self.path):
            self._load_unlocked()
            now = datetime.now(timezone.utc)
            dead = []
            for worker in self.workers.values():
                if not worker.last_heartbeat:
                    worker.status = "dead"
                    dead.append(worker)
                    continue
                seen = datetime.fromisoformat(
                    worker.last_heartbeat.replace("Z", "+00:00")
                )
                if now - seen > timedelta(seconds=timeout_seconds):
                    worker.status = "dead"
                    dead.append(worker)
            if dead:
                self._save_unlocked()
            return dead

    def available(self) -> list[Worker]:
        return [
            w for w in self.workers.values()
            if w.status == "online" and w.active_tasks < w.max_concurrency
        ]


def select_worker(
    registry: WorkerRegistry,
    required_capabilities: list[str] | None = None,
    allowed_worker_classes: list[str] | tuple[str, ...] | None = None,
) -> Worker | None:
    required = set(required_capabilities or [])
    allowed = set(allowed_worker_classes or [])
    candidates = []
    for worker in registry.available():
        caps = set(worker.capabilities)
        if allowed and not caps.intersection(allowed):
            continue
        missing = len(required - caps)
        load = worker.active_tasks / max(worker.max_concurrency, 1)
        candidates.append(
            (missing, load, worker.active_tasks, worker.worker_id, worker)
        )
    if not candidates:
        return None
    candidates.sort(key=lambda x: (x[0], x[1], x[2], x[3]))
    best = candidates[0]
    if best[0] > 0 and required:
        return None
    return best[-1]
