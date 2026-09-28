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



def test_build_rollback_plan_carries_non_blocking_bisect_range():
    plan = build_rollback_plan(
        repository="o/a",
        merge_sha="b" * 40,
        known_good_sha="a" * 40,
        failure_summary="regression",
    )

    assert plan["strategy"] == "compensating-pr"
    assert plan["diagnostic"] == {
        "schema_version":"production-os/regression-bisect-request/v1",
        "strategy":"regression-bisect",
        "known_good_sha":"a" * 40,
        "known_bad_sha":"b" * 40,
        "requires_reproduction_command":True,
        "blocking":False,
    }
    assert "production-os regression-bisect" in plan["instruction"]
    assert "Do not delay an urgent compensating rollback" in plan["instruction"]


def test_build_rollback_plan_rejects_invalid_known_good_sha():
    with pytest.raises(ValueError, match="known_good_sha must be a full commit sha"):
        build_rollback_plan(
            repository="o/a",
            merge_sha="b" * 40,
            known_good_sha="abc123",
        )
