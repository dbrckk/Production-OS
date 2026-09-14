import json
import threading
import urllib.request
from http.server import ThreadingHTTPServer

from production_os.api_auth import TokenAuthorizer, token_digest
from production_os.control_plane import ControlPlane, make_handler


def api(base, path, token, payload=None):
    data=None if payload is None else json.dumps(payload).encode("utf-8")
    req=urllib.request.Request(
        base+path,
        data=data,
        headers={
            "Authorization":f"Bearer {token}",
            "Content-Type":"application/json",
        },
        method="POST" if payload is not None else "GET",
    )
    with urllib.request.urlopen(req,timeout=3) as response:
        raw=response.read()
        return response.status,json.loads(raw or b"{}")


def test_first_success_wins_over_speculative_copy(tmp_path):
    auth=TokenAuthorizer([
        {"name":"op","role":"operator","sha256":token_digest("op")},
        {"name":"worker","role":"worker","sha256":token_digest("worker")},
    ])
    control=ControlPlane(str(tmp_path/"db.sqlite"),authorizer=auth)
    control.workers.register("slow",["python"],1)
    control.workers.register("fast",["python"],1)

    original=control.queue.enqueue({
        "handoff":{
            "repository":"o/a",
            "task":"Build",
            "constraints":{"speculative_safe":True},
        },
        "required_capabilities":["python"],
    })
    control.queue.claim_next("slow",capabilities=["python"])
    duplicate=control.speculation.spawn(
        original["key"],
        target_worker="fast",
    )

    server=ThreadingHTTPServer(("127.0.0.1",0),make_handler(control))
    thread=threading.Thread(target=server.serve_forever,daemon=True)
    thread.start()
    base=f"http://127.0.0.1:{server.server_port}"
    try:
        _,claimed=api(base,"/v1/jobs/claim","worker",{
            "worker_id":"fast",
            "capabilities":["python"],
        })
        assert claimed["job"]["key"]==duplicate["key"]

        api(base,"/v1/jobs/ack","worker",{
            "key":duplicate["key"],
            "worker_id":"fast",
        })
        _,won=api(base,"/v1/jobs/complete","worker",{
            "key":duplicate["key"],
            "worker_id":"fast",
            "duration_seconds":30,
        })
        assert won["speculation"]["winner"] is True
        assert original["key"] in won["speculation"]["cancelled_losers"]

        assert control.queue.get(original["key"])["status"]=="cancelled"
        assert control.queue.get(duplicate["key"])["status"]=="completed"
    finally:
        server.shutdown()
        server.server_close()
