from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from base64 import b64decode
from typing import Any

from .models import RepoEvidence


class GitHubAPIError(RuntimeError):
    pass


class GitHubClient:
    API = "https://api.github.com"

    def __init__(self, token: str | None = None, timeout: float = 20.0):
        self.token = token or os.getenv("GITHUB_TOKEN")
        self.timeout = timeout

    def _get(self, path: str) -> Any:
        request = urllib.request.Request(
            f"{self.API}{path}",
            headers={
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "Production-OS/0.4",
                **({"Authorization": f"Bearer {self.token}"} if self.token else {}),
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise GitHubAPIError(f"GitHub API {exc.code}: {body}") from exc
        except urllib.error.URLError as exc:
            raise GitHubAPIError(f"GitHub API unavailable: {exc}") from exc

    def list_repositories(self, owner: str) -> list[dict[str, Any]]:
        repos: list[dict[str, Any]] = []
        page = 1
        while True:
            payload = self._get(
                f"/users/{urllib.parse.quote(owner)}/repos"
                f"?per_page=100&page={page}&sort=pushed&direction=desc"
            )
            if not payload:
                break
            repos.extend(payload)
            if len(payload) < 100:
                break
            page += 1
        return repos

    def _contents(self, full_name: str, path: str = "") -> list[dict[str, Any]]:
        encoded_path = "/".join(urllib.parse.quote(part) for part in path.split("/") if part)
        suffix = f"/{encoded_path}" if encoded_path else ""
        try:
            payload = self._get(f"/repos/{full_name}/contents{suffix}")
        except GitHubAPIError as exc:
            if "404" in str(exc):
                return []
            raise
        return payload if isinstance(payload, list) else [payload]

    def _read_text(self, full_name: str, path: str) -> str:
        try:
            payload = self._get(f"/repos/{full_name}/contents/{path}")
        except GitHubAPIError as exc:
            if "404" in str(exc):
                return ""
            raise
        encoded = payload.get("content")
        if not encoded:
            return ""
        try:
            return b64decode(encoded).decode("utf-8", errors="replace")
        except Exception:
            return ""

    def _latest_workflow_run(self, full_name: str, branch: str) -> dict[str, Any] | None:
        try:
            payload = self._get(
                f"/repos/{full_name}/actions/runs?per_page=10&branch="
                f"{urllib.parse.quote(branch)}"
            )
        except GitHubAPIError:
            return None
        runs = payload.get("workflow_runs", []) if isinstance(payload, dict) else []
        return runs[0] if runs else None

    def _collect_source_documents(self, full_name: str, names: set[str], workflow_names: list[str]) -> dict[str, str]:
        candidates = [
            "pyproject.toml", "requirements.txt", "package.json",
            "build.gradle", "build.gradle.kts", "settings.gradle.kts",
            "gradle.properties", "pom.xml", "Cargo.toml", "go.mod",
            "docker-compose.yml", "compose.yml", "compose.yaml",
            "Dockerfile",
        ]
        docs: dict[str, str] = {}
        for path in candidates:
            if path in names:
                text = self._read_text(full_name, path)
                if text:
                    docs[path] = text[:20000]

        for workflow in workflow_names[:12]:
            path = f".github/workflows/{workflow}"
            text = self._read_text(full_name, path)
            if text:
                docs[path] = text[:20000]

        return docs

    def collect_evidence(self, repo: dict[str, Any]) -> RepoEvidence:
        full_name = repo["full_name"]
        default_branch = repo.get("default_branch") or "main"
        root = self._contents(full_name)
        names = {item.get("name", "") for item in root}
        lower = {name.lower() for name in names}

        workflow_entries = self._contents(full_name, ".github/workflows")
        workflow_names = sorted(
            item.get("name", "") for item in workflow_entries if item.get("name")
        )
        workflow_lower = {name.lower() for name in workflow_names}
        github_entries = self._contents(full_name, ".github")
        github_names = {item.get("name", "").lower() for item in github_entries}
        latest_run = self._latest_workflow_run(full_name, default_branch) if workflow_names else None

        readme_name = next((n for n in names if n.lower().startswith("readme")), "")
        readme = self._read_text(full_name, readme_name) if readme_name else ""
        readme_lower = readme.lower()
        source_documents = self._collect_source_documents(full_name, names, workflow_names)

        manifest_names = {
            "pyproject.toml", "package.json", "pom.xml", "build.gradle",
            "build.gradle.kts", "cargo.toml", "go.mod", "requirements.txt",
            "composer.json", "gemfile",
        }
        test_markers = {"tests", "test", "spec", "src/test", "androidtest"}
        release_words = ("release", "publish", "deploy", "play", "store")
        roadmap_words = ("roadmap", "todo", "milestone")

        return RepoEvidence(
            name=repo["name"],
            full_name=full_name,
            html_url=repo.get("html_url", ""),
            default_branch=default_branch,
            archived=bool(repo.get("archived")),
            fork=bool(repo.get("fork")),
            private=bool(repo.get("private")),
            language=repo.get("language"),
            stars=int(repo.get("stargazers_count") or 0),
            forks=int(repo.get("forks_count") or 0),
            open_issues=int(repo.get("open_issues_count") or 0),
            pushed_at=repo.get("pushed_at"),
            has_readme=bool(readme_name),
            has_tests=bool(test_markers & lower)
            or "pytest" in readme_lower
            or "unit test" in readme_lower
            or "junit" in readme_lower,
            has_ci=bool(workflow_names),
            latest_ci_status=latest_run.get("status") if latest_run else None,
            latest_ci_conclusion=latest_run.get("conclusion") if latest_run else None,
            latest_ci_url=latest_run.get("html_url") if latest_run else None,
            has_release_workflow=any(
                any(word in workflow for word in release_words)
                for workflow in workflow_lower
            ),
            has_manifest=bool(manifest_names & lower),
            has_license=any(name.startswith("license") for name in lower),
            has_security_policy="security.md" in github_names or "security.md" in lower,
            has_dependency_automation="dependabot.yml" in github_names or "renovate.json" in lower,
            has_roadmap=any(word in name for name in lower for word in roadmap_words)
            or any(word in readme_lower for word in roadmap_words),
            readme_text=readme[:12000],
            detected_files=sorted(names),
            workflow_names=workflow_names,
            source_documents=source_documents,
        )
