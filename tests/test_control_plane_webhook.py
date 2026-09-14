import hashlib
import hmac
import json
import threading
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer

import production_os.control_plane as control_plane
from production_os.api_auth import TokenAuthorizer
from production_os.control_plane import ControlPlane, make_handler


def signed_request(url, payload, delivery="delivery-1", secret="secret"):
    body=json.dumps(payload).encode()
    sig="sha256="+hmac.new(
        secret.encode(),
        body,
        hashlib.sha256,
    ).hexdigest()
    req=urllib.request.Request(
        url,
        data=body,
        headers={
            "Content-Type":"application/json",
            "X-Hub-Signature-256":sig,
            "X-GitHub-Delivery":delivery,
            "X-GitHub-Event":"pull_request",
        },
        method="POST",
    )
    with urllib.request.urlopen(req,timeout=3) as response:
        return response.status, json.loads(response.read() or b"{}")


def test_signed_pr_webhook_refreshes_and_dispatches(tmp_path, monkeypatch):
    class FakeGitHubClient:
        def list_pull_request_files(self, repository, pr_number):
            assert repository=="o/a"
            assert pr_number==12
            return ["src/core.py"]

    monkeypatch.setattr(control_plane, "GitHubClient", FakeGitHubClient)

    control=ControlPlane(
        str(tmp_path/"db.sqlite"),
        authorizer=TokenAuthorizer([]),
        github_webhook_secret="secret",
    )
    workflow=control.workflows.create(
        name="pr-12",
        repository="o/a",
        metadata={
            "github_pr_number":12,
            "github_pr_head_sha":"oldsha",
            "github_pr_generation":1,
        },
        tasks=[
            control_plane.WorkflowTaskSpec(
                "src-tests",
                "Source tests",
                {
                    "impact":{
                        "paths":["src/**"],
                        "skip_when_unaffected":True,
                    }
                },
            ),
            control_plane.WorkflowTaskSpec(
                "docs-tests",
                "Docs tests",
                {
                    "impact":{
                        "paths":["docs/**"],
                        "skip_when_unaffected":True,
                    }
                },
            ),
        ],
    )

    server=ThreadingHTTPServer(
        ("127.0.0.1",0),
        make_handler(control),
    )
    thread=threading.Thread(target=server.serve_forever,daemon=True)
    thread.start()
    base=f"http://127.0.0.1:{server.server_port}"
    payload={
        "action":"synchronize",
        "repository":{"full_name":"o/a"},
        "pull_request":{
            "number":12,
            "head":{"sha":"newsha"},
        },
    }
    try:
        status,result=signed_request(
            base+"/v1/github/webhook",
            payload,
        )
        assert status==200
        assert result["status"]=="processed"
        assert result["refreshed"]==1
        assert result["head_sha"]=="newsha"
        assert result["superseded_workflows"]==[workflow["id"]]
        assert len(result["dispatched_jobs"])==1
        new_workflow_id=result["workflows"][0]["workflow_id"]
        assert new_workflow_id!=workflow["id"]
        assert result["dispatched_jobs"][0]["payload"][
            "workflow_id"
        ]==new_workflow_id
        old=control.workflows.get(workflow["id"])
        assert old["status"]=="cancelled"
        assert old["metadata"]["superseded"] is True

        status,duplicate=signed_request(
            base+"/v1/github/webhook",
            payload,
        )
        assert status==200
        assert duplicate["status"]=="duplicate"
    finally:
        server.shutdown()
        server.server_close()


def test_webhook_rejects_bad_signature(tmp_path):
    control=ControlPlane(
        str(tmp_path/"db.sqlite"),
        authorizer=TokenAuthorizer([]),
        github_webhook_secret="secret",
    )
    server=ThreadingHTTPServer(
        ("127.0.0.1",0),
        make_handler(control),
    )
    thread=threading.Thread(target=server.serve_forever,daemon=True)
    thread.start()
    base=f"http://127.0.0.1:{server.server_port}"
    body=b'{"action":"opened"}'
    req=urllib.request.Request(
        base+"/v1/github/webhook",
        data=body,
        headers={
            "Content-Type":"application/json",
            "X-Hub-Signature-256":"sha256=bad",
            "X-GitHub-Delivery":"delivery-bad",
            "X-GitHub-Event":"pull_request",
        },
        method="POST",
    )
    try:
        try:
            urllib.request.urlopen(req,timeout=3)
        except urllib.error.HTTPError as exc:
            assert exc.code==401
        else:
            raise AssertionError("expected HTTP 401")
    finally:
        server.shutdown()
        server.server_close()
