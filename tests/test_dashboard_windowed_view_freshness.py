from production_os.dashboard_ui import DASHBOARD_HTML


def test_overview_ignores_stale_window_or_view_responses():
    assert "let overviewLoadSequence=0;" in DASHBOARD_HTML

    body = DASHBOARD_HTML.split(
        "async function loadOverview(){", 1
    )[1].split("function autopilotWaitLabel", 1)[0]

    assert "const requestSequence=++overviewLoadSequence;" in body
    assert "const requestedWindow=appState.window;" in body
    assert (
        'api("/v1/dashboard/overview?window="+encodeURIComponent(requestedWindow))'
        in body
    )
    assert "'+esc(requestedWindow)+'" in body
    assert body.count("requestSequence!==overviewLoadSequence") >= 2
    assert body.count('appState.view!=="overview"') >= 2
    assert body.count("appState.window!==requestedWindow") >= 2

    await_index = body.index("const results=await Promise.all([")
    guard_index = body.index("requestSequence!==overviewLoadSequence")
    render_index = body.index("const data=results[0]")
    assert await_index < guard_index < render_index


def test_activity_ignores_stale_window_or_view_responses():
    assert "let activityLoadSequence=0;" in DASHBOARD_HTML

    body = DASHBOARD_HTML.split(
        "async function loadActivityView(){", 1
    )[1].split("function navigate(next)", 1)[0]

    assert "const requestSequence=++activityLoadSequence;" in body
    assert "const requestedWindow=appState.window;" in body
    assert (
        'api("/v1/dashboard/remediation-analytics?window="+encodeURIComponent(requestedWindow))'
        in body
    )
    assert "'+esc(requestedWindow)+'" in body
    assert body.count("requestSequence!==activityLoadSequence") >= 2
    assert body.count('appState.view!=="activity"') >= 2
    assert body.count("appState.window!==requestedWindow") >= 2

    await_index = body.index("const results=await Promise.all([")
    guard_index = body.index("requestSequence!==activityLoadSequence")
    render_index = body.index("const data=results[0]")
    assert await_index < guard_index < render_index
