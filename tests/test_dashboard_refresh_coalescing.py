from production_os.dashboard_ui import DASHBOARD_HTML


def test_full_dashboard_refresh_coalesces_overlapping_requests():
    assert "let refreshPending=false;" in DASHBOARD_HTML
    assert "let refreshPromise=null;" in DASHBOARD_HTML

    body = DASHBOARD_HTML.split(
        "async function refreshDashboard(){", 1
    )[1].split("bootstrapPairingFromFragment()", 1)[0]

    assert "if(refreshBusy){" in body
    assert "refreshPending=true;" in body
    assert "return refreshPromise;" in body
    assert "refreshPromise=(async function(){" in body
    assert "do{" in body
    assert "refreshPending=false;" in body
    assert "}while(refreshPending);" in body
    assert "refreshBusy=false;" in body
    assert "refreshPromise=null;" in body


def test_full_dashboard_refresh_waiters_share_coalesced_cycle():
    body = DASHBOARD_HTML.split(
        "async function refreshDashboard(){", 1
    )[1].split("bootstrapPairingFromFragment()", 1)[0]

    assert body.count("return refreshPromise;") >= 2
    assert body.index("refreshPending=true;") < body.index("return refreshPromise;")
    assert body.index("refreshPromise=(async function(){") < body.rindex("return refreshPromise;")
