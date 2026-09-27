from __future__ import annotations

import hashlib
import re


_SCHEMA = "production-os/git-worktree-isolation/v1"


def _slug(value: str, *, limit: int = 32) -> str:
    text = re.sub(r"[^a-zA-Z0-9._-]+", "-", str(value or "").strip())
    text = re.sub(r"-+", "-", text).strip("-.").lower()
    return (text or "task")[:limit]


def build_worktree_contract(
    *,
    repository: str,
    workflow_id: str,
    task_id: str,
    attempt: int,
    base_ref: str | None = None,
    integration_target: bool = False,
) -> dict:
    if int(attempt) < 1:
        raise ValueError("attempt must be >= 1")
    repository = str(repository or "").strip()
    workflow_id = str(workflow_id or "").strip()
    task_id = str(task_id or "").strip()
    if not repository or not workflow_id or not task_id:
        raise ValueError("repository, workflow_id and task_id are required")

    digest = hashlib.sha256(
        f"{repository}\0{workflow_id}\0{task_id}\0{attempt}".encode("utf-8")
    ).hexdigest()[:12]
    branch = (
        "production-os/"
        f"{_slug(workflow_id, limit=20)}/"
        f"{_slug(task_id, limit=28)}-a{int(attempt)}-{digest}"
    )
    workspace_key = f"{_slug(task_id, limit=20)}-{digest}"
    return {
        "schema_version":_SCHEMA,
        "mode":"git-worktree",
        "repository":repository,
        "workflow_id":workflow_id,
        "task_id":task_id,
        "attempt":int(attempt),
        "branch":branch,
        "workspace_key":workspace_key,
        "base_ref":str(base_ref or "HEAD"),
        "integration_target":bool(integration_target),
        "requirements":{
            "exclusive_workspace":True,
            "no_shared_working_tree_writes":True,
            "commit_changes_before_success":True,
            "report_commit_shas":True,
        },
    }
