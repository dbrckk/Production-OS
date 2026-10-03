from production_os.dashboard_ui import DASHBOARD_HTML


def test_launch_keeps_newer_repository_or_instruction_draft():
    body = DASHBOARD_HTML.split(
        "async function launchWorkflow(){", 1
    )[1].split("async function refreshDashboard(){", 1)[0]

    assert "const instructionInput=document.getElementById('instruction');" in body
    assert "const launchFingerprint=launchDraftFingerprint(repository,task);" in body
    assert "const readinessAtLaunch=launchReadiness;" in body
    assert "const immediate=readinessAtLaunch&&readinessAtLaunch.execution==='immediate';" in body

    assert "const draftStillCurrent=" in body
    assert "repositorySelect.value.trim()," in body
    assert "instructionInput.value.trim()" in body
    assert ")===launchFingerprint;" in body
    assert "if(draftStillCurrent)instructionInput.value='';" in body
    assert "document.getElementById('instruction').value='';" not in body


def test_launch_does_not_retarget_dashboard_state_after_repository_change():
    body = DASHBOARD_HTML.split(
        "async function launchWorkflow(){", 1
    )[1].split("async function refreshDashboard(){", 1)[0]

    assert (
        "if(workflowId&&repositorySelect.value.trim()===repository) "
        "appState.repository=repository;"
    ) in body
