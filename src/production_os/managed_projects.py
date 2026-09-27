from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from .workflow_engine import WorkflowEngine, WorkflowTaskSpec, _execute
from .github_client import GitHubAPIError, GitHubClient
from .github_work_state import fetch_github_work_state, runtime_decision_from_github


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


def _clean_commit_shas(values) -> list[str]:
    if not isinstance(values, (list, tuple)):
        return []
    clean: list[str] = []
    for raw in values:
        value = (
            str(raw.get("sha") or "").strip().lower()
            if isinstance(raw, dict)
            else str(raw or "").strip().lower()
        )
        if (
            7 <= len(value) <= 40
            and all(ch in "0123456789abcdef" for ch in value)
            and value not in clean
        ):
            clean.append(value)
    return clean[:20]


def _result_tasks_by_depth(workflow: dict) -> list[dict]:
    tasks = [
        task
        for task in workflow.get("tasks", [])
        if isinstance(task, dict) and isinstance(task.get("result"), dict)
    ]
    by_id = {
        str(task.get("task_id") or ""): task
        for task in tasks
        if str(task.get("task_id") or "")
    }
    memo: dict[str, int] = {}

    def depth(task_id: str, visiting: set[str] | None = None) -> int:
        if task_id in memo:
            return memo[task_id]
        visiting = set(visiting or ())
        if task_id in visiting:
            return 0
        visiting.add(task_id)
        task = by_id.get(task_id) or {}
        deps = [
            str(item)
            for item in (task.get("dependencies") or [])
            if str(item) in by_id
        ]
        value = 0 if not deps else 1 + max(
            depth(dep, visiting)
            for dep in deps
        )
        memo[task_id] = value
        return value

    return sorted(
        tasks,
        key=lambda task: (
            depth(str(task.get("task_id") or "")),
            str(task.get("updated_at") or ""),
            str(task.get("task_id") or ""),
        ),
    )


def _result_evidence(result: dict) -> dict:
    evidence = result.get("evidence")
    return evidence if isinstance(evidence, dict) else {}


