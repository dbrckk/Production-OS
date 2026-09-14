from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from .atomic_io import atomic_write_json
from .locks import sidecar_lock


@dataclass(frozen=True, slots=True)
class BudgetDecision:
    allowed: bool
    reasons: tuple[str, ...]
    usage: dict[str, float]
    limits: dict[str, float]

    def to_dict(self) -> dict:
        return {
            "allowed": self.allowed,
            "reasons": list(self.reasons),
            "usage": self.usage,
            "limits": self.limits,
        }


class BudgetLedger:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.payload: dict = {}
        self.load()

    def _load_unlocked(self) -> None:
        if not self.path.exists():
            self.payload = {"usage": {}}
            return
        self.payload = json.loads(self.path.read_text(encoding="utf-8"))
        self.payload.setdefault("usage", {})

    def load(self) -> None:
        self._load_unlocked()

    def _save_unlocked(self) -> None:
        atomic_write_json(self.path, {
            "schema_version":"production-os/budget-ledger/v1",
            **self.payload,
        })

    def check(
        self,
        repository: str,
        limits: dict[str, float],
        request: dict[str, float] | None = None,
    ) -> BudgetDecision:
        self.load()
        usage = dict(self.payload.get("usage", {}).get(repository, {}))
        request = request or {}
        reasons=[]
        for key, limit in limits.items():
            projected = float(usage.get(key, 0.0)) + float(request.get(key, 0.0))
            if projected > float(limit):
                reasons.append(f"{key} budget exceeded: {projected}>{limit}")
        return BudgetDecision(
            allowed=not reasons,
            reasons=tuple(reasons),
            usage={k:float(v) for k,v in usage.items()},
            limits={k:float(v) for k,v in limits.items()},
        )

    def record(self, repository: str, delta: dict[str, float]) -> dict[str, float]:
        with sidecar_lock(self.path):
            self._load_unlocked()
            usage = self.payload.setdefault("usage", {}).setdefault(repository, {})
            for key, value in delta.items():
                usage[key] = float(usage.get(key, 0.0)) + float(value)
            self.payload["updated_at"] = datetime.now(timezone.utc).isoformat()
            self._save_unlocked()
            return {k:float(v) for k,v in usage.items()}
