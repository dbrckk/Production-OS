from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .approvals import ApprovalStore
from .budgets import BudgetLedger
from .emergency import emergency_stop_active
from .policy import PolicySet, evaluate_policy
from .quarantine import QuarantineStore
from .rate_limit import RateLimitStore
from .runtime_state import RuntimeState
from .workers import WorkerRegistry, select_worker


@dataclass(frozen=True, slots=True)
class AutonomousAdmissionRequest:
    handoff: dict[str, Any]
    required_capabilities: tuple[str, ...] = ()
    repo_rate_limit: int = 20
    worker_rate_limit: int = 60
    rate_window_seconds: int = 3600


@dataclass(frozen=True, slots=True)
class AutonomousAdmissionDecision:
    repository: str
    task: str
    handoff: dict[str, Any]
    risk_class: str
    constraints: dict[str, Any]
    resource_request: dict[str, float]
    runtime_action_key: str
    worker_id: str | None
    repo_rate_limit: int
    worker_rate_limit: int
    rate_window_seconds: int


def evaluate_autonomous_admission(
    request: AutonomousAdmissionRequest,
    runtime_state: RuntimeState,
    *,
    worker_registry: WorkerRegistry | None = None,
    emergency_stop_path: str | Path | None = None,
    rate_limit_store: RateLimitStore | None = None,
    approval_store: ApprovalStore | None = None,
    policy_set: PolicySet | None = None,
    budget_ledger: BudgetLedger | None = None,
    quarantine_store: QuarantineStore | None = None,
) -> AutonomousAdmissionDecision:
    handoff = dict(request.handoff or {})
    repository = str(handoff.get("repository", ""))
    task = str(handoff.get("task", ""))
    if not repository or not task:
        raise ValueError("handoff requires repository and task")
    if emergency_stop_active(emergency_stop_path):
        raise RuntimeError("emergency stop active")

    policies = policy_set or PolicySet({})
    policy_decision = evaluate_policy(policies, handoff)
    if quarantine_store is not None:
        quarantined, reason = quarantine_store.active(repository)
        if quarantined:
            raise RuntimeError(
                f"repository quarantined: {reason or 'policy'}"
            )
    if not policy_decision.allowed:
        raise RuntimeError(
            "policy blocked dispatch: "
            + "; ".join(policy_decision.reasons)
        )

    constraints = dict(handoff.get("constraints", {}) or {})
    if policy_decision.requires_approval:
        constraints["requires_human_approval"] = True
    normalized_handoff = {
        **handoff,
        "risk_class":policy_decision.risk_class,
        "constraints":constraints,
    }

    raw_request = normalized_handoff.get("resource_request", {}) or {}
    normalized_request = {
        str(key):float(value)
        for key, value in raw_request.items()
        if isinstance(value, (int, float))
        and not isinstance(value, bool)
    }
    if budget_ledger is not None and policy_decision.budgets:
        decision = budget_ledger.check(
            repository,
            policy_decision.budgets,
            normalized_request,
        )
        if not decision.allowed:
            raise RuntimeError(
                "budget blocked dispatch: " + "; ".join(decision.reasons)
            )

    portfolio_budgets = {
        str(key):float(value)
        for key, value in (
            policies.payload.get("portfolio_budgets", {}) or {}
        ).items()
        if isinstance(value, (int, float))
        and not isinstance(value, bool)
    }
    if budget_ledger is not None and portfolio_budgets:
        decision = budget_ledger.check(
            "__portfolio__",
            portfolio_budgets,
            normalized_request,
        )
        if not decision.allowed:
            raise RuntimeError(
                "portfolio budget blocked dispatch: "
                + "; ".join(decision.reasons)
            )

    worker = None
    if worker_registry is not None:
        worker_registry.detect_dead()
        worker = select_worker(
            worker_registry,
            list(request.required_capabilities),
            policy_decision.allowed_worker_classes,
        )
        if worker is None:
            if policy_decision.allowed_worker_classes:
                raise RuntimeError(
                    "backpressure: no allowed capable worker available"
                )
            raise RuntimeError("backpressure: no capable worker available")

    if rate_limit_store is not None:
        repo_decision = rate_limit_store.check(
            f"repo:{repository}",
            limit=int(request.repo_rate_limit),
            window_seconds=int(request.rate_window_seconds),
        )
        if not repo_decision.allowed:
            raise RuntimeError("rate limit exceeded for repository")
        if worker is not None:
            worker_decision = rate_limit_store.check(
                f"worker:{worker.worker_id}",
                limit=int(request.worker_rate_limit),
                window_seconds=int(request.rate_window_seconds),
            )
            if not worker_decision.allowed:
                raise RuntimeError("rate limit exceeded for worker")

    record = runtime_state.get(repository, task)
    if bool(constraints.get("requires_human_approval", False)):
        if (
            approval_store is None
            or not approval_store.is_approved(record.key)
        ):
            raise RuntimeError("human approval required")
    if runtime_state.is_leased(record):
        raise RuntimeError("task already leased")
    if runtime_state.in_cooldown(record):
        raise RuntimeError("task is in cooldown")
    if record.status in {"circuit-open", "succeeded"}:
        raise RuntimeError(f"task not dispatchable: {record.status}")

    return AutonomousAdmissionDecision(
        repository=repository,
        task=task,
        handoff=normalized_handoff,
        risk_class=policy_decision.risk_class,
        constraints=constraints,
        resource_request=normalized_request,
        runtime_action_key=record.key,
        worker_id=worker.worker_id if worker is not None else None,
        repo_rate_limit=int(request.repo_rate_limit),
        worker_rate_limit=int(request.worker_rate_limit),
        rate_window_seconds=int(request.rate_window_seconds),
    )


def commit_autonomous_admission(
    decision: AutonomousAdmissionDecision,
    *,
    rate_limit_store: RateLimitStore | None = None,
    budget_ledger: BudgetLedger | None = None,
    idempotency_key: str | None = None,
    include_worker_rate_limit: bool = True,
) -> None:
    if rate_limit_store is not None:
        repo_key = f"repo:{decision.repository}"
        if idempotency_key:
            rate_limit_store.record_once(
                repo_key,
                idempotency_key,
                window_seconds=decision.rate_window_seconds,
            )
        else:
            result = rate_limit_store.check_and_record(
                repo_key,
                limit=decision.repo_rate_limit,
                window_seconds=decision.rate_window_seconds,
            )
            if not result.allowed:
                raise RuntimeError("rate limit exceeded for repository")

        if include_worker_rate_limit and decision.worker_id is not None:
            worker_key = f"worker:{decision.worker_id}"
            result = rate_limit_store.check_and_record(
                worker_key,
                limit=decision.worker_rate_limit,
                window_seconds=decision.rate_window_seconds,
            )
            if not result.allowed:
                raise RuntimeError("rate limit exceeded for worker")

    if budget_ledger is not None and decision.resource_request:
        if idempotency_key:
            budget_ledger.record_once(
                decision.repository,
                decision.resource_request,
                idempotency_key=f"{idempotency_key}:repository",
            )
            budget_ledger.record_once(
                "__portfolio__",
                decision.resource_request,
                idempotency_key=f"{idempotency_key}:portfolio",
            )
        else:
            budget_ledger.record(
                decision.repository,
                decision.resource_request,
            )
            budget_ledger.record(
                "__portfolio__",
                decision.resource_request,
            )
