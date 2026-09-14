from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _is_postgres(backend) -> bool:
    return backend.__class__.__name__.startswith("Postgres")


def _sql(backend, statement: str) -> str:
    return statement.replace("?", "%s") if _is_postgres(backend) else statement


def _execute(db, backend, statement: str, params: tuple = ()):
    return db.execute(_sql(backend, statement), params)


class ReleaseLedger:
    def __init__(self, backend, workflows):
        self.backend = backend
        self.workflows = workflows

    @staticmethod
    def _validation_passed(validation: dict) -> bool:
        if str(validation.get("status") or "") != "passed":
            return False
        if validation.get("blocking_failures"):
            return False
        if (
            "promotion_allowed" in validation
            and not bool(validation["promotion_allowed"])
        ):
            return False
        return True

    @staticmethod
    def _row(row) -> dict:
        return {
            "id":row["id"],
            "workflow_id":row["workflow_id"],
            "artifact_id":row["artifact_id"],
            "repository":row["repository"],
            "source_revision":row["source_revision"],
            "workflow_generation":row["workflow_generation"],
            "validation":json.loads(row["validation_json"]),
            "metadata":json.loads(row["metadata_json"]),
            "status":row["status"],
            "rollback_of":row["rollback_of"],
            "created_at":row["created_at"],
        }

    def get(self, release_id: str) -> dict:
        with self.backend.connect() as db:
            row = _execute(
                db,
                self.backend,
                "SELECT * FROM releases WHERE id=?",
                (release_id,),
            ).fetchone()
        if row is None:
            raise KeyError(release_id)
        return self._row(row)

    def list_for_workflow(self, workflow_id: str) -> list[dict]:
        with self.backend.connect() as db:
            rows = _execute(
                db,
                self.backend,
                """
                SELECT * FROM releases
                WHERE workflow_id=?
                ORDER BY created_at ASC, id ASC
                """,
                (workflow_id,),
            ).fetchall()
        return [self._row(row) for row in rows]

    def promote(
        self,
        *,
        workflow_id: str,
        artifact_id: str,
        validation: dict,
        metadata: dict | None = None,
    ) -> dict:
        workflow = self.workflows.get(workflow_id)
        if workflow["status"] != "succeeded":
            raise RuntimeError(
                "workflow must be succeeded before promotion"
            )
        if not self._validation_passed(validation):
            raise RuntimeError(
                "validation must be passed before promotion"
            )

        artifact = next(
            (
                item
                for item in workflow.get("artifacts", [])
                if str(item["id"]) == str(artifact_id)
            ),
            None,
        )
        if artifact is None:
            raise KeyError(f"artifact {artifact_id}")
        if not artifact.get("sha256"):
            raise RuntimeError(
                "artifact sha256 is required before promotion"
            )

        artifact_metadata = dict(artifact.get("metadata") or {})
        workflow_metadata = dict(workflow.get("metadata") or {})
        source_revision = artifact_metadata.get("source_revision")
        workflow_generation = artifact_metadata.get(
            "workflow_generation"
        )

        if (
            workflow_metadata.get("github_pr_head_sha")
            or workflow_metadata.get("github_pr_generation") is not None
        ):
            self.workflows.assert_generation_current(
                workflow_id,
                source_revision=source_revision,
                workflow_generation=workflow_generation,
            )

        release_id = uuid.uuid4().hex
        now = _now()
        release_metadata = {
            **dict(metadata or {}),
            "artifact_name":artifact["name"],
            "artifact_uri":artifact["uri"],
            "artifact_sha256":artifact["sha256"],
        }

        with self.backend.transaction() as db:
            existing = _execute(
                db,
                self.backend,
                """
                SELECT id FROM releases
                WHERE artifact_id=? AND status='promoted'
                """,
                (artifact_id,),
            ).fetchone()
            if existing is not None:
                raise RuntimeError(
                    "artifact already promoted as release "
                    f"{existing['id']}"
                )

            _execute(
                db,
                self.backend,
                """
                INSERT INTO releases(
                    id, workflow_id, artifact_id, repository,
                    source_revision, workflow_generation,
                    validation_json, metadata_json, status,
                    rollback_of, created_at
                )
                VALUES(?, ?, ?, ?, ?, ?, ?, ?, 'promoted', NULL, ?)
                """,
                (
                    release_id,
                    workflow_id,
                    artifact_id,
                    workflow["repository"],
                    source_revision,
                    (
                        int(workflow_generation)
                        if workflow_generation is not None
                        else None
                    ),
                    json.dumps(validation, ensure_ascii=False),
                    json.dumps(release_metadata, ensure_ascii=False),
                    now,
                ),
            )
            self.backend.append_event(
                db,
                "release-promoted",
                {
                    "release_id":release_id,
                    "workflow_id":workflow_id,
                    "artifact_id":artifact_id,
                    "artifact_sha256":artifact["sha256"],
                    "source_revision":source_revision,
                    "workflow_generation":workflow_generation,
                },
                repository=workflow["repository"],
            )
            row = _execute(
                db,
                self.backend,
                "SELECT * FROM releases WHERE id=?",
                (release_id,),
            ).fetchone()

        return self._row(row)

    def rollback(
        self,
        release_id: str,
        *,
        reason: str,
        metadata: dict | None = None,
    ) -> dict:
        original = self.get(release_id)
        if original["status"] != "promoted":
            raise RuntimeError(
                "only promoted releases can be rolled back"
            )
        reason = str(reason or "").strip()
        if not reason:
            raise ValueError("rollback reason is required")

        rollback_id = uuid.uuid4().hex
        now = _now()
        with self.backend.transaction() as db:
            existing = _execute(
                db,
                self.backend,
                """
                SELECT id FROM releases
                WHERE rollback_of=? AND status='rollback'
                """,
                (release_id,),
            ).fetchone()
            if existing is not None:
                raise RuntimeError(
                    "release already rolled back by "
                    f"{existing['id']}"
                )

            _execute(
                db,
                self.backend,
                """
                INSERT INTO releases(
                    id, workflow_id, artifact_id, repository,
                    source_revision, workflow_generation,
                    validation_json, metadata_json, status,
                    rollback_of, created_at
                )
                VALUES(?, ?, ?, ?, ?, ?, ?, ?, 'rollback', ?, ?)
                """,
                (
                    rollback_id,
                    original["workflow_id"],
                    original["artifact_id"],
                    original["repository"],
                    original["source_revision"],
                    original["workflow_generation"],
                    json.dumps(
                        {
                            "status":"rollback",
                            "reason":reason,
                        },
                        ensure_ascii=False,
                    ),
                    json.dumps(
                        dict(metadata or {}),
                        ensure_ascii=False,
                    ),
                    release_id,
                    now,
                ),
            )
            self.backend.append_event(
                db,
                "release-rollback-recorded",
                {
                    "rollback_id":rollback_id,
                    "release_id":release_id,
                    "reason":reason,
                },
                repository=original["repository"],
            )
            row = _execute(
                db,
                self.backend,
                "SELECT * FROM releases WHERE id=?",
                (rollback_id,),
            ).fetchone()

        return self._row(row)
