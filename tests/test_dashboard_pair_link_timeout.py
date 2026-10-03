from production_os.dashboard_ui import DASHBOARD_HTML


def test_pairing_fragment_exchange_has_network_timeout():
    body = DASHBOARD_HTML.split(
        "async function bootstrapPairingFromFragment(){", 1
    )[1].split("function esc(value)", 1)[0]

    assert "const controller=new AbortController();" in body
    assert "setTimeout(function(){controller.abort()},15000)" in body
    assert "signal:controller.signal" in body
    assert "if(e&&e.name==='AbortError'){" in body
    assert "Serveur trop lent" in body
    assert "clearTimeout(timeoutId);" in body


def test_pairing_fragment_still_persists_only_server_minted_token():
    body = DASHBOARD_HTML.split(
        "async function bootstrapPairingFromFragment(){", 1
    )[1].split("function esc(value)", 1)[0]

    assert "if(!r.ok||!payload.session_token)" in body
    assert "localStorage.setItem(TOKEN_KEY,String(payload.session_token));" in body
    assert (
        body.index("if(!r.ok||!payload.session_token)")
        < body.index("localStorage.setItem(TOKEN_KEY,String(payload.session_token));")
    )
