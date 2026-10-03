from production_os.dashboard_ui import DASHBOARD_HTML


def test_device_session_list_ignores_stale_token_or_request():
    assert "let deviceSessionsLoadSequence=0;" in DASHBOARD_HTML

    body = DASHBOARD_HTML.split(
        "async function loadDeviceSessions(){", 1
    )[1].split("async function revokeDeviceSession", 1)[0]

    assert "const requestSequence=++deviceSessionsLoadSequence;" in body
    assert "const requestToken=token();" in body
    assert body.count("requestSequence!==deviceSessionsLoadSequence") >= 2
    assert body.count("token()!==requestToken") >= 2


def test_pairing_link_creation_is_single_flight_and_token_scoped():
    assert "let pairingLinkBusy=false;" in DASHBOARD_HTML

    body = DASHBOARD_HTML.split(
        "async function createPairingLink(){", 1
    )[1].split("async function savePairing(){", 1)[0]

    assert "if(pairingLinkBusy){" in body
    assert "pairingLinkBusy=true;" in body
    assert "pairingLinkBusy=false;" in body
    assert body.count("token()!==requestToken") >= 3
    assert "Création du lien déjà en cours..." in body


def test_candidate_pairing_token_is_verified_before_persistence():
    assert "let pairingSaveBusy=false;" in DASHBOARD_HTML

    body = DASHBOARD_HTML.split(
        "async function savePairing(){", 1
    )[1].split("async function clearPairing(){", 1)[0]

    assert "if(pairingSaveBusy){" in body
    assert "pairingSaveBusy=true;" in body
    assert "await api('/v1/workers',{authToken:value});" in body
    assert "localStorage.setItem(TOKEN_KEY,value);" in body
    assert (
        body.index("await api('/v1/workers',{authToken:value});")
        < body.index("localStorage.setItem(TOKEN_KEY,value);")
    )
    assert "if(previous) localStorage.setItem(TOKEN_KEY,previous)" not in body
    assert "appairage actuel conservé" in body
    assert "pairingSaveBusy=false;" in body


def test_pairing_success_preserves_newer_token_draft():
    body = DASHBOARD_HTML.split(
        "async function savePairing(){", 1
    )[1].split("async function clearPairing(){", 1)[0]

    assert "const draftStillCurrent=input.value.trim()===value;" in body
    assert "if(draftStillCurrent){" in body
    assert "Appareil appairé. Un nouveau token reste à vérifier." in body



def test_candidate_token_does_not_overwrite_pairing_changed_during_validation():
    body = DASHBOARD_HTML.split(
        "async function savePairing(){", 1
    )[1].split("async function clearPairing(){", 1)[0]

    assert "if(token()!==previous){" in body
    assert "nouveau token non appliqué" in body
    assert (
        body.index("if(token()!==previous){")
        < body.index("localStorage.setItem(TOKEN_KEY,value);")
    )
