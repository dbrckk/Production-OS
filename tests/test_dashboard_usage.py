from __future__ import annotations

from datetime import datetime, timezone

import pytest

from production_os.dashboard_usage import PricingCatalog, aggregate_usage


def test_pricing_returns_unknown_for_unlisted_model():
    catalog = PricingCatalog.from_mapping({"version":"2026-09-22","rules":[]})
    cost, version = catalog.estimate(
        "unknown", "model-x", {"input_tokens":1000}, "2026-09-22T00:00:00Z"
    )
    assert cost is None
    assert version is None


def test_pricing_uses_exact_versioned_rule_and_zero_is_zero():
    catalog = PricingCatalog.from_mapping({
        "version":"2026-09-22",
        "rules":[{
            "provider":"nvidia", "model":"example-model",
            "valid_from":"2026-09-01T00:00:00+00:00", "valid_to":None,
            "input_per_million_usd":1.0,
            "cached_input_per_million_usd":0.2,
            "output_per_million_usd":2.0,
            "reasoning_per_million_usd":2.0,
        }],
    })
    cost, version = catalog.estimate(
        "nvidia", "example-model",
        {"input_tokens":1000,"cached_input_tokens":0,"output_tokens":500,
         "reasoning_tokens":0},
        "2026-09-22T10:00:00+00:00",
    )
    assert cost == pytest.approx(0.002)
    assert version == "2026-09-22"
    zero, _ = catalog.estimate(
        "nvidia", "example-model",
        {"input_tokens":0,"cached_input_tokens":0,"output_tokens":0,
         "reasoning_tokens":0},
        "2026-09-22T10:00:00+00:00",
    )
    assert zero == 0.0


def test_pricing_missing_token_field_is_unknown():
    catalog = PricingCatalog.from_mapping({
        "version":"v1",
        "rules":[{
            "provider":"p", "model":"m",
            "valid_from":"2026-01-01T00:00:00+00:00", "valid_to":None,
            "input_per_million_usd":1, "cached_input_per_million_usd":1,
            "output_per_million_usd":1, "reasoning_per_million_usd":1,
        }],
    })
    assert catalog.estimate(
        "p", "m", {"input_tokens":1}, "2026-09-22T00:00:00Z"
    ) == (None, None)


def test_usage_aggregation_does_not_mix_live_snapshot_with_final_events():
    rows = [{
        "provider":"studio","model":"model-a","api_calls":1,
        "input_tokens":700,"cached_input_tokens":0,"output_tokens":200,
        "reasoning_tokens":0,"total_tokens":900,"estimated_cost_usd":None,
        "occurred_at":"2026-09-22T10:00:00+00:00",
    }]
    result = aggregate_usage(
        rows, window="24h",
        now=datetime(2026,9,22,12,tzinfo=timezone.utc),
    )
    assert result["totals"]["total_tokens"] == 900
    assert result["totals"]["estimated_cost_usd"] is None
    assert result["providers"][0]["provider"] == "studio"


def test_usage_aggregation_hides_unauthenticated_quota_numbers():
    result = aggregate_usage(
        [], window="all",
        quota_rows=[
            {"provider":"p","quota_type":"monthly_tokens","used_value":5,
             "limit_value":10,"remaining_value":5,"unit":"tokens",
             "source_status":"unavailable","captured_at":"2026-09-22T10:00:00+00:00"},
            {"provider":"q","quota_type":"monthly_tokens","used_value":2,
             "limit_value":10,"remaining_value":8,"unit":"tokens",
             "source_status":"authenticated","captured_at":"2026-09-22T10:00:00+00:00"},
        ],
    )
    quotas = {row["provider"]: row for row in result["quotas"]}
    assert quotas["p"]["used_value"] is None
    assert quotas["p"]["remaining_value"] is None
    assert quotas["q"]["remaining_value"] == 8


def test_usage_aggregation_rejects_unknown_window():
    with pytest.raises(ValueError, match="invalid window"):
        aggregate_usage([], window="1h")
