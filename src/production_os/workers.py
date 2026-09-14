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

    def to_dict(self) -> dict:
        return asdict(self)


class WorkerRegistry:
    SCHEMA_VERSION = "production-os/workers/v2"

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

    def heartbeat(self, worker_id: str, active_tasks: int | None = None) -> Worker:
        with sidecar_lock(self.path):
            self._load_unlocked()
            worker = self.workers[worker_id]
            if active_tasks is not None:
                worker.active_tasks = max(0, active_tasks)
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
) -> Worker | None:
    required = set(required_capabilities or [])
    candidates = []
    for worker in registry.available():
        caps = set(worker.capabilities)
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
