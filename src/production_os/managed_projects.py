from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4

from .dashboard_store import _execute
from .workflow_engine import WorkflowTaskSpec


ACTIVE = "ACTIVE"
REVIEW_REQUIRED = "REVIEW_REQUIRED"
NEEDS_ATTENTION = "NEEDS_ATTENTION"
DONE = "DONE"
PROJECT_STATES = {ACTIVE, REVIEW_REQUIRED, NEEDS_ATTENTION, DONE}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class ManagedProjectError(RuntimeError):
    pass


@dataclass(frozen=True)
class ManagedProjectSpec:
    repository: str
    final_goal: str


class ManagedProjects:
    def __init__(self, backend, workflows):
        self.backend = backend
        self.workflows = workflows

    def _row(self, row) -> dict:
        return dict(row)

    def _task_spec(
        self,
        *,
        repository: str,
        final_goal: str,
        instruction: str,
        project_id: str,
        generation: int,
        kind: str,
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
                    "agent_preference":"codex",
                    "token_budget":30000,
                },
            },
            priority=100,
            max_attempts=2,
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
    ) -> dict:
        workflow = self.workflows.create(
            name=f"Managed project: {repository} · g{generation}",
            repository=repository,
            tasks=[
                self._task_spec(
                    repository=repository,
                    final_goal=final_goal,
                    instruction=instruction,
                    project_id=project_id,
                    generation=generation,
                    kind=kind,
                )
            ],
            metadata={
                "managed_project_id":project_id,
                "managed_project_generation":generation,
                "managed_project_kind":kind,
                "final_goal":final_goal,
            },
        )
        self.workflows.dispatch_ready(workflow["id"], limit=1)
        return self.workflows.get(workflow["id"])

    def create(
        self,
        *,
        repository: str,
        final_goal: str,
        requested_by: str,
    ) -> dict:
        repository = str(repository or "").strip()
        final_goal = str(final_goal or "").strip()
        if not repository or "/" not in repository:
            raise ManagedProjectError("repository must be owner/name")
        if not final_goal:
            raise ManagedProjectError("final_goal required")
        project_id = uuid4().hex
        now = _now()
        with self.backend.transaction() as db:
            _execute(
                db,
                self.backend,
                """INSERT INTO managed_projects(
                    id, repository, final_goal, status,
                    current_workflow_id, generation, created_by,
                    created_at, updated_at, reviewed_at, completed_at
                ) VALUES(?,?,?,'ACTIVE',NULL,1,?,?,?,NULL,NULL)""",
                (
                    project_id,
                    repository,
                    final_goal,
                    requested_by,
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
        run_id = uuid4().hex
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
                    run_id,
                    project_id,
                    1,
                    "initial",
                    final_goal,
                    workflow["id"],
                    requested_by,
                    now,
                ),
            )
        return self.get(project_id)

    def _get_raw(self, project_id: str) -> dict:
        with self.backend.connect() as db:
            row = _execute(
                db,
                self.backend,
                "SELECT * FROM managed_projects WHERE id=?",
                (project_id,),
            ).fetchone()
        if row is None:
            raise KeyError(project_id)
        return self._row(row)

    def reconcile(self, project_id: str) -> dict:
        project = self._get_raw(project_id)
        if project["status"] == DONE:
            return project
        workflow_id = project.get("current_workflow_id")
        if not workflow_id:
            target = NEEDS_ATTENTION
        else:
            try:
                workflow = self.workflows.refresh(str(workflow_id))
            except KeyError:
                target = NEEDS_ATTENTION
            else:
                status = workflow["status"]
                if status == "succeeded":
                    target = REVIEW_REQUIRED
                elif status in {"failed", "cancelled"}:
                    target = NEEDS_ATTENTION
                else:
                    target = ACTIVE
        if target == project["status"]:
            return project
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
        return self._get_raw(project_id)

    def get(self, project_id: str) -> dict:
        project = self.reconcile(project_id)
        with self.backend.connect() as db:
            runs = _execute(
                db,
                self.backend,
                """SELECT * FROM managed_project_runs
                   WHERE project_id=?
                   ORDER BY generation ASC""",
                (project_id,),
            ).fetchall()
        current = None
        if project.get("current_workflow_id"):
            try:
                current = self.workflows.get(project["current_workflow_id"])
            except KeyError:
                current = None
        return {
            **project,
            "runs":[self._row(row) for row in runs],
            "current_workflow":current,
        }

    def list(self, *, limit: int = 100) -> list[dict]:
        bounded = max(1, min(500, int(limit)))
        with self.backend.connect() as db:
            rows = _execute(
                db,
                self.backend,
                """SELECT id FROM managed_projects
                   ORDER BY updated_at DESC
                   LIMIT ?""",
                (bounded,),
            ).fetchall()
        return [self.get(str(row["id"])) for row in rows]

    def _follow_up(
        self,
        project_id: str,
        *,
        instruction: str,
        kind: str,
        requested_by: str,
    ) -> dict:
        project = self.reconcile(project_id)
        if project["status"] not in {REVIEW_REQUIRED, NEEDS_ATTENTION}:
            raise ManagedProjectError(
                "project must require review or attention before follow-up"
            )
        instruction = str(instruction or "").strip()
        if not instruction:
            raise ManagedProjectError("instruction required")
        generation = int(project["generation"]) + 1
        workflow = self._create_workflow(
            project_id=project_id,
            repository=project["repository"],
            final_goal=project["final_goal"],
            instruction=instruction,
            generation=generation,
            kind=kind,
        )
        now = _now()
        with self.backend.transaction() as db:
            current = _execute(
                db,
                self.backend,
                "SELECT status,generation FROM managed_projects WHERE id=?",
                (project_id,),
            ).fetchone()
            if (
                current is None
                or current["status"] not in {
                    REVIEW_REQUIRED,
                    NEEDS_ATTENTION,
                }
                or int(current["generation"]) != generation - 1
            ):
                raise ManagedProjectError("managed project generation changed")
            _execute(
                db,
                self.backend,
                """UPDATE managed_projects
                   SET status='ACTIVE', current_workflow_id=?,
                       generation=?, updated_at=?, reviewed_at=NULL
                   WHERE id=?""",
                (workflow["id"], generation, now, project_id),
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
                    requested_by,
                    now,
                ),
            )
        return self.get(project_id)

    def add_instruction(
        self,
        project_id: str,
        *,
        instruction: str,
        requested_by: str,
    ) -> dict:
        return self._follow_up(
            project_id,
            instruction=instruction,
            kind="instruction",
            requested_by=requested_by,
        )

    def retest(self, project_id: str, *, requested_by: str) -> dict:
        project = self.reconcile(project_id)
        instruction = (
            "Review and retest the repository against the managed project's "
            f"final goal. Fix any issues found and produce validation evidence. "
            f"Final goal: {project['final_goal']}"
        )
        return self._follow_up(
            project_id,
            instruction=instruction,
            kind="retest",
            requested_by=requested_by,
        )

    def complete(self, project_id: str, *, requested_by: str) -> dict:
        project = self.reconcile(project_id)
        if project["status"] != REVIEW_REQUIRED:
            raise ManagedProjectError(
                "project must be in REVIEW_REQUIRED before completion"
            )
        now = _now()
        with self.backend.transaction() as db:
            _execute(
                db,
                self.backend,
                """UPDATE managed_projects
                   SET status='DONE', updated_at=?, completed_at=?
                   WHERE id=? AND status='REVIEW_REQUIRED'""",
                (now, now, project_id),
            )
            self.backend.append_event(
                db,
                "managed-project-completed",
                {
                    "project_id":project_id,
                    "requested_by":requested_by,
                },
                repository=project["repository"],
            )
        return self.get(project_id)
