#!/usr/bin/env python3
"""Actual pinned Asset Forge producer bundle -> Production-OS consumer -> Godot 4.

This is a functional integration smoke, not a new unit test. It uses only
locally authored original PNG pixels and the real Asset Forge CLI; no paid
inference, hosted dispatch, credentials, old canaries, or network is invoked.
"""
from __future__ import annotations

import hashlib
import io
from base64 import b64encode
import json
import os
import shlex
import sys
import tempfile
import zipfile
from pathlib import Path

from production_os.asset_forge import _deliver_produced_assets, build_asset_forge_request, execute_asset_forge, execute_asset_forge_batch
from production_os.github_client import GitHubAPIError, GitHubClient
from godot4_relocated_import_smoke import (
    OfflineClient,
    VALIDATOR,
    original_png,
    run as run_godot,
)


def main() -> None:
    godot_bin = os.environ.get("GODOT_BIN", "").strip()
    source_dir = os.environ.get("ASSET_FORGE_SOURCE_DIR", "").strip()
    if not godot_bin or not source_dir:
        raise RuntimeError("GODOT_BIN and ASSET_FORGE_SOURCE_DIR are mandatory")
    godot = str(Path(godot_bin).resolve(strict=True))
    forge_dir = Path(source_dir).resolve(strict=True)
    if not (forge_dir / "asset_forge.py").is_file():
        raise RuntimeError("Pinned Asset Forge CLI entry not found")
    if str(forge_dir) not in sys.path:
        sys.path.insert(0, str(forge_dir))
    from remote_batch import run as run_real_producer

    with tempfile.TemporaryDirectory(prefix="godot-cross-repo-contract-") as temp:
        root = Path(temp)
        originals = root / "original-art"
        originals.mkdir()
        image = originals / "owned-player.png"
        image_bytes = original_png()
        image.write_bytes(image_bytes)

        request = build_asset_forge_request(
            request_id="godot-real-producer-consumer-contract",
            project="original-owned-smoke",
            asset_id="player",
            asset_type="sprite-sheet",
            instruction="Export two originally authored frames for Godot 4",
            target_format="png",
            engine="godot4",
            source_mode="custom",
            author="original-ci",
            license_id="project-owned",
        )
        request["manifest"]["constraints"] = {
            "pixelArt": True,
            "interpolation": "nearest",
            "frameWidth": 32,
            "frameHeight": 32,
            "expectedFrames": 2,
            "requiresAlpha": True,
        }
        target = "assets/characters/player.png"
        item = {"id": "player", "request": request,
                "target_path": target, "source_path": str(image)}
        spec = root / "producer-spec.json"
        spec.write_text(json.dumps({"items": [item]}), encoding="utf-8")

        # Keep CLI execution self-contained and deterministic without any
        # provider credential, model selection, or remote source paths.
        bin_dir = root / "bin"
        bin_dir.mkdir()
        wrapper = bin_dir / "asset-forge"
        wrapper.write_text(
            "#!/bin/sh\nexec " + shlex.quote(sys.executable) + " "
            + shlex.quote(str(forge_dir / "asset_forge.py")) + ' "$@"\n',
            encoding="utf-8",
        )
        wrapper.chmod(0o700)
        produced_root = root / "native-bundle"
        original_root = os.environ.get("ASSET_FORGE_BATCH_SOURCE_ROOT")
        os.environ["ASSET_FORGE_BATCH_SOURCE_ROOT"] = str(originals.resolve())
        try:
            produced = run_real_producer(
                spec, produced_root, executable=str(wrapper), backend="auto"
            )
        finally:
            if original_root is None:
                os.environ.pop("ASSET_FORGE_BATCH_SOURCE_ROOT", None)
            else:
                os.environ["ASSET_FORGE_BATCH_SOURCE_ROOT"] = original_root

        if produced.get("success") is not True or produced.get("count") != 1:
            raise RuntimeError("Real Asset Forge batch did not produce one successful job")
        row = produced["items"][0]
        roles = {comp.get("role") for comp in row.get("additional_artifacts") or []}
        if roles != {"godot-spriteframes", "godot-atlas-metadata"}:
            raise RuntimeError("Real Asset Forge batch lacked required Godot companion roles")

        # Produce exactly the ZIP layout the GitHub workflow uploads from
        # the real remote_batch output tree, not synthetic report fixtures.
        archive_bytes = io.BytesIO()
        with zipfile.ZipFile(archive_bytes, "w", zipfile.ZIP_DEFLATED) as archive:
            for path in sorted(produced_root.rglob("*")):
                if path.is_file():
                    archive.write(
                        path, arcname=path.relative_to(produced_root).as_posix()
                    )
        source_archive = archive_bytes.getvalue()
        dispatch_item = {"id": item["id"], "request": request, "target_path": target}

        consumer = root / "verified-consumer"
        consumer.mkdir()
        (consumer / "project.godot").write_text(
            'config_version=5\n[application]\nconfig/name="Cross repo consumer"\n'
            '[rendering]\nrenderer/rendering_method="gl_compatibility"\n',
            encoding="utf-8",
        )
        (consumer / "verify.gd").write_text(VALIDATOR, encoding="utf-8")
        delivered = execute_asset_forge_batch(
            [dispatch_item],
            mode="github",
            output_root=str(root / "consumer-receipt"),
            target_worktree=str(consumer),
            client=OfflineClient(source_archive),
        )
        if delivered.get("success") is not True or delivered.get("count") != 1:
            raise RuntimeError("Production-OS rejected the genuine producer bundle")
        if (consumer / target).read_bytes() != image_bytes:
            raise RuntimeError("Real producer original PNG changed during delivery")
        version = json.loads(
            (consumer / (target + ".asset-forge.json")).read_text(encoding="utf-8")
        )
        if len(version.get("companions") or []) != 2:
            raise RuntimeError("Consumer did not preserve both companion digests")
        for companion in version["companions"]:
            resource = consumer / companion["target_path"]
            if hashlib.sha256(resource.read_bytes()).hexdigest() != companion["sha256"]:
                raise RuntimeError("Delivered Godot companion SHA256 mismatch")
        run_godot([godot, "--headless", "--path", str(consumer), "--import"], cwd=root)
        run_godot(
            [godot, "--headless", "--path", str(consumer),
             "--script", "res://verify.gd"],
            cwd=root, marker="GODOT_RELOCATED_SPRITEFRAMES_OK",
        )

        # Direct GitHub-mode single-asset calls must no longer return a mere
        # dispatch receipt when a consumer delivery was explicitly requested.
        single = root / "direct-github-consumer"
        single.mkdir()
        (single / "project.godot").write_bytes((consumer / "project.godot").read_bytes())
        (single / "verify.gd").write_text(VALIDATOR, encoding="utf-8")
        direct = execute_asset_forge(
            request, mode="github", target_path=target,
            target_worktree=str(single),
            output_dir=str(root / "direct-github-receipt"),
            client=OfflineClient(source_archive),
        )
        if direct.delivery_mode != "worktree" or direct.delivered_to != str((single / target).resolve()):
            raise RuntimeError("Direct remote single-asset delivery returned dispatch-only state")
        if (single / target).read_bytes() != image_bytes:
            raise RuntimeError("Direct remote consumer PNG does not match producer")
        direct_version = json.loads(
            (single / (target + ".asset-forge.json")).read_text(encoding="utf-8")
        )
        if len(direct_version.get("companions") or []) != 2:
            raise RuntimeError("Direct remote consumer lost Godot SpriteFrames sidecars")
        run_godot([godot, "--headless", "--path", str(single), "--import"], cwd=root)
        run_godot(
            [godot, "--headless", "--path", str(single),
             "--script", "res://verify.gd"], cwd=root,
            marker="GODOT_RELOCATED_SPRITEFRAMES_OK",
        )
        # Refuse to dispatch a billed remote generation when delivery would
        # silently write a repository's default branch without PR review.
        try:
            execute_asset_forge(
                request, mode="github", target_path=target,
                target_repository="dbrckk/consumer",
                client=OfflineClient(source_archive),
            )
        except ValueError as exc:
            if "non-default review branch" not in str(exc):
                raise
        else:
            raise RuntimeError("Remote single-asset attempted implicit main-branch delivery")

        # Existing end-to-end smoke also verifies destination preflight.
        # None of these cases may dispatch, generate, or create receipt files.
        bad_receipt = root / "blocked-path-receipt"
        for unsafe in ("../escape.png", "/absolute.png", "assets/./sprite.png",
                       "assets//sprite.png", "C:\\Windows\\sprite.png",
                       "assets/../sprite.png"):
            try:
                execute_asset_forge_batch(
                    [{"id": "player", "request": request, "target_path": unsafe}],
                    mode="github", output_root=str(bad_receipt),
                    target_worktree=str(consumer), client=OfflineClient(source_archive),
                )
            except ValueError:
                pass
            else:
                raise RuntimeError(f"Unsafe batch destination was accepted: {unsafe!r}")
        for second in ("assets/PLAYER.png", "assets/cafe\u0301.png"):
            first = "assets/player.png" if "PLAYER" in second else "assets/café.png"
            try:
                execute_asset_forge_batch(
                    [{"id": "first", "request": request, "target_path": first},
                     {"id": "second", "request": request, "target_path": second}],
                    mode="github", output_root=str(bad_receipt),
                    target_worktree=str(consumer), client=OfflineClient(source_archive),
                )
            except ValueError:
                pass
            else:
                raise RuntimeError("Equivalent batch destinations bypassed preflight")
        if bad_receipt.exists():
            raise RuntimeError("Unsafe target path started a remote batch before preflight")

        # Verify real GitHub Contents ref encoding and branch-specific
        # version continuity using an offline recording client.
        class OfflineReviewBranch(GitHubClient):
            def __init__(self, receipt=None):
                self.read_paths = []
                self.written_files = {}
                self.written_branch = None
                self.receipt = (
                    json.dumps({"version": 7, "sha256": "previous-image-digest"})
                    if receipt is None else receipt
                )

            def _get(self, path):
                self.read_paths.append(path)
                return {"content": b64encode(self.receipt.encode()).decode()}

            def commit_files(self, repository, files, *, message, branch):
                self.written_branch = branch
                self.written_files = dict(files)
                return {"files": sorted(files)}

        review_ref = "review/asset-handoff"
        review_item = {
            "batch_id": "player",
            "request_id": request["requestId"],
            "target_path": target,
            "artifact": image,
            "sha256": hashlib.sha256(image_bytes).hexdigest(),
            "request_fingerprint": "original-review-branch-smoke",
            "depends_on": [],
            "dependency_artifacts": [],
            "companion_files": [],
            "cache_hit": False,
        }
        github = OfflineReviewBranch()
        delivery_mode, delivered_files = _deliver_produced_assets(
            [review_item],
            target_repository="dbrckk/consumer",
            target_worktree=None,
            target_ref=review_ref,
            client=github,
        )
        expected_url = (
            "/repos/dbrckk/consumer/contents/"
            + target + ".asset-forge.json?ref=review%2Fasset-handoff"
        )
        if github.read_paths != [expected_url]:
            raise RuntimeError("GitHub version lookup ignored review branch ref")
        if delivery_mode != "github" or github.written_branch != review_ref:
            raise RuntimeError("Asset delivery wrote to an unexpected GitHub branch")
        if not delivered_files or not github.written_files:
            raise RuntimeError("Review branch delivery did not prepare atomic GitHub payload")
        version = json.loads(github.written_files[target + ".asset-forge.json"].decode("utf-8"))
        if version.get("version") != 8 or version.get("history", [{}])[-1].get("version") != 7:
            raise RuntimeError("Review branch asset history did not advance version 7 to 8")

        # A corrupt existing receipt cannot be silently replaced with version 1.
        # The actual GitHubClient must reject malformed JSON before commit_files.
        for malformed in ('{"version":', '[]'):
            blocked = OfflineReviewBranch(receipt=malformed)
            try:
                _deliver_produced_assets(
                    [review_item], target_repository="dbrckk/consumer",
                    target_worktree=None, target_ref=review_ref, client=blocked,
                )
            except GitHubAPIError:
                pass
            else:
                raise RuntimeError("GitHub delivery silently reset a corrupt version receipt")
            if blocked.written_files:
                raise RuntimeError("Corrupt GitHub receipt triggered a commit")

        # The real worktree delivery path must also refuse malformed history
        # before touching the existing PNG, sidecars or the corrupt metadata.
        local_sidecar = consumer / (target + ".asset-forge.json")
        original_sidecar = local_sidecar.read_bytes()
        original_artifact = (consumer / target).read_bytes()
        local_sidecar.write_text('{"version":', encoding="utf-8")
        try:
            try:
                _deliver_produced_assets(
                    [review_item], target_repository=None,
                    target_worktree=str(consumer), target_ref="main", client=None,
                )
            except RuntimeError as exc:
                if "existing asset version receipt" not in str(exc):
                    raise
            else:
                raise RuntimeError("Worktree delivery silently reset a corrupt receipt")
            if (consumer / target).read_bytes() != original_artifact:
                raise RuntimeError("Refused worktree delivery changed the existing asset")
            if local_sidecar.read_text(encoding="utf-8") != '{"version":':
                raise RuntimeError("Refused worktree delivery rewrote corrupt metadata")
        finally:
            local_sidecar.write_bytes(original_sidecar)

        # Tamper with the REAL producer .tres byte payload but preserve its
        # real declared checksum; fail closed before any consumer file write.
        tres_path = next(
            entry["artifact"] for entry in row["additional_artifacts"]
            if entry.get("role") == "godot-spriteframes"
        )
        tampered_zip = io.BytesIO()
        with zipfile.ZipFile(io.BytesIO(source_archive), "r") as genuine:
            with zipfile.ZipFile(tampered_zip, "w", zipfile.ZIP_DEFLATED) as corrupted:
                for member in genuine.infolist():
                    content = genuine.read(member.filename)
                    if member.filename == tres_path:
                        content += b"\n; tampered original resource\n"
                    corrupted.writestr(member, content)
        rejected_root = root / "rejected-consumer"
        rejected_root.mkdir()
        try:
            execute_asset_forge_batch(
                [dispatch_item],
                mode="github",
                output_root=str(root / "rejected-receipt"),
                target_worktree=str(rejected_root),
                client=OfflineClient(tampered_zip.getvalue()),
            )
        except RuntimeError:
            pass
        else:
            raise RuntimeError("Consumer accepted a tampered genuine producer ZIP")
        if (rejected_root / target).exists():
            raise RuntimeError("Rejected producer archive partially delivered an asset")

        print("PASS: REAL Asset Forge remote_batch -> Production-OS -> Godot 4")
        print("PASS: Native batch-result/report, sidecar SHA256 and Godot resource load")
        print("PASS: Direct GitHub-mode single-asset transaction + Godot import")
        print("PASS: Implicit main-branch remote delivery refused before dispatch")
        print("PASS: Review-branch version lookup/transaction remains on target ref")
        print("PASS: Corrupt existing GitHub/worktree version receipts rejected before delivery")
        print("PASS: Tampered real producer SpriteFrames rejected before delivery")


if __name__ == "__main__":
    main()
