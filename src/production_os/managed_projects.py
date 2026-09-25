from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from .workflow_engine import WorkflowEngine, WorkflowTaskSpec, _execute


MANAGED_PROJECT_SCHEMA = "production-os/managed-project/v3"
LEGACY_MANAGED_PROJECT_SCHEMA = "production-os/managed-project/v2"
ACTIVE = "ACTIVE"
REVIEW_REQUIRED = "REVIEW_REQUIRED"
NEEDS_ATTENTION = "NEEDS_ATTENTION"
DONE = "DONE"
PROJECT_STATES = {ACTIVE, REVIEW_REQUIRED, NEEDS_ATTENTION, DONE}
USAGE_KEYS = (
    "input_tokens",
    "cached_input_tokens",
    "output_tokens",
    "reasoning_tokens",
    "total_tokens",
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _positive_int(value, *, field: str) -> int:
    if isinstance(value, bool):
        raise ValueError(f"{field} must be a positive integer")
    try:
        number = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field} must be a positive integer") from exc
    if number <= 0:
        raise ValueError(f"{field} must be a positive integer")
    return number


def _usage_from_result(result: dict | None) -> dict:
    if not isinstance(result, dict):
        return {}
    candidates = [result.get("usage")]
    evidence = result.get("evidence")
    if isinstance(evidence, dict):
        candidates.append(evidence.get("usage"))
    usage = next((item for item in candidates if isinstance(item, dict)), None)
    if usage is None:
        return {}

    normalized: dict = {}
    for key in USAGE_KEYS:
        value = usage.get(key)
        if isinstance(value, bool):
            continue
        try:
            number = int(value)
        except (TypeError, ValueError):
            continue
        if number >= 0:
            normalized[key] = number
    if "total_tokens" not in normalized:
        normalized["total_tokens"] = (
            normalized.get("input_tokens", 0)
            + normalized.get("output_tokens", 0)
        )
    runs = usage.get("runs")
    if not isinstance(runs, bool):
        try:
            run_count = int(runs)
        except (TypeError, ValueError):
            run_count = 0
        if run_count >= 0:
            normalized["runs"] = run_count
    agents = usage.get("agents")
    if isinstance(agents, dict):
        clean = {}
        for name, count in agents.items():
            if (
                not isinstance(name, str)
                or not name.strip()
                or isinstance(count, bool)
            ):
                continue
            try:
                value = int(count)
            except (TypeError, ValueError):
                continue
            if value >= 0:
                clean[name] = value
        normalized["agents"] = clean
    return normalized


