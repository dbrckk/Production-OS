#!/usr/bin/env python3
"""Actual pinned Asset Forge producer bundle -> Production-OS consumer -> Godot 4.

This is a functional integration smoke, not a new unit test. It uses only
locally authored original PNG pixels and the real Asset Forge CLI; no paid
inference, hosted dispatch, credentials, old canaries, or network is invoked.
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import shlex
import sys
import tempfile
import zipfile
from pathlib import Path

from production_os.asset_forge import build_asset_forge_request, execute_asset_forge_batch
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
        item = {"id": "real-hero", "request": request,
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

        # Tamper with the REAL producer .tres byte payload but preserve its
        # real declared checksum; fail closed before any consumer file write.
        tres_path = next(
            entry["artifact"] for entry in row["additional_artifacts"]
            if entry.get("role") == "godot-spriteframes"
        )
        tampered_zip = io.BytesIO()
        with zipfile.ZipFile(source_archive, "r") as genuine:
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
        print("PASS: Tampered real producer SpriteFrames rejected before delivery")


if __name__ == "__main__":
    main()
