from production_os.dashboard_ui import DASHBOARD_HTML


def test_last_production_only_latest_request_can_render():
    assert "function currentLastProjectId(){" in DASHBOARD_HTML
    assert "let lastProductionLoadSequence=0;" in DASHBOARD_HTML

    body = DASHBOARD_HTML.split(
        "async function loadLastProduction(){", 1
    )[1].split("function launchDraftFingerprint", 1)[0]

    assert "const requestSequence=++lastProductionLoadSequence;" in body
    assert "const projectId=currentLastProjectId();" in body
    assert body.count("requestSequence!==lastProductionLoadSequence") >= 2
    assert body.count("currentLastProjectId()!==projectId") >= 2

    await_index = body.index(
        "'/v1/dashboard/production-status?project_id='+encodeURIComponent(projectId)"
    )
    guard_index = body.index("requestSequence!==lastProductionLoadSequence")
    render_index = body.index("el.hidden=false;")
    assert await_index < guard_index < render_index


def test_missing_last_project_invalidates_older_inflight_request():
    body = DASHBOARD_HTML.split(
        "async function loadLastProduction(){", 1
    )[1].split("function launchDraftFingerprint", 1)[0]

    sequence_index = body.index(
        "const requestSequence=++lastProductionLoadSequence;"
    )
    project_index = body.index("const projectId=currentLastProjectId();")
    empty_index = body.index("if(!token()||!projectId){")
    assert sequence_index < project_index < empty_index
