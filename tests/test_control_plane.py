import json
import threading
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer

from production_os.api_auth import TokenAuthorizer, token_digest
from production_os.control_plane import ControlPlane, make_handler


def request(url, token, payload=None):
    data=None if payload is None else json.dumps(payload).encode()
    req=urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization":f"Bearer {token}",
            "Content-Type":"application/json",
        },
        method="POST" if payload is not None else "GET",
    )
    with urllib.request.urlopen(req,timeout=3) as response:
        body=response.read()
        return response.status, json.loads(body or b"{}")


def test_control_plane_worker_and_queue(tmp_path):
    auth=TokenAuthorizer([
        {"name":"op","role":"operator","sha256":token_digest("op")},
        {"name":"worker","role":"worker","sha256":token_digest("worker")},
    ])
    control=ControlPlane(str(tmp_path/"db.sqlite"),authorizer=auth)
    server=ThreadingHTTPServer(("127.0.0.1",0),make_handler(control))
    thread=threading.Thread(target=server.serve_forever,daemon=True)
    thread.start()
    base=f"http://127.0.0.1:{server.server_port}"
    try:
        status,_=request(base+"/v1/workers/register","op",{
            "worker_id":"python-1",
            "capabilities":["python"],
            "max_concurrency":2,
        })
        assert status==200

        status,enqueued=request(base+"/v1/jobs/enqueue","op",{
            "handoff":{"repository":"o/a","task":"x","priority":10},
            "required_capabilities":["python"],
        })
        assert status==201

        status,claimed=request(base+"/v1/jobs/claim","worker",{
            "worker_id":"python-1",
            "capabilities":["python"],
        })
        assert status==200
        key=claimed["job"]["key"]
        assert key==enqueued["job"]["key"]

        status,_=request(base+"/v1/jobs/ack","worker",{
            "key":key,
            "worker_id":"python-1",
        })
        assert status==200

        status,completed=request(base+"/v1/jobs/complete","worker",{
            "key":key,
            "worker_id":"python-1",
        })
        assert status==200
        assert completed["job"]["status"]=="completed"
    finally:
        server.shutdown()
        server.server_close()


def test_trust_status_endpoint_requires_auth_and_forwards_filters(tmp_path):
    auth=TokenAuthorizer([
        {"name":"viewer","role":"viewer","sha256":token_digest("viewer")},
    ])
    control=ControlPlane(str(tmp_path/"db.sqlite"),authorizer=auth)
    captured={}

    def trust_status(**kwargs):
        captured.update(kwargs)
        return {
            "valid":True,
            "total_releases":0,
            "matched_releases":0,
            "affected_releases":0,
            "severity":"none",
            "filters":kwargs,
            "releases":[],
        }

    control.releases.trust_status=trust_status
    server=ThreadingHTTPServer(("127.0.0.1",0),make_handler(control))
    thread=threading.Thread(target=server.serve_forever,daemon=True)
    thread.start()
    base=f"http://127.0.0.1:{server.server_port}"
    try:
        url=(
            base+"/v1/trust-status"
            "?validator_id=validator-prod"
            "&builder_id=https%3A%2F%2Fbuilder.example%2Fprod"
            "&key_id=sha256%3Aabc"
        )
        status,body=request(url,"viewer")
        assert status==200
        assert body["schema_version"]=="production-os/trust-status/v1"
        assert body["valid"] is True
        assert captured=={
            "validator_id":"validator-prod",
            "builder_id":"https://builder.example/prod",
            "key_id":"sha256:abc",
        }

        req=urllib.request.Request(base+"/v1/trust-status",method="GET")
        try:
            urllib.request.urlopen(req,timeout=3)
            assert False, "unauthenticated trust-status request must fail"
        except urllib.error.HTTPError as exc:
            assert exc.code==401
            payload=json.loads(exc.read())
            assert payload["error"]=="unauthorized"
    finally:
        server.shutdown()
        server.server_close()


