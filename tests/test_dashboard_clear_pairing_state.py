from production_os.dashboard_ui import DASHBOARD_HTML


def test_clear_pairing_purges_local_operator_state_and_url_context():
    body = DASHBOARD_HTML.split(
        "async function clearPairing(){", 1
    )[1].split("function updateLaunchButtonState(){", 1)[0]

    assert "const secret=token();" in body
    assert "keepalive:true" in body
    assert "headers:{Authorization:'Bearer '+secret}" in body
    assert "localStorage.removeItem(TOKEN_KEY);" in body
    assert "localStorage.removeItem(LAST_PROJECT_KEY);" in body
    assert "localStorage.removeItem(LAST_REPOSITORY_KEY);" in body
    assert "localStorage.removeItem(PENDING_LAUNCH_KEY);" in body
    assert "workerOnline=false;" in body
    assert "launchReadiness=null;" in body
    assert "window.location.replace(window.location.pathname);" in body

    token_remove = body.index("localStorage.removeItem(TOKEN_KEY);")
    reload_index = body.index("window.location.replace(window.location.pathname);")
    assert token_remove < reload_index


def test_clear_pairing_does_not_wait_for_remote_revoke_before_local_purge():
    body = DASHBOARD_HTML.split(
        "async function clearPairing(){", 1
    )[1].split("function updateLaunchButtonState(){", 1)[0]

    assert "await fetch('/v1/dashboard/session/revoke'" not in body
    assert "fetch('/v1/dashboard/session/revoke'" in body
    assert ".catch(function(){});" in body
