from __future__ import annotations

from datetime import datetime, timezone
import json
import re
from urllib.parse import urlsplit
from uuid import uuid4

from .workflow_engine import WorkflowEngine, WorkflowTaskSpec, _execute
from .agent_planning_policy import planning_policy_for_repository
from .project_memory import ProjectMemoryStore
from .github_client import GitHubAPIError, GitHubClient
from .github_work_state import fetch_github_work_state, runtime_decision_from_github
from .rollback_plan import build_rollback_plan


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


def _stage_budgets(total: int, weights: list[int]) -> list[int]:
    if int(total) < len(weights):
        raise ValueError("cooperative token_budget must cover every stage")
    if not weights or any(int(weight) <= 0 for weight in weights):
        raise ValueError("stage weights must be positive")
    remaining = int(total) - len(weights)
    weight_total = sum(int(weight) for weight in weights)
    shares = [
        remaining * int(weight) / weight_total
        for weight in weights
    ]
    budgets = [1 + int(share) for share in shares]
    leftover = int(total) - sum(budgets)
    order = sorted(
        range(len(weights)),
        key=lambda index: (
            -(shares[index] - int(shares[index])),
            index,
        ),
    )
    for index in order[:leftover]:
        budgets[index] += 1
    return budgets


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


def _safe_github_review_url(value) -> str | None:
    """Only expose real GitHub compare pages; treat worker evidence as untrusted."""
    if not isinstance(value, str) or len(value) > 2048:
        return None
    try:
        parsed = urlsplit(value)
    except ValueError:
        return None
    if (
        parsed.scheme != "https"
        or parsed.netloc != "github.com"
        or parsed.fragment
        or parsed.query not in {"", "expand=1"}
        or not re.fullmatch(
            r"/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/compare/"
            r"[A-Za-z0-9_.%-]+\.\.\.[A-Za-z0-9_./%-]+",
            parsed.path,
        )
    ):
        return None
    return value


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
            "delivery_status":None,
            "release_status":None,
            "ci":None,
            "browser_validation":None,
            "mobile_validation":None,
            "dynamic_plan":None,
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
        if isinstance(pr, dict) and state == "unavailable":
            reason = str(pr.get("reason") or "").strip()
            if reason in {"pull_request_write_denied", "pull_request_unavailable"}:
                pull_request["reason"] = reason
            review_url = _safe_github_review_url(pr.get("compare_url"))
            if review_url is not None:
                pull_request["compare_url"] = review_url

    delivery_status = None
    release_status = None
    for item in reversed(results):
        item_evidence = _result_evidence(item)
        if delivery_status is None:
            candidate = item_evidence.get("delivery_status") or item.get("delivery_status")
            if candidate in {"review_blocked", "pull_request_open"}:
                delivery_status = candidate
        if release_status is None:
            candidate = item_evidence.get("release_status") or item.get("release_status")
            if candidate in {"verified_branch_review_blocked", "verified_project_complete"}:
                release_status = candidate

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

    raw_mobile_validation = None
    for item in reversed(results):
        item_evidence = _result_evidence(item)
        candidate = (
            item.get("mobile_validation")
            or item_evidence.get("mobile_validation")
        )
        if isinstance(candidate, dict):
            raw_mobile_validation = candidate
            break
    mobile_validation = None
    if isinstance(raw_mobile_validation, dict):
        clean_mobile = {}
        for key, limit in {
            "status":120,
            "reason":500,
            "runtime":120,
            "script":300,
            "package_name":240,
            "activity":500,
            "device_serial":240,
        }.items():
            value = raw_mobile_validation.get(key)
            if value is None:
                continue
            text = str(value).strip()
            if text:
                clean_mobile[key] = text[:limit]
        passed = raw_mobile_validation.get("passed")
        if isinstance(passed, bool):
            clean_mobile["passed"] = passed
        for key, limit in {
            "fatal_errors":50,
            "screenshots":20,
            "copied_artifacts":30,
        }.items():
            value = raw_mobile_validation.get(key)
            if isinstance(value, list):
                clean_mobile[key] = [
                    str(item).strip()[:1200]
                    for item in value
                    if str(item).strip()
                ][:limit]
        adb_verification = raw_mobile_validation.get("adb_verification")
        if isinstance(adb_verification, dict):
            clean_adb = {}
            for key in (
                "passed",
                "device_state_verified",
                "package_installed_verified",
                "activity_visible_verified",
            ):
                value = adb_verification.get(key)
                if isinstance(value, bool):
                    clean_adb[key] = value
            reason = str(adb_verification.get("reason") or "").strip()
            if reason:
                clean_adb["reason"] = reason[:500]
            for key, limit in {
                "device_state_log":1200,
                "package_log":1200,
                "activity_log":3000,
            }.items():
                value = str(adb_verification.get(key) or "").strip()
                if value:
                    clean_adb[key] = value[-limit:]
            if clean_adb:
                clean_mobile["adb_verification"] = clean_adb
        execution = raw_mobile_validation.get("execution")
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
                clean_mobile["execution"] = clean_execution
        if clean_mobile:
            mobile_validation = clean_mobile

    dynamic_children = [
        task
        for task in (workflow.get("tasks") or [])
        if isinstance(task, dict)
        and isinstance(task.get("payload"), dict)
        and task["payload"].get("dynamic_agent_child") is True
    ]
    dynamic_plan = None
    if dynamic_children:
        sources = {
            str(task["payload"].get("dynamic_agent_plan_source") or "").strip()
            for task in dynamic_children
            if str(
                task["payload"].get("dynamic_agent_plan_source") or ""
            ).strip()
        }
        source = (
            next(iter(sources))
            if len(sources) == 1
            else "mixed"
        )
        dynamic_plan = {
            "source":source or "unknown",
            "child_agent_count":len(dynamic_children),
            "task_ids":[
                str(task.get("task_id") or "")
                for task in dynamic_children
                if str(task.get("task_id") or "")
            ][:16],
        }

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
        mobile_validation,
        dynamic_plan,
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
        "delivery_status":delivery_status,
        "release_status":release_status,
        "ci":ci,
        "browser_validation":browser_validation,
        "mobile_validation":mobile_validation,
        "dynamic_plan":dynamic_plan,
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
        self.project_memory = ProjectMemoryStore(self.backend)

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

    def _project_memory_context(
        self,
        *,
        repository: str,
        project_id: str,
        final_goal: str,
        instruction: str,
    ) -> tuple[dict, str]:
        context = self.project_memory.context(
            repository=repository,
            project_id=project_id,
            query=f"{final_goal}\n{instruction}",
            limit=6,
        )
        return context, self.project_memory.context_text(context)

    @staticmethod
    def _needs_browser_validation(final_goal: str) -> bool:
        text = str(final_goal or "").lower()
        markers = (
            "browser", "frontend", "front-end", "web ui", "website",
            "dashboard", "visual regression", "screenshot", "playwright",
            "selenium",
        )
        return any(marker in text for marker in markers)

    @staticmethod
    def _needs_mobile_ui_validation(final_goal: str) -> bool:
        text = str(final_goal or "").lower()
        markers = (
            "android ui",
            "flutter ui",
            "mobile ui",
            "android app ui",
            "flutter app ui",
            "android interface",
            "flutter interface",
            "mobile interface",
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
        mobile = self._needs_mobile_ui_validation(final_goal)
        browser = self._needs_browser_validation(final_goal) and not mobile
        specialist = browser or mobile
        planning_policy = planning_policy_for_repository(
            self.backend,
            repository,
        )
        memory_context, memory_text = self._project_memory_context(
            repository=repository,
            project_id=project_id,
            final_goal=final_goal,
            instruction=instruction,
        )
        planner_max_agents = planning_policy.max_agents

        weights = [8, 42, 15, 15, 10, 10] if specialist else [10, 45, 15, 15, 15]
        budgets = _stage_budgets(int(token_budget), weights)
        (
            planner_budget,
            agent_budget,
            integration_budget,
            validation_budget,
            review_budget,
            *specialist_budgets,
        ) = budgets
        specialist_budget = specialist_budgets[0] if specialist_budgets else 0

        if agent_budget < 2:
            raise ValueError(
                "cooperative token_budget must reserve at least 2 tokens "
                "for fallback child agents"
            )
        code_budget = max(1, (agent_budget * 7) // 10)
        tests_budget = agent_budget - code_budget
        if tests_budget < 1:
            tests_budget = 1
            code_budget = agent_budget - 1

        common = {
            "managed_project_id":project_id,
            "managed_project_generation":generation,
            "managed_project_kind":kind,
        }
        continuation = [
            {
                "task_id":"validation",
                "title":"Validate and debug the integrated implementation",
                "instruction":(
                    "Validate the integrated implementation against the final "
                    "goal. Run the most relevant tests, diagnose failures, make "
                    "the smallest correct fixes when needed, commit fixes, and "
                    "report clear validation evidence."
                ),
                "token_budget":validation_budget,
                "preferred_capabilities":["test-debug"],
                "max_attempts":2,
                "estimated_minutes":20,
            },
            {
                "task_id":"review",
                "title":"Review the verified implementation",
                "instruction":(
                    "Review the integrated implementation and validation "
                    "evidence. Inspect correctness, regressions, security, "
                    "maintainability and unnecessary changes. Fix only clearly "
                    "actionable issues, commit any fixes, then report evidence."
                ),
                "token_budget":review_budget,
                "preferred_capabilities":["code-review"],
                "max_attempts":2,
                "estimated_minutes":15,
            },
        ]
        if browser:
            continuation.append({
                "task_id":"ui-validation",
                "title":"Validate the user interface in a real browser/runtime",
                "instruction":(
                    "Validate the relevant user interface in a real Chromium "
                    "browser using Python Playwright. Create or update "
                    ".production-os/browser_validate.py as the validation "
                    "entrypoint. Exercise changed flows, capture console/page "
                    "errors and screenshots, and write the required browser "
                    "validation report. Commit only fixes caused by this "
                    "implementation."
                ),
                "token_budget":specialist_budget,
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
                "max_attempts":2,
                "estimated_minutes":15,
            })
        if mobile:
            continuation.append({
                "task_id":"mobile-ui-validation",
                "title":"Validate the native user interface on an Android emulator",
                "instruction":(
                    "Validate the relevant native Android or Flutter user "
                    "interface on a real Android emulator using ADB. Build or "
                    "locate the debug APK, boot or reuse an emulator, exercise "
                    "the changed flow, capture screenshots and fatal/crash "
                    "evidence, and write the required mobile validation report. "
                    "Commit only fixes caused by this implementation."
                ),
                "token_budget":specialist_budget,
                "required_capabilities":["mobile-ui-validation"],
                "preferred_capabilities":["mobile-ui-validation"],
                "tool_contracts":{
                    "mobile_validation":{
                        "schema":"production-os/mobile-validation/v1",
                        "report_schema":"production-os/mobile-validation-report/v1",
                        "script":".production-os/mobile_validate.py",
                        "artifacts_dir":".production-os/mobile-artifacts",
                        "runtime":"android-adb-emulator",
                    },
                },
                "max_attempts":2,
                "estimated_minutes":20,
            })

        fallback_plan = {
            "schema_version":"production-os/dynamic-agent-plan/v1",
            "tasks":[
                {
                    "task_id":"code",
                    "title":instruction[:120] or "Implement requested change",
                    "instruction":(
                        f"{instruction}\n\n"
                        "Implement the production code in your isolated worktree. "
                        "Do not modify tests unless required to keep the repository "
                        "runnable. Commit every successful change and report commit "
                        "SHAs and changed files."
                    ),
                    "token_budget":code_budget,
                    "preferred_capabilities":["code-implementation"],
                    "estimated_minutes":30,
                },
                {
                    "task_id":"tests",
                    "title":"Design tests for the requested change",
                    "instruction":(
                        "Independently design and implement the tests needed to "
                        "prove the final goal. Work only in your isolated worktree. "
                        "Prefer tests and test support code; avoid changing product "
                        "code unless a minimal testability fix is essential. Commit "
                        "the result and report commit SHAs and changed files."
                    ),
                    "token_budget":tests_budget,
                    "preferred_capabilities":["test-debug"],
                    "estimated_minutes":20,
                },
            ],
        }

        planner_instruction = (
            "Act as the implementation planner for this repository task. "
            "Return a structured result.agent_plan using schema "
            "production-os/dynamic-agent-plan/v1. Split the work only when "
            f"parallelism is useful. Use at most {planner_max_agents} tasks. "
            "Keep dependencies "
            "acyclic by depending only on earlier tasks. Assign each task a "
            "token_budget, title, instruction, preferred_capabilities and "
            "estimated_minutes. The total child-agent token budget must not "
            f"exceed {agent_budget}. Do not modify repository files in this "
            "planning stage. "
            f"Planning guidance from durable repository evidence: "
            f"{planning_policy.guidance}\n\n"
            f"{memory_text}\n\n"
            f"Final goal: {final_goal}\n"
            f"Current instruction: {instruction}"
        )

        return [
            WorkflowTaskSpec(
                task_id="planner",
                title="Plan adaptive multi-agent implementation",
                payload={
                    **common,
                    "cooperative_stage":"planner",
                    "dynamic_agent_planner":{
                        "available_token_budget":agent_budget,
                        "max_agents":planner_max_agents,
                        "fallback_plan":fallback_plan,
                        "integration_task_id":"integration",
                        "integration_title":"Integrate dynamic agent branches",
                        "integration_instruction":(
                            "Integrate all dynamic agent results from "
                            "upstream_context into one clean branch. Use reported "
                            "commit SHAs as authoritative inputs. Resolve conflicts "
                            "conservatively, preserve each agent's intent, run "
                            "targeted checks, commit the integrated result, and "
                            "report final commit SHAs and changed files."
                        ),
                        "integration_token_budget":integration_budget,
                        "integration_capabilities":["code-implementation"],
                        "integration_max_attempts":2,
                        "integration_estimated_minutes":20,
                        "post_integration_tasks":continuation,
                        "priority":100,
                        "max_attempts":3,
                        "planning_policy":planning_policy.to_dict(),
                        "handoff":{
                            "final_goal":final_goal,
                            "agent_preference":agent_preference,
                            "planning_policy":planning_policy.to_dict(),
                            "project_memory":memory_context,
                            **common,
                        },
                    },
                    "handoff":{
                        "repository":repository,
                        "task":planner_instruction,
                        "final_goal":final_goal,
                        "agent_preference":agent_preference,
                        "planning_policy":planning_policy.to_dict(),
                        "project_memory":memory_context,
                        "token_budget":planner_budget,
                        "required_capabilities":[],
                        "preferred_capabilities":["code-implementation"],
                        "tool_contracts":{
                            "dynamic_agent_plan":{
                                "schema":"production-os/dynamic-agent-plan/v1",
                                "result_field":"agent_plan",
                                "max_agents":planner_max_agents,
                                "max_total_token_budget":agent_budget,
                            },
                        },
                    },
                },
                priority=100,
                max_attempts=2,
                estimated_minutes=10,
            ),
        ]

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
        memory_context, _memory_text = self._project_memory_context(
            repository=repository,
            project_id=project_id,
            final_goal=final_goal,
            instruction=instruction,
        )
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
                    "project_memory":memory_context,
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
            self.workflows.dispatch_ready(
                workflow["id"],
                limit=10 if cooperative else 1,
            )
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

        self.workflows.dispatch_ready(
            workflow["id"],
            limit=10 if cooperative else 1,
        )
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

    def _automerge_receipt(
        self,
        *,
        repository: str,
        project_id: str,
        workflow_id: str,
        pr_number: int,
        head_sha: str,
    ) -> dict | None:
        with self.backend.connect() as db:
            rows = _execute(
                db,
                self.backend,
                """SELECT payload_json
                   FROM events
                   WHERE event_type='managed-project-automerge'
                     AND repository=?
                   ORDER BY id DESC
                   LIMIT 50""",
                (repository,),
            ).fetchall()
        for row in rows:
            try:
                payload = json.loads(row["payload_json"])
            except (TypeError, ValueError, json.JSONDecodeError):
                continue
            if not isinstance(payload, dict):
                continue
            if (
                str(payload.get("project_id") or "") == project_id
                and str(payload.get("workflow_id") or "") == workflow_id
                and int(payload.get("pr_number") or 0) == pr_number
                and str(payload.get("head_sha") or "").lower() == head_sha
                and payload.get("merged") is True
            ):
                return payload
        return None

    def _record_automerge_receipt(
        self,
        *,
        repository: str,
        project_id: str,
        workflow_id: str,
        pr_number: int,
        head_sha: str,
        base_sha: str,
        merge_sha: str | None,
    ) -> None:
        with self.backend.transaction() as db:
            self.backend.append_event(
                db,
                "managed-project-automerge",
                {
                    "project_id":project_id,
                    "workflow_id":workflow_id,
                    "pr_number":pr_number,
                    "head_sha":head_sha,
                    "base_sha":base_sha,
                    "merge_sha":str(merge_sha or "")[:40] or None,
                    "merged":True,
                },
                repository=repository,
            )

    def _github_resolution_for_succeeded_workflow(
        self,
        repository: str,
        workflow: dict,
    ) -> dict | None:
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

        client = self.github_client_factory()
        try:
            state = fetch_github_work_state(
                client,
                repository,
                pr_number=pr_number,
            )
        except (GitHubAPIError, OSError, ValueError):
            return {"target":ACTIVE, "decision":"unavailable", "state":None}

        decision = runtime_decision_from_github(state)
        if decision == "rollback":
            rollback_plan = None
            if (
                isinstance(state.validation_sha, str)
                and len(state.validation_sha) == 40
            ):
                try:
                    known_good_sha = (
                        str(state.base_sha).strip().lower()
                        if isinstance(state.base_sha, str)
                        and len(state.base_sha) == 40
                        and str(state.base_sha).strip().lower()
                        != str(state.validation_sha).strip().lower()
                        else None
                    )
                    rollback_plan = build_rollback_plan(
                        repository=repository,
                        merge_sha=state.validation_sha,
                        failure_summary=outcome.get("summary"),
                        ci=outcome.get("ci"),
                        known_good_sha=known_good_sha,
                    )
                except ValueError:
                    rollback_plan = None
            return {
                "target":NEEDS_ATTENTION,
                "decision":"rollback",
                "state":state,
                "rollback_plan":rollback_plan,
            }
        if decision in {"retry", "replan"}:
            return {
                "target":NEEDS_ATTENTION,
                "decision":decision,
                "state":state,
            }
        if state.ready_for_promotion:
            head_sha = str(state.head_sha or "").strip().lower()
            base_sha = str(state.base_sha or "").strip().lower()
            metadata = workflow.get("metadata")
            metadata = metadata if isinstance(metadata, dict) else {}
            project_id = str(
                metadata.get("managed_project_id") or ""
            ).strip()
            workflow_id = str(workflow.get("id") or "").strip()
            if len(head_sha) != 40 or len(base_sha) != 40:
                return {
                    "target":REVIEW_REQUIRED,
                    "decision":"merge-blocked",
                    "state":state,
                    "merge":{
                        "merged":False,
                        "reason":"invalid-observed-sha",
                    },
                }

            if project_id and workflow_id:
                receipt = self._automerge_receipt(
                    repository=repository,
                    project_id=project_id,
                    workflow_id=workflow_id,
                    pr_number=pr_number,
                    head_sha=head_sha,
                )
                if isinstance(receipt, dict):
                    return {
                        "target":ACTIVE,
                        "decision":"merged-awaiting-validation",
                        "state":state,
                        "merge":{
                            "merged":True,
                            "sha":receipt.get("merge_sha"),
                            "receipt":True,
                        },
                    }

            try:
                fresh_state = fetch_github_work_state(
                    client,
                    repository,
                    pr_number=pr_number,
                )
            except (GitHubAPIError, OSError, ValueError):
                return {
                    "target":ACTIVE,
                    "decision":"promotion-recheck-unavailable",
                    "state":state,
                }

            fresh_head = str(
                fresh_state.head_sha or ""
            ).strip().lower()
            fresh_base = str(
                fresh_state.base_sha or ""
            ).strip().lower()
            if (
                fresh_head != head_sha
                or fresh_base != base_sha
            ):
                return {
                    "target":ACTIVE,
                    "decision":"promotion-state-changed",
                    "state":fresh_state,
                }
            if not fresh_state.ready_for_promotion:
                fresh_decision = runtime_decision_from_github(
                    fresh_state
                )
                if fresh_decision in {"retry", "replan"}:
                    return {
                        "target":NEEDS_ATTENTION,
                        "decision":fresh_decision,
                        "state":fresh_state,
                    }
                if (
                    fresh_state.human_review_required
                    or (
                        fresh_state.ci_state is None
                        and fresh_state.status_state is None
                        and not fresh_state.required_checks_missing
                    )
                ):
                    return {
                        "target":REVIEW_REQUIRED,
                        "decision":"promotion-recheck-blocked",
                        "state":fresh_state,
                    }
                return {
                    "target":ACTIVE,
                    "decision":"promotion-recheck-pending",
                    "state":fresh_state,
                }

            try:
                merge = client.merge_pull_request(
                    repository,
                    pr_number,
                    head_sha=fresh_head,
                    method="squash",
                    commit_title=(
                        f"Production-OS: managed project PR #{pr_number}"
                    ),
                )
            except (GitHubAPIError, OSError, ValueError) as exc:
                return {
                    "target":REVIEW_REQUIRED,
                    "decision":"merge-blocked",
                    "state":fresh_state,
                    "merge":{
                        "merged":False,
                        "reason":type(exc).__name__,
                    },
                }
            if merge.get("merged") is True:
                merge_sha = str(merge.get("sha") or "")[:40] or None
                if project_id and workflow_id:
                    self._record_automerge_receipt(
                        repository=repository,
                        project_id=project_id,
                        workflow_id=workflow_id,
                        pr_number=pr_number,
                        head_sha=fresh_head,
                        base_sha=fresh_base,
                        merge_sha=merge_sha,
                    )
                return {
                    "target":ACTIVE,
                    "decision":"merged-awaiting-validation",
                    "state":fresh_state,
                    "merge":{
                        "merged":True,
                        "sha":merge_sha,
                        "receipt":bool(project_id and workflow_id),
                    },
                }
            return {
                "target":REVIEW_REQUIRED,
                "decision":"merge-blocked",
                "state":fresh_state,
                "merge":{
                    "merged":False,
                    "reason":str(
                        merge.get("message")
                        or "github-merge-declined"
                    )[:500],
                },
            }
        if (
            state.ci_state is None
            and state.status_state is None
            and not state.required_checks_missing
        ):
            return {
                "target":REVIEW_REQUIRED,
                "decision":decision,
                "state":state,
            }
        if (
            state.human_review_required
            and state.ci_state == "passed"
            and state.status_state in {None, "passed"}
        ):
            return {
                "target":REVIEW_REQUIRED,
                "decision":decision,
                "state":state,
            }
        if state.merged and decision == "promote":
            return {
                "target":DONE,
                "decision":decision,
                "state":state,
            }
        return {"target":ACTIVE, "decision":decision, "state":state}

    def _github_target_for_succeeded_workflow(
        self,
        repository: str,
        workflow: dict,
    ) -> str | None:
        resolution = self._github_resolution_for_succeeded_workflow(
            repository,
            workflow,
        )
        if not isinstance(resolution, dict):
            return None
        return resolution.get("target")

    def _start_automatic_rollback(
        self,
        current: dict,
        current_workflow: dict,
        plan: dict,
    ) -> dict:
        project_id = str(current["id"])
        generation = int(current["generation"]) + 1
        metadata = (
            current_workflow.get("metadata")
            if isinstance(current_workflow, dict)
            else {}
        )
        cooperative = bool(
            isinstance(metadata, dict)
            and metadata.get("cooperative") is True
        )
        workflow = self._create_workflow(
            project_id=project_id,
            repository=str(current["repository"]),
            final_goal=str(current["final_goal"]),
            instruction=str(plan["instruction"]),
            generation=generation,
            kind="rollback",
            token_budget=int(current["token_budget"]),
            agent_preference=str(current["agent_preference"]),
            dispatch=False,
            cooperative=cooperative,
        )
        now = _now()
        try:
            with self.backend.transaction() as db:
                row = _execute(
                    db,
                    self.backend,
                    """SELECT status,generation,current_workflow_id
                       FROM managed_projects WHERE id=?""",
                    (project_id,),
                ).fetchone()
                if (
                    row is None
                    or row["status"] != NEEDS_ATTENTION
                    or int(row["generation"]) != generation - 1
                    or str(row["current_workflow_id"] or "")
                    != str(current.get("current_workflow_id") or "")
                ):
                    raise RuntimeError(
                        "managed project rollback generation changed"
                    )
                updated = _execute(
                    db,
                    self.backend,
                    """UPDATE managed_projects
                       SET status='ACTIVE', current_workflow_id=?,
                           generation=?, updated_at=?, reviewed_at=NULL
                       WHERE id=? AND generation=?
                         AND status='NEEDS_ATTENTION'""",
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
                        "managed project rollback generation changed"
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
                        "rollback",
                        str(plan["instruction"]),
                        workflow["id"],
                        "system:github-rollback",
                        now,
                    ),
                )
        except Exception:
            self._delete_unstarted_workflow(workflow["id"])
            raise

        self.workflows.dispatch_ready(
            workflow["id"],
            limit=10 if cooperative else 1,
        )
        with self.backend.connect() as db:
            row = _execute(
                db,
                self.backend,
                "SELECT * FROM managed_projects WHERE id=?",
                (project_id,),
            ).fetchone()
        return dict(row)

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

        rollback_plan = None
        workflow = None
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
                    resolution = self._github_resolution_for_succeeded_workflow(
                        str(current["repository"]),
                        workflow,
                    )
                    if isinstance(resolution, dict):
                        target = str(
                            resolution.get("target")
                            or ACTIVE
                        )
                        rollback_plan = resolution.get(
                            "rollback_plan"
                        )
                    else:
                        target = REVIEW_REQUIRED
                elif workflow_status in {"failed", "cancelled"}:
                    target = NEEDS_ATTENTION
                else:
                    target = ACTIVE

        if target == current["status"]:
            if (
                target == NEEDS_ATTENTION
                and isinstance(rollback_plan, dict)
                and isinstance(workflow, dict)
            ):
                return self._start_automatic_rollback(
                    current,
                    workflow,
                    rollback_plan,
                )
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
                       END,
                       completed_at=CASE
                           WHEN ?='DONE' THEN ?
                           ELSE completed_at
                       END,
                       completed_by=CASE
                           WHEN ?='DONE' THEN 'system:github-promotion'
                           ELSE completed_by
                       END
                   WHERE id=? AND status<>'DONE'""",
                (
                    target,
                    now,
                    target,
                    now,
                    target,
                    now,
                    target,
                    project_id,
                ),
            )
            if target == DONE:
                self.backend.append_event(
                    db,
                    "managed-project-completed",
                    {
                        "project_id":project_id,
                        "requested_by":"system:github-promotion",
                        "reason":"post-merge-validation-passed",
                    },
                    repository=str(current["repository"]),
                )
        with self.backend.connect() as db:
            row = _execute(
                db,
                self.backend,
                "SELECT * FROM managed_projects WHERE id=?",
                (project_id,),
            ).fetchone()
        updated_project = dict(row)
        if (
            target == NEEDS_ATTENTION
            and isinstance(rollback_plan, dict)
            and isinstance(workflow, dict)
        ):
            return self._start_automatic_rollback(
                updated_project,
                workflow,
                rollback_plan,
            )
        return updated_project

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

        self.workflows.dispatch_ready(
            workflow["id"],
            limit=10 if cooperative else 1,
        )
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
