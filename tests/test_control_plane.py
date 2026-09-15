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
