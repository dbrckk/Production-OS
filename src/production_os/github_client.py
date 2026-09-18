from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from base64 import b64decode
from typing import Any

from .models import RepoEvidence
from .source_tree import TreeSamplePolicy, is_candidate_file, path_priority


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
                "User-Agent": "Production-OS/0.5",
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



    def get_branch_protection(
        self,
        full_name: str,
        branch: str,
    ) -> bool | None:
        encoded = urllib.parse.quote(branch, safe="")
        try:
            payload = self._get(
                f"/repos/{full_name}/branches/{encoded}/protection"
            )
        except GitHubAPIError as exc:
            if "404" in str(exc):
                return False
            return None
        return isinstance(payload, dict)

    def get_issue(self, full_name: str, issue_number: int) -> dict[str, Any] | None:
        try:
            payload = self._get(f"/repos/{full_name}/issues/{issue_number}")
        except GitHubAPIError:
            return None
        return payload if isinstance(payload, dict) else None

    def get_pull_request(self, full_name: str, pr_number: int) -> dict[str, Any] | None:
        try:
            payload = self._get(f"/repos/{full_name}/pulls/{pr_number}")
        except GitHubAPIError:
            return None
        return payload if isinstance(payload, dict) else None

    def get_pull_request_reviews(self, full_name: str, pr_number: int) -> list[dict[str, Any]]:
        try:
            payload = self._get(f"/repos/{full_name}/pulls/{pr_number}/reviews")
        except GitHubAPIError:
            return []
        return payload if isinstance(payload, list) else []


    def list_pull_request_files(
        self,
        full_name: str,
        pr_number: int,
    ) -> list[str]:
        """Return every changed path in a pull request.

        Unlike informational GitHub reads, this method intentionally propagates
        API failures. Incremental pruning must fail closed when the changed-file
        set cannot be established reliably.
        """
        files: list[str] = []
        page = 1
        while True:
            payload = self._get(
                f"/repos/{full_name}/pulls/{pr_number}/files"
                f"?per_page=100&page={page}"
            )
            if not isinstance(payload, list):
                raise GitHubAPIError(
                    "GitHub PR files response was not a list"
                )
            for item in payload:
                if not isinstance(item, dict):
                    continue
                filename = str(item.get("filename") or "").strip()
                if filename:
                    files.append(filename)
            if len(payload) < 100:
                break
            page += 1
        return sorted(set(files))

    def get_commit_workflow_runs(self, full_name: str, commit_sha: str) -> list[dict[str, Any]]:
        try:
            payload = self._get(
                f"/repos/{full_name}/actions/runs?head_sha={urllib.parse.quote(commit_sha)}&per_page=100"
            )
        except GitHubAPIError:
            return []
        if not isinstance(payload, dict):
            return []
        runs = payload.get("workflow_runs", [])
        return runs if isinstance(runs, list) else []

    def list_accessible_repositories(
        self,
        owner: str | None = None,
    ) -> list[dict[str, Any]]:
        """List repositories visible to the configured GitHub identity.

        Authenticated clients use /user/repos so private/collaborator/org
        repositories are included. Anonymous clients fall back to the public
        owner listing.
        """
        owner = str(owner or "").strip()
        if not self.token:
            if not owner:
                raise GitHubAPIError("GitHub owner is required without authentication")
            return self.list_repositories(owner)

        repos: list[dict[str, Any]] = []
        page = 1
        while True:
            payload = self._get(
                "/user/repos"
                f"?per_page=100&page={page}&sort=pushed&direction=desc"
                "&visibility=all"
                "&affiliation=owner%2Ccollaborator%2Corganization_member"
            )
            if not isinstance(payload, list):
                raise GitHubAPIError("GitHub repository listing was not a list")
            repos.extend(payload)
            if len(payload) < 100:
                break
            page += 1

        if not owner:
            return repos

        wanted = owner.casefold()
        return [
            repo
            for repo in repos
            if isinstance(repo, dict)
            and isinstance(repo.get("owner"), dict)
            and str(repo["owner"].get("login") or "").casefold() == wanted
        ]

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
        encoded_path = "/".join(urllib.parse.quote(part) for part in path.split("/") if part)
        try:
            payload = self._get(f"/repos/{full_name}/contents/{encoded_path}")
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

    def read_json_file(self, full_name: str, path: str) -> dict[str, Any] | None:
        text = self._read_text(full_name, path)
        if not text:
            return None
        try:
            value = json.loads(text)
        except json.JSONDecodeError:
            return None
        return value if isinstance(value, dict) else None

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

    def _recursive_tree_paths(self, full_name: str, ref: str) -> list[str]:
        try:
            payload = self._get(
                f"/repos/{full_name}/git/trees/{urllib.parse.quote(ref)}?recursive=1"
            )
        except GitHubAPIError:
            return []
        tree = payload.get("tree", []) if isinstance(payload, dict) else []
        return [
            item.get("path", "")
            for item in tree
            if item.get("type") == "blob" and item.get("path")
        ]

    def _collect_source_documents(
        self,
        full_name: str,
        names: set[str],
        workflow_names: list[str],
        default_branch: str,
        policy: TreeSamplePolicy | None = None,
    ) -> dict[str, str]:
        policy = policy or TreeSamplePolicy()
        candidates = [
            "pyproject.toml", "requirements.txt", "package.json",
            "build.gradle", "build.gradle.kts", "settings.gradle.kts",
            "gradle.properties", "pom.xml", "Cargo.toml", "go.mod",
            "docker-compose.yml", "compose.yml", "compose.yaml", "Dockerfile",
        ]
        docs: dict[str, str] = {}

        for path in candidates:
            if path in names:
                text = self._read_text(full_name, path)
                if text:
                    docs[path] = text[:policy.max_chars_per_file]

        for workflow in workflow_names[:12]:
            path = f".github/workflows/{workflow}"
            text = self._read_text(full_name, path)
            if text:
                docs[path] = text[:policy.max_chars_per_file]

        tree_paths = self._recursive_tree_paths(full_name, default_branch)
        nested = [
            path for path in tree_paths
            if path.count("/") <= policy.max_depth
            and is_candidate_file(path)
            and path not in docs
            and not path.lower().startswith(".github/")
        ]
        nested.sort(key=path_priority)

        remaining = max(policy.max_files - len(docs), 0)
        for path in nested[:remaining]:
            text = self._read_text(full_name, path)
            if text:
                docs[path] = text[:policy.max_chars_per_file]

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
        source_documents = self._collect_source_documents(
            full_name, names, workflow_names, default_branch
        )

        manifest_names = {
            "pyproject.toml", "package.json", "pom.xml", "build.gradle",
            "build.gradle.kts", "cargo.toml", "go.mod", "requirements.txt",
            "composer.json", "gemfile",
        }
        all_source_paths = {path.lower() for path in source_documents}
        has_tests = (
            any(
                "/test/" in f"/{path}/"
                or "/tests/" in f"/{path}/"
                or "androidtest" in path
                or path.startswith("tests/")
                for path in all_source_paths
            )
            or "pytest" in readme_lower
            or "unit test" in readme_lower
            or "junit" in readme_lower
        )
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
            has_tests=has_tests,
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
