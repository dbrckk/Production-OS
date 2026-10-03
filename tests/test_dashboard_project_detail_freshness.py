from production_os.dashboard_ui import DASHBOARD_HTML


def test_project_detail_ignores_stale_project_or_window_responses():
    assert "let projectDetailLoadSequence=0;" in DASHBOARD_HTML

    body = DASHBOARD_HTML.split(
        "async function loadProjectDetail(repository){", 1
    )[1].split("function openWorker(encoded)", 1)[0]

    assert "const requestSequence=++projectDetailLoadSequence;" in body
    assert "const requestedWindow=appState.window;" in body
    assert 'api(base+"/commits?window="+encodeURIComponent(requestedWindow))' in body
    assert 'api(base+"/usage?window="+encodeURIComponent(requestedWindow))' in body
    assert body.count("requestSequence!==projectDetailLoadSequence") >= 2
    assert body.count('appState.view!=="projects"') >= 2
    assert body.count("appState.repository!==repository") >= 2
    assert body.count("appState.window!==requestedWindow") >= 2

    await_index = body.index("const results=await Promise.all([")
    guard_index = body.index("requestSequence!==projectDetailLoadSequence")
    render_index = body.index("const detail=results[0]")
    assert await_index < guard_index < render_index
