from __future__ import annotations

import json
import math
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


def validated_budget_amounts(values: dict, *, label: str) -> dict[str, float]:
    """Reject invalid/negative budget values before checks or persistence.

    A NaN projection compares false to every finite ceiling; negative amounts
    would silently refund consumed quota. Neither is a valid resource request.
    Numeric strings remain accepted for backwards-compatible ledger reads.
    """
    if not isinstance(values, dict):
        raise ValueError(f"{label} must be a mapping")
    normalized: dict[str, float] = {}
    for key, raw in values.items():
        if not isinstance(key, str) or not key.strip() or isinstance(raw, bool):
            raise ValueError(f"{label} must use nonempty names and numeric amounts")
        try:
            value = float(raw)
        except (TypeError, ValueError, OverflowError):
            raise ValueError(f"{label} {key!r} must be finite and nonnegative") from None
        if not math.isfinite(value) or value < 0:
            raise ValueError(f"{label} {key!r} must be finite and nonnegative")
        normalized[key] = value
    return normalized


class BudgetLedger:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.payload: dict = {}
        self.load()

    def _load_unlocked(self) -> None:
        if not self.path.exists():
            self.payload = {
                "usage": {},
                "recorded_idempotency_keys": [],
            }
            return
        self.payload = json.loads(self.path.read_text(encoding="utf-8"))
        self.payload.setdefault("usage", {})
        self.payload.setdefault("recorded_idempotency_keys", [])

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
        usage = validated_budget_amounts(
            self.payload.get("usage", {}).get(repository, {}),
            label="recorded budget usage",
        )
        request = validated_budget_amounts(request or {}, label="budget request")
        limits = validated_budget_amounts(limits, label="budget limits")
        reasons: list[str] = []
        for key, limit in limits.items():
            projected = usage.get(key, 0.0) + request.get(key, 0.0)
            if not math.isfinite(projected) or projected > limit:
                reasons.append(f"{key} budget exceeded: {projected}>{limit}")
        return BudgetDecision(
            allowed=not reasons,
            reasons=tuple(reasons),
            usage=usage,
            limits=limits,
        )

    def record_once(
        self,
        repository: str,
        delta: dict[str, float],
        *,
        idempotency_key: str,
    ) -> dict[str, float]:
        idempotency_key = str(idempotency_key or "").strip()
        if not idempotency_key:
            raise ValueError("idempotency_key is required")
        normalized_delta = validated_budget_amounts(delta, label="budget delta")
        with sidecar_lock(self.path):
            self._load_unlocked()
            recorded = self.payload.setdefault(
                "recorded_idempotency_keys",
                [],
            )
            usage = self.payload.setdefault("usage", {}).setdefault(
                repository,
                {},
            )
            normalized_usage = validated_budget_amounts(
                usage, label="recorded budget usage"
            )
            if idempotency_key in recorded:
                return normalized_usage
            updated = dict(normalized_usage)
            for key, value in normalized_delta.items():
                projected = updated.get(key, 0.0) + value
                if not math.isfinite(projected):
                    raise ValueError(f"budget delta {key!r} exceeds numeric range")
                updated[key] = projected
            usage.update(updated)
            recorded.append(idempotency_key)
            self.payload["updated_at"] = datetime.now(timezone.utc).isoformat()
            self._save_unlocked()
            return updated

    def record(self, repository: str, delta: dict[str, float]) -> dict[str, float]:
        normalized_delta = validated_budget_amounts(delta, label="budget delta")
        with sidecar_lock(self.path):
            self._load_unlocked()
            usage = self.payload.setdefault("usage", {}).setdefault(repository, {})
            updated = validated_budget_amounts(
                usage, label="recorded budget usage"
            )
            for key, value in normalized_delta.items():
                projected = updated.get(key, 0.0) + value
                if not math.isfinite(projected):
                    raise ValueError(f"budget delta {key!r} exceeds numeric range")
                updated[key] = projected
            usage.update(updated)
            self.payload["updated_at"] = datetime.now(timezone.utc).isoformat()
            self._save_unlocked()
            return updated
