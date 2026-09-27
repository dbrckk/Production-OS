import pytest

from production_os.rollback_plan import build_rollback_plan


def test_build_rollback_plan_is_compensating_and_preserves_history():
    plan = build_rollback_plan(
        repository="o/a",
        merge_sha="a" * 40,
        failure_summary="post-merge integration regression",
        ci={
            "workflow":"CI",
            "job":"tests",
            "step":"pytest",
            "log_excerpt":"FAILED tests/test_app.py::test_x",
        },
    )

    assert plan["strategy"] == "compensating-pr"
    assert plan["history_rewrite_allowed"] is False
    assert plan["force_push_allowed"] is False
    assert plan["requires_green_ci"] is True
    assert "Do not reset" in plan["instruction"]
    assert "Preserve later compatible changes" in plan["instruction"]
    assert "CI / tests / pytest" in plan["instruction"]
    assert "FAILED tests/test_app.py::test_x" in plan["instruction"]
    assert "open a pull request" in plan["instruction"]


def test_build_rollback_plan_rejects_unpinned_merge_commit():
    with pytest.raises(ValueError, match="full commit sha"):
        build_rollback_plan(
            repository="o/a",
            merge_sha="abc1234",
        )
