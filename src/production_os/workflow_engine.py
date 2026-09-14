from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from .runtime_state import task_key
from .result_cache import ResultCache, fingerprint
from .change_impact import analyze_change_impact


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
    @staticmethod
    def _expand_splittable_tasks(
        tasks: list[WorkflowTaskSpec],
    ) -> list[WorkflowTaskSpec]:
        expanded: list[WorkflowTaskSpec] = []
        for task in tasks:
            payload = dict(task.payload)
            if not bool(payload.get("splittable", False)):
                expanded.append(task)
                continue

            items = list(payload.get("split_items", []))
            if not items:
                expanded.append(task)
                continue

            split_size = max(1, int(payload.get("split_size", 1)))
            shards = [
                items[index:index + split_size]
                for index in range(0, len(items), split_size)
            ]
            shard_ids: list[str] = []

            for index, chunk in enumerate(shards, start=1):
                shard_id = f"{task.task_id}#shard-{index}"
                shard_ids.append(shard_id)
                shard_payload = {
                    key:value
                    for key, value in payload.items()
                    if key not in {
                        "splittable",
                        "split_items",
                        "split_size",
                    }
                }
                shard_payload["split_chunk"] = chunk
                shard_payload["split_index"] = index
                shard_payload["split_count"] = len(shards)
                shard_payload["split_parent_task_id"] = task.task_id

                expanded.append(
                    WorkflowTaskSpec(
                        task_id=shard_id,
                        title=f"{task.title} [{index}/{len(shards)}]",
                        payload=shard_payload,
                        dependencies=task.dependencies,
                        priority=task.priority,
                        max_attempts=task.max_attempts,
                        estimated_minutes=max(
                            0.01,
                            task.estimated_minutes / len(shards),
                        ),
                    )
                )

            expanded.append(
                WorkflowTaskSpec(
                    task_id=task.task_id,
                    title=task.title,
                    payload={
                        "virtual_barrier":True,
                        "split_parent":True,
                        "split_shards":shard_ids,
                    },
                    dependencies=tuple(shard_ids),
                    priority=task.priority,
                    max_attempts=1,
                    estimated_minutes=0.0,
                )
            )

        return expanded

    def __init__(self, backend, queue):
        self.backend = backend
        self.queue = queue
        self.cache = ResultCache(backend)

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
        tasks = self._expand_splittable_tasks(tasks)
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

        if metadata is not None and "changed_paths" in metadata:
            self.apply_change_impact(
                workflow_id,
                [
                    str(path)
                    for path in metadata.get("changed_paths", [])
                ],
            )
        else:
            self.refresh(workflow_id)
        return self.get(workflow_id)

    def apply_change_impact(
        self,
        workflow_id: str,
        changed_paths: list[str],
    ) -> list[dict]:
        workflow = self.get(workflow_id)

        # Impact can be recomputed only before real execution starts.
        # Prior impact-skips and virtual barriers are reversible because they
        # have not consumed worker capacity or produced execution side effects.
        for task in workflow["tasks"]:
            result = dict(task.get("result") or {})
            reversible_success = (
                task["status"] == "succeeded"
                and (
                    bool(result.get("skipped", False))
                    or bool(
                        task.get("payload", {}).get(
                            "virtual_barrier",
                            False,
                        )
                    )
                )
            )
            if (
                task["status"] not in {"pending", "ready"}
                and not reversible_success
            ):
                raise RuntimeError(
                    "change impact cannot be recomputed after "
                    f"workflow execution started: {task['task_id']} "
                    f"is {task['status']}"
                )

        decisions = analyze_change_impact(
            workflow["tasks"],
            changed_paths,
        )
        task_lookup = {
            task["task_id"]:task
            for task in workflow["tasks"]
        }
        now = _now()

        with self.backend.transaction() as db:
            # Reopen tasks skipped by a previous impact evaluation before
            # applying the new decision set.
            for task in workflow["tasks"]:
                result = dict(task.get("result") or {})
                if not bool(result.get("skipped", False)):
                    continue
                _execute(
                    db,
                    self.backend,
                    """
                    UPDATE workflow_tasks
                    SET status='pending', result_json=NULL,
                        claimed_job_key=NULL, updated_at=?
                    WHERE workflow_id=? AND task_id=?
                      AND status='succeeded'
                    """,
                    (
                        now,
                        workflow_id,
                        task["task_id"],
                    ),
                )

            for decision in decisions:
                if decision.affected:
                    continue
                task = task_lookup[decision.task_id]
                if bool(
                    task.get("payload", {}).get(
                        "virtual_barrier",
                        False,
                    )
                ):
                    continue

                _execute(
                    db,
                    self.backend,
                    """
                    UPDATE workflow_tasks
                    SET status='succeeded', result_json=?,
                        claimed_job_key=NULL, updated_at=?
                    WHERE workflow_id=? AND task_id=?
                      AND status IN ('pending','ready')
                    """,
                    (
                        json.dumps(
                            {
                                "skipped":True,
                                "reason":decision.reason,
                                "changed_paths":changed_paths,
                            },
                            ensure_ascii=False,
                        ),
                        now,
                        workflow_id,
                        decision.task_id,
                    ),
                )

            self.backend.append_event(
                db,
                "workflow-impact-evaluated",
                {
                    "workflow_id":workflow_id,
                    "changed_paths":changed_paths,
                    "affected":[
                        item.task_id
                        for item in decisions
                        if item.affected
                    ],
                    "skipped":[
                        item.task_id
                        for item in decisions
                        if not item.affected
                    ],
                },
                repository=workflow["repository"],
            )

        self.refresh(workflow_id)
        return [item.to_dict() for item in decisions]

    @staticmethod
    def _spec_from_task(task: dict) -> WorkflowTaskSpec:
        return WorkflowTaskSpec(
            task_id=str(task["task_id"]),
            title=str(task["title"]),
            payload=dict(task.get("payload") or {}),
            dependencies=tuple(
                str(value)
                for value in task.get("dependencies", [])
            ),
            priority=float(task.get("priority", 0.0)),
            max_attempts=max(
                1,
                int(task.get("max_attempts", 1)),
            ),
            estimated_minutes=max(
                0.0,
                float(task.get("estimated_minutes", 1.0)),
            ),
        )

    def create_pr_generation(
        self,
        source_workflow_id: str,
        *,
        head_sha: str,
    ) -> dict:
        source = self.get(source_workflow_id)
        metadata = dict(source.get("metadata") or {})
        current_generation = int(
            metadata.get("github_pr_generation", 1)
        )
        metadata.update({
            "github_pr_head_sha":str(head_sha),
            "github_pr_generation":current_generation + 1,
            "supersedes_workflow_id":source_workflow_id,
        })
        metadata.pop("changed_paths", None)

        return self.create(
            name=source["name"],
            repository=source["repository"],
            tasks=[
                self._spec_from_task(task)
                for task in source["tasks"]
            ],
            metadata=metadata,
        )

    def supersede(
        self,
        workflow_id: str,
        *,
        superseded_by: str,
        head_sha: str,
    ) -> dict:
        workflow = self.get(workflow_id)
        now = _now()
        metadata = dict(workflow.get("metadata") or {})
        metadata.update({
            "superseded":True,
            "superseded_by_workflow_id":superseded_by,
            "superseded_by_head_sha":str(head_sha),
        })

        with self.backend.transaction() as db:
            rows = _execute(
                db,
                self.backend,
                """
                SELECT task_id, claimed_job_key
                FROM workflow_tasks
                WHERE workflow_id=?
                  AND status NOT IN (
                    'succeeded','failed','cancelled'
                  )
                """,
                (workflow_id,),
            ).fetchall()

            cancelled_jobs: list[str] = []
            for row in rows:
                key = row["claimed_job_key"]
                if not key:
                    continue
                job = _execute(
                    db,
                    self.backend,
                    "SELECT status FROM jobs WHERE key=?",
                    (key,),
                ).fetchone()
                if job is None:
                    continue
                if job["status"] not in {
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
                cancelled_jobs.append(str(key))

            _execute(
                db,
                self.backend,
                """
                UPDATE workflow_tasks
                SET status='cancelled', updated_at=?
                WHERE workflow_id=?
                  AND status NOT IN (
                    'succeeded','failed','cancelled'
                  )
                """,
                (now, workflow_id),
            )
            _execute(
                db,
                self.backend,
                """
                UPDATE workflows
                SET status='cancelled',
                    metadata_json=?,
                    updated_at=?
                WHERE id=?
                """,
                (
                    json.dumps(metadata, ensure_ascii=False),
                    now,
                    workflow_id,
                ),
            )
            self.backend.append_event(
                db,
                "workflow-superseded",
                {
                    "workflow_id":workflow_id,
                    "superseded_by":superseded_by,
                    "head_sha":head_sha,
                    "cancelled_jobs":cancelled_jobs,
                },
                repository=workflow["repository"],
            )
        return self.get(workflow_id)

    def ensure_pr_generation(
        self,
        repository: str,
        pr_number: int,
        head_sha: str,
    ) -> tuple[dict | None, list[dict]]:
        workflows = self.find_by_github_pr(
            repository,
            pr_number,
        )
        if not workflows:
            return None, []

        latest = workflows[0]
        latest_metadata = dict(latest.get("metadata") or {})
        current_sha = str(
            latest_metadata.get("github_pr_head_sha") or ""
        )
        if not current_sha:
            latest_metadata.update({
                "github_pr_head_sha":str(head_sha),
                "github_pr_generation":int(
                    latest_metadata.get(
                        "github_pr_generation",
                        1,
                    )
                ),
            })
            with self.backend.transaction() as db:
                _execute(
                    db,
                    self.backend,
                    """
                    UPDATE workflows
                    SET metadata_json=?, updated_at=?
                    WHERE id=?
                    """,
                    (
                        json.dumps(
                            latest_metadata,
                            ensure_ascii=False,
                        ),
                        _now(),
                        latest["id"],
                    ),
                )
                self.backend.append_event(
                    db,
                    "workflow-pr-generation-bound",
                    {
                        "workflow_id":latest["id"],
                        "pr_number":pr_number,
                        "head_sha":head_sha,
                        "generation":latest_metadata[
                            "github_pr_generation"
                        ],
                    },
                    repository=repository,
                )
            return self.get(latest["id"]), []

        if current_sha == str(head_sha):
            return latest, []

        generation = self.create_pr_generation(
            latest["id"],
            head_sha=head_sha,
        )
        superseded = []
        for workflow in workflows:
            metadata = dict(workflow.get("metadata") or {})
            if bool(metadata.get("superseded", False)):
                continue
            if workflow["id"] == generation["id"]:
                continue
            superseded.append(
                self.supersede(
                    workflow["id"],
                    superseded_by=generation["id"],
                    head_sha=head_sha,
                )
            )
        return generation, superseded

    def find_by_github_pr(
        self,
        repository: str,
        pr_number: int,
    ) -> list[dict]:
        matches: list[dict] = []
        with self.backend.connect() as db:
            rows = _execute(
                db,
                self.backend,
                """
                SELECT id, metadata_json
                FROM workflows
                WHERE repository=?
                ORDER BY created_at DESC
                """,
                (repository,),
            ).fetchall()

        for row in rows:
            metadata = json.loads(row["metadata_json"])
            value = metadata.get("github_pr_number")
            if value is None:
                continue
            try:
                bound_pr = int(value)
            except (TypeError, ValueError):
                continue
            if bound_pr != int(pr_number):
                continue
            matches.append(self.get(str(row["id"])))
        return matches

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
                    payload = json.loads(row["payload_json"])
                    if any(
                        state in {"failed", "cancelled", "blocked"}
                        for state in dep_states
                    ):
                        new_status = "blocked"
                    elif all(state == "succeeded" for state in dep_states):
                        new_status = (
                            "succeeded"
                            if bool(payload.get("virtual_barrier", False))
                            else "ready"
                        )
                    elif not deps:
                        new_status = (
                            "succeeded"
                            if bool(payload.get("virtual_barrier", False))
                            else "ready"
                        )

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
        cache_hits = 0

        for task in ready[:max(1, limit)]:
            payload = dict(task["payload"])
            if bool(payload.get("cacheable", False)):
                cache_inputs = dict(
                    payload.get("cache_inputs")
                    or {"payload":payload}
                )
                cache_key = fingerprint(
                    repository=workflow["repository"],
                    task=task["title"],
                    inputs=cache_inputs,
                )
                cached = self.cache.get(cache_key)
                if cached is not None:
                    now = _now()
                    with self.backend.transaction() as db:
                        updated = _execute(
                            db,
                            self.backend,
                            """
                            UPDATE workflow_tasks
                            SET status='succeeded', result_json=?,
                                claimed_job_key=NULL, updated_at=?
                            WHERE workflow_id=? AND task_id=?
                              AND status='ready'
                            """,
                            (
                                json.dumps(
                                    {
                                        "cache_hit":True,
                                        "cache_fingerprint":cache_key,
                                        "cached_result":cached["result"],
                                        "artifacts":cached["artifacts"],
                                    },
                                    ensure_ascii=False,
                                ),
                                now,
                                workflow_id,
                                task["task_id"],
                            ),
                        )
                        if updated.rowcount == 1:
                            self.backend.append_event(
                                db,
                                "workflow-task-cache-hit",
                                {
                                    "workflow_id":workflow_id,
                                    "task_id":task["task_id"],
                                    "fingerprint":cache_key,
                                },
                                repository=workflow["repository"],
                            )
                            cache_hits += 1
                    continue
            handoff = dict(payload.get("handoff") or payload)
            handoff.setdefault("repository", workflow["repository"])
            handoff.setdefault("task", task["title"])
            handoff.setdefault("priority", task["priority"])
            handoff["workflow_id"] = workflow_id
            handoff["workflow_task_id"] = task["task_id"]
            attempt_number = int(task["attempts"]) + 1
            queue_payload = {
                **payload,
                "schema_version":"production-os/workflow-dispatch/v1",
                "workflow_id":workflow_id,
                "workflow_task_id":task["task_id"],
                "workflow_attempt":attempt_number,
                "idempotency_key":task_key(
                    workflow_id,
                    f"{task['task_id']}:{attempt_number}",
                ),
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

        if dispatched or cache_hits:
            self.refresh(workflow_id)
        if cache_hits:
            remaining = max(0, limit - len(dispatched))
            if remaining > 0:
                dispatched.extend(
                    self.dispatch_ready(
                        workflow_id,
                        limit=remaining,
                    )
                )
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

        if succeeded:
            task_payload = json.loads(row["payload_json"])
            if bool(task_payload.get("cacheable", False)):
                cache_inputs = dict(
                    task_payload.get("cache_inputs")
                    or {"payload":task_payload}
                )
                cache_key = fingerprint(
                    repository=self.get(workflow_id)["repository"],
                    task=row["title"],
                    inputs=cache_inputs,
                )
                self.cache.put(
                    key=cache_key,
                    repository=self.get(workflow_id)["repository"],
                    task=row["title"],
                    result=result or {},
                )

        refreshed = self.refresh(workflow_id)
        if status in {"succeeded", "ready"}:
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