class ManagedProjectService:
    def __init__(self, workflows: WorkflowEngine):
        self.workflows = workflows
        self.backend = workflows.backend

    @staticmethod
    def _validate_repository(repository: str) -> str:
        repository = str(repository or "").strip()
        parts = repository.split("/")
        if (
            len(parts) != 2
            or any(not part or part in {".", ".."} for part in parts)
        ):
            raise ValueError("repository must be owner/name")
        return repository

    def _workflow_spec(
        self,
        *,
        project_id: str,
        repository: str,
        final_goal: str,
        instruction: str,
        generation: int,
        kind: str,
        token_budget: int,
        agent_preference: str,
    ) -> WorkflowTaskSpec:
        return WorkflowTaskSpec(
            task_id="implementation",
            title=instruction[:120],
            payload={
                "managed_project_id":project_id,
                "managed_project_generation":generation,
                "managed_project_kind":kind,
                "handoff":{
                    "repository":repository,
                    "task":instruction,
                    "final_goal":final_goal,
                    "agent_preference":agent_preference,
                    "token_budget":token_budget,
                },
            },
            priority=100,
            max_attempts=3,
            estimated_minutes=30,
        )

    def _create_workflow(
        self,
        *,
        project_id: str,
        repository: str,
        final_goal: str,
        instruction: str,
        generation: int,
        kind: str,
        token_budget: int,
        agent_preference: str,
        dispatch: bool,
    ) -> dict:
        workflow = self.workflows.create(
            name=f"Managed project: {repository} · g{generation}",
            repository=repository,
            tasks=[
                self._workflow_spec(
                    project_id=project_id,
                    repository=repository,
                    final_goal=final_goal,
                    instruction=instruction,
                    generation=generation,
                    kind=kind,
                    token_budget=token_budget,
                    agent_preference=agent_preference,
                )
            ],
            metadata={
                "managed_project_id":project_id,
                "managed_project_generation":generation,
                "managed_project_kind":kind,
                "managed_project_schema":MANAGED_PROJECT_SCHEMA,
                "final_goal":final_goal,
                "token_budget":token_budget,
                "agent_preference":agent_preference,
            },
        )
        if dispatch:
            self.workflows.dispatch_ready(workflow["id"], limit=1)
        return self.workflows.get(workflow["id"])

    def _delete_unstarted_workflow(self, workflow_id: str) -> None:
        with self.backend.transaction() as db:
            _execute(
                db,
                self.backend,
                "DELETE FROM workflow_tasks WHERE workflow_id=?",
                (workflow_id,),
            )
            _execute(
                db,
                self.backend,
                "DELETE FROM workflows WHERE id=?",
                (workflow_id,),
            )

    def create(
        self,
        *,
        repository: str,
        final_goal: str,
        token_budget: int,
        agent_preference: str = "auto",
        requested_by: str = "operator",
    ) -> dict:
        repository = self._validate_repository(repository)
        final_goal = str(final_goal or "").strip()
        if not final_goal:
            raise ValueError("final_goal is required")
        budget = _positive_int(token_budget, field="token_budget")
        agent = str(agent_preference or "auto").strip() or "auto"
        actor = str(requested_by or "operator").strip() or "operator"
        project_id = uuid4().hex
        now = _now()

        with self.backend.transaction() as db:
            _execute(
                db,
                self.backend,
                """INSERT INTO managed_projects(
                    id, repository, final_goal, token_budget,
                    agent_preference, status, current_workflow_id,
                    generation, created_by, created_at, updated_at,
                    reviewed_at, completed_at, completed_by
                ) VALUES(?,?,?,?,?,'ACTIVE',NULL,1,?,?,?,NULL,NULL,NULL)""",
                (
                    project_id,
                    repository,
                    final_goal,
                    budget,
                    agent,
                    actor,
                    now,
                    now,
                ),
            )

        try:
            workflow = self._create_workflow(
                project_id=project_id,
                repository=repository,
                final_goal=final_goal,
                instruction=final_goal,
                generation=1,
                kind="initial",
                token_budget=budget,
                agent_preference=agent,
                dispatch=False,
            )
        except Exception:
            with self.backend.transaction() as db:
                _execute(
                    db,
                    self.backend,
                    "DELETE FROM managed_projects WHERE id=?",
                    (project_id,),
                )
            raise

        try:
            with self.backend.transaction() as db:
                _execute(
                    db,
                    self.backend,
                    """UPDATE managed_projects
                       SET current_workflow_id=?, updated_at=?
                       WHERE id=?""",
                    (workflow["id"], _now(), project_id),
                )
                _execute(
                    db,
                    self.backend,
                    """INSERT INTO managed_project_runs(
                        id, project_id, generation, kind, instruction,
                        workflow_id, requested_by, created_at
                    ) VALUES(?,?,?,?,?,?,?,?)""",
                    (
                        uuid4().hex,
                        project_id,
                        1,
                        "initial",
                        final_goal,
                        workflow["id"],
                        actor,
                        now,
                    ),
                )
        except Exception:
            self._delete_unstarted_workflow(workflow["id"])
            with self.backend.transaction() as db:
                _execute(
                    db,
                    self.backend,
                    "DELETE FROM managed_projects WHERE id=?",
                    (project_id,),
                )
            raise

        self.workflows.dispatch_ready(workflow["id"], limit=1)
        return self.get(project_id)

    def _resolve_project_id(self, identifier: str) -> str:
        identifier = str(identifier)
        with self.backend.connect() as db:
            row = _execute(
                db,
                self.backend,
                """SELECT id FROM managed_projects
                   WHERE id=? OR current_workflow_id=?
                   LIMIT 1""",
                (identifier, identifier),
            ).fetchone()
            if row is None:
                row = _execute(
                    db,
                    self.backend,
                    """SELECT project_id AS id
                       FROM managed_project_runs
                       WHERE workflow_id=?
                       LIMIT 1""",
                    (identifier,),
                ).fetchone()
        if row is None:
            migrated = self._migrate_legacy_workflow(identifier)
            if migrated is None:
                raise KeyError(identifier)
            return migrated
        return str(row["id"])

    def _migrate_legacy_workflow(self, workflow_id: str) -> str | None:
        try:
            workflow = self.workflows.get(workflow_id)
        except KeyError:
            return None
        metadata = dict(workflow.get("metadata") or {})
        legacy = metadata.get("managed_project")
        if (
            not isinstance(legacy, dict)
            or legacy.get("schema_version") != LEGACY_MANAGED_PROJECT_SCHEMA
        ):
            return None

        project_id = uuid4().hex
        now = _now()
        final_goal = str(legacy.get("final_goal") or "")
        budget = _positive_int(
            legacy.get("token_budget") or 1,
            field="token_budget",
        )
        agent = str(legacy.get("agent_preference") or "auto")
        human_state = str(legacy.get("human_state") or "active")
        if human_state == "done":
            status = DONE
            completed_at = legacy.get("approved_at") or now
            completed_by = legacy.get("approved_by")
        elif workflow.get("status") == "succeeded":
            status = REVIEW_REQUIRED
            completed_at = None
            completed_by = None
        elif workflow.get("status") in {"failed", "cancelled"}:
            status = NEEDS_ATTENTION
            completed_at = None
            completed_by = None
        else:
            status = ACTIVE
            completed_at = None
            completed_by = None

        with self.backend.transaction() as db:
            existing = _execute(
                db,
                self.backend,
                """SELECT project_id FROM managed_project_runs
                   WHERE workflow_id=? LIMIT 1""",
                (workflow_id,),
            ).fetchone()
            if existing is not None:
                return str(existing["project_id"])
            _execute(
                db,
                self.backend,
                """INSERT INTO managed_projects(
                    id, repository, final_goal, token_budget,
                    agent_preference, status, current_workflow_id,
                    generation, created_by, created_at, updated_at,
                    reviewed_at, completed_at, completed_by
                ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    project_id,
                    workflow["repository"],
                    final_goal,
                    budget,
                    agent,
                    status,
                    workflow_id,
                    1,
                    "legacy-migration",
                    workflow.get("created_at") or now,
                    now,
                    now if status == REVIEW_REQUIRED else None,
                    completed_at,
                    completed_by,
                ),
            )
            _execute(
                db,
                self.backend,
                """INSERT INTO managed_project_runs(
                    id, project_id, generation, kind, instruction,
                    workflow_id, requested_by, created_at
                ) VALUES(?,?,?,?,?,?,?,?)""",
                (
                    uuid4().hex,
                    project_id,
                    1,
                    "legacy",
                    final_goal,
                    workflow_id,
                    "legacy-migration",
                    workflow.get("created_at") or now,
                ),
            )
        return project_id

    def reconcile(self, identifier: str) -> dict:
        project_id = self._resolve_project_id(identifier)
        with self.backend.connect() as db:
            project = _execute(
                db,
                self.backend,
                "SELECT * FROM managed_projects WHERE id=?",
                (project_id,),
            ).fetchone()
        if project is None:
            raise KeyError(project_id)
        current = dict(project)
        if current["status"] == DONE:
            return current

        workflow_id = current.get("current_workflow_id")
        if not workflow_id:
            target = NEEDS_ATTENTION
        else:
            try:
                workflow = self.workflows.refresh(str(workflow_id))
            except KeyError:
                target = NEEDS_ATTENTION
            else:
                workflow_status = workflow.get("status")
                if workflow_status == "succeeded":
                    target = REVIEW_REQUIRED
                elif workflow_status in {"failed", "cancelled"}:
                    target = NEEDS_ATTENTION
                else:
                    target = ACTIVE

        if target == current["status"]:
            return current
        now = _now()
        with self.backend.transaction() as db:
            _execute(
                db,
                self.backend,
                """UPDATE managed_projects
                   SET status=?, updated_at=?,
                       reviewed_at=CASE
                           WHEN ?='REVIEW_REQUIRED' THEN ?
                           ELSE reviewed_at
                       END
                   WHERE id=? AND status<>'DONE'""",
                (target, now, target, now, project_id),
            )
        with self.backend.connect() as db:
            row = _execute(
                db,
                self.backend,
                "SELECT * FROM managed_projects WHERE id=?",
                (project_id,),
            ).fetchone()
        return dict(row)

    def _usage(self, runs: list[dict]) -> dict:
        usage = {
            **{key:0 for key in USAGE_KEYS},
            "runs":0,
            "agents":{},
        }
        for run in runs:
            try:
                workflow = self.workflows.get(str(run["workflow_id"]))
            except KeyError:
                continue
            for task in workflow.get("tasks", []):
                item = _usage_from_result(task.get("result"))
                for key in USAGE_KEYS:
                    value = item.get(key)
                    if isinstance(value, int) and not isinstance(value, bool):
                        usage[key] += max(0, value)
                if (
                    isinstance(item.get("runs"), int)
                    and not isinstance(item.get("runs"), bool)
                ):
                    usage["runs"] += max(0, item["runs"])
                for name, count in dict(item.get("agents") or {}).items():
                    usage["agents"][name] = (
                        int(usage["agents"].get(name, 0)) + count
                    )
        return usage

    def get(self, identifier: str) -> dict:
        project = self.reconcile(identifier)
        project_id = str(project["id"])
        with self.backend.connect() as db:
            run_rows = _execute(
                db,
                self.backend,
                """SELECT * FROM managed_project_runs
                   WHERE project_id=?
                   ORDER BY generation ASC""",
                (project_id,),
            ).fetchall()
        runs = [dict(row) for row in run_rows]
        current_workflow = None
        if project.get("current_workflow_id"):
            try:
                current_workflow = self.workflows.get(
                    str(project["current_workflow_id"])
                )
            except KeyError:
                current_workflow = None
        usage = self._usage(runs)
        return {
            "id":project_id,
            "project_id":project_id,
            "workflow_id":project.get("current_workflow_id"),
            "current_workflow_id":project.get("current_workflow_id"),
            "repository":project["repository"],
            "final_goal":project["final_goal"],
            "token_budget":int(project["token_budget"]),
            "agent_preference":project["agent_preference"],
            "state":project["status"],
            "status":project["status"],
            "generation":int(project["generation"]),
            "usage":usage,
            "approved_by":project.get("completed_by"),
            "approved_at":project.get("completed_at"),
            "created_by":project.get("created_by"),
            "created_at":project.get("created_at"),
            "updated_at":project.get("updated_at"),
            "reviewed_at":project.get("reviewed_at"),
            "completed_at":project.get("completed_at"),
            "runs":runs,
            "current_workflow":current_workflow,
        }

    def list(self, *, limit: int = 100) -> list[dict]:
        bounded = max(1, min(500, int(limit)))
        with self.backend.connect() as db:
            rows = _execute(
                db,
                self.backend,
                """SELECT id FROM managed_projects
                   ORDER BY updated_at DESC, id DESC
                   LIMIT ?""",
                (bounded,),
            ).fetchall()

            legacy_rows = _execute(
                db,
                self.backend,
                """SELECT id FROM workflows
                   WHERE metadata_json LIKE ?
                   ORDER BY created_at DESC""",
                (f'%"{LEGACY_MANAGED_PROJECT_SCHEMA}"%',),
            ).fetchall()

        for row in legacy_rows:
            try:
                self._migrate_legacy_workflow(str(row["id"]))
            except Exception:
                continue

        with self.backend.connect() as db:
            rows = _execute(
                db,
                self.backend,
                """SELECT id FROM managed_projects
                   ORDER BY updated_at DESC, id DESC
                   LIMIT ?""",
                (bounded,),
            ).fetchall()
        return [self.get(str(row["id"])) for row in rows]

    def _follow_up(
        self,
        identifier: str,
        *,
        instruction: str,
        kind: str,
        requested_by: str,
    ) -> dict:
        current = self.get(identifier)
        if current["state"] not in {REVIEW_REQUIRED, NEEDS_ATTENTION}:
            raise RuntimeError(
                "managed project must require review or attention before follow-up"
            )
        instruction = str(instruction or "").strip()
        if not instruction:
            raise ValueError("instruction is required")

        project_id = current["project_id"]
        generation = int(current["generation"]) + 1
        workflow = self._create_workflow(
            project_id=project_id,
            repository=current["repository"],
            final_goal=current["final_goal"],
            instruction=instruction,
            generation=generation,
            kind=kind,
            token_budget=current["token_budget"],
            agent_preference=current["agent_preference"],
            dispatch=False,
        )
        now = _now()
        actor = str(requested_by or "operator").strip() or "operator"
        try:
            with self.backend.transaction() as db:
                row = _execute(
                    db,
                    self.backend,
                    """SELECT status,generation FROM managed_projects
                       WHERE id=?""",
                    (project_id,),
                ).fetchone()
                if (
                    row is None
                    or row["status"] not in {
                        REVIEW_REQUIRED,
                        NEEDS_ATTENTION,
                    }
                    or int(row["generation"]) != generation - 1
                ):
                    raise RuntimeError(
                        "managed project generation changed"
                    )
                updated = _execute(
                    db,
                    self.backend,
                    """UPDATE managed_projects
                       SET status='ACTIVE', current_workflow_id=?,
                           generation=?, updated_at=?, reviewed_at=NULL
                       WHERE id=? AND generation=?
                         AND status IN ('REVIEW_REQUIRED','NEEDS_ATTENTION')""",
                    (
                        workflow["id"],
                        generation,
                        now,
                        project_id,
                        generation - 1,
                    ),
                )
                if updated.rowcount != 1:
                    raise RuntimeError(
                        "managed project generation changed"
                    )
                _execute(
                    db,
                    self.backend,
                    """INSERT INTO managed_project_runs(
                        id, project_id, generation, kind, instruction,
                        workflow_id, requested_by, created_at
                    ) VALUES(?,?,?,?,?,?,?,?)""",
                    (
                        uuid4().hex,
                        project_id,
                        generation,
                        kind,
                        instruction,
                        workflow["id"],
                        actor,
                        now,
                    ),
                )
        except Exception:
            self._delete_unstarted_workflow(workflow["id"])
            raise

        self.workflows.dispatch_ready(workflow["id"], limit=1)
        return self.get(project_id)

    def add_instruction(
        self,
        identifier: str,
        instruction: str,
        *,
        requested_by: str = "operator",
    ) -> dict:
        return self._follow_up(
            identifier,
            instruction=instruction,
            kind="instruction",
            requested_by=requested_by,
        )

    def request_verification(
        self,
        identifier: str,
        *,
        requested_by: str = "operator",
    ) -> dict:
        current = self.get(identifier)
        instruction = (
            "Review and retest the repository against the managed project's "
            "final goal. Fix issues found and report validation evidence. "
            f"Final goal: {current['final_goal']}"
        )
        return self._follow_up(
            identifier,
            instruction=instruction,
            kind="retest",
            requested_by=requested_by,
        )

    def mark_done(
        self,
        identifier: str,
        *,
        approved_by: str,
    ) -> dict:
        current = self.get(identifier)
        if current["state"] != REVIEW_REQUIRED:
            raise RuntimeError(
                "managed project must be REVIEW_REQUIRED before DONE"
            )
        now = _now()
        actor = str(approved_by or "operator").strip() or "operator"
        with self.backend.transaction() as db:
            updated = _execute(
                db,
                self.backend,
                """UPDATE managed_projects
                   SET status='DONE', updated_at=?,
                       completed_at=?, completed_by=?
                   WHERE id=? AND status='REVIEW_REQUIRED'""",
                (now, now, actor, current["project_id"]),
            )
            if updated.rowcount != 1:
                raise RuntimeError(
                    "managed project state changed before completion"
                )
            self.backend.append_event(
                db,
                "managed-project-completed",
                {
                    "project_id":current["project_id"],
                    "requested_by":actor,
                },
                repository=current["repository"],
            )
        return self.get(current["project_id"])