def _outcome_from_workflow(workflow: dict | None) -> dict:
    if not isinstance(workflow, dict):
        return {
            "available":False,
            "workflow_status":None,
            "summary":None,
            "validation_status":None,
            "validation_tests":[],
            "commit_shas":[],
            "artifact_count":0,
            "artifact_names":[],
            "changed_file_count":0,
            "pull_request":None,
            "ci":None,
            "browser_validation":None,
            "completed_at":None,
        }

    result_tasks = _result_tasks_by_depth(workflow)
    results = [
        task["result"]
        for task in result_tasks
    ]
    result = results[-1] if results else {}
    evidence = _result_evidence(result)
    summary = (
        result.get("summary")
        or evidence.get("summary")
        or result.get("message")
        or evidence.get("message")
    )
    summary = str(summary).strip() if summary is not None else None
    if not summary:
        summary = None

    validation = result.get("validation")
    if not isinstance(validation, dict):
        validation = evidence.get("validation")
    if not isinstance(validation, dict):
        validation = {}
    validation_status = (
        validation.get("status")
        or result.get("validation_status")
        or evidence.get("validation_status")
    )
    validation_status = (
        str(validation_status).strip()
        if validation_status is not None
        else None
    ) or None
    raw_tests = (
        validation.get("tests")
        or result.get("tests")
        or evidence.get("tests")
    )
    validation_tests = (
        [str(item).strip() for item in raw_tests if str(item).strip()][:20]
        if isinstance(raw_tests, list)
        else []
    )

    commit_shas = []
    for item in results:
        item_evidence = _result_evidence(item)
        raw_commits = (
            item.get("commit_shas")
            or item_evidence.get("commit_shas")
            or item.get("commits")
            or item_evidence.get("commits")
            or item.get("commit_sha")
            or item_evidence.get("commit_sha")
        )
        if isinstance(raw_commits, (str, dict)):
            raw_commits = [raw_commits]
        for sha in _clean_commit_shas(raw_commits):
            if sha not in commit_shas:
                commit_shas.append(sha)
            if len(commit_shas) >= 20:
                break
        if len(commit_shas) >= 20:
            break

    artifacts = [
        artifact
        for artifact in workflow.get("artifacts", [])
        if isinstance(artifact, dict)
    ]
    artifact_names = [
        str(artifact.get("name") or "").strip()
        for artifact in artifacts
        if str(artifact.get("name") or "").strip()
    ][:20]

    changed_files = []
    for item in results:
        item_evidence = _result_evidence(item)
        raw_changed = (
            item.get("changed_files")
            or item_evidence.get("changed_files")
            or []
        )
        if not isinstance(raw_changed, (list, tuple)):
            continue
        for raw in raw_changed:
            value = str(raw or "").strip()
            if value and value not in changed_files:
                changed_files.append(value)
            if len(changed_files) >= 500:
                break
        if len(changed_files) >= 500:
            break
    changed_file_count = len(changed_files)

    pr = None
    pr_source = result
    pr_evidence = evidence
    for item in reversed(results):
        item_evidence = _result_evidence(item)
        candidate = item.get("pull_request") or item_evidence.get("pull_request")
        candidate_number = (
            item.get("pull_request_number")
            or item_evidence.get("pull_request_number")
            or item.get("pr_number")
            or item_evidence.get("pr_number")
        )
        if isinstance(candidate, dict) or candidate_number is not None:
            pr = candidate
            pr_source = item
            pr_evidence = item_evidence
            break
    pull_request = None
    if isinstance(pr, dict):
        number = pr.get("number")
        state = str(pr.get("state") or "").strip() or None
    else:
        number = (
            pr_source.get("pull_request_number")
            or pr_evidence.get("pull_request_number")
            or pr_source.get("pr_number")
            or pr_evidence.get("pr_number")
        )
        state = (
            str(
                pr_source.get("pull_request_state")
                or pr_evidence.get("pull_request_state")
                or ""
            ).strip()
            or None
        )
    try:
        number = int(number) if number is not None else None
    except (TypeError, ValueError):
        number = None
    if number is not None or state is not None:
        pull_request = {"number":number, "state":state}

    raw_ci = None
    for item in reversed(results):
        item_evidence = _result_evidence(item)
        candidate = item.get("ci") or item_evidence.get("ci")
        if isinstance(candidate, dict):
            raw_ci = candidate
            break
    ci = None
    if isinstance(raw_ci, dict):
        clean_ci = {}
        limits = {
            "provider":120,
            "status":120,
            "workflow":300,
            "job":300,
            "step":300,
            "conclusion":120,
            "url":2000,
            "sha":80,
            "log_excerpt":8000,
        }
        for key, limit in limits.items():
            value = raw_ci.get(key)
            if value is None:
                continue
            text = str(value).strip()
            if text:
                clean_ci[key] = text[:limit]
        if clean_ci:
            ci = clean_ci

    raw_browser_validation = None
    for item in reversed(results):
        item_evidence = _result_evidence(item)
        candidate = (
            item.get("browser_validation")
            or item_evidence.get("browser_validation")
        )
        if isinstance(candidate, dict):
            raw_browser_validation = candidate
            break
    browser_validation = None
    if isinstance(raw_browser_validation, dict):
        clean_browser = {}
        for key, limit in {
            "status":120,
            "reason":500,
            "runtime":120,
            "script":300,
            "url":2000,
        }.items():
            value = raw_browser_validation.get(key)
            if value is None:
                continue
            text = str(value).strip()
            if text:
                clean_browser[key] = text[:limit]
        passed = raw_browser_validation.get("passed")
        if isinstance(passed, bool):
            clean_browser["passed"] = passed
        for key, limit in {
            "console_errors":50,
            "page_errors":50,
            "screenshots":20,
            "copied_artifacts":25,
        }.items():
            value = raw_browser_validation.get(key)
            if isinstance(value, list):
                clean_browser[key] = [
                    str(item).strip()[:1000]
                    for item in value
                    if str(item).strip()
                ][:limit]
        execution = raw_browser_validation.get("execution")
        if isinstance(execution, dict):
            clean_execution = {}
            for key in (
                "returncode",
                "duration_seconds",
                "credential_isolated",
                "network_allowed",
            ):
                if execution.get(key) is not None:
                    clean_execution[key] = execution.get(key)
            log_tail = str(execution.get("log_tail") or "").strip()
            if log_tail:
                clean_execution["log_tail"] = log_tail[-4000:]
            if clean_execution:
                clean_browser["execution"] = clean_execution
        if clean_browser:
            browser_validation = clean_browser

    workflow_status = str(workflow.get("status") or "").strip() or None
    terminal = workflow_status in {"succeeded", "failed", "cancelled"}
    available = terminal or any((
        summary,
        validation_status,
        validation_tests,
        commit_shas,
        artifact_names,
        changed_file_count,
        pull_request,
        ci,
        browser_validation,
    ))
    return {
        "available":bool(available),
        "workflow_status":workflow_status,
        "summary":summary,
        "validation_status":validation_status,
        "validation_tests":validation_tests,
        "commit_shas":commit_shas,
        "artifact_count":len(artifacts),
        "artifact_names":artifact_names,
        "changed_file_count":changed_file_count,
        "pull_request":pull_request,
        "ci":ci,
        "browser_validation":browser_validation,
        "completed_at":workflow.get("updated_at") if terminal else None,
    }


