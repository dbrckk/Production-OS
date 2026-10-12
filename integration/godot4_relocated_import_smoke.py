#!/usr/bin/env python3
"""Offline Production-OS remote delivery -> real Godot 4 editor/runtime smoke.

Generates an ORIGINAL local RGBA PNG and SpriteFrames with the actual Godot
editor, then passes the hashed bytes through the real Production-OS remote
batch parser and transactional worktree delivery. No inference, token, network
dispatch, external art or new unit tests. GODOT_BIN must point to Godot 4.
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import shlex
import struct
import subprocess
import sys
import tempfile
import zlib
import zipfile
from pathlib import Path

from production_os.asset_forge import (build_asset_forge_request, execute_asset_forge, execute_asset_forge_batch)


GENERATOR = """extends SceneTree

func _init() -> void:
    var image: Texture2D = load("res://player.png")
    if image == null:
        push_error("Original PNG not imported")
        quit(1)
        return
    var frames := SpriteFrames.new()
    if not frames.has_animation("default"):
        frames.add_animation("default")
    for index in range(2):
        var region := AtlasTexture.new()
        region.atlas = image
        region.region = Rect2(index * 32, 0, 32, 32)
        frames.add_frame("default", region)
    if ResourceSaver.save(frames, "res://player.tres") != OK:
        push_error("Original SpriteFrames save failed")
        quit(2)
        return
    print("GODOT_ORIGINAL_RESOURCE_SAVED")
    quit()
"""

VALIDATOR = """extends SceneTree

func _init() -> void:
    var frames: SpriteFrames = load("res://assets/characters/player.tres")
    if frames == null or not frames.has_animation("default"):
        push_error("Relocated SpriteFrames failed to load")
        quit(1)
        return
    if frames.get_frame_count("default") != 2:
        push_error("Relocated resource lost frames")
        quit(2)
        return
    for index in range(2):
        var frame: Texture2D = frames.get_frame_texture("default", index)
        if not (frame is AtlasTexture):
            push_error("Relocated frame is not an AtlasTexture")
            quit(3)
            return
        if frame.region != Rect2(index * 32, 0, 32, 32):
            push_error("Relocated frame has incorrect region")
            quit(4)
            return
        if frame.atlas == null or frame.atlas.get_width() != 64 or frame.atlas.get_height() != 32:
            push_error("Relocated atlas cannot be loaded")
            quit(5)
            return
    var sprite := AnimatedSprite2D.new()
    sprite.sprite_frames = frames
    sprite.animation = "default"
    sprite.frame = 1
    if sprite.frame != 1:
        push_error("Relocated SpriteFrames unusable by AnimatedSprite2D")
        quit(6)
        return
    sprite.free()
    print("GODOT_RELOCATED_SPRITEFRAMES_OK frames=2 atlas=64x32")
    quit()
