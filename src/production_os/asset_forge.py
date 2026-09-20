from __future__ import annotations

import hashlib
import io
import json
import shutil
import subprocess
import tempfile
import uuid
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .github_client import GitHubClient


ASSET_FORGE_REPOSITORY = "dbrckk/asset-forge"
ASSET_FORGE_WORKFLOW = "production-os-dispatch.yml"
ASSET_FORGE_BATCH_WORKFLOW = "production-os-batch.yml"


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




def _request_fingerprint(
    request: dict[str, Any],
    dependency_artifacts: list[dict[str, Any]],
    *,
    source_path: str | None = None,
) -> str:
    canonical_request = {
        key: value
        for key, value in request.items()
        if key not in {"requestId", "delivery"}
    }
    source_sha256 = None
    if source_path:
        source = Path(source_path)
        if source.is_file():
            source_sha256 = hashlib.sha256(source.read_bytes()).hexdigest()
    payload = {
        "request": canonical_request,
        "dependencies": [
            {"id": value["id"], "sha256": value["sha256"]}
            for value in dependency_artifacts
        ],
        "source_sha256": source_sha256,
    }
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _sidecar_relative_path(target_path: str) -> str:
    return target_path.strip().replace("\\", "/").lstrip("/") + ".asset-forge.json"


