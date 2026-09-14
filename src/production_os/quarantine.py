from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from .atomic_io import atomic_write_json
from .locks import sidecar_lock


class QuarantineStore:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.entries: dict[str, dict] = {}
        self.load()

    def _load_unlocked(self) -> None:
        self.entries={}
        if not self.path.exists():
            return
        payload=json.loads(self.path.read_text(encoding="utf-8"))
        self.entries=dict(payload.get("repositories", {}))

    def load(self) -> None:
        self._load_unlocked()

    def _save_unlocked(self) -> None:
        atomic_write_json(self.path,{
            "schema_version":"production-os/quarantine/v1",
            "repositories":self.entries,
        })

    def set(self, repository: str, *, active: bool, reason: str) -> dict:
        with sidecar_lock(self.path):
            self._load_unlocked()
            self.entries[repository]={
                "active":bool(active),
                "reason":reason,
                "updated_at":datetime.now(timezone.utc).isoformat(),
            }
            self._save_unlocked()
            return dict(self.entries[repository])

    def active(self, repository: str) -> tuple[bool, str | None]:
        self.load()
        item=self.entries.get(repository) or {}
        return bool(item.get("active")), item.get("reason")
