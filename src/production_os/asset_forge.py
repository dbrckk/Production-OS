from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .github_client import GitHubClient


ASSET_FORGE_REPOSITORY = "dbrckk/asset-forge"
ASSET_FORGE_WORKFLOW = "production-os-dispatch.yml"


@dataclass(frozen=True)
class AssetForgeDispatch:
    repository: str
    workflow: str
    ref: str
    request_id: str
    backend: str
    mode: str = "github"
    report_path: str | None = None
    delivery_mode: str | None = None
    delivered_to: str | None = None

    def to_dict(self) -> dict[str, str]:
        return {
            "schema_version": "production-os/asset-forge-dispatch/v1",
            "repository": self.repository,
            "workflow": self.workflow,
            "ref": self.ref,
            "request_id": self.request_id,
            "backend": self.backend,
            "mode": self.mode,
            **({"report_path": self.report_path} if self.report_path else {}),
            **({"delivery_mode": self.delivery_mode} if self.delivery_mode else {}),
            **({"delivered_to": self.delivered_to} if self.delivered_to else {}),
        }


def build_asset_forge_request(
    *,
    request_id: str,
    project: str,
    asset_id: str,
    asset_type: str,
    instruction: str,
    target_format: str,
    importance: str = "primary",
    engine: str | None = None,
    output_dir: str | None = None,
    source_mode: str = "generated",
    source_uri: str | None = None,
    author: str | None = None,
    license_id: str = "generated",
) -> dict[str, Any]:
    request_id = str(request_id).strip()
    project = str(project).strip()
    asset_id = str(asset_id).strip()
    asset_type = str(asset_type).strip()
    instruction = str(instruction).strip()
    target_format = str(target_format).strip().lower()
    source_mode = str(source_mode).strip().lower()
    importance = str(importance).strip().lower()

    required = {
        "request_id": request_id,
        "project": project,
        "asset_id": asset_id,
        "asset_type": asset_type,
        "instruction": instruction,
        "target_format": target_format,
    }
    missing = [name for name, value in required.items() if not value]
    if missing:
        raise ValueError("missing asset-forge request fields: " + ", ".join(missing))
    if source_mode not in {"generated", "external", "custom"}:
        raise ValueError("source_mode must be generated, external, or custom")
    if importance not in {"primary", "secondary"}:
        raise ValueError("importance must be primary or secondary")

    request: dict[str, Any] = {
        "schema": "asset-forge/production-request/v1",
        "requestId": request_id,
        "instruction": instruction,
        "manifest": {
            "schema": "asset-forge/manifest/v1",
            "id": asset_id,
            "project": project,
            "type": asset_type,
            "importance": importance,
            "source": {
                "mode": source_mode,
                "uri": source_uri,
                "author": author,
            },
            "license": {
                "id": license_id,
                "commercialUse": True,
                "derivatives": True,
                "attributionRequired": False,
            },
            "target": {
                "format": target_format,
                "engine": engine,
            },
        },
    }
    if output_dir or engine:
        request["delivery"] = {}
        if output_dir:
            request["delivery"]["outputDir"] = output_dir
        if engine:
            request["delivery"]["engine"] = engine
    return request




def _validated_artifact(report: dict[str, Any], destination: Path) -> Path:
    raw = str(report.get("artifact") or "").strip()
    if not raw:
        raise RuntimeError("asset-forge production report has no artifact")
    artifact = Path(raw)
    if not artifact.is_absolute():
        candidate = destination / artifact
        if candidate.is_file():
            artifact = candidate
    if not artifact.is_file():
        raise RuntimeError("asset-forge production artifact is missing")
    resolved_destination = destination.resolve()
    resolved_artifact = artifact.resolve()
    if not resolved_artifact.is_relative_to(resolved_destination):
        raise RuntimeError("asset-forge production artifact escapes output directory")
    return artifact


def _deliver_artifact(
    artifact: Path,
    *,
    target_path: str,
    target_repository: str | None,
    target_worktree: str | None,
    target_ref: str,
    client: GitHubClient | None,
    request_id: str,
) -> tuple[str, str]:
    normalized = target_path.strip().replace("\\", "/").lstrip("/")
    if not normalized or normalized in {".", ".."} or any(part in {"", ".", ".."} for part in normalized.split("/")):
        raise ValueError("target_path must be a safe repository-relative path")

    if target_worktree:
        root = Path(target_worktree).resolve()
        destination = (root / normalized).resolve()
        if not destination.is_relative_to(root):
            raise ValueError("target_path escapes target worktree")
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(artifact, destination)
        return "worktree", str(destination)

    if not target_repository:
        raise ValueError("target_repository is required when no target_worktree is provided")
    gh = client or GitHubClient()
    gh.put_file(
        target_repository,
        normalized,
        artifact.read_bytes(),
        message=f"assets: deliver {request_id}",
        branch=target_ref,
    )
    return "github", f"{target_repository}:{normalized}@{target_ref}"


