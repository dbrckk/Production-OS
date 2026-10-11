# Project state

Status: active

## Working
- 2026-10-11: PR #263 includes a dedicated **real Godot 4 relocated consumer import** CI smoke (`integration/godot4_relocated_import_smoke.py`): original local atlas, Godot-generated SpriteFrames, genuine Production-OS remote bundle parsing and worktree delivery, then headless Godot 4.4.1 editor import/runtime verification in the destination. It uses no generation backend, secrets, canary or new unit tests. Evidence requires the new job to pass on exact HEAD. This is not live worker E2E, model/output commercial licensing or semantic visual quality proof.
- 2026-10-11: **Draft PR #263 Godot 4 remote bundle consumer**: code `c92f1fd` verifies required `godot-spriteframes` and `godot-atlas-metadata` companions from Asset Forge's correlated ZIP (per-file SHA256, bounded sizes, source identity, metadata/image and SpriteFrames atlas reference), rewrites the `.tres` `res://` texture path and atlas metadata image to the final consumer path, and stages PNG + both companions atomically for worktree or a single GitHub commit; preflights normalized/case-insensitive destination collisions. Fix `9ed9c14` corrects single-backslash Windows path normalization. Existing CI *offline functional* parser/delivery smoke exercises a valid Godot receipt, missing sidecar and tampered SHA before any worktree modification. **Exact code-head CI 38133751566 COMPLETED SUCCESS 3/3** (Python 3.11/3.12 + test including functional Godot sidecar smoke). Asset Forge counterpart PR #13 source `12decdc`/`474fae9`, exact-head CI 38133508643 SUCCESS 4/4, documents a separately verified local Godot editor/runtime resource import plus real batch bundling. The linked pair remains DRAFT/nonmerged and requires qualified integration/deployment; no same-bundle Godot project runtime import, real worker-to-repository PR delivery, licensed commercial AI output or semantic validation is proved. Local Production-OS batch mode and cached sidecar restore are not claimed complete; proof targets the remote bundle consumer. No secrets, Render, GPU, old canaries, new unit tests, merges or deploys.
- 2026-10-11: **Draft PR #263 remote Asset Forge batch receipt correlation:** branch `fix/remote-batch-receipt-integrity-20261011` protects against duplicate remote item rows, missing items, mismatched `request_id`, missing per-job reports, and mismatched report schema/request/asset identity BEFORE worktree delivery or GitHub commit. First code/smoke commit `c2710a5` passed exact-head CI **38132465112 SUCCESS 3/3** (test, Python 3.11, Python 3.12; offline functional remote parser/delivery smoke SUCCESS). Further report-validation hardening and an existing remote fixture update are pending their own exact-head CI. No new unit tests, secrets, Render actions, historical canaries, GPU jobs, merges or deployments. The offline ZIP proof is not a real worker-to-consumer E2E or commercial image qualification. Known consumer gap: Asset Forge's Godot SpriteFrames `.tres` and atlas metadata are not propagated by the current Production-OS batch delivery path; do not claim a usable Godot game handoff from this receipt test.
- 2026-10-09: live canary #19 succeeded on Render with commit `0faf6bf`, structural verification and structured `delivery_status=review_blocked` (PR permission HTTP 403). The read-only Render warmup PR #279 in ai-dev-server is merged and verified. Current fix excludes ephemeral, stale and paused workers from automatic cooperative specialist-mode selection; the one-shot Actions worker must not impersonate a durable specialist fleet.
- 2026-10-09: live AI Dev Server canary 17 finished and published commit `b82a9e2` in `dbrckk/repo-standards`, but PR creation returned HTTP 403. Dashboard outcome now preserves only a validated GitHub compare URL and a clear review-blocked delivery warning when available. Matching worker result contract is in `dbrckk/ai-dev-server` PR #278; these branches still require passing CI before release.
- 2026-10-09 (branch `fix/actions-worker-push-fallback-readiness`): added a constrained Contents:write fallback for GitHub Actions 403/404 when waking `production-os-actions-worker.yml` on `main`. It writes a unique, non-secret request to the workflow's existing push trigger; success only confirms a GitHub commit, not a running worker.
- Dashboard launch readiness now excludes configured ephemeral worker IDs from immediately available slots to avoid treating stale Actions heartbeats as active capacity.
- Dashboard focused items now scroll into view once per navigation instead of every five-second refresh. Polling leaves the viewport alone when the user scrolls during a pending request.
- Central repository standards are configured.
- Compact AI context is generated through dbrckk/repo-standards.
- Controller cycle error reporting tolerates unavailable state and failed diagnostic storage without stopping daemon retries or masking the original bounded-run exception.
- PostgreSQL keyword DSNs use the PostgreSQL backend and locks. Schema v19 supplies the release transparency and trust incident ledgers; concurrent appends preserve their hash chains.
- Trust inspection and incident snapshots support existing legacy HMAC releases.

## Broken / blockers
- Asset Forge remote batch now falls back to a correlated request commit when cross-repository Actions write is unavailable; live worker and artifact verification remain pending.
- Server fix #250 is deployed and healthy; worker fix #240 is merged. Live run 37181156718 authenticated but found no compatible jobs. Queue diagnostics now distinguish empty queues, controls and capability/generation filters.
- Dashboard pairing fixes remain in existing PRs #247 and #248; this change does not duplicate them.

## Current priority
- Qualify the wake push fallback through canonical CI and a real remote canary; verify the token has Contents:write and confirm the worker completes a task. Do not claim remote execution success before observing it.
- Qualify a dedicated Asset Forge dispatch credential and a successful live visual job. The Actions worker now has a separate token path; repository permissions still need live verification.
- Merge the dashboard scroll fix and verify the deployed page. Continue the worker's remote persistence diagnosis and a successful real coding run.
- Deploy worker queue diagnostics, identify the actual live queue blocker and validate a real coding job.

## Validation
- Dashboard scroll and refresh regression checks: 124 selected tests passed, including JavaScript behavior in a Node VM.
- Standards workflow: configured.
- Tests/build: use this repository's existing validation commands.
- Controller, health, and CLI regression checks passed (65 tests), including 14 fault-injection cases.
- PostgreSQL release migration, concurrent ledger appends, real HTTP worker/release E2E, and legacy trust checks passed (33 targeted tests). The previous production-stack test silently used SQLite; it now asserts PostgreSQL explicitly.
- Final full suite with PostgreSQL 16: 1290 passed, none skipped. Compilation, distribution build, and isolated wheel CLI installation passed; missing PostgreSQL extras fail explicitly without a SQLite fallback.

## Last verified
- 2026-10-04

<!-- AUTO:START -->
## Automatic repository state

Generated: 2026-10-09T19:51:37Z

### Git
- Branch: `main`
- Head: `2752685edd0e`
- Commit date: 2026-10-09T21:51:27+02:00
- Commit: fix(workers): require persistent active specialists for cooperative launch (#261)
- Tracked files: 564

### Recently changed files
- `src/production_os/control_plane.py`
- `docs/production-readiness.md`
- `src/production_os/dashboard_ui.py`
- `src/production_os/managed_projects.py`
- `docs/worker-wake.md`
- `src/production_os/dashboard_control.py`
- `src/production_os/dashboard_service.py`
- `README.md`
- `tests/test_dashboard_control.py`
- `tests/test_dashboard_launch_readiness.py`
- `AGENTS.md`

### Project signals
- `pyproject.toml`
- `Dockerfile`

> Generated by dbrckk/repo-standards. Keep manual priorities and blockers outside the AUTO markers.
<!-- AUTO:END -->
