from production_os.dashboard_ui import DASHBOARD_HTML


def test_authenticated_api_requests_have_bounded_timeout():
    body = DASHBOARD_HTML.split(
        "async function api(path,options){", 1
    )[1].split("async function checkServer()", 1)[0]

    assert "const timeoutValue=Number(options.timeoutMs);" in body
    assert "const timeoutMs=Number.isFinite(timeoutValue)?Math.max(0,timeoutValue):30000;" in body
    assert "delete requestOptions.timeoutMs;" in body
    assert "const controller=new AbortController();" in body
    assert "requestOptions.signal=controller.signal;" in body
    assert "controller.abort();" in body
    assert "Délai réseau dépassé. Réessaie." in body
    assert "if(timeoutId!==null)clearTimeout(timeoutId);" in body


def test_authenticated_api_timeout_preserves_external_abort_signal():
    body = DASHBOARD_HTML.split(
        "async function api(path,options){", 1
    )[1].split("async function checkServer()", 1)[0]

    assert "const externalSignal=requestOptions.signal||null;" in body
    assert "if(externalSignal.aborted) controller.abort();" in body
    assert "externalSignal.addEventListener('abort',onExternalAbort,{once:true});" in body
    assert "externalSignal.removeEventListener('abort',onExternalAbort);" in body


def test_authenticated_api_allows_explicit_timeout_disable():
    body = DASHBOARD_HTML.split(
        "async function api(path,options){", 1
    )[1].split("async function checkServer()", 1)[0]

    assert "if(timeoutMs>0){" in body