"""


def run(command: list[str], *, cwd: Path, marker: str | None = None) -> None:
    result = subprocess.run(command, cwd=cwd, text=True, capture_output=True,
                            timeout=120, check=False)
    output = result.stdout + "\n" + result.stderr
    if result.returncode != 0 or (marker is not None and marker not in output):
        raise RuntimeError("Godot import/runtime failed: " + output[-4000:])


def original_png() -> bytes:
    # Deterministically generate two original 32x32 drawings, with alpha.
    def chunk(name: bytes, data: bytes) -> bytes:
        return (struct.pack(">I", len(data)) + name + data
                + struct.pack(">I", zlib.crc32(name + data) & 0xFFFFFFFF))
    rows = []
    for y in range(32):
        row = bytearray(b"\x00")
        for x in range(64):
            if 4 <= x % 32 < 28 and 4 <= y < 28:
                row.extend((35, 185, 225, 255) if x < 32 else (230, 115, 45, 255))
            else:
                row.extend((0, 0, 0, 0))
        rows.append(bytes(row))
    return (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", struct.pack(">IIBBBBB", 64, 32, 8, 6, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(b"".join(rows)))
            + chunk(b"IEND", b""))


class OfflineClient:
    def __init__(self, archive: bytes) -> None:
        self.archive = archive
        self.correlation = None

    def can_dispatch_workflow(self, *_args) -> bool:
        return True

    def dispatch_workflow(self, _repo, _workflow, *, ref, inputs) -> None:
        self.correlation = inputs["correlation_id"]

    def wait_for_workflow_run(self, *_args, **_kwargs) -> dict:
        return {"id": 77, "conclusion": "success"}

    def workflow_run_artifacts(self, *_args) -> list[dict]:
        return [{"id": 88, "name": "asset-forge-batch-" + self.correlation,
                 "expired": False}]

    def download_workflow_artifact(self, *_args) -> bytes:
        return self.archive


def main() -> None:
    raw_bin = os.environ.get("GODOT_BIN", "").strip()
    if not raw_bin:
        raise RuntimeError("GODOT_BIN is required; real Godot 4 cannot be skipped")
    godot = str(Path(raw_bin).resolve(strict=True))
    with tempfile.TemporaryDirectory(prefix="production-os-godot-delivery-") as temp:
        root = Path(temp)
        original = root / "original"
        original.mkdir()
        (original / "project.godot").write_text(
            'config_version=5\n[application]\nconfig/name="Original Godot resource"\n'
            '[rendering]\nrenderer/rendering_method="gl_compatibility"\n',
            encoding="utf-8",
        )
        primary = original_png()
        (original / "player.png").write_bytes(primary)
        (original / "generate.gd").write_text(GENERATOR, encoding="utf-8")
        run([godot, "--headless", "--path", str(original), "--import"], cwd=root)
        run([godot, "--headless", "--path", str(original), "--script",
             "res://generate.gd"], cwd=root, marker="GODOT_ORIGINAL_RESOURCE_SAVED")
        tres = (original / "player.tres").read_bytes()
        if tres.count(b'path="res://player.png"') != 1:
            raise RuntimeError("Unexpected Godot 4 SpriteFrames texture reference")
        metadata = json.dumps({
            "assetId": "player", "image": "player.png",
            "frames": [
                {"index": 0, "x": 0, "y": 0, "width": 32, "height": 32},
                {"index": 1, "x": 32, "y": 0, "width": 32, "height": 32},
            ],
        }).encode("utf-8")
        parts = {"bundle/hero.png": primary, "bundle/hero.tres": tres,
                 "bundle/hero.atlas-metadata.json": metadata}
        request_id = "godot-relocated-engine-smoke"
        request = build_asset_forge_request(
            request_id=request_id, project="original-local-integration",
            asset_id="player", asset_type="sprite-sheet",
            instruction="Import original local atlas after relocation", target_format="png",
            engine="godot4", source_mode="custom", author="original-ci",
            license_id="project-owned",
        )
        target = "assets/characters/player.png"
        extras = [
            {"artifact": "bundle/hero.tres",
             "sha256": hashlib.sha256(tres).hexdigest(),
             "source_name": "player.tres", "role": "godot-spriteframes"},
            {"artifact": "bundle/hero.atlas-metadata.json",
             "sha256": hashlib.sha256(metadata).hexdigest(),
             "source_name": "atlas-metadata.json", "role": "godot-atlas-metadata"},
        ]
        row = {
            "id": "hero", "depends_on": [], "request_id": request_id,
            "target_path": target, "artifact": "bundle/hero.png",
            "sha256": hashlib.sha256(primary).hexdigest(),
            "additional_artifacts": extras,
        }
        report = {
            "schema": "asset-forge/production-report/v1", "success": True,
            "requestId": request_id, "assetId": "player", "assetType": "sprite-sheet",
            "artifact": "jobs/" + request_id + "/player.png",
            "engineHandoff": {
                "engine": "godot4", "type": "spriteframes", "ready": True,
                "spriteFrames": "jobs/" + request_id + "/player.tres",
                "atlasMetadata": "jobs/" + request_id + "/atlas-metadata.json",
                "atlasResourcePath": "res://player.png",
            },
        }
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("batch-result.json", json.dumps({
                "schema_version": "asset-forge/remote-batch-result/v1",
                "success": True, "count": 1, "items": [row],
            }))
            archive.writestr("jobs/" + request_id + "/production-report.json",
                             json.dumps(report))
            for name, content in parts.items():
                archive.writestr(name, content)

        consumer = root / "consumer"
        consumer.mkdir()
        (consumer / "project.godot").write_text(
            'config_version=5\n[application]\nconfig/name="Consumer integration"\n'
            '[rendering]\nrenderer/rendering_method="gl_compatibility"\n',
            encoding="utf-8",
        )
        delivered = execute_asset_forge_batch(
            [{"id": "hero", "request": request, "target_path": target}],
            mode="github", output_root=str(root / "receipts"),
            target_worktree=str(consumer), client=OfflineClient(zip_buffer.getvalue()),
        )
        if delivered["success"] is not True or delivered["count"] != 1:
            raise RuntimeError("Production-OS did not deliver the complete batch")
        if (consumer / target).read_bytes() != primary:
            raise RuntimeError("Relocated original atlas content changed")
        relocated_tres = consumer / "assets/characters/player.tres"
        if b'path="res://assets/characters/player.png"' not in relocated_tres.read_bytes():
            raise RuntimeError("SpriteFrames URI was not relocated")
        meta = json.loads((consumer / "assets/characters/player.atlas-metadata.json").read_text())
        if meta["image"] != "player.png" or len(meta["frames"]) != 2:
            raise RuntimeError("Atlas companion lost metadata")
        (consumer / "verify.gd").write_text(VALIDATOR, encoding="utf-8")
        run([godot, "--headless", "--path", str(consumer), "--import"], cwd=root)
        run([godot, "--headless", "--path", str(consumer), "--script",
             "res://verify.gd"], cwd=root, marker="GODOT_RELOCATED_SPRITEFRAMES_OK")
        print("PASS: actual Godot 4 import of Production-OS relocated SpriteFrames")
        print("PASS: two AtlasTexture regions, 64x32 source, AnimatedSprite2D assignment")
        print("PASS: remote receipt SHA256 and transactional consumer sidecars")

        # Real local Asset Forge CLI, no fake generation, and verified cache repair.
        source_root = os.environ.get("ASSET_FORGE_SOURCE_DIR", "").strip()
        if not source_root:
            raise RuntimeError("ASSET_FORGE_SOURCE_DIR required for local/cache smoke")
        forge_entry = Path(source_root).resolve(strict=True) / "asset_forge.py"
        if not forge_entry.is_file():
            raise RuntimeError("pinned Asset Forge CLI source unavailable")
        binary_dir = root / "local-cli-bin"
        binary_dir.mkdir()
        wrapper = binary_dir / "asset-forge"
        shell_command = (
            "#!/bin/sh\nexec " + shlex.quote(sys.executable) + " "
            + shlex.quote(str(forge_entry)) + ' "$@"\n'
        )
        wrapper.write_text(shell_command, encoding="utf-8")
        wrapper.chmod(0o700)
        local_request = build_asset_forge_request(
            request_id="godot-local-cache-smoke", project="original-local-integration",
            asset_id="player", asset_type="sprite-sheet",
            instruction="Export two original locally provided SpriteFrames",
            target_format="png", engine="godot4", source_mode="custom",
            author="original-ci", license_id="project-owned",
        )
        local_request["manifest"]["constraints"] = {
            "pixelArt": True, "interpolation": "nearest",
            "frameWidth": 32, "frameHeight": 32,
            "expectedFrames": 2, "requiresAlpha": True,
        }
        local_items = [{
            "id": "local-hero", "request": local_request, "target_path": target,
            "source_path": str(original / "player.png"),
        }]
        old_path = os.environ.get("PATH", "")
        os.environ["PATH"] = str(binary_dir) + os.pathsep + old_path
        try:
            first = execute_asset_forge_batch(
                local_items, mode="local", output_root=str(root / "local-production"),
                target_worktree=str(consumer),
            )
            if first["quality_summary"]["cache_hits"] != 0:
                raise RuntimeError("Initial local production unexpectedly used cache")
            receipt = json.loads(
                (consumer / (target + ".asset-forge.json")).read_text(encoding="utf-8")
            )
            if len(receipt.get("companions") or []) != 2:
                raise RuntimeError("Local sidecar hashes missing from version receipt")
            for record in receipt["companions"]:
                payload = (consumer / record["target_path"]).read_bytes()
                if hashlib.sha256(payload).hexdigest() != record["sha256"]:
                    raise RuntimeError("Local companion digest mismatch")
            run([godot, "--headless", "--path", str(consumer), "--import"], cwd=root)
            run([godot, "--headless", "--path", str(consumer), "--script",
                 "res://verify.gd"], cwd=root, marker="GODOT_RELOCATED_SPRITEFRAMES_OK")

            # A valid cache must work with the CLI removed.
            wrapper.unlink()
            cached = execute_asset_forge_batch(
                local_items, mode="local", output_root=str(root / "cached-production"),
                target_worktree=str(consumer),
            )
            if cached["quality_summary"]["cache_hits"] != 1:
                raise RuntimeError("Verified Godot cache did not avoid regeneration")
            # A cache from one generator/model must never masquerade as
            # a different generation. The CLI is absent here: a wrong cache
            # hit would succeed, while correct invalidation must refuse.
            receipt_path = consumer / (target + ".asset-forge.json")
            baseline_receipt = receipt_path.read_bytes()
            for variant in (
                {"backend": "another-backend"},
                {"model": "another-model"},
            ):
                try:
                    execute_asset_forge_batch(
                        local_items, mode="local",
                        output_root=str(root / ("variant-" + next(iter(variant)))),
                        target_worktree=str(consumer), **variant,
                    )
                except RuntimeError as exc:
                    if "CLI is required" not in str(exc):
                        raise
                else:
                    raise RuntimeError(
                        "Asset cache incorrectly reused across generator/model change"
                    )
                if receipt_path.read_bytes() != baseline_receipt:
                    raise RuntimeError("Refused generation altered version provenance")
            print("PASS: cache invalidates on backend/model changes without CLI")
            tres = consumer / "assets/characters/player.tres"
            clean = tres.read_bytes()
            tres.write_bytes(clean + b"\n; altered cached SpriteFrames\n")
            try:
                execute_asset_forge_batch(
                    local_items, mode="local", output_root=str(root / "altered-cache"),
                    target_worktree=str(consumer),
                )
            except RuntimeError as exc:
                if "CLI is required" not in str(exc):
                    raise
            else:
                raise RuntimeError("Modified Godot sidecar falsely passed cache")
            if tres.read_bytes() == clean:
                raise RuntimeError("Cache failure unexpectedly overwrote local worktree")
            (consumer / "assets/characters/player.atlas-metadata.json").unlink()
            try:
                execute_asset_forge_batch(
                    local_items, mode="local", output_root=str(root / "missing-cache"),
                    target_worktree=str(consumer),
                )
            except RuntimeError as exc:
                if "CLI is required" not in str(exc):
                    raise
            else:
                raise RuntimeError("Missing Godot sidecar falsely passed cache")

            # A true CLI production repairs both files, then Godot reimports.
            wrapper.write_text(shell_command, encoding="utf-8")
            wrapper.chmod(0o700)
            repaired = execute_asset_forge_batch(
                local_items, mode="local", output_root=str(root / "repaired-production"),
                target_worktree=str(consumer),
            )
            if repaired["quality_summary"]["cache_hits"] != 0:
                raise RuntimeError("Corrupted cache was not regenerated")
            run([godot, "--headless", "--path", str(consumer), "--import"], cwd=root)
            run([godot, "--headless", "--path", str(consumer), "--script",
                 "res://verify.gd"], cwd=root, marker="GODOT_RELOCATED_SPRITEFRAMES_OK")
            print("PASS: real Asset Forge local CLI -> Production-OS -> Godot")
            print("PASS: valid cache without CLI; altered/missing companions rejected")
            print("PASS: real local cache repair and Godot engine reimport")

            # Single-asset API must preserve the complete Godot handoff too.
            single_consumer = root / "single-consumer"
            single_consumer.mkdir()
            (single_consumer / "project.godot").write_bytes(
                (consumer / "project.godot").read_bytes()
            )
            (single_consumer / "verify.gd").write_text(VALIDATOR, encoding="utf-8")
            direct = execute_asset_forge(
                local_request, mode="local",
                output_dir=str(root / "single-production"),
                source_path=str(original / "player.png"),
                target_path=target, target_worktree=str(single_consumer),
            )
            if direct.delivery_mode != "worktree":
                raise RuntimeError("Single-asset Godot delivery mode missing")
            if (single_consumer / target).read_bytes() != primary:
                raise RuntimeError("Single-asset Godot PNG not delivered")
            single_receipt = json.loads(
                (single_consumer / (target + ".asset-forge.json")).read_text(
                    encoding="utf-8"
                )
            )
            if len(single_receipt.get("companions") or []) != 2:
                raise RuntimeError("Single-asset Godot companion receipt missing")
            for companion in single_receipt["companions"]:
                payload = (single_consumer / companion["target_path"]).read_bytes()
                if hashlib.sha256(payload).hexdigest() != companion["sha256"]:
                    raise RuntimeError("Single-asset Godot companion digest mismatch")
            run([godot, "--headless", "--path", str(single_consumer), "--import"],
                cwd=root)
            run([godot, "--headless", "--path", str(single_consumer), "--script",
                 "res://verify.gd"], cwd=root,
                marker="GODOT_RELOCATED_SPRITEFRAMES_OK")
            print("PASS: direct single-asset local CLI -> complete Godot 4 import")

            # Same original PNG source, but a newly supplied reference image,
            # must cause a new receipt version even if output bytes match.
            reference_png = root / "owned-reference.png"
            reference_png.write_bytes(original_png())
            receipt_path = single_consumer / (target + ".asset-forge.json")
            baseline = json.loads(receipt_path.read_text(encoding="utf-8"))
            if baseline.get("version") != 1:
                raise RuntimeError("Original direct asset receipt version is invalid")
            supplied = execute_asset_forge(
                local_request, mode="local",
                output_dir=str(root / "single-reference-first"),
                source_path=str(original / "player.png"),
                reference_paths=[str(reference_png)],
                target_path=target, target_worktree=str(single_consumer),
            )
            first_ref = json.loads(receipt_path.read_text(encoding="utf-8"))
            if (
                supplied.delivery_mode != "worktree"
                or first_ref.get("version") != 2
                or first_ref.get("sha256") != baseline.get("sha256")
                or first_ref.get("request_fingerprint") == baseline.get("request_fingerprint")
            ):
                raise RuntimeError("Provided image reference was missing from version identity")

            # Add a valid original PNG text chunk: its reference contents
            # change, whereas the actual source image and final pixels do not.
            ref_content = b"project-owned\x00alternate-reference"
            ref_chunk = (
                struct.pack(">I", len(ref_content))
                + b"tEXt" + ref_content
                + struct.pack(">I", zlib.crc32(b"tEXt" + ref_content) & 0xFFFFFFFF)
            )
            reference_png.write_bytes(original_png()[:-12] + ref_chunk + original_png()[-12:])
            execute_asset_forge(
                local_request, mode="local",
                output_dir=str(root / "single-reference-changed"),
                source_path=str(original / "player.png"),
                reference_paths=[str(reference_png)],
                target_path=target, target_worktree=str(single_consumer),
            )
            changed_ref = json.loads(receipt_path.read_text(encoding="utf-8"))
            if (
                changed_ref.get("version") != 3
                or changed_ref.get("sha256") != baseline.get("sha256")
                or changed_ref.get("request_fingerprint") == first_ref.get("request_fingerprint")
                or changed_ref.get("history", [{}])[-1].get("request_fingerprint")
                    != first_ref.get("request_fingerprint")
            ):
                raise RuntimeError("Modified local reference lost version provenance")

            # A missing explicit local reference is rejected before any
            # generation output directory or consumer write exists.
            invalid_output = root / "invalid-reference-production"
            try:
                execute_asset_forge(
                    local_request, mode="local", output_dir=str(invalid_output),
                    source_path=str(original / "player.png"),
                    reference_paths=[str(root / "nonexistent-reference.png")],
                    target_path=target, target_worktree=str(single_consumer),
                )
            except OSError:
                pass
            else:
                raise RuntimeError("Missing local reference incorrectly reached producer")
            if invalid_output.exists():
                raise RuntimeError("Invalid local reference created generator files")
            run([godot, "--headless", "--path", str(single_consumer), "--import"],
                cwd=root)
            run([godot, "--headless", "--path", str(single_consumer), "--script",
                 "res://verify.gd"], cwd=root,
                marker="GODOT_RELOCATED_SPRITEFRAMES_OK")
            print("PASS: original local visual reference hashes preserve version history")


        finally:
            os.environ["PATH"] = old_path



if __name__ == "__main__":
    main()