class ManagedProjectService:
    def __init__(
        self,
        workflows: WorkflowEngine,
        *,
        github_client_factory=GitHubClient,
    ):
        self.workflows = workflows
        self.backend = workflows.backend
        self.github_client_factory = github_client_factory

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

    @staticmethod
    def _needs_browser_validation(final_goal: str) -> bool:
        text = str(final_goal or "").lower()
        markers = (
            "browser", "frontend", "front-end", "web ui", "website",
            "dashboard", "visual regression", "screenshot", "playwright",
            "selenium", "mobile ui", "android ui", "flutter ui",
        )
        return any(marker in text for marker in markers)

    def _cooperative_workflow_specs(
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
    ) -> list[WorkflowTaskSpec]:
        browser = self._needs_browser_validation(final_goal)
        stage_count = 4 if browser else 3
        if int(token_budget) < stage_count:
            raise ValueError(
                "cooperative token_budget must cover every stage"
            )
        implementation_budget = max(1, int(token_budget * 0.55))
        validation_budget = max(1, int(token_budget * 0.25))
        remaining = max(
            1,
            token_budget - implementation_budget - validation_budget,
        )
        review_budget = (
            max(1, int(remaining * 0.55))
            if browser
            else remaining
        )
        browser_budget = (
            max(1, remaining - review_budget)
            if browser
            else 0
        )

        common = {
            "managed_project_id":project_id,
            "managed_project_generation":generation,
            "managed_project_kind":kind,
        }
        tasks = [
            WorkflowTaskSpec(
                task_id="implementation",
                title=instruction[:120],
                payload={
                    **common,
                    "cooperative_stage":"implementation",
                    "handoff":{
                        "repository":repository,
                        "task":instruction,
                        "final_goal":final_goal,
                        "agent_preference":agent_preference,
                        "token_budget":implementation_budget,
                        "required_capabilities":[],
                        "preferred_capabilities":["code-implementation"],
                    },
                },
                priority=100,
                max_attempts=3,
                estimated_minutes=30,
            ),
            WorkflowTaskSpec(
                task_id="validation",
                title="Validate and debug the implementation",
                payload={
                    **common,
                    "cooperative_stage":"validation",
                    "handoff":{
                        "repository":repository,
                        "task":(
                            "Validate the current implementation against the final "
                            "goal. Run the most relevant tests, diagnose failures, "
                            "make the smallest correct fixes when needed, and report "
                            "clear validation evidence."
                        ),
                        "final_goal":final_goal,
                        "agent_preference":agent_preference,
                        "token_budget":validation_budget,
                        "required_capabilities":[],
                        "preferred_capabilities":["test-debug"],
                    },
                },
                dependencies=("implementation",),
                priority=100,
                max_attempts=2,
                estimated_minutes=20,
            ),
            WorkflowTaskSpec(
                task_id="review",
                title="Review the verified implementation",
                payload={
                    **common,
                    "cooperative_stage":"review",
                    "handoff":{
                        "repository":repository,
                        "task":(
                            "Review the implementation and its validation evidence. "
                            "Inspect the diff for correctness, regressions, security, "
                            "maintainability and unnecessary changes. Fix only issues "
                            "that are clearly actionable, then report review evidence."
                        ),
                        "final_goal":final_goal,
                        "agent_preference":agent_preference,
                        "token_budget":review_budget,
                        "required_capabilities":[],
                        "preferred_capabilities":["code-review"],
                    },
                },
                dependencies=("validation",),
                priority=100,
                max_attempts=2,
                estimated_minutes=15,
            ),
        ]
        if browser:
            tasks.append(
                WorkflowTaskSpec(
                    task_id="ui-validation",
                    title="Validate the user interface in a real browser/runtime",
                    payload={
                        **common,
                        "cooperative_stage":"ui-validation",
                        "handoff":{
                            "repository":repository,
                            "task":(
                                "Validate the relevant user interface in a real "
                                "Chromium browser using Python Playwright. Create or "
                                "update .production-os/browser_validate.py as the "
                                "validation entrypoint. It must exercise the changed "
                                "user flows, capture console and page errors, save at "
                                "least one screenshot under "
                                ".production-os/browser-artifacts/, and write "
                                ".production-os/browser-artifacts/report.json using "
                                "the required browser validation report schema. Fix "
                                "only defects caused by this implementation."
                            ),
                            "final_goal":final_goal,
                            "agent_preference":agent_preference,
                            "token_budget":browser_budget,
                            "required_capabilities":["browser-ui-validation"],
                            "preferred_capabilities":["browser-ui-validation"],
                            "tool_contracts":{
                                "browser_validation":{
                                    "schema":"production-os/browser-validation/v1",
                                    "report_schema":"production-os/browser-validation-report/v1",
                                    "script":".production-os/browser_validate.py",
                                    "artifacts_dir":".production-os/browser-artifacts",
                                    "runtime":"python-playwright-chromium",
                                },
                            },
                        },
                    },
                    dependencies=("review",),
                    priority=100,
                    max_attempts=2,
                    estimated_minutes=15,
                )
            )
        return tasks

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
        cooperative: bool = False,
    ) -> dict:
        tasks = (
            self._cooperative_workflow_specs(
                project_id=project_id,
                repository=repository,
                final_goal=final_goal,
                instruction=instruction,
                generation=generation,
                kind=kind,
                token_budget=token_budget,
                agent_preference=agent_preference,
            )
            if cooperative
            else [
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
            ]
        )
        workflow = self.workflows.create(
            name=f"Managed project: {repository} · g{generation}",
            repository=repository,
            tasks=tasks,
            metadata={
                "managed_project_id":project_id,
                "managed_project_generation":generation,
                "managed_project_kind":kind,
                "managed_project_schema":MANAGED_PROJECT_SCHEMA,
                "final_goal":final_goal,
                "token_budget":token_budget,
                "agent_preference":agent_preference,
                "cooperative":bool(cooperative),
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
        project_id: str | None = None,
        cooperative: bool = False,
    ) -> dict:
        repository = self._validate_repository(repository)
        final_goal = str(final_goal or "").strip()
        if not final_goal:
            raise ValueError("final_goal is required")
        budget = _positive_int(token_budget, field="token_budget")
        agent = str(agent_preference or "auto").strip() or "auto"
        actor = str(requested_by or "operator").strip() or "operator"
        if project_id is None:
            project_id = uuid4().hex
        else:
            project_id = str(project_id or "").strip()
            if (
                not (8 <= len(project_id) <= 64)
                or any(
                    not (char.isalnum() or char in {"-", "_"})
                    for char in project_id
                )
            ):
                raise ValueError("project_id is invalid")
        now = _now()

        with self.backend.transaction() as db:
            inserted = _execute(
                db,
                self.backend,
                """INSERT INTO managed_projects(
                    id, repository, final_goal, token_budget,
                    agent_preference, status, current_workflow_id,
                    generation, created_by, created_at, updated_at,
                    reviewed_at, completed_at, completed_by
                ) VALUES(?,?,?,?,?,'ACTIVE',NULL,1,?,?,?,NULL,NULL,NULL)
                ON CONFLICT(id) DO NOTHING""",
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
            created_row = inserted.rowcount == 1
            if not created_row:
                existing = _execute(
                    db,
                    self.backend,
                    """SELECT repository, final_goal, token_budget,
                              agent_preference, created_by,
                              current_workflow_id
                       FROM managed_projects
                       WHERE id=?""",
                    (project_id,),
                ).fetchone()
                if existing is None:
                    raise RuntimeError(
                        "idempotent managed project reservation disappeared"
                    )
                matches = (
                    str(existing["repository"]) == repository
                    and str(existing["final_goal"]) == final_goal
                    and int(existing["token_budget"]) == budget
                    and str(existing["agent_preference"]) == agent
                    and str(existing["created_by"]) == actor
                )
                if not matches:
                    raise RuntimeError(
                        "request_id already used with different launch parameters"
                    )
                if not existing["current_workflow_id"]:
                    raise RuntimeError(
                        "idempotent launch initialization is still in progress"
                    )

        if not created_row:
            return self.get(project_id)

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
                cooperative=bool(cooperative),
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

    def _github_target_for_succeeded_workflow(
        self,
        repository: str,
        workflow: dict,
    ) -> str | None:
        outcome = _outcome_from_workflow(workflow)
        pull_request = outcome.get("pull_request")
        if not isinstance(pull_request, dict):
            return None
        number = pull_request.get("number")
        try:
            pr_number = int(number)
        except (TypeError, ValueError):
            return None
        if pr_number < 1:
            return None

        try:
            state = fetch_github_work_state(
                self.github_client_factory(),
                repository,
                pr_number=pr_number,
            )
        except (GitHubAPIError, OSError, ValueError):
            return ACTIVE

        decision = runtime_decision_from_github(state)
        if decision in {"retry", "replan", "rollback"}:
            return NEEDS_ATTENTION
        if state.ready_for_promotion:
            return REVIEW_REQUIRED
        if (
            state.ci_state is None
            and state.status_state is None
            and not state.required_checks_missing
        ):
            return REVIEW_REQUIRED
        if (
            state.human_review_required
            and state.ci_state == "passed"
            and state.status_state in {None, "passed"}
        ):
            return REVIEW_REQUIRED
        if state.merged and decision == "promote":
            return REVIEW_REQUIRED
        return ACTIVE

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
                workflow = self.workflows.get(str(workflow_id))
            except KeyError:
                target = NEEDS_ATTENTION
            else:
                workflow_status = workflow.get("status")
                if workflow_status == "succeeded":
                    github_target = self._github_target_for_succeeded_workflow(
                        str(current["repository"]),
                        workflow,
                    )
                    target = (
                        github_target
                        if github_target is not None
                        else REVIEW_REQUIRED
                    )
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
        display_state = (
            "RUNNING"
            if project["status"] == ACTIVE
            else project["status"]
        )
        return {
            "id":project_id,
            "project_id":project_id,
            "workflow_id":project.get("current_workflow_id"),
            "current_workflow_id":project.get("current_workflow_id"),
            "repository":project["repository"],
            "final_goal":project["final_goal"],
            "token_budget":int(project["token_budget"]),
            "agent_preference":project["agent_preference"],
            "state":display_state,
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
            "outcome":_outcome_from_workflow(current_workflow),
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
        if current["status"] not in {REVIEW_REQUIRED, NEEDS_ATTENTION}:
            raise RuntimeError(
                "managed project must require review or attention before follow-up"
            )
        instruction = str(instruction or "").strip()
        if not instruction:
            raise ValueError("instruction is required")

        project_id = current["project_id"]
        generation = int(current["generation"]) + 1
        current_workflow = current.get("current_workflow")
        cooperative = bool(
            isinstance(current_workflow, dict)
            and isinstance(current_workflow.get("metadata"), dict)
            and current_workflow["metadata"].get("cooperative") is True
        )
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
            cooperative=cooperative,
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
        if current["status"] != REVIEW_REQUIRED:
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
