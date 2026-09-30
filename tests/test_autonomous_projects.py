from __future__ import annotations

import re

import pytest

from production_os.autonomous_projects import (
    autonomous_action_fingerprint,
    autonomous_project_id,
)


def _fingerprint(**overrides):
    payload = {
        "repository":"owner/repo",
        "task":"Fix flaky login regression",
        "acceptance_criteria":[
            "Tests pass",
            "No login regression",
        ],
        "trigger_evidence":[
            "ci:test_login failed",
            "issue:123 reopened",
        ],
        "risk_class":"medium",
    }
    payload.update(overrides)
    return autonomous_action_fingerprint(**payload)


def test_autonomous_project_id_is_deterministic():
    first = autonomous_project_id(
        repository="owner/repo",
        action_fingerprint=_fingerprint(),
    )
    second = autonomous_project_id(
        repository="owner/repo",
        action_fingerprint=_fingerprint(),
    )

    assert first == second
    assert re.fullmatch(r"controller-[0-9a-f]{32}", first)


def test_action_fingerprint_normalizes_evidence_order():
    first = _fingerprint(
        trigger_evidence=["b", "a"],
        acceptance_criteria=["two", "one"],
    )
    second = _fingerprint(
        trigger_evidence=["a", "b"],
        acceptance_criteria=["one", "two"],
    )

    assert first == second


def test_action_fingerprint_changes_on_task_change():
    assert _fingerprint(task="Task A") != _fingerprint(task="Task B")


def test_action_fingerprint_changes_on_acceptance_change():
    assert _fingerprint(
        acceptance_criteria=["A"],
    ) != _fingerprint(
        acceptance_criteria=["B"],
    )


def test_action_fingerprint_changes_on_trigger_evidence_change():
    assert _fingerprint(
        trigger_evidence=["A"],
    ) != _fingerprint(
        trigger_evidence=["B"],
    )


def test_action_fingerprint_excludes_score_and_lane_metadata():
    baseline = _fingerprint()

    first = autonomous_action_fingerprint(
        repository="owner/repo",
        task="Fix flaky login regression",
        acceptance_criteria=["Tests pass", "No login regression"],
        trigger_evidence=["ci:test_login failed", "issue:123 reopened"],
        risk_class="medium",
        metadata={"priority":99.0, "lane":"NOW"},
    )
    second = autonomous_action_fingerprint(
        repository="owner/repo",
        task="Fix flaky login regression",
        acceptance_criteria=["Tests pass", "No login regression"],
        trigger_evidence=["ci:test_login failed", "issue:123 reopened"],
        risk_class="medium",
        metadata={"priority":1.0, "lane":"PARALLEL"},
    )

    assert first == baseline
    assert second == baseline


@pytest.mark.parametrize(
    "repository",
    ["", "owner", "../repo", "owner/../repo", "owner/repo/extra"],
)
def test_autonomous_project_id_rejects_invalid_repository(repository):
    with pytest.raises(ValueError, match="repository must be owner/name"):
        autonomous_project_id(
            repository=repository,
            action_fingerprint="abc123",
        )
