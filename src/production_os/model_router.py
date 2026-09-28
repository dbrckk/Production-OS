from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


ROUTE_SCHEMA = "production-os/model-route/v1"


def _is_postgres(backend) -> bool:
    return backend.__class__.__name__.startswith("Postgres")


def _sql(backend, statement: str) -> str:
    return statement.replace("?", "%s") if _is_postgres(backend) else statement


def _execute(db, backend, statement: str, params: tuple = ()):
    return db.execute(_sql(backend, statement), params)


@dataclass(frozen=True, slots=True)
class ModelCandidate:
    provider: str
    model: str
    capabilities: tuple[str, ...]
    free: bool
    priority: float

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "ModelCandidate":
        if not isinstance(payload, dict):
            raise ValueError("model candidate must be an object")
        provider = str(payload.get("provider") or "").strip()
        model = str(payload.get("model") or "").strip()
        if not provider or not model:
            raise ValueError("model candidate requires provider and model")
        raw_caps = payload.get("capabilities") or []
        if not isinstance(raw_caps, list):
            raise ValueError("model candidate capabilities must be a list")
        capabilities = tuple(sorted(set(
            str(value or "").strip()
            for value in raw_caps
            if str(value or "").strip()
        )))
        if len(capabilities) > 32:
            raise ValueError("model candidate has too many capabilities")
        priority = float(payload.get("priority", 0.0))
        if priority < -1000 or priority > 1000:
            raise ValueError("model candidate priority is out of bounds")
        return cls(
            provider=provider,
            model=model,
            capabilities=capabilities,
            free=bool(payload.get("free", False)),
            priority=priority,
        )

    def key(self) -> tuple[str, str]:
        return self.provider, self.model


def normalize_model_candidates(
    candidates: list[dict[str, Any]],
    *,
    max_candidates: int = 64,
) -> list[dict[str, Any]]:
    if not isinstance(candidates, list):
        raise ValueError("model_candidates must be a list")
    if len(candidates) > int(max_candidates):
        raise ValueError("too many model_candidates")
    normalized = []
    seen = set()
    for raw in candidates:
        candidate = ModelCandidate.from_dict(raw)
        key = candidate.key()
        if key in seen:
            continue
        seen.add(key)
        normalized.append({
            "provider":candidate.provider,
            "model":candidate.model,
            "capabilities":list(candidate.capabilities),
            "free":candidate.free,
            "priority":candidate.priority,
        })
    return normalized


