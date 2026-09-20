from __future__ import annotations

import json
from dataclasses import dataclass
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

    def to_dict(self) -> dict[str, str]:
        return {
            "schema_version": "production-os/asset-forge-dispatch/v1",
            "repository": self.repository,
            "workflow": self.workflow,
            "ref": self.ref,
            "request_id": self.request_id,
            "backend": self.backend,
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
