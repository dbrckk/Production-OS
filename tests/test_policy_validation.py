from production_os.policy_validation import validate_policy_payload


def test_valid_policy_payload():
    result=validate_policy_payload({
        "defaults":{
            "max_risk_class":"high",
            "approval_required_from":"high",
            "budgets":{"tokens":1000},
            "slo":{"max_attempts":3},
        },
        "repositories":[{"match":"o/*"}],
    })
    assert result.valid is True


def test_invalid_policy_payload():
    result=validate_policy_payload({
        "defaults":{"max_risk_class":"extreme"},
        "repositories":[{}],
    })
    assert result.valid is False
