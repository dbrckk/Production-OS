from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


TERMINAL_TASK_STATES = {"succeeded", "failed", "cancelled", "blocked"}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _is_postgres(backend) -> bool:
    return backend.__class__.__name__.startswith("Postgres")


def _sql(backend, statement: str) -> str:
    return statement.replace("?", "%s") if _is_postgres(backend) else statement


def _execute(db, backend, statement: str, params: tuple = ()):
    return db.execute(_sql(backend, statement), params)


@dataclass(frozen=True, slots=True)
class WorkflowTaskSpec:
    task_id: str
    title: str
    payload: dict
    dependencies: tuple[str, ...] = ()
    priority: float = 0.0
    max_attempts: int = 1
    estimated_minutes: float = 1.0

    @classmethod
    def from_dict(cls, payload: dict) -> "WorkflowTaskSpec":
        return cls(
            task_id=str(payload["task_id"]),
            title=str(payload.get("title") or payload["task_id"]),
            payload=dict(payload.get("payload") or {}),
            dependencies=tuple(
                str(x) for x in payload.get("dependencies", [])
            ),
            priority=float(payload.get("priority", 0.0)),
            max_attempts=max(1, int(payload.get("max_attempts", 1))),
            estimated_minutes=max(
                0.0,
                float(payload.get("estimated_minutes", 1.0)),
            ),
        )


