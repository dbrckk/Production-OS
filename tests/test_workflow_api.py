import json
import threading
import urllib.request
from http.server import ThreadingHTTPServer

from production_os.api_auth import TokenAuthorizer, token_digest
from production_os.control_plane import ControlPlane, make_handler


def api(base, path, token, payload=None):
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        base + path,
        data=data,
        headers={
            "Authorization":f"Bearer {token}",
            "Content-Type":"application/json",
        },
        method="POST" if payload is not None else "GET",
    )
    with urllib.request.urlopen(request, timeout=3) as response:
        raw = response.read()
        return response.status, json.loads(raw or b"{}")


def test_workflow_api_end_to_end(tmp_path):
    auth=TokenAuthorizer([
        {"name":"op","role":"operator","sha256":token_digest("op")},
        {"name":"worker","role":"worker","sha256":token_digest("worker")},
    ])
    control=ControlPlane(str(tmp_path/"db.sqlite"),authorizer=auth)
    control.workers.register("w1",["python"],1)

    server=ThreadingHTTPServer(("127.0.0.1",0),make_handler(control))
    thread=threading.Thread(target=server.serve_forever,daemon=True)
    thread.start()
    base=f"http://127.0.0.1:{server.server_port}"

    try:
        _,created=api(base,"/v1/workflows","op",{
            "name":"build-release",
            "repository":"o/a",
            "tasks":[
                {
                    "task_id":"build",
                    "title":"Build",
                    "payload":{"required_capabilities":["python"]},
                },
                {
                    "task_id":"package",
                    "title":"Package",
                    "dependencies":["build"],
                    "payload":{"required_capabilities":["python"]},
                },
            ],
        })
        workflow_id=created["workflow"]["id"]

        _,dispatched=api(
            base,
            f"/v1/workflows/{workflow_id}/dispatch",
            "op",
            {},
        )
        assert len(dispatched["jobs"])==1

        _,claimed=api(base,"/v1/jobs/claim","worker",{
            "worker_id":"w1",
            "capabilities":["python"],
        })
        first_key=claimed["job"]["key"]
        api(base,"/v1/jobs/ack","worker",{
            "key":first_key,
            "worker_id":"w1",
        })
        _,completed=api(base,"/v1/jobs/complete","worker",{
            "key":first_key,
            "worker_id":"w1",
            "result":{"ok":True},
        })
        assert completed["workflow"]["status"]=="running"

        _,claimed2=api(base,"/v1/jobs/claim","worker",{
            "worker_id":"w1",
            "capabilities":["python"],
        })
        second_key=claimed2["job"]["key"]
        assert second_key != first_key
        api(base,"/v1/jobs/ack","worker",{
            "key":second_key,
            "worker_id":"w1",
        })
        _,completed2=api(base,"/v1/jobs/complete","worker",{
            "key":second_key,
            "worker_id":"w1",
            "result":{"artifact":"app.zip"},
        })
        assert completed2["workflow"]["status"]=="succeeded"

        _,status=api(
            base,
            f"/v1/workflows/{workflow_id}",
            "op",
        )
        assert status["workflow"]["status"]=="succeeded"
    finally:
        server.shutdown()
        server.server_close()
