from production_os.managed_projects import (
    ACTIVE,
    DONE,
    NEEDS_ATTENTION,
    REVIEW_REQUIRED,
    _review_guidance,
)


def outcome(**overrides):
    base = {
        "available":True,
        "workflow_status":"succeeded",
        "summary":"Delivered result",
        "validation_status":"passed",
        "validation_tests":["unit","integration"],
        "commit_shas":["abcdef1"],
        "artifact_count":1,
        "changed_file_count":2,
        "pull_request":{"number":42,"state":"open"},
    }
    base.update(overrides)
    return base


def test_review_guidance_for_active_project_requires_no_operator_action():
    guidance = _review_guidance(ACTIVE, outcome())
    assert guidance["action_required"] is False
    assert guidance["state"] == "running"
    assert guidance["primary_action"] is None
    assert guidance["available_actions"] == []
    assert guidance["validation_passed"] is True
    assert guidance["evidence_level"] == "rich"


def test_review_guidance_for_passed_review_is_decision_support_not_auto_done():
    guidance = _review_guidance(REVIEW_REQUIRED, outcome())
    assert guidance["action_required"] is True
    assert guidance["state"] == "review"
    assert guidance["headline"] == "Examiner les preuves puis décider"
    assert guidance["primary_action"] == "review"
    assert guidance["available_actions"] == [
        "instructions",
        "verify",
        "complete",
    ]
    assert guidance["validation_passed"] is True
    assert "valider DONE" in guidance["detail"]
    assert "automatique" not in guidance["detail"].lower()


def test_review_guidance_for_failed_validation_prefers_correction_or_retest():
    guidance = _review_guidance(
        NEEDS_ATTENTION,
        outcome(
            workflow_status="failed",
            validation_status="failed",
            validation_tests=["integration"],
        ),
    )
    assert guidance["action_required"] is True
    assert guidance["state"] == "needs_attention"
    assert guidance["headline"] == "Corriger puis relancer la validation"
    assert guidance["primary_action"] == "instructions"
    assert guidance["available_actions"] == ["instructions", "verify"]
    assert guidance["validation_passed"] is False


def test_review_guidance_handles_missing_validation_without_false_pass():
    guidance = _review_guidance(
        REVIEW_REQUIRED,
        outcome(
            validation_status=None,
            validation_tests=[],
            commit_shas=[],
            artifact_count=0,
            changed_file_count=0,
            pull_request=None,
        ),
    )
    assert guidance["validation_passed"] is None
    assert guidance["headline"] == "Examiner le résultat"
    assert guidance["evidence_level"] == "minimal"
    assert guidance["evidence_count"] == 1
    assert guidance["evidence"] == {
        "summary":True,
        "validation":False,
        "tests":False,
        "commits":False,
        "artifacts":False,
        "pull_request":False,
    }


def test_done_project_has_no_required_action():
    guidance = _review_guidance(DONE, outcome())
    assert guidance["action_required"] is False
    assert guidance["state"] == "done"
    assert guidance["headline"] == "Projet terminé"
    assert guidance["available_actions"] == []
