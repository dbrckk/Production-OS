import json
import threading
import urllib.request
from http.server import ThreadingHTTPServer

from production_os.api_auth import TokenAuthorizer, token_digest
import production_os.control_plane as control_plane
from production_os.control_plane import ControlPlane, make_handler


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


def test_control_plane_applies_pr_changed_paths(tmp_path, monkeypatch):
    class FakeGitHubClient:
        def list_pull_request_files(self, repository, pr_number):
            assert repository=="o/a"
            assert pr_number==12
            return ["src/core.py"]

    monkeypatch.setattr(control_plane, "GitHubClient", FakeGitHubClient)

    auth=TokenAuthorizer([
        {"name":"op","role":"operator","sha256":token_digest("op")},
    ])
    control=ControlPlane(str(tmp_path/"db.sqlite"),authorizer=auth)
    workflow=control.workflows.create(
        name="incremental",
        repository="o/a",
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
    try:
        status,payload=request(
            base+f"/v1/workflows/{workflow['id']}/impact-pr",
            "op",
            {"repository":"o/a","pr_number":12},
        )
        assert status==200
        assert payload["changed_paths"]==["src/core.py"]
        tasks={
            task["task_id"]:task
            for task in payload["workflow"]["tasks"]
        }
        assert tasks["src-tests"]["status"]=="ready"
        assert tasks["docs-tests"]["status"]=="succeeded"
        assert tasks["docs-tests"]["result"]["skipped"] is True
    finally:
        server.shutdown()
        server.server_close()
