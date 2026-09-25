from types import SimpleNamespace

from production_os.dashboard_service import DashboardService


class ManagedProjects:
    def __init__(self, rows):
        self.rows = rows

    def list(self, *, limit=100):
        return self.rows[:limit]


def test_attention_prioritizes_failures_reviews_blocked_jobs_and_incidents():
    managed = [
        {
            "project_id":"project-failed",
            "repository":"dbrckk/failing",
            "final_goal":"Ship failing project",
            "status":"NEEDS_ATTENTION",
            "updated_at":"2026-09-25T18:00:00+00:00",
            "completed_at":None,
            "current_workflow":{"status":"failed"},
        },
        {
            "project_id":"project-review",
            "repository":"dbrckk/review",
            "final_goal":"Review completed production",
            "status":"REVIEW_REQUIRED",
            "updated_at":"2026-09-25T18:01:00+00:00",
            "completed_at":None,
            "current_workflow":{"status":"succeeded"},
        },
        {
            "project_id":"project-done",
            "repository":"dbrckk/done",
            "final_goal":"Finished production",
            "status":"DONE",
            "updated_at":"2026-09-25T17:59:00+00:00",
            "completed_at":"2026-09-25T17:59:00+00:00",
            "current_workflow":{"status":"succeeded"},
        },
    ]
    control = SimpleNamespace(
        dashboard_store=None,
        managed_projects=ManagedProjects(managed),
    )
    service = DashboardService(control)
    service.autopilot_queue = lambda limit=50: {
        "jobs":[{
            "job_key":"job-blocked",
            "repository":"dbrckk/blocked",
            "task":"blocked task",
            "wait_reason":"no_online_worker",
            "created_at":"2026-09-25T18:02:00+00:00",
        }]
    }
    service.incidents = lambda limit=100, status=None: {
        "incidents":[{
            "id":"incident-1",
            "status":"open",
            "severity":"high",
            "title":"Worker unavailable",
            "message":"No healthy worker can run the queue.",
            "target_type":"worker",
            "target_id":"worker-a",
            "last_seen_at":"2026-09-25T18:03:00+00:00",
            "playbook":{
                "suggestions":[{
                    "action":"kick",
                    "worker_id":"worker-a",
                    "job_key":None,
                    "availability":"fallback",
                }]
            },
        }]
    }

    payload = service.attention(limit=50)

    assert payload["schema_version"] == "production-os/dashboard-attention/v1"
    assert payload["summary"] == {
        "action_required":4,
        "incidents":1,
        "projects_to_review":1,
        "projects_needing_attention":1,
        "blocked_jobs":1,
        "blocked_jobs_shown":1,
        "recently_completed":1,
    }
    assert payload["items"][0]["kind"] == "incident"
    kinds = [item["kind"] for item in payload["items"]]
    assert "validation_failed" in kinds
    assert "project_review" in kinds
    assert "blocked_job" in kinds
    assert kinds[-1] == "completed_project"
    assert payload["items"][-1]["action_required"] is False

    incident = next(item for item in payload["items"] if item["kind"] == "incident")
    assert incident["incident_id"] == "incident-1"
    assert [action["name"] for action in incident["actions"]] == [
        "acknowledge",
        "playbook",
    ]
    assert incident["actions"][1]["control_action"] == "kick"

    failed = next(item for item in payload["items"] if item["kind"] == "validation_failed")
    assert failed["actions"] == [{"name":"verify","label":"Retester"}]

    review = next(item for item in payload["items"] if item["kind"] == "project_review")
    assert review["actions"] == [
        {"name":"verify","label":"Retester"},
        {"name":"complete","label":"Valider DONE"},
    ]


def test_attention_limit_is_bounded_and_completed_items_are_informational():
    managed = [
        {
            "project_id":f"done-{index}",
            "repository":f"dbrckk/done-{index}",
            "final_goal":"Done",
            "status":"DONE",
            "updated_at":f"2026-09-25T17:5{index}:00+00:00",
            "completed_at":f"2026-09-25T17:5{index}:00+00:00",
            "current_workflow":{"status":"succeeded"},
        }
        for index in range(3)
    ]
    control = SimpleNamespace(
        dashboard_store=None,
        managed_projects=ManagedProjects(managed),
    )
    service = DashboardService(control)
    service.autopilot_queue = lambda limit=50: {"jobs":[]}
    service.incidents = lambda limit=100, status=None: {"incidents":[]}

    payload = service.attention(limit=2)

    assert len(payload["items"]) == 2
    assert payload["summary"]["action_required"] == 0
    assert payload["summary"]["recently_completed"] == 3
    assert all(item["action_required"] is False for item in payload["items"])

def test_attention_caps_blocked_job_cards_but_preserves_total_count():
    control = SimpleNamespace(
        dashboard_store=None,
        managed_projects=ManagedProjects([]),
    )
    service = DashboardService(control)
    service.incidents = lambda limit=100, status=None: {"incidents":[]}
    service.autopilot_queue = lambda limit=50: {
        "jobs":[
            {
                "job_key":f"job-{index}",
                "repository":"dbrckk/noisy",
                "task":f"blocked {index}",
                "wait_reason":"capacity_full",
                "created_at":f"2026-09-25T18:{index:02d}:00+00:00",
            }
            for index in range(12)
        ]
    }

    payload = service.attention(limit=50)

    blocked = [item for item in payload["items"] if item["kind"] == "blocked_job"]
    assert len(blocked) == 8
    assert payload["summary"]["blocked_jobs"] == 12
    assert payload["summary"]["blocked_jobs_shown"] == 8
    assert payload["summary"]["action_required"] == 12

