# Worktree asset delivery: symlink alias safety

## Confirmed failure mode (2026-10-12)

An existing worktree destination such as `assets/characters/player.png`
may be a symbolic link to an unrelated asset in the **same** worktree.
Previously, `Path.resolve()` followed that link and the containment
check passed. A subsequent asset write could replace the unrelated file.
The same risk applies to version receipts, Godot companion files and
symlinked parent directories.

## Delivery contract

`_deliver_produced_assets` now checks every existing destination path
component for a symbolic link before staging writes. A detected link
raises `ValueError` without delivering the asset or receipt. The existing
native producer-to-Godot functional smoke exercises three aliases:
primary asset, `.asset-forge.json` receipt and parent directory. It
verifies that the unrelated content remains unchanged.

This is a **static preflight**, not a race-proof guarantee against another
process modifying the filesystem concurrently. Consumers should use a
trusted, exclusive worktree during delivery.

## Verification and scope

The integration entrypoint is
`integration/real_producer_bundle_smoke.py`; it requires `GODOT_BIN`
and `ASSET_FORGE_SOURCE_DIR` pointing to the pinned real Godot and
Asset Forge producer. GitHub CI runs the existing functional smoke with
a locally authored original image and no paid inference.

A successful CI does **not** establish commercial model/output rights,
a live hosted worker-to-PR chain, or a published game release.
