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



def test_finish_execution_persists_primary_provider_and_aggregates_usage(tmp_path):
    store = _store(tmp_path)
    store.start_execution(_sample_job(), "worker-a")
    done = store.finish_execution(
        "job-1",
        "worker-a",
        status="succeeded",
        duration_seconds=3,
        result={
            "usage":{
                "providers":[
                    {
                        "provider":"cloudflare",
                        "model":"qwen-code",
                        "api_calls":1,
                        "input_tokens":60,
                        "output_tokens":40,
                        "total_tokens":100,
                        "estimated_cost_usd":0.0,
                        "pricing_catalog_version":"free-v1",
                    },
                    {
                        "provider":"pollinations",
                        "model":"fallback-code",
                        "api_calls":2,
                        "input_tokens":10,
                        "output_tokens":10,
                        "total_tokens":20,
                        "estimated_cost_usd":0.0,
                        "pricing_catalog_version":"free-v1",
                    },
                ],
            },
        },
    )

    assert done["provider"] == "cloudflare"
    assert done["model"] == "qwen-code"
    assert done["api_calls"] == 3
    assert done["input_tokens"] == 70
    assert done["output_tokens"] == 50
    assert done["total_tokens"] == 120
    assert done["estimated_cost_usd"] == 0.0
    assert done["pricing_catalog_version"] == "free-v1"


def test_finish_execution_top_level_usage_overrides_provider_summary(tmp_path):
    store = _store(tmp_path)
    store.start_execution(_sample_job(), "worker-a")
    done = store.finish_execution(
        "job-1",
        "worker-a",
        status="succeeded",
        duration_seconds=1,
        result={
            "usage":{
                "provider":"router",
                "model":"selected-model",
                "api_calls":9,
                "total_tokens":999,
                "estimated_cost_usd":1.25,
                "pricing_catalog_version":"catalog-v2",
                "providers":[
                    {
                        "provider":"other",
                        "model":"other-model",
                        "api_calls":1,
                        "total_tokens":100,
                        "estimated_cost_usd":0.2,
                        "pricing_catalog_version":"catalog-v1",
                    },
                ],
            },
        },
    )

    assert done["provider"] == "router"
    assert done["model"] == "selected-model"
    assert done["api_calls"] == 9
    assert done["total_tokens"] == 999
    assert done["estimated_cost_usd"] == 1.25
    assert done["pricing_catalog_version"] == "catalog-v2"


def test_finish_execution_does_not_invent_partial_cost_or_catalog(tmp_path):
    store = _store(tmp_path)
    store.start_execution(_sample_job(), "worker-a")
    done = store.finish_execution(
        "job-1",
        "worker-a",
        status="succeeded",
        duration_seconds=1,
        result={
            "usage":{
                "providers":[
                    {
                        "provider":"one",
                        "model":"m1",
                        "total_tokens":50,
                        "estimated_cost_usd":0.1,
                        "pricing_catalog_version":"v1",
                    },
                    {
                        "provider":"two",
                        "model":"m2",
                        "total_tokens":50,
                        "estimated_cost_usd":None,
                        "pricing_catalog_version":"v2",
                    },
                    "malformed",
                ],
            },
        },
    )

    assert done["provider"] == "one"
    assert done["model"] == "m1"
    assert done["estimated_cost_usd"] is None
    assert done["pricing_catalog_version"] is None
