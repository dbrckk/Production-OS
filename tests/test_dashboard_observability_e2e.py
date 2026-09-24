from __future__ import annotations

import json

from production_os.api_auth import TokenAuthorizer, token_digest
from production_os.control_plane import ControlPlane
from production_os.workflow_engine import WorkflowTaskSpec


def _auth():
    return TokenAuthorizer([
        {"name":"worker-a","role":"worker","sha256":token_digest("worker-token")},
        {"name":"viewer","role":"viewer","sha256":token_digest("viewer-token")},
    ])


def test_observability_lifecycle_uses_final_usage_and_attributed_commits(tmp_path):
    control=ControlPlane(str(tmp_path/"db.sqlite"),authorizer=_auth())
    workflow=control.workflows.create(
        name="observability-e2e", repository="dbrckk/example",
        tasks=[WorkflowTaskSpec(task_id="build",title="Build",payload={},estimated_minutes=30)],
    )
    control.workers.register("worker-a",["python"],1)
    control.workflows.dispatch_ready(workflow["id"],limit=1)
    job=control.queue.claim_next("worker-a",capabilities=["python"])
    job=control.queue.ack(job["key"],"worker-a")
    control.dashboard_store.start_execution(job,"worker-a")
    control.dashboard_store.update_live_execution(job["key"],"worker-a",{"stage":"implementation","progress":60,"usage":{"total_tokens":500}})
    result={"usage":{"total_tokens":900,"providers":[{"provider":"test-provider","model":"test-model","api_calls":1,"input_tokens":700,"cached_input_tokens":0,"output_tokens":200,"reasoning_tokens":0,"total_tokens":900}]},"commits":{"count":1,"shas":["a"*40]}}
    control.dashboard_store.finish_execution(job["key"],"worker-a",status="succeeded",duration_seconds=12,result=result)
    assert control.dashboard.project_usage("dbrckk/example","all")["totals"]["total_tokens"] == 900
    assert control.dashboard.project_commits("dbrckk/example","all")["production_os"] == 1
    assert control.dashboard.worker_detail("worker-a")["executions"][0]["status"] == "succeeded"


def test_attributed_commit_count_deduplicates_sha_across_executions(tmp_path):
    control=ControlPlane(str(tmp_path/"db.sqlite"),authorizer=_auth()); store=control.dashboard_store
    for index in (1,2):
        job={"key":f"job-{index}","repository":"dbrckk/example","task":"ship","delivery_attempt":1,"payload":{}}
        store.start_execution(job,"worker-a")
        store.finish_execution(job["key"],"worker-a",status="succeeded",duration_seconds=1,result={"commits":{"shas":["b"*40]}})
    assert control.dashboard.project_commits("dbrckk/example","all")["production_os"] == 1


def test_secret_like_log_values_are_redacted_before_persistence(tmp_path):
    control=ControlPlane(str(tmp_path/"db.sqlite"),authorizer=_auth())
    control.dashboard_store.append_logs("worker-a",[{"message":"Authorization: Bearer super-secret-token","metadata":{"api_key":"abc123","nested":{"password":"pw"}}}])
    row=control.dashboard_store.logs_for_worker("worker-a")[0]
    assert "super-secret-token" not in row["message"]
    assert row["metadata"]["api_key"] == "[REDACTED]"
    assert row["metadata"]["nested"]["password"] == "[REDACTED]"


def test_project_progress_exposes_weighted_current_workflow(tmp_path):
    control=ControlPlane(str(tmp_path/"db.sqlite"),authorizer=_auth())
    workflow=control.workflows.create(name="progress-e2e",repository="dbrckk/example",tasks=[WorkflowTaskSpec(task_id="done",title="Done",payload={},estimated_minutes=10),WorkflowTaskSpec(task_id="todo",title="Todo",payload={},estimated_minutes=30)])
    with control.backend.transaction() as db:
        db.execute("UPDATE workflow_tasks SET status='succeeded' WHERE workflow_id=? AND task_id=?",(workflow["id"],"done"))
    progress=control.dashboard.project_progress("dbrckk/example")
    assert progress["production"]["percent"] == 25.0
    assert progress["estimate"]["calculation_version"] == "project-progress/v1"
    assert progress["estimate"]["confidence"] in {"low","medium","high"}


def test_activity_worker_filter_uses_event_payload(tmp_path):
    control=ControlPlane(str(tmp_path/"db.sqlite"),authorizer=_auth())
    with control.backend.transaction() as db:
        control.backend.append_event(db,"job.completed",{"worker_id":"worker-a"},repository="dbrckk/example",task_key_value="a")
        control.backend.append_event(db,"job.completed",{"worker_id":"worker-b"},repository="dbrckk/example",task_key_value="b")
    rows=control.dashboard.activity(worker_id="worker-a")["events"]
    assert len(rows) == 1 and rows[0]["payload"]["worker_id"] == "worker-a"