def test_incident_history_endpoints_require_auth_and_forward_filter(tmp_path):
    auth=TokenAuthorizer([
        {"name":"viewer","role":"viewer","sha256":token_digest("viewer")},
    ])
    control=ControlPlane(str(tmp_path/"db.sqlite"),authorizer=auth)
    captured={}
    control.releases.incident_history=lambda incident_id=None: (
        captured.update({"incident_id":incident_id}) or
        [{"sequence":1,"incident_id":incident_id or "trust-one"}]
    )
    control.releases.verify_incident_history=lambda: {
        "valid":True,"entries":1,"head_hash":"abc"
    }
    server=ThreadingHTTPServer(("127.0.0.1",0),make_handler(control))
    thread=threading.Thread(target=server.serve_forever,daemon=True)
    thread.start()
    base=f"http://127.0.0.1:{server.server_port}"
    try:
        status,body=request(
            base+"/v1/incident-history?incident_id=trust-one","viewer"
        )
        assert status==200
        assert body["schema_version"]==(
            "production-os/trust-incident-history/v1"
        )
        assert captured["incident_id"]=="trust-one"
        assert body["entries"][0]["sequence"]==1

        status,body=request(base+"/v1/incident-history/verify","viewer")
        assert status==200
        assert body["schema_version"]==(
            "production-os/trust-incident-history-verification/v1"
        )
        assert body["valid"] is True
        assert body["head_hash"]=="abc"

        for path in ("/v1/incident-history","/v1/incident-history/verify"):
            req=urllib.request.Request(base+path,method="GET")
            try:
                urllib.request.urlopen(req,timeout=3)
                assert False, "unauthenticated incident history must fail"
            except urllib.error.HTTPError as exc:
                assert exc.code==401
    finally:
        server.shutdown()
        server.server_close()


