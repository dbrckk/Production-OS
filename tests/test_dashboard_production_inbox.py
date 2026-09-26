from __future__ import annotations

from production_os.control_plane import ControlPlane


def test_production_inbox_aggregates_live_review_attention_and_done(tmp_path):
    control = ControlPlane(str(tmp_path / "production-inbox.sqlite"))

    queued = control.managed_projects.create(
        repository="dbrckk/inbox-queued",
        final_goal="Stay queued.",
        token_budget=30000,
        agent_preference="auto",
    )

    review = control.managed_projects.create(
        repository="dbrckk/inbox-review",
        final_goal="Become reviewable.",
        token_budget=30000,
        agent_preference="auto",
    )
    control.workflows.record_result(
        review["current_workflow_id"],
        "implementation",
        succeeded=True,
        result={
            "summary":"review result",
            "validation":{"status":"passed","tests":["unit"]},
        },
    )

    attention = control.managed_projects.create(
        repository="dbrckk/inbox-attention",
        final_goal="Be cancelled.",
        token_budget=30000,
        agent_preference="auto",
    )
    cancelled = control.dashboard.cancel_production(
        attention["project_id"],
        requested_by="operator:test",
    )
    assert cancelled["status"] == "cancelled"

    done = control.managed_projects.create(
        repository="dbrckk/inbox-done",
        final_goal="Be done.",
        token_budget=30000,
        agent_preference="auto",
    )
    control.workflows.record_result(
        done["current_workflow_id"],
        "implementation",
        succeeded=True,
        result={"summary":"done result","validation":{"status":"passed"}},
    )
    control.managed_projects.mark_done(
        done["project_id"],
        approved_by="operator:test",
    )

    payload = control.dashboard.production_inbox(limit=50)

    assert payload["schema_version"] == "production-os/production-inbox/v1"
    by_id = {item["project_id"]:item for item in payload["items"]}
    assert by_id[queued["project_id"]]["runtime"]["phase"] == "queued"
    assert by_id[review["project_id"]]["runtime"]["phase"] == "review_required"
    assert by_id[attention["project_id"]]["runtime"]["phase"] == "needs_attention"
    assert by_id[done["project_id"]]["runtime"]["phase"] == "done"
    assert by_id[review["project_id"]]["outcome"]["validation_status"] == "passed"

    summary = payload["summary"]
    assert summary["active"] == 1
    assert summary["queued"] == 1
    assert summary["review_required"] == 1
    assert summary["needs_attention"] == 1
    assert summary["done"] == 1
    assert summary["visible"] == 4


def test_production_inbox_respects_response_limit(tmp_path):
    control = ControlPlane(str(tmp_path / "production-inbox-limit.sqlite"))
    for index in range(4):
        control.managed_projects.create(
            repository=f"dbrckk/inbox-{index}",
            final_goal=f"Production {index}",
            token_budget=30000,
            agent_preference="auto",
        )

    payload = control.dashboard.production_inbox(limit=2)
    assert len(payload["items"]) == 2
    assert payload["summary"]["visible"] == 2
