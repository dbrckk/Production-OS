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



def execute_asset_forge(
    request: dict[str, Any],
    *,
    backend: str = "auto",
    model: str | None = None,
    mode: str = "auto",
    output_dir: str | None = None,
    source_path: str | None = None,
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

    return AssetForgeDispatch(
        repository=repository,
        workflow=workflow,
        ref=ref,
        request_id=request_id,
        backend=backend,
        mode="local",
        report_path=str(report_path),
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
