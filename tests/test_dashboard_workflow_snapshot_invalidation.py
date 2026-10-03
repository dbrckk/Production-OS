from production_os.dashboard_ui import DASHBOARD_HTML


def test_workflow_snapshot_invalidation_replaces_inflight_generation():
    block = DASHBOARD_HTML.split(
        "let workflowsSnapshotCache=null;", 1
    )[1].split("function selectedLaunchRepository(){", 1)[0]

    assert "let workflowsSnapshotGeneration=0;" in block

    invalidate = block.split(
        "function invalidateWorkflowsSnapshot(){", 1
    )[1].split("async function loadWorkflowsSnapshot(){", 1)[0]
    assert "workflowsSnapshotGeneration+=1;" in invalidate
    assert "workflowsSnapshotCache=null;" in invalidate
    assert "workflowsSnapshotAt=0;" in invalidate
    assert "workflowsSnapshotRequest=null;" in invalidate

    loader = block.split("async function loadWorkflowsSnapshot(){", 1)[1]
    assert "const requestGeneration=workflowsSnapshotGeneration;" in loader
    assert "const request=api('/v1/workflows').then(function(data){" in loader
    assert "if(requestGeneration!==workflowsSnapshotGeneration){" in loader
    assert "return loadWorkflowsSnapshot();" in loader
    assert "workflowsSnapshotRequest=request;" in loader
    assert "return request;" in loader


def test_old_workflow_snapshot_finally_cannot_clear_newer_request():
    block = DASHBOARD_HTML.split(
        "async function loadWorkflowsSnapshot(){", 1
    )[1].split("function selectedLaunchRepository(){", 1)[0]

    assert "if(workflowsSnapshotRequest===request){" in block
    assert "workflowsSnapshotRequest=null;" in block
    assert (
        block.index("if(workflowsSnapshotRequest===request){")
        < block.rindex("workflowsSnapshotRequest=null;")
    )
