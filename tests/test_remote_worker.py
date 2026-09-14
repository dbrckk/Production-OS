import json
import threading
from http.server import ThreadingHTTPServer

from production_os.api_auth import TokenAuthorizer, token_digest
from production_os.control_plane import ControlPlane, make_handler
from production_os.remote_worker import RemoteWorkerClient


def test_remote_worker_claim_ack_complete(tmp_path):
    auth=TokenAuthorizer([
        {"name":"op","role":"operator","sha256":token_digest("op")},
        {"name":"worker","role":"worker","sha256":token_digest("worker")},
    ])
    control=ControlPlane(str(tmp_path/"db.sqlite"),authorizer=auth)
    control.workers.register("w1",["python"],1)
    control.queue.enqueue({
        "handoff":{"repository":"o/a","task":"x"},
        "required_capabilities":["python"],
    })

    server=ThreadingHTTPServer(("127.0.0.1",0),make_handler(control))
    thread=threading.Thread(target=server.serve_forever,daemon=True)
    thread.start()
    try:
        client=RemoteWorkerClient(
            f"http://127.0.0.1:{server.server_port}",
            "worker",
            "w1",
            ["python"],
        )
        job=client.claim()
        assert job is not None
        assert client.ack(job.key)["status"]=="acked"
        assert client.complete(job.key)["status"]=="completed"
    finally:
        server.shutdown()
        server.server_close()