def _parse_time(value: Any) -> datetime | None:
    raw = str(value or "").strip()
    if not raw:
        return None
    if raw.endswith("Z"):
        raw = raw[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(raw)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


class ModelRouter:
    """Deterministic provider/model routing from durable execution evidence.

    No provider secrets are stored or inferred here. The router only emits a
    ranked execution hint for external executors.
    """

    def __init__(self, backend):
        self.backend = backend

    def catalog_candidates(
        self,
        *,
        max_age_seconds: int = 600,
    ) -> list[dict[str, Any]]:
        age = max(30, min(int(max_age_seconds), 86400))
        with self.backend.connect() as db:
            rows = _execute(
                db,
                self.backend,
                """
                SELECT payload_json, created_at
                FROM events
                WHERE event_type='worker-model-catalog'
                ORDER BY created_at DESC, id DESC
                LIMIT 256
                """,
            ).fetchall()

        now = datetime.now(timezone.utc)
        latest_workers: set[str] = set()
        merged: dict[tuple[str, str], dict[str, Any]] = {}
        for row in rows:
            created = _parse_time(row["created_at"])
            if created is None or (now - created).total_seconds() > age:
                continue
            try:
                payload = json.loads(row["payload_json"] or "{}")
            except (TypeError, json.JSONDecodeError):
                continue
            if not isinstance(payload, dict):
                continue
            worker_id = str(payload.get("worker_id") or "").strip()
            if not worker_id or worker_id in latest_workers:
                continue
            latest_workers.add(worker_id)
            raw_candidates = payload.get("model_candidates")
            if not isinstance(raw_candidates, list):
                continue
            try:
                candidates = normalize_model_candidates(raw_candidates)
            except ValueError:
                continue
            for candidate in candidates:
                key = (
                    str(candidate["provider"]),
                    str(candidate["model"]),
                )
                existing = merged.get(key)
                if existing is None:
                    merged[key] = dict(candidate)
                    continue
                existing["capabilities"] = sorted(set(
                    list(existing.get("capabilities") or [])
                    + list(candidate.get("capabilities") or [])
                ))
                existing["free"] = bool(
                    existing.get("free") or candidate.get("free")
                )
                existing["priority"] = max(
                    float(existing.get("priority") or 0),
                    float(candidate.get("priority") or 0),
                )
        return [
            merged[key]
            for key in sorted(merged)
        ]

    def _history(self) -> dict[tuple[str, str], dict[str, float]]:
        with self.backend.connect() as db:
            rows = _execute(
                db,
                self.backend,
                """
                SELECT provider, model, status, duration_seconds,
                       estimated_cost_usd
                FROM job_executions
                WHERE provider IS NOT NULL
                  AND model IS NOT NULL
                  AND status IN ('succeeded','failed','cancelled')
                ORDER BY finished_at DESC
                LIMIT 1000
                """,
            ).fetchall()

        stats: dict[tuple[str, str], dict[str, float]] = {}
        for row in rows:
            key = (str(row["provider"]), str(row["model"]))
            bucket = stats.setdefault(key, {
                "runs":0.0,
                "successes":0.0,
                "failures":0.0,
                "duration_total":0.0,
                "duration_count":0.0,
                "cost_total":0.0,
                "cost_count":0.0,
            })
            bucket["runs"] += 1.0
            if str(row["status"]) == "succeeded":
                bucket["successes"] += 1.0
            else:
                bucket["failures"] += 1.0
            duration = row["duration_seconds"]
            if isinstance(duration, (int, float)) and not isinstance(duration, bool):
                bucket["duration_total"] += max(0.0, float(duration))
                bucket["duration_count"] += 1.0
            cost = row["estimated_cost_usd"]
            if isinstance(cost, (int, float)) and not isinstance(cost, bool):
                bucket["cost_total"] += max(0.0, float(cost))
                bucket["cost_count"] += 1.0
        return stats

    def _quotas(self) -> dict[str, dict[str, Any]]:
        with self.backend.connect() as db:
            rows = _execute(
                db,
                self.backend,
                """
                SELECT q.*
                FROM provider_quota_snapshots q
                JOIN (
                    SELECT provider, MAX(captured_at) AS captured_at
                    FROM provider_quota_snapshots
                    GROUP BY provider
                ) latest
                  ON latest.provider=q.provider
                 AND latest.captured_at=q.captured_at
                """,
            ).fetchall()
        return {
            str(row["provider"]):dict(row)
            for row in rows
            if row["provider"] is not None
        }

    @staticmethod
    def _quota_available(snapshot: dict[str, Any] | None) -> bool:
        if not snapshot:
            return True
        if str(snapshot.get("source_status") or "") != "authenticated":
            return True
        remaining = snapshot.get("remaining_value")
        if isinstance(remaining, bool):
            return True
        if isinstance(remaining, (int, float)):
            return float(remaining) > 0
        return True

    @staticmethod
    def _score(
        candidate: ModelCandidate,
        *,
        required: set[str],
        preferred: set[str],
        history: dict[str, float] | None,
        quota: dict[str, Any] | None,
    ) -> tuple[float, dict[str, Any]]:
        if required and not required.issubset(set(candidate.capabilities)):
            raise ValueError("candidate does not satisfy required capabilities")
        if not ModelRouter._quota_available(quota):
            raise ValueError("provider quota is exhausted")

        score = float(candidate.priority)
        reasons: list[str] = []
        if candidate.free:
            score += 30.0
            reasons.append("free")

        overlap = len(preferred.intersection(candidate.capabilities))
        if overlap:
            score += overlap * 4.0
            reasons.append(f"preferred-capability-overlap:{overlap}")

        success_rate = None
        avg_duration = None
        avg_cost = None
        runs = 0
        if history:
            runs = int(history.get("runs") or 0)
            successes = float(history.get("successes") or 0.0)
            success_rate = successes / runs if runs else None
            if success_rate is not None:
                score += success_rate * 20.0
                score -= (1.0 - success_rate) * min(runs, 10) * 0.5
                reasons.append(f"historical-success-rate:{success_rate:.3f}")

            duration_count = float(history.get("duration_count") or 0.0)
            if duration_count:
                avg_duration = float(history["duration_total"]) / duration_count
                score -= min(avg_duration / 60.0, 10.0)

            cost_count = float(history.get("cost_count") or 0.0)
            if cost_count:
                avg_cost = float(history["cost_total"]) / cost_count
                if avg_cost == 0:
                    score += 10.0
                    reasons.append("historically-zero-cost")
                else:
                    score -= min(avg_cost * 10.0, 20.0)

        return score, {
            "provider":candidate.provider,
            "model":candidate.model,
            "free":candidate.free,
            "score":round(score, 6),
            "historical_runs":runs,
            "historical_success_rate":success_rate,
            "average_duration_seconds":avg_duration,
            "average_cost_usd":avg_cost,
            "quota_status":(
                str(quota.get("source_status") or "")
                if quota
                else None
            ),
            "quota_remaining":(
                quota.get("remaining_value")
                if quota and str(quota.get("source_status") or "") == "authenticated"
                else None
            ),
            "reasons":reasons,
        }

    def route(
        self,
        candidates: list[dict[str, Any]],
        *,
        required_capabilities: list[str] | tuple[str, ...] = (),
        preferred_capabilities: list[str] | tuple[str, ...] = (),
        fallback_limit: int = 3,
    ) -> dict[str, Any]:
        if not isinstance(candidates, list) or not candidates:
            raise ValueError("model_candidates must be a non-empty list")
        normalized = [
            ModelCandidate.from_dict(item)
            for item in normalize_model_candidates(candidates)
        ]
        if len({item.key() for item in normalized}) != len(normalized):
            raise ValueError("duplicate provider/model candidate")

        required = {
            str(value)
            for value in required_capabilities
            if str(value)
        }
        preferred = {
            str(value)
            for value in preferred_capabilities
            if str(value)
        }
        history = self._history()
        quotas = self._quotas()

        ranked: list[tuple[float, dict[str, Any]]] = []
        rejected: list[dict[str, str]] = []
        for candidate in normalized:
            try:
                score, detail = self._score(
                    candidate,
                    required=required,
                    preferred=preferred,
                    history=history.get(candidate.key()),
                    quota=quotas.get(candidate.provider),
                )
            except ValueError as exc:
                rejected.append({
                    "provider":candidate.provider,
                    "model":candidate.model,
                    "reason":str(exc),
                })
                continue
            ranked.append((score, detail))

        if not ranked:
            raise ValueError("no model candidate satisfies routing constraints")

        ranked.sort(
            key=lambda item:(
                -item[0],
                item[1]["provider"],
                item[1]["model"],
            )
        )
        limit = max(0, min(int(fallback_limit), 8))
        ordered = [detail for _score, detail in ranked]
        primary = ordered[0]
        return {
            "schema_version":ROUTE_SCHEMA,
            "provider":primary["provider"],
            "model":primary["model"],
            "fallbacks":[
                {
                    "provider":item["provider"],
                    "model":item["model"],
                }
                for item in ordered[1:1 + limit]
            ],
            "ranking":ordered,
            "rejected":rejected,
        }