class WorkflowEngine:
    def __init__(self, backend, queue):
        self.backend = backend
        self.queue = queue

    @staticmethod
    def _validate(tasks: list[WorkflowTaskSpec]) -> None:
        ids = [task.task_id for task in tasks]
        if len(ids) != len(set(ids)):
            raise ValueError("workflow task_id values must be unique")
        known = set(ids)
        for task in tasks:
            missing = set(task.dependencies) - known
            if missing:
                raise ValueError(
                    f"task {task.task_id} has missing dependencies: "
                    + ", ".join(sorted(missing))
                )
            if task.task_id in task.dependencies:
                raise ValueError(
                    f"task {task.task_id} cannot depend on itself"
                )

        graph = {task.task_id: set(task.dependencies) for task in tasks}
        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(task_id: str) -> None:
            if task_id in visited:
                return
            if task_id in visiting:
                raise ValueError("workflow dependency cycle detected")
            visiting.add(task_id)
            for dep in graph[task_id]:
                visit(dep)
            visiting.remove(task_id)
            visited.add(task_id)

        for task_id in graph:
            visit(task_id)

    def create(
        self,
        *,
        name: str,
        repository: str,
        tasks: list[WorkflowTaskSpec],
        metadata: dict | None = None,
        workflow_id: str | None = None,
    ) -> dict:
        if not name or not repository:
            raise ValueError("workflow requires name and repository")
        if not tasks:
            raise ValueError("workflow requires at least one task")
        self._validate(tasks)

        workflow_id = workflow_id or uuid.uuid4().hex
        now = _now()
        with self.backend.transaction() as db:
            _execute(
                db,
                self.backend,
                """
                INSERT INTO workflows(
                    id, name, repository, status,
                    metadata_json, created_at, updated_at
                )
                VALUES(?, ?, ?, 'pending', ?, ?, ?)
                """,
                (
                    workflow_id,
                    name,
                    repository,
                    json.dumps(metadata or {}, ensure_ascii=False),
                    now,
                    now,
                ),
            )
            for task in tasks:
                _execute(
                    db,
                    self.backend,
                    """
                    INSERT INTO workflow_tasks(
                        workflow_id, task_id, title, payload_json,
                        status, priority, dependencies_json,
                        claimed_job_key, result_json, attempts,
                        max_attempts, estimated_minutes,
                        created_at, updated_at
                    )
                    VALUES(
                        ?, ?, ?, ?, 'pending', ?, ?, NULL, NULL, 0,
                        ?, ?, ?, ?
                    )
                    """,
                    (
                        workflow_id,
                        task.task_id,
                        task.title,
                        json.dumps(task.payload, ensure_ascii=False),
                        task.priority,
                        json.dumps(list(task.dependencies)),
                        task.max_attempts,
                        task.estimated_minutes,
                        now,
                        now,
                    ),
                )
            self.backend.append_event(
                db,
                "workflow-created",
                {
                    "workflow_id":workflow_id,
                    "name":name,
                    "task_count":len(tasks),
                },
                repository=repository,
            )

        self.refresh(workflow_id)
        return self.get(workflow_id)

    def get(self, workflow_id: str) -> dict:
        with self.backend.connect() as db:
            workflow = _execute(
                db,
                self.backend,
                "SELECT * FROM workflows WHERE id=?",
                (workflow_id,),
            ).fetchone()
            if workflow is None:
                raise KeyError(workflow_id)
            tasks = _execute(
                db,
                self.backend,
                """
                SELECT * FROM workflow_tasks
                WHERE workflow_id=?
                ORDER BY created_at ASC, task_id ASC
                """,
                (workflow_id,),
            ).fetchall()
            artifacts = _execute(
                db,
                self.backend,
                """
                SELECT * FROM artifacts
                WHERE workflow_id=?
                ORDER BY created_at ASC
                """,
                (workflow_id,),
            ).fetchall()

        return {
            "id":workflow["id"],
            "name":workflow["name"],
            "repository":workflow["repository"],
            "status":workflow["status"],
            "metadata":json.loads(workflow["metadata_json"]),
            "created_at":workflow["created_at"],
            "updated_at":workflow["updated_at"],
            "tasks":[self._task_dict(row) for row in tasks],
            "artifacts":[self._artifact_dict(row) for row in artifacts],
        }

    @staticmethod
    def _task_dict(row) -> dict:
        return {
            "workflow_id":row["workflow_id"],
            "task_id":row["task_id"],
            "title":row["title"],
            "payload":json.loads(row["payload_json"]),
            "status":row["status"],
            "priority":row["priority"],
            "dependencies":json.loads(row["dependencies_json"]),
            "claimed_job_key":row["claimed_job_key"],
            "result":(
                json.loads(row["result_json"])
                if row["result_json"]
                else None
            ),
            "attempts":row["attempts"],
            "max_attempts":row["max_attempts"],
            "estimated_minutes":row["estimated_minutes"],
            "created_at":row["created_at"],
            "updated_at":row["updated_at"],
        }

    @staticmethod
    def _artifact_dict(row) -> dict:
        return {
            "id":row["id"],
            "workflow_id":row["workflow_id"],
            "task_id":row["task_id"],
            "name":row["name"],
            "uri":row["uri"],
            "sha256":row["sha256"],
            "metadata":json.loads(row["metadata_json"]),
            "created_at":row["created_at"],
        }

    def refresh(self, workflow_id: str) -> dict:
        now = _now()
        with self.backend.transaction() as db:
            rows = _execute(
                db,
                self.backend,
                """
                SELECT * FROM workflow_tasks
                WHERE workflow_id=?
                """,
                (workflow_id,),
            ).fetchall()
            if not rows:
                exists = _execute(
                    db,
                    self.backend,
                    "SELECT id FROM workflows WHERE id=?",
                    (workflow_id,),
                ).fetchone()
                if exists is None:
                    raise KeyError(workflow_id)

            status_by_id = {
                row["task_id"]:row["status"]
                for row in rows
            }

            changed = True
            while changed:
                changed = False
                for row in rows:
                    current = status_by_id[row["task_id"]]
                    if current not in {"pending", "blocked"}:
                        continue
                    deps = json.loads(row["dependencies_json"])
                    dep_states = [
                        status_by_id[dep]
                        for dep in deps
                    ]
                    new_status = current
                    if any(
                        state in {"failed", "cancelled", "blocked"}
                        for state in dep_states
                    ):
                        new_status = "blocked"
                    elif all(state == "succeeded" for state in dep_states):
                        new_status = "ready"
                    elif not deps:
                        new_status = "ready"

                    if new_status != current:
                        _execute(
                            db,
                            self.backend,
                            """
                            UPDATE workflow_tasks
                            SET status=?, updated_at=?
                            WHERE workflow_id=? AND task_id=?
                            """,
                            (
                                new_status,
                                now,
                                workflow_id,
                                row["task_id"],
                            ),
                        )
                        status_by_id[row["task_id"]] = new_status
                        changed = True

            statuses = list(status_by_id.values())
            if statuses and all(s == "succeeded" for s in statuses):
                workflow_status = "succeeded"
            elif any(s == "failed" for s in statuses):
                if all(s in TERMINAL_TASK_STATES for s in statuses):
                    workflow_status = "failed"
                else:
                    workflow_status = "running"
            elif any(
                s in {"ready", "queued", "running", "acked"}
                for s in statuses
            ):
                workflow_status = "running"
            elif any(s == "cancelled" for s in statuses):
                workflow_status = "cancelled"
            else:
                workflow_status = "pending"

            _execute(
                db,
                self.backend,
                """
                UPDATE workflows
                SET status=?, updated_at=?
                WHERE id=?
                """,
                (workflow_status, now, workflow_id),
            )

        return self.get(workflow_id)

    def dispatch_ready(
        self,
        workflow_id: str,
        *,
        limit: int = 10,
    ) -> list[dict]:
        self.refresh(workflow_id)
        workflow = self.get(workflow_id)
        if workflow["status"] in {"succeeded", "failed", "cancelled"}:
            return []

        ready = [
            task for task in workflow["tasks"]
            if task["status"] == "ready"
        ]
        ready.sort(
            key=lambda task: (
                -float(task["priority"]),
                task["task_id"],
            )
        )
        dispatched = []

        for task in ready[:max(1, limit)]:
            payload = dict(task["payload"])
            handoff = dict(payload.get("handoff") or payload)
            handoff.setdefault("repository", workflow["repository"])
            handoff.setdefault("task", task["title"])
            handoff.setdefault("priority", task["priority"])
            handoff["workflow_id"] = workflow_id
            handoff["workflow_task_id"] = task["task_id"]
            queue_payload = {
                **payload,
                "schema_version":"production-os/workflow-dispatch/v1",
                "workflow_id":workflow_id,
                "workflow_task_id":task["task_id"],
                "handoff":handoff,
            }
            job = self.queue.enqueue(queue_payload)
            now = _now()
            with self.backend.transaction() as db:
                updated = _execute(
                    db,
                    self.backend,
                    """
                    UPDATE workflow_tasks
                    SET status='queued', claimed_job_key=?,
                        attempts=attempts+1, updated_at=?
                    WHERE workflow_id=? AND task_id=? AND status='ready'
                    """,
                    (
                        job["key"],
                        now,
                        workflow_id,
                        task["task_id"],
                    ),
                )
                if updated.rowcount != 1:
                    raise RuntimeError(
                        f"workflow task {task['task_id']} lost dispatch race"
                    )
                self.backend.append_event(
                    db,
                    "workflow-task-dispatched",
                    {
                        "workflow_id":workflow_id,
                        "task_id":task["task_id"],
                        "job_key":job["key"],
                    },
                    repository=workflow["repository"],
                    task_key_value=job["key"],
                )
            dispatched.append(job)

        if dispatched:
            self.refresh(workflow_id)
        return dispatched

    def record_result(
        self,
        workflow_id: str,
        task_id: str,
        *,
        succeeded: bool,
        result: dict | None = None,
    ) -> dict:
        now = _now()
        with self.backend.transaction() as db:
            row = _execute(
                db,
                self.backend,
                """
                SELECT * FROM workflow_tasks
                WHERE workflow_id=? AND task_id=?
                """,
                (workflow_id, task_id),
            ).fetchone()
            if row is None:
                raise KeyError(f"{workflow_id}/{task_id}")

            if succeeded:
                status = "succeeded"
            elif int(row["attempts"]) < int(row["max_attempts"]):
                status = "ready"
            else:
                status = "failed"

            _execute(
                db,
                self.backend,
                """
                UPDATE workflow_tasks
                SET status=?, result_json=?, claimed_job_key=NULL,
                    updated_at=?
                WHERE workflow_id=? AND task_id=?
                """,
                (
                    status,
                    json.dumps(result or {}, ensure_ascii=False),
                    now,
                    workflow_id,
                    task_id,
                ),
            )
            self.backend.append_event(
                db,
                "workflow-task-result",
                {
                    "workflow_id":workflow_id,
                    "task_id":task_id,
                    "succeeded":succeeded,
                    "status":status,
                },
                task_key_value=row["claimed_job_key"],
            )

        refreshed = self.refresh(workflow_id)
        if status == "succeeded":
            self.dispatch_ready(workflow_id)
            refreshed = self.refresh(workflow_id)
        return refreshed

    def cancel(self, workflow_id: str) -> dict:
        now = _now()
        with self.backend.transaction() as db:
            exists = _execute(
                db,
                self.backend,
                "SELECT id FROM workflows WHERE id=?",
                (workflow_id,),
            ).fetchone()
            if exists is None:
                raise KeyError(workflow_id)
            _execute(
                db,
                self.backend,
                """
                UPDATE workflow_tasks
                SET status='cancelled', updated_at=?
                WHERE workflow_id=?
                  AND status NOT IN ('succeeded','failed','cancelled')
                """,
                (now, workflow_id),
            )
            _execute(
                db,
                self.backend,
                """
                UPDATE workflows
                SET status='cancelled', updated_at=?
                WHERE id=?
                """,
                (now, workflow_id),
            )
            self.backend.append_event(
                db,
                "workflow-cancelled",
                {"workflow_id":workflow_id},
            )
        return self.get(workflow_id)

    def add_artifact(
        self,
        workflow_id: str,
        *,
        name: str,
        uri: str,
        task_id: str | None = None,
        sha256: str | None = None,
        metadata: dict | None = None,
    ) -> dict:
        artifact_id = uuid.uuid4().hex
        now = _now()
        with self.backend.transaction() as db:
            _execute(
                db,
                self.backend,
                """
                INSERT INTO artifacts(
                    id, workflow_id, task_id, name, uri,
                    sha256, metadata_json, created_at
                )
                VALUES(?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    artifact_id,
                    workflow_id,
                    task_id,
                    name,
                    uri,
                    sha256,
                    json.dumps(metadata or {}, ensure_ascii=False),
                    now,
                ),
            )
            self.backend.append_event(
                db,
                "artifact-registered",
                {
                    "artifact_id":artifact_id,
                    "workflow_id":workflow_id,
                    "task_id":task_id,
                    "name":name,
                    "uri":uri,
                },
            )
            row = _execute(
                db,
                self.backend,
                "SELECT * FROM artifacts WHERE id=?",
                (artifact_id,),
            ).fetchone()
        return self._artifact_dict(row)

    def critical_path(self, workflow_id: str) -> dict:
        workflow = self.get(workflow_id)
        tasks = {task["task_id"]:task for task in workflow["tasks"]}
        memo: dict[str, tuple[float, list[str]]] = {}

        def longest(task_id: str) -> tuple[float, list[str]]:
            if task_id in memo:
                return memo[task_id]
            task = tasks[task_id]
            weight = float(task["estimated_minutes"])
            deps = task["dependencies"]
            if not deps:
                result = (weight, [task_id])
            else:
                best = max(
                    (longest(dep) for dep in deps),
                    key=lambda item: item[0],
                )
                result = (best[0] + weight, best[1] + [task_id])
            memo[task_id] = result
            return result

        best = max(
            (longest(task_id) for task_id in tasks),
            key=lambda item: item[0],
        )
        return {
            "workflow_id":workflow_id,
            "estimated_minutes":round(best[0], 2),
            "task_ids":best[1],
        }
