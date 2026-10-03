from production_os.dashboard_ui import DASHBOARD_HTML


def test_worker_status_ignores_stale_request_or_pairing_token():
    assert "let workerStatusLoadSequence=0;" in DASHBOARD_HTML

    body = DASHBOARD_HTML.split(
        "async function loadWorkerStatus(){", 1
    )[1].split("function workflowState(status)", 1)[0]

    assert "const requestSequence=++workerStatusLoadSequence;" in body
    assert "const requestToken=token();" in body
    assert body.count("requestSequence!==workerStatusLoadSequence") >= 2
    assert body.count("token()!==requestToken") >= 2

    await_index = body.index("const data=await api('/v1/workers');")
    guard_index = body.index("requestSequence!==workerStatusLoadSequence")
    mutation_index = body.index("workerOnline=online.length>0;")
    assert await_index < guard_index < mutation_index


def test_visual_quality_only_latest_request_can_render():
    assert "let visualQualityLoadSequence=0;" in DASHBOARD_HTML
    assert "function clearVisualQualityDetails(){" in DASHBOARD_HTML

    body = DASHBOARD_HTML.split(
        "async function loadVisualQuality(){", 1
    )[1].split("let launchReadinessLoadSequence=0;", 1)[0]

    assert "const requestSequence=++visualQualityLoadSequence;" in body
    assert "const requestToken=token();" in body
    assert body.count("requestSequence!==visualQualityLoadSequence") >= 3
    assert body.count("token()!==requestToken") >= 3
    assert body.count(
        "!repositorySelectionStillCurrent(selectedRepository)"
    ) >= 3
    assert "Sélectionne un repository pour afficher la qualité visuelle." in body
    assert body.count("clearVisualQualityDetails();") >= 4


def test_launch_readiness_only_latest_request_can_render():
    assert "let launchReadinessLoadSequence=0;" in DASHBOARD_HTML

    body = DASHBOARD_HTML.split(
        "async function loadLaunchReadiness(){", 1
    )[1].split("function rememberLastProject", 1)[0]

    assert "const requestSequence=++launchReadinessLoadSequence;" in body
    assert "const requestToken=token();" in body
    assert body.count("requestSequence!==launchReadinessLoadSequence") >= 2
    assert body.count("token()!==requestToken") >= 2
    assert body.count("!repositorySelectionStillCurrent(repository)") >= 2
    assert "Disponibilité : sélectionne un repository." in body

    await_index = body.index(
        "'/v1/dashboard/launch-readiness?repository='+encodeURIComponent(repository)"
    )
    guard_index = body.index("requestSequence!==launchReadinessLoadSequence")
    state_index = body.index("launchReadiness=data;")
    assert await_index < guard_index < state_index
