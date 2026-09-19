"""Managed autonomous projects built on top of the existing workflow engine."""
from __future__ import annotations

from datetime import datetime, timezone

from .workflow_engine import WorkflowEngine, WorkflowTaskSpec


MANAGED_PROJECT_SCHEMA = "production-os/managed-project/v1"
USAGE_KEYS = (
    "input_tokens",
    "cached_input_tokens",
    "output_tokens",
    "reasoning_tokens",
    "total_tokens",
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _clean_positive_int(value, *, field: str) -> int:
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

    normalized: dict[str, int] = {}
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
        normalized_agents = {}
        for name, raw_count in agents.items():
            if not isinstance(name, str) or not name.strip():
                continue
            if isinstance(raw_count, bool):
                continue
            try:
                count = int(raw_count)
            except (TypeError, ValueError):
                continue
            if count >= 0:
                normalized_agents[name] = count
        normalized["agents"] = normalized_agents
    return normalized


def global_token_capacity(
    projects: list[dict],
    workers: list[dict],
) -> dict:
    """Choose the best trustworthy numeric capacity for the portfolio."""
    candidates = []
    for worker in workers:
        if not isinstance(worker, dict):
            continue
        capacity = worker.get("capacity")
        if not isinstance(capacity, dict):
            continue
        if (
            capacity.get("source") != "omniroute"
            or capacity.get("status") != "ok"
            or capacity.get("authenticated_usage") is not True
        ):
            continue
        steady = capacity.get("steady_recurring_tokens")
        used = capacity.get("used_this_month")
        remaining = capacity.get("remaining_tokens")
        if (
            isinstance(steady, bool)
            or not isinstance(steady, int)
            or steady <= 0
            or isinstance(used, bool)
            or not isinstance(used, int)
            or used < 0
            or isinstance(remaining, bool)
            or not isinstance(remaining, int)
            or remaining < 0
        ):
            continue
        candidates.append((
            str(worker.get("last_heartbeat") or ""),
            str(worker.get("worker_id") or ""),
            steady,
            used,
            remaining,
        ))

    if candidates:
        _, _, steady, used, remaining = max(candidates)
        return {
            "source": "omniroute",
            "label": "OmniRoute monthly",
            "monthly_budget": steady,
            "used": used,
            "remaining": remaining,
            "authenticated_usage": True,
        }

    budget = 0
    used = 0
    for project in projects:
        if not isinstance(project, dict):
            continue
        try:
            project_budget = int(project.get("token_budget") or 0)
        except (TypeError, ValueError):
            project_budget = 0
        usage = project.get("usage")
        total = usage.get("total_tokens", 0) if isinstance(usage, dict) else 0
        try:
            project_used = int(total or 0)
        except (TypeError, ValueError):
            project_used = 0
        budget += max(0, project_budget)
        used += max(0, project_used)

    return {
        "source": "project-budgets",
        "label": "Managed project budgets",
        "monthly_budget": budget,
        "used": used,
        "remaining": max(0, budget - used),
        "authenticated_usage": False,
    }


class ManagedProjectService:
    """Project-level human review state layered over WorkflowEngine."""

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
        budget = _clean_positive_int(token_budget, field="token_budget")

        metadata = {
            "managed_project": {
                "schema_version": MANAGED_PROJECT_SCHEMA,
                "final_goal": final_goal,
                "token_budget": budget,
                "agent_preference": agent_preference,
                "human_state": "active",
            }
        }
        workflow = self.workflows.create(
            name=f"Managed project: {repository}",
            repository=repository,
            tasks=[
                WorkflowTaskSpec(
                    task_id="goal",
                    title=final_goal,
                    payload={
                        "handoff": {
                            "repository": repository,
                            "task": final_goal,
                            "final_goal": final_goal,
                            "agent_preference": agent_preference,
                            "token_budget": budget,
                        }
                    },
                    max_attempts=3,
                )
            ],
            metadata=metadata,
        )
        self.workflows.dispatch_ready(workflow["id"])
        return self.get(workflow["id"])

    def get(self, workflow_id: str) -> dict:
        workflow = self.workflows.get(str(workflow_id))
        project = self._project(workflow)
        if project is None:
            raise KeyError(workflow_id)
        return project

    def list(self) -> list[dict]:
        with self.workflows.backend.connect() as db:
            rows = db.execute(
                """
                SELECT id
                FROM workflows
                ORDER BY created_at DESC, id DESC
                """
            ).fetchall()
        projects = []
        for row in rows:
            workflow = self.workflows.get(str(row["id"]))
            project = self._project(workflow)
            if project is not None:
                projects.append(project)
        return projects

    @staticmethod
    def _next_task_id(workflow: dict, prefix: str) -> str:
        known = {str(task.get("task_id") or "") for task in workflow.get("tasks", [])}
        index = 1
        while f"{prefix}-{index}" in known:
            index += 1
        return f"{prefix}-{index}"

    def _resume_with_task(
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

        workflow = self.workflows.get(str(workflow_id))
        task_id = self._next_task_id(workflow, prefix)
        dependencies = tuple(
            str(task["task_id"])
            for task in workflow.get("tasks", [])
        )
        self.workflows.add_task(
            str(workflow_id),
            WorkflowTaskSpec(
                task_id=task_id,
                title=title,
                payload=payload,
                dependencies=dependencies,
                max_attempts=3,
            ),
        )
        self.workflows.dispatch_ready(str(workflow_id))
        return self.get(str(workflow_id))

    def add_instruction(self, workflow_id: str, instruction: str) -> dict:
        instruction = str(instruction or "").strip()
        if not instruction:
            raise ValueError("instruction is required")
        current = self.get(workflow_id)
        return self._resume_with_task(
            workflow_id,
            prefix="instruction",
            title=instruction,
            payload={
                "handoff": {
                    "repository": current["repository"],
                    "task": instruction,
                    "final_goal": current["final_goal"],
                    "agent_preference": current["agent_preference"],
                    "token_budget": current["token_budget"],
                }
            },
        )

    def request_verification(self, workflow_id: str) -> dict:
        current = self.get(workflow_id)
        instruction = (
            "Verify the repository against the final goal. "
            "Run the relevant tests, lint, build, and report concrete evidence."
        )
        return self._resume_with_task(
            workflow_id,
            prefix="verification",
            title="Retest final goal",
            payload={
                "phase": "verification",
                "handoff": {
                    "repository": current["repository"],
                    "task": instruction,
                    "final_goal": current["final_goal"],
                    "agent_preference": current["agent_preference"],
                    "token_budget": current["token_budget"],
                },
            },
        )

    def mark_done(self, workflow_id: str, *, approved_by: str) -> dict:
        current = self.get(workflow_id)
        if current["state"] != "REVIEW_REQUIRED":
            raise RuntimeError("managed project must be REVIEW_REQUIRED before DONE")

        workflow = self.workflows.get(str(workflow_id))
        metadata = dict(workflow.get("metadata") or {})
        managed = dict(metadata.get("managed_project") or {})
        managed.update({
            "human_state": "done",
            "approved_by": str(approved_by or "").strip() or "operator",
            "approved_at": _now(),
        })
        metadata["managed_project"] = managed
        self.workflows.update_metadata(str(workflow_id), metadata)
        return self.get(str(workflow_id))

    def _project(self, workflow: dict) -> dict | None:
        metadata = dict(workflow.get("metadata") or {})
        managed = metadata.get("managed_project")
        if not isinstance(managed, dict):
            return None
        if managed.get("schema_version") != MANAGED_PROJECT_SCHEMA:
            return None

        usage = {
            **{key: 0 for key in USAGE_KEYS},
            "runs": 0,
            "agents": {},
        }
        for task in workflow.get("tasks", []):
            item = _usage_from_result(task.get("result"))
            for key in USAGE_KEYS:
                value = item.get(key)
                if isinstance(value, int) and not isinstance(value, bool):
                    usage[key] += max(0, value)
            runs = item.get("runs")
            if isinstance(runs, int) and not isinstance(runs, bool):
                usage["runs"] += max(0, runs)
            agents = item.get("agents")
            if isinstance(agents, dict):
                for name, count in agents.items():
                    if (
                        isinstance(name, str)
                        and isinstance(count, int)
                        and not isinstance(count, bool)
                        and count >= 0
                    ):
                        usage["agents"][name] = (
                            int(usage["agents"].get(name, 0)) + count
                        )

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
            "workflow_id": workflow["id"],
            "repository": workflow["repository"],
            "final_goal": str(managed.get("final_goal") or ""),
            "token_budget": int(managed.get("token_budget") or 0),
            "agent_preference": str(managed.get("agent_preference") or "auto"),
            "state": state,
            "workflow_status": workflow.get("status"),
            "usage": usage,
            "approved_by": managed.get("approved_by"),
            "approved_at": managed.get("approved_at"),
            "created_at": workflow.get("created_at"),
            "updated_at": workflow.get("updated_at"),
        }
