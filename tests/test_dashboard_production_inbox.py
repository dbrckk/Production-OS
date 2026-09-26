from __future__ import annotations

from production_os.control_plane import ControlPlane


def _production_fixture(tmp_path):
    control = ControlPlane(str(tmp_path / "production-inbox.sqlite"))
    queued = control.managed_projects.create(
        repository="dbrckk/inbox-queued", final_goal="Stay queued.",
        token_budget=30000, agent_preference="auto",
    )
    review = control.managed_projects.create(
        repository="dbrckk/inbox-review", final_goal="Become reviewable.",
        token_budget=30000, agent_preference="auto",
    )
    control.workflows.record_result(
        review["current_workflow_id"], "implementation", succeeded=True,
        result={"summary":"review result","validation":{"status":"passed","tests":["unit"]}},
    )
    attention = control.managed_projects.create(
        repository="dbrckk/inbox-attention", final_goal="Be cancelled.",
        token_budget=30000, agent_preference="auto",
    )
    cancelled = control.dashboard.cancel_production(
        attention["project_id"], requested_by="operator:test",
    )
    assert cancelled["status"] == "cancelled"
    done = control.managed_projects.create(
        repository="dbrckk/inbox-done", final_goal="Be done.",
        token_budget=30000, agent_preference="auto",
    )
    control.workflows.record_result(
        done["current_workflow_id"], "implementation", succeeded=True,
        result={"summary":"done result","validation":{"status":"passed"}},
    )
    control.managed_projects.mark_done(done["project_id"], approved_by="operator:test")
    return control, queued, review, attention, done


def test_production_inbox_aggregates_live_review_attention_and_done(tmp_path):
    control, queued, review, attention, done = _production_fixture(tmp_path)
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
    assert summary["total"] == 4


def test_production_inbox_filters_server_side_without_changing_totals(tmp_path):
    control, queued, review, attention, done = _production_fixture(tmp_path)

    active = control.dashboard.production_inbox(limit=50, category="active")
    assert [row["project_id"] for row in active["items"]] == [queued["project_id"]]
    assert active["filter"] == "active"
    assert active["summary"]["visible"] == 1
    assert active["summary"]["total"] == 4
    assert active["summary"]["review_required"] == 1

    review_payload = control.dashboard.production_inbox(limit=50, category="review")
    assert [row["project_id"] for row in review_payload["items"]] == [review["project_id"]]

    problems = control.dashboard.production_inbox(limit=50, category="problems")
    assert [row["project_id"] for row in problems["items"]] == [attention["project_id"]]

    completed = control.dashboard.production_inbox(limit=50, category="completed")
    assert [row["project_id"] for row in completed["items"]] == [done["project_id"]]


def test_production_inbox_rejects_unknown_filter(tmp_path):
    control = ControlPlane(str(tmp_path / "production-inbox-filter.sqlite"))
    try:
        control.dashboard.production_inbox(category="surprise")
    except ValueError as exc:
        assert str(exc) == "invalid production inbox filter"
    else:
        raise AssertionError("unknown production inbox filter must be rejected")


def test_production_inbox_orders_operator_decisions_before_live_and_done(tmp_path):
    control, queued, review, attention, done = _production_fixture(tmp_path)
    payload = control.dashboard.production_inbox(limit=50)
    phases = [row["runtime"]["phase"] for row in payload["items"]]
    assert phases == ["needs_attention", "review_required", "queued", "done"]


def test_production_inbox_respects_response_limit_after_priority_sort(tmp_path):
    control = ControlPlane(str(tmp_path / "production-inbox-limit.sqlite"))
    for index in range(4):
        control.managed_projects.create(
            repository=f"dbrckk/inbox-{index}", final_goal=f"Production {index}",
            token_budget=30000, agent_preference="auto",
        )

    payload = control.dashboard.production_inbox(limit=2)
    assert len(payload["items"]) == 2
    assert payload["summary"]["visible"] == 2
    assert payload["summary"]["total"] == 4

def test_production_inbox_orders_recent_activity_first_within_same_priority(tmp_path):
    control = ControlPlane(str(tmp_path / "production-inbox-recency.sqlite"))
    older = control.managed_projects.create(
        repository="dbrckk/inbox-older",
        final_goal="Older active production.",
        token_budget=30000,
        agent_preference="auto",
    )
    newer = control.managed_projects.create(
        repository="dbrckk/inbox-newer",
        final_goal="Newer active production.",
        token_budget=30000,
        agent_preference="auto",
    )
    with control.backend.transaction() as db:
        db.execute(
            "UPDATE managed_projects SET updated_at=? WHERE id=?",
            ("2026-01-01T00:00:00+00:00", older["project_id"]),
        )
        db.execute(
            "UPDATE managed_projects SET updated_at=? WHERE id=?",
            ("2026-02-01T00:00:00+00:00", newer["project_id"]),
        )

    payload = control.dashboard.production_inbox(limit=50, category="active")

    assert [row["project_id"] for row in payload["items"]] == [
        newer["project_id"],
        older["project_id"],
    ]

def test_production_inbox_search_matches_repository_goal_and_project_id(tmp_path):
    control, queued, review, attention, done = _production_fixture(tmp_path)

    by_repository = control.dashboard.production_inbox(
        limit=50,
        search="INBOX-REVIEW",
    )
    assert [row["project_id"] for row in by_repository["items"]] == [
        review["project_id"]
    ]
    assert by_repository["search"] == "INBOX-REVIEW"
    assert by_repository["summary"]["matching"] == 1
    assert by_repository["summary"]["total"] == 4

    by_goal = control.dashboard.production_inbox(
        limit=50,
        search="be cancelled",
    )
    assert [row["project_id"] for row in by_goal["items"]] == [
        attention["project_id"]
    ]

    by_id = control.dashboard.production_inbox(
        limit=50,
        search=done["project_id"],
    )
    assert [row["project_id"] for row in by_id["items"]] == [
        done["project_id"]
    ]


def test_production_inbox_recent_sort_ignores_priority_but_keeps_filter(tmp_path):
    control, queued, review, attention, done = _production_fixture(tmp_path)

    # Prime reconciliation first so timestamp edits below represent the
    # externally visible project activity order rather than status migration.
    control.dashboard.production_inbox(limit=50)

    timestamps = {
        queued["project_id"]:"2026-01-04T00:00:00+00:00",
        review["project_id"]:"2026-01-03T00:00:00+00:00",
        attention["project_id"]:"2026-01-02T00:00:00+00:00",
        done["project_id"]:"2026-01-01T00:00:00+00:00",
    }
    with control.backend.transaction() as db:
        for project_id, updated_at in timestamps.items():
            db.execute(
                "UPDATE managed_projects SET updated_at=? WHERE id=?",
                (updated_at, project_id),
            )

    recent = control.dashboard.production_inbox(limit=50, sort="recent")
    assert recent["sort"] == "recent"
    assert [row["project_id"] for row in recent["items"]] == [
        queued["project_id"],
        review["project_id"],
        attention["project_id"],
        done["project_id"],
    ]

    review_only = control.dashboard.production_inbox(
        limit=50,
        category="review",
        sort="recent",
    )
    assert [row["project_id"] for row in review_only["items"]] == [
        review["project_id"]
    ]


def test_production_inbox_rejects_unknown_sort(tmp_path):
    control = ControlPlane(str(tmp_path / "production-inbox-sort.sqlite"))
    try:
        control.dashboard.production_inbox(sort="oldest")
    except ValueError as exc:
        assert str(exc) == "invalid production inbox sort"
    else:
        raise AssertionError("unknown production inbox sort must be rejected")

