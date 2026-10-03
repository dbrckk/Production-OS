from production_os.dashboard_ui import DASHBOARD_HTML


def test_production_inbox_only_latest_request_can_render():
    assert "let productionInboxLoadSequence=0;" in DASHBOARD_HTML

    body = DASHBOARD_HTML.split(
        "async function loadProductionInbox(){", 1
    )[1].split("async function loadAttention(){", 1)[0]

    assert "const requestSequence=++productionInboxLoadSequence;" in body
    assert "if(requestSequence!==productionInboxLoadSequence)return null;" in body
    assert body.count("requestSequence!==productionInboxLoadSequence") >= 2
    assert "if(requestSequence===productionInboxLoadSequence){" in body
    assert (
        body.index("if(requestSequence!==productionInboxLoadSequence)return null;")
        < body.index("count.textContent=String(")
    )


def test_production_detail_only_latest_focus_can_render():
    assert "let productionDetailLoadSequence=0;" in DASHBOARD_HTML

    body = DASHBOARD_HTML.split(
        "async function loadProductionInboxDetail(projectId){", 1
    )[1].split("async function submitProductionInstruction", 1)[0]

    assert "const requestSequence=++productionDetailLoadSequence;" in body
    assert body.count("requestSequence!==productionDetailLoadSequence") >= 2
    assert body.count("appState.focus!==value") >= 2

    await_index = body.index(
        '"/v1/dashboard/production-status?project_id="+encodeURIComponent(value)'
    )
    guard_index = body.index("requestSequence!==productionDetailLoadSequence")
    render_index = body.index("detail.innerHTML=")
    assert await_index < guard_index
    assert guard_index < render_index


def test_closing_production_detail_invalidates_inflight_detail_request():
    body = DASHBOARD_HTML.split(
        "async function loadProductionInboxDetail(projectId){", 1
    )[1].split("async function submitProductionInstruction", 1)[0]

    sequence_index = body.index(
        "const requestSequence=++productionDetailLoadSequence;"
    )
    empty_index = body.index("if(!value){")
    assert sequence_index < empty_index
