from __future__ import annotations

import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _pg(backend) -> bool:
    return backend.__class__.__name__.startswith("Postgres")


def _sql(backend, sql: str) -> str:
    return sql.replace("?", "%s") if _pg(backend) else sql


def _execute(db, backend, sql: str, params: tuple = ()):
    return db.execute(_sql(backend, sql), params)


@dataclass(frozen=True, slots=True)
class Placement:
    worker_id: str
    score: float
    predicted_minutes: float
    samples: int


class ExecutionOptimizer:
    """Historical runtime learning and deterministic worker placement."""

    def __init__(self, backend):
        self.backend = backend

    def record_execution(
        self,
        *,
        repository: str,
        task: str,
        worker_id: str,
        duration_seconds: float,
        succeeded: bool,
        capabilities: list[str] | None = None,
    ) -> None:
        duration = max(0.001, float(duration_seconds))
        now = _now()
        with self.backend.transaction() as db:
            _execute(
                db, self.backend,
                """
                INSERT INTO execution_history(
                    repository, task, worker_id, duration_seconds,
                    succeeded, capabilities_json, created_at
                ) VALUES(?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    repository, task, worker_id, duration,
                    bool(succeeded),
                    json.dumps(sorted(set(capabilities or []))),
                    now,
                ),
            )
            self.backend.append_event(
                db,
                "execution-observed",
                {
                    "worker_id":worker_id,
                    "duration_seconds":duration,
                    "succeeded":bool(succeeded),
                },
                repository=repository,
            )

    def task_prediction(
        self,
        repository: str,
        task: str,
        *,
        fallback_minutes: float = 1.0,
    ) -> dict:
        with self.backend.connect() as db:
            rows = _execute(
                db, self.backend,
                """
                SELECT duration_seconds, succeeded
                FROM execution_history
                WHERE repository=? AND task=?
                ORDER BY created_at DESC
                LIMIT 100
                """,
                (repository, task),
            ).fetchall()
        successful = [
            float(row["duration_seconds"]) for row in rows
            if bool(row["succeeded"])
        ]
        if not successful:
            return {
                "predicted_minutes":max(0.0, float(fallback_minutes)),
                "samples":0,
                "confidence":0.0,
            }
        successful.sort()
        # Robust trimmed mean: resistant to rare CI/network outliers.
        trim = int(len(successful) * 0.1) if len(successful) >= 10 else 0
        sample = successful[trim:len(successful)-trim] if trim else successful
        predicted = sum(sample) / len(sample) / 60.0
        confidence = min(1.0, math.log2(len(successful) + 1) / 5.0)
        return {
            "predicted_minutes":round(predicted, 3),
            "samples":len(successful),
            "confidence":round(confidence, 3),
        }

    def worker_profiles(self, repository: str, task: str) -> list[dict]:
        with self.backend.connect() as db:
            rows = _execute(
                db, self.backend,
                """
                SELECT worker_id,
                       COUNT(*) AS samples,
                       SUM(CASE WHEN succeeded THEN 1 ELSE 0 END) AS successes,
                       AVG(duration_seconds) AS avg_seconds
                FROM execution_history
                WHERE repository=? AND task=?
                GROUP BY worker_id
                """,
                (repository, task),
            ).fetchall()
        result = []
        for row in rows:
            samples = int(row["samples"])
            successes = int(row["successes"] or 0)
            success_rate = successes / samples if samples else 0.0
            result.append({
                "worker_id":row["worker_id"],
                "samples":samples,
                "success_rate":round(success_rate, 4),
                "avg_minutes":round(float(row["avg_seconds"]) / 60.0, 3),
            })
        return sorted(
            result,
            key=lambda item: (-item["success_rate"], item["avg_minutes"]),
        )

    def choose_worker(
        self,
        *,
        repository: str,
        task: str,
        workers: list,
        required_capabilities: list[str] | None = None,
        fallback_minutes: float = 1.0,
    ) -> Placement | None:
        required = set(required_capabilities or [])
        eligible = [
            worker for worker in workers
            if worker.status == "online"
            and worker.active_tasks < worker.max_concurrency
            and required.issubset(set(worker.capabilities))
        ]
        if not eligible:
            return None

        profiles = {
            item["worker_id"]:item
            for item in self.worker_profiles(repository, task)
        }
        default_prediction = self.task_prediction(
            repository, task, fallback_minutes=fallback_minutes
        )["predicted_minutes"]

        candidates = []
        for worker in eligible:
            profile = profiles.get(worker.worker_id)
            if profile:
                predicted = profile["avg_minutes"]
                reliability = profile["success_rate"]
                samples = profile["samples"]
            else:
                predicted = default_prediction
                reliability = 0.8
                samples = 0
            load = worker.active_tasks / max(1, worker.max_concurrency)
            # Lower is better. Reliability penalty prevents fast-but-flaky workers.
            score = predicted * (1.0 + load) / max(0.1, reliability)
            candidates.append(
                Placement(
                    worker_id=worker.worker_id,
                    score=round(score, 4),
                    predicted_minutes=round(predicted, 3),
                    samples=samples,
                )
            )
        return min(candidates, key=lambda item: (item.score, item.worker_id))

    def stragglers(
        self,
        *,
        threshold_factor: float = 1.75,
        min_runtime_seconds: float = 60.0,
        min_samples: int = 2,
        workers: list | None = None,
    ) -> list[dict]:
        now = datetime.now(timezone.utc)
        with self.backend.connect() as db:
            rows = _execute(
                db,
                self.backend,
                """
                SELECT *
                FROM jobs
                WHERE status IN ('claimed','acked')
                  AND claimed_at IS NOT NULL
                ORDER BY claimed_at ASC
                """,
            ).fetchall()

        result = []
        for row in rows:
            claimed_at = datetime.fromisoformat(
                str(row["claimed_at"]).replace("Z", "+00:00")
            )
            runtime_seconds = max(
                0.0,
                (now - claimed_at).total_seconds(),
            )
            if runtime_seconds < min_runtime_seconds:
                continue

            prediction = self.task_prediction(
                str(row["repository"]),
                str(row["task"]),
                fallback_minutes=runtime_seconds / 60.0,
            )
            if int(prediction["samples"]) < min_samples:
                continue

            expected_seconds = max(
                1.0,
                float(prediction["predicted_minutes"]) * 60.0,
            )
            ratio = runtime_seconds / expected_seconds
            if ratio < threshold_factor:
                continue

            payload = json.loads(row["payload_json"])
            required = [
                str(x)
                for x in payload.get("required_capabilities", [])
            ]
            alternate = None
            if workers:
                candidates = [
                    worker
                    for worker in workers
                    if worker.worker_id != row["claimed_by"]
                ]
                placement = self.choose_worker(
                    repository=str(row["repository"]),
                    task=str(row["task"]),
                    workers=candidates,
                    required_capabilities=required,
                    fallback_minutes=float(
                        prediction["predicted_minutes"]
                    ),
                )
                if placement is not None:
                    alternate = {
                        "worker_id":placement.worker_id,
                        "predicted_minutes":placement.predicted_minutes,
                        "score":placement.score,
                    }

            result.append({
                "job_key":row["key"],
                "repository":row["repository"],
                "task":row["task"],
                "worker_id":row["claimed_by"],
                "runtime_seconds":round(runtime_seconds, 2),
                "expected_seconds":round(expected_seconds, 2),
                "slowdown_ratio":round(ratio, 3),
                "samples":prediction["samples"],
                "alternate_worker":alternate,
            })

        return sorted(
            result,
            key=lambda item: (
                -item["slowdown_ratio"],
                item["job_key"],
            ),
        )

    def workflow_eta(self, workflow: dict) -> dict:
        tasks = {task["task_id"]:task for task in workflow["tasks"]}
        memo: dict[str, tuple[float, list[str]]] = {}

        def duration(task: dict) -> float:
            if task["status"] == "succeeded":
                return 0.0
            prediction = self.task_prediction(
                workflow["repository"],
                task["title"],
                fallback_minutes=float(task["estimated_minutes"]),
            )
            return float(prediction["predicted_minutes"])

        def longest(task_id: str) -> tuple[float, list[str]]:
            if task_id in memo:
                return memo[task_id]
            task = tasks[task_id]
            weight = duration(task)
            deps = task["dependencies"]
            if not deps:
                value = (weight, [task_id])
            else:
                best = max((longest(dep) for dep in deps), key=lambda x:x[0])
                value = (best[0] + weight, best[1] + [task_id])
            memo[task_id] = value
            return value

        best = max((longest(task_id) for task_id in tasks), key=lambda x:x[0])
        return {
            "workflow_id":workflow["id"],
            "predicted_remaining_minutes":round(best[0], 3),
            "critical_task_ids":best[1],
        }
