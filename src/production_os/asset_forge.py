from __future__ import annotations

import hashlib
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
    reference_paths: list[str] | None = None,
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
        for reference_path in reference_paths or []:
            cmd.extend(["--reference", reference_path])
        completed = subprocess.run(
            cmd,
            check=False,
            capture_output=True,
            text=True,
        )
        if completed.returncode != 0:
            detail = (getattr(completed, "stderr", "") or getattr(completed, "stdout", "") or "").strip()
            suffix = f": {detail}" if detail else ""
            raise RuntimeError(
                f"asset-forge local execution failed with exit code {completed.returncode}{suffix}"
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

def _batch_item_id(item: dict[str, Any], index: int) -> str:
    explicit = str(item.get("id") or "").strip()
    request = item.get("request")
    request_id = str(request.get("requestId") or "").strip() if isinstance(request, dict) else ""
    value = explicit or request_id or f"item-{index + 1}"
    if not value:
        raise ValueError("asset-forge batch item id is required")
    return value


def _order_asset_batch(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    order_hint: list[str] = []
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            raise ValueError("asset-forge batch item must be an object")
        item_id = _batch_item_id(item, index)
        if item_id in indexed:
            raise ValueError(f"duplicate asset-forge batch item id: {item_id}")
        copy = dict(item)
        copy["_batch_id"] = item_id
        indexed[item_id] = copy
        order_hint.append(item_id)

    indegree = {item_id: 0 for item_id in indexed}
    dependents: dict[str, list[str]] = {item_id: [] for item_id in indexed}
    for item_id, item in indexed.items():
        raw = item.get("depends_on") or []
        if isinstance(raw, str):
            raw = [raw]
        if not isinstance(raw, list):
            raise ValueError(f"depends_on for {item_id} must be a list")
        dependencies = []
        for dep in raw:
            dep_id = str(dep).strip()
            if not dep_id:
                continue
            if dep_id == item_id:
                raise ValueError(f"asset-forge batch item cannot depend on itself: {item_id}")
            if dep_id not in indexed:
                raise ValueError(f"unknown asset-forge batch dependency for {item_id}: {dep_id}")
            if dep_id not in dependencies:
                dependencies.append(dep_id)
        item["_depends_on"] = dependencies
        indegree[item_id] = len(dependencies)
        for dep_id in dependencies:
            dependents[dep_id].append(item_id)

    ready = [item_id for item_id in order_hint if indegree[item_id] == 0]
    sorted_ids: list[str] = []
    while ready:
        current = ready.pop(0)
        sorted_ids.append(current)
        for dependent in dependents[current]:
            indegree[dependent] -= 1
            if indegree[dependent] == 0:
                ready.append(dependent)

    if len(sorted_ids) != len(indexed):
        blocked = [item_id for item_id in order_hint if indegree[item_id] > 0]
        raise ValueError(
            "cyclic asset-forge batch dependencies: " + ", ".join(blocked)
        )
    return [indexed[item_id] for item_id in sorted_ids]


def execute_asset_forge_batch(
    items: list[dict[str, Any]],
    *,
    backend: str = "auto",
    model: str | None = None,
    mode: str = "auto",
    output_root: str = "build/asset-forge-batch",
    target_repository: str | None = None,
    target_worktree: str | None = None,
    target_ref: str = "main",
    client: GitHubClient | None = None,
) -> dict[str, Any]:
    if not items:
        raise ValueError("asset-forge batch requires at least one item")

    root = Path(output_root)
    root.mkdir(parents=True, exist_ok=True)
    produced: list[dict[str, Any]] = []
    produced_by_id: dict[str, dict[str, Any]] = {}
    ordered_items = _order_asset_batch(items)

    for index, item in enumerate(ordered_items):
        dependency_artifacts = []
        for dependency_id in item.get("_depends_on") or []:
            dependency = produced_by_id.get(dependency_id)
            if dependency is None:
                raise RuntimeError(
                    f"asset dependency was not validated before execution: {dependency_id}"
                )
            dependency_artifacts.append({
                "id": dependency_id,
                "artifact": str(dependency["artifact"]),
                "sha256": dependency["sha256"],
            })
        request = item.get("request")
        if not isinstance(request, dict):
            raise ValueError("asset-forge batch item request is required")
        target_path = str(item.get("target_path") or "").strip()
        if not target_path:
            raise ValueError("asset-forge batch item target_path is required")
        source_path = str(item.get("source_path") or "").strip() or None
        request_id = str(request.get("requestId") or f"item-{index+1}")
        out = root / request_id

        raster_reference_suffixes = {".png", ".webp", ".jpg", ".jpeg"}
        visual_reference_paths = []
        if source_path is None:
            visual_reference_paths = [
                str(Path(dep["artifact"]))
                for dep in dependency_artifacts
                if Path(str(dep["artifact"])).suffix.lower() in raster_reference_suffixes
            ][:4]

        receipt = execute_asset_forge(
            request,
            backend=backend,
            model=model,
            mode=mode,
            output_dir=str(out),
            source_path=source_path,
            reference_paths=visual_reference_paths,
            target_repository=None,
            target_path=None,
            target_worktree=None,
            target_ref=target_ref,
            client=client,
        )
        if receipt.mode != "local":
            raise RuntimeError("transactional batch currently requires local asset-forge execution")
        report_path = Path(str(receipt.report_path))
        report = json.loads(report_path.read_text(encoding="utf-8"))
        artifact = _validated_artifact(report, out)
        produced_item = {
            "batch_id": item["_batch_id"],
            "depends_on": list(item.get("_depends_on") or []),
            "dependency_artifacts": dependency_artifacts,
            "visual_references": visual_reference_paths,
            "request_id": request_id,
            "target_path": target_path,
            "artifact": artifact,
            "sha256": hashlib.sha256(artifact.read_bytes()).hexdigest(),
            "report_path": report_path,
        }
        produced.append(produced_item)
        produced_by_id[item["_batch_id"]] = produced_item

    delivery_mode = None
    delivered_to: list[str] = []

    if target_worktree:
        root_worktree = Path(target_worktree).resolve()
        staged = []
        for item in produced:
            normalized = item["target_path"].replace("\\", "/").lstrip("/")
            destination = (root_worktree / normalized).resolve()
            if not destination.is_relative_to(root_worktree):
                raise ValueError("target_path escapes target worktree")
            staged.append((destination, item["artifact"]))

        backup_root = Path(tempfile.mkdtemp(prefix="production-os-asset-batch-backup-"))
        backups: list[tuple[Path, Path | None]] = []
        try:
            for destination, artifact in staged:
                destination.parent.mkdir(parents=True, exist_ok=True)
                backup = None
                if destination.exists():
                    backup = backup_root / str(len(backups))
                    backup.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(destination, backup)
                backups.append((destination, backup))
                shutil.copyfile(artifact, destination)
                delivered_to.append(str(destination))
        except Exception:
            for destination, backup in reversed(backups):
                if backup and backup.exists():
                    shutil.copyfile(backup, destination)
                elif destination.exists():
                    destination.unlink()
            raise
        finally:
            shutil.rmtree(backup_root, ignore_errors=True)
        delivery_mode = "worktree"

    elif target_repository:
        gh = client or GitHubClient()
        payload = {
            item["target_path"]: item["artifact"].read_bytes()
            for item in produced
        }
        result = gh.commit_files(
            target_repository,
            payload,
            message="assets: deliver validated asset batch",
            branch=target_ref,
        )
        delivered_to = [
            f"{target_repository}:{path}@{target_ref}"
            for path in result["files"]
        ]
        delivery_mode = "github"
    else:
        raise ValueError("target_worktree or target_repository is required for batch delivery")

    return {
        "schema_version": "production-os/asset-forge-batch/v1",
        "success": True,
        "count": len(produced),
        "execution_order": [item["batch_id"] for item in produced],
        "delivery_mode": delivery_mode,
        "delivered_to": delivered_to,
        "items": [
            {
                "id": item["batch_id"],
                "depends_on": item["depends_on"],
                "dependency_artifacts": item["dependency_artifacts"],
                "visual_references": item["visual_references"],
                "sha256": item["sha256"],
                "request_id": item["request_id"],
                "target_path": item["target_path"],
                "report_path": str(item["report_path"]),
            }
            for item in produced
        ],
    }


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
