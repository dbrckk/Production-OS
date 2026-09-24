from __future__ import annotations

import json
import threading
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer

from production_os.api_auth import TokenAuthorizer, token_digest
from production_os.control_plane import ControlPlane, make_handler
from production_os.github_client import GitHubAPIError


def _auth():
    return TokenAuthorizer([
        {"name":"viewer","role":"viewer","sha256":token_digest("viewer")},
        {"name":"operator","role":"operator","sha256":token_digest("operator")},
        {"name":"worker","role":"worker","sha256":token_digest("worker")},
    ])


def _server(control):
    server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(control))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread, f"http://127.0.0.1:{server.server_port}"


def _get(url, token=None, *, follow_redirects=True):
    request = urllib.request.Request(
        url,
        headers=(
            {"Authorization":f"Bearer {token}"}
            if token is not None
            else {}
        ),
        method="GET",
    )
    opener = urllib.request.build_opener()
    if not follow_redirects:
        class NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, req, fp, code, msg, headers, newurl):
                return None
        opener = urllib.request.build_opener(NoRedirect())
    try:
        with opener.open(request, timeout=3) as response:
            raw = response.read()
            content_type = response.headers.get("Content-Type", "")
            if "application/json" in content_type:
                return response.status, json.loads(raw or b"{}"), response.headers
            return response.status, raw.decode("utf-8"), response.headers
    except urllib.error.HTTPError as exc:
        raw = exc.read()
        try:
            payload = json.loads(raw or b"{}")
        except Exception:
            payload = raw.decode("utf-8", errors="replace")
        return exc.code, payload, exc.headers


def test_root_redirects_to_dashboard_and_health_stays_json(tmp_path):
    control = ControlPlane(str(tmp_path / "launch-ux.sqlite"), authorizer=_auth())
    server, thread, base = _server(control)
    try:
        status, _, headers = _get(base + "/", follow_redirects=False)
        assert status == 302
        assert headers["Location"] == "/dashboard"
        assert headers["Cache-Control"] == "no-store"

        status, payload, _ = _get(base + "/health")
        assert status == 200
        assert payload["status"] == "healthy"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_repository_picker_is_server_backed_sorted_and_excludes_archived(
    tmp_path,
    monkeypatch,
):
    control = ControlPlane(str(tmp_path / "repos.sqlite"), authorizer=_auth())

    def fake_repos(self, owner):
        assert owner == "dbrckk"
        return [
            {
                "full_name":"dbrckk/Zeta",
                "private":False,
                "archived":False,
                "default_branch":"main",
                "pushed_at":"2026-09-24T10:00:00Z",
            },
            {
                "full_name":"dbrckk/Alpha",
                "private":True,
                "archived":False,
                "default_branch":"main",
                "pushed_at":"2026-09-24T11:00:00Z",
            },
            {
                "full_name":"dbrckk/Archived",
                "private":False,
                "archived":True,
                "default_branch":"main",
                "pushed_at":"2026-09-24T12:00:00Z",
            },
        ]

    monkeypatch.setattr(
        "production_os.dashboard_service.GitHubClient.list_accessible_repositories",
        fake_repos,
    )

    server, thread, base = _server(control)
    try:
        status, payload, _ = _get(
            base + "/v1/dashboard/repositories",
            "viewer",
        )
        assert status == 200
        assert [x["full_name"] for x in payload["repositories"]] == [
            "dbrckk/Alpha",
            "dbrckk/Zeta",
        ]
        assert payload["repositories"][0]["private"] is True

        status, payload, _ = _get(
            base + "/v1/dashboard/repositories",
            "worker",
        )
        assert status == 403
        assert payload["error"] == "forbidden"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_repository_picker_falls_back_to_observed_projects_on_github_failure(
    tmp_path,
    monkeypatch,
):
    control = ControlPlane(
        str(tmp_path / "repos-fallback.sqlite"),
        authorizer=_auth(),
    )

    def fail_repos(self, owner):
        raise GitHubAPIError("offline")

    monkeypatch.setattr(
        "production_os.dashboard_service.GitHubClient.list_accessible_repositories",
        fail_repos,
    )
    monkeypatch.setattr(
        "production_os.dashboard_service.DashboardService.projects",
        lambda self: {
            "projects":[
                {"repository":"dbrckk/Zeta"},
                {"repository":"dbrckk/Alpha"},
            ],
            "generated_at":"2026-09-24T18:00:00+00:00",
        },
    )

    server, thread, base = _server(control)
    try:
        status, payload, _ = _get(
            base + "/v1/dashboard/repositories",
            "viewer",
        )
        assert status == 200
        assert payload["source"] == "observed-projects"
        assert [row["full_name"] for row in payload["repositories"]] == [
            "dbrckk/Alpha",
            "dbrckk/Zeta",
        ]
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
