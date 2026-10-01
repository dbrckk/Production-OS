from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from production_os.approvals import ApprovalStore
from production_os.autonomous_admission import (
    AutonomousAdmissionRequest,
    evaluate_autonomous_admission,
)
from production_os.budgets import BudgetLedger
from production_os.emergency import set_emergency_stop
from production_os.policy import PolicySet
from production_os.quarantine import QuarantineStore
from production_os.rate_limit import RateLimitStore
from production_os.runtime_state import RuntimeState, task_key
from production_os.workers import WorkerRegistry


def _request(**overrides):
    values = {
        "handoff":{
            "repository":"owner/repo",
            "task":"Improve login tests",
            "resource_request":{"tokens":10},
        },
        "required_capabilities":(),
        "repo_rate_limit":20,
        "worker_rate_limit":60,
        "rate_window_seconds":3600,
    }
    values.update(overrides)
    return AutonomousAdmissionRequest(**values)


def _evaluate(
    tmp_path,
    *,
    request=None,
    state=None,
    workers=None,
    policies=None,
    rate_limits=None,
    approvals=None,
    budgets=None,
    quarantine=None,
    emergency_stop_path=None,
):
    state = state or RuntimeState(tmp_path / "runtime.json")
    return evaluate_autonomous_admission(
        request or _request(),
        state,
        worker_registry=workers,
        emergency_stop_path=emergency_stop_path,
        rate_limit_store=rate_limits,
        approval_store=approvals,
        policy_set=policies or PolicySet({}),
        budget_ledger=budgets,
        quarantine_store=quarantine,
    )


def test_managed_admission_uses_same_runtime_key_as_legacy_dispatch(tmp_path):
    decision = _evaluate(tmp_path)

    assert decision.runtime_action_key == task_key(
        "owner/repo",
        "Improve login tests",
    )


def test_managed_admission_rate_limit_check_is_read_only_until_commit(tmp_path):
    path = tmp_path / "rate.json"
    store = RateLimitStore(path)

    decision = _evaluate(tmp_path, rate_limits=store)

    assert decision.repository == "owner/repo"
    assert RateLimitStore(path).events.get("repo:owner/repo", []) == []


def test_autonomous_admission_blocks_emergency_stop(tmp_path):
    stop = tmp_path / "stop.json"
    set_emergency_stop(stop, reason="incident")

    with pytest.raises(RuntimeError, match="emergency stop active"):
        _evaluate(tmp_path, emergency_stop_path=stop)


def test_autonomous_admission_blocks_policy(tmp_path):
    policies = PolicySet({
        "defaults":{"disabled":True},
    })

    with pytest.raises(RuntimeError, match="policy blocked"):
        _evaluate(tmp_path, policies=policies)


def test_autonomous_admission_blocks_quarantine(tmp_path):
    store = QuarantineStore(tmp_path / "quarantine.json")
    store.set("owner/repo", active=True, reason="incident")

    with pytest.raises(RuntimeError, match="repository quarantined"):
        _evaluate(tmp_path, quarantine=store)


def test_autonomous_admission_blocks_repository_budget(tmp_path):
    ledger = BudgetLedger(tmp_path / "budget.json")
    ledger.record("owner/repo", {"tokens":95})
    policies = PolicySet({
        "defaults":{"budgets":{"tokens":100}},
    })

    with pytest.raises(RuntimeError, match="budget blocked"):
        _evaluate(tmp_path, policies=policies, budgets=ledger)


def test_autonomous_admission_blocks_portfolio_budget(tmp_path):
    ledger = BudgetLedger(tmp_path / "budget.json")
    ledger.record("__portfolio__", {"tokens":95})
    policies = PolicySet({
        "portfolio_budgets":{"tokens":100},
    })

    with pytest.raises(RuntimeError, match="portfolio budget blocked"):
        _evaluate(tmp_path, policies=policies, budgets=ledger)


def test_autonomous_admission_requires_human_approval(tmp_path):
    policies = PolicySet({
        "defaults":{"approval_required_from":"low"},
    })

    with pytest.raises(RuntimeError, match="human approval required"):
        _evaluate(tmp_path, policies=policies)


def test_autonomous_admission_accepts_same_canonical_approval_key(tmp_path):
    policies = PolicySet({
        "defaults":{"approval_required_from":"low"},
    })
    approvals = ApprovalStore(tmp_path / "approvals.json")
    approvals.set(
        task_key("owner/repo", "Improve login tests"),
        approved=True,
        approved_by="operator",
        reason="ok",
    )

    decision = _evaluate(
        tmp_path,
        policies=policies,
        approvals=approvals,
    )

    assert decision.runtime_action_key == task_key(
        "owner/repo",
        "Improve login tests",
    )


def test_autonomous_admission_blocks_repository_rate_limit(tmp_path):
    store = RateLimitStore(tmp_path / "rate.json")
    store.check_and_record(
        "repo:owner/repo",
        limit=1,
        window_seconds=3600,
    )
    request = _request(repo_rate_limit=1)

    with pytest.raises(RuntimeError, match="rate limit exceeded for repository"):
        _evaluate(tmp_path, request=request, rate_limits=store)


def test_autonomous_admission_blocks_no_capable_worker(tmp_path):
    workers = WorkerRegistry(tmp_path / "workers.json")
    workers.register("worker-a", ["python"], 1)
    request = _request(required_capabilities=("android",))

    with pytest.raises(RuntimeError, match="no capable worker"):
        _evaluate(tmp_path, request=request, workers=workers)


def test_autonomous_admission_blocks_active_lease(tmp_path):
    state = RuntimeState(tmp_path / "runtime.json")
    state.acquire_lease(
        "owner/repo",
        "Improve login tests",
        "worker-a",
    )

    with pytest.raises(RuntimeError, match="task already leased"):
        _evaluate(tmp_path, state=state)


def test_autonomous_admission_blocks_cooldown(tmp_path):
    state = RuntimeState(tmp_path / "runtime.json")
    record = state.get("owner/repo", "Improve login tests")
    record.cooldown_until = (
        datetime.now(timezone.utc) + timedelta(hours=1)
    ).isoformat()
    state.save()

    with pytest.raises(RuntimeError, match="task is in cooldown"):
        _evaluate(tmp_path, state=state)


@pytest.mark.parametrize("status", ["circuit-open", "succeeded"])
def test_autonomous_admission_blocks_terminal_runtime_state(tmp_path, status):
    state = RuntimeState(tmp_path / "runtime.json")
    record = state.get("owner/repo", "Improve login tests")
    record.status = status
    state.save()

    with pytest.raises(RuntimeError, match=f"task not dispatchable: {status}"):
        _evaluate(tmp_path, state=state)
