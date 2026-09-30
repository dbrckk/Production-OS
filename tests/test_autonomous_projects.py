from __future__ import annotations

import re

import pytest

from production_os.autonomous_projects import (
    AutonomousProjectRequest,
    autonomous_action_fingerprint,
    autonomous_project_id,
    launch_autonomous_project,
)
from production_os.managed_projects import ManagedProjectService
from production_os.sqlite_backend import SQLiteBackend, SQLiteJobQueue
from production_os.workflow_engine import WorkflowEngine


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



def _service(tmp_path):
    backend = SQLiteBackend(tmp_path / "autonomous.sqlite")
    return ManagedProjectService(
        WorkflowEngine(backend, SQLiteJobQueue(backend))
    )


def _request(**overrides):
    fingerprint = _fingerprint(
        trigger_evidence=overrides.pop(
            "trigger_evidence",
            ["ci:test_login failed"],
        ),
    )
    values = {
        "repository":"owner/repo",
        "task":"Fix flaky login regression",
        "rationale":"CI regression",
        "acceptance_criteria":("Tests pass",),
        "priority":90.0,
        "token_budget":12000,
        "agent_preference":"auto",
        "cooperative":False,
        "action_fingerprint":fingerprint,
    }
    values.update(overrides)
    return AutonomousProjectRequest(**values)


def test_launch_creates_managed_project_once(tmp_path):
    managed = _service(tmp_path)

    launch = launch_autonomous_project(managed, _request())

    assert launch.created is True
    assert launch.project_id.startswith("controller-")
    assert launch.project["project_id"] == launch.project_id
    assert launch.project["created_by"] == "controller"


def test_repeated_identical_launch_reuses_existing_project(tmp_path):
    managed = _service(tmp_path)
    first = launch_autonomous_project(managed, _request())

    second = launch_autonomous_project(managed, _request())

    assert second.created is False
    assert second.project_id == first.project_id
    assert second.project["project_id"] == first.project_id


def test_reuse_does_not_create_second_workflow(tmp_path):
    managed = _service(tmp_path)
    first = launch_autonomous_project(managed, _request())
    first_workflow = first.project["current_workflow_id"]

    second = launch_autonomous_project(managed, _request())

    assert second.project["current_workflow_id"] == first_workflow
    with managed.backend.connect() as db:
        workflow_count = db.execute(
            "SELECT COUNT(*) AS n FROM workflows"
        ).fetchone()["n"]
    assert workflow_count == 1


def test_successful_terminal_identical_project_is_skipped(tmp_path):
    managed = _service(tmp_path)
    first = launch_autonomous_project(managed, _request())
    with managed.backend.transaction() as db:
        db.execute(
            """
            UPDATE managed_projects
            SET status='DONE', completed_by='controller-test',
                completed_at=updated_at
            WHERE id=?
            """,
            (first.project_id,),
        )

    second = launch_autonomous_project(managed, _request())

    assert second.created is False
    assert second.project_id == first.project_id
    assert second.project["status"] == "DONE"


def test_changed_trigger_evidence_creates_new_project(tmp_path):
    managed = _service(tmp_path)
    first = launch_autonomous_project(
        managed,
        _request(trigger_evidence=["ci:first"]),
    )

    second = launch_autonomous_project(
        managed,
        _request(trigger_evidence=["ci:second"]),
    )

    assert second.created is True
    assert second.project_id != first.project_id


def test_partial_initialization_retry_uses_same_project_id(tmp_path, monkeypatch):
    managed = _service(tmp_path)
    request = _request()
    seen = []
    real_create = managed.create

    def flaky_create(**kwargs):
        seen.append(kwargs["project_id"])
        if len(seen) == 1:
            raise RuntimeError("simulated initialization failure")
        return real_create(**kwargs)

    monkeypatch.setattr(managed, "create", flaky_create)

    with pytest.raises(RuntimeError, match="simulated initialization failure"):
        launch_autonomous_project(managed, request)
    second = launch_autonomous_project(managed, request)

    assert second.created is True
    assert seen[0] == seen[1] == second.project_id
