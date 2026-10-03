from __future__ import annotations

import json
from types import SimpleNamespace

import production_os.dashboard_service as dashboard_service
from production_os.dashboard_service import DashboardService
from production_os.github_client import GitHubAPIError


class FailingGitHub:
    def list_accessible_repositories(self, owner):
        raise GitHubAPIError("rate limited")


class LiveGitHub:
    def list_accessible_repositories(self, owner):
        return [
            {
                "full_name": f"{owner}/Jumpy",
                "private": False,
                "archived": False,
                "default_branch": "develop",
                "pushed_at": "2026-10-03T09:00:00Z",
            },
            {
                "full_name": f"{owner}/live-only",
                "private": False,
                "archived": False,
                "default_branch": "main",
                "pushed_at": "2026-10-03T10:00:00Z",
            },
        ]


def _service():
    service = DashboardService(SimpleNamespace(dashboard_store=object()))
    service.projects = lambda: {
        "projects": [
            {"repository": "dbrckk/observed-only"},
        ]
    }
    return service


def _catalog(tmp_path):
    path = tmp_path / "repository-catalog.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": "production-os/repository-catalog/v1",
                "owner": "dbrckk",
                "repositories": [
                    {
                        "full_name": "dbrckk/Jumpy",
                        "private": False,
                        "archived": False,
                        "default_branch": "main",
                        "pushed_at": None,
                    },
                    {
                        "full_name": "dbrckk/catalog-only",
                        "private": False,
                        "archived": False,
                        "default_branch": "main",
                        "pushed_at": None,
                    },
                ],
            }
        ),
        encoding="utf-8",
    )
    return path


def test_repositories_keep_catalog_and_observed_projects_when_github_fails(
    tmp_path,
    monkeypatch,
):
    monkeypatch.setenv("PRODUCTION_OS_REPOSITORY_CATALOG", str(_catalog(tmp_path)))
    monkeypatch.setattr(dashboard_service, "GitHubClient", lambda: FailingGitHub())

    payload = _service().repositories()

    assert payload["source"] == "catalog"
    assert [item["full_name"] for item in payload["repositories"]] == [
        "dbrckk/catalog-only",
        "dbrckk/Jumpy",
        "dbrckk/observed-only",
    ]


def test_repositories_merge_live_github_over_catalog_metadata(
    tmp_path,
    monkeypatch,
):
    monkeypatch.setenv("PRODUCTION_OS_REPOSITORY_CATALOG", str(_catalog(tmp_path)))
    monkeypatch.setattr(dashboard_service, "GitHubClient", lambda: LiveGitHub())

    payload = _service().repositories()
    by_name = {item["full_name"]: item for item in payload["repositories"]}

    assert payload["source"] == "github"
    assert by_name["dbrckk/Jumpy"]["default_branch"] == "develop"
    assert by_name["dbrckk/Jumpy"]["pushed_at"] == "2026-10-03T09:00:00Z"
    assert "dbrckk/catalog-only" in by_name
    assert "dbrckk/observed-only" in by_name
    assert "dbrckk/live-only" in by_name
