from __future__ import annotations

from production_os.project_progress import (
    CONFIDENCE_HIGH,
    CONFIDENCE_MEDIUM,
    ProjectProgressEngine,
    workflow_progress,
)


def test_workflow_progress_is_weighted_by_estimated_minutes():
    workflow={"tasks":[{"status":"succeeded","estimated_minutes":10},{"status":"running","estimated_minutes":30}]}
    result=workflow_progress(workflow)
    assert result["percent"]==25.0
    assert result["completed_weight"]==10.0
    assert result["total_weight"]==40.0


def test_zero_minute_virtual_barrier_does_not_distort_progress():
    workflow={"tasks":[{"status":"succeeded","estimated_minutes":10},{"status":"pending","estimated_minutes":0}]}
    assert workflow_progress(workflow)["percent"]==100.0


def test_terminal_semantics_and_no_executable_weight():
    assert workflow_progress({"tasks":[{"status":"impact_skipped","estimated_minutes":5}]})["percent"]==100.0
    for status in ("failed","blocked","cancelled"):
        assert workflow_progress({"tasks":[{"status":status,"estimated_minutes":5}]})["percent"]==0.0
    assert workflow_progress({"tasks":[{"status":"pending","estimated_minutes":0}]})["percent"] is None


def test_backend_profile_marks_ui_and_assets_not_applicable():
    engine=ProjectProgressEngine()
    result=engine.calculate("dbrckk/api",{"profile":"backend","dimensions":{
        "code":{"score":80,"evidence":4,"fresh":True},
        "tests":{"score":70,"evidence":3,"fresh":True},
        "stability":{"score":90,"evidence":3,"fresh":True},
        "release":{"score":50,"evidence":2,"fresh":True},
    }})
    assert result["components"]["ui_ux"]["status"]=="not_applicable"
    assert result["components"]["assets"]["status"]=="not_applicable"
    assert 0<=result["score"]<=100


def test_confidence_thresholds_are_stable():
    assert CONFIDENCE_HIGH==0.80
    assert CONFIDENCE_MEDIUM==0.50