def execute_asset_forge(
    request: dict[str, Any],
    *,
    backend: str = "auto",
    model: str | None = None,
    mode: str = "auto",
    output_dir: str | None = None,
    source_path: str | None = None,
    target_repository: str | None = None,
    target_path: str | None = None,
    target_worktree: str | None = None,
    target_ref: str = "main",
    client: GitHubClient | None = None,
    repository: str = ASSET_FORGE_REPOSITORY,
    workflow: str = ASSET_FORGE_WORKFLOW,
    ref: str = "main",
) -> AssetForgeDispatch:
    if mode not in {"auto", "local", "github"}:
        raise ValueError("asset-forge mode must be auto, local, or github")

    local_cli = shutil.which("asset-forge")
    effective = mode
    if mode == "auto":
        effective = "local" if local_cli else "github"

    if effective == "github":
        return dispatch_asset_forge(
            request,
            client=client,
            repository=repository,
            workflow=workflow,
            ref=ref,
            backend=backend,
            model=model,
        )

    if not local_cli:
        raise RuntimeError("asset-forge CLI is required for local execution")

    request_id = str(request.get("requestId") or "").strip()
    if not request_id:
        raise ValueError("asset-forge requestId is required")
    destination = Path(output_dir or f"build/asset-forge/{request_id}")
    destination.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="production-os-asset-forge-") as tmp:
        request_path = Path(tmp) / "request.json"
        request_path.write_text(
            json.dumps(request, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        cmd = [
            local_cli,
            "fulfill",
            str(request_path),
            "--output-dir",
            str(destination),
            "--backend",
            backend,
        ]
        if model:
            cmd.extend(["--model", model])
        if source_path:
            cmd.extend(["--source", source_path])
        completed = subprocess.run(cmd, check=False)
        if completed.returncode != 0:
            raise RuntimeError(
                f"asset-forge local execution failed with exit code {completed.returncode}"
            )

    report_path = destination / "production-report.json"
    if not report_path.is_file():
        raise RuntimeError("asset-forge local execution produced no production report")
    report = json.loads(report_path.read_text(encoding="utf-8"))
    if report.get("success") is not True:
        raise RuntimeError("asset-forge production report indicates failure")
    artifact = _validated_artifact(report, destination)

    delivery_mode = None
    delivered_to = None
    if target_path:
        delivery_mode, delivered_to = _deliver_artifact(
            artifact,
            target_path=target_path,
            target_repository=target_repository,
            target_worktree=target_worktree,
            target_ref=target_ref,
            client=client,
            request_id=request_id,
        )

    return AssetForgeDispatch(
        repository=repository,
        workflow=workflow,
        ref=ref,
        request_id=request_id,
        backend=backend,
        mode="local",
        report_path=str(report_path),
        delivery_mode=delivery_mode,
        delivered_to=delivered_to,
    )

def dispatch_asset_forge(
    request: dict[str, Any],
    *,
    client: GitHubClient | None = None,
    repository: str = ASSET_FORGE_REPOSITORY,
    workflow: str = ASSET_FORGE_WORKFLOW,
    ref: str = "main",
    backend: str = "auto",
    model: str | None = None,
) -> AssetForgeDispatch:
    if request.get("schema") != "asset-forge/production-request/v1":
        raise ValueError("unsupported asset-forge production request schema")
    request_id = str(request.get("requestId") or "").strip()
    if not request_id:
        raise ValueError("asset-forge requestId is required")
    if backend not in {"auto", "pollinations", "imagen-codex"}:
        raise ValueError("unsupported asset-forge backend")

    inputs = {
        "request_json": json.dumps(request, separators=(",", ":"), sort_keys=True),
        "backend": backend,
        "model": model or "",
    }
    (client or GitHubClient()).dispatch_workflow(
        repository,
        workflow,
        ref=ref,
        inputs=inputs,
    )
    return AssetForgeDispatch(
        repository=repository,
        workflow=workflow,
        ref=ref,
        request_id=request_id,
        backend=backend,
    )
