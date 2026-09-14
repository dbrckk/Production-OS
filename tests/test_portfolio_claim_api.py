import json
import threading
import urllib.request
from http.server import ThreadingHTTPServer

from production_os.api_auth import TokenAuthorizer, token_digest
from production_os.control_plane import ControlPlane, make_handler
from production_os.workflow_engine import WorkflowTaskSpec


def api(base, path, token, payload=None):
    data=None if payload is None else json.dumps(payload).encode("utf-8")
    request=urllib.request.Request(
        base+path,
        data=data,
        headers={
            "Authorization":f"Bearer {token}",
            "Content-Type":"application/json",
        },
        method="POST" if payload is not None else "GET",
    )
    with urllib.request.urlopen(request,timeout=3) as response:
        raw=response.read()
        return response.status,json.loads(raw or b"{}")


def test_claim_uses_portfolio_criticality(tmp_path):
    auth=TokenAuthorizer([
        {"name":"worker","role":"worker","sha256":token_digest("worker")},
    ])
    control=ControlPlane(str(tmp_path/"db.sqlite"),authorizer=auth)
    control.workers.register("w1",["python"],1)

    workflow=control.workflows.create(
        name="pipeline",
        repository="o/a",
        tasks=[
            WorkflowTaskSpec(
                "root","Root",
                {"required_capabilities":["python"]},
                priority=10,
                estimated_minutes=2,
            ),
            WorkflowTaskSpec(
                "middle","Middle",
                {"required_capabilities":["python"]},
                dependencies=("root",),
                priority=10,
                estimated_minutes=5,
            ),
            WorkflowTaskSpec(
                "end","End",
                {"required_capabilities":["python"]},
                dependencies=("middle",),
                priority=10,
                estimated_minutes=1,
            ),
        ],
    )
    control.workflows.dispatch_ready(workflow["id"])

    independent=control.queue.enqueue({
        "handoff":{
            "repository":"o/b",
            "task":"Independent",
            "priority":20,
        },
        "required_capabilities":["python"],
    })

    server=ThreadingHTTPServer(("127.0.0.1",0),make_handler(control))
    thread=threading.Thread(target=server.serve_forever,daemon=True)
    thread.start()
    base=f"http://127.0.0.1:{server.server_port}"
    try:
        _,claimed=api(base,"/v1/jobs/claim","worker",{
            "worker_id":"w1",
            "capabilities":["python"],
        })
        assert claimed["job"]["repository"]=="o/a"
        assert claimed["job"]["key"] != independent["key"]
        assert claimed["optimization"]["critical"] is True
        assert claimed["optimization"]["descendants"]==2
    finally:
        server.shutdown()
        server.server_close()
