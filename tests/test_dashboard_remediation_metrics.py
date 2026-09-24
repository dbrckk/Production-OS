from __future__ import annotations

from datetime import datetime, timezone

import pytest

from production_os.dashboard_remediation_metrics import (
    aggregate_remediation_analytics,
)


NOW = datetime(2026, 9, 24, 17, 0, tzinfo=timezone.utc)


def test_effectiveness_denominator_excludes_pending_and_not_applicable():
    rows = [
        {
            "action":"kick",
            "incident_code":"queue_without_worker",
            "verification_state":"resolved",
            "requested_at":"2026-09-24T16:00:00+00:00",
            "completed_at":"2026-09-24T16:01:00+00:00",
            "verified_at":"2026-09-24T16:06:00+00:00",
        },
        {
            "action":"kick",
            "incident_code":"queue_without_worker",
            "verification_state":"still_active",
            "requested_at":"2026-09-24T16:10:00+00:00",
            "completed_at":"2026-09-24T16:11:00+00:00",
            "verified_at":"2026-09-24T16:12:00+00:00",
        },
        {
            "action":"kick",
            "incident_code":"queue_without_worker",
            "verification_state":"pending",
            "requested_at":"2026-09-24T16:20:00+00:00",
        },
        {
            "action":"kick",
            "incident_code":"queue_without_worker",
            "verification_state":"not_applicable",
            "requested_at":"2026-09-24T16:30:00+00:00",
        },
    ]
    result = aggregate_remediation_analytics(
        rows,
        window="24h",
        now=NOW,
    )
    summary = result["summary"]
    assert summary["total"] == 4
    assert summary["effectiveness_denominator"] == 2
    assert summary["observed_resolution_rate"] == 50.0
    assert summary["pending"] == 1
    assert summary["not_applicable"] == 1


def test_median_resolution_detection_uses_only_valid_resolved_rows():
    rows = [
        {
            "action":"kick",
            "incident_code":"queue_without_worker",
            "verification_state":"resolved",
            "requested_at":"2026-09-24T15:00:00+00:00",
            "completed_at":"2026-09-24T15:01:00+00:00",
            "verified_at":"2026-09-24T15:03:00+00:00",
        },
        {
            "action":"recover-stuck",
            "incident_code":"stale_busy_workers",
            "verification_state":"resolved",
            "requested_at":"2026-09-24T15:10:00+00:00",
            "completed_at":"2026-09-24T15:11:00+00:00",
            "verified_at":"2026-09-24T15:17:00+00:00",
        },
        {
            "action":"cancel-current",
            "incident_code":"stale_running_executions",
            "verification_state":"still_active",
            "requested_at":"2026-09-24T15:20:00+00:00",
            "completed_at":"2026-09-24T15:21:00+00:00",
            "verified_at":"2026-09-24T15:40:00+00:00",
        },
    ]
    result = aggregate_remediation_analytics(
        rows,
        window="24h",
        now=NOW,
    )
    assert result["summary"]["median_resolution_detection_seconds"] == 240.0


def test_window_filter_and_breakdowns_are_deterministic():
    rows = [
        {
            "action":"kick",
            "incident_code":"queue_without_worker",
            "verification_state":"resolved",
            "requested_at":"2026-09-24T16:00:00+00:00",
            "completed_at":"2026-09-24T16:00:00+00:00",
            "verified_at":"2026-09-24T16:01:00+00:00",
        },
        {
            "action":"recover-stuck",
            "incident_code":"stale_busy_workers",
            "verification_state":"resolved",
            "requested_at":"2026-09-20T16:00:00+00:00",
            "completed_at":"2026-09-20T16:00:00+00:00",
            "verified_at":"2026-09-20T16:02:00+00:00",
        },
    ]
    result = aggregate_remediation_analytics(
        rows,
        window="24h",
        now=NOW,
    )
    assert result["summary"]["total"] == 1
    assert result["by_action"][0]["name"] == "kick"
    assert result["by_incident_code"][0]["name"] == "queue_without_worker"


def test_zero_denominator_has_no_resolution_rate():
    result = aggregate_remediation_analytics(
        [{
            "action":"kick",
            "incident_code":"queue_without_worker",
            "verification_state":"pending",
            "requested_at":"2026-09-24T16:00:00+00:00",
        }],
        window="24h",
        now=NOW,
    )
    assert result["summary"]["effectiveness_denominator"] == 0
    assert result["summary"]["observed_resolution_rate"] is None


def test_invalid_window_is_rejected():
    with pytest.raises(ValueError, match="invalid window"):
        aggregate_remediation_analytics([], window="90d", now=NOW)
