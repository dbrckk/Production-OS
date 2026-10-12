# Production readiness

## Remote single-asset delivery with an explicit destination (offline CI qualified)

Before this correction, `execute_asset_forge(..., mode="github",
target_path=...)` returned a fire-and-forget dispatch receipt and ignored
`target_worktree`, `target_repository` and `target_ref`: the requested
consumer was never populated. Calls **without** a destination keep the
existing asynchronous dispatch behavior.

When a delivery destination is supplied, the direct GitHub-mode API now
uses the existing one-item **remote transactional batch**, waits for
its correlated workflow and ZIP, validates the native producer report and
SHA-256 companions, then delivers to the specified worktree or GitHub
branch before returning `delivery_mode` and `delivered_to`. A direct
request must include `target_path`; it rejects local file references
which the hosted workflow cannot access. Direct remote deliveries to a
GitHub repository require an **explicit non-default review branch**
(`--target-ref`); implicit `main`/`master` delivery fails before
dispatch to avoid modifying released files outside PR review.

The **remote batch API** independently requires a consumer destination and
refuses implicit `main`/`master` repository writes **before creating its
output directory or invoking Asset Forge**, not only when called through the
single-asset wrapper. This closes the direct-batch bypass and prevents an
otherwise guaranteed failed batch from incurring remote generation cost.
The existing native producer → Godot functional smoke checks these negative
batch calls offline, without any hosted dispatch or new unit tests.

Existing `.asset-forge.json` receipts are integrity metadata, not disposable cache.
An invalid JSON/non-object/invalid-encoding receipt on a GitHub review branch,
or an unreadable or structurally invalid local/worktree or GitHub receipt,
**blocks delivery before any asset write** instead of silently resetting its
version history. A prior receipt must have the expected schema, target path,
positive integer version, SHA-256 digest and list-valued history/companions. A genuinely absent
receipt still starts at version 1. The existing native Asset Forge → Godot 4
functional smoke includes both negative delivery cases without invoking GPU,
network providers or creating unit tests.

For GitHub review branches, the previous `.asset-forge.json` receipt
must be read from the **same destination branch**, not the default
branch; otherwise a successful delivery can reset version history.
`GitHubClient.read_json_file(..., ref=target_ref)` now qualifies the
GET with an encoded branch ref, retaining backward compatibility for
default-main lookups. The destination branch HEAD is captured before reading
receipts and passed to `GitHubClient.commit_files(expected_sha=...)`. If the
branch moves, the transaction fails before constructing any Git blob; if it
moves during the Git commit, GitHub's `force=false` ref update must reject
the non-fast-forward. No retry is attempted with stale receipt metadata.
The existing functional integration smoke verifies
this offline using an instrumented real GitHub client and a simulated
version 7 → 8 GitHub review-branch transaction; there is no network
request, hosted dispatch or test-only production implementation. It also
simulates concurrent movement of a review branch between receipt reads and
commit, requiring a refusal with zero asset writes.

Hosted ZIP bundles are preflighted **before creating an extraction directory**.
File entries that collide after casefold + Unicode NFC normalization, repeated
separators, or file/directory parent conflicts are rejected, preventing
silent overwrites and ambiguous checksums on cross-platform consumers. The
existing functional Godot smoke exercises the native producer ZIP and negative
ambiguous-archive cases, without external inference or a new unit-test file.
The same preflight also rejects Windows-reserved device basenames (including
`CON`, `COM1`, `LPT1`), alternate-data-stream colons, forbidden characters,
control bytes and segments ending in a dot or space. Without this guard, a ZIP
accepted on Linux can fail or alias another path on a Windows consumer. The
existing genuine producer → Godot smoke includes these negative ZIP cases and
asserts that rejected archives do not create an extraction directory.

The **consumer destination preflight** applies these same portable segment
rules to user-supplied `target_path` before starting either local asset
generation or a remote GitHub workflow. It rejects Windows devices, colon/ADS,
wildcards and trailing dot/space components, and also rejects file-vs-child
conflicts across requested batch targets (including Unicode/case aliases)
before creating a batch output directory. The transactional delivery stage
independently rejects conflicts involving generated metadata sidecars and
Godot companion files, before any target repository/worktree mutation.
The existing native producer → Godot functional smoke covers these failures
offline; it does not prove execution on a physical Windows machine.

For local transactional batches, a valid ASCII `requestId` alone is not
sufficient: a pre-existing symlink at `output_root/requestId` can redirect
generated report/assets outside the designated job root. The consumer now
resolves all job paths against the resolved batch root before starting **any**
local generator. An escaping path aborts with no producer invocation. The
existing real producer → Godot functional smoke exercises a malicious
external-target symlink without network, secrets or GPU. This static
preflight is not a guarantee against concurrent filesystem mutation by an
untrusted process. A second ambiguity exists when a job path is a symlink
**inside** the output root to another job; that is now rejected as well,
instead of writing another job's production report. The same cross-platform
file-component rules already used for delivery paths now reject reserved
Windows names such as `CON`, `AUX.log` and `LPT9.data` in request/item
identifiers before dispatch. Both cases are exercised by the existing
functional Godot smoke without introducing new unit tests.

**Direct local single-asset delivery** validates the complete destination
contract before starting generation: a supplied `target_path` must be
portable and paired with a consumer worktree or repository, and an explicit
consumer requires a nonempty target path. This avoids generation cost and
partially created output folders for invalid local delivery requests. The
existing native producer → Godot 4 smoke checks invalid paths, Windows
devices and mismatched destination options offline. No paid provider
is invoked for these cases.

The existing `integration/real_producer_bundle_smoke.py` verifies the
direct route using a **native pinned Asset Forge ZIP** created from an
original local PNG and consumed by real Godot 4.4.1. It also proves that
an implicit remote `main` write is blocked before triggering an Action.
No GPU, remote dispatch, secrets, old canaries, new unit tests, merge or
deployment. **Exact code HEAD `b94069ffa70bd1ac6e7ee5d8ece89a01293c26bc` CI [38156921965](https://github.com/dbrckk/Production-OS/actions/runs/38156921965) COMPLETED SUCCESS 4/4** (Python 3.11/3.12, real Godot 4.4.1 consumer import, production E2E/build/Docker and remote integrity smoke); this is still not a live
worker-to-PR/CI/game qualification.

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
consumer rejects the archive before writing any asset. The first CI run
38155804378 FAILED in the smoke itself because it handed a bytes object
instead of io.BytesIO to zipfile.ZipFile during tampering; this was corrected
without changing the production contract. The corrected code on exact HEAD
02641f4d87b58f1219d41a84367c04d244cfd482 passed CI 38155924949
COMPLETED SUCCESS (4/4: real Godot 4 integration, Python 3.11/3.12,
existing E2E/build and Docker). The real producer-to-consumer and negative
SHA256 scenarios printed PASS in the CI job logs.

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
