from production_os.dashboard_ui import DASHBOARD_HTML


def test_worker_detail_ignores_stale_worker_or_window_responses():
    assert "let workerDetailLoadSequence=0;" in DASHBOARD_HTML

    body = DASHBOARD_HTML.split(
        "async function loadWorkerDetail(workerId){", 1
    )[1].split("async function createManagedProject", 1)[0]

    assert "const requestSequence=++workerDetailLoadSequence;" in body
    assert "const requestedWindow=appState.window;" in body
    assert 'api(base+"/usage?window="+encodeURIComponent(requestedWindow))' in body
    assert body.count("requestSequence!==workerDetailLoadSequence") >= 2
    assert body.count('appState.view!=="workers"') >= 2
    assert body.count("appState.workerId!==workerId") >= 2
    assert body.count("appState.window!==requestedWindow") >= 2

    await_index = body.index("const results=await Promise.all([")
    guard_index = body.index("requestSequence!==workerDetailLoadSequence")
    render_index = body.index("const detail=results[0]")
    assert await_index < guard_index < render_index
