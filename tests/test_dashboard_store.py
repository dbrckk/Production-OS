from __future__ import annotations

from production_os.dashboard_store import DashboardStore
from production_os.sqlite_backend import SQLiteBackend


def _store(tmp_path): return DashboardStore(SQLiteBackend(tmp_path/"db.sqlite"))


def _sample_job():
    return {"key":"job-1","repository":"dbrckk/example","delivery_attempt":1,
            "payload":{"workflow_id":"wf-1","workflow_task_id":"task-1"}}


def test_execution_lifecycle_and_attempt_identity(tmp_path):
    store=_store(tmp_path); job=_sample_job()
    first=store.start_execution(job,"worker-a")
    duplicate=store.start_execution(job,"worker-a")
    assert first["id"] == duplicate["id"] == "job-1:1"
    assert store.execution_count("job-1") == 1
    live=store.update_live_execution("job-1","worker-a",{"stage":"tests","progress":50,"usage":{"total_tokens":10}})
    assert live["progress_percent"] == 50
    result={"usage":{"api_calls":1,"input_tokens":4,"cached_input_tokens":1,"output_tokens":3,
                     "reasoning_tokens":2,"total_tokens":10},"commits":{"shas":["a"*40]}}
    done=store.finish_execution("job-1","worker-a",status="succeeded",duration_seconds=12,result=result)
    assert done["status"] == "succeeded" and done["commit_count"] == 1
    retry={**job,"delivery_attempt":2}
    assert store.start_execution(retry,"worker-a")["id"] == "job-1:2"


def test_live_progress_cannot_move_backward_in_same_stage(tmp_path):
    store=_store(tmp_path); store.start_execution(_sample_job(),"worker-a")
    store.update_live_execution("job-1","worker-a",{"stage":"tests","progress":60})
    try: store.update_live_execution("job-1","worker-a",{"stage":"tests","progress":40})
    except ValueError: pass
    else: raise AssertionError("expected ValueError")


def test_finish_execution_is_idempotent(tmp_path):
    store=_store(tmp_path); store.start_execution(_sample_job(),"worker-a")
    first=store.finish_execution("job-1","worker-a",status="succeeded",duration_seconds=2,result={})
    second=store.finish_execution("job-1","worker-a",status="failed",duration_seconds=9,result={})
    assert second["status"] == first["status"] == "succeeded"


def test_log_cursor_is_deterministic(tmp_path):
    store=_store(tmp_path)
    store.append_logs("worker-a",[
        {"id":"a","created_at":"2026-09-22T10:00:00+00:00","message":"first"},
        {"id":"b","created_at":"2026-09-22T10:00:00+00:00","message":"second"},
    ])
    rows=store.logs_for_worker("worker-a",limit=1)
    assert rows[0]["id"] == "b"
    older=store.logs_for_worker("worker-a",after="b",limit=10)
    assert [x["id"] for x in older] == ["a"]


def test_snapshot_roundtrip_and_usage_query(tmp_path):
    store=_store(tmp_path)
    repo=store.save_repository_snapshot({"id":"r1","repository":"dbrckk/example","default_branch":"main",
        "production_os_commits":1,"github_commits":2,"snapshot_json":{"ok":True},"captured_at":"2026-09-22T10:00:00+00:00"})
    assert repo["snapshot"]["ok"] is True
    progress=store.save_progress_snapshot({"id":"p1","repository":"dbrckk/example","confidence":"high",
        "evidence_json":{"a":1},"remaining_work_json":[],"blockers_json":[],"calculation_version":"v1",
        "captured_at":"2026-09-22T10:00:00+00:00"})
    assert progress["evidence"] == {"a":1}


def test_append_logs_generates_collision_safe_ids(tmp_path):
    store=_store(tmp_path); at="2026-09-22T10:00:00+00:00"
    rows=store.append_logs("worker-a",[{"created_at":at,"message":"same"},{"created_at":at,"message":"same"}])
    assert rows[0]["id"] != rows[1]["id"]
    assert len(store.logs_for_worker("worker-a")) == 2


def test_finish_execution_ignores_malformed_commit_shas(tmp_path):
    store=_store(tmp_path); store.start_execution(_sample_job(),"worker-a"); valid="a"*40
    row=store.finish_execution("job-1","worker-a",status="succeeded",duration_seconds=1,result={
        "commits":{"count":5,"shas":[valid,valid,"not-a-sha","b"*39,"G"*40,None,123]}})
    assert row["commit_count"] == 1
    assert row["commit_shas"] == [valid]


def test_progress_snapshot_order_is_deterministic_when_timestamps_tie(tmp_path):
    store=_store(tmp_path); captured="2026-09-24T04:00:00+00:00"
    base={"repository":"dbrckk/example","captured_at":captured,"calculation_version":"project-progress/v1","confidence":"low"}
    store.save_progress_snapshot({**base,"id":"snapshot-a","project_progress":10})
    store.save_progress_snapshot({**base,"id":"snapshot-z","project_progress":20})
    assert store.latest_progress_snapshot("dbrckk/example")["id"] == "snapshot-z"
    assert [row["id"] for row in store.progress_history("dbrckk/example")] == ["snapshot-z","snapshot-a"]
