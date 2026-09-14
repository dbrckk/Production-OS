import json
import threading
import urllib.request
from http.server import ThreadingHTTPServer

from production_os.api_auth import TokenAuthorizer, token_digest
from production_os.attestations import create_validation_attestation
from production_os.control_plane import ControlPlane, make_handler
from production_os.workflow_engine import WorkflowTaskSpec


def get_request(url, token):
    req=urllib.request.Request(
        url,
        headers={
            "Authorization":f"Bearer {token}",
            "Accept":"application/json",
        },
        method="GET",
    )
    with urllib.request.urlopen(req,timeout=3) as response:
        return response.status, json.loads(response.read() or b"{}")


def request(url, token, payload):
    req=urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={
            "Authorization":f"Bearer {token}",
            "Content-Type":"application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req,timeout=3) as response:
        return response.status, json.loads(response.read() or b"{}")


def test_control_plane_promote_and_rollback_release(tmp_path):
    auth=TokenAuthorizer([
        {"name":"op","role":"operator","sha256":token_digest("op")},
    ])
    control=ControlPlane(
        str(tmp_path/"db.sqlite"),
        authorizer=auth,
        trusted_validation_secrets={
            "validator-1":"validator-secret"
        },
        provenance_secret="provenance-secret",
    )
    workflow=control.workflows.create(
        name="release",
        repository="o/a",
        metadata={
            "github_pr_number":12,
            "github_pr_head_sha":"sha-1",
            "github_pr_generation":1,
        },
        tasks=[WorkflowTaskSpec("build","Build",{})],
    )
    control.workflows.dispatch_ready(workflow["id"])
    control.workflows.record_result(
        workflow["id"],
        "build",
        succeeded=True,
    )
    artifact=control.workflows.add_artifact(
        workflow["id"],
        name="app.aab",
        uri="artifact://app.aab",
        sha256="aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        metadata={
            "source_revision":"sha-1",
            "workflow_generation":1,
        },
    )

    server=ThreadingHTTPServer(
        ("127.0.0.1",0),
        make_handler(control),
    )
    thread=threading.Thread(target=server.serve_forever,daemon=True)
    thread.start()
    base=f"http://127.0.0.1:{server.server_port}"
    try:
        validation={
            "status":"passed",
            "promotion_allowed":True,
            "blocking_failures":[],
        }
        attestation=create_validation_attestation(
            validator_id="validator-1",
            secret="validator-secret",
            workflow_id=workflow["id"],
            artifact_id=artifact["id"],
            artifact_sha256=artifact["sha256"],
            source_revision="sha-1",
            workflow_generation=1,
            validation=validation,
        )
        status,payload=request(
            base+f"/v1/workflows/{workflow['id']}/promote",
            "op",
            {
                "artifact_id":artifact["id"],
                "validation":validation,
                "attestation":attestation,
                "metadata":{"channel":"internal"},
            },
        )
        assert status==201
        promoted=payload["release"]
        assert promoted["status"]=="promoted"
        assert promoted["metadata"]["artifact_sha256"]=="aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
        assert promoted["metadata"]["approval"]["approved_by"]=="op"
        assert promoted["metadata"]["approval"]["role"]=="operator"

        status,verified=get_request(
            base+f"/v1/releases/{promoted['id']}/verify",
            "op",
        )
        assert status==200
        assert verified["verification"]["valid"] is True
        assert verified["verification"]["validator_id"]=="validator-1"

        status,payload=request(
            base+f"/v1/releases/{promoted['id']}/rollback",
            "op",
            {
                "reason":"regression",
                "metadata":{"incident":"INC-1"},
            },
        )
        assert status==201
        rollback=payload["release"]
        assert rollback["status"]=="rollback"
        assert rollback["rollback_of"]==promoted["id"]

        ledger=control.releases.list_for_workflow(workflow["id"])
        assert [row["status"] for row in ledger]==[
            "promoted",
            "rollback",
        ]
    finally:
        server.shutdown()
        server.server_close()
