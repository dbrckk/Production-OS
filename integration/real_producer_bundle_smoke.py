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
from unittest.mock import patch

from production_os.asset_forge import _deliver_produced_assets, _extract_remote_batch_bundle, build_asset_forge_request, execute_asset_forge, execute_asset_forge_batch
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

        # An untrusted ZIP must be fully preflighted before any extraction:
        # aliases, Unicode NFC names, duplicate separators and parent/file
        # conflicts all risk overwriting earlier bundle entries.
        ambiguous_bundles = (
            (("jobs/A.png", b"first"), ("jobs/a.png", b"second")),
            (("jobs/café.png", b"first"), ("jobs/cafe\u0301.png", b"second")),
            (("jobs/a//b.png", b"first"),),
            (("jobs/report", b"first"), ("jobs/report/child.png", b"second")),
            (("jobs/CON.png", b"reserved-device"),),
            (("jobs/COM1.png", b"reserved-serial"),),
            (("jobs/atlas.png.", b"trailing-dot"),),
            (("jobs/atlas.png ", b"trailing-space"),),
            (("jobs/atlas:alternate.png", b"alternate-stream"),),
            (("jobs/preview?.png", b"wildcard"),),
        )
        for index, entries in enumerate(ambiguous_bundles):
            suspicious = io.BytesIO()
            with zipfile.ZipFile(suspicious, "w", zipfile.ZIP_DEFLATED) as archive:
                for name, content in entries:
                    archive.writestr(name, content)
            should_not_exist = root / f"unsafe-zip-preflight-{index}"
            try:
                _extract_remote_batch_bundle(suspicious.getvalue(), should_not_exist)
            except RuntimeError:
                pass
            else:
                raise RuntimeError("Ambiguous remote ZIP entry passed preflight")
            if should_not_exist.exists():
                raise RuntimeError("Rejected remote ZIP created an output directory")

        # A ZIP central directory can have valid paths and declared sizes
        # while a later stored entry fails its CRC. Without preflight, the
        # preceding file is written first, including an overwrite of a real
        # existing file. Test both a new directory and a populated one.
        corrupt_zip = io.BytesIO()
        crc_original = b"original-owned-crc-verification-payload"
        with zipfile.ZipFile(corrupt_zip, "w", zipfile.ZIP_STORED) as archive:
            archive.writestr("owned-marker.bin", b"must-not-overwrite")
            archive.writestr("corrupt-last.png", crc_original)
        corrupted_bytes = bytearray(corrupt_zip.getvalue())
        corrupt_at = corrupted_bytes.index(crc_original) + 4
        corrupted_bytes[corrupt_at] ^= 1
        for existing_destination in (False, True):
            corrupt_root = root / (
                "unsafe-zip-crc-existing" if existing_destination
                else "unsafe-zip-crc-new"
            )
            owned_marker = corrupt_root / "owned-marker.bin"
            if existing_destination:
                corrupt_root.mkdir()
                owned_marker.write_bytes(b"original-owned-file-unchanged")
            try:
                _extract_remote_batch_bundle(bytes(corrupted_bytes), corrupt_root)
            except RuntimeError as exc:
                if "corrupt ZIP payload" not in str(exc):
                    raise
            else:
                raise RuntimeError("CRC-corrupted remote ZIP passed preflight")
            if existing_destination:
                if (
                    owned_marker.read_bytes() != b"original-owned-file-unchanged"
                    or (corrupt_root / "corrupt-last.png").exists()
                ):
                    raise RuntimeError("Corrupt ZIP modified existing extraction contents")
            elif corrupt_root.exists():
                raise RuntimeError("Corrupt ZIP created partial output directory")

        # A pre-existing directory where the ZIP expects a file, or a
        # regular file where it expects a parent directory, must be refused
        # BEFORE any earlier good ZIP entry is written. Previously the first
        # entry was extracted, then an IsADirectoryError/FileExistsError
        # interrupted extraction and left a partial bundle.
        for conflict in ("file-target-is-directory", "parent-is-file"):
            conflict_root = root / ("unsafe-zip-existing-type-" + conflict)
            conflict_root.mkdir()
            marker = conflict_root / "owned-marker.bin"
            marker.write_bytes(b"preserve-original-owned-file")
            if conflict == "file-target-is-directory":
                (conflict_root / "blocked.png").mkdir()
                conflicting_entry = "blocked.png"
            else:
                (conflict_root / "blocked").write_bytes(b"preserve-parent-file")
                conflicting_entry = "blocked/child.png"
            archive_buffer = io.BytesIO()
            with zipfile.ZipFile(archive_buffer, "w", zipfile.ZIP_DEFLATED) as archive:
                archive.writestr("safe-first.png", b"must-not-extract")
                archive.writestr(conflicting_entry, b"untrusted-file")
            try:
                _extract_remote_batch_bundle(archive_buffer.getvalue(), conflict_root)
            except RuntimeError as exc:
                if "extraction has existing non-directory parent" not in str(exc) and (
                    "extraction targets existing non-file" not in str(exc)
                ):
                    raise
            else:
                raise RuntimeError("Pre-existing ZIP destination type conflict was accepted")
            if (
                (conflict_root / "safe-first.png").exists()
                or marker.read_bytes() != b"preserve-original-owned-file"
                or (
                    conflict == "parent-is-file"
                    and (conflict_root / "blocked").read_bytes() != b"preserve-parent-file"
                )
                or (
                    conflict == "file-target-is-directory"
                    and not (conflict_root / "blocked.png").is_dir()
                )
            ):
                raise RuntimeError("Rejected ZIP left partial files or damaged existing data")

        # Pre-existing case/Unicode aliases are just as ambiguous as symlinks
        # when the consumer runs on case-insensitive or NFC-normalizing hosts.
        # Refuse the *entire* archive without altering earlier files.
        for alias_kind, existing_name, zip_name in (
            ("file-case", "assets/PLAYER.png", "assets/player.png"),
            ("parent-case", "Assets", "assets/player.png"),
            ("file-unicode", "assets/café.png", "assets/cafe\u0301.png"),
            ("parent-unicode", "café", "cafe\u0301/child.png"),
        ):
            alias_root = root / ("unsafe-zip-existing-portable-" + alias_kind)
            alias_root.mkdir()
            existing_path = alias_root / existing_name
            if alias_kind.startswith("parent"):
                existing_path.mkdir(parents=True)
                protected = existing_path / "preserved.bin"
            else:
                existing_path.parent.mkdir(parents=True, exist_ok=True)
                protected = existing_path
            protected.write_bytes(b"preserve-original-owned-file")
            bundle = io.BytesIO()
            with zipfile.ZipFile(bundle, "w", zipfile.ZIP_DEFLATED) as archive:
                archive.writestr("safe-first.png", b"must-not-extract")
                archive.writestr(zip_name, b"untrusted-overwrite")
            try:
                _extract_remote_batch_bundle(bundle.getvalue(), alias_root)
            except RuntimeError as exc:
                if "extraction aliases existing case/Unicode path" not in str(exc):
                    raise
            else:
                raise RuntimeError(
                    "Existing ZIP extraction portable alias passed preflight: " + alias_kind
                )
            if (
                (alias_root / "safe-first.png").exists()
                or protected.read_bytes() != b"preserve-original-owned-file"
            ):
                raise RuntimeError(
                    "Rejected portable-alias ZIP mutated existing data or extracted first file"
                )

        # An existing *internal* symlink aliases another file in the same
        # extraction root. Earlier path-escape checks accepted such aliases,
        # overwriting files the producer ZIP did not explicitly name.
        # Reject the whole archive before extracting even its first good file.
        for alias_type in ("file", "parent"):
            alias_root = root / ("unsafe-zip-existing-symlink-" + alias_type)
            alias_root.mkdir()
            protected = alias_root / "protected"
            protected.mkdir()
            preserved = protected / "owned.png"
            preserved.write_bytes(b"preserve-original-owned-file")
            if alias_type == "file":
                (alias_root / "aliased.png").symlink_to(preserved)
                malicious_entry = "aliased.png"
            else:
                (alias_root / "aliased").symlink_to(
                    protected, target_is_directory=True
                )
                malicious_entry = "aliased/owned.png"
            archive_buffer = io.BytesIO()
            with zipfile.ZipFile(archive_buffer, "w", zipfile.ZIP_DEFLATED) as archive:
                archive.writestr("safe-first.png", b"must-not-extract")
                archive.writestr(malicious_entry, b"untrusted-overwrite")
            try:
                _extract_remote_batch_bundle(archive_buffer.getvalue(), alias_root)
            except RuntimeError as exc:
                if "targets existing symlink" not in str(exc):
                    raise
            else:
                raise RuntimeError(
                    "Existing ZIP extraction symlink escaped preflight: " + alias_type
                )
            if (
                (alias_root / "safe-first.png").exists()
                or preserved.read_bytes() != b"preserve-original-owned-file"
            ):
                raise RuntimeError(
                    "Rejected ZIP mutated existing files or partially extracted"
                )

        dispatch_item = {"id": item["id"], "request": request, "target_path": target}

        # A second job may choose the first sheet's SpriteFrames or atlas
        # companion as its own output. Such a batch must be rejected *before*
        # creating an output root or trying a paid/hosted producer.
        for collision_target in (
            "assets/characters/player.tres",
            "assets/characters/player.atlas-metadata.json",
            "assets/characters/PLAYER.PNG.asset-forge.json",
        ):
            second = json.loads(json.dumps(request))
            second["requestId"] = "companion-collision-check"
            second["manifest"]["id"] = "collision"
            conflicting_items = [
                dispatch_item,
                {
                    "id": "collision",
                    "request": second,
                    "target_path": collision_target,
                },
            ]
            for execution_mode in ("local", "github"):
                refused_root = root / (
                    "refused-companion-" + str(len(collision_target))
                    + "-" + execution_mode
                )
                try:
                    execute_asset_forge_batch(
                        conflicting_items, mode=execution_mode,
                        output_root=str(refused_root),
                        target_worktree=str(root / "collision-worktree"),
                    )
                except ValueError as exc:
                    if "planned media/receipt/companion path collision" not in str(exc):
                        raise
                else:
                    raise RuntimeError("Batch generated despite planned companion collision")
                if refused_root.exists():
                    raise RuntimeError("Rejected batch created generation output")

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

        # Batch callers previously bypassed the direct API's main-branch
        # guard, or dispatched generation with no consumer at all. Both must
        # fail before creating output or reaching a remote workflow.
        blocked_batch_root = root / "blocked-batch-destination"
        for ref in ("main", "refs/heads/main", "master", "refs/heads/master"):
            try:
                execute_asset_forge_batch(
                    [dispatch_item], mode="github",
                    output_root=str(blocked_batch_root),
                    target_repository="dbrckk/consumer", target_ref=ref,
                    client=OfflineClient(source_archive),
                )
            except ValueError as exc:
                if "non-default review branch" not in str(exc):
                    raise
            else:
                raise RuntimeError("Remote batch accepted implicit main-branch delivery")
        try:
            execute_asset_forge_batch(
                [dispatch_item], mode="github",
                output_root=str(blocked_batch_root),
                client=OfflineClient(source_archive),
            )
        except ValueError as exc:
            if "requires target_worktree or target_repository" not in str(exc):
                raise
        else:
            raise RuntimeError("Remote batch accepted generation without any destination")
        if blocked_batch_root.exists():
            raise RuntimeError("Invalid remote batch destination created an output directory")

        # Explicit local raster sources cannot be fulfilled by a remote
        # worker. Fail *before* any GitHub dispatch or output directory,
        # including auto mode when the local CLI is unavailable. The same
        # restriction also applies to fire-and-forget single requests, which
        # previously silently discarded source/reference inputs.
        for remote_mode in ("github", "auto"):
            refused = root / ("blocked-remote-local-source-" + remote_mode)
            with patch("production_os.asset_forge.shutil.which", return_value=None):
                try:
                    execute_asset_forge_batch(
                        [{"id": "player", "request": request,
                          "target_path": target, "source_path": str(image)}],
                        mode=remote_mode,
                        output_root=str(refused), target_worktree=str(consumer),
                        client=OfflineClient(source_archive),
                    )
                except ValueError as exc:
                    if "remote transactional batch does not accept local source_path" not in str(exc):
                        raise
                else:
                    raise RuntimeError("Remote batch accepted an inaccessible local source")
                for kwargs in (
                    {"source_path": str(image)},
                    {"reference_paths": [str(image)]},
                ):
                    try:
                        execute_asset_forge(
                            request, mode=remote_mode, output_dir=str(refused),
                            client=OfflineClient(source_archive), **kwargs,
                        )
                    except ValueError as exc:
                        if "cannot access local source/reference files" not in str(exc):
                            raise
                    else:
                        raise RuntimeError("Remote fire-and-forget lost local reference input")
            if refused.exists():
                raise RuntimeError("Rejected remote source created an output directory")

        # Existing end-to-end smoke also verifies destination preflight.
        # None of these cases may dispatch, generate, or create receipt files.
        bad_receipt = root / "blocked-path-receipt"
        for unsafe in ("../escape.png", "/absolute.png", "assets/./sprite.png",
                       "assets//sprite.png", "C:\\Windows\\sprite.png",
                       "assets/../sprite.png", "assets/CON.png",
                       "assets/COM¹.png", "assets/atlas:alt.png",
                       "assets/a?b.png", "assets/dot./sprite.png",
                       "assets/trail /sprite.png"):
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
        # These distinct strings still conflict as file and parent folder.
        for first, second in (
            ("assets/atlas.png", "assets/atlas.png/child.png"),
            ("assets/PLAYER.PNG", "assets/player.png/child.png"),
        ):
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
                raise RuntimeError("Batch file/child destination conflict bypassed preflight")
        # The consumer must reject producer-incompatible IDs before any
        # local job directory, remote dispatch, or artifact write.
        for unsafe_id in ("../escape", "a/b", "..", "bad id", "bad\\\\id",
                          "CON", "con.txt", "PRN", "AUX.log", "COM1",
                          "LPT9.data", "NUL"):
            unsafe_request = dict(request)
            unsafe_request["requestId"] = unsafe_id
            try:
                execute_asset_forge_batch(
                    [{"id": "unsafe", "request": unsafe_request, "target_path": target}],
                    mode="github", output_root=str(bad_receipt),
                    target_worktree=str(consumer), client=OfflineClient(source_archive),
                )
            except ValueError:
                pass
            else:
                raise RuntimeError("Unsafe batch requestId passed preflight")
            try:
                execute_asset_forge(
                    unsafe_request, mode="github", output_dir=str(bad_receipt),
                    target_path=target, target_worktree=str(consumer),
                    client=OfflineClient(source_archive),
                )
            except ValueError:
                pass
            else:
                raise RuntimeError("Unsafe single requestId passed preflight")
        for left, right in (("shared", "shared"), ("Shared", "shared")):
            first = dict(request)
            second = dict(request)
            first["requestId"] = left
            second["requestId"] = right
            try:
                execute_asset_forge_batch(
                    [{"id": "first", "request": first, "target_path": "assets/first.png"},
                     {"id": "second", "request": second, "target_path": "assets/second.png"}],
                    mode="github", output_root=str(bad_receipt),
                    target_worktree=str(consumer), client=OfflineClient(source_archive),
                )
            except ValueError:
                pass
            else:
                raise RuntimeError("Duplicate physical batch requestId passed preflight")
        if bad_receipt.exists():
            raise RuntimeError("Unsafe target/request IDs started a remote batch before preflight")

        # A direct local request formerly checked destination paths only
        # after generating an asset. Refuse unsafe or missing destinations
        # before creating even the local output directory or invoking CLI.
        bad_local_root = root / "blocked-local-single"
        for invalid_target in ("../escape.png", "assets/CON.png",
                               "assets/atlas:alternate.png", "assets/dot./x.png",
                               "assets/player?.png", ""):
            try:
                execute_asset_forge(
                    request, mode="local", output_dir=str(bad_local_root),
                    source_path=str(image), target_path=invalid_target,
                    target_worktree=str(consumer),
                )
            except ValueError:
                pass
            else:
                raise RuntimeError(f"Unsafe local delivery path reached generation: {invalid_target!r}")
        for delivery_fields in (
            {"target_worktree": str(consumer)},
            {"target_path": target},
        ):
            try:
                execute_asset_forge(
                    request, mode="local", output_dir=str(bad_local_root),
                    source_path=str(image), **delivery_fields,
                )
            except ValueError:
                pass
            else:
                raise RuntimeError("Incomplete local delivery destination reached generation")
        if bad_local_root.exists():
            raise RuntimeError("Refused local asset delivery created output before preflight")

        # Direct local generation must not follow a symlinked output root
        # (or an ancestor), including when no consumer delivery is requested.
        # The batch API already rejects its output_root symlinks.
        for alias_type in ("root", "parent"):
            protected_root = root / ("protected-single-output-" + alias_type)
            protected_root.mkdir()
            protected_marker = protected_root / "do-not-touch.bin"
            protected_marker.write_bytes(b"owned-single-output")
            link = root / ("single-output-link-" + alias_type)
            link.symlink_to(protected_root, target_is_directory=True)
            output_destination = link if alias_type == "root" else link / "generated"
            for delivery_fields in (
                {},
                {"target_path": target, "target_worktree": str(consumer)},
            ):
                try:
                    execute_asset_forge(
                        request, mode="local", output_dir=str(output_destination),
                        source_path=str(image), **delivery_fields,
                    )
                except ValueError as exc:
                    if "output directory must not traverse a symlink" not in str(exc):
                        raise
                else:
                    raise RuntimeError("Direct local generator followed output symlink")
            if (
                sorted(path.name for path in protected_root.iterdir()) != ["do-not-touch.bin"]
                or protected_marker.read_bytes() != b"owned-single-output"
            ):
                raise RuntimeError("Direct output symlink modified a protected directory")

        # Existing regular files also cannot serve as local generator output.
        blocked_direct_file = root / "blocked-single-output-file"
        blocked_direct_file.write_bytes(b"preserve-file")
        try:
            execute_asset_forge(
                request, mode="local", output_dir=str(blocked_direct_file),
                source_path=str(image),
            )
        except ValueError as exc:
            if "output directory must be a directory" not in str(exc):
                raise
        else:
            raise RuntimeError("Direct local generator accepted a file output root")
        if blocked_direct_file.read_bytes() != b"preserve-file":
            raise RuntimeError("Direct output type check modified an existing file")

        # A missing explicit source must never become an implicit no-source
        # fingerprint, reuse a cache entry, or start generator work.
        absent_source = root / "missing-owned-source.png"
        direct_absent = root / "blocked-missing-direct-source"
        for destination_fields in (
            {},
            {"target_path": target, "target_worktree": str(consumer)},
        ):
            try:
                execute_asset_forge(
                    request, mode="local", output_dir=str(direct_absent),
                    source_path=str(absent_source), **destination_fields,
                )
            except ValueError as exc:
                if "source_path must be an existing file" not in str(exc):
                    raise
            else:
                raise RuntimeError("Missing explicit local source reached generator")
        if direct_absent.exists():
            raise RuntimeError("Missing direct source created output directory")

        # Validate *all* source paths before creating output even if another
        # item in the batch has a valid, cacheable target.
        for batch_mode in ("local", "auto"):
            absent_batch = root / ("blocked-missing-batch-" + batch_mode)
            try:
                execute_asset_forge_batch(
                    [
                        {"id": "valid-owned", "request": request,
                         "target_path": target, "source_path": str(image)},
                        {"id": "missing-owned", "request": {
                            **request, "requestId": "missing-owned",
                            "manifest": {**request["manifest"], "id": "missing-owned"},
                         }, "target_path": "assets/characters/missing.png",
                         "source_path": str(absent_source)},
                    ],
                    mode=batch_mode, output_root=str(absent_batch),
                    target_worktree=str(consumer),
                )
            except ValueError as exc:
                if "source_path must be an existing file" not in str(exc):
                    raise
            else:
                raise RuntimeError("Missing source in batch reached generator")
            if absent_batch.exists():
                raise RuntimeError("Missing batch source created output directory")

        # A locally generated asset must not be pushed directly to GitHub's
        # default branch without an explicit review branch. This is refused
        # before any CLI or expensive generation.
        blocked_local_github = root / "blocked-local-main-delivery"
        for default_branch in ("main", "master", "refs/heads/main"):
            try:
                execute_asset_forge(
                    request, mode="local", output_dir=str(blocked_local_github),
                    source_path=str(image), target_path=target,
                    target_repository="dbrckk/consumer",
                    target_ref=default_branch,
                )
            except ValueError as exc:
                if "non-default review branch" not in str(exc):
                    raise
            else:
                raise RuntimeError("Local single asset allowed direct GitHub main delivery")
        if blocked_local_github.exists():
            raise RuntimeError("Refused local main-branch delivery started generation")

        # A destination alias must be blocked *before* local CLI generation
        # or remote dispatch, not just by the final transactional write.
        for alias in ("asset", "receipt", "parent"):
            blocked_root = root / ("preflight-alias-" + alias)
            characters = blocked_root / "assets" / "characters"
            characters.mkdir(parents=True)
            protected = root / ("preflight-protected-" + alias + ".bin")
            protected.write_bytes(b"unrelated-original-bytes")
            if alias == "parent":
                (blocked_root / "assets" / "characters").rmdir()
                (blocked_root / "assets" / "characters").symlink_to(
                    root, target_is_directory=True
                )
            else:
                name = "player.png" if alias == "asset" else "player.png.asset-forge.json"
                (characters / name).symlink_to(protected)
            for delivery in ("single", "batch"):
                output = root / ("no-generation-" + alias + "-" + delivery)
                try:
                    if delivery == "single":
                        execute_asset_forge(
                            request, mode="local", output_dir=str(output),
                            source_path=str(image), target_path=target,
                            target_worktree=str(blocked_root),
                        )
                    else:
                        execute_asset_forge_batch(
                            [{"id": "player", "request": request,
                              "target_path": target, "source_path": str(image)}],
                            mode="local", output_root=str(output),
                            target_worktree=str(blocked_root),
                        )
                except ValueError as exc:
                    if "symlink" not in str(exc):
                        raise
                else:
                    raise RuntimeError("Destination alias reached local generation")
                if output.exists():
                    raise RuntimeError("Rejected destination alias created output")
                if protected.read_bytes() != b"unrelated-original-bytes":
                    raise RuntimeError("Rejected destination alias mutated unrelated file")

        # An existing worktree ROOT may itself be a regular file.
        # Reject it before creating output or invoking the actual producer
        # (or dispatching a remote workflow), not only at final delivery.
        blocked_root_file = root / "invalid-consumer-root.bin"
        blocked_root_file.write_bytes(b"keep-unrelated-consumer-data")
        for blocked_mode in ("single-local", "batch-local", "batch-github"):
            output = root / ("no-generation-root-file-" + blocked_mode)
            try:
                if blocked_mode == "single-local":
                    execute_asset_forge(
                        request, mode="local", output_dir=str(output),
                        source_path=str(image), target_path=target,
                        target_worktree=str(blocked_root_file),
                    )
                else:
                    execute_asset_forge_batch(
                        [{"id": "player", "request": request,
                          "target_path": target,
                          **({"source_path": str(image)} if blocked_mode == "batch-local" else {})}],
                        mode="local" if blocked_mode == "batch-local" else "github",
                        output_root=str(output),
                        target_worktree=str(blocked_root_file),
                        client=OfflineClient(source_archive),
                    )
            except ValueError as exc:
                if "target_worktree must be a directory" not in str(exc):
                    raise
            else:
                raise RuntimeError("Non-directory consumer root reached generation")
            if output.exists():
                raise RuntimeError("Invalid consumer root caused output creation")
            if blocked_root_file.read_bytes() != b"keep-unrelated-consumer-data":
                raise RuntimeError("Invalid consumer root changed protected file")

        # An unsupported mode must not make a generation directory either.
        invalid_mode_root = root / "no-generation-invalid-mode"
        try:
            execute_asset_forge_batch(
                [{"id": "player", "request": request, "target_path": target}],
                mode="invalid", output_root=str(invalid_mode_root),
                target_worktree=str(consumer),
            )
        except ValueError as exc:
            if "mode must be auto, local, or github" not in str(exc):
                raise
        else:
            raise RuntimeError("Invalid asset batch mode reached output creation")
        if invalid_mode_root.exists():
            raise RuntimeError("Invalid asset batch mode created output directory")

        # A pre-existing job directory symlink may escape the batch output
        # root even when requestId is otherwise a safe single component.
        linked_root = root / "linked-local-jobs"
        linked_root.mkdir()
        outside_job = root / "outside-local-job"
        outside_job.mkdir()
        (linked_root / request["requestId"]).symlink_to(outside_job, target_is_directory=True)
        try:
            execute_asset_forge_batch(
                [{"id": "player", "request": request, "target_path": target,
                  "source_path": str(image)}],
                mode="local", output_root=str(linked_root),
                target_worktree=str(consumer),
            )
        except ValueError as exc:
            if "escapes output_root" not in str(exc):
                raise
        else:
            raise RuntimeError("Local batch followed an output symlink outside its root")
        if list(outside_job.iterdir()):
            raise RuntimeError("Refused local batch wrote into an external symlink target")

        # A symlink to a *different job inside the same output root* also
        # aliases paths and can overwrite another production report.
        alias_root = root / "aliased-local-jobs"
        alias_root.mkdir()
        other_job = alias_root / "existing-other-job"
        other_job.mkdir()
        (alias_root / request["requestId"]).symlink_to(other_job, target_is_directory=True)
        try:
            execute_asset_forge_batch(
                [{"id": "player", "request": request, "target_path": target,
                  "source_path": str(image)}],
                mode="local", output_root=str(alias_root),
                target_worktree=str(consumer),
            )
        except ValueError as exc:
            if "must not be a symlink" not in str(exc):
                raise
        else:
            raise RuntimeError("Local batch followed a job alias symlink inside its root")
        if list(other_job.iterdir()):
            raise RuntimeError("Refused local batch wrote into another job directory")

        # Existing file and directory names may have cross-platform aliases
        # on Windows or NFC-normalizing filesystems. Refuse before any local
        # generation or provider dispatch, including a case-aliased filename
        # and a Unicode-equivalent filename.
        for case_name, existing_name, target_name in (
            ("case", "PLAYER.png", target),
            ("unicode", "café.png", "assets/characters/cafe\u0301.png"),
        ):
            alias_consumer = root / ("cross-platform-alias-" + case_name)
            protected_alias = alias_consumer / "assets" / "characters" / existing_name
            protected_alias.parent.mkdir(parents=True)
            protected_alias.write_bytes(b"keep-original-aliased-asset")
            for alias_mode in ("single-local", "batch-local", "batch-github"):
                blocked_output = root / ("no-generation-cross-platform-" + case_name + "-" + alias_mode)
                try:
                    if alias_mode == "single-local":
                        execute_asset_forge(
                            request, mode="local", output_dir=str(blocked_output),
                            source_path=str(image), target_path=target_name,
                            target_worktree=str(alias_consumer),
                        )
                    else:
                        execute_asset_forge_batch(
                            [{"id": "player", "request": request,
                              "target_path": target_name,
                              **({"source_path": str(image)} if alias_mode == "batch-local" else {})}],
                            mode="local" if alias_mode == "batch-local" else "github",
                            output_root=str(blocked_output),
                            target_worktree=str(alias_consumer),
                            client=OfflineClient(source_archive),
                        )
                except ValueError as exc:
                    if "aliases an existing path by case or Unicode" not in str(exc):
                        raise
                else:
                    raise RuntimeError("Existing cross-platform worktree alias reached generation")
                if blocked_output.exists() or protected_alias.read_bytes() != b"keep-original-aliased-asset":
                    raise RuntimeError("Rejected cross-platform alias created output or mutated existing asset")

        # Pre-existing local job directories must be real directories. A
        # regular-file collision on a later job must refuse the entire batch
        # before the first item can generate anything.
        job_type_root = root / "blocked-local-job-file"
        job_type_root.mkdir()
        blocked_job = job_type_root / "blocked-job"
        blocked_job.write_bytes(b"keep-existing-job-file")
        first_job_id = "unused-first-job"
        second_request = {
            **request, "requestId": "blocked-job",
            "manifest": {**request["manifest"], "id": "blocked-job"},
        }
        first_request = {
            **request, "requestId": first_job_id,
            "manifest": {**request["manifest"], "id": first_job_id},
        }
        try:
            execute_asset_forge_batch(
                [
                    {"id": "fresh-job", "request": first_request,
                     "target_path": "assets/fresh-first-job.png",
                     "source_path": str(image)},
                    {"id": "blocked-job", "request": second_request,
                     "target_path": "assets/blocked-second-job.png",
                     "source_path": str(image)},
                ],
                mode="local", output_root=str(job_type_root),
                target_worktree=str(consumer),
            )
        except ValueError as exc:
            if "request output must be a directory" not in str(exc):
                raise
        else:
            raise RuntimeError("File-backed job output allowed earlier asset generation")
        if (job_type_root / first_job_id).exists() or blocked_job.read_bytes() != b"keep-existing-job-file":
            raise RuntimeError("Rejected job-directory collision modified the worktree")

        # The configured batch output root itself cannot be a symlink to an
        # unrelated working directory, even when each job id is safe.
        linked_output = root / "aliased-batch-output-root"
        guarded_output = root / "guarded-output-root"
        guarded_output.mkdir()
        (guarded_output / "do-not-overwrite").write_bytes(b"owned-output")
        linked_output.symlink_to(guarded_output, target_is_directory=True)
        for alias_mode in ("local", "github"):
            try:
                execute_asset_forge_batch(
                    [{"id": "player", "request": request, "target_path": target,
                      **({"source_path": str(image)} if alias_mode == "local" else {})}],
                    mode=alias_mode, output_root=str(linked_output),
                    target_worktree=str(consumer),
                    client=OfflineClient(source_archive),
                )
            except ValueError as exc:
                if "output_root must not be a symlink" not in str(exc):
                    raise
            else:
                raise RuntimeError("Batch output root symlink reached generation")
        if sorted(p.name for p in guarded_output.iterdir()) != ["do-not-overwrite"]:
            raise RuntimeError("Rejected batch output root alias modified protected output")

        # Verify real GitHub Contents ref encoding and branch-specific
        # version continuity using an offline recording client.
        class OfflineReviewBranch(GitHubClient):
            def __init__(self, receipt=None, *, move_before_commit=False):
                self.read_paths = []
                self.written_files = {}
                self.written_branch = None
                self.head_sha = "a" * 40
                self.move_before_commit = move_before_commit
                self.receipt = (
                    json.dumps({
                        "schema_version": "production-os/asset-version/v1",
                        "target_path": "assets/characters/player.png",
                        "version": 7,
                        "sha256": "a" * 64,
                        "history": [],
                        "companions": [],
                    })
                    if receipt is None else receipt
                )

            def _get(self, path):
                self.read_paths.append(path)
                return {"content": b64encode(self.receipt.encode()).decode()}

            def branch_head_sha(self, repository, branch):
                return self.head_sha

            def commit_files(self, repository, files, *, message, branch, expected_sha=None):
                if self.move_before_commit:
                    self.head_sha = "b" * 40
                if self.head_sha != expected_sha:
                    raise GitHubAPIError("GitHub target branch changed during asset delivery")
                self.written_branch = branch
                self.written_files = dict(files)
                return {"files": sorted(files)}

        # Preserve legacy GitHubAPIError("GitHub API NNN: ...") callers while
        # never considering a status number quoted only inside a response body.
        for message, expected_status in (
            ("GitHub API 404: not found", 404),
            ("GitHub API 422: Invalid request", 422),
            ("GitHub API 503: backend reported 404 and GitHub API 422:", 503),
            ("GitHub API unavailable: upstream 404", None),
        ):
            if GitHubAPIError(message).status_code != expected_status:
                raise RuntimeError("GitHub HTTP legacy status classification regressed")

        # GitHub response bodies are untrusted: their text must never spoof
        # a different HTTP status and erase a review-branch version receipt.
        class OfflineStatusClient(GitHubClient):
            def __init__(self, code: int, body: str):
                super().__init__(token="offline-smoke-placeholder")
                self.code = code
                self.body = body
                self.writes = 0

            def _get(self, _path):
                raise GitHubAPIError(
                    f"GitHub API {self.code}: {self.body}",
                    status_code=self.code,
                )

            def _request(self, _method, _path, _payload=None):
                self.writes += 1
                return {"content": {"sha": "offline-smoke"}}

        misleading = OfflineStatusClient(
            503, '{"message": "upstream 404 while fetching receipt"}'
        )
        for operation in (
            lambda: misleading.read_json_file(
                "dbrckk/consumer", "assets/test.asset-forge.json",
                ref="review/asset-handoff", strict=True,
            ),
            lambda: misleading.put_file(
                "dbrckk/consumer", "assets/test.png", b"payload",
                message="offline status gate", branch="review/asset-handoff",
            ),
            lambda: misleading.latest_release("dbrckk/consumer"),
            lambda: misleading._contents("dbrckk/consumer", "assets"),
        ):
            try:
                operation()
            except GitHubAPIError as exc:
                if exc.status_code != 503:
                    raise
            else:
                raise RuntimeError("GitHub HTTP 503 was silently mistaken for 404")
        if misleading.writes:
            raise RuntimeError("Ambiguous GitHub error triggered a contents write")
        if misleading.get_branch_protection("dbrckk/consumer", "main") is not None:
            raise RuntimeError("GitHub 503 spoofed an unprotected branch")
        if misleading.get_branch_required_checks("dbrckk/consumer", "main") is not None:
            raise RuntimeError("GitHub 503 spoofed absent required checks")

        missing = OfflineStatusClient(404, '{"message": "Not Found"}')
        if missing.read_json_file(
            "dbrckk/consumer", "assets/test.asset-forge.json",
            ref="review/asset-handoff", strict=True,
        ) is not None:
            raise RuntimeError("Real HTTP 404 receipt was not treated as absent")
        missing.put_file(
            "dbrckk/consumer", "assets/test.png", b"payload",
            message="offline missing contents", branch="review/asset-handoff",
        )
        if missing.writes != 1:
            raise RuntimeError("Real HTTP 404 did not permit first contents write")

        class OfflinePermissionError(OfflineStatusClient):
            def _request(self, _method, _path, _payload=None):
                raise GitHubAPIError(
                    f"GitHub API {self.code}: {self.body}",
                    status_code=self.code,
                )

        spoofed = OfflinePermissionError(
            503, '{"message": "GitHub API 422: not valid Base64"}'
        )
        for operation in (
            lambda: spoofed.can_dispatch_workflow(
                "dbrckk/consumer", "asset-forge-batch.yml"
            ),
            lambda: spoofed.can_write_contents("dbrckk/consumer"),
        ):
            try:
                operation()
            except GitHubAPIError as exc:
                if exc.status_code != 503:
                    raise
            else:
                raise RuntimeError("GitHub HTTP 503 spoofed positive permission probe")

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
        # Internal shared delivery must independently reject names that
        # would overwrite or collide across Windows/Unicode-normalizing hosts.
        for alias_kind, existing_name, target_name in (
            ("case", "PLAYER.png", target),
            ("unicode", "café.png", "assets/characters/cafe\u0301.png"),
        ):
            shared_consumer = root / ("shared-cross-platform-alias-" + alias_kind)
            protected_alias = shared_consumer / "assets" / "characters" / existing_name
            protected_alias.parent.mkdir(parents=True)
            protected_alias.write_bytes(b"original-portable-alias-data")
            try:
                _deliver_produced_assets(
                    [{**review_item, "target_path": target_name}],
                    target_repository=None,
                    target_worktree=str(shared_consumer),
                    target_ref="main", client=None,
                )
            except ValueError as exc:
                if "aliases an existing path by case or Unicode" not in str(exc):
                    raise
            else:
                raise RuntimeError("Internal delivery accepted cross-platform alias")
            if protected_alias.read_bytes() != b"original-portable-alias-data":
                raise RuntimeError("Internal alias delivery mutated existing content")
            if (shared_consumer / target_name).exists():
                raise RuntimeError("Internal alias delivery created conflicting media")

        # Refuse same-root aliases before writing any asset or receipt.
        for alias_case in ("asset", "sidecar", "parent"):
            worktree = root / f"consumer-symlink-{alias_case}"
            assets_root = worktree / "assets"
            assets_root.mkdir(parents=True)
            if alias_case == "parent":
                alternate = assets_root / "elsewhere"
                alternate.mkdir()
                (assets_root / "characters").symlink_to(
                    alternate, target_is_directory=True
                )
                protected = alternate / "unrelated.bin"
            else:
                characters = assets_root / "characters"
                characters.mkdir()
                protected = characters / "unrelated.bin"
                link_name = (
                    "player.png" if alias_case == "asset"
                    else "player.png.asset-forge.json"
                )
                (characters / link_name).symlink_to(protected)
            protected.write_bytes(b"original-unrelated-content")
            try:
                _deliver_produced_assets(
                    [review_item],
                    target_repository=None,
                    target_worktree=str(worktree),
                    target_ref="main",
                    client=None,
                )
            except ValueError as exc:
                if "must not traverse a symlink" not in str(exc):
                    raise
            else:
                raise RuntimeError(
                    f"Worktree delivery followed a same-root {alias_case} symlink"
                )
            if protected.read_bytes() != b"original-unrelated-content":
                raise RuntimeError("Refused worktree alias modified unrelated content")
            if alias_case == "asset" and (
                characters / "player.png.asset-forge.json"
            ).exists():
                raise RuntimeError("Refused asset alias wrote a receipt")
            if alias_case == "sidecar" and (characters / "player.png").exists():
                raise RuntimeError("Refused receipt alias wrote an asset")
            if alias_case == "parent" and (
                alternate / "player.png"
            ).exists():
                raise RuntimeError("Refused directory alias wrote an asset")

        # The shared transaction must check existing destination file types
        # before staging *any* asset, even when invoked without outer preflight.
        # These are not links: a directory at a media/receipt path or a file
        # at a parent path must never create a partial asset or receipt.
        for blocked_kind in ("media-directory", "receipt-directory", "file-parent"):
            worktree = root / ("consumer-type-" + blocked_kind)
            media = worktree / target
            receipt_path = worktree / (target + ".asset-forge.json")
            if blocked_kind == "media-directory":
                media.mkdir(parents=True)
                preserved = media
            elif blocked_kind == "receipt-directory":
                receipt_path.mkdir(parents=True)
                preserved = receipt_path
            else:
                preserved = worktree / "assets" / "characters"
                preserved.parent.mkdir(parents=True)
                preserved.write_bytes(b"owned-parent-content")
            try:
                _deliver_produced_assets(
                    [review_item], target_repository=None,
                    target_worktree=str(worktree), target_ref="main", client=None,
                )
            except ValueError as exc:
                if not (
                    "must be a file" in str(exc)
                    or "parent must be a directory" in str(exc)
                ):
                    raise
            else:
                raise RuntimeError("Shared worktree delivery accepted existing non-file destination")
            if blocked_kind == "file-parent":
                if preserved.read_bytes() != b"owned-parent-content":
                    raise RuntimeError("Refused file parent was modified")
            elif not preserved.is_dir():
                raise RuntimeError("Refused directory destination was modified")
            if blocked_kind == "media-directory" and receipt_path.exists():
                raise RuntimeError("Directory media path caused receipt write")
            if blocked_kind == "receipt-directory" and media.exists():
                raise RuntimeError("Directory receipt path caused partial media write")

        # Direct shared-helper calls must also refuse GitHub default branches.
        for forbidden_ref in ("main", "master", "refs/heads/main"):
            forbidden = OfflineReviewBranch()
            try:
                _deliver_produced_assets(
                    [review_item], target_repository="dbrckk/consumer",
                    target_worktree=None, target_ref=forbidden_ref,
                    client=forbidden,
                )
            except ValueError as exc:
                if "non-default review branch" not in str(exc):
                    raise
            else:
                raise RuntimeError("Shared asset delivery bypassed GitHub review")
            if forbidden.read_paths or forbidden.written_files:
                raise RuntimeError("Refused default-branch delivery accessed GitHub")

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

        # Identical bytes do not imply the same asset provenance. A new
        # semantic request must advance the version and preserve fingerprint
        # history, while an exact retry stays on its existing version.
        source_version = json.loads(
            github.written_files[target + ".asset-forge.json"].decode("utf-8")
        )
        if source_version["version"] != 8:
            raise RuntimeError("Baseline branch version is not eight")
        for new_fingerprint, expected_version in (
            ("original-review-branch-smoke", 8),
            ("original-review-branch-smoke-changed", 9),
        ):
            original = OfflineReviewBranch(receipt=json.dumps(source_version))
            rerun = {**review_item, "request_fingerprint": new_fingerprint}
            _deliver_produced_assets(
                [rerun], target_repository="dbrckk/consumer",
                target_worktree=None, target_ref=review_ref, client=original,
            )
            new_version = json.loads(
                original.written_files[target + ".asset-forge.json"].decode("utf-8")
            )
            if new_version["version"] != expected_version:
                raise RuntimeError(
                    "Identical asset payload failed request-fingerprint versioning"
                )
            if new_fingerprint != source_version["request_fingerprint"]:
                old_record = new_version["history"][-1]
                if (old_record.get("version") != 8 or
                        old_record.get("request_fingerprint") !=
                        source_version["request_fingerprint"]):
                    raise RuntimeError(
                        "Changed semantic request lost prior provenance history"
                    )

        # Exercise a concurrent branch change after reading the receipt.
        # No stale version can be committed on top of another writer's HEAD.
        moved = OfflineReviewBranch(move_before_commit=True)
        try:
            _deliver_produced_assets(
                [review_item], target_repository="dbrckk/consumer",
                target_worktree=None, target_ref=review_ref, client=moved,
            )
        except GitHubAPIError as exc:
            if "branch changed" not in str(exc):
                raise
        else:
            raise RuntimeError("Concurrent GitHub branch update was ignored")
        if moved.written_files:
            raise RuntimeError("Concurrent GitHub update received stale asset files")

        # A corrupt existing receipt cannot be silently replaced with version 1.
        # The actual GitHubClient must reject malformed JSON before commit_files.
        for malformed in ('{"version":', '[]', '{"version": 0}'):
            blocked = OfflineReviewBranch(receipt=malformed)
            try:
                _deliver_produced_assets(
                    [review_item], target_repository="dbrckk/consumer",
                    target_worktree=None, target_ref=review_ref, client=blocked,
                )
            except (GitHubAPIError, RuntimeError):
                pass
            else:
                raise RuntimeError("GitHub delivery silently reset a corrupt version receipt")
            if blocked.written_files:
                raise RuntimeError("Corrupt GitHub receipt triggered a commit")

        # A list-typed history/companion field with corrupt *entries* must
        # never propagate into a new GitHub version receipt.
        good_history = {
            "version": 7, "sha256": "a" * 64,
            "request_fingerprint": None,
        }
        invalid_nested_receipts = (
            {**source_version, "request_fingerprint": {"unsafe": "nested-object"}},
            {**source_version, "request_fingerprint": ["not-a-fingerprint"]},
            {**source_version, "history": ["not-an-entry"]},
            {**source_version, "history": [
                {**good_history, "version": True}]},
            {**source_version, "history": [
                {**good_history, "version": source_version["version"]}]},
            {**source_version, "history": [
                {**good_history, "sha256": "invalid-sha"}]},
            {**source_version, "history": [good_history, good_history]},
            {**source_version, "companions": [
                {"target_path": "../outside.tres", "sha256": "b" * 64}]},
            {**source_version, "companions": [
                {"target_path": target, "sha256": "b" * 64}]},
            {**source_version, "companions": [
                {"target_path": "assets/characters/frame.tres", "sha256": "b" * 64},
                {"target_path": "assets/characters/FRAME.tres", "sha256": "c" * 64}]},
            {**source_version, "companions": [
                {"target_path": "assets/characters/frame.tres", "sha256": "bad"}]},
            {**source_version, "companions": [
                {"target_path": "assets/characters/frame.tres", "sha256": "b" * 64},
                {"target_path": "assets/characters/frame.tres/nested", "sha256": "c" * 64}]},
        )
        for invalid in invalid_nested_receipts:
            blocked = OfflineReviewBranch(receipt=json.dumps(invalid))
            try:
                _deliver_produced_assets(
                    [review_item], target_repository="dbrckk/consumer",
                    target_worktree=None, target_ref=review_ref, client=blocked,
                )
            except RuntimeError as exc:
                if "existing asset version receipt" not in str(exc):
                    raise
            else:
                raise RuntimeError("Nested malformed GitHub receipt was accepted")
            if blocked.written_files:
                raise RuntimeError("Nested malformed receipt triggered a GitHub commit")

        # The real worktree delivery path must also refuse malformed history
        # before touching the existing PNG, sidecars or the corrupt metadata.
        local_sidecar = consumer / (target + ".asset-forge.json")
        original_sidecar = local_sidecar.read_bytes()
        original_artifact = (consumer / target).read_bytes()
        try:
            # A valid real Godot cache can carry malformed producer-provided
            # visual metadata. Historically the batch wrote the receipt and
            # only then raised when parsing its quality summary. Prove that
            # an error never mutates the consumer after a reported failure.
            from production_os.asset_forge import _request_fingerprint
            invalid_metric = json.loads(original_sidecar.decode("utf-8"))
            invalid_metric["request_fingerprint"] = _request_fingerprint(
                request, [], source_path=str(image), backend="auto", model=None,
            )
            invalid_metric["visual_similarity"] = {
                "attempts": [{"score": "not-a-number"}],
            }
            local_sidecar.write_text(json.dumps(invalid_metric), encoding="utf-8")
            protected_metric_receipt = local_sidecar.read_bytes()
            try:
                execute_asset_forge_batch(
                    [item], mode="local",
                    output_root=str(root / "invalid-producer-metric"),
                    target_worktree=str(consumer),
                )
            except ValueError as exc:
                if "could not convert string to float" not in str(exc):
                    raise
            else:
                raise RuntimeError("Invalid producer metric bypassed quality validation")
            if (
                local_sidecar.read_bytes() != protected_metric_receipt
                or (consumer / target).read_bytes() != original_artifact
            ):
                raise RuntimeError("Failed quality summary mutated the delivered asset")

            for invalid_content in (
                '{"version":', '{"version": 0}', '[]',
                *(json.dumps(value) for value in invalid_nested_receipts),
            ):
                local_sidecar.write_text(invalid_content, encoding="utf-8")
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
                if local_sidecar.read_text(encoding="utf-8") != invalid_content:
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
        print("PASS: ZIP aliases, Windows reserved names and file/directory conflicts blocked before extraction")
        print("PASS: Existing ZIP target/parent case and Unicode aliases fail before extraction")
        print("PASS: Corrupt ZIP CRC rejected before creating or overwriting any extraction files")
        print("PASS: Existing file/parent symlink ZIP aliases refused before any write")
        print("PASS: Existing ZIP file/directory destination conflicts refuse partial extraction")
        print("PASS: Destination paths and nested file conflicts blocked before remote dispatch")
        print("PASS: Planned media/receipt/Godot companion collisions refused before generation")
        print("PASS: Unsafe/colliding request IDs rejected before batch or single dispatch")
        print("PASS: Local batch refuses escaping or aliasing job symlinks before generator")
        print("PASS: Local batch rejects file-backed job directories and symlink output roots before generation")
        print("PASS: Existing case/Unicode-equivalent worktree names rejected before generation or writes")
        print("PASS: Worktree asset, receipt and parent symlink aliases fail before writes")
        print("PASS: Local single and batch aliases rejected before generator/output")
        print("PASS: Invalid consumer root and batch execution mode refused before generation/dispatch")
        print("PASS: Windows-reserved batch identifiers rejected before any dispatch")
        print("PASS: Invalid/incomplete local single-asset destinations refused before CLI generation")
        print("PASS: Direct local output root, parent symlink and file aliases refused before generation")
        print("PASS: Missing direct/batch explicit source files refused before generation or cache reuse")
        print("PASS: Local single-asset GitHub main/master delivery refused before generation")
        print("PASS: Direct GitHub-mode single-asset transaction + Godot import")
        print("PASS: Implicit main-branch remote delivery refused before dispatch")
        print("PASS: Remote batch rejects main/master and missing destination before dispatch")
        print("PASS: Remote batch and dispatch-only reject inaccessible local inputs before output")
        print("PASS: Review-branch version lookup/transaction remains on target ref")
        print("PASS: Same binary/different request fingerprint increments provenance version")
        print("PASS: GitHub HTTP status cannot be spoofed by response-body digits")
        print("PASS: Concurrent destination HEAD movement refuses stale asset commit")
        print("PASS: Malformed and structurally invalid GitHub/worktree receipts rejected")
        print("PASS: Nested receipt history and companion corruption refused before GitHub/worktree writes")
        print("PASS: Invalid current receipt fingerprint and non-file worktree destinations refused before writes")
        print("PASS: Invalid cached visual score fails before transactional asset delivery")
        print("PASS: Tampered real producer SpriteFrames rejected before delivery")


if __name__ == "__main__":
    main()
