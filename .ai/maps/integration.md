This file is a merged representation of a subset of the codebase, containing specifically included files and files not matching ignore patterns, combined into a single document by Repomix.
The content has been processed where content has been compressed (code blocks are separated by ⋮---- delimiter).

# File Summary

## Purpose
This file contains a packed representation of a subset of the repository's contents that is considered the most important context.
It is designed to be easily consumable by AI systems for analysis, code review,
or other automated processes.

## File Format
The content is organized as follows:
1. This summary section
2. Repository information
3. Directory structure
4. Repository files (if enabled)
5. Multiple file entries, each consisting of:
  a. A header with the file path (## File: path/to/file)
  b. The full contents of the file in a code block

## Usage Guidelines
- This file should be treated as read-only. Any changes should be made to the
  original repository files, not this packed version.
- When processing this file, use the file path to distinguish
  between different files in the repository.
- Be aware that this file may contain sensitive information. Handle it with
  the same level of security as you would the original repository.

## Notes
- Some files may have been excluded based on .gitignore rules and Repomix's configuration
- Binary files are not included in this packed representation. Please refer to the Repository Structure section for a complete list of file paths, including binary files
- Only files matching these patterns are included: **/*.{py,js,mjs,cjs,ts,tsx,jsx,java,kt,kts,gd,groovy,gradle,toml,json,yaml,yml,sql,sh}
- Files matching these patterns are excluded: .ai/**, **/node_modules/**, **/.gradle/**, **/build/**, **/dist/**, **/.venv/**, **/__pycache__/**, **/.pytest_cache/**, **/.git/**, **/coverage/**, **/*.lock, **/*.min.js, **/*.map, assets/**, art/**, art_sources/**, marketing/**, colab/**, kaggle/**, discovery-cache.json, health-snapshot.json, history.json
- Files matching patterns in .gitignore are excluded
- Files matching default ignore patterns are excluded
- Content has been compressed - code blocks are separated by ⋮---- delimiter
- Files are sorted by Git change count (files with more changes are at the bottom)

# Directory Structure
```
godot4_relocated_import_smoke.py
real_producer_bundle_smoke.py
```

# Files

## File: godot4_relocated_import_smoke.py
```python
#!/usr/bin/env python3
"""Offline Production-OS remote delivery -> real Godot 4 editor/runtime smoke.

Generates an ORIGINAL local RGBA PNG and SpriteFrames with the actual Godot
editor, then passes the hashed bytes through the real Production-OS remote
batch parser and transactional worktree delivery. No inference, token, network
dispatch, external art or new unit tests. GODOT_BIN must point to Godot 4.
"""
⋮----
GENERATOR = """extends SceneTree
⋮----
VALIDATOR = """extends SceneTree
⋮----
def run(command: list[str], *, cwd: Path, marker: str | None = None) -> None
⋮----
result = subprocess.run(command, cwd=cwd, text=True, capture_output=True,
output = result.stdout + "\n" + result.stderr
⋮----
def original_png() -> bytes
⋮----
# Deterministically generate two original 32x32 drawings, with alpha.
def chunk(name: bytes, data: bytes) -> bytes
rows = []
⋮----
row = bytearray(b"\x00")
⋮----
class OfflineClient
⋮----
def __init__(self, archive: bytes) -> None
⋮----
def can_dispatch_workflow(self, *_args) -> bool
⋮----
def dispatch_workflow(self, _repo, _workflow, *, ref, inputs) -> None
⋮----
def wait_for_workflow_run(self, *_args, **_kwargs) -> dict
⋮----
def workflow_run_artifacts(self, *_args) -> list[dict]
⋮----
def download_workflow_artifact(self, *_args) -> bytes
⋮----
def main() -> None
⋮----
raw_bin = os.environ.get("GODOT_BIN", "").strip()
⋮----
godot = str(Path(raw_bin).resolve(strict=True))
⋮----
root = Path(temp)
original = root / "original"
⋮----
primary = original_png()
⋮----
tres = (original / "player.tres").read_bytes()
⋮----
metadata = json.dumps({
parts = {"bundle/hero.png": primary, "bundle/hero.tres": tres,
request_id = "godot-relocated-engine-smoke"
request = build_asset_forge_request(
target = "assets/characters/player.png"
extras = [
row = {
report = {
zip_buffer = io.BytesIO()
⋮----
consumer = root / "consumer"
⋮----
delivered = execute_asset_forge_batch(
⋮----
relocated_tres = consumer / "assets/characters/player.tres"
⋮----
meta = json.loads((consumer / "assets/characters/player.atlas-metadata.json").read_text())
⋮----
# Real local Asset Forge CLI, no fake generation, and verified cache repair.
source_root = os.environ.get("ASSET_FORGE_SOURCE_DIR", "").strip()
⋮----
forge_entry = Path(source_root).resolve(strict=True) / "asset_forge.py"
⋮----
binary_dir = root / "local-cli-bin"
⋮----
wrapper = binary_dir / "asset-forge"
shell_command = (
⋮----
local_request = build_asset_forge_request(
⋮----
local_items = [{
old_path = os.environ.get("PATH", "")
⋮----
first = execute_asset_forge_batch(
⋮----
receipt = json.loads(
⋮----
payload = (consumer / record["target_path"]).read_bytes()
⋮----
# A valid cache must work with the CLI removed.
⋮----
cached = execute_asset_forge_batch(
⋮----
# A cache from one generator/model must never masquerade as
# a different generation. The CLI is absent here: a wrong cache
# hit would succeed, while correct invalidation must refuse.
receipt_path = consumer / (target + ".asset-forge.json")
baseline_receipt = receipt_path.read_bytes()
⋮----
tres = consumer / "assets/characters/player.tres"
clean = tres.read_bytes()
⋮----
# A true CLI production repairs both files, then Godot reimports.
⋮----
repaired = execute_asset_forge_batch(
⋮----
# Single-asset API must preserve the complete Godot handoff too.
single_consumer = root / "single-consumer"
⋮----
direct = execute_asset_forge(
⋮----
single_receipt = json.loads(
⋮----
payload = (single_consumer / companion["target_path"]).read_bytes()
⋮----
# Reproduce real input drift without provider calls: run the
# original owned-image Asset Forge CLI, then alter the source or
# visual reference before Production-OS can publish a receipt.
# No consumer asset or sidecar may be written by these attempts.
drift_source = root / "drift-source.png"
drift_reference = root / "drift-reference.png"
drift_consumer = root / "drift-consumer"
⋮----
real_cli_run = subprocess.run
⋮----
def change_input_after_real_cli(*args, **kwargs)
⋮----
completed = real_cli_run(*args, **kwargs)
⋮----
changed = drift_reference if drift_kind == "direct-reference" else drift_source
⋮----
# Same original PNG source, but a newly supplied reference image,
# must cause a new receipt version even if output bytes match.
reference_png = root / "owned-reference.png"
⋮----
receipt_path = single_consumer / (target + ".asset-forge.json")
baseline = json.loads(receipt_path.read_text(encoding="utf-8"))
⋮----
supplied = execute_asset_forge(
first_ref = json.loads(receipt_path.read_text(encoding="utf-8"))
⋮----
# Add a valid original PNG text chunk: its reference contents
# change, whereas the actual source image and final pixels do not.
ref_content = b"project-owned\x00alternate-reference"
ref_chunk = (
⋮----
changed_ref = json.loads(receipt_path.read_text(encoding="utf-8"))
⋮----
# A missing explicit local reference is rejected before any
# generation output directory or consumer write exists.
invalid_output = root / "invalid-reference-production"
```

## File: real_producer_bundle_smoke.py
```python
#!/usr/bin/env python3
"""Actual pinned Asset Forge producer bundle -> Production-OS consumer -> Godot 4.

This is a functional integration smoke, not a new unit test. It uses only
locally authored original PNG pixels and the real Asset Forge CLI; no paid
inference, hosted dispatch, credentials, old canaries, or network is invoked.
"""
⋮----
def main() -> None
⋮----
godot_bin = os.environ.get("GODOT_BIN", "").strip()
source_dir = os.environ.get("ASSET_FORGE_SOURCE_DIR", "").strip()
⋮----
godot = str(Path(godot_bin).resolve(strict=True))
forge_dir = Path(source_dir).resolve(strict=True)
⋮----
root = Path(temp)
originals = root / "original-art"
⋮----
image = originals / "owned-player.png"
image_bytes = original_png()
⋮----
request = build_asset_forge_request(
⋮----
target = "assets/characters/player.png"
item = {"id": "player", "request": request,
spec = root / "producer-spec.json"
⋮----
# Keep CLI execution self-contained and deterministic without any
# provider credential, model selection, or remote source paths.
bin_dir = root / "bin"
⋮----
wrapper = bin_dir / "asset-forge"
⋮----
produced_root = root / "native-bundle"
original_root = os.environ.get("ASSET_FORGE_BATCH_SOURCE_ROOT")
⋮----
produced = run_real_producer(
⋮----
row = produced["items"][0]
roles = {comp.get("role") for comp in row.get("additional_artifacts") or []}
⋮----
# Produce exactly the ZIP layout the GitHub workflow uploads from
# the real remote_batch output tree, not synthetic report fixtures.
archive_bytes = io.BytesIO()
⋮----
source_archive = archive_bytes.getvalue()
⋮----
# An untrusted ZIP must be fully preflighted before any extraction:
# aliases, Unicode NFC names, duplicate separators and parent/file
# conflicts all risk overwriting earlier bundle entries.
ambiguous_bundles = (
⋮----
suspicious = io.BytesIO()
⋮----
should_not_exist = root / f"unsafe-zip-preflight-{index}"
⋮----
# A ZIP central directory can have valid paths and declared sizes
# while a later stored entry fails its CRC. Without preflight, the
# preceding file is written first, including an overwrite of a real
# existing file. Test both a new directory and a populated one.
corrupt_zip = io.BytesIO()
crc_original = b"original-owned-crc-verification-payload"
⋮----
corrupted_bytes = bytearray(corrupt_zip.getvalue())
corrupt_at = corrupted_bytes.index(crc_original) + 4
⋮----
corrupt_root = root / (
owned_marker = corrupt_root / "owned-marker.bin"
⋮----
# An existing hardlinked filename is an alias too: writing the ZIP
# member would change a protected file outside the extraction root.
owned_hardlink_target = root / "owned-zip-hardlink-source.bin"
⋮----
zip_hardlink_root = root / "unsafe-zip-existing-hardlink"
⋮----
hardlink_zip = io.BytesIO()
⋮----
# A symbolic link on the extraction ROOT (or one of its parents)
# must be rejected before unzipping to the resolved external folder.
zip_root_owner = root / "protected-zip-extraction-root"
⋮----
zip_root_marker = zip_root_owner / "keep-owned.bin"
⋮----
zip_root_link = root / "zip-extraction-root-link"
⋮----
# A pre-existing directory where the ZIP expects a file, or a
# regular file where it expects a parent directory, must be refused
# BEFORE any earlier good ZIP entry is written. Previously the first
# entry was extracted, then an IsADirectoryError/FileExistsError
# interrupted extraction and left a partial bundle.
⋮----
conflict_root = root / ("unsafe-zip-existing-type-" + conflict)
⋮----
marker = conflict_root / "owned-marker.bin"
⋮----
conflicting_entry = "blocked.png"
⋮----
conflicting_entry = "blocked/child.png"
archive_buffer = io.BytesIO()
⋮----
# Pre-existing case/Unicode aliases are just as ambiguous as symlinks
# when the consumer runs on case-insensitive or NFC-normalizing hosts.
# Refuse the *entire* archive without altering earlier files.
⋮----
alias_root = root / ("unsafe-zip-existing-portable-" + alias_kind)
⋮----
existing_path = alias_root / existing_name
⋮----
protected = existing_path / "preserved.bin"
⋮----
protected = existing_path
⋮----
bundle = io.BytesIO()
⋮----
# An existing *internal* symlink aliases another file in the same
# extraction root. Earlier path-escape checks accepted such aliases,
# overwriting files the producer ZIP did not explicitly name.
# Reject the whole archive before extracting even its first good file.
⋮----
alias_root = root / ("unsafe-zip-existing-symlink-" + alias_type)
⋮----
protected = alias_root / "protected"
⋮----
preserved = protected / "owned.png"
⋮----
malicious_entry = "aliased.png"
⋮----
malicious_entry = "aliased/owned.png"
⋮----
dispatch_item = {"id": item["id"], "request": request, "target_path": target}
⋮----
# A second job may choose the first sheet's SpriteFrames or atlas
# companion as its own output. Such a batch must be rejected *before*
# creating an output root or trying a paid/hosted producer.
⋮----
second = json.loads(json.dumps(request))
⋮----
conflicting_items = [
⋮----
refused_root = root / (
⋮----
consumer = root / "verified-consumer"
⋮----
delivered = execute_asset_forge_batch(
⋮----
version = json.loads(
⋮----
resource = consumer / companion["target_path"]
⋮----
# Direct GitHub-mode single-asset calls must no longer return a mere
# dispatch receipt when a consumer delivery was explicitly requested.
single = root / "direct-github-consumer"
⋮----
direct = execute_asset_forge(
⋮----
direct_version = json.loads(
⋮----
# Refuse to dispatch a billed remote generation when delivery would
# silently write a repository's default branch without PR review.
⋮----
# Case variants of GitHub's default branch are not review branches.
# They must fail before any remote workflow call or output write.
⋮----
# Batch callers previously bypassed the direct API's main-branch
# guard, or dispatched generation with no consumer at all. Both must
# fail before creating output or reaching a remote workflow.
blocked_batch_root = root / "blocked-batch-destination"
⋮----
# Explicit local raster sources cannot be fulfilled by a remote
# worker. Fail *before* any GitHub dispatch or output directory,
# including auto mode when the local CLI is unavailable. The same
# restriction also applies to fire-and-forget single requests, which
# previously silently discarded source/reference inputs.
⋮----
refused = root / ("blocked-remote-local-source-" + remote_mode)
⋮----
# Existing end-to-end smoke also verifies destination preflight.
# None of these cases may dispatch, generate, or create receipt files.
bad_receipt = root / "blocked-path-receipt"
⋮----
first = "assets/player.png" if "PLAYER" in second else "assets/café.png"
⋮----
# These distinct strings still conflict as file and parent folder.
⋮----
# The consumer must reject producer-incompatible IDs before any
# local job directory, remote dispatch, or artifact write.
⋮----
unsafe_request = dict(request)
⋮----
first = dict(request)
second = dict(request)
⋮----
# A direct local request formerly checked destination paths only
# after generating an asset. Refuse unsafe or missing destinations
# before creating even the local output directory or invoking CLI.
bad_local_root = root / "blocked-local-single"
⋮----
# Direct local generation must not follow a symlinked output root
# (or an ancestor), including when no consumer delivery is requested.
# The batch API already rejects its output_root symlinks.
⋮----
protected_root = root / ("protected-single-output-" + alias_type)
⋮----
protected_marker = protected_root / "do-not-touch.bin"
⋮----
link = root / ("single-output-link-" + alias_type)
⋮----
output_destination = link if alias_type == "root" else link / "generated"
⋮----
# Existing regular files also cannot serve as local generator output.
blocked_direct_file = root / "blocked-single-output-file"
⋮----
# A missing explicit source must never become an implicit no-source
# fingerprint, reuse a cache entry, or start generator work.
absent_source = root / "missing-owned-source.png"
direct_absent = root / "blocked-missing-direct-source"
⋮----
# Reference inputs were previously fingerprint-preflighted only when
# a consumer delivery target was provided. Local producer-only mode
# must reject missing, directory and malformed references just as
# strongly, before creating output or invoking a generator.
⋮----
refused_output = root / (
⋮----
# An explicitly supplied empty source is invalid: it must not fall
# back to no-source generation just because the string is falsey.
⋮----
refused_output = root / ("blocked-empty-source-" + delivery_case)
⋮----
# Validate *all* source paths before creating output even if another
# item in the batch has a valid, cacheable target.
⋮----
absent_batch = root / ("blocked-missing-batch-" + batch_mode)
⋮----
# A locally generated asset must not be pushed directly to GitHub's
# default branch without an explicit review branch. This is refused
# before any CLI or expensive generation.
blocked_local_github = root / "blocked-local-main-delivery"
⋮----
# A destination alias must be blocked *before* local CLI generation
# or remote dispatch, not just by the final transactional write.
⋮----
blocked_root = root / ("preflight-alias-" + alias)
characters = blocked_root / "assets" / "characters"
⋮----
protected = root / ("preflight-protected-" + alias + ".bin")
⋮----
name = "player.png" if alias == "asset" else "player.png.asset-forge.json"
⋮----
output = root / ("no-generation-" + alias + "-" + delivery)
⋮----
# Existing hardlinks look like regular files, but overwriting
# them silently mutates the other linked inode outside the consumer.
# Refuse both media and receipt aliases before producer/provider calls.
⋮----
hardlink_root = root / ("hardlink-consumer-" + hardlink_kind)
owned_target = root / ("owned-hardlink-" + hardlink_kind + ".bin")
⋮----
alias = hardlink_root / (
⋮----
blocked_output = root / (
⋮----
# An existing worktree ROOT may itself be a regular file.
# Reject it before creating output or invoking the actual producer
# (or dispatching a remote workflow), not only at final delivery.
blocked_root_file = root / "invalid-consumer-root.bin"
⋮----
output = root / ("no-generation-root-file-" + blocked_mode)
⋮----
# The consumer root itself (or one of its ancestors) may be a
# symlink. Path.resolve() must not silently redirect an asset delivery
# into a different, unintended workspace. Refuse *before* generating
# locally or dispatching the offline-correlated remote batch.
protected_consumer_root = root / "protected-consumer-root"
⋮----
protected_consumer_marker = protected_consumer_root / "do-not-touch.bin"
⋮----
linked_consumer_root = root / "linked-consumer-root"
⋮----
linked_consumer_parent = root / "linked-consumer-parent"
⋮----
# An unsupported mode must not make a generation directory either.
invalid_mode_root = root / "no-generation-invalid-mode"
⋮----
# A pre-existing job directory symlink may escape the batch output
# root even when requestId is otherwise a safe single component.
linked_root = root / "linked-local-jobs"
⋮----
outside_job = root / "outside-local-job"
⋮----
# A symlink to a *different job inside the same output root* also
# aliases paths and can overwrite another production report.
alias_root = root / "aliased-local-jobs"
⋮----
other_job = alias_root / "existing-other-job"
⋮----
# Existing file and directory names may have cross-platform aliases
# on Windows or NFC-normalizing filesystems. Refuse before any local
# generation or provider dispatch, including a case-aliased filename
# and a Unicode-equivalent filename.
⋮----
alias_consumer = root / ("cross-platform-alias-" + case_name)
protected_alias = alias_consumer / "assets" / "characters" / existing_name
⋮----
blocked_output = root / ("no-generation-cross-platform-" + case_name + "-" + alias_mode)
⋮----
# Pre-existing local job directories must be real directories. A
# regular-file collision on a later job must refuse the entire batch
# before the first item can generate anything.
job_type_root = root / "blocked-local-job-file"
⋮----
blocked_job = job_type_root / "blocked-job"
⋮----
first_job_id = "unused-first-job"
second_request = {
first_request = {
⋮----
# The configured batch output root itself cannot be a symlink to an
# unrelated working directory, even when each job id is safe.
linked_output = root / "aliased-batch-output-root"
guarded_output = root / "guarded-output-root"
⋮----
# The batch output leaf may be a normal path while its *parent*
# aliases another directory. Fail before mkdir, a local producer,
# or the offline-correlated GitHub dispatch in both modes.
guarded_parent = root / "guarded-batch-output-parent"
⋮----
marker_file = guarded_parent / "do-not-touch.bin"
⋮----
alias_parent = root / "batch-output-parent-link"
⋮----
nested_output = alias_parent / "nested" / "jobs"
⋮----
# Verify real GitHub Contents ref encoding and branch-specific
# version continuity using an offline recording client.
class OfflineReviewBranch(GitHubClient)
⋮----
def __init__(self, receipt=None, *, move_before_commit=False)
⋮----
def _get(self, path)
⋮----
def branch_head_sha(self, repository, branch)
⋮----
def commit_files(self, repository, files, *, message, branch, expected_sha=None)
⋮----
# Reproduce the original TOCTOU gap with a real PNG and offline
# review-branch client: the producer mutates its path *after* the
# initial integrity check, during the GitHub branch-head read. Both
# the media payload and SHA receipt must still describe the same
# original bytes. No hosted workflow or API request is made.
class OfflineLateProducerMutation(OfflineReviewBranch)
⋮----
def __init__(self)
⋮----
frozen_review = OfflineLateProducerMutation()
frozen_item = {
⋮----
frozen_receipt = json.loads(
⋮----
# Preserve legacy GitHubAPIError("GitHub API NNN: ...") callers while
# never considering a status number quoted only inside a response body.
⋮----
# GitHub response bodies are untrusted: their text must never spoof
# a different HTTP status and erase a review-branch version receipt.
class OfflineStatusClient(GitHubClient)
⋮----
def __init__(self, code: int, body: str)
⋮----
def _get(self, _path)
⋮----
def _request(self, _method, _path, _payload=None)
⋮----
misleading = OfflineStatusClient(
⋮----
missing = OfflineStatusClient(404, '{"message": "Not Found"}')
⋮----
class OfflinePermissionError(OfflineStatusClient)
⋮----
spoofed = OfflinePermissionError(
⋮----
review_ref = "review/asset-handoff"
review_item = {
# Two produced files may not be stable by the time transactional
# delivery starts. Corrupt the second item *after* recording its real
# authored PNG SHA-256, then prove that neither the first nor second
# output, nor any version receipt, was written to either consumer.
drift_media = root / "changed-after-production.png"
⋮----
original_drift_sha = hashlib.sha256(drift_media.read_bytes()).hexdigest()
⋮----
drift_target = "assets/characters/changed-after-production.png"
drift_item = {
drift_batch = [review_item, drift_item]
drift_consumer = root / "reject-stale-producer-outputs"
protected_media = drift_consumer / target
⋮----
rejected_github = OfflineReviewBranch()
⋮----
# Direct callers of the shared transactional writer must not bypass
# the public preflight and follow consumer-root symlink aliases.
⋮----
# Internal shared delivery must independently reject names that
# would overwrite or collide across Windows/Unicode-normalizing hosts.
⋮----
shared_consumer = root / ("shared-cross-platform-alias-" + alias_kind)
protected_alias = shared_consumer / "assets" / "characters" / existing_name
⋮----
# Refuse same-root aliases before writing any asset or receipt.
⋮----
worktree = root / f"consumer-symlink-{alias_case}"
assets_root = worktree / "assets"
⋮----
alternate = assets_root / "elsewhere"
⋮----
protected = alternate / "unrelated.bin"
⋮----
characters = assets_root / "characters"
⋮----
protected = characters / "unrelated.bin"
link_name = (
⋮----
# The shared transaction must check existing destination file types
# before staging *any* asset, even when invoked without outer preflight.
# These are not links: a directory at a media/receipt path or a file
# at a parent path must never create a partial asset or receipt.
⋮----
worktree = root / ("consumer-type-" + blocked_kind)
media = worktree / target
receipt_path = worktree / (target + ".asset-forge.json")
⋮----
preserved = media
⋮----
preserved = receipt_path
⋮----
preserved = worktree / "assets" / "characters"
⋮----
# Internal callers must not bypass the hardlink guard merely
# because they skip the public pre-generation validation.
⋮----
internal_root = root / ("hardlink-internal-" + hardlink_kind)
protected = root / ("hardlink-internal-owner-" + hardlink_kind + ".bin")
⋮----
hardlinked_path = internal_root / (
⋮----
# Direct shared-helper calls must also refuse GitHub default branches.
⋮----
forbidden = OfflineReviewBranch()
⋮----
github = OfflineReviewBranch()
⋮----
expected_url = (
⋮----
version = json.loads(github.written_files[target + ".asset-forge.json"].decode("utf-8"))
⋮----
# Identical bytes do not imply the same asset provenance. A new
# semantic request must advance the version and preserve fingerprint
# history, while an exact retry stays on its existing version.
source_version = json.loads(
⋮----
original = OfflineReviewBranch(receipt=json.dumps(source_version))
rerun = {**review_item, "request_fingerprint": new_fingerprint}
⋮----
new_version = json.loads(
⋮----
old_record = new_version["history"][-1]
⋮----
# Exercise a concurrent branch change after reading the receipt.
# No stale version can be committed on top of another writer's HEAD.
moved = OfflineReviewBranch(move_before_commit=True)
⋮----
# A corrupt existing receipt cannot be silently replaced with version 1.
# The actual GitHubClient must reject malformed JSON before commit_files.
⋮----
blocked = OfflineReviewBranch(receipt=malformed)
⋮----
# A list-typed history/companion field with corrupt *entries* must
# never propagate into a new GitHub version receipt.
good_history = {
invalid_nested_receipts = (
⋮----
blocked = OfflineReviewBranch(receipt=json.dumps(invalid))
⋮----
# The real worktree delivery path must also refuse malformed history
# before touching the existing PNG, sidecars or the corrupt metadata.
local_sidecar = consumer / (target + ".asset-forge.json")
original_sidecar = local_sidecar.read_bytes()
original_artifact = (consumer / target).read_bytes()
⋮----
# A valid real Godot cache can carry malformed producer-provided
# visual metadata. Historically the batch wrote the receipt and
# only then raised when parsing its quality summary. Prove that
# an error never mutates the consumer after a reported failure.
⋮----
invalid_metric = json.loads(original_sidecar.decode("utf-8"))
⋮----
protected_metric_receipt = local_sidecar.read_bytes()
⋮----
# Tamper with the REAL producer .tres byte payload but preserve its
# real declared checksum; fail closed before any consumer file write.
tres_path = next(
tampered_zip = io.BytesIO()
⋮----
content = genuine.read(member.filename)
⋮----
rejected_root = root / "rejected-consumer"
```
