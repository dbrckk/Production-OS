import json
import threading
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer

from production_os.api_auth import TokenAuthorizer, token_digest
from production_os.control_plane import ControlPlane, DASHBOARD_HTML, make_handler


def get_json(url, token):
    req = urllib.request.Request(
        url,
        headers={"Authorization": f"Bearer {token}"},
        method="GET",
    )
    with urllib.request.urlopen(req, timeout=3) as response:
        return response.status, json.loads(response.read() or b"{}")


def test_github_repository_picker_endpoint_returns_safe_fields(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "production_os.control_plane.GitHubClient.list_repositories",
        lambda self, owner: [
            {
                "name": "alpha",
                "full_name": f"{owner}/alpha",
                "private": False,
                "archived": False,
                "fork": False,
                "default_branch": "main",
                "pushed_at": "2026-09-18T12:00:00Z",
            },
            {
                "name": "beta",
                "full_name": f"{owner}/beta",
                "private": True,
                "archived": False,
                "fork": False,
                "default_branch": "trunk",
                "pushed_at": "2026-09-17T12:00:00Z",
            },
        ],
    )
    auth = TokenAuthorizer([
        {"name": "viewer", "role": "viewer", "sha256": token_digest("viewer")},
    ])
    control = ControlPlane(str(tmp_path / "db.sqlite"), authorizer=auth)
    server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(control))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{server.server_port}"
    try:
        status, body = get_json(
            base + "/v1/github/repositories?owner=dbrckk",
            "viewer",
        )
        assert status == 200
        assert body["owner"] == "dbrckk"
        assert [row["full_name"] for row in body["repositories"]] == [
            "dbrckk/alpha",
            "dbrckk/beta",
        ]
        assert body["repositories"][1]["private"] is True
        assert set(body["repositories"][0]) == {
            "name",
            "full_name",
            "private",
            "archived",
            "fork",
            "default_branch",
            "pushed_at",
        }
    finally:
        server.shutdown()
        server.server_close()


def test_dashboard_contains_managed_project_controls_and_token_bars():
    assert "/v1/github/repositories" in DASHBOARD_HTML
    assert "/v1/managed-projects" in DASHBOARD_HTML
    assert 'id="repo-list"' in DASHBOARD_HTML
    assert 'id="managed-projects"' in DASHBOARD_HTML
    assert 'id="global-token-progress"' in DASHBOARD_HTML
    assert "REVIEW_REQUIRED" in DASHBOARD_HTML
    assert "Mark done" in DASHBOARD_HTML
    assert "Retest" in DASHBOARD_HTML
    assert "Send instruction" in DASHBOARD_HTML
    assert "/instructions" in DASHBOARD_HTML
    assert "/verify" in DASHBOARD_HTML