def test_project_history_marks_legacy_backfill_partial(tmp_path):
    control=ControlPlane(str(tmp_path/"db.sqlite"),authorizer=_auth())
    with control.backend.transaction() as db:
        db.execute("INSERT INTO execution_history(repository,task,worker_id,duration_seconds,succeeded,capabilities_json,created_at) VALUES(?,?,?,?,?,?,?)",("dbrckk/example","legacy","worker-a",3.5,1,"[]","2026-09-01T00:00:00+00:00"))
    history=control.dashboard.project_history("dbrckk/example")
    assert history["history_coverage"] == "partial"
    assert history["legacy_executions"][0]["worker_id"] == "worker-a"


def test_project_usage_backfills_legacy_workflow_result_usage(tmp_path):
    control=ControlPlane(str(tmp_path/"db.sqlite"),authorizer=_auth())
    workflow=control.workflows.create(name="legacy-usage",repository="dbrckk/example",tasks=[WorkflowTaskSpec(task_id="done",title="Done",payload={})])
    result_json=json.dumps({"usage":{"providers":[{"provider":"legacy-provider","model":"legacy-model","api_calls":1,"input_tokens":200,"cached_input_tokens":0,"output_tokens":100,"reasoning_tokens":0,"total_tokens":300}]}})
    with control.backend.transaction() as db:
        db.execute("UPDATE workflow_tasks SET status='succeeded', result_json=?, updated_at=? WHERE workflow_id=? AND task_id=?",(result_json,"2026-09-01T00:00:00+00:00",workflow["id"],"done"))
    usage=control.dashboard.project_usage("dbrckk/example","all")
    assert usage["totals"]["api_calls"] == 1 and usage["totals"]["total_tokens"] == 300
    assert usage["history_coverage"] == "partial"


def test_project_progress_persists_snapshot_only_when_meaningful_state_changes(tmp_path):
    control=ControlPlane(str(tmp_path/"db.sqlite"),authorizer=_auth())
    workflow=control.workflows.create(name="snapshot-progress",repository="dbrckk/example",tasks=[WorkflowTaskSpec(task_id="build",title="Build",payload={},estimated_minutes=10)])
    first=control.dashboard.project_progress("dbrckk/example"); second=control.dashboard.project_progress("dbrckk/example")
    history=control.dashboard_store.progress_history("dbrckk/example")
    assert first["estimate"]["calculation_version"] == "project-progress/v1"
    assert second["production"]["percent"] == first["production"]["percent"]
    assert len(history) == 1
    with control.backend.transaction() as db:
        db.execute("UPDATE workflow_tasks SET status='succeeded' WHERE workflow_id=? AND task_id=?",(workflow["id"],"build"))
    changed=control.dashboard.project_progress("dbrckk/example"); history=control.dashboard_store.progress_history("dbrckk/example")
    assert changed["production"]["percent"] == 100.0
    assert len(history) == 2 and history[0]["production_progress"] == 100.0
    assert "evidence" in changed["estimate"]


def test_project_progress_persists_when_auditable_evidence_changes(tmp_path):
    control=ControlPlane(str(tmp_path/"db.sqlite"),authorizer=_auth())
    control.workflows.create(name="evidence-progress",repository="dbrckk/example",tasks=[WorkflowTaskSpec(task_id="build",title="Build",payload={},estimated_minutes=10)])
    control.dashboard.project_progress("dbrckk/example")
    before=control.dashboard_store.progress_history("dbrckk/example")
    control.dashboard_store.save_repository_snapshot({"id":"repo-snapshot-1","repository":"dbrckk/example","ci_status":"success","tests_detected":10,"tests_passing":10,"tests_failing":0,"captured_at":"2026-09-24T01:00:00+00:00"})
    control.dashboard.project_progress("dbrckk/example")
    after=control.dashboard_store.progress_history("dbrckk/example")
    assert len(before) == 1
    assert len(after) == 2
    assert after[0]["evidence"]["repository"]["ci_status"] == "success"


def test_project_progress_snapshot_persists_selected_profile(tmp_path):
    control=ControlPlane(str(tmp_path/"db.sqlite"),authorizer=_auth())
    control.workflows.create(name="profile-progress",repository="dbrckk/example",tasks=[WorkflowTaskSpec(task_id="build",title="Build",payload={},estimated_minutes=10)])
    control.dashboard.project_progress("dbrckk/example")
    snapshot=control.dashboard_store.latest_progress_snapshot("dbrckk/example")
    assert snapshot["profile"] == "generic"
