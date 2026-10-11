# Production readiness

## Godot 4 remote batch sidecars (offline-verified)

For remote Asset Forge `sprite-sheet` production targeting Godot 4, the
primary PNG/WebP is not by itself a usable Godot animation resource. The
remote batch result must include two digest-verified companions identified
by explicit roles: `godot-spriteframes` (`.tres`) and
`godot-atlas-metadata` (JSON). Missing, duplicated, oversized, escaping,
incorrectly attributed or SHA256-mismatched companions abort before
any destination write. The consumer also checks the `.tres` reference and
metadata source image against the verified production report before changing
their references.

Before delivery, Production-OS rewrites only the verified SpriteFrames
Texture2D external resource path to the final consumer location, for example
`res://assets/characters/player.png`; it updates the atlas metadata image
basename. The texture, relocated `player.tres` and
`player.atlas-metadata.json` then participate in the same transactional
worktree staging or GitHub multi-file commit as the existing receipt and
version metadata. A normalized case-insensitive path ledger rejects
collisions before writing anything.

The existing CI functional smoke uses a local synthetic ZIP and in-memory
GitHub Actions client to exercise the actual remote receipt parser, including
a valid relocation, a missing sidecar and a modified SHA. There is **no**
remote dispatch or expensive inference in that smoke. Production-OS code
[commit c92f1fd](https://github.com/dbrckk/Production-OS/commit/c92f1fd88c3a65652054d028099569757a0e0425),
[separator fix 9ed9c14](https://github.com/dbrckk/Production-OS/commit/9ed9c149a9308a0f160f339a0683d0103fff7886),
[exact-code CI 38133751566](https://github.com/dbrckk/Production-OS/actions/runs/38133751566)
COMPLETED SUCCESS 3/3 including functional smoke. Provider Asset Forge's
[CI 38133508643](https://github.com/dbrckk/asset-forge/actions/runs/38133508643)
COMPLETED SUCCESS 4/4 independently verified real CLI bundling of original
local PNG plus companions and real Godot 4 editor/runtime import of the
original exported resource.

**Limitations:** Both changes are in separate unmerged **draft** PRs
(Production-OS #263 and Asset Forge #13). The paired tests do not yet prove
a **published consuming game**, commercial rights for AI-produced art,
semantic visual fidelity or live Production-OS → worker → GitHub PR → game release.
The separate relocated-import and local/cache/direct-single-asset engine
smokes have passed on their explicitly cited code SHA values. No deployment,
GPU inference or privileged Render action has been executed.

## Relocated Godot 4 engine import gate (CI)

The optional, original-art, no-inference integration smoke at `integration/godot4_relocated_import_smoke.py`
uses a SHA512-verified official Godot 4.4.1 editor. It creates an original
local RGBA atlas, saves a genuine `SpriteFrames` resource via Godot's
`ResourceSaver`, sends the image and hashed sidecars through the **actual**
Production-OS offline remote-result parser/worktree transaction, then imports
and loads the relocated `res://assets/characters/player.tres` in a second
real Godot 4 project. It verifies both AtlasTexture regions and assignment to
AnimatedSprite2D. The separate canonical CI job succeeded on the **exact code HEAD**
`bcee95a31c2fe286e6cf08a7348a7f15389d3f5d` in
[run 38154300786](https://github.com/dbrckk/Production-OS/actions/runs/38154300786). There is no new unit test,
paid generation, historical canary, remote dispatch or secret inspection.

This checks remote receipt parsing and consumer engine load together, but the
archive is created locally; it does **not** establish a live Asset Forge
workflow, commercial artwork/model rights, semantic visual acceptance,
actual Production-OS worker → PR publication, or a deployed game.

## Local Godot batch sidecars and verified cache

The local Asset Forge batch now reads the real CLI report and requires
Godot SpriteFrames and atlas metadata to be declared in additionalArtifacts,
located within the job output directory, matched to their explicit engine
handoff roles and validated through the same resource/identity checks as
remote batch sidecars. The original atlas and both companions participate in
a single transactional worktree delivery or GitHub multi-file commit.

Version receipts now record each companion's destination and SHA-256. Cache
reuse checks both companion digests, Godot res:// atlas reference, JSON image
name and nonempty frame list. Missing, altered or untracked legacy sidecars
make a cache MISS. If the local CLI is unavailable, the job fails instead of
returning a broken cache hit. Changes to companions affect versioning even
when the primary image digest is unchanged.

The existing Godot 4.4.1 integration job now checks out Asset Forge PR #13 at
pinned SHA 35e0b1289b760c3a84765d0d2d28b86c6f110476. Using only an
original locally constructed PNG, it runs the genuine Asset Forge CLI through
Production-OS, imports the locally delivered animation into Godot, verifies
reuse without a CLI, rejects altered/missing sidecars and regenerates through
the real local CLI. Exact code-head CI 38137130685 completed SUCCESS (4/4 jobs) on
commit ba534b05ea53b4e2363809e1325c31fe66e7dbcf, including the
real Godot 4 local CLI/cache/tamper/repair import smoke and the canonical
Python 3.11/3.12, production E2E, packaging and Docker verification.
This is an offline/locally provided image qualification only. No new unit
tests, inference, historic canaries or secrets are involved.

Still not proved: live worker-to-PR/game release, commercial model/output
rights, semantic image fidelity or published consumer game integration.

## Direct local single-asset Godot delivery (exact-head CI qualified)

The direct `execute_asset_forge(..., mode="local", target_path=...)`
Godot 4 sprite-sheet path now uses the **same transactional delivery helper**
as batch mode. The real CLI production report must contain validated
SpriteFrames and atlas metadata companions. PNG, relocated `.tres`,
`.atlas-metadata.json`, and the version receipt (including companion
SHA-256 hashes) are staged together. A failed companion validation occurs
before any consumer write. Non-Godot direct delivery keeps its prior
single-file behavior.

The existing `integration/godot4_relocated_import_smoke.py` functional
smoke now also exercises this direct path with the pinned Asset Forge CLI,
an original local PNG and a real Godot 4.4.1 editor/runtime import into a
separate consumer project. Exact-HEAD [CI 38154300786](https://github.com/dbrckk/Production-OS/actions/runs/38154300786)
COMPLETED SUCCESS 4/4 on `bcee95a31c2fe286e6cf08a7348a7f15389d3f5d`.
The Godot 4.4.1 job completed successfully with the real pinned Asset Forge CLI,
original local PNG, direct single-asset sidecars and headless editor/runtime import.
The other jobs passed Python 3.11/3.12, existing integration checks, packaging and Docker. This does not prove worker-to-PR delivery, commercial Qwen model
rights, semantic image quality or a deployed game.

## Real producer-to-consumer Godot bundle integration (CI)

The existing Godot 4 integration job now additionally executes
integration/real_producer_bundle_smoke.py. It runs the genuine pinned Asset
Forge remote_batch.run coordinator on a locally authored original 64x32 PNG,
with an explicit provided source (no AI generation). The real result tree,
including batch-result.json, jobs/request/production-report.json, and image
plus two role-labelled and SHA256-verified Godot sidecars, is zipped exactly
as a GitHub Actions artifact would be. Production-OS consumes that unmodified
ZIP with its actual remote-receipt parser and transactional worktree delivery.
A second consumer Godot 4.4.1 project imports and loads the relocated animation
and validates both AtlasTexture frames in AnimatedSprite2D.

The integration deliberately changes a .tres payload inside a genuine
producer ZIP without changing its declared SHA256 and confirms that the
consumer rejects the archive before writing any asset. The new job must
pass on the exact PR HEAD before this proof is considered successful.

This is real cross-repository artifact compatibility in ONE isolated CI
runner, not an actual hosted cross-repository Actions dispatch or a worker
job. It does not prove secrets or permissions for remote triggering, worker
claim, PR publication, consuming-game build/deployment, commercial model
rights, or semantic fidelity of AI images. No new unit tests, old canaries,
GPU, paid inference, merge or deployment are used.

## Asset Forge remote batch receipt integrity

The batch download/parser validates identity and content correlation before
committing assets into a worktree or target GitHub repository. In addition to
artifact SHA256 and target/dependency checks, it refuses duplicate or
unexpected item IDs, missing expected items, mismatched request IDs and
missing per-item production reports. The report must be a successful
`asset-forge/production-report/v1` object matching the original request ID,
asset ID and asset type. A matching row count alone is not sufficient.

The existing CI includes an offline functional smoke using the actual remote
batch parser and transactional worktree delivery, a local ZIP containing
simulated bytes, and an in-memory GitHub Actions client. Cases include a
valid two-item delivery, duplicate/unknown items, mismatched request ID,
missing production report and mismatched report identity. This executes no
remote action, GPU inference or network call.

[Production-OS PR #263](https://github.com/dbrckk/Production-OS/pull/263)
is **draft and unmerged**. Initial code-head
[CI 38132465112](https://github.com/dbrckk/Production-OS/actions/runs/38132465112)
passed 3/3; later report-validation changes require separate exact-head
qualification. This smoke does **not** establish deployed worker E2E,
commercial model/output rights, independent semantic fidelity, or complete
Godot asset sidecar delivery. This was the historical gap at the receipt-integrity-only stage. The
current draft PR #263 now includes verified sidecar delivery and Godot
import of both remote-style receipt and local CLI output; the full hosted
worker-to-consumer E2E remains unverified.

Production-OS 1.0 is qualified as a stable release when the canonical CI workflow is green on the exact release commit.

## GitHub review delivery versus coding completion

A worker may successfully verify and publish a coding checkpoint while its GitHub credential lacks target-repository **Pull requests: write** permission. That implementation must not be presented as a merged or deployed release. New AI Dev Server result evidence reports `delivery_status=review_blocked`, `release_status=verified_branch_review_blocked` and a restricted, non-secret `pull_request.compare_url` when GitHub returns PR HTTP 403. The Production-OS dashboard labels the missing PR and offers a manually actionable GitHub comparison link. Always verify the target branch, pull-request review and CI separately before promoting a release.


The release commit must pass all of the following on GitHub Actions:

1. install the development and PostgreSQL dependency sets;
2. compile every module under `src`;
3. pass the complete non-E2E pytest suite on Python 3.11 and Python 3.12;
4. pass the production-stack E2E test against PostgreSQL 16 on Python 3.12;
5. build both Python wheel and source distribution artifacts;
6. install the wheel into an isolated virtual environment and run the installed CLI;
7. build the production Docker image and run the image CLI smoke test;
8. run the editable-install CLI smoke test.

The E2E test uses an isolated PostgreSQL database and exercises a real HTTP control plane, authenticated operator and worker identities, remote claim/ack/complete, a dependency-ordered workflow, artifact registration, validation attestation, release promotion, release verification, transparency verification and final control-plane statistics.

## Supported runtime paths

- Python 3.11 and 3.12, both covered by the compatibility gate
- Python 3.12 in the production container and production-stack E2E gate
- SQLite for local/single-node durable state
- PostgreSQL for distributed/production state
- Docker / Docker Compose deployment

## Security and trust expectations

Production-OS treats repository content and GitHub metadata as untrusted input and keeps privileged/destructive behavior behind explicit policy and auditable authorization.

Supply-chain controls include signed validation attestations, provenance verification, trusted-builder enforcement, local transparency, Rekor v1 receipts, signed tree checkpoints, RFC6962 inclusion and consistency verification, rollback protection and optional independent witness quorum.

Rekor witness independence is an operational requirement: deployments that rely on quorum for split-view resistance should place witnesses in genuinely independent administrative and network domains.

## Stable-release policy

The supported stable line is 1.x. Changes that break documented CLI, persistence, receipt or API contracts require a new major version. Security and correctness fixes may ship in compatible 1.x releases after passing the same canonical qualification gate.

A release must not be declared stable from a branch-only result. The exact merged release commit on `main` must be green before a tag or GitHub Release is created.


## Generated-context head qualification

Repository-standards may advance `main` after an application merge by committing regenerated `.ai/**` context. Those generated-only commits are part of the branch history, so Production-OS treats the resulting commit as the new release candidate rather than relying on the CI result of its parent.

The repository-standards workflow therefore compares the post-generation `main` head with the triggering commit. If generated context advanced the branch, it explicitly dispatches the canonical `ci.yml` workflow against the new head. A generated-only commit must not be considered release-qualified until that exact-head CI succeeds.

Generated unified AI-context commits are marked `[skip render]`. They stage only `.ai/**`, so this prevents redundant Render rebuilds without suppressing deployment of application, workflow, configuration, or documentation changes that can affect the production artifact.
