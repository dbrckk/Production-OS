from __future__ import annotations

from datetime import datetime, timezone


class PortfolioOptimizer:
    def __init__(self, workflow_engine, execution_optimizer):
        self.workflows = workflow_engine
        self.execution = execution_optimizer

    @staticmethod
    def _descendant_counts(workflow: dict) -> dict[str, int]:
        children: dict[str, set[str]] = {
            task["task_id"]:set()
            for task in workflow["tasks"]
        }
        for task in workflow["tasks"]:
            for dependency in task["dependencies"]:
                children.setdefault(dependency, set()).add(
                    task["task_id"]
                )

        memo: dict[str, set[str]] = {}

        def descendants(task_id: str) -> set[str]:
            if task_id in memo:
                return memo[task_id]
            result: set[str] = set()
            for child in children.get(task_id, set()):
                result.add(child)
                result.update(descendants(child))
            memo[task_id] = result
            return result

        return {
            task_id:len(descendants(task_id))
            for task_id in children
        }

    def rank(self, jobs: list[dict]) -> list[dict]:
        now = datetime.now(timezone.utc)
        workflow_cache: dict[str, dict] = {}
        critical_cache: dict[str, set[str]] = {}
        descendants_cache: dict[str, dict[str, int]] = {}
        ranked: list[dict] = []

        for job in jobs:
            payload = job.get("payload", {})
            workflow_id = payload.get("workflow_id")
            workflow_task_id = payload.get("workflow_task_id")

            critical = False
            descendant_count = 0
            if workflow_id and workflow_task_id:
                workflow_id = str(workflow_id)
                if workflow_id not in workflow_cache:
                    workflow = self.workflows.get(workflow_id)
                    workflow_cache[workflow_id] = workflow
                    eta = self.execution.workflow_eta(workflow)
                    critical_cache[workflow_id] = set(
                        eta["critical_task_ids"]
                    )
                    descendants_cache[workflow_id] = (
                        self._descendant_counts(workflow)
                    )
                critical = str(workflow_task_id) in critical_cache[
                    workflow_id
                ]
                descendant_count = descendants_cache[
                    workflow_id
                ].get(str(workflow_task_id), 0)

            prediction = self.execution.task_prediction(
                str(job["repository"]),
                str(job["task"]),
                fallback_minutes=float(
                    payload.get("handoff", {}).get(
                        "estimated_minutes",
                        1.0,
                    )
                ),
            )

            created_at = datetime.fromisoformat(
                str(job["created_at"]).replace("Z", "+00:00")
            )
            age_minutes = max(
                0.0,
                (now - created_at).total_seconds() / 60.0,
            )
            predicted_minutes = float(
                prediction["predicted_minutes"]
            )

            score = (
                float(job.get("priority", 0.0))
                + (40.0 if critical else 0.0)
                + (8.0 * descendant_count)
                + min(20.0, age_minutes * 0.25)
                - min(20.0, predicted_minutes * 0.25)
            )

            ranked.append({
                "job":job,
                "score":round(score, 4),
                "critical":critical,
                "descendants":descendant_count,
                "predicted_minutes":predicted_minutes,
                "age_minutes":round(age_minutes, 3),
            })

        return sorted(
            ranked,
            key=lambda item: (
                -item["score"],
                str(item["job"]["created_at"]),
                str(item["job"]["key"]),
            ),
        )
