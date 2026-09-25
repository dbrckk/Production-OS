from __future__ import annotations

from datetime import datetime, timezone

from .workflow_engine import WorkflowEngine, WorkflowTaskSpec, _execute


MANAGED_PROJECT_SCHEMA = "production-os/managed-project/v2"
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
            if not isinstance(name, str) or not name.strip() or isinstance(count, bool):
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

    def create(
        self,
        *,
        repository: str,
        final_goal: str,
        token_budget: int,
        agent_preference: str = "auto",
    ) -> dict:
        repository = str(repository or "").strip()
        final_goal = str(final_goal or "").strip()
        agent_preference = str(agent_preference or "auto").strip() or "auto"
        if not repository:
            raise ValueError("repository is required")
        if not final_goal:
            raise ValueError("final_goal is required")
        budget = _positive_int(token_budget, field="token_budget")
        workflow = self.workflows.create(
            name=f"Managed project: {repository}",
            repository=repository,
            metadata={
                "managed_project":{
                    "schema_version":MANAGED_PROJECT_SCHEMA,
                    "final_goal":final_goal,
                    "token_budget":budget,
                    "agent_preference":agent_preference,
                    "human_state":"active",
                }
            },
            tasks=[
                WorkflowTaskSpec(
                    task_id="goal",
                    title=final_goal,
                    payload={
                        "handoff":{
                            "repository":repository,
                            "task":final_goal,
                            "final_goal":final_goal,
                            "agent_preference":agent_preference,
                            "token_budget":budget,
                        }
                    },
                    max_attempts=3,
                )
            ],
        )
        self.workflows.dispatch_ready(workflow["id"])
        return self.get(workflow["id"])

    def list(self) -> list[dict]:
        with self.workflows.backend.connect() as db:
            rows = _execute(
                db,
                self.workflows.backend,
                "SELECT id FROM workflows ORDER BY created_at DESC, id DESC",
            ).fetchall()
        projects = []
        for row in rows:
            project = self._project(self.workflows.get(str(row["id"])))
            if project is not None:
                projects.append(project)
        return projects

    def get(self, workflow_id: str) -> dict:
        project = self._project(self.workflows.get(str(workflow_id)))
        if project is None:
            raise KeyError(workflow_id)
        return project

    @staticmethod
    def _next_task_id(workflow: dict, prefix: str) -> str:
        known = {str(task.get("task_id") or "") for task in workflow.get("tasks", [])}
        index = 1
        while f"{prefix}-{index}" in known:
            index += 1
        return f"{prefix}-{index}"

    def _resume(
        self,
        workflow_id: str,
        *,
        prefix: str,
        title: str,
        payload: dict,
    ) -> dict:
        current = self.get(workflow_id)
        if current["state"] != "REVIEW_REQUIRED":
            raise RuntimeError(
                "managed project must be REVIEW_REQUIRED before follow-up work"
            )
        workflow = self.workflows.get(workflow_id)
        task_id = self._next_task_id(workflow, prefix)
        dependencies = tuple(str(task["task_id"]) for task in workflow["tasks"])
        self.workflows.add_task(
            workflow_id,
            WorkflowTaskSpec(
                task_id=task_id,
                title=title,
                payload=payload,
                dependencies=dependencies,
                max_attempts=3,
            ),
        )
        self.workflows.dispatch_ready(workflow_id, task_id=task_id)
        return self.get(workflow_id)

    def add_instruction(self, workflow_id: str, instruction: str) -> dict:
        instruction = str(instruction or "").strip()
        if not instruction:
            raise ValueError("instruction is required")
        current = self.get(workflow_id)
        return self._resume(
            workflow_id,
            prefix="instruction",
            title=instruction,
            payload={
                "handoff":{
                    "repository":current["repository"],
                    "task":instruction,
                    "final_goal":current["final_goal"],
                    "agent_preference":current["agent_preference"],
                    "token_budget":current["token_budget"],
                }
            },
        )

    def request_verification(self, workflow_id: str) -> dict:
        current = self.get(workflow_id)
        instruction = (
            "Verify the repository against the final goal. "
            "Run relevant tests, lint and build checks, then report concrete evidence."
        )
        return self._resume(
            workflow_id,
            prefix="verification",
            title="Retest final goal",
            payload={
                "phase":"verification",
                "handoff":{
                    "repository":current["repository"],
                    "task":instruction,
                    "final_goal":current["final_goal"],
                    "agent_preference":current["agent_preference"],
                    "token_budget":current["token_budget"],
                },
            },
        )

    def mark_done(self, workflow_id: str, *, approved_by: str) -> dict:
        current = self.get(workflow_id)
        if current["state"] != "REVIEW_REQUIRED":
            raise RuntimeError(
                "managed project must be REVIEW_REQUIRED before DONE"
            )
        workflow = self.workflows.get(workflow_id)
        metadata = dict(workflow.get("metadata") or {})
        managed = dict(metadata.get("managed_project") or {})
        managed.update({
            "human_state":"done",
            "approved_by":str(approved_by or "").strip() or "operator",
            "approved_at":_now(),
        })
        metadata["managed_project"] = managed
        self.workflows.update_metadata(workflow_id, metadata)
        return self.get(workflow_id)

    def _project(self, workflow: dict) -> dict | None:
        metadata = dict(workflow.get("metadata") or {})
        managed = metadata.get("managed_project")
        if not isinstance(managed, dict):
            return None
        if managed.get("schema_version") != MANAGED_PROJECT_SCHEMA:
            return None

        usage = {
            **{key:0 for key in USAGE_KEYS},
            "runs":0,
            "agents":{},
        }
        for task in workflow.get("tasks", []):
            item = _usage_from_result(task.get("result"))
            for key in USAGE_KEYS:
                value = item.get(key)
                if isinstance(value, int) and not isinstance(value, bool):
                    usage[key] += max(0, value)
            if isinstance(item.get("runs"), int) and not isinstance(item.get("runs"), bool):
                usage["runs"] += max(0, item["runs"])
            for name, count in dict(item.get("agents") or {}).items():
                usage["agents"][name] = int(usage["agents"].get(name, 0)) + count

        human_state = str(managed.get("human_state") or "active")
        task_states = {str(task.get("status") or "") for task in workflow.get("tasks", [])}
        if human_state == "done":
            state = "DONE"
        elif workflow.get("status") == "succeeded":
            state = "REVIEW_REQUIRED"
        elif workflow.get("status") == "failed":
            state = "FAILED"
        elif "blocked" in task_states:
            state = "BLOCKED"
        elif workflow.get("status") == "cancelled":
            state = "PAUSED"
        else:
            state = "RUNNING"

        return {
            "workflow_id":workflow["id"],
            "repository":workflow["repository"],
            "final_goal":str(managed.get("final_goal") or ""),
            "token_budget":int(managed.get("token_budget") or 0),
            "agent_preference":str(managed.get("agent_preference") or "auto"),
            "state":state,
            "workflow_status":workflow.get("status"),
            "usage":usage,
            "approved_by":managed.get("approved_by"),
            "approved_at":managed.get("approved_at"),
            "created_at":workflow.get("created_at"),
            "updated_at":workflow.get("updated_at"),
        }
