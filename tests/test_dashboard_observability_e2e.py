from __future__ import annotations

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
        "observability-e2e","dbrckk/example",
        [WorkflowTaskSpec(task_id="build",title="Build",payload={},estimated_minutes=30)],
    )
    control.workers.register("worker-a",["python"],1)
    control.workflows.dispatch_ready(workflow["id"],limit=1)
    job=control.queue.claim_next("worker-a",capabilities=["python"])
    job=control.queue.ack(job["key"],"worker-a")
    control.dashboard_store.start_execution(job,"worker-a")
    control.dashboard_store.update_live_execution(job["key"],"worker-a",{
        "stage":"implementation","progress":60,"usage":{"total_tokens":500},
    })
    result={"usage":{"total_tokens":900,"providers":[{
        "provider":"test-provider","model":"test-model","api_calls":1,
        "input_tokens":700,"cached_input_tokens":0,"output_tokens":200,
        "reasoning_tokens":0,"total_tokens":900,
    }]},"commits":{"count":1,"shas":["a"*40]}}
    control.dashboard_store.finish_execution(
        job["key"],"worker-a",status="succeeded",duration_seconds=12,result=result,
    )
    usage=control.dashboard.project_usage("dbrckk/example","all")
    assert usage["totals"]["total_tokens"] == 900
    commits=control.dashboard.project_commits("dbrckk/example","all")
    assert commits["production_os"] == 1
    detail=control.dashboard.worker_detail("worker-a")
    assert detail["executions"][0]["status"] == "succeeded"
