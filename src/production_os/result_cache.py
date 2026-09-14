from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _pg(backend) -> bool:
    return backend.__class__.__name__.startswith("Postgres")


def _sql(backend, statement: str) -> str:
    return statement.replace("?", "%s") if _pg(backend) else statement


def _execute(db, backend, statement: str, params: tuple = ()):
    return db.execute(_sql(backend, statement), params)


def fingerprint(
    *,
    repository: str,
    task: str,
    inputs: dict,
) -> str:
    canonical = json.dumps(
        {
            "repository":repository,
            "task":task,
            "inputs":inputs,
        },
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


class ResultCache:
    def __init__(self, backend):
        self.backend = backend

    def get(self, key: str) -> dict | None:
        with self.backend.transaction() as db:
            row = _execute(
                db,
                self.backend,
                "SELECT * FROM result_cache WHERE fingerprint=?",
                (key,),
            ).fetchone()
            if row is None:
                return None
            _execute(
                db,
                self.backend,
                """
                UPDATE result_cache
                SET hits=hits+1, last_used_at=?
                WHERE fingerprint=?
                """,
                (_now(), key),
            )
            return {
                "fingerprint":row["fingerprint"],
                "repository":row["repository"],
                "task":row["task"],
                "result":json.loads(row["result_json"]),
                "artifacts":json.loads(row["artifact_json"]),
                "created_at":row["created_at"],
                "hits":int(row["hits"]) + 1,
            }

    def put(
        self,
        *,
        key: str,
        repository: str,
        task: str,
        result: dict,
        artifacts: list[dict] | None = None,
    ) -> dict:
        now = _now()
        with self.backend.transaction() as db:
            _execute(
                db,
                self.backend,
                """
                INSERT INTO result_cache(
                    fingerprint, repository, task, result_json,
                    artifact_json, created_at, last_used_at, hits
                )
                VALUES(?, ?, ?, ?, ?, ?, ?, 0)
                ON CONFLICT(fingerprint) DO UPDATE SET
                    result_json=excluded.result_json,
                    artifact_json=excluded.artifact_json,
                    last_used_at=excluded.last_used_at
                """.replace("excluded.", "EXCLUDED." if _pg(self.backend) else "excluded."),
                (
                    key,
                    repository,
                    task,
                    json.dumps(result, ensure_ascii=False),
                    json.dumps(artifacts or [], ensure_ascii=False),
                    now,
                    now,
                ),
            )
            self.backend.append_event(
                db,
                "result-cached",
                {"fingerprint":key},
                repository=repository,
            )
        return {
            "fingerprint":key,
            "repository":repository,
            "task":task,
            "result":result,
            "artifacts":artifacts or [],
        }

    def prune(self, *, max_entries: int = 10000) -> int:
        with self.backend.transaction() as db:
            rows = _execute(
                db,
                self.backend,
                """
                SELECT fingerprint
                FROM result_cache
                ORDER BY last_used_at DESC
                """,
            ).fetchall()
            stale = rows[max(0, int(max_entries)):]
            for row in stale:
                _execute(
                    db,
                    self.backend,
                    "DELETE FROM result_cache WHERE fingerprint=?",
                    (row["fingerprint"],),
                )
        return len(stale)
