from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any


PLAN_SCHEMA = "production-os/dynamic-agent-plan/v1"
_TASK_ID = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
_CAPABILITY = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")


@dataclass(frozen=True, slots=True)
class PlannedAgentTask:
    task_id: str
    title: str
    instruction: str
    token_budget: int
    preferred_capabilities: tuple[str, ...]
    dependencies: tuple[str, ...]
    estimated_minutes: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id":self.task_id,
            "title":self.title,
            "instruction":self.instruction,
            "token_budget":self.token_budget,
            "preferred_capabilities":list(self.preferred_capabilities),
            "dependencies":list(self.dependencies),
            "estimated_minutes":self.estimated_minutes,
        }


def validate_agent_plan(
    payload: dict[str, Any],
    *,
    available_token_budget: int,
    max_agents: int = 6,
) -> list[PlannedAgentTask]:
    if not isinstance(payload, dict):
        raise ValueError("agent plan must be an object")
    if str(payload.get("schema_version") or "") != PLAN_SCHEMA:
        raise ValueError("unsupported agent plan schema")
    if int(available_token_budget) < 1:
        raise ValueError("available_token_budget must be >= 1")
    if not 1 <= int(max_agents) <= 16:
        raise ValueError("max_agents must be between 1 and 16")

    raw_tasks = payload.get("tasks")
    if not isinstance(raw_tasks, list) or not raw_tasks:
        raise ValueError("agent plan requires tasks")
    if len(raw_tasks) > int(max_agents):
        raise ValueError("agent plan exceeds max_agents")

    normalized: list[PlannedAgentTask] = []
    seen: set[str] = set()
    total_budget = 0
    for index, raw in enumerate(raw_tasks):
        if not isinstance(raw, dict):
            raise ValueError(f"agent task {index + 1} must be an object")
        task_id = str(raw.get("task_id") or "").strip().lower()
        if _TASK_ID.fullmatch(task_id) is None:
            raise ValueError(f"invalid agent task_id: {task_id!r}")
        if task_id in seen:
            raise ValueError(f"duplicate agent task_id: {task_id}")

        title = str(raw.get("title") or "").strip()
        instruction = str(raw.get("instruction") or "").strip()
        if not title or len(title) > 200:
            raise ValueError(f"agent task {task_id} has invalid title")
        if not instruction or len(instruction) > 8000:
            raise ValueError(f"agent task {task_id} has invalid instruction")

        raw_token_budget = raw.get("token_budget")
        if isinstance(raw_token_budget, bool) or not isinstance(
            raw_token_budget,
            int,
        ):
            raise ValueError(
                f"agent task {task_id} has invalid token_budget"
            )
        token_budget = raw_token_budget
        if token_budget < 1:
            raise ValueError(f"agent task {task_id} token_budget must be >= 1")
        total_budget += token_budget
        if total_budget > int(available_token_budget):
            raise ValueError("agent plan exceeds available token budget")

        raw_capabilities = raw.get("preferred_capabilities")
        if raw_capabilities is None:
            raw_capabilities = []
        if not isinstance(raw_capabilities, list):
            raise ValueError(
                f"agent task {task_id} preferred_capabilities must be a list"
            )
        capabilities: list[str] = []
        for value in raw_capabilities:
            capability = str(value or "").strip().lower()
            if _CAPABILITY.fullmatch(capability) is None:
                raise ValueError(
                    f"agent task {task_id} has invalid capability"
                )
            if capability not in capabilities:
                capabilities.append(capability)
        if len(capabilities) > 8:
            raise ValueError(
                f"agent task {task_id} has too many capabilities"
            )

        raw_dependencies = raw.get("dependencies")
        if raw_dependencies is None:
            raw_dependencies = []
        if not isinstance(raw_dependencies, list):
            raise ValueError(
                f"agent task {task_id} dependencies must be a list"
            )
        dependencies: list[str] = []
        for value in raw_dependencies:
            dependency = str(value or "").strip().lower()
            if dependency == task_id:
                raise ValueError(f"agent task {task_id} cannot depend on itself")
            if dependency not in seen:
                raise ValueError(
                    f"agent task {task_id} dependency must reference "
                    "an earlier planned task"
                )
            if dependency not in dependencies:
                dependencies.append(dependency)

        try:
            estimated_minutes = float(raw.get("estimated_minutes", 20))
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"agent task {task_id} has invalid estimated_minutes"
            ) from exc
        if not 0 < estimated_minutes <= 240:
            raise ValueError(
                f"agent task {task_id} estimated_minutes is out of bounds"
            )

        normalized.append(
            PlannedAgentTask(
                task_id=task_id,
                title=title,
                instruction=instruction,
                token_budget=token_budget,
                preferred_capabilities=tuple(capabilities),
                dependencies=tuple(dependencies),
                estimated_minutes=estimated_minutes,
            )
        )
        seen.add(task_id)

    return normalized
