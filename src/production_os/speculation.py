from __future__ import annotations

import json
from datetime import datetime, timezone

from .runtime_state import task_key


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _pg(backend) -> bool:
    return backend.__class__.__name__.startswith("Postgres")


def _sql(backend, statement: str) -> str:
    return statement.replace("?", "%s") if _pg(backend) else statement


def _execute(db, backend, statement: str, params: tuple = ()):
    return db.execute(_sql(backend, statement), params)


class SpeculationManager:
    def __init__(self, backend, queue):
        self.backend = backend
        self.queue = queue

    @staticmethod
    def _safe(payload: dict) -> bool:
        if bool(payload.get("speculative_safe", False)):
            return True
        constraints = (
            payload.get("handoff", {})
            .get("constraints", {})
        )
        return bool(constraints.get("speculative_safe", False))

    def spawn(
        self,
        canonical_job_key: str,
        *,
        target_worker: str,
    ) -> dict:
        canonical = self.queue.get(canonical_job_key)
        payload = dict(canonical["payload"])
        if not self._safe(payload):
            raise RuntimeError("job is not marked speculative_safe")

        group_id = str(
            payload.get("speculation_group")
            or canonical_job_key
        )
        duplicate_key = task_key(
            group_id,
            f"speculative:{target_worker}",
        )
        now = _now()

        with self.backend.transaction() as db:
            _execute(
                db,
                self.backend,
                """
                INSERT INTO speculation_groups(
                    group_id, canonical_job_key, winner_job_key,
                    created_at, resolved_at
                )
                VALUES(?, ?, NULL, ?, NULL)
                ON CONFLICT(group_id) DO NOTHING
                """,
                (group_id, canonical_job_key, now),
            )

            existing = _execute(
                db,
                self.backend,
                """
                SELECT job_key
                FROM speculation_members
                WHERE group_id=? AND worker_id=?
                """,
                (group_id, target_worker),
            ).fetchone()
            if existing is not None:
                return self.queue.get(existing["job_key"])

            _execute(
                db,
                self.backend,
                """
                INSERT INTO speculation_members(
                    group_id, job_key, worker_id, created_at
                )
                VALUES(?, ?, ?, ?)
                ON CONFLICT(group_id, job_key) DO NOTHING
                """,
                (
                    group_id,
                    canonical_job_key,
                    canonical.get("claimed_by")
                    or canonical.get("assigned_worker"),
                    now,
                ),
            )

        duplicate_payload = {
            **payload,
            "idempotency_key":duplicate_key,
            "worker_id":target_worker,
            "speculation_group":group_id,
            "speculative_of":canonical_job_key,
        }
        job = self.queue.enqueue(duplicate_payload)

        with self.backend.transaction() as db:
            _execute(
                db,
                self.backend,
                """
                INSERT INTO speculation_members(
                    group_id, job_key, worker_id, created_at
                )
                VALUES(?, ?, ?, ?)
                ON CONFLICT(group_id, job_key) DO NOTHING
                """,
                (group_id, duplicate_key, target_worker, now),
            )
            self.backend.append_event(
                db,
                "speculative-job-spawned",
                {
                    "group_id":group_id,
                    "canonical_job_key":canonical_job_key,
                    "duplicate_job_key":duplicate_key,
                    "target_worker":target_worker,
                },
                repository=canonical["repository"],
                task_key_value=canonical_job_key,
            )
        return job

    def group_for_job(self, job_key: str) -> str | None:
        with self.backend.connect() as db:
            row = _execute(
                db,
                self.backend,
                """
                SELECT group_id
                FROM speculation_members
                WHERE job_key=?
                """,
                (job_key,),
            ).fetchone()
        return str(row["group_id"]) if row is not None else None

    def try_win(self, group_id: str, job_key: str) -> bool:
        now = _now()
        with self.backend.transaction() as db:
            if _pg(self.backend):
                row = _execute(
                    db,
                    self.backend,
                    """
                    SELECT winner_job_key
                    FROM speculation_groups
                    WHERE group_id=?
                    FOR UPDATE
                    """,
                    (group_id,),
                ).fetchone()
            else:
                row = _execute(
                    db,
                    self.backend,
                    """
                    SELECT winner_job_key
                    FROM speculation_groups
                    WHERE group_id=?
                    """,
                    (group_id,),
                ).fetchone()

            if row is None:
                return True
            winner = row["winner_job_key"]
            if winner:
                return str(winner) == job_key

            _execute(
                db,
                self.backend,
                """
                UPDATE speculation_groups
                SET winner_job_key=?, resolved_at=?
                WHERE group_id=? AND winner_job_key IS NULL
                """,
                (job_key, now, group_id),
            )
            self.backend.append_event(
                db,
                "speculation-winner-selected",
                {
                    "group_id":group_id,
                    "winner_job_key":job_key,
                },
                task_key_value=job_key,
            )
            return True

    def cancel_losers(
        self,
        group_id: str,
        winner_job_key: str,
    ) -> list[str]:
        now = _now()
        cancelled: list[str] = []
        with self.backend.transaction() as db:
            rows = _execute(
                db,
                self.backend,
                """
                SELECT job_key
                FROM speculation_members
                WHERE group_id=? AND job_key<>?
                """,
                (group_id, winner_job_key),
            ).fetchall()

            for row in rows:
                key = str(row["job_key"])
                current = _execute(
                    db,
                    self.backend,
                    "SELECT status FROM jobs WHERE key=?",
                    (key,),
                ).fetchone()
                if current is None:
                    continue
                if current["status"] not in {
                    "queued", "claimed", "acked"
                }:
                    continue
                _execute(
                    db,
                    self.backend,
                    """
                    UPDATE jobs
                    SET status='cancelled', updated_at=?
                    WHERE key=?
                    """,
                    (now, key),
                )
                cancelled.append(key)

            if cancelled:
                self.backend.append_event(
                    db,
                    "speculation-losers-cancelled",
                    {
                        "group_id":group_id,
                        "winner_job_key":winner_job_key,
                        "cancelled":cancelled,
                    },
                    task_key_value=winner_job_key,
                )
        return cancelled

    def failure_is_terminal(
        self,
        group_id: str,
        failed_job_key: str,
    ) -> bool:
        with self.backend.connect() as db:
            rows = _execute(
                db,
                self.backend,
                """
                SELECT j.key, j.status
                FROM speculation_members m
                JOIN jobs j ON j.key=m.job_key
                WHERE m.group_id=? AND j.key<>?
                """,
                (group_id, failed_job_key),
            ).fetchall()
        for row in rows:
            if row["status"] in {
                "queued", "claimed", "acked", "completed"
            }:
                return False
        return True

    def cancel_job(
        self,
        job_key: str,
    ) -> dict:
        now = _now()
        with self.backend.transaction() as db:
            current = _execute(
                db,
                self.backend,
                "SELECT status FROM jobs WHERE key=?",
                (job_key,),
            ).fetchone()
            if current is None:
                raise KeyError(job_key)
            if current["status"] in {"completed", "cancelled"}:
                return self.queue.get(job_key)
            _execute(
                db,
                self.backend,
                """
                UPDATE jobs
                SET status='cancelled', updated_at=?
                WHERE key=?
                """,
                (now, job_key),
            )
        return self.queue.get(job_key)