def test_incident_snapshot_requires_operator_and_reports_dedup(tmp_path):
    auth=TokenAuthorizer([
        {"name":"viewer","role":"viewer","sha256":token_digest("viewer")},
        {"name":"operator","role":"operator","sha256":token_digest("operator")},
    ])
    control=ControlPlane(str(tmp_path/"db.sqlite"),authorizer=auth)
    calls=[]
    def snapshot(**kwargs):
        calls.append(kwargs)
        return {
            "incident_id":"trust-test",
            "report_hash":"abc",
            "recorded":len(calls)==1,
            "deduplicated":len(calls)>1,
            "report":{"valid":False},
        }
    control.releases.record_incident_report=snapshot
    server=ThreadingHTTPServer(("127.0.0.1",0),make_handler(control))
    thread=threading.Thread(target=server.serve_forever,daemon=True)
    thread.start()
    base=f"http://127.0.0.1:{server.server_port}"
    payload=json.dumps({
        "validator_id":"validator-prod",
        "builder_id":"https://builder.example/prod",
        "key_id":"sha256:abc",
    }).encode()
    try:
        req=urllib.request.Request(
            base+"/v1/incident-snapshot",
            data=payload,
            headers={
                "Authorization":"Bearer operator",
                "Content-Type":"application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(req,timeout=3) as response:
            body=json.loads(response.read())
            assert response.status==201
        assert body["schema_version"]==(
            "production-os/trust-incident-snapshot/v1"
        )
        assert body["recorded"] is True
        assert calls[0]["key_id"]=="sha256:abc"

        req=urllib.request.Request(
            base+"/v1/incident-snapshot",
            data=payload,
            headers={
                "Authorization":"Bearer operator",
                "Content-Type":"application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(req,timeout=3) as response:
            body=json.loads(response.read())
            assert response.status==200
        assert body["deduplicated"] is True

        req=urllib.request.Request(
            base+"/v1/incident-snapshot",
            data=payload,
            headers={
                "Authorization":"Bearer viewer",
                "Content-Type":"application/json",
            },
            method="POST",
        )
        try:
            urllib.request.urlopen(req,timeout=3)
            assert False, "viewer must not write incident ledger"
        except urllib.error.HTTPError as exc:
            assert exc.code==403

        req=urllib.request.Request(
            base+"/v1/incident-snapshot",
            data=payload,
            headers={"Content-Type":"application/json"},
            method="POST",
        )
        try:
            urllib.request.urlopen(req,timeout=3)
            assert False, "anonymous incident snapshot must fail"
        except urllib.error.HTTPError as exc:
            assert exc.code==401
    finally:
        server.shutdown()
        server.server_close()


def test_incident_snapshot_rejects_invalid_payload_shapes(tmp_path):
    auth=TokenAuthorizer([
        {"name":"operator","role":"operator","sha256":token_digest("operator")},
    ])
    control=ControlPlane(str(tmp_path/"db.sqlite"),authorizer=auth)
    calls=[]
    control.releases.record_incident_report=lambda **kwargs: calls.append(kwargs)
    server=ThreadingHTTPServer(("127.0.0.1",0),make_handler(control))
    thread=threading.Thread(target=server.serve_forever,daemon=True)
    thread.start()
    base=f"http://127.0.0.1:{server.server_port}"

    def post(payload):
        req=urllib.request.Request(
            base+"/v1/incident-snapshot",
            data=json.dumps(payload).encode(),
            headers={
                "Authorization":"Bearer operator",
                "Content-Type":"application/json",
            },
            method="POST",
        )
        try:
            urllib.request.urlopen(req,timeout=3)
            assert False, "invalid payload must fail"
        except urllib.error.HTTPError as exc:
            assert exc.code==400
            return json.loads(exc.read())

    try:
        assert "JSON object" in post([])["error"]
        body=post({"unexpected":"value"})
        assert body["error"]=="unknown incident snapshot fields"
        assert body["fields"]==["unexpected"]
        assert "non-empty string" in post({"key_id":42})["error"]
        assert "non-empty string" in post({"validator_id":"   "})["error"]
        assert "too long" in post({"builder_id":"x"*513})["error"]
        assert calls==[]
    finally:
        server.shutdown()
        server.server_close()


def test_http_body_parser_rejects_invalid_json_and_oversized_payload(tmp_path):
    auth=TokenAuthorizer([
        {"name":"operator","role":"operator","sha256":token_digest("operator")},
    ])
    control=ControlPlane(str(tmp_path/"db.sqlite"),authorizer=auth)
    server=ThreadingHTTPServer(("127.0.0.1",0),make_handler(control))
    thread=threading.Thread(target=server.serve_forever,daemon=True)
    thread.start()
    base=f"http://127.0.0.1:{server.server_port}"
    try:
        req=urllib.request.Request(
            base+"/v1/incident-snapshot",
            data=b'{"key_id":',
            headers={
                "Authorization":"Bearer operator",
                "Content-Type":"application/json",
            },
            method="POST",
        )
        try:
            urllib.request.urlopen(req,timeout=3)
            assert False, "invalid JSON must fail"
        except urllib.error.HTTPError as exc:
            assert exc.code==400
            assert json.loads(exc.read())["error"]=="invalid JSON body"

        req=urllib.request.Request(
            base+"/v1/incident-snapshot",
            data=b"x"*(1024*1024+1),
            headers={
                "Authorization":"Bearer operator",
                "Content-Type":"application/json",
            },
            method="POST",
        )
        try:
            urllib.request.urlopen(req,timeout=3)
            assert False, "oversized body must fail"
        except urllib.error.HTTPError as exc:
            assert exc.code==413
            assert json.loads(exc.read())["error"]=="request body too large"
    finally:
        server.shutdown()
        server.server_close()


def test_github_webhook_returns_413_for_oversized_body(tmp_path):
    control=ControlPlane(
        str(tmp_path/"db.sqlite"),
        github_webhook_secret="secret",
    )
    server=ThreadingHTTPServer(("127.0.0.1",0),make_handler(control))
    thread=threading.Thread(target=server.serve_forever,daemon=True)
    thread.start()
    try:
        req=urllib.request.Request(
            f"http://127.0.0.1:{server.server_port}/v1/github/webhook",
            data=b"x"*(1024*1024+1),
            headers={
                "Content-Type":"application/json",
                "X-Hub-Signature-256":"sha256=invalid",
            },
            method="POST",
        )
        try:
            urllib.request.urlopen(req,timeout=3)
            assert False, "oversized webhook must fail"
        except urllib.error.HTTPError as exc:
            assert exc.code==413
            assert json.loads(exc.read())["error"]=="request body too large"
    finally:
        server.shutdown()
        server.server_close()


def test_generic_post_returns_413_before_endpoint_processing(tmp_path):
    auth=TokenAuthorizer([
        {"name":"operator","role":"operator","sha256":token_digest("operator")},
    ])
    control=ControlPlane(str(tmp_path/"db.sqlite"),authorizer=auth)
    server=ThreadingHTTPServer(("127.0.0.1",0),make_handler(control))
    thread=threading.Thread(target=server.serve_forever,daemon=True)
    thread.start()
    try:
        req=urllib.request.Request(
            f"http://127.0.0.1:{server.server_port}/v1/stragglers/speculate",
            data=b"x"*(1024*1024+1),
            headers={
                "Authorization":"Bearer operator",
                "Content-Type":"application/json",
            },
            method="POST",
        )
        try:
            urllib.request.urlopen(req,timeout=3)
            assert False, "oversized generic POST must fail"
        except urllib.error.HTTPError as exc:
            assert exc.code==413
            assert json.loads(exc.read())["error"]=="request body too large"
    finally:
        server.shutdown()
        server.server_close()
