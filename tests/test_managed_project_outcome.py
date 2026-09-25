from production_os.managed_projects import _outcome_from_workflow


def test_outcome_normalizes_worker_result_evidence():
    outcome = _outcome_from_workflow({
        "status":"succeeded",
        "updated_at":"2026-09-25T18:40:00+00:00",
        "tasks":[{
            "task_id":"implementation",
            "status":"succeeded",
            "result":{
                "summary":"Implemented feature and validated it.",
                "validation":{
                    "status":"passed",
                    "tests":["unit","integration"],
                },
                "commit_shas":[
                    "abcdef1234567890abcdef1234567890abcdef12",
                    "ABCDEF1234567890ABCDEF1234567890ABCDEF12",
                    "not-a-sha",
                ],
                "pull_request":{"number":"42","state":"open"},
            },
        }],
        "artifacts":[
            {"name":"test-report"},
            {"name":"release-evidence"},
        ],
    })

    assert outcome == {
        "available":True,
        "workflow_status":"succeeded",
        "summary":"Implemented feature and validated it.",
        "validation_status":"passed",
        "validation_tests":["unit","integration"],
        "commit_shas":["abcdef1234567890abcdef1234567890abcdef12"],
        "artifact_count":2,
        "artifact_names":["test-report","release-evidence"],
        "pull_request":{"number":42,"state":"open"},
        "completed_at":"2026-09-25T18:40:00+00:00",
    }


def test_outcome_uses_evidence_fallback_and_keeps_optional_shape_stable():
    outcome = _outcome_from_workflow({
        "status":"failed",
        "updated_at":"2026-09-25T18:41:00+00:00",
        "tasks":[{
            "result":{
                "evidence":{
                    "summary":"Validation failed on integration suite.",
                    "validation":{"status":"failed","tests":["integration"]},
                    "commits":[{"sha":"1234567"}],
                }
            }
        }],
        "artifacts":[],
    })

    assert outcome["available"] is True
    assert outcome["summary"] == "Validation failed on integration suite."
    assert outcome["validation_status"] == "failed"
    assert outcome["validation_tests"] == ["integration"]
    assert outcome["commit_shas"] == ["1234567"]
    assert outcome["completed_at"] == "2026-09-25T18:41:00+00:00"

    empty = _outcome_from_workflow(None)
    assert empty == {
        "available":False,
        "workflow_status":None,
        "summary":None,
        "validation_status":None,
        "validation_tests":[],
        "commit_shas":[],
        "artifact_count":0,
        "artifact_names":[],
        "pull_request":None,
        "completed_at":None,
    }
