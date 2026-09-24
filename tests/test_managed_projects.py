from __future__ import annotations

import pytest

from production_os.control_plane import ControlPlane
from production_os.managed_projects import (
    ACTIVE,
    DONE,
    NEEDS_ATTENTION,
    REVIEW_REQUIRED,
    ManagedProjectError,
)


def _create(control):
    return control.managed_projects.create(
        repository="dbrckk/managed-example",
        final_goal="Build and validate the complete product",
        requested_by="operator:test",
    )


def test_managed_project_creation_persists_across_restart(tmp_path):
    database = str(tmp_path / "managed.sqlite")
    first = ControlPlane(database)
    project = _create(first)

    assert project["status"] == ACTIVE
    assert project["generation"] == 1
    assert len(project["runs"]) == 1
    assert project["runs"][0]["kind"] == "initial"
    workflow = project["current_workflow"]
    assert workflow["metadata"]["managed_project_id"] == project["id"]
    assert workflow["metadata"]["managed_project_generation"] == 1
    assert workflow["metadata"]["managed_project_kind"] == "initial"
    assert workflow["tasks"][0]["payload"]["handoff"]["final_goal"] == project["final_goal"]

    second = ControlPlane(database)
    restored = second.managed_projects.get(project["id"])
    assert restored["id"] == project["id"]
    assert restored["current_workflow_id"] == project["current_workflow_id"]
    assert restored["generation"] == 1
    assert len(restored["runs"]) == 1


def test_succeeded_generation_moves_to_review_required(tmp_path):
    control = ControlPlane(str(tmp_path / "managed.sqlite"))
    project = _create(control)
    workflow_id = project["current_workflow_id"]

    control.workflows.record_result(
        workflow_id,
        "implementation",
        succeeded=True,
        result={"summary":"done"},
    )
    reviewed = control.managed_projects.get(project["id"])

    assert reviewed["status"] == REVIEW_REQUIRED
    assert reviewed["reviewed_at"] is not None
    assert reviewed["current_workflow"]["status"] == "succeeded"


def test_cancelled_generation_moves_to_needs_attention(tmp_path):
    control = ControlPlane(str(tmp_path / "managed.sqlite"))
    project = _create(control)

    control.workflows.cancel(project["current_workflow_id"])
    current = control.managed_projects.get(project["id"])

    assert current["status"] == NEEDS_ATTENTION


def test_follow_up_instruction_creates_immutable_new_generation(tmp_path):
    control = ControlPlane(str(tmp_path / "managed.sqlite"))
    project = _create(control)
    first_workflow = project["current_workflow_id"]
    control.workflows.record_result(
        first_workflow,
        "implementation",
        succeeded=True,
        result={"summary":"first"},
    )
    assert control.managed_projects.get(project["id"])["status"] == REVIEW_REQUIRED

    follow = control.managed_projects.add_instruction(
        project["id"],
        instruction="Improve onboarding and rerun all tests",
        requested_by="operator:test",
    )

    assert follow["status"] == ACTIVE
    assert follow["generation"] == 2
    assert follow["current_workflow_id"] != first_workflow
    assert len(follow["runs"]) == 2
    assert follow["runs"][1]["kind"] == "instruction"
    assert follow["runs"][1]["instruction"] == "Improve onboarding and rerun all tests"
    assert control.workflows.get(first_workflow)["status"] == "succeeded"
    assert control.workflows.get(first_workflow)["metadata"]["managed_project_generation"] == 1
    assert follow["current_workflow"]["metadata"]["managed_project_generation"] == 2


def test_active_project_rejects_second_follow_up(tmp_path):
    control = ControlPlane(str(tmp_path / "managed.sqlite"))
    project = _create(control)

    with pytest.raises(ManagedProjectError, match="require review or attention"):
        control.managed_projects.add_instruction(
            project["id"],
            instruction="Do something else",
            requested_by="operator:test",
        )
    assert control.managed_projects.get(project["id"])["generation"] == 1


def test_retest_creates_new_generation_and_keeps_final_goal(tmp_path):
    control = ControlPlane(str(tmp_path / "managed.sqlite"))
    project = _create(control)
    control.workflows.record_result(
        project["current_workflow_id"],
        "implementation",
        succeeded=True,
        result={"summary":"done"},
    )

    retest = control.managed_projects.retest(
        project["id"],
        requested_by="operator:test",
    )

    assert retest["generation"] == 2
    assert retest["runs"][1]["kind"] == "retest"
    handoff = retest["current_workflow"]["tasks"][0]["payload"]["handoff"]
    assert handoff["final_goal"] == project["final_goal"]
    assert "Review and retest" in handoff["task"]


def test_project_can_be_completed_only_after_review(tmp_path):
    control = ControlPlane(str(tmp_path / "managed.sqlite"))
    project = _create(control)

    with pytest.raises(ManagedProjectError, match="REVIEW_REQUIRED"):
        control.managed_projects.complete(
            project["id"],
            requested_by="operator:test",
        )

    control.workflows.record_result(
        project["current_workflow_id"],
        "implementation",
        succeeded=True,
        result={"summary":"done"},
    )
    completed = control.managed_projects.complete(
        project["id"],
        requested_by="operator:test",
    )

    assert completed["status"] == DONE
    assert completed["completed_at"] is not None
    assert control.managed_projects.get(project["id"])["status"] == DONE


@pytest.mark.parametrize(
    "repository",
    ["", "owner", "../repo", "owner/..", "owner/repo/extra", "/repo"],
)
def test_managed_project_rejects_invalid_repository_identity(tmp_path, repository):
    control = ControlPlane(str(tmp_path / "managed.sqlite"))
    with pytest.raises(ManagedProjectError, match="owner/name"):
        control.managed_projects.create(
            repository=repository,
            final_goal="Ship it",
            requested_by="operator:test",
        )
