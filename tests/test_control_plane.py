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
