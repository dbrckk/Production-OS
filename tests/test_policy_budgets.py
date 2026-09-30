from datetime import datetime, timezone

from production_os.budgets import BudgetLedger
from production_os.policy import PolicySet, evaluate_policy
from production_os.rate_limit import RateLimitStore


def test_high_risk_requires_approval():
    policies=PolicySet({
        "defaults":{
            "approval_required_from":"high",
            "max_risk_class":"critical",
        }
    })
    decision=evaluate_policy(
        policies,
        {"repository":"o/a","task":"production release","constraints":{}},
        now=datetime(2026,9,14,12,0,tzinfo=timezone.utc),
    )
    assert decision.allowed is True
    assert decision.requires_approval is True
    assert decision.risk_class=="high"


def test_budget_blocks_projected_usage(tmp_path):
    ledger=BudgetLedger(tmp_path/"budget.json")
    ledger.record("o/a",{"tokens":90})
    decision=ledger.check("o/a",{"tokens":100},{"tokens":20})
    assert decision.allowed is False



def test_rate_limit_check_does_not_mutate_store(tmp_path):
    path = tmp_path / "rate.json"
    store = RateLimitStore(path)

    first = store.check("repo:o/a", limit=2, window_seconds=3600)
    second = store.check("repo:o/a", limit=2, window_seconds=3600)

    assert first.allowed is True
    assert second.allowed is True
    reloaded = RateLimitStore(path)
    assert reloaded.events.get("repo:o/a", []) == []


def test_rate_limit_record_once_is_idempotent(tmp_path):
    path = tmp_path / "rate.json"
    store = RateLimitStore(path)

    store.record_once(
        "repo:o/a",
        "controller-project-1",
        window_seconds=3600,
    )
    reloaded = RateLimitStore(path)
    reloaded.record_once(
        "repo:o/a",
        "controller-project-1",
        window_seconds=3600,
    )

    final = RateLimitStore(path)
    assert len(final.events["repo:o/a"]) == 1


def test_budget_record_once_is_idempotent(tmp_path):
    path = tmp_path / "budget.json"
    ledger = BudgetLedger(path)

    first = ledger.record_once(
        "o/a",
        {"tokens":25},
        idempotency_key="controller-project-1",
    )
    reloaded = BudgetLedger(path)
    second = reloaded.record_once(
        "o/a",
        {"tokens":25},
        idempotency_key="controller-project-1",
    )

    assert first["tokens"] == 25
    assert second["tokens"] == 25
    assert BudgetLedger(path).payload["usage"]["o/a"]["tokens"] == 25


def test_different_project_ids_charge_independently(tmp_path):
    path = tmp_path / "budget.json"
    ledger = BudgetLedger(path)

    ledger.record_once(
        "o/a",
        {"tokens":25},
        idempotency_key="controller-project-1",
    )
    ledger.record_once(
        "o/a",
        {"tokens":25},
        idempotency_key="controller-project-2",
    )

    assert BudgetLedger(path).payload["usage"]["o/a"]["tokens"] == 50


def test_legacy_rate_limit_check_and_record_still_records_each_call(tmp_path):
    path = tmp_path / "rate.json"
    store = RateLimitStore(path)

    first = store.check_and_record("repo:o/a", limit=3, window_seconds=3600)
    second = store.check_and_record("repo:o/a", limit=3, window_seconds=3600)

    assert first.allowed is True
    assert second.allowed is True
    assert len(RateLimitStore(path).events["repo:o/a"]) == 2
