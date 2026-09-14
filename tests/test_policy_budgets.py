from datetime import datetime, timezone

from production_os.budgets import BudgetLedger
from production_os.policy import PolicySet, evaluate_policy


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
