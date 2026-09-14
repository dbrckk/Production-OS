from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from .atomic_io import atomic_write_json
from .locks import sidecar_lock


@dataclass(slots=True)
class Approval:
    key: str
    approved: bool
    approved_by: str | None = None
    reason: str | None = None
    updated_at: str | None = None

    def to_dict(self) -> dict:
        return {
            "key": self.key,
            "approved": self.approved,
            "approved_by": self.approved_by,
            "reason": self.reason,
            "updated_at": self.updated_at,
        }


class ApprovalStore:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.approvals: dict[str, Approval] = {}
        self.load()

    def _load_unlocked(self) -> None:
        self.approvals = {}
        if not self.path.exists():
            return
        payload = json.loads(self.path.read_text(encoding="utf-8"))
        for row in payload.get("approvals", []):
            item = Approval(**row)
            self.approvals[item.key] = item

    def load(self) -> None:
        self._load_unlocked()

    def _save_unlocked(self) -> None:
        atomic_write_json(self.path, {
            "schema_version":"production-os/approvals/v1",
            "approvals":[item.to_dict() for item in self.approvals.values()],
        })

    def set(
        self,
        key: str,
        *,
        approved: bool,
        approved_by: str | None,
        reason: str | None,
    ) -> Approval:
        with sidecar_lock(self.path):
            self._load_unlocked()
            item = Approval(
                key=key,
                approved=approved,
                approved_by=approved_by,
                reason=reason,
                updated_at=datetime.now(timezone.utc).isoformat(),
            )
            self.approvals[key] = item
            self._save_unlocked()
            return item

    def is_approved(self, key: str) -> bool:
        self.load()
        item = self.approvals.get(key)
        return bool(item and item.approved)