def _cached_worktree_asset(
    worktree: str | None,
    target_path: str,
    fingerprint: str,
) -> tuple[Path, dict[str, Any]] | None:
    if not worktree:
        return None
    root = Path(worktree).resolve()
    normalized = target_path.strip().replace("\\", "/").lstrip("/")
    artifact = (root / normalized).resolve()
    sidecar = (root / _sidecar_relative_path(normalized)).resolve()
    if not artifact.is_relative_to(root) or not sidecar.is_relative_to(root):
        raise ValueError("target_path escapes target worktree")
    if not artifact.is_file() or not sidecar.is_file():
        return None
    try:
        metadata = json.loads(sidecar.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return None
    if not isinstance(metadata, dict):
        return None
    if metadata.get("schema_version") != "production-os/asset-version/v1":
        return None
    if str(metadata.get("request_fingerprint") or "") != fingerprint:
        return None
    digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
    if digest != str(metadata.get("sha256") or ""):
        return None
    return artifact, metadata


def _version_sidecar(
    item: dict[str, Any],
    *,
    existing: dict[str, Any] | None = None,
) -> dict[str, Any]:
    existing = existing if isinstance(existing, dict) else {}
    prior_sha = str(existing.get("sha256") or "")
    prior_version = int(existing.get("version") or 0)
    same = prior_sha == item["sha256"] and prior_version > 0
    version = prior_version if same else prior_version + 1
    history = list(existing.get("history") or []) if isinstance(existing.get("history"), list) else []
    if prior_version > 0 and not same:
        history.append({
            "version": prior_version,
            "sha256": prior_sha,
            "request_fingerprint": existing.get("request_fingerprint"),
        })
    history = history[-12:]
    return {
        "schema_version": "production-os/asset-version/v1",
        "asset_id": item["batch_id"],
        "request_id": item["request_id"],
        "target_path": item["target_path"],
        "version": version,
        "sha256": item["sha256"],
        "request_fingerprint": item["request_fingerprint"],
        "depends_on": item["depends_on"],
        "dependency_sha256": {
            value["id"]: value["sha256"]
            for value in item["dependency_artifacts"]
        },
        "cache_hit": bool(item.get("cache_hit")),
        "visual_similarity": item.get("visual_similarity"),
        "technical_art": item.get("technical_art"),
        "history": history,
    }


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



def _extract_remote_batch_bundle(data: bytes, destination: Path) -> Path:
    destination.mkdir(parents=True, exist_ok=True)
    root = destination.resolve()
    max_files = 5000
    max_uncompressed = 512 * 1024 * 1024
    total = 0
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        infos = archive.infolist()
        if len(infos) > max_files:
            raise RuntimeError("asset-forge remote batch artifact has too many files")
        for info in infos:
            name = info.filename.replace("\\", "/")
            if not name or name.endswith("/"):
                continue
            parts = [part for part in name.split("/") if part]
            if not parts or any(part in {".", ".."} for part in parts):
                raise RuntimeError("asset-forge remote batch artifact contains unsafe path")
            mode = (info.external_attr >> 16) & 0o170000
            if mode == 0o120000:
                raise RuntimeError("asset-forge remote batch artifact contains symlink")
            total += int(info.file_size)
            if total > max_uncompressed:
                raise RuntimeError("asset-forge remote batch artifact exceeds extraction limit")
            target = (root / "/".join(parts)).resolve()
            if not target.is_relative_to(root):
                raise RuntimeError("asset-forge remote batch artifact escapes extraction root")
            target.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(info) as source, target.open("wb") as output:
                shutil.copyfileobj(source, output)
    return root


def _produce_asset_forge_batch_remote(
    ordered_items: list[dict[str, Any]],
    *,
    root: Path,
    backend: str,
    model: str | None,
    client: GitHubClient | None,
    repository: str = ASSET_FORGE_REPOSITORY,
    workflow: str = ASSET_FORGE_BATCH_WORKFLOW,
    ref: str = "main",
) -> list[dict[str, Any]]:
    for item in ordered_items:
        if str(item.get("source_path") or "").strip():
            raise RuntimeError(
                "remote transactional batch does not accept local source_path inputs"
            )

    serializable_items = []
    for item in ordered_items:
        serializable_items.append({
            key: value
            for key, value in item.items()
            if not key.startswith("_")
        })
    spec_json = json.dumps(
        {"items": serializable_items},
        separators=(",", ":"),
        sort_keys=True,
    )
    if len(spec_json.encode("utf-8")) > 60_000:
        raise RuntimeError("asset-forge remote batch spec exceeds workflow input limit")

    correlation = "pos-" + uuid.uuid4().hex
    gh = client or GitHubClient()
    gh.dispatch_workflow(
        repository,
        workflow,
        ref=ref,
        inputs={
            "correlation_id": correlation,
            "spec_json": spec_json,
            "backend": backend,
            "model": model or "",
        },
    )
    title = f"Asset Forge batch {correlation}"
    run = gh.wait_for_workflow_run(
        repository,
        workflow,
        display_title=title,
        timeout_seconds=2100.0,
        poll_seconds=5.0,
    )
    if str(run.get("conclusion") or "") != "success":
        raise RuntimeError(
            "asset-forge remote batch workflow failed: "
            + str(run.get("html_url") or run.get("id") or title)
        )
    run_id = int(run.get("id") or 0)
    if run_id <= 0:
        raise RuntimeError("asset-forge remote batch workflow returned no run id")
    artifacts = gh.workflow_run_artifacts(repository, run_id)
    expected_name = f"asset-forge-batch-{correlation}"
    artifact = next(
        (
            value for value in artifacts
            if isinstance(value, dict)
            and str(value.get("name") or "") == expected_name
            and value.get("expired") is not True
        ),
        None,
    )
    if not artifact:
        raise RuntimeError("asset-forge remote batch workflow produced no correlated artifact")
    artifact_id = int(artifact.get("id") or 0)
    if artifact_id <= 0:
        raise RuntimeError("asset-forge remote batch artifact has no id")
    zip_bytes = gh.download_workflow_artifact(repository, artifact_id)

    remote_root = _extract_remote_batch_bundle(
        zip_bytes,
        root / f"remote-{correlation}",
    )
    result_path = remote_root / "batch-result.json"
    if not result_path.is_file():
        raise RuntimeError("asset-forge remote batch result is missing")
    result = json.loads(result_path.read_text(encoding="utf-8"))
    if (
        result.get("schema_version") != "asset-forge/remote-batch-result/v1"
        or result.get("success") is not True
    ):
        raise RuntimeError("asset-forge remote batch result is invalid")
    rows = result.get("items")
    if not isinstance(rows, list) or len(rows) != len(ordered_items):
        raise RuntimeError("asset-forge remote batch result item count mismatch")

    expected_by_id = {
        str(item["_batch_id"]): item
        for item in ordered_items
    }
    produced: list[dict[str, Any]] = []
    produced_by_id: dict[str, dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict):
            raise RuntimeError("asset-forge remote batch item is invalid")
        item_id = str(row.get("id") or "")
        expected = expected_by_id.get(item_id)
        if expected is None:
            raise RuntimeError(f"unexpected remote batch item: {item_id}")
        target_path = str(row.get("target_path") or "")
        if target_path != str(expected.get("target_path") or ""):
            raise RuntimeError(f"remote batch target mismatch for {item_id}")
        relative = Path(str(row.get("artifact") or ""))
        artifact_path = (remote_root / relative).resolve()
        if not artifact_path.is_relative_to(remote_root):
            raise RuntimeError(f"remote batch artifact escapes root for {item_id}")
        if not artifact_path.is_file():
            raise RuntimeError(f"remote batch artifact missing for {item_id}")
        digest = hashlib.sha256(artifact_path.read_bytes()).hexdigest()
        if digest != str(row.get("sha256") or ""):
            raise RuntimeError(f"remote batch artifact sha256 mismatch for {item_id}")
        dependencies = [str(value) for value in row.get("depends_on") or []]
        if dependencies != list(expected.get("_depends_on") or []):
            raise RuntimeError(f"remote batch dependency mismatch for {item_id}")
        dependency_artifacts = []
        for dependency_id in dependencies:
            dependency = produced_by_id.get(dependency_id)
            if dependency is None:
                raise RuntimeError(
                    f"remote batch dependency was not produced first: {dependency_id}"
                )
            dependency_artifacts.append({
                "id": dependency_id,
                "artifact": str(dependency["artifact"]),
                "sha256": dependency["sha256"],
            })
        visual_references = [
            str(Path(value["artifact"]))
            for value in dependency_artifacts
            if Path(str(value["artifact"])).suffix.lower()
            in {".png", ".webp", ".jpg", ".jpeg"}
        ][:4]
        request_id = str(row.get("request_id") or "")
        report_path = remote_root / "jobs" / request_id / "production-report.json"
        produced_item = {
            "batch_id": item_id,
            "depends_on": dependencies,
            "dependency_artifacts": dependency_artifacts,
            "visual_references": visual_references,
            "visual_similarity": (
                row.get("visual_similarity")
                if isinstance(row.get("visual_similarity"), dict)
                else None
            ),
            "technical_art": (
                row.get("technical_art")
                if isinstance(row.get("technical_art"), dict)
                else None
            ),
            "request_id": request_id,
            "target_path": target_path,
            "artifact": artifact_path,
            "sha256": digest,
            "report_path": report_path,
            "request_fingerprint": _request_fingerprint(
                expected["request"],
                dependency_artifacts,
            ),
            "cache_hit": False,
        }
        produced.append(produced_item)
        produced_by_id[item_id] = produced_item
    return produced



def _hex_hash_similarity(left: str, right: str) -> float | None:
    left = str(left or "").strip().lower()
    right = str(right or "").strip().lower()
    if not left or len(left) != len(right):
        return None
    try:
        left_value = int(left, 16)
        right_value = int(right, 16)
    except ValueError:
        return None
    bits = len(left) * 4
    distance = (left_value ^ right_value).bit_count()
    return 1.0 - distance / max(1, bits)


def _rgb_distance(left, right) -> float | None:
    if not (
        isinstance(left, list)
        and isinstance(right, list)
        and len(left) == 3
        and len(right) == 3
        and all(isinstance(value, (int, float)) for value in left + right)
    ):
        return None
    return sum((float(a) - float(b)) ** 2 for a, b in zip(left, right)) ** 0.5


def _asset_ancestors(produced: list[dict[str, Any]]) -> dict[str, set[str]]:
    direct = {
        str(item["batch_id"]): set(str(value) for value in item.get("depends_on") or [])
        for item in produced
    }
    memo: dict[str, set[str]] = {}

    def visit(item_id: str) -> set[str]:
        if item_id in memo:
            return memo[item_id]
        result = set(direct.get(item_id, set()))
        for dependency in list(result):
            result.update(visit(dependency))
        memo[item_id] = result
        return result

    for item_id in direct:
        visit(item_id)
    return memo


def _dedup_summary(produced: list[dict[str, Any]]) -> dict[str, Any]:
    exact = []
    near = []
    ancestors = _asset_ancestors(produced)
    for index, left in enumerate(produced):
        for right in produced[index + 1:]:
            left_id = str(left["batch_id"])
            right_id = str(right["batch_id"])
            if (
                left_id in ancestors.get(right_id, set())
                or right_id in ancestors.get(left_id, set())
            ):
                continue
            if left.get("sha256") == right.get("sha256"):
                exact.append({
                    "asset_ids": [left_id, right_id],
                    "sha256": left["sha256"],
                })
                continue
            left_art = left.get("technical_art")
            right_art = right.get("technical_art")
            left_metrics = (
                left_art.get("metrics")
                if isinstance(left_art, dict)
                and isinstance(left_art.get("metrics"), dict)
                else {}
            )
            right_metrics = (
                right_art.get("metrics")
                if isinstance(right_art, dict)
                and isinstance(right_art.get("metrics"), dict)
                else {}
            )
            similarity = _hex_hash_similarity(
                left_metrics.get("perceptualHash"),
                right_metrics.get("perceptualHash"),
            )
            color_distance = _rgb_distance(
                left_metrics.get("averageRgb"),
                right_metrics.get("averageRgb"),
            )
            if (
                similarity is not None
                and color_distance is not None
                and similarity >= 0.97
                and color_distance <= 30.0
            ):
                near.append({
                    "asset_ids": [left_id, right_id],
                    "perceptual_similarity": round(similarity, 6),
                    "average_rgb_distance": round(color_distance, 3),
                })
    return {
        "exact_duplicates": exact,
        "near_duplicates": near,
        "exact_count": len(exact),
        "near_count": len(near),
        "destructive_actions": 0,
    }


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

    target_paths = [
        str(item.get("target_path") or "").strip().replace("\\", "/").lstrip("/")
        for item in ordered_items
    ]
    if len(target_paths) != len(set(target_paths)):
        raise ValueError("asset-forge batch target_path values must be unique")

    effective_mode = mode
    if mode == "auto":
        effective_mode = "local" if shutil.which("asset-forge") else "github"
    if effective_mode == "github":
        produced = _produce_asset_forge_batch_remote(
            ordered_items,
            root=root,
            backend=backend,
            model=model,
            client=client,
        )
        produced_by_id = {
            item["batch_id"]: item
            for item in produced
        }
    else:
        if effective_mode != "local":
            raise ValueError("asset-forge mode must be auto, local, or github")

        for index, item in enumerate(ordered_items):
            dependency_artifacts = []
            for dependency_id in item.get("_depends_on") or []:
                dependency = produced_by_id.get(dependency_id)
                if dependency is None:
                    raise RuntimeError(
                        f"asset dependency was not validated before execution: {dependency_id}"
                    )
                dependency_path = Path(dependency["artifact"])
                current_sha256 = hashlib.sha256(dependency_path.read_bytes()).hexdigest()
                if current_sha256 != dependency["sha256"]:
                    raise RuntimeError(
                        f"validated asset dependency changed before use: {dependency_id}"
                    )
                dependency_artifacts.append({
                    "id": dependency_id,
                    "artifact": str(dependency_path),
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
            request_fingerprint = _request_fingerprint(
                request,
                dependency_artifacts,
                source_path=source_path,
            )
            cached = _cached_worktree_asset(
                target_worktree,
                target_path,
                request_fingerprint,
            )
            if cached is not None:
                cached_artifact, cached_metadata = cached
                produced_item = {
                    "batch_id": item["_batch_id"],
                    "depends_on": list(item.get("_depends_on") or []),
                    "dependency_artifacts": dependency_artifacts,
                    "visual_references": [
                        str(Path(dep["artifact"]))
                        for dep in dependency_artifacts
                        if Path(str(dep["artifact"])).suffix.lower()
                        in {".png", ".webp", ".jpg", ".jpeg"}
                    ][:4],
                    "visual_similarity": cached_metadata.get("visual_similarity"),
                    "technical_art": cached_metadata.get("technical_art"),
                    "request_id": request_id,
                    "target_path": target_path,
                    "artifact": cached_artifact,
                    "sha256": str(cached_metadata["sha256"]),
                    "report_path": out / "cache-hit.json",
                    "request_fingerprint": request_fingerprint,
                    "cache_hit": True,
                }
                produced.append(produced_item)
                produced_by_id[item["_batch_id"]] = produced_item
                continue

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
            generation = report.get("generation") if isinstance(report.get("generation"), dict) else {}
            validation = report.get("validation") if isinstance(report.get("validation"), dict) else {}
            visual_similarity = (
                generation.get("visualSimilarity")
                if isinstance(generation.get("visualSimilarity"), dict)
                else None
            )
            produced_item = {
                "batch_id": item["_batch_id"],
                "depends_on": list(item.get("_depends_on") or []),
                "dependency_artifacts": dependency_artifacts,
                "visual_references": visual_reference_paths,
                "visual_similarity": visual_similarity,
                "technical_art": (
                    validation.get("technicalArt")
                    if isinstance(validation.get("technicalArt"), dict)
                    else None
                ),
                "request_id": request_id,
                "target_path": target_path,
                "artifact": artifact,
                "sha256": hashlib.sha256(artifact.read_bytes()).hexdigest(),
                "report_path": report_path,
                "request_fingerprint": request_fingerprint,
                "cache_hit": False,
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
            sidecar_destination = (
                root_worktree / _sidecar_relative_path(normalized)
            ).resolve()
            if not sidecar_destination.is_relative_to(root_worktree):
                raise ValueError("asset sidecar escapes target worktree")
            existing = None
            if sidecar_destination.is_file():
                try:
                    value = json.loads(sidecar_destination.read_text(encoding="utf-8"))
                    existing = value if isinstance(value, dict) else None
                except (OSError, UnicodeError, json.JSONDecodeError):
                    existing = None
            sidecar = _version_sidecar(item, existing=existing)
            staged.append((destination, item["artifact"]))
            staged.append((
                sidecar_destination,
                json.dumps(sidecar, indent=2, sort_keys=True).encode("utf-8"),
            ))

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
                if isinstance(artifact, (bytes, bytearray)):
                    destination.write_bytes(bytes(artifact))
                elif Path(artifact).resolve() != destination.resolve():
                    shutil.copyfile(artifact, destination)
                if not destination.name.endswith(".asset-forge.json"):
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
        payload: dict[str, bytes] = {}
        for item in produced:
            payload[item["target_path"]] = item["artifact"].read_bytes()
            sidecar_path = _sidecar_relative_path(item["target_path"])
            existing = gh.read_json_file(target_repository, sidecar_path)
            sidecar = _version_sidecar(item, existing=existing)
            payload[sidecar_path] = (
                json.dumps(sidecar, indent=2, sort_keys=True) + "\n"
            ).encode("utf-8")
        result = gh.commit_files(
            target_repository,
            payload,
            message="assets: deliver validated asset batch",
            branch=target_ref,
        )
        delivered_to = [
            f"{target_repository}:{path}@{target_ref}"
            for path in result["files"]
            if not path.endswith(".asset-forge.json")
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
        "dedup_summary": _dedup_summary(produced),
        "quality_summary": {
            "checked": sum(1 for item in produced if item["visual_similarity"]),
            "regenerated": sum(
                1
                for item in produced
                if item["visual_similarity"]
                and len(item["visual_similarity"].get("attempts") or []) > 1
            ),
            "cache_hits": sum(1 for item in produced if item.get("cache_hit")),
            "minimum_score": min(
                (
                    float(item["visual_similarity"]["attempts"][-1]["score"])
                    for item in produced
                    if item["visual_similarity"]
                    and item["visual_similarity"].get("attempts")
                ),
                default=None,
            ),
        },
        "items": [
            {
                "id": item["batch_id"],
                "depends_on": item["depends_on"],
                "dependency_artifacts": item["dependency_artifacts"],
                "visual_references": item["visual_references"],
                "visual_similarity": item["visual_similarity"],
                "technical_art": item.get("technical_art"),
                "sha256": item["sha256"],
                "request_id": item["request_id"],
                "target_path": item["target_path"],
                "report_path": str(item["report_path"]),
                "request_fingerprint": item["request_fingerprint"],
                "cache_hit": bool(item.get("cache_hit")),
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
