from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from .audit_integrity import hash_event
from .locks import sidecar_lock


class ExecutionJournal:
    def __init__(self, path: str | Path):
        self.path = Path(path)

    def _head_hash_unlocked(self) -> str:
        if not self.path.exists():
            return "0" * 64
        head = "0" * 64
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(row, dict) and row.get("event_hash"):
                head = str(row["event_hash"])
        return head

    def append(self, event: dict) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **event,
        }
        with sidecar_lock(self.path):
            previous_hash = self._head_hash_unlocked()
            event_hash = hash_event(previous_hash, payload)
            row = {
                "previous_hash": previous_hash,
                "event_hash": event_hash,
                "event": payload,
            }
            with self.path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")
                handle.flush()

    def read(self) -> list[dict]:
        if not self.path.exists():
            return []
        rows = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            payload = json.loads(line)
            if isinstance(payload, dict) and isinstance(payload.get("event"), dict):
                rows.append(payload["event"])
            else:
                rows.append(payload)
        return rows
