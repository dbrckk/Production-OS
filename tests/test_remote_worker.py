import json
import threading
from http.server import ThreadingHTTPServer

from production_os.api_auth import TokenAuthorizer, token_digest
import production_os.control_plane as control_plane
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


def test_remote_worker_detects_superseded_generation(tmp_path):
    auth=TokenAuthorizer([
        {"name":"worker","role":"worker","sha256":token_digest("worker")},
    ])
    control=ControlPlane(str(tmp_path/"db.sqlite"),authorizer=auth)
    control.workers.register("w1",["python"],1)

    original=control.workflows.create(
        name="pr-build",
        repository="o/a",
        metadata={
            "github_pr_number":12,
            "github_pr_head_sha":"sha-1",
            "github_pr_generation":1,
        },
        tasks=[
            control_plane.WorkflowTaskSpec(
                "tests",
                "Tests",
                {"required_capabilities":["python"]},
            ),
        ],
    )
    jobs=control.workflows.dispatch_ready(original["id"])
    assert len(jobs)==1

    server=ThreadingHTTPServer(
        ("127.0.0.1",0),
        make_handler(control),
    )
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
        assert job.key==jobs[0]["key"]
        client.ack(job.key)

        generation,_=control.workflows.ensure_pr_generation(
            "o/a",
            12,
            "sha-2",
        )
        assert generation is not None
        assert generation["id"]!=original["id"]

        heartbeat=client.heartbeat(
            active_tasks=1,
            active_job_keys=[job.key],
        )
        assert heartbeat["stale_job_keys"]==[job.key]

        checkpoint=client.checkpoint_stale(
            job.key,
            "checkpoint://worker/w1/job-1",
        )
        assert checkpoint["status"]=="checkpointed"
        events=control.backend.events_after(0,1000)
        checkpoint_events=[
            event
            for event in events
            if event["event_type"]=="stale-job-checkpointed"
        ]
        assert len(checkpoint_events)==1
        assert checkpoint_events[0]["payload"][
            "checkpoint_ref"
        ]=="checkpoint://worker/w1/job-1"

        try:
            client.complete(job.key)
        except RuntimeError as exc:
            assert "stale workflow generation" in str(exc)
        else:
            raise AssertionError("expected stale-generation rejection")
    finally:
        server.shutdown()
        server.server_close()

