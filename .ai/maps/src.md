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
production_os/
  __init__.py
  adaptation_plan.py
  adaptation.py
  api_auth.py
  approvals.py
  asset_forge.py
  asymmetric_attestations.py
  atomic_io.py
  attestations.py
  audit_checkpoint.py
  audit_integrity.py
  backup.py
  budgets.py
  builder_identity.py
  callgraph.py
  capabilities.py
  change_impact.py
  claims.py
  classification.py
  cli.py
  compatibility.py
  components.py
  control_plane.py
  control_surface.py
  controller.py
  dashboard_alerts.py
  dashboard_backups.py
  dashboard_control.py
  dashboard_github.py
  dashboard_health.py
  dashboard_incidents.py
  dashboard_maintenance.py
  dashboard_playbooks.py
  dashboard_remediation_metrics.py
  dashboard_security.py
  dashboard_service.py
  dashboard_store.py
  dashboard_ui.py
  dashboard_usage.py
  database_maintenance_lock.py
  deep_fingerprint.py
  delivery.py
  dispatch.py
  dual_sign.py
  emergency.py
  execution_feedback.py
  execution_optimizer.py
  fairness.py
  feedback.py
  github_client.py
  github_webhook.py
  github_work_state.py
  governance.py
  graph.py
  health_server.py
  health.py
  heartbeat_manager.py
  history.py
  journal.py
  key_domains.py
  key_registry.py
  learning.py
  locks.py
  managed_projects.py
  metrics.py
  migration_registry.py
  migrations.py
  models.py
  observability.py
  policy_validation.py
  policy.py
  portfolio_optimizer.py
  postgres_backend.py
  preemption.py
  project_progress.py
  quarantine.py
  queue_maintenance.py
  rate_limit.py
  receipts.py
  reconciliation.py
  rekor_checkpoint_state.py
  rekor_witness_quorum.py
  release_ledger.py
  remote_worker_runner.py
  remote_worker.py
  resources.py
  result_cache.py
  reuse.py
  runtime_state.py
  scheduler.py
  scoring.py
  self_healing.py
  signer_factory.py
  signers.py
  signing.py
  source_tree.py
  speculation.py
  sqlite_backend.py
  sqlite_migration.py
  starlist.py
  storage.py
  supply_chain.py
  task_capabilities.py
  transparency_receipts.py
  transparency.py
  trends.py
  trust_policy.py
  validation.py
  vault_auth.py
  vault_signer.py
  versioning.py
  witness.py
  workers.py
  workflow_engine.py
```

# Files

## File: production_os/__init__.py
```python
"""Production-OS portfolio control plane."""
⋮----
__version__ = "0.1.0"
```

## File: production_os/adaptation_plan.py
```python
@dataclass(frozen=True, slots=True)
class AdaptationPlan
⋮----
source_repository: str
target_repository: str
capability: str
strategy: str
copy_or_adapt: tuple[dict, ...]
recreate: tuple[str, ...]
reuse_tests: tuple[dict, ...]
do_not_copy: tuple[dict, ...]
target_changes: tuple[str, ...]
overall_risk: int
⋮----
def to_dict(self) -> dict
⋮----
def _is_ui_coupled(component: dict) -> bool
⋮----
name = str(component.get("name", "")).lower()
path = str(component.get("path", "")).lower()
⋮----
def _is_low_value_for_reuse(component: dict) -> bool
⋮----
copy_or_adapt: list[dict] = []
do_not_copy: list[dict] = []
tests: list[dict] = []
recreate: set[str] = set()
target_changes: set[str] = set()
⋮----
dep_name = str(dep)
⋮----
target_lang = target.evidence.language.lower()
source_lang = str(component["language"]).lower()
⋮----
unique_tests = {
⋮----
avg_risk = round(
strategy = "component-adaptation"
⋮----
candidate_risks = [
avg_risk = min(candidate_risks) if candidate_risks else 75
strategy = "architecture-pattern-only"
```

## File: production_os/adaptation.py
```python
@dataclass(frozen=True, slots=True)
class ComponentAdaptation
⋮----
source_repository: str
target_repository: str
capability: str
component_name: str
path: str
language: str
risk_score: int
risk_level: str
reasons: tuple[str, ...]
linked_tests: tuple[dict, ...]
⋮----
def to_dict(self) -> dict
⋮----
def _normalize(name: str) -> str
⋮----
def link_tests(source: RepoAssessment, component) -> tuple[dict, ...]
⋮----
target = _normalize(component.name)
matches = []
⋮----
cname = _normalize(candidate.name)
path = candidate.path.lower()
⋮----
score = 0
reasons = []
⋮----
risk = 10
reasons: list[str] = []
⋮----
target_lang = target.evidence.language.lower()
comp_lang = component.language.lower()
compatible = (
⋮----
dep_count = len(component.dependencies)
⋮----
linked_tests = link_tests(source, component)
⋮----
risk = max(0, min(100, risk))
⋮----
level = "low"
⋮----
level = "medium"
⋮----
level = "high"
⋮----
level = "very-high"
```

## File: production_os/api_auth.py
```python
ROLE_LEVEL = {
⋮----
def token_digest(token: str) -> str
⋮----
@dataclass(frozen=True, slots=True)
class Principal
⋮----
name: str
role: str
⋮----
def allows(self, required_role: str) -> bool
⋮----
class TokenAuthorizer
⋮----
def __init__(self, entries: list[dict])
⋮----
@classmethod
    def load(cls, path: str | Path | None) -> "TokenAuthorizer"
⋮----
source = Path(path)
⋮----
payload = json.loads(source.read_text(encoding="utf-8"))
entries = payload.get("tokens", [])
⋮----
def authenticate(self, token: str | None) -> Principal | None
⋮----
digest = token_digest(token)
⋮----
expected = str(entry.get("sha256", ""))
⋮----
role = str(entry.get("role", "viewer"))
```

## File: production_os/approvals.py
```python
@dataclass(slots=True)
class Approval
⋮----
key: str
approved: bool
approved_by: str | None = None
reason: str | None = None
updated_at: str | None = None
⋮----
def to_dict(self) -> dict
⋮----
class ApprovalStore
⋮----
def __init__(self, path: str | Path)
⋮----
def _load_unlocked(self) -> None
⋮----
payload = json.loads(self.path.read_text(encoding="utf-8"))
⋮----
item = Approval(**row)
⋮----
def load(self) -> None
⋮----
def _save_unlocked(self) -> None
⋮----
item = Approval(
⋮----
def is_approved(self, key: str) -> bool
⋮----
item = self.approvals.get(key)
```

## File: production_os/asset_forge.py
```python
ASSET_FORGE_REPOSITORY = "dbrckk/asset-forge"
ASSET_FORGE_WORKFLOW = "production-os-dispatch.yml"
ASSET_FORGE_BATCH_WORKFLOW = "production-os-batch.yml"
⋮----
@dataclass(frozen=True)
class AssetForgeDispatch
⋮----
repository: str
workflow: str
ref: str
request_id: str
backend: str
mode: str = "github"
report_path: str | None = None
delivery_mode: str | None = None
delivered_to: str | None = None
⋮----
def to_dict(self) -> dict[str, str]
⋮----
request_id = str(request_id).strip()
project = str(project).strip()
asset_id = str(asset_id).strip()
asset_type = str(asset_type).strip()
instruction = str(instruction).strip()
target_format = str(target_format).strip().lower()
source_mode = str(source_mode).strip().lower()
importance = str(importance).strip().lower()
⋮----
required = {
missing = [name for name, value in required.items() if not value]
⋮----
request: dict[str, Any] = {
⋮----
canonical_request = {
source_sha256 = None
⋮----
source = Path(source_path)
⋮----
source_sha256 = hashlib.sha256(source.read_bytes()).hexdigest()
payload = {
⋮----
def _sidecar_relative_path(target_path: str) -> str
⋮----
root = Path(worktree).resolve()
normalized = target_path.strip().replace("\\", "/").lstrip("/")
artifact = (root / normalized).resolve()
sidecar = (root / _sidecar_relative_path(normalized)).resolve()
⋮----
metadata = json.loads(sidecar.read_text(encoding="utf-8"))
⋮----
digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
⋮----
existing = existing if isinstance(existing, dict) else {}
prior_sha = str(existing.get("sha256") or "")
prior_version = int(existing.get("version") or 0)
same = prior_sha == item["sha256"] and prior_version > 0
version = prior_version if same else prior_version + 1
history = list(existing.get("history") or []) if isinstance(existing.get("history"), list) else []
⋮----
history = history[-12:]
⋮----
def _validated_artifact(report: dict[str, Any], destination: Path) -> Path
⋮----
raw = str(report.get("artifact") or "").strip()
⋮----
artifact = Path(raw)
⋮----
candidate = destination / artifact
⋮----
artifact = candidate
⋮----
resolved_destination = destination.resolve()
resolved_artifact = artifact.resolve()
⋮----
root = Path(target_worktree).resolve()
destination = (root / normalized).resolve()
⋮----
gh = client or GitHubClient()
⋮----
local_cli = shutil.which("asset-forge")
effective = mode
⋮----
effective = "local" if local_cli else "github"
⋮----
request_id = str(request.get("requestId") or "").strip()
⋮----
destination = Path(output_dir or f"build/asset-forge/{request_id}")
⋮----
request_path = Path(tmp) / "request.json"
⋮----
cmd = [
⋮----
completed = subprocess.run(
⋮----
detail = (getattr(completed, "stderr", "") or getattr(completed, "stdout", "") or "").strip()
suffix = f": {detail}" if detail else ""
⋮----
report_path = destination / "production-report.json"
⋮----
report = json.loads(report_path.read_text(encoding="utf-8"))
⋮----
artifact = _validated_artifact(report, destination)
⋮----
delivery_mode = None
delivered_to = None
⋮----
def _batch_item_id(item: dict[str, Any], index: int) -> str
⋮----
explicit = str(item.get("id") or "").strip()
request = item.get("request")
request_id = str(request.get("requestId") or "").strip() if isinstance(request, dict) else ""
value = explicit or request_id or f"item-{index + 1}"
⋮----
def _order_asset_batch(items: list[dict[str, Any]]) -> list[dict[str, Any]]
⋮----
indexed: dict[str, dict[str, Any]] = {}
order_hint: list[str] = []
⋮----
item_id = _batch_item_id(item, index)
⋮----
copy = dict(item)
⋮----
indegree = {item_id: 0 for item_id in indexed}
dependents: dict[str, list[str]] = {item_id: [] for item_id in indexed}
⋮----
raw = item.get("depends_on") or []
⋮----
raw = [raw]
⋮----
dependencies = []
⋮----
dep_id = str(dep).strip()
⋮----
ready = [item_id for item_id in order_hint if indegree[item_id] == 0]
sorted_ids: list[str] = []
⋮----
current = ready.pop(0)
⋮----
blocked = [item_id for item_id in order_hint if indegree[item_id] > 0]
⋮----
def _extract_remote_batch_bundle(data: bytes, destination: Path) -> Path
⋮----
root = destination.resolve()
max_files = 5000
max_uncompressed = 512 * 1024 * 1024
total = 0
⋮----
infos = archive.infolist()
⋮----
name = info.filename.replace("\\", "/")
⋮----
parts = [part for part in name.split("/") if part]
⋮----
mode = (info.external_attr >> 16) & 0o170000
⋮----
target = (root / "/".join(parts)).resolve()
⋮----
serializable_items = []
⋮----
spec_json = json.dumps(
⋮----
correlation = "pos-" + uuid.uuid4().hex
⋮----
title = f"Asset Forge batch {correlation}"
run = gh.wait_for_workflow_run(
⋮----
run_id = int(run.get("id") or 0)
⋮----
artifacts = gh.workflow_run_artifacts(repository, run_id)
expected_name = f"asset-forge-batch-{correlation}"
artifact = next(
⋮----
artifact_id = int(artifact.get("id") or 0)
⋮----
zip_bytes = gh.download_workflow_artifact(repository, artifact_id)
⋮----
remote_root = _extract_remote_batch_bundle(
result_path = remote_root / "batch-result.json"
⋮----
result = json.loads(result_path.read_text(encoding="utf-8"))
⋮----
rows = result.get("items")
⋮----
expected_by_id = {
produced: list[dict[str, Any]] = []
produced_by_id: dict[str, dict[str, Any]] = {}
⋮----
item_id = str(row.get("id") or "")
expected = expected_by_id.get(item_id)
⋮----
target_path = str(row.get("target_path") or "")
⋮----
relative = Path(str(row.get("artifact") or ""))
artifact_path = (remote_root / relative).resolve()
⋮----
digest = hashlib.sha256(artifact_path.read_bytes()).hexdigest()
⋮----
dependencies = [str(value) for value in row.get("depends_on") or []]
⋮----
dependency_artifacts = []
⋮----
dependency = produced_by_id.get(dependency_id)
⋮----
visual_references = [
request_id = str(row.get("request_id") or "")
report_path = remote_root / "jobs" / request_id / "production-report.json"
produced_item = {
⋮----
def _hex_hash_similarity(left: str, right: str) -> float | None
⋮----
left = str(left or "").strip().lower()
right = str(right or "").strip().lower()
⋮----
left_value = int(left, 16)
right_value = int(right, 16)
⋮----
bits = len(left) * 4
distance = (left_value ^ right_value).bit_count()
⋮----
def _rgb_distance(left, right) -> float | None
⋮----
def _asset_ancestors(produced: list[dict[str, Any]]) -> dict[str, set[str]]
⋮----
direct = {
memo: dict[str, set[str]] = {}
⋮----
def visit(item_id: str) -> set[str]
⋮----
result = set(direct.get(item_id, set()))
⋮----
def _dedup_summary(produced: list[dict[str, Any]]) -> dict[str, Any]
⋮----
exact = []
near = []
ancestors = _asset_ancestors(produced)
⋮----
left_id = str(left["batch_id"])
right_id = str(right["batch_id"])
⋮----
left_art = left.get("technical_art")
right_art = right.get("technical_art")
left_metrics = (
right_metrics = (
similarity = _hex_hash_similarity(
color_distance = _rgb_distance(
⋮----
root = Path(output_root)
⋮----
ordered_items = _order_asset_batch(items)
⋮----
target_paths = [
⋮----
effective_mode = mode
⋮----
effective_mode = "local" if shutil.which("asset-forge") else "github"
⋮----
produced = _produce_asset_forge_batch_remote(
produced_by_id = {
⋮----
dependency_path = Path(dependency["artifact"])
current_sha256 = hashlib.sha256(dependency_path.read_bytes()).hexdigest()
⋮----
target_path = str(item.get("target_path") or "").strip()
⋮----
source_path = str(item.get("source_path") or "").strip() or None
request_id = str(request.get("requestId") or f"item-{index+1}")
out = root / request_id
request_fingerprint = _request_fingerprint(
cached = _cached_worktree_asset(
⋮----
raster_reference_suffixes = {".png", ".webp", ".jpg", ".jpeg"}
visual_reference_paths = []
⋮----
visual_reference_paths = [
⋮----
receipt = execute_asset_forge(
⋮----
report_path = Path(str(receipt.report_path))
⋮----
artifact = _validated_artifact(report, out)
generation = report.get("generation") if isinstance(report.get("generation"), dict) else {}
validation = report.get("validation") if isinstance(report.get("validation"), dict) else {}
visual_similarity = (
⋮----
delivered_to: list[str] = []
⋮----
root_worktree = Path(target_worktree).resolve()
staged = []
⋮----
normalized = item["target_path"].replace("\\", "/").lstrip("/")
destination = (root_worktree / normalized).resolve()
⋮----
sidecar_destination = (
⋮----
existing = None
⋮----
value = json.loads(sidecar_destination.read_text(encoding="utf-8"))
existing = value if isinstance(value, dict) else None
⋮----
sidecar = _version_sidecar(item, existing=existing)
⋮----
backup_root = Path(tempfile.mkdtemp(prefix="production-os-asset-batch-backup-"))
backups: list[tuple[Path, Path | None]] = []
⋮----
backup = None
⋮----
backup = backup_root / str(len(backups))
⋮----
delivery_mode = "worktree"
⋮----
payload: dict[str, bytes] = {}
⋮----
sidecar_path = _sidecar_relative_path(item["target_path"])
existing = gh.read_json_file(target_repository, sidecar_path)
⋮----
result = gh.commit_files(
delivered_to = [
delivery_mode = "github"
⋮----
inputs = {
```

## File: production_os/asymmetric_attestations.py
```python
ATTESTATION_SCHEMA = "production-os/validation-attestation/v2"
PROVENANCE_SCHEMA = "production-os/release-provenance/v2"
⋮----
class AsymmetricAttestationError(ValueError)
⋮----
payload = {
⋮----
payload = dict(attestation)
signature = dict(payload.pop("signature", {}) or {})
⋮----
validator_id = str(payload.get("validator_id") or "")
⋮----
issued_raw = str(payload.get("issued_at") or "")
⋮----
issued_at = datetime.fromisoformat(
⋮----
now = datetime.now(timezone.utc)
⋮----
registry = TrustedKeyRegistry(trusted_public_keys)
public_key = registry.resolve(
⋮----
expected = {
⋮----
valid = verify_payload(public_key, payload, signature)
⋮----
approval = release["metadata"]["approval"]
expected_key = release_approval_key(
⋮----
payload = dict(provenance)
```

## File: production_os/atomic_io.py
```python
def atomic_write_text(path: str | Path, text: str) -> None
⋮----
destination = Path(path)
⋮----
def atomic_write_json(path: str | Path, payload: Any) -> None
```

## File: production_os/attestations.py
```python
ATTESTATION_SCHEMA = "production-os/validation-attestation/v1"
PROVENANCE_SCHEMA = "production-os/release-provenance/v1"
⋮----
class AttestationError(ValueError)
⋮----
def _canonical(payload: dict[str, Any]) -> bytes
⋮----
def _sign(secret: str, payload: dict[str, Any]) -> str
⋮----
payload = {
⋮----
payload = dict(attestation)
signature = str(payload.pop("signature", ""))
⋮----
validator_id = str(payload.get("validator_id") or "")
secret = trusted_secrets.get(validator_id)
⋮----
issued_raw = str(payload.get("issued_at") or "")
⋮----
issued_at = datetime.fromisoformat(
⋮----
now = datetime.now(timezone.utc)
⋮----
expected_bindings = {
⋮----
expected = _sign(secret, payload)
⋮----
payload = dict(provenance)
```

## File: production_os/audit_checkpoint.py
```python
verification = verify_hash_chain(journal_path)
⋮----
payload = {
canonical = json.dumps(
signature = hmac.new(
output = {**payload, "signature": signature}
⋮----
payload = json.loads(Path(checkpoint_path).read_text(encoding="utf-8"))
signature = str(payload.pop("signature", ""))
⋮----
expected = hmac.new(
```

## File: production_os/audit_integrity.py
```python
def hash_event(previous_hash: str, event: dict) -> str
⋮----
canonical = json.dumps(
⋮----
def verify_hash_chain(path: str | Path) -> dict
⋮----
source = Path(path)
previous = "0" * 64
checked = 0
legacy = 0
chain_started = False
⋮----
row = json.loads(line)
⋮----
is_chained = (
⋮----
chain_started = True
expected_previous = row.get("previous_hash")
stored_hash = row.get("event_hash")
event = row.get("event")
⋮----
calculated = hash_event(previous, event)
⋮----
previous = calculated
```

## File: production_os/backup.py
```python
def _sha256(path: Path) -> str
⋮----
digest = hashlib.sha256()
⋮----
def create_backup(paths: list[str], destination_dir: str) -> dict
⋮----
destination = Path(destination_dir)
⋮----
stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
root = destination / stamp
⋮----
files = []
⋮----
source = Path(raw)
⋮----
target = root / source.name
⋮----
manifest = {
⋮----
def restore_backup(manifest_path: str, *, verify_only: bool = False) -> dict
⋮----
manifest_file = Path(manifest_path)
manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
restored = []
⋮----
backup = Path(item["backup"])
expected = str(item["sha256"])
actual = _sha256(backup)
⋮----
source = Path(item["source"])
```

## File: production_os/budgets.py
```python
@dataclass(frozen=True, slots=True)
class BudgetDecision
⋮----
allowed: bool
reasons: tuple[str, ...]
usage: dict[str, float]
limits: dict[str, float]
⋮----
def to_dict(self) -> dict
⋮----
class BudgetLedger
⋮----
def __init__(self, path: str | Path)
⋮----
def _load_unlocked(self) -> None
⋮----
def load(self) -> None
⋮----
def _save_unlocked(self) -> None
⋮----
usage = dict(self.payload.get("usage", {}).get(repository, {}))
request = request or {}
reasons=[]
⋮----
projected = float(usage.get(key, 0.0)) + float(request.get(key, 0.0))
⋮----
def record(self, repository: str, delta: dict[str, float]) -> dict[str, float]
⋮----
usage = self.payload.setdefault("usage", {}).setdefault(repository, {})
```

## File: production_os/builder_identity.py
```python
class BuilderIdentityError(ValueError)
⋮----
parsed = datetime.fromisoformat(
⋮----
@dataclass(frozen=True)
class BuilderIdentity
⋮----
builder_id: str
key_owner: str
allowed_repositories: tuple[str, ...] = ()
not_before: str | None = None
not_after: str | None = None
⋮----
owner = str(value.get("key_owner") or builder_id)
repositories = tuple(
not_before = value.get("not_before")
not_after = value.get("not_after")
start = _parse_identity_time(not_before, "not_before")
end = _parse_identity_time(not_after, "not_after")
⋮----
def allows_repository(self, repository: str) -> bool
⋮----
class BuilderTrustPolicy
⋮----
identity = self.builders.get(str(builder_id))
⋮----
when = _parse_identity_time(signed_at, "signed_at")
⋮----
start = _parse_identity_time(
⋮----
end = _parse_identity_time(
```

## File: production_os/callgraph.py
```python
@dataclass(frozen=True, slots=True)
class CallEdge
⋮----
source_component: str
target_symbol: str
relation: str
confidence: float
⋮----
def to_dict(self) -> dict
⋮----
def build_call_import_graph(assessment: RepoAssessment) -> dict
⋮----
edges: list[CallEdge] = []
components_by_path: dict[str, list] = {}
⋮----
lower = path.lower()
⋮----
tree = ast.parse(text)
⋮----
calls = {
attrs = {
⋮----
cid = f"{component.path}:{component.name}"
⋮----
call_names = set(
keywords = {
```

## File: production_os/capabilities.py
```python
@dataclass(frozen=True, slots=True)
class Capability
⋮----
name: str
confidence: float
evidence: tuple[str, ...]
portable: bool = True
⋮----
def to_dict(self) -> dict
⋮----
def _contains(text: str, *terms: str) -> bool
⋮----
def extract_capabilities(e: RepoEvidence) -> list[Capability]
⋮----
text = e.readme_text.lower()
files = {name.lower() for name in e.detected_files}
workflows = {name.lower() for name in e.workflow_names}
caps: dict[str, Capability] = {}
⋮----
def add(name: str, confidence: float, evidence: list[str], portable: bool = True) -> None
⋮----
current = caps.get(name)
candidate = Capability(name, round(confidence, 2), tuple(evidence), portable)
```

## File: production_os/change_impact.py
```python
@dataclass(frozen=True, slots=True)
class ImpactDecision
⋮----
task_id: str
affected: bool
reason: str
⋮----
def to_dict(self) -> dict
⋮----
def _normalize_path(path: str) -> str
⋮----
normalized = path.replace("\\", "/")
⋮----
normalized = normalized[2:]
⋮----
def _matches(path: str, patterns: list[str]) -> bool
⋮----
normalized = _normalize_path(path)
⋮----
matches: list[str] = []
⋮----
path = _normalize_path(raw_path)
⋮----
"""Fail-safe impact analysis with explicit opt-in skipping.

    Empty or unknown change sets execute by default. A task may explicitly
    opt into empty-change skipping with allow_empty_changes.
    """
normalized_changes = [
⋮----
by_id = {
children: dict[str, set[str]] = {
⋮----
affected: set[str] = set()
reasons: dict[str, str] = {}
⋮----
payload = dict(task.get("payload") or {})
impact = dict(payload.get("impact") or {})
⋮----
skip_when_unaffected = bool(
patterns = [
exclude_patterns = [
⋮----
matches = _direct_match(
⋮----
# Any directly affected task makes all downstream work affected.
queue = list(affected)
⋮----
task_id = queue.pop(0)
⋮----
decisions = []
```

## File: production_os/claims.py
```python
@dataclass(slots=True)
class ClaimRecord
⋮----
key: str
worker_id: str
repository: str
task: str
status: str
claimed_at: str
ack_deadline: str
completed_at: str | None = None
⋮----
def to_dict(self) -> dict
⋮----
class ClaimStore
⋮----
SCHEMA_VERSION = "production-os/claims/v2"
⋮----
def __init__(self, path: str | Path)
⋮----
def _load_unlocked(self) -> None
⋮----
payload = json.loads(self.path.read_text(encoding="utf-8"))
⋮----
claim = ClaimRecord(**row)
⋮----
def load(self) -> None
⋮----
def _save_unlocked(self) -> None
⋮----
def save(self) -> None
⋮----
existing = self.claims.get(key)
⋮----
now = datetime.now(timezone.utc)
record = ClaimRecord(
⋮----
def ack(self, key: str, worker_id: str) -> ClaimRecord
⋮----
record = self.claims[key]
⋮----
def complete(self, key: str, worker_id: str) -> ClaimRecord
⋮----
def expired_unacked(self) -> list[ClaimRecord]
⋮----
result = []
⋮----
deadline = datetime.fromisoformat(
```

## File: production_os/classification.py
```python
@dataclass(frozen=True, slots=True)
class ProjectProfile
⋮----
kind: str
confidence: float
signals: tuple[str, ...]
⋮----
def classify_repository(e: RepoEvidence) -> ProjectProfile
⋮----
names = {name.lower() for name in e.detected_files}
text = e.readme_text.lower()
signals: list[str] = []
```

## File: production_os/cli.py
```python
def _parse_args(argv: list[str] | None = None) -> argparse.Namespace
⋮----
parser = argparse.ArgumentParser(prog="production-os")
sub = parser.add_subparsers(dest="command", required=True)
⋮----
scan = sub.add_parser("scan", help="Scan and prioritize a GitHub portfolio")
⋮----
validation = sub.add_parser(
⋮----
feedback = sub.add_parser("execution-feedback", help="Decide promote/retry/rollback/replan from before/after snapshots and validation")
⋮----
trends = sub.add_parser("trends", help="Build long-term repository score trends from snapshot JSON files")
⋮----
heartbeat = sub.add_parser("heartbeat", help="Renew an execution lease")
⋮----
reconcile = sub.add_parser("reconcile", help="Recover expired leases and cooled-down circuits")
⋮----
dispatch = sub.add_parser("dispatch", help="Dispatch a handoff to the ai-dev-server file queue")
⋮----
assetforge = sub.add_parser(
⋮----
assetforgebatch = sub.add_parser(
⋮----
ghrec = sub.add_parser("github-reconcile", help="Reconcile runtime tasks from explicit GitHub issue/PR mappings")
⋮----
controller = sub.add_parser("controller", help="Run bounded autonomous control cycles")
⋮----
healthserver = sub.add_parser("health-server", help="Serve the health JSON over HTTP")
⋮----
workerreg = sub.add_parser("worker-register", help="Register or update a worker")
⋮----
workerhb = sub.add_parser("worker-heartbeat", help="Heartbeat a worker and update its active task count")
⋮----
workerlist = sub.add_parser("worker-list", help="List worker registry state")
⋮----
jobclaim = sub.add_parser("job-claim", help="Claim a dispatched job")
⋮----
joback = sub.add_parser("job-ack", help="Acknowledge a claimed job")
⋮----
jobcomplete = sub.add_parser("job-complete", help="Mark a job complete and release worker/runtime accounting")
⋮----
deliveryrecover = sub.add_parser("delivery-recover", help="Recover expired unacked deliveries")
⋮----
preempt = sub.add_parser("preempt-request", help="Request cooperative preemption of an interruptible running task")
⋮----
checkpoint = sub.add_parser("preempt-checkpoint", help="Confirm checkpoint and release a preempted task slot")
⋮----
estop = sub.add_parser("emergency-stop", help="Activate global emergency stop")
⋮----
eresume = sub.add_parser("emergency-resume", help="Clear global emergency stop")
⋮----
auditverify = sub.add_parser("audit-verify", help="Verify execution journal hash chain")
⋮----
backup = sub.add_parser("backup", help="Backup critical state files")
⋮----
restore = sub.add_parser("restore", help="Restore or verify a backup manifest")
⋮----
restoreactivate = sub.add_parser(
⋮----
approve = sub.add_parser("approve", help="Approve a gated task key")
⋮----
revoke = sub.add_parser("revoke", help="Revoke a gated task key")
⋮----
migrate = sub.add_parser("migrate-state", help="Migrate a persistent state file to the current schema")
⋮----
migratebatch = sub.add_parser("migrate-many", help="Migrate multiple persistent state files")
⋮----
qcompact = sub.add_parser("queue-compact", help="Remove/archive completed queue entries")
⋮----
dlretry = sub.add_parser("dead-letter-retry", help="Requeue dead-letter jobs within retry budget")
⋮----
acreate = sub.add_parser("audit-checkpoint-create", help="Create signed HMAC audit checkpoint")
⋮----
averify = sub.add_parser("audit-checkpoint-verify", help="Verify signed HMAC audit checkpoint")
⋮----
quarantine = sub.add_parser("quarantine", help="Manually quarantine a repository")
⋮----
unquarantine = sub.add_parser("unquarantine", help="Release a repository from quarantine")
⋮----
budgetrecord = sub.add_parser("budget-record", help="Record portfolio budget usage")
⋮----
policyvalidate = sub.add_parser("policy-validate", help="Validate policy-as-code JSON")
⋮----
policycheck = sub.add_parser("policy-check", help="Evaluate one handoff against policy-as-code")
⋮----
dbinit = sub.add_parser("db-init", help="Initialize the P8 SQLite backend")
⋮----
dbimport = sub.add_parser("db-import", help="Import legacy JSON state into SQLite")
⋮----
tokenhash = sub.add_parser("token-hash", help="Hash an API bearer token for auth config")
⋮----
controlplane = sub.add_parser("control-plane", help="Run authenticated distributed control-plane API")
⋮----
remotepoll = sub.add_parser("remote-worker-poll", help="Poll the P8 control plane for remote jobs")
⋮----
remoterun = sub.add_parser(
⋮----
workflowcreate = sub.add_parser("workflow-create", help="Create a persistent DAG workflow")
⋮----
workflowstatus = sub.add_parser("workflow-status", help="Inspect a persistent workflow")
⋮----
workflowdispatch = sub.add_parser("workflow-dispatch", help="Dispatch ready workflow tasks")
⋮----
workflowcritical = sub.add_parser("workflow-critical-path", help="Calculate workflow critical path")
⋮----
workfloweta = sub.add_parser("workflow-eta", help="Predict remaining workflow duration")
⋮----
stragglers = sub.add_parser("stragglers", help="Detect slow running jobs")
⋮----
speculate = sub.add_parser(
⋮----
workflowimpact = sub.add_parser(
⋮----
workflowimpactpr = sub.add_parser(
⋮----
prrefresh = sub.add_parser(
⋮----
workflowcancel = sub.add_parser("workflow-cancel", help="Cancel a workflow")
⋮----
artifactadd = sub.add_parser("artifact-add", help="Register a workflow artifact")
⋮----
releasepromote = sub.add_parser(
⋮----
keygen = sub.add_parser(
⋮----
validationattestv2 = sub.add_parser(
⋮----
checkpoint = sub.add_parser(
⋮----
checkpointverify = sub.add_parser(
⋮----
slsaverify = sub.add_parser(
⋮----
provenanceverifyv2 = sub.add_parser(
⋮----
validationattest = sub.add_parser(
⋮----
incidentsnapshot = sub.add_parser(
⋮----
incidentreport = sub.add_parser(
⋮----
truststatus = sub.add_parser(
⋮----
releaseverify = sub.add_parser(
⋮----
releaserollback = sub.add_parser(
⋮----
def _rank_actions(assessments: Iterable[RepoAssessment]) -> list[ActionCandidate]
⋮----
actions = [action for assessment in assessments for action in assessment.actions]
⋮----
def _external_refs_for_action(action: ActionCandidate, catalog: dict | None) -> list[dict]
⋮----
mapping = {
capability = mapping.get(action.task)
⋮----
def _handoff(action: ActionCandidate, reuse: list, catalog: dict | None) -> dict
⋮----
related_reuse = [
⋮----
reusable_components = []
adaptation_plans = []
⋮----
recommended = [
⋮----
executable_plans = [
⋮----
def _print_human(assessments, actions, regressions, reuse, catalog_loaded: bool) -> None
⋮----
e = assessment.evidence
⋮----
plan = item.adaptation_plan or {}
⋮----
top = actions[0]
⋮----
def run_scan(args: argparse.Namespace) -> int
⋮----
client = GitHubClient()
⋮----
repos = client.list_repositories(args.owner)
⋮----
catalog = None
⋮----
catalog = client.read_json_file(args.star_list_repo, args.star_list_path)
⋮----
include = set(args.include or [])
exclude = set(args.exclude or [])
selected = []
⋮----
assessments: list[RepoAssessment] = []
⋮----
evidence = client.collect_evidence(repo)
⋮----
actions = _rank_actions(assessments)
reuse = detect_reuse(assessments)
graph = build_knowledge_graph(assessments)
snapshot = build_snapshot(args.owner, assessments)
previous = load_snapshot(args.compare) if args.compare else None
regressions = detect_regressions(previous, snapshot)
⋮----
learning_signals = []
⋮----
events_payload = json.loads(Path(args.learning_events).read_text(encoding="utf-8"))
events = events_payload.get("events", events_payload)
⋮----
learning_signals = build_learning_signals(events)
⋮----
runtime_state = RuntimeState(args.runtime_state) if args.runtime_state else None
schedule = build_schedule(
payload = {
⋮----
payload = _handoff(actions[0], reuse, catalog) if actions else {
⋮----
def run_validation_results(args: argparse.Namespace) -> int
⋮----
plan_payload = json.loads(Path(args.plan).read_text(encoding="utf-8"))
results_payload = json.loads(Path(args.results).read_text(encoding="utf-8"))
⋮----
validation_plan = plan_payload.get("validation_plan", plan_payload)
⋮----
validation_plan = validation_plan.get("steps", [])
results = results_payload.get("results", results_payload)
⋮----
summary = summarize_validation_results(validation_plan, results)
⋮----
rendered = json.dumps(payload, indent=2, ensure_ascii=False)
⋮----
destination = Path(args.output)
⋮----
def run_execution_feedback(args: argparse.Namespace) -> int
⋮----
before = json.loads(Path(args.before).read_text(encoding="utf-8"))
after = json.loads(Path(args.after).read_text(encoding="utf-8"))
validation_payload = json.loads(Path(args.validation_summary).read_text(encoding="utf-8"))
⋮----
before_score = int(before.get("repositories", {}).get(args.repository, {}).get("score", 0))
after_score = int(after.get("repositories", {}).get(args.repository, {}).get("score", 0))
summary = validation_payload.get("summary", validation_payload)
⋮----
decision = decide_execution_outcome(before_score, after_score, summary)
⋮----
state = RuntimeState(args.runtime_state)
record = state.record_outcome(args.repository, args.task, decision.decision)
⋮----
journal = ExecutionJournal(args.journal)
⋮----
def run_trends(args: argparse.Namespace) -> int
⋮----
snapshots = [
⋮----
def run_heartbeat(args: argparse.Namespace) -> int
⋮----
record = state.heartbeat_lease(
⋮----
def run_reconcile(args: argparse.Namespace) -> int
⋮----
actions = reconcile_runtime_state(state)
⋮----
def run_dispatch(args: argparse.Namespace) -> int
⋮----
handoff = json.loads(Path(args.handoff).read_text(encoding="utf-8"))
⋮----
backend = open_backend(args.database)
queue = job_queue_for(backend)
⋮----
job = queue.enqueue(payload)
backend_name = (
⋮----
worker_registry = (
rate_limit_store = (
approval_store = (
policy_set = PolicySet.load(args.policy)
budget_ledger = (
quarantine_store = (
⋮----
result = dispatch_handoff(
⋮----
def _write_asset_result(path_value: str | None, payload: dict) -> None
⋮----
path = Path(path_value)
⋮----
def _asset_failure_result(exc: Exception) -> dict
⋮----
message = str(exc)
quality_failed = "visual consistency score" in message.lower()
⋮----
def run_asset_forge_dispatch(args: argparse.Namespace) -> int
⋮----
request = build_asset_forge_request(
⋮----
receipt = execute_asset_forge(
⋮----
failure = _asset_failure_result(exc)
⋮----
result = {
⋮----
report_path = Path(receipt.report_path)
⋮----
report = json.loads(report_path.read_text(encoding="utf-8"))
⋮----
report = {}
generation = report.get("generation") if isinstance(report, dict) else None
visual = generation.get("visualSimilarity") if isinstance(generation, dict) else None
⋮----
attempts = visual.get("attempts") if isinstance(visual.get("attempts"), list) else []
⋮----
def run_asset_forge_batch(args: argparse.Namespace) -> int
⋮----
payload = json.loads(Path(args.spec).read_text(encoding="utf-8"))
items = payload.get("items", payload) if isinstance(payload, dict) else payload
⋮----
result = execute_asset_forge_batch(
⋮----
def run_github_reconcile(args: argparse.Namespace) -> int
⋮----
payload = json.loads(Path(args.mapping).read_text(encoding="utf-8"))
mappings = payload.get("mappings", payload)
⋮----
journal = ExecutionJournal(args.journal) if args.journal else None
results = []
⋮----
repository = str(item.get("repository", ""))
task = str(item.get("task", ""))
⋮----
work_state = fetch_github_work_state(
decision = runtime_decision_from_github(work_state)
⋮----
updated = None
⋮----
updated = state.record_outcome(repository, task, decision).to_dict()
⋮----
row = {
⋮----
def run_controller_command(args: argparse.Namespace) -> int
⋮----
results = run_controller(
⋮----
def run_worker_register(args: argparse.Namespace) -> int
⋮----
registry = WorkerRegistry(args.registry)
worker = registry.register(
⋮----
def run_worker_heartbeat(args: argparse.Namespace) -> int
⋮----
worker = registry.heartbeat(args.worker_id, active_tasks=args.active_tasks)
⋮----
def run_worker_list(args: argparse.Namespace) -> int
⋮----
dead = registry.detect_dead(args.dead_timeout_seconds)
⋮----
def run_job_claim(args: argparse.Namespace) -> int
⋮----
payload = json.loads(Path(args.queue_file).read_text(encoding="utf-8"))
handoff = payload.get("handoff", {})
key = str(payload.get("idempotency_key", ""))
repository = str(handoff.get("repository", ""))
task = str(handoff.get("task", ""))
assigned_worker = payload.get("worker_id")
⋮----
store = ClaimStore(args.claims)
claim = store.claim(
⋮----
def run_job_ack(args: argparse.Namespace) -> int
⋮----
claim = store.ack(args.key, args.worker_id)
⋮----
def run_job_complete(args: argparse.Namespace) -> int
⋮----
claim = store.complete(args.key, args.worker_id)
⋮----
worker = registry.workers.get(args.worker_id)
⋮----
worker = registry.adjust_active_tasks(args.worker_id, -1)
⋮----
record = state.get(claim.repository, claim.task)
⋮----
def run_delivery_recover(args: argparse.Namespace) -> int
⋮----
claims = ClaimStore(args.claims)
⋮----
rows = recover_unacked_jobs(
⋮----
def run_preempt_request(args: argparse.Namespace) -> int
⋮----
record = request_preemption(state, args.repository, args.task)
⋮----
def run_preempt_checkpoint(args: argparse.Namespace) -> int
⋮----
record = confirm_checkpoint_and_release(
⋮----
def run_emergency_stop(args: argparse.Namespace) -> int
⋮----
payload = set_emergency_stop(args.state, reason=args.reason)
⋮----
def run_emergency_resume(args: argparse.Namespace) -> int
⋮----
payload = clear_emergency_stop(args.state)
⋮----
def run_audit_verify(args: argparse.Namespace) -> int
⋮----
payload = verify_hash_chain(args.journal)
⋮----
def run_backup(args: argparse.Namespace) -> int
⋮----
payload = create_backup(args.paths, args.destination_dir)
⋮----
def run_restore(args: argparse.Namespace) -> int
⋮----
payload = restore_backup(args.manifest, verify_only=args.verify_only)
⋮----
def run_restore_activate(args: argparse.Namespace) -> int
⋮----
payload = activate_staged_sqlite_restore(
⋮----
def run_approve(args: argparse.Namespace) -> int
⋮----
store = ApprovalStore(args.store)
item = store.set(
⋮----
def run_revoke(args: argparse.Namespace) -> int
⋮----
def run_migrate_state(args: argparse.Namespace) -> int
⋮----
payload = migrate_state_file(args.path)
⋮----
def run_migrate_many(args: argparse.Namespace) -> int
⋮----
def run_queue_compact(args: argparse.Namespace) -> int
⋮----
rows = compact_queue(
⋮----
def run_dead_letter_retry(args: argparse.Namespace) -> int
⋮----
rows = retry_dead_letters(
⋮----
def run_audit_checkpoint_create(args: argparse.Namespace) -> int
⋮----
payload = create_audit_checkpoint(
⋮----
def run_audit_checkpoint_verify(args: argparse.Namespace) -> int
⋮----
payload = verify_audit_checkpoint(
⋮----
def run_quarantine(args: argparse.Namespace) -> int
⋮----
store = QuarantineStore(args.store)
item = store.set(args.repository, active=True, reason=args.reason)
⋮----
def run_unquarantine(args: argparse.Namespace) -> int
⋮----
item = store.set(args.repository, active=False, reason=args.reason or "manual release")
⋮----
def run_budget_record(args: argparse.Namespace) -> int
⋮----
ledger = BudgetLedger(args.ledger)
usage = ledger.record(
⋮----
def run_policy_validate(args: argparse.Namespace) -> int
⋮----
payload = json.loads(Path(args.policy).read_text(encoding="utf-8"))
result = validate_policy_payload(payload)
⋮----
def run_policy_check(args: argparse.Namespace) -> int
⋮----
decision = evaluate_policy(policy_set, handoff)
⋮----
def run_db_init(args: argparse.Namespace) -> int
⋮----
def run_db_import(args: argparse.Namespace) -> int
⋮----
payload = import_json_state(
⋮----
def run_token_hash(args: argparse.Namespace) -> int
⋮----
def _trusted_validation_keys_from_env(name: str) -> dict
⋮----
raw = os.getenv(name, "").strip()
⋮----
payload = json.loads(raw)
⋮----
def run_control_plane(args: argparse.Namespace) -> int
⋮----
def run_remote_worker_poll(args: argparse.Namespace) -> int
⋮----
client = RemoteWorkerClient(
jobs = client.poll(
⋮----
def run_remote_worker_run(args: argparse.Namespace) -> int
⋮----
token = str(os.getenv(args.token_env) or "").strip()
⋮----
command = shlex.split(str(args.executor_command))
⋮----
runner = RemoteWorkerRunner(
outcomes = runner.run(
⋮----
def _workflow_engine(database: str) -> WorkflowEngine
⋮----
backend = open_backend(database)
⋮----
def run_workflow_create(args: argparse.Namespace) -> int
⋮----
engine = _workflow_engine(args.database)
workflow = engine.create(
⋮----
def run_workflow_status(args: argparse.Namespace) -> int
⋮----
workflow = _workflow_engine(args.database).get(args.workflow_id)
⋮----
def run_workflow_dispatch(args: argparse.Namespace) -> int
⋮----
jobs = engine.dispatch_ready(args.workflow_id, limit=args.limit)
⋮----
def run_workflow_critical_path(args: argparse.Namespace) -> int
⋮----
payload = _workflow_engine(args.database).critical_path(
⋮----
def run_workflow_eta(args: argparse.Namespace) -> int
⋮----
workflow = engine.get(args.workflow_id)
optimizer = ExecutionOptimizer(engine.backend)
⋮----
def run_stragglers(args: argparse.Namespace) -> int
⋮----
optimizer = ExecutionOptimizer(backend)
workers = worker_registry_for(backend)
⋮----
payload = optimizer.stragglers(
⋮----
def run_speculate_stragglers(args: argparse.Namespace) -> int
⋮----
manager = SpeculationManager(backend, queue)
⋮----
rows = optimizer.stragglers(
spawned = []
skipped = []
⋮----
alternate = item.get("alternate_worker")
⋮----
job = manager.spawn(
⋮----
def run_workflow_impact(args: argparse.Namespace) -> int
⋮----
decisions = engine.apply_change_impact(
⋮----
def run_workflow_impact_pr(args: argparse.Namespace) -> int
⋮----
changed_paths = client.list_pull_request_files(
⋮----
def run_pr_refresh(args: argparse.Namespace) -> int
⋮----
workflows = engine.find_by_github_pr(
⋮----
changed_paths = GitHubClient().list_pull_request_files(
refreshed = []
⋮----
def run_workflow_cancel(args: argparse.Namespace) -> int
⋮----
workflow = _workflow_engine(args.database).cancel(args.workflow_id)
⋮----
def run_artifact_add(args: argparse.Namespace) -> int
⋮----
artifact = _workflow_engine(args.database).add_artifact(
⋮----
engine = _workflow_engine(database)
⋮----
def run_signing_keygen(args: argparse.Namespace) -> int
⋮----
def run_validation_attest_v2(args: argparse.Namespace) -> int
⋮----
engine=_workflow_engine(args.database)
workflow=engine.get(args.workflow_id)
artifact=next(
⋮----
validation=json.loads(
metadata=dict(artifact.get("metadata") or {})
attestation=create_validation_attestation_v2(
rendered=json.dumps(attestation,indent=2,ensure_ascii=False)
⋮----
ledger=_release_ledger(args.database)
chain=ledger.verify_transparency()
⋮----
checkpoint=create_checkpoint(
private_key_pem=(
witness_signer=(
⋮----
envelope=sign_checkpoint_with_signer(
result={"envelope":envelope}
⋮----
token=(
⋮----
rekor_url=getattr(args,"rekor_url",None)
receipt_output=getattr(args,"receipt_output",None)
rekor_witness_config=getattr(args,"rekor_witness_config",None)
⋮----
rekor_private_key=getattr(args,"rekor_private_key",None)
rekor_log_public_key=getattr(
⋮----
publisher=RekorV1Publisher.from_private_key(
receipt=publisher.publish(envelope)
⋮----
proof=receipt.get("inclusion_proof")
⋮----
identity=parse_checkpoint_identity(
quorum=collect_rekor_witness_quorum(
⋮----
checkpoint_state=RekorCheckpointMonitor(
⋮----
rendered=json.dumps(result,indent=2,ensure_ascii=False)
⋮----
envelope=json.loads(
checkpoint_valid=verify_checkpoint(
receipt_path=getattr(args,"receipt",None)
receipt_valid=None
⋮----
log_key_path=getattr(
⋮----
receipt=json.loads(
receipt_valid=verify_rekor_v1_receipt(
valid=bool(checkpoint_valid) and receipt_valid is not False
result={
⋮----
def run_slsa_verify(args: argparse.Namespace) -> int
⋮----
valid=verify_signed_slsa_statement(
⋮----
def run_provenance_verify_v2(args: argparse.Namespace) -> int
⋮----
provenance=json.loads(
valid=verify_release_provenance_v2(
⋮----
def run_validation_attest(args: argparse.Namespace) -> int
⋮----
secret = os.getenv(args.secret_env, "")
⋮----
artifact = next(
⋮----
validation = json.loads(
metadata = dict(artifact.get("metadata") or {})
attestation = create_validation_attestation(
rendered = json.dumps(
⋮----
def run_incident_snapshot(args: argparse.Namespace) -> int
⋮----
result = _release_ledger(args.database).record_incident_report(
⋮----
def run_incident_report(args: argparse.Namespace) -> int
⋮----
report = _release_ledger(args.database).incident_report(
⋮----
def run_trust_status(args: argparse.Namespace) -> int
⋮----
result = _release_ledger(args.database).trust_status(
⋮----
def run_release_verify(args: argparse.Namespace) -> int
⋮----
result = _release_ledger(
⋮----
def run_release_promote(args: argparse.Namespace) -> int
⋮----
metadata = (
attestation = json.loads(
release = _release_ledger(args.database).promote(
⋮----
def run_release_rollback(args: argparse.Namespace) -> int
⋮----
release = _release_ledger(args.database).rollback(
⋮----
def run_health_server(args: argparse.Namespace) -> int
⋮----
def main(argv: list[str] | None = None) -> int
⋮----
args = _parse_args(argv)
```

## File: production_os/compatibility.py
```python
@dataclass(frozen=True, slots=True)
class DependencyCompatibility
⋮----
dependency: str
status: str
confidence: float
evidence: tuple[str, ...]
⋮----
def to_dict(self) -> dict
⋮----
def _target_tokens(target: RepoAssessment) -> set[str]
⋮----
tokens: set[str] = set()
⋮----
ALIASES: dict[str, tuple[str, ...]] = {
⋮----
tokens = _target_tokens(target)
source_text = "\n".join(
results: list[DependencyCompatibility] = []
⋮----
dep = str(dependency).strip()
⋮----
key = dep.lower()
aliases = ALIASES.get(key, (key,))
matched = [
```

## File: production_os/components.py
```python
@dataclass(frozen=True, slots=True)
class Component
⋮----
name: str
kind: str
path: str
language: str
confidence: float
dependencies: tuple[str, ...] = ()
capability_hints: tuple[str, ...] = ()
test_like: bool = False
⋮----
def to_dict(self) -> dict
⋮----
CAPABILITY_PATTERNS: tuple[tuple[str, tuple[str, ...]], ...] = (
⋮----
def _capability_hints(text: str) -> tuple[str, ...]
⋮----
lower = text.lower()
result = []
⋮----
def _python_components(path: str, text: str) -> list[Component]
⋮----
tree = ast.parse(text)
⋮----
imports: set[str] = set()
⋮----
result: list[Component] = []
⋮----
segment = ast.get_source_segment(text, node) or node.name
⋮----
def _jvm_components(path: str, text: str) -> list[Component]
⋮----
language = "kotlin" if path.lower().endswith((".kt", ".kts")) else "java"
imports = tuple(sorted(set(
pattern = re.compile(
⋮----
kind = match.group(1).replace(" ", "-")
name = match.group(2)
window = text[match.start(): match.start() + 6000]
⋮----
def extract_components(e: RepoEvidence, limit: int = 250) -> list[Component]
⋮----
seen: set[tuple[str, str, str]] = set()
⋮----
lower = path.lower()
⋮----
components = _python_components(path, text)
⋮----
components = _jvm_components(path, text)
⋮----
key = (component.path, component.kind, component.name)
```

## File: production_os/control_plane.py
```python
class ControlPlane
⋮----
github_token = str(os.getenv("GITHUB_TOKEN") or "").strip()
actions_repository = str(
actions_workflow = str(
actions_ref = str(
⋮----
@staticmethod
    def _parse_timestamp(value)
⋮----
parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
⋮----
def recover_abandoned_acked_jobs(self) -> list[dict]
⋮----
now = datetime.now(timezone.utc)
⋮----
cursor = db.cursor()
⋮----
rows = cursor.fetchall()
⋮----
rows = db.execute(
⋮----
recovered = []
⋮----
job = dict(raw)
worker_id = str(job.get("claimed_by") or "")
worker = self.workers.workers.get(worker_id)
⋮----
execution = self.dashboard_store.latest_execution(job["key"])
⋮----
last_activity = self._parse_timestamp(
⋮----
timestamp = now.isoformat()
⋮----
updated = cursor.rowcount
⋮----
cursor = db.execute(
⋮----
action = {
⋮----
active = {str(key) for key in active_job_keys if str(key)}
⋮----
now = datetime.now(timezone.utc).isoformat()
⋮----
key = str(job["key"])
⋮----
previous_status = str(job["status"])
target = (
⋮----
execution = self.dashboard_store.latest_execution(key)
⋮----
def _json_bytes(payload: dict | list) -> bytes
⋮----
class RequestBodyTooLarge(ValueError)
⋮----
def make_handler(control: ControlPlane)
⋮----
class Handler(BaseHTTPRequestHandler)
⋮----
server_version = "ProductionOS"
⋮----
def version_string(self) -> str
⋮----
def log_message(self, format: str, *args) -> None
⋮----
def _send_html(self, status: int, html: str) -> None
⋮----
body = html.encode("utf-8")
⋮----
body = _json_bytes(payload)
⋮----
def _method_not_allowed(self) -> None
⋮----
def do_PUT(self) -> None
⋮----
def do_PATCH(self) -> None
⋮----
def do_DELETE(self) -> None
⋮----
def _read_body(self) -> bytes
⋮----
raw_length = self.headers.get("Content-Length", "0")
⋮----
length = int(raw_length)
⋮----
max_body = 1024 * 1024
⋮----
body = self.rfile.read(length)
⋮----
def _read_json(self) -> dict
⋮----
raw = self._read_body()
⋮----
payload = json.loads(raw.decode("utf-8"))
⋮----
def _principal(self) -> Principal | None
⋮----
header = self.headers.get("Authorization", "")
prefix = "Bearer "
token = header[len(prefix):] if header.startswith(prefix) else None
⋮----
def _require(self, role: str) -> Principal | None
⋮----
principal = self._principal()
⋮----
def do_GET(self) -> None
⋮----
parsed = urlparse(self.path)
⋮----
principal = self._require("viewer")
⋮----
query = parse_qs(parsed.query)
⋮----
window = query.get("window", ["7d"])[0]
parts = [part for part in parsed.path.split("/") if part]
service = control.dashboard
⋮----
payload = service.overview(window)
⋮----
payload = service.launch_readiness(
⋮----
payload = service.production_status(
⋮----
payload = service.production_inbox(
⋮----
payload = service.attention(
⋮----
payload = service.health()
⋮----
payload = service.autopilot_queue(
⋮----
payload = service.workers()
⋮----
worker_id = parts[3] if len(parts) >= 4 else ""
⋮----
payload = service.worker_detail(worker_id)
⋮----
payload = service.worker_logs(worker_id, query.get("after",[None])[0], query.get("limit",["100"])[0])
⋮----
payload = service.worker_usage(worker_id, window)
⋮----
payload = service.maintenance()
⋮----
payload = service.backups()
⋮----
payload = service.repositories()
⋮----
payload = service.projects()
⋮----
repository = parts[3] + "/" + parts[4]
⋮----
payload = service.project_detail(repository)
⋮----
payload = service.project_progress(repository)
⋮----
payload = service.project_commits(repository, window)
⋮----
payload = service.project_usage(repository, window)
⋮----
payload = service.project_workflows(repository)
⋮----
payload = service.project_history(repository)
⋮----
payload = service.control_audit(
⋮----
payload = service.remediation_history(
⋮----
payload = service.remediation_analytics(
⋮----
payload = service.incidents(
⋮----
payload = service.activity(
⋮----
workers = db.execute(
workflow_rows = db.execute(
⋮----
after = int(query.get("after", ["0"])[0])
limit = int(query.get("limit", ["100"])[0])
⋮----
key = parsed.path.split("/", 3)[-1]
⋮----
job = control.queue.get(key)
⋮----
workflow_id = parts[2]
⋮----
payload = control.workflows.critical_path(workflow_id)
⋮----
workflow = control.workflows.get(workflow_id)
payload = control.optimizer.workflow_eta(workflow)
⋮----
payload = control.workflows.get(workflow_id)
⋮----
incident_id = (
⋮----
report = control.releases.incident_report(
⋮----
result = control.releases.trust_status(
⋮----
parts = [
⋮----
verification = control.releases.verify(
⋮----
release = control.releases.get(parts[2])
⋮----
project = control.managed_projects.get(parts[2])
⋮----
def do_POST(self) -> None
⋮----
principal = self._require("operator")
⋮----
body = self._read_json()
request_id = str(body.get("request_id") or "").strip()
project_id = None
⋮----
actor = f"{principal.role}:{principal.name}"
project_id = hashlib.sha256(
project = control.managed_projects.create(
⋮----
action = parts[3]
⋮----
project = control.managed_projects.add_instruction(
⋮----
project = (
⋮----
project = control.managed_projects.mark_done(
⋮----
result = control.dashboard.cancel_production(
⋮----
delivery_id = self.headers.get(
event_name = self.headers.get(
⋮----
payload = parse_github_webhook(raw)
target = pull_request_event_target(
⋮----
repository = target[0] if target else None
⋮----
claimed = control.webhook_deliveries.claim(
⋮----
generation = (
workflows = [generation] if generation else []
refreshable = [
changed_paths = (
refreshed = []
dispatched = []
⋮----
decisions = control.workflows.apply_change_impact(
jobs = control.workflows.dispatch_ready(
⋮----
backup_id = parts[3]
requested_by = f"{principal.role}:{principal.name}"
audit = control.dashboard_store.append_control_audit(
⋮----
result = control.dashboard.stage_backup_restore(
⋮----
result = (
⋮----
expected_count = body.get("expected_candidate_count")
expected_fingerprint = str(
⋮----
result = control.dashboard.prune_expired_backups(
⋮----
expected = body.get("expected_candidate_count")
⋮----
result = control.dashboard.prune_backup_temps(
⋮----
result = control.dashboard.create_verified_backup()
⋮----
expected = body.get("expected_candidate_rows")
⋮----
result = control.dashboard.prune_maintenance(expected)
⋮----
incident_id = parts[3]
⋮----
incident = control.dashboard_store.acknowledge_dashboard_incident(
⋮----
action = str(body.get("action") or "").strip()
state_by_action = {
worker_id = parts[3]
⋮----
audit_job_key = (
⋮----
remediation_event = None
⋮----
incident_rows = control.dashboard.incidents(
incident = next(
⋮----
matched = next(
⋮----
remediation_event = (
audit_event = control.dashboard_store.append_control_audit(
⋮----
# The pre-action reservation remains durable even
# if result finalization cannot be written.
⋮----
# Keep the requested remediation event durable
# even if final outcome persistence fails.
⋮----
job_key = str(body.get("job_key") or "").strip()
⋮----
job = control.queue.get(job_key)
⋮----
recovered = control.queue.recover_job(
⋮----
kicked = control.dashboard_control.kick_worker(worker_id)
status = (
⋮----
retried = control.dashboard_control.retry_job(
⋮----
state = control.dashboard_control.request_job_cancel(
⋮----
desired_state = state_by_action.get(action)
⋮----
state = control.dashboard_control.set_worker_state(
⋮----
stragglers = control.optimizer.stragglers(
spawned = []
skipped = []
⋮----
alternate = item.get("alternate_worker")
⋮----
job = control.speculation.spawn(
⋮----
repository = str(body["repository"])
pr_number = int(body["pr_number"])
workflows = control.workflows.find_by_github_pr(
⋮----
changed_paths = GitHubClient().list_pull_request_files(
⋮----
tasks = [
workflow = control.workflows.create(
⋮----
workflow = control.workflows.cancel(workflow_id)
⋮----
release = control.releases.promote(
⋮----
artifact = control.workflows.add_artifact(
⋮----
principal = self._require("worker")
⋮----
worker_id = str(body["worker_id"]).strip()
⋮----
raw_capabilities = body.get("capabilities", [])
⋮----
raw_active = body.get("active_job_keys", [])
⋮----
active_job_keys = sorted({
worker = control.workers.register(
recovered = control.reconcile_worker_registration(
worker = control.workers.heartbeat(
⋮----
worker_id = str(body["worker_id"])
⋮----
reconciliation = None
⋮----
raw_active = body.get("active_job_keys")
⋮----
reconciliation = {
⋮----
capacity = body.get("capacity")
⋮----
source = str(capacity.get("source") or "").strip()
source_status = str(capacity.get("status") or "unavailable")
used = capacity.get("used_this_month")
remaining = capacity.get("remaining_tokens")
⋮----
authenticated = (
used_value = used if authenticated and isinstance(used, int) else None
remaining_value = (
limit_value = (
⋮----
active_job_keys = body.get(
⋮----
stale_job_keys = []
⋮----
job = control.queue.get(str(key))
⋮----
control_state = body.get("control_state")
⋮----
current_control = control.dashboard_control.worker_state(
⋮----
current_control = (
⋮----
job_control_states = body.get("job_control_states", {})
⋮----
job_key = str(raw_key)
reported_state = str(raw_state)
current_job_control = control.dashboard_control.job_state(job_key)
⋮----
cancelled_job = control.queue.cancel(
⋮----
payload = cancelled_job.get("payload") or {}
workflow_id = payload.get("workflow_id")
workflow_task_id = payload.get("workflow_task_id")
⋮----
allowed = {"validator_id", "builder_id", "key_id"}
unknown = sorted(set(body) - allowed)
⋮----
filters = {}
⋮----
value = body.get(name)
⋮----
result = control.releases.record_incident_report(
⋮----
release = control.releases.rollback(
⋮----
job = control.queue.enqueue(body)
⋮----
capabilities = [
⋮----
desired = control.dashboard_control.worker_state(worker_id)
⋮----
compatible = []
⋮----
job_control = control.dashboard_control.job_state(
⋮----
required = set(
⋮----
ranked = control.portfolio.rank(compatible)
candidate = ranked[0]["job"]
⋮----
assigned = candidate.get("assigned_worker")
⋮----
available_workers = list(
⋮----
available_workers = [
⋮----
placement = control.optimizer.choose_worker(
⋮----
job = control.queue.claim_key(
⋮----
key = str(body["key"])
before = control.queue.get(key)
⋮----
job = control.queue.ack(key, worker_id)
⋮----
key = parts[2]
worker_id = str(body.get("worker_id") or "")
⋮----
execution = control.dashboard_store.update_live_execution(
logs = body.get("logs") or []
⋮----
enriched = [
⋮----
checkpoint_ref = str(
⋮----
payload = dict(job.get("payload") or {})
⋮----
duration_seconds = body.get("duration_seconds")
⋮----
group_id = control.speculation.group_for_job(key)
⋮----
job = control.speculation.cancel_job(key)
⋮----
job = control.queue.complete(key, worker_id)
⋮----
cancelled = []
⋮----
cancelled = control.speculation.cancel_losers(
⋮----
workflow_id = before["payload"].get("workflow_id")
workflow_task_id = before["payload"].get(
workflow = None
⋮----
workflow = control.workflows.record_result(
⋮----
reason = str(body.get("reason", "worker failure"))
⋮----
job = control.queue.fail(
⋮----
actions = control.queue.recover_expired(
⋮----
control = ControlPlane(
server = ThreadingHTTPServer(
```

## File: production_os/control_surface.py
```python
def render_control_surface(payload: dict) -> str
⋮----
schedule = payload.get("schedule", {})
allocation = payload.get("resource_allocation", {})
work = schedule.get("work", [])
⋮----
rows = []
⋮----
allocation_rows = []
⋮----
raw = html.escape(json.dumps(payload, indent=2, ensure_ascii=False))
⋮----
def write_control_surface(payload: dict, path: str | Path) -> None
⋮----
destination = Path(path)
```

## File: production_os/controller.py
```python
def _rank_actions(assessments)
⋮----
actions = [action for assessment in assessments for action in assessment.actions]
⋮----
def _handoff_for_action(action, reuse, *, branch_protected: bool | None = None)
⋮----
related = [item.to_dict() for item in reuse if item.target == action.repository][:5]
handoff = {
asset_forge = asset_forge_tool_contract(handoff)
⋮----
def _required_capabilities_for(assessment, handoff: dict) -> list[str]
⋮----
required: list[str] = []
⋮----
lang = assessment.evidence.language.lower()
⋮----
def _load_github_mappings(path: str | None) -> list[dict]
⋮----
source = Path(path)
⋮----
payload = json.loads(source.read_text(encoding="utf-8"))
rows = payload.get("mappings", payload)
⋮----
results = []
⋮----
repository = str(item.get("repository", ""))
task = str(item.get("task", ""))
⋮----
work_state = fetch_github_work_state(
decision = runtime_decision_from_github(work_state)
updated = None
⋮----
updated = state.record_outcome(repository, task, decision).to_dict()
⋮----
row = {
⋮----
backend = open_backend(database_path) if database_path else None
⋮----
state = runtime_state_for(backend)
worker_registry = worker_registry_for(backend)
durable_queue = job_queue_for(backend)
claim_store = claim_store_for(backend)
⋮----
state = RuntimeState(runtime_state_path)
worker_registry = WorkerRegistry(worker_registry_path) if worker_registry_path else None
durable_queue = None
claim_store = ClaimStore(claims_path) if claims_path else None
⋮----
metrics_store = MetricsStore(metrics_path)
journal = ExecutionJournal(journal_path)
rate_limit_store = RateLimitStore(rate_limit_path) if rate_limit_path else None
approval_store = ApprovalStore(approval_path) if approval_path else None
policy_set = PolicySet.load(policy_path)
budget_ledger = BudgetLedger(budget_path) if budget_path else None
quarantine_store = QuarantineStore(quarantine_path) if quarantine_path else None
delivery_recovery = []
⋮----
delivery_recovery = durable_queue.recover_expired()
⋮----
delivery_recovery = recover_unacked_jobs(
⋮----
reconcile_actions = reconcile_runtime_state(state)
⋮----
healing_actions = apply_self_healing(state)
⋮----
governance_actions = []
⋮----
governance_actions = apply_governance(
⋮----
heartbeat_results = renew_active_leases(
⋮----
client = GitHubClient()
github_results = _reconcile_github(
⋮----
repos = client.list_repositories(owner)
assessments = []
⋮----
actions = _rank_actions(assessments)
reuse = detect_reuse(assessments)
schedule = build_schedule(
allocation = allocate_resources(schedule, total_slots=slots)
⋮----
action_lookup = {(a.repository, a.task): a for a in actions}
assessment_lookup = {a.evidence.full_name: a for a in assessments}
dispatches = []
emergency_stopped = emergency_stop_active(emergency_stop_path)
⋮----
action = action_lookup.get((item["repository"], item["task"]))
⋮----
assessment = assessment_lookup.get(action.repository)
branch_protected = None
base_handoff = _handoff_for_action(action, reuse)
policy = policy_set.merged_for(action.repository)
risk = classify_risk(base_handoff)
protected_for = set(
⋮----
branch_protected = client.get_branch_protection(
handoff = _handoff_for_action(
required_capabilities = _required_capabilities_for(
⋮----
result = dispatch_handoff(
⋮----
snapshot = build_snapshot(owner, assessments)
stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
snapshot_path = str(Path(snapshot_dir) / f"{stamp}.json")
⋮----
health = build_health(state, metrics_store.metrics.to_dict())
⋮----
observability = build_observability_payload(
⋮----
metrics_path = kwargs.get("metrics_path")
health_path = kwargs.get("health_path")
runtime_state_path = kwargs.get("runtime_state_path")
database_path = kwargs.get("database_path")
⋮----
state = (
```

## File: production_os/dashboard_alerts.py
```python
CONSECUTIVE_FAILURE_THRESHOLD = 3
COST_SPIKE_RATIO = 2.0
BUSY_TELEMETRY_STALE_SECONDS = 180
⋮----
def _parse_time(value)
⋮----
parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
⋮----
parsed = parsed.replace(tzinfo=timezone.utc)
⋮----
def derive_alerts(snapshot: dict) -> list[dict]
⋮----
alerts = []
workers = dict(snapshot.get("workers") or {})
productions = dict(snapshot.get("productions") or {})
performance = dict(snapshot.get("performance") or {})
usage = dict(snapshot.get("usage") or {})
⋮----
queued = int(productions.get("queued") or 0)
online = int(workers.get("online") or 0)
⋮----
consecutive_failures = int(performance.get("recent_failures") or 0)
⋮----
current_cost = usage.get("estimated_cost_usd")
baseline = usage.get("cost_baseline_usd")
⋮----
ratio = float(current_cost) / float(baseline)
⋮----
now = _parse_time(snapshot.get("generated_at")) or datetime.now(timezone.utc)
stale_workers = []
⋮----
last = _parse_time(worker.get("last_heartbeat"))
⋮----
age = max(0.0, (now - last).total_seconds())
⋮----
severity_order = {"high":0, "medium":1, "low":2}
```

## File: production_os/dashboard_backups.py
```python
BACKUP_ID_RE = re.compile(r"^\d{8}T\d{6}Z-[0-9a-f]{12}$")
⋮----
class BackupError(RuntimeError)
⋮----
class BackupTempCandidateConflict(BackupError)
⋮----
def __init__(self, expected: int, actual: int)
⋮----
class BackupRetentionCandidateConflict(BackupError)
⋮----
def _now() -> str
⋮----
def _backend_kind(backend) -> str
⋮----
name = backend.__class__.__name__.lower()
⋮----
def _configured_dir() -> Path | None
⋮----
raw = str(os.getenv("PRODUCTION_OS_BACKUP_DIR") or "").strip()
⋮----
def _safe_manifest(path: Path) -> dict | None
⋮----
data = json.loads(path.read_text(encoding="utf-8"))
⋮----
allowed = {
⋮----
def _safe_activation_receipt(path: Path) -> dict | None
⋮----
required = {
⋮----
candidate_id = str(data.get("candidate_id") or "")
source_backup_id = str(data.get("source_backup_id") or "")
rollback_backup_id = str(data.get("rollback_backup_id") or "")
activated_at = str(data.get("activated_at") or "")
schema_version = str(data.get("schema_version") or "")
digest = str(data.get("sha256") or "").lower()
⋮----
directory = _configured_dir()
⋮----
bounded = max(1, min(200, int(limit)))
rows = []
⋮----
item = _safe_activation_receipt(path)
⋮----
def _backup_filesystem_capacity(directory: Path | None) -> dict
⋮----
unavailable = {
⋮----
target = directory
⋮----
target = target.parent
⋮----
stats = os.statvfs(target)
⋮----
block_size = int(stats.f_frsize or stats.f_bsize or 0)
⋮----
total = max(0, int(stats.f_blocks) * block_size)
free = max(0, int(stats.f_bfree) * block_size)
available = max(0, int(stats.f_bavail) * block_size)
⋮----
used = max(0, total - free)
available_percent = round(available / total * 100, 2)
used_percent = round(used / total * 100, 2)
⋮----
status = "critical"
⋮----
status = "warning"
⋮----
status = "ok"
⋮----
def _backup_age_summary(created_values: list[str], *, now: datetime | None = None) -> dict
⋮----
now = now or datetime.now(timezone.utc)
valid: list[datetime] = []
invalid = 0
buckets = {
⋮----
parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
⋮----
parsed = parsed.replace(tzinfo=timezone.utc)
parsed = parsed.astimezone(timezone.utc)
age_seconds = max(0.0, (now - parsed).total_seconds())
⋮----
BACKUP_RETENTION_DAYS = 30
BACKUP_RETENTION_MIN_KEEP = 3
⋮----
invalid_timestamp_count = 0
⋮----
backup_id = str(item.get("backup_id") or "")
created_at = str(item.get("created_at") or "")
⋮----
parsed = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
⋮----
size = item.get("size_bytes")
size_bytes = (
⋮----
newest_ids = {
cutoff_seconds = BACKUP_RETENTION_DAYS * 86400
candidate_ids: list[str] = []
candidate_count = 0
candidate_bytes = 0
protected_recent = 0
protected_latest_floor = 0
protected_restore_history = 0
⋮----
backup_id = item["backup_id"]
age_seconds = max(0.0, (now - item["created_at"]).total_seconds())
⋮----
candidate_fingerprint = sha256(
preview = {
⋮----
def _retention_source_state(directory: Path) -> tuple[list[dict], set[str]]
⋮----
verified_backups: list[dict] = []
protected_backup_ids: set[str] = set()
backup_manifest = re.compile(
activation_receipt = re.compile(
⋮----
manifest = _safe_manifest(path)
⋮----
receipt = _safe_activation_receipt(path)
⋮----
def backup_storage_inventory(backend) -> dict
⋮----
backup_age = _backup_age_summary([])
retention_preview = _backup_retention_preview([], set())
zero = {
⋮----
backup_ids: set[str] = set()
candidate_ids: set[str] = set()
metrics = dict(zero)
verified_backup_created_at: list[str] = []
⋮----
backup_sqlite = re.compile(
⋮----
candidate_sqlite = re.compile(
candidate_manifest = re.compile(
⋮----
paths = list(directory.iterdir())
⋮----
size = int(path.stat().st_size)
⋮----
size = max(0, size)
⋮----
name = path.name
⋮----
age_seconds = max(
⋮----
age_seconds = 0.0
⋮----
match = activation_receipt.fullmatch(name)
⋮----
match = candidate_sqlite.fullmatch(name) or candidate_manifest.fullmatch(name)
⋮----
sqlite_match = backup_sqlite.fullmatch(name)
manifest_match = backup_manifest.fullmatch(name)
match = sqlite_match or manifest_match
⋮----
expected_candidate_fingerprint = str(
⋮----
actual_count = int(preview["candidate_count"])
actual_fingerprint = str(preview["candidate_fingerprint"])
⋮----
deleted_count = 0
deleted_bytes = 0
⋮----
manifest_path = directory / f"{backup_id}.json"
backup_path = directory / f"{backup_id}.sqlite"
manifest = _safe_manifest(manifest_path)
⋮----
paths = [path for path in (backup_path, manifest_path) if path.is_file()]
sizes = []
⋮----
inventory = backup_storage_inventory(backend)
⋮----
actual = int(inventory.get("stale_temp_count") or 0)
⋮----
now_ts = datetime.now(timezone.utc).timestamp()
⋮----
stat = path.stat()
⋮----
age_seconds = max(0.0, now_ts - stat.st_mtime)
⋮----
size = max(0, int(stat.st_size))
⋮----
def backup_readiness(backend) -> dict
⋮----
kind = _backend_kind(backend)
⋮----
manifests = []
⋮----
item = _safe_manifest(path)
⋮----
parent = directory.parent
⋮----
def verify_backup_for_restore(backend, backup_id: str) -> dict
⋮----
backup_id = str(backup_id or "").strip()
⋮----
readiness = backup_readiness(backend)
⋮----
digest = sha256()
size = 0
⋮----
chunk = handle.read(1024 * 1024)
⋮----
actual_sha = digest.hexdigest()
⋮----
expected_size = manifest.get("size_bytes")
expected_sha = str(manifest.get("sha256") or "")
⋮----
connection = sqlite3.connect(
⋮----
integrity_row = connection.execute(
integrity = integrity_row[0] if integrity_row else None
⋮----
schema_row = connection.execute(
⋮----
schema_version = str(schema_row[0])
⋮----
def stage_verified_sqlite_restore(backend, backup_id: str) -> dict
⋮----
verified = verify_backup_for_restore(backend, backup_id)
⋮----
source_path = directory / f"{backup_id}.sqlite"
candidate_id = (
temp_path = directory / f".restore-{candidate_id}.sqlite.tmp"
final_path = directory / f"restore-{candidate_id}.sqlite"
manifest_path = directory / f"restore-{candidate_id}.json"
temp_manifest = directory / f".restore-{candidate_id}.json.tmp"
⋮----
source = sqlite3.connect(
⋮----
destination = sqlite3.connect(temp_path)
⋮----
integrity_row = destination.execute(
⋮----
schema_row = destination.execute(
⋮----
staged_at = _now()
manifest = {
⋮----
def verify_staged_restore_candidate(backend, candidate_id: str) -> dict
⋮----
candidate_id = str(candidate_id or "").strip()
⋮----
candidate_path = directory / f"restore-{candidate_id}.sqlite"
⋮----
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
⋮----
integrity_row = connection.execute("PRAGMA integrity_check").fetchone()
⋮----
expected_schema = str(getattr(backend, "SCHEMA_VERSION", ""))
⋮----
candidate = verify_staged_restore_candidate(backend, candidate_id)
database_path = Path(getattr(backend, "path", ""))
⋮----
receipt_path = directory / f"restore-{candidate_id}.activation.json"
⋮----
# Revalidate after acquiring the exclusive lock so the activation
# decision is based on the exact bytes we will install.
⋮----
rollback = create_verified_sqlite_backup(backend)
rollback_path = directory / f"{rollback['backup_id']}.sqlite"
⋮----
temp_target = database_path.with_name(
rollback_temp = database_path.with_name(
receipt_temp = directory / (
manifest_temp = directory / (
sidecars = [
replaced = False
⋮----
row = staged.execute("PRAGMA integrity_check").fetchone()
⋮----
replaced = True
⋮----
restored = sqlite3.connect(database_path)
⋮----
row = restored.execute("PRAGMA integrity_check").fetchone()
⋮----
schema_row = restored.execute(
⋮----
activated_at = _now()
receipt = {
⋮----
rollback_db = sqlite3.connect(database_path)
⋮----
rollback_row = rollback_db.execute(
⋮----
def create_verified_sqlite_backup(backend) -> dict
⋮----
backup_id = (
temp_path = directory / f".{backup_id}.sqlite.tmp"
final_path = directory / f"{backup_id}.sqlite"
⋮----
temp_manifest = directory / f".{backup_id}.json.tmp"
⋮----
source = backend.connect()
⋮----
row = destination.execute("PRAGMA integrity_check").fetchone()
integrity = row[0] if row else None
```

## File: production_os/dashboard_control.py
```python
WORKER_STATES = {"active", "paused", "draining"}
JOB_STATES = {"active", "cancel_requested"}
⋮----
class DashboardControlError(RuntimeError)
⋮----
class DashboardControl
⋮----
@staticmethod
    def _worker_view(row: dict | None, worker_id: str) -> dict
⋮----
value = dict(row)
⋮----
requested = value.get("requested_at")
updated = value.get("updated_at")
⋮----
@staticmethod
    def _job_view(row: dict | None, job_key: str) -> dict
⋮----
def worker_state(self, worker_id: str) -> dict
⋮----
row = self.store.set_worker_control(
⋮----
current = self.store.get_worker_control(worker_id)
⋮----
row = self.store.acknowledge_worker_control(worker_id, desired_state, at=at)
⋮----
def job_state(self, job_key: str) -> dict
⋮----
row = self.store.set_job_control(
⋮----
def acknowledge_job_cancel(self, job_key: str, *, at: str | None = None) -> dict
⋮----
row = self.store.acknowledge_job_control(job_key, at=at)
⋮----
def kick_worker(self, worker_id: str) -> dict
⋮----
def retry_job(self, job_key: str, *, requested_by: str) -> dict
⋮----
job = self.queue.get(job_key)
payload = job.get("payload") or {}
workflow_id = str(payload.get("workflow_id") or "").strip()
task_id = str(payload.get("workflow_task_id") or "").strip()
⋮----
current = self.job_state(job_key)
⋮----
replacement = self.workflows.retry_task(
```

## File: production_os/dashboard_github.py
```python
_REPOSITORY = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
⋮----
class RepositorySnapshotUnavailable(RuntimeError)
⋮----
def _now() -> str
⋮----
class RepositorySnapshotter
⋮----
def __init__(self, github, store)
⋮----
@staticmethod
    def _validate(repository: str) -> str
⋮----
value = str(repository or "").strip()
⋮----
def refresh(self, repository: str) -> dict
⋮----
repository = self._validate(repository)
meta = self.github.repository(repository)
branch = str(meta.get("default_branch") or "")
⋮----
latest = self.github.latest_commit(repository, branch) or {}
release = self.github.latest_release(repository)
captured = _now()
commit_shas = set()
⋮----
sha = str(raw_sha).strip().lower()
⋮----
snapshot = {
stored = self.store.save_repository_snapshot(snapshot)
⋮----
def get(self, repository: str, *, max_age_seconds: int = 300) -> dict
⋮----
cached = self.store.latest_repository_snapshot(repository)
⋮----
captured = datetime.fromisoformat(str(cached["captured_at"]).replace("Z","+00:00"))
```

## File: production_os/dashboard_health.py
```python
STALE_BUSY_WORKER_SECONDS = 180
STALE_RUNNING_EXECUTION_SECONDS = 300
⋮----
def _dt(value)
⋮----
parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
⋮----
def derive_control_health(snapshot: dict) -> dict
⋮----
now = _dt(snapshot.get("generated_at")) or datetime.now(timezone.utc)
reasons = []
⋮----
queued = int((snapshot.get("productions") or {}).get("queued") or 0)
online = int((snapshot.get("workers") or {}).get("online") or 0)
⋮----
stale_workers = []
⋮----
last = _dt(worker.get("last_heartbeat"))
⋮----
age = max(0.0, (now - last).total_seconds())
⋮----
stale_executions = []
⋮----
last = _dt(
⋮----
filesystem = (
filesystem_status = str(filesystem.get("status") or "")
⋮----
available_percent = filesystem.get("available_percent")
```

## File: production_os/dashboard_incidents.py
```python
def signals_from_health(health: dict) -> list[dict]
⋮----
signals = []
⋮----
code = str(reason.get("code") or "")
severity = str(reason.get("severity") or "medium")
evidence = dict(reason.get("evidence") or {})
⋮----
queued = int(evidence.get("queued") or 0)
⋮----
status = str(evidence.get("status") or "warning")
available = evidence.get("available_percent")
⋮----
worker_id = str(worker.get("worker_id") or "")
⋮----
age = worker.get("age_seconds")
⋮----
job_key = str(execution.get("job_key") or "")
⋮----
age = execution.get("age_seconds")
⋮----
def dedupe_key(signal: dict) -> str
```

## File: production_os/dashboard_maintenance.py
```python
TERMINAL_EXECUTION_STATUSES = {"succeeded", "failed", "cancelled"}
⋮----
@dataclass(frozen=True)
class RetentionSpec
⋮----
label: str
table: str
timestamp_column: str
env_name: str
default_days: int
key_column: str = "id"
mode: str = "prunable"
⋮----
RETENTION_SPECS = (
⋮----
class RetentionCandidateConflict(RuntimeError)
⋮----
def __init__(self, expected: int, actual: int)
⋮----
def _is_postgres(backend) -> bool
⋮----
def _execute(db, backend, statement: str, params: tuple = ())
⋮----
sql = statement.replace("?", "%s") if _is_postgres(backend) else statement
⋮----
def _parse_time(value)
⋮----
parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
⋮----
parsed = parsed.replace(tzinfo=timezone.utc)
⋮----
def _retention_days(env_name: str, default: int) -> int
⋮----
raw = str(os.getenv(env_name) or "").strip()
⋮----
value = int(raw)
⋮----
def _database_size_bytes(backend) -> int | None
⋮----
row = db.execute(
⋮----
value = row["bytes"]
⋮----
path = getattr(backend, "path", None)
⋮----
base = Path(path)
total = 0
found = False
⋮----
found = True
⋮----
def _select_columns(spec: RetentionSpec) -> str
⋮----
columns = [
⋮----
parsed = _parse_time(row["timestamp"])
⋮----
status = str(row["row_status"] or "")
⋮----
cutoff = now - timedelta(days=retention_days)
⋮----
valid_count = 0
invalid = 0
prunable = 0
protected = 0
oldest = None
newest = None
⋮----
cursor = db.execute(
⋮----
oldest = parsed
⋮----
newest = parsed
disposition = _old_row_disposition(
⋮----
current = now or datetime.now(timezone.utc)
⋮----
current = current.replace(tzinfo=timezone.utc)
current = current.astimezone(timezone.utc)
⋮----
tables = []
errors = []
⋮----
total_candidates = sum(
prunable_candidates = sum(
protected_candidates = sum(
total_rows = sum(int(row.get("rows") or 0) for row in tables)
⋮----
size_bytes = _database_size_bytes(backend)
⋮----
size_bytes = None
⋮----
status = (
⋮----
selected: dict[str, list[object]] = {}
⋮----
cutoff = now - timedelta(
keys: list[object] = []
cursor = _execute(
⋮----
deleted: dict[str, int] = {}
⋮----
keys_by_label = _collect_prunable_keys(
actual = sum(len(keys) for keys in keys_by_label.values())
⋮----
spec_by_label = {spec.label:spec for spec in RETENTION_SPECS}
⋮----
spec = spec_by_label[label]
count = 0
⋮----
chunk = keys[offset:offset + 200]
⋮----
placeholders = ",".join("?" for _ in chunk)
⋮----
deleted_total = sum(deleted.values())
```

## File: production_os/dashboard_playbooks.py
```python
ACTIVE_JOB_STATUSES = {"claimed", "acked", "running"}
⋮----
code = str(incident.get("code") or "")
target_type = str(incident.get("target_type") or "")
target_id = str(incident.get("target_id") or "")
suggestions: list[dict] = []
⋮----
availability = (
⋮----
key = str(row.get("key") or "")
⋮----
owner = str((job or {}).get("claimed_by") or "")
status = str((job or {}).get("status") or "")
```

## File: production_os/dashboard_remediation_metrics.py
```python
WINDOW_SECONDS = {
⋮----
def _parse_time(value)
⋮----
parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
⋮----
parsed = parsed.replace(tzinfo=timezone.utc)
⋮----
def _bucket(rows: list[dict], *, now: datetime) -> dict
⋮----
total = len(rows)
resolved = sum(
still_active = sum(
pending = sum(
not_applicable = sum(
denominator = resolved + still_active
resolution_rate = (
durations = []
⋮----
completed = _parse_time(row.get("completed_at"))
verified = _parse_time(row.get("verified_at"))
⋮----
watching = sum(
recurred = sum(
recurrence_denominator = watching + recurred
recurrence_rate = (
recurrence_durations = []
watching_ages = []
⋮----
state = str(row.get("recurrence_state") or "not_evaluated")
⋮----
recurred_at = _parse_time(row.get("recurred_at"))
⋮----
current = now or datetime.now(timezone.utc)
⋮----
current = current.replace(tzinfo=timezone.utc)
seconds = WINDOW_SECONDS[window]
cutoff = (
selected = []
⋮----
requested = _parse_time(row.get("requested_at"))
⋮----
def grouped(key: str) -> list[dict]
⋮----
groups: dict[str, list[dict]] = {}
⋮----
value = str(row.get(key) or "unknown")
```

## File: production_os/dashboard_security.py
```python
_SENSITIVE_KEYS = {
⋮----
_PATTERNS = (
⋮----
def _scrub_secret_patterns(value: str) -> str
⋮----
value = pattern.sub(r"\1[REDACTED]", value)
⋮----
def redact_log_value(value: object) -> object
```

## File: production_os/dashboard_service.py
```python
class DashboardNotFound(KeyError)
⋮----
def _now()
⋮----
def _is_postgres(backend) -> bool
⋮----
def _execute(db, backend, statement: str, params: tuple = ())
⋮----
sql = statement.replace("?", "%s") if _is_postgres(backend) else statement
⋮----
class DashboardService
⋮----
def __init__(self, control)
⋮----
def _worker_rows(self)
⋮----
rows=db.execute("SELECT * FROM workers ORDER BY worker_id").fetchall()
⋮----
@staticmethod
    def _distinct_commit_shas(executions: list[dict]) -> set[str]
⋮----
shas: set[str] = set()
⋮----
value = str(sha).strip().lower()
⋮----
@staticmethod
    def _window_cutoff(window: str)
⋮----
seconds={"24h":86400,"7d":604800,"30d":2592000,"all":None}
⋮----
value=seconds[window]
⋮----
def _executions_in_window(self, executions: list[dict], window: str) -> list[dict]
⋮----
cutoff=self._window_cutoff(window)
⋮----
selected=[]
⋮----
raw=row.get("finished_at") or row.get("started_at")
⋮----
parsed=datetime.fromisoformat(str(raw).replace("Z","+00:00"))
⋮----
parsed=parsed.replace(tzinfo=timezone.utc)
⋮----
@staticmethod
    def _previous_window_cost(rows: list[dict], window: str)
⋮----
seconds = {"24h":86400, "7d":604800, "30d":2592000}.get(window)
⋮----
now = datetime.now(timezone.utc)
start = now - timedelta(seconds=seconds * 2)
end = now - timedelta(seconds=seconds)
total = 0.0
found = False
⋮----
raw = row.get("occurred_at")
⋮----
occurred = datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
⋮----
occurred = occurred.replace(tzinfo=timezone.utc)
⋮----
cost = row.get("estimated_cost_usd")
⋮----
found = True
⋮----
def overview(self, window: str) -> dict
⋮----
usage_rows=self.store.usage_events()
usage=aggregate_usage(usage_rows,window=window,
previous_cost=self._previous_window_cost(usage_rows, window)
workers=self._worker_rows()
executions=[]
⋮----
rows=db.execute("SELECT * FROM job_executions").fetchall()
executions=[dict(x) for x in rows]
jobs=db.execute("SELECT status,COUNT(*) AS count FROM jobs GROUP BY status").fetchall()
states={str(x["status"]):int(x["count"]) for x in jobs}
succeeded=sum(x.get("status")=="succeeded" for x in executions)
finished=sum(x.get("status") in {"succeeded","failed","cancelled"} for x in executions)
terminal = sorted(
recent_failures=0
⋮----
snapshot = {
⋮----
@staticmethod
    def _worker_capabilities(worker: dict) -> list[str]
⋮----
value = worker.get("capabilities")
⋮----
raw = worker.get("capabilities_json")
⋮----
parsed = json.loads(raw)
⋮----
parsed = []
⋮----
def autopilot_queue(self, limit: int = 50) -> dict
⋮----
limit = max(1, min(200, int(limit)))
queued = self.control.queue.peek_candidates(limit=limit)
ranked = []
⋮----
ranked_item = self.control.portfolio.rank([job])[0]
⋮----
ranked_item = {
⋮----
workers = self._worker_rows()
⋮----
worker_views = []
⋮----
worker_id = str(worker.get("worker_id") or "")
desired = self.control.dashboard_control.worker_state(worker_id)
item = {
⋮----
jobs = []
⋮----
job = ranked_item["job"]
payload = dict(job.get("payload") or {})
required = sorted({
assigned = str(job.get("assigned_worker") or "").strip() or None
⋮----
scoped = [
capable = [
eligible = [
⋮----
wait_reason = None
⋮----
wait_reason = "assigned_worker_unavailable"
⋮----
wait_reason = "no_worker"
⋮----
wait_reason = "missing_capability"
⋮----
wait_reason = "worker_controlled"
⋮----
wait_reason = "capacity_full"
⋮----
wait_reason = "no_online_worker"
⋮----
predicted = [
free_slots = sum(
summary = {
⋮----
def attention(self, *, limit: int = 50) -> dict
⋮----
bounded = max(1, min(200, int(limit)))
managed = self.control.managed_projects.list(limit=200)
autopilot = self.autopilot_queue(limit=200)
incidents = self.incidents(limit=200).get("incidents", [])
⋮----
items: list[dict] = []
severity_priority = {
⋮----
severity = str(incident.get("severity") or "medium")
actions = []
⋮----
status = str(project.get("status") or "")
workflow = project.get("current_workflow") or {}
outcome = project.get("outcome") or {}
workflow_status = str(workflow.get("status") or "")
⋮----
failed = workflow_status == "failed"
⋮----
wait_priorities = {
blocked_jobs = [
⋮----
reason = job.get("wait_reason")
⋮----
completed = [
⋮----
selected = items[:bounded]
⋮----
def health(self) -> dict
⋮----
job_rows = db.execute(
execution_rows = db.execute(
states = {
⋮----
health = self.health()
signals = signals_from_health(health)
active_keys: set[str] = set()
⋮----
rows = self.store.dashboard_incidents(
kick_mode = (
enriched = []
⋮----
item = dict(incident)
recoverable_jobs = []
job = None
⋮----
found = _execute(
recoverable_jobs = [dict(row) for row in found]
⋮----
job = self.control.queue.get(str(item.get("target_id")))
⋮----
# Refresh durable incident state first so verification reflects
# current server facts rather than stale browser state.
⋮----
def remediation_analytics(self, window: str) -> dict
⋮----
payload = aggregate_remediation_analytics(
⋮----
def backups(self) -> dict
⋮----
def create_verified_backup(self) -> dict
⋮----
def verify_backup_restore_readiness(self, backup_id: str) -> dict
⋮----
def stage_backup_restore(self, backup_id: str) -> dict
⋮----
def control_audit(self, limit: int = 100) -> dict
⋮----
def workers(self)
⋮----
rows=[]
⋮----
desired=self.control.dashboard_control.worker_state(worker["worker_id"])
item=dict(worker)
⋮----
def worker_detail(self, worker_id)
⋮----
rows=[x for x in self._worker_rows() if x.get("worker_id")==worker_id]
⋮----
worker=dict(rows[0])
desired=self.control.dashboard_control.worker_state(worker_id)
⋮----
recoverable_rows = _execute(
⋮----
def worker_logs(self,worker_id,after,limit)
⋮----
limit=max(1,min(500,int(limit)))
⋮----
def worker_usage(self,worker_id,window)
⋮----
def _repositories(self)
⋮----
found=set()
⋮----
rows=db.execute(f"SELECT DISTINCT repository FROM {table} WHERE repository IS NOT NULL").fetchall()
⋮----
def maintenance(self, *, force: bool = False) -> dict
⋮----
now = time.monotonic()
cached = self._maintenance_cache
⋮----
ttl = 30.0 if cached.get("status") == "unknown" else 300.0
⋮----
payload = storage_maintenance_snapshot(self.control.backend)
⋮----
def prune_maintenance(self, expected_candidate_rows: int) -> dict
⋮----
result = prune_expired_history(
⋮----
def launch_readiness(self, repository: str) -> dict
⋮----
repository = str(repository or "").strip()
parts = repository.split("/")
⋮----
catalog = self.repositories()
known = any(
workers = self.workers().get("workers", [])
online = [
available = [
⋮----
queued_row = db.execute(
queued = int(queued_row["count"] if queued_row else 0)
⋮----
execution = "immediate" if available else "queued"
message = (
⋮----
key = str(job.get("key") or "").strip()
⋮----
control_state = self.control.dashboard_control.job_state(key)
⋮----
cancelled = self.control.queue.cancel_queued(
⋮----
payload = cancelled.get("payload") or {}
workflow_id = str(payload.get("workflow_id") or "").strip()
task_id = str(payload.get("workflow_task_id") or "").strip()
⋮----
project = self.control.managed_projects.get(project_id)
⋮----
pending = False
⋮----
task_status = str(task.get("status") or "")
⋮----
job_key = str(task.get("claimed_job_key") or "").strip()
⋮----
job = self.control.queue.get(job_key)
⋮----
job_status = str(job.get("status") or "")
⋮----
cancelled = self.finalize_queued_cancel(
⋮----
state = self.control.dashboard_control.request_job_cancel(
pending = state.get("acknowledged_at") is None
⋮----
status = "cancel_requested" if pending else (
primary = jobs[0] if jobs else {}
⋮----
def production_status(self, project_id: str) -> dict
⋮----
project_id = str(project_id or "").strip()
⋮----
tasks = [
current_task = next(
job_key = (
⋮----
execution = None
⋮----
execution = self.store.latest_execution(job_key)
⋮----
project_status = str(project.get("status") or "")
⋮----
job_status = str((job or {}).get("status") or "")
task_status = str((current_task or {}).get("status") or "")
execution_status = str((execution or {}).get("status") or "")
job_control = (
cancel_requested = (
⋮----
phase = "cancelling"
⋮----
phase = "done"
⋮----
phase = "review_required"
⋮----
phase = "needs_attention"
⋮----
phase = "running"
⋮----
phase = "claimed"
⋮----
phase = "queued"
⋮----
phase = "preparing"
⋮----
queue_position = None
⋮----
queue_position = index
⋮----
progress = (execution or {}).get("progress_percent")
⋮----
progress = None
⋮----
progress = max(0.0, min(100.0, float(progress)))
⋮----
worker_id = (
stage = (execution or {}).get("current_stage")
attempt = (
telemetry_at = (execution or {}).get("last_telemetry_at")
⋮----
message = "Annulation demandée · arrêt coopératif en cours."
⋮----
details = []
⋮----
message = "En cours" + (
⋮----
message = "Résultat prêt à revoir."
⋮----
message = "Une action opérateur est requise."
⋮----
message = "Projet terminé."
⋮----
message = "Préparation de l’exécution."
⋮----
selected_filter = str(category or "all").strip().lower()
allowed = {"all", "active", "review", "problems", "completed"}
⋮----
selected_sort = str(sort or "priority").strip().lower()
⋮----
raw_search = str(search or "").strip()
normalized_search = raw_search.casefold()
⋮----
managed = self.control.managed_projects.list(limit=500)
allowed_statuses = {
candidates = [
⋮----
items = []
phase_counts: dict[str, int] = {}
⋮----
project_id = str(
⋮----
status = self.production_status(project_id)
current = status.get("project") or project
runtime = status.get("runtime") or {}
phase = str(runtime.get("phase") or "preparing")
⋮----
def group(item: dict) -> str
⋮----
phase = str(
⋮----
priority = {
⋮----
def matches_search(item: dict) -> bool
⋮----
haystack = "\n".join([
⋮----
filtered = [
⋮----
visible = filtered[:bounded]
⋮----
live_phases = {
⋮----
def repositories(self) -> dict
⋮----
owner = str(
github = GitHubClient()
source = "github"
⋮----
rows = github.list_accessible_repositories(owner)
⋮----
source = "observed-projects"
rows = [
repositories = []
⋮----
full_name = str(row.get("full_name") or "").strip()
⋮----
def projects(self)
⋮----
def _require_project(self,repository)
⋮----
def project_detail(self,repository)
⋮----
@staticmethod
    def _progress_snapshot_state(snapshot)
⋮----
def project_progress(self,repository)
⋮----
rows=_execute(
workflow=self.control.workflows.get(str(rows[0]["id"])) if rows else None
production=workflow_progress(workflow) if workflow else {
snapshot=self.store.latest_repository_snapshot(repository)
executions=self.store.executions_for_repository(repository,limit=500)
events=self.control.backend.events_after(0,500)
evidence=build_project_evidence(
calculated=ProjectProgressEngine().calculate(repository,evidence)
⋮----
components=calculated.get("components") or {}
candidate={
candidate_state=self._progress_snapshot_state(candidate)
fingerprint=hashlib.sha256(json.dumps(candidate_state,sort_keys=True,separators=(",",":"),default=str).encode()).hexdigest()
⋮----
persisted=self.store.latest_progress_snapshot(repository)
meaningful=self._progress_snapshot_state(persisted) != candidate_state
⋮----
persisted=self.store.save_progress_snapshot(candidate)
⋮----
def project_commits(self,repository,window)
⋮----
executions=self._executions_in_window(self.store.executions_for_repository(repository,limit=500),window)
⋮----
def _legacy_workflow_usage_rows(self, repository)
⋮----
modern_rows=_execute(
modern_pairs={
⋮----
usage_rows=[]
⋮----
result=json.loads(row["result_json"]) if isinstance(row["result_json"],str) else row["result_json"]
⋮----
usage=(result or {}).get("usage") if isinstance(result,dict) else None
providers=usage.get("providers") if isinstance(usage,dict) else None
⋮----
def project_usage(self,repository,window)
⋮----
current=self.store.usage_events(repository=repository)
legacy=self._legacy_workflow_usage_rows(repository)
payload=aggregate_usage(current+legacy,window=window,
⋮----
def project_workflows(self,repository)
⋮----
rows=_execute(db,self.control.backend,"SELECT id,name,status,created_at,updated_at FROM workflows WHERE repository=? ORDER BY created_at DESC LIMIT 100",(repository,)).fetchall()
⋮----
def project_history(self,repository)
⋮----
executions=self.store.executions_for_repository(repository,limit=100)
⋮----
legacy=[dict(x) for x in rows]
coverage="complete"
⋮----
coverage="partial"
⋮----
def activity(self,*,repository=None,worker_id=None,event_type=None,after=0,limit=100)
⋮----
rows=self.control.backend.events_after(int(after),limit)
if repository: rows=[x for x in rows if x.get("repository")==repository]
⋮----
rows=[x for x in rows if str((x.get("payload") or {}).get("worker_id") or "")==worker_id]
if event_type: rows=[x for x in rows if x.get("event_type")==event_type]
```

## File: production_os/dashboard_store.py
```python
def _now() -> str
⋮----
def _is_postgres(backend) -> bool
⋮----
def _sql(backend, statement: str) -> str
⋮----
def _execute(db, backend, statement: str, params: tuple = ())
⋮----
cursor = db.cursor()
⋮----
def execution_id(job_key: str, attempt: int) -> str
⋮----
def _bounded_progress(value)
⋮----
value = float(value)
⋮----
def _valid_commit_shas(values) -> list[str]
⋮----
shas = []
seen = set()
⋮----
sha = value.strip().lower()
⋮----
def _decode(row) -> dict | None
⋮----
value = dict(row)
⋮----
evidence = value.get("evidence") or {}
⋮----
class DashboardStore
⋮----
def __init__(self, backend)
⋮----
def _fetchone(self, db, statement, params=())
⋮----
cur = _execute(db, self.backend, statement, tuple(params))
⋮----
def _fetchall(self, db, statement, params=())
⋮----
def start_execution(self, job: dict, worker_id: str, *, started_at: str | None = None) -> dict
⋮----
attempt = max(1, int(job.get("delivery_attempt") or 1))
ident = execution_id(job["key"], attempt)
payload = job.get("payload") or {}
at = started_at or _now()
⋮----
row = self._fetchone(db, "SELECT * FROM job_executions WHERE id=?", (ident,))
⋮----
def execution_count(self, job_key: str) -> int
⋮----
cur = _execute(db, self.backend, "SELECT COUNT(*) AS n FROM job_executions WHERE job_key=?", (job_key,))
row = cur.fetchone()
⋮----
def latest_execution(self, job_key: str) -> dict | None
⋮----
def update_live_execution(self, job_key: str, worker_id: str, telemetry: dict, *, at: str | None = None) -> dict
⋮----
progress = _bounded_progress(telemetry.get("progress")); usage = telemetry.get("usage")
⋮----
row = self._fetchone(db, "SELECT * FROM job_executions WHERE job_key=? ORDER BY attempt DESC LIMIT 1", (job_key,))
⋮----
old = row.get("progress_percent"); stage = telemetry.get("stage", row.get("current_stage"))
⋮----
live_usage = usage if usage is not None else (row.get("live_usage") or {})
⋮----
result = result or {}; usage = result.get("usage") or {}; commits = result.get("commits") or {}; shas = _valid_commit_shas(commits.get("shas"))
⋮----
timestamp = at or _now()
dedupe_key = f"{code}:{target_type}:{target_id}"
ident = uuid4().hex
⋮----
bounded = max(1, min(500, int(limit)))
⋮----
rows = self._fetchall(
resolved = []
⋮----
row = self._fetchone(
⋮----
incident = self._fetchone(
⋮----
timestamp = completed_at or _now()
⋮----
updated: list[dict] = []
⋮----
state = (
⋮----
current = self._fetchone(
⋮----
def remediation_analytics_rows(self) -> list[dict]
⋮----
def control_audit_events(self, *, limit: int = 100) -> list[dict]
⋮----
def get_worker_control(self, worker_id: str) -> dict | None
⋮----
def get_job_control(self, job_key: str) -> dict | None
⋮----
def executions_for_worker(self, worker_id: str, *, limit: int = 100) -> list[dict]
⋮----
def executions_for_repository(self, repository: str, *, limit: int = 100) -> list[dict]
⋮----
def usage_events(self, *, worker_id=None, repository=None, since=None) -> list[dict]
⋮----
where = (" WHERE " + " AND ".join(clauses)) if clauses else ""
⋮----
def append_logs(self, worker_id: str, rows: list[dict]) -> list[dict]
⋮----
saved=[]
⋮----
row=redact_log_value(source); ident=str(row.get("id") or uuid4()); created=row.get("created_at") or _now()
⋮----
def logs_for_worker(self, worker_id: str, *, after: str | None = None, limit: int = 100) -> list[dict]
⋮----
limit=max(1,min(int(limit),500))
⋮----
cursor=self._fetchone(db,"SELECT * FROM worker_log_events WHERE id=? AND worker_id=?",(after,worker_id))
⋮----
def _save_snapshot(self, table: str, snapshot: dict, json_fields: tuple[str, ...]) -> dict
⋮----
allowed={
values=dict(snapshot)
⋮----
cols=[x for x in allowed if x in values]
⋮----
def save_repository_snapshot(self, snapshot: dict) -> dict: return self._save_snapshot("project_repository_snapshots",snapshot,("snapshot_json",))
def latest_repository_snapshot(self, repository: str) -> dict | None
def save_progress_snapshot(self, snapshot: dict) -> dict: return self._save_snapshot("project_progress_snapshots",snapshot,("evidence_json","remaining_work_json","blockers_json"))
def latest_progress_snapshot(self, repository: str) -> dict | None
def progress_history(self, repository: str, *, limit: int = 100) -> list[dict]
def save_provider_quota_snapshot(self, snapshot: dict) -> dict: return self._save_snapshot("provider_quota_snapshots",snapshot,())
def latest_provider_quota_snapshots(self) -> list[dict]
```

## File: production_os/dashboard_ui.py
```python
DASHBOARD_HTML = """<!doctype html>
```

## File: production_os/dashboard_usage.py
```python
"""Versioned pricing and safe historical API-usage aggregation."""
⋮----
WINDOW_SECONDS = {
_TOKEN_FIELDS = (
⋮----
def _dt(value)
⋮----
raw = str(value or "").strip()
⋮----
raw = raw[:-1] + "+00:00"
parsed = datetime.fromisoformat(raw)
⋮----
class PricingCatalog
⋮----
def __init__(self, version, rules)
⋮----
@classmethod
    def from_mapping(cls, payload)
⋮----
rules = payload.get("rules", [])
⋮----
def estimate(self, provider, model, usage, at)
⋮----
when = _dt(at)
⋮----
start = _dt(rule["valid_from"])
end = _dt(rule["valid_to"]) if rule.get("valid_to") else None
⋮----
rates = {
⋮----
cost = sum(
⋮----
def aggregate_usage(rows, *, window, quota_rows=None, now=None)
⋮----
now = _dt(now or datetime.now(timezone.utc))
seconds = WINDOW_SECONDS[window]
cutoff = None if seconds is None else now - timedelta(seconds=seconds)
selected = []
⋮----
occurred = _dt(row.get("occurred_at"))
⋮----
totals = {
breakdown = {}
daily = {}
known_cost = 0.0
any_cost = False
⋮----
key = (str(row.get("provider") or "unknown"), str(row.get("model") or "unknown"))
bucket = breakdown.setdefault(key, {
day = daily.setdefault(occurred.date().isoformat(), {
⋮----
value = row.get(field)
⋮----
cost = row.get("estimated_cost_usd")
⋮----
any_cost = True
⋮----
latest = {}
⋮----
captured = _dt(row.get("captured_at"))
⋮----
provider = str(row["provider"])
⋮----
quotas = []
⋮----
row = latest[provider][1]
```

## File: production_os/database_maintenance_lock.py
```python
except ImportError:  # pragma: no cover - Production-OS servers run on POSIX.
fcntl = None
⋮----
class DatabaseInUseError(RuntimeError)
⋮----
class SQLiteDatabaseProcessLock
⋮----
def __init__(self, database: str)
⋮----
def acquire(self) -> None
⋮----
fd = os.open(
⋮----
owner = self._read_metadata(fd)
suffix = (
⋮----
payload = {
encoded = json.dumps(
⋮----
@staticmethod
    def _read_metadata(fd: int) -> dict
⋮----
raw = os.read(fd, 4096)
payload = json.loads(raw.decode("utf-8")) if raw else {}
⋮----
def release(self) -> None
⋮----
fd = self._fd
⋮----
def __enter__(self)
⋮----
def __exit__(self, exc_type, exc, tb)
⋮----
def database_server_lock(database: str)
```

## File: production_os/deep_fingerprint.py
```python
@dataclass(frozen=True, slots=True)
class SourceSignal
⋮----
kind: str
value: str
confidence: float
evidence: tuple[str, ...]
⋮----
def to_dict(self) -> dict
⋮----
def analyze_source_evidence(e: RepoEvidence) -> list[SourceSignal]
⋮----
signals: list[SourceSignal] = []
combined = "\n".join(e.source_documents.values()).lower()
⋮----
def add(kind: str, value: str, confidence: float, evidence: list[str]) -> None
⋮----
patterns = [
```

## File: production_os/delivery.py
```python
recovered = []
queue = Path(queue_dir)
dead = Path(dead_letter_dir) if dead_letter_dir else None
⋮----
expired = claims.expired_unacked()
⋮----
source_candidates = list(queue.glob(f"{claim.key}*.json"))
⋮----
record = runtime_state.get(claim.repository, claim.task)
⋮----
current = claims.claims.get(claim.key)
⋮----
target = dead / source.name
```

## File: production_os/dispatch.py
```python
@dataclass(frozen=True, slots=True)
class DispatchResult
⋮----
repository: str
task: str
key: str
queue_file: str
lease_owner: str
worker_id: str | None = None
receipt_file: str | None = None
⋮----
def to_dict(self) -> dict
⋮----
repository = str(handoff.get("repository", ""))
task = str(handoff.get("task", ""))
⋮----
policy_decision = evaluate_policy(policy_set or PolicySet({}), handoff)
⋮----
constraints = dict(handoff.get("constraints", {}) or {})
⋮----
handoff = {**handoff, "risk_class": policy_decision.risk_class, "constraints": constraints}
⋮----
resource_request = handoff.get("resource_request", {}) or {}
normalized_request = {
⋮----
budget_decision = budget_ledger.check(
⋮----
portfolio_budgets = {
⋮----
portfolio_budget_decision = budget_ledger.check(
⋮----
worker = None
⋮----
worker = select_worker(
⋮----
repo_decision = rate_limit_store.check_and_record(
⋮----
worker_decision = rate_limit_store.check_and_record(
⋮----
record = runtime_state.get(repository, task)
requires_approval = bool(
⋮----
owner = worker.worker_id if worker is not None else lease_owner
⋮----
worker_incremented = False
destination: Path | None = None
⋮----
worker_incremented = True
⋮----
payload = {
⋮----
destination = Path(f"sqlite-{record.key}")
⋮----
queue = Path(queue_dir)
⋮----
worker_suffix = f".{worker.worker_id}" if worker is not None else ""
destination = queue / f"{record.key}{worker_suffix}.json"
⋮----
receipt_file = None
⋮----
receipt_file = write_dispatch_receipt(
⋮----
latest = runtime_state.get(repository, task)
```

## File: production_os/dual_sign.py
```python
DUAL_SCHEMA = "production-os/validation-attestation-bundle/v1"
⋮----
class DualSignError(ValueError)
⋮----
common = dict(
⋮----
hmac = dict(bundle.get("hmac") or {})
ed25519 = dict(bundle.get("ed25519") or {})
⋮----
kwargs = dict(
⋮----
verified_hmac = verify_v1(
verified_ed25519 = verify_v2(
```

## File: production_os/emergency.py
```python
def set_emergency_stop(path: str | Path, *, reason: str) -> dict
⋮----
payload = {
⋮----
def clear_emergency_stop(path: str | Path) -> dict
⋮----
def emergency_stop_active(path: str | Path | None) -> bool
⋮----
source = Path(path)
⋮----
payload = json.loads(source.read_text(encoding="utf-8"))
```

## File: production_os/execution_feedback.py
```python
@dataclass(frozen=True, slots=True)
class ExecutionDecision
⋮----
decision: str
score_delta: int
validation_status: str
rationale: tuple[str, ...]
⋮----
def to_dict(self) -> dict
⋮----
delta = after_score - before_score
status = str(validation_summary.get("status", "incomplete"))
reasons: list[str] = []
```

## File: production_os/execution_optimizer.py
```python
def _now() -> str
⋮----
def _pg(backend) -> bool
⋮----
def _sql(backend, sql: str) -> str
⋮----
def _execute(db, backend, sql: str, params: tuple = ())
⋮----
@dataclass(frozen=True, slots=True)
class Placement
⋮----
worker_id: str
score: float
predicted_minutes: float
samples: int
⋮----
class ExecutionOptimizer
⋮----
"""Historical runtime learning and deterministic worker placement."""
⋮----
def __init__(self, backend)
⋮----
duration = max(0.001, float(duration_seconds))
now = _now()
⋮----
rows = _execute(
successful = [
⋮----
# Robust trimmed mean: resistant to rare CI/network outliers.
trim = int(len(successful) * 0.1) if len(successful) >= 10 else 0
sample = successful[trim:len(successful)-trim] if trim else successful
predicted = sum(sample) / len(sample) / 60.0
confidence = min(1.0, math.log2(len(successful) + 1) / 5.0)
⋮----
def worker_profiles(self, repository: str, task: str) -> list[dict]
⋮----
result = []
⋮----
samples = int(row["samples"])
successes = int(row["successes"] or 0)
success_rate = successes / samples if samples else 0.0
⋮----
required = set(required_capabilities or [])
eligible = [
⋮----
profiles = {
default_prediction = self.task_prediction(
⋮----
candidates = []
⋮----
profile = profiles.get(worker.worker_id)
⋮----
predicted = profile["avg_minutes"]
reliability = profile["success_rate"]
samples = profile["samples"]
⋮----
predicted = default_prediction
reliability = 0.8
samples = 0
load = worker.active_tasks / max(1, worker.max_concurrency)
# Lower is better. Reliability penalty prevents fast-but-flaky workers.
score = predicted * (1.0 + load) / max(0.1, reliability)
⋮----
now = datetime.now(timezone.utc)
⋮----
claimed_at = datetime.fromisoformat(
runtime_seconds = max(
⋮----
prediction = self.task_prediction(
⋮----
expected_seconds = max(
ratio = runtime_seconds / expected_seconds
⋮----
payload = json.loads(row["payload_json"])
required = [
alternate = None
⋮----
candidates = [
placement = self.choose_worker(
⋮----
alternate = {
⋮----
def workflow_eta(self, workflow: dict) -> dict
⋮----
tasks = {task["task_id"]:task for task in workflow["tasks"]}
memo: dict[str, tuple[float, list[str]]] = {}
⋮----
def duration(task: dict) -> float
⋮----
def longest(task_id: str) -> tuple[float, list[str]]
⋮----
task = tasks[task_id]
weight = duration(task)
deps = task["dependencies"]
⋮----
value = (weight, [task_id])
⋮----
best = max((longest(dep) for dep in deps), key=lambda x:x[0])
value = (best[0] + weight, best[1] + [task_id])
⋮----
best = max((longest(task_id) for task_id in tasks), key=lambda x:x[0])
```

## File: production_os/fairness.py
```python
def round_robin_by_repository(rows: list[tuple]) -> list[tuple]
⋮----
"""Interleave already-ranked rows by repository while preserving per-repo order."""
buckets: dict[str, deque] = defaultdict(deque)
repo_order: list[str] = []
⋮----
action = row[0]
repo = action.repository
⋮----
ordered: list[tuple] = []
remaining = True
⋮----
remaining = False
```

## File: production_os/feedback.py
```python
@dataclass(frozen=True, slots=True)
class ValidationSummary
⋮----
status: str
passed: int
failed: int
pending: int
blocking_failures: tuple[str, ...]
⋮----
def to_dict(self) -> dict
⋮----
by_kind = {
⋮----
passed = 0
failed = 0
pending = 0
blocking: list[str] = []
⋮----
kind = str(step.get("kind"))
required = bool(step.get("required", True))
status = by_kind.get(kind)
⋮----
overall = "blocked"
⋮----
overall = "incomplete"
⋮----
overall = "passed"
```

## File: production_os/github_client.py
```python
class GitHubAPIError(RuntimeError)
⋮----
class GitHubClient
⋮----
API = "https://api.github.com"
⋮----
def __init__(self, token: str | None = None, timeout: float = 20.0)
⋮----
def _headers(self) -> dict[str, str]
⋮----
request = urllib.request.Request(
⋮----
body = response.read()
payload = json.loads(body.decode("utf-8")) if body else None
⋮----
body = exc.read().decode("utf-8", errors="replace")
⋮----
def _get(self, path: str) -> Any
⋮----
def _request(self, method: str, path: str, payload: dict[str, Any] | None = None) -> Any
⋮----
data = None
⋮----
data = json.dumps(payload, separators=(",", ":")).encode("utf-8")
⋮----
def repository(self, full_name: str) -> dict[str, Any]
⋮----
payload = self._get(f"/repos/{full_name}")
⋮----
def default_branch_commit_count(self, full_name: str, branch: str) -> int
⋮----
encoded = urllib.parse.quote(str(branch), safe="")
⋮----
link = headers.get("Link") or headers.get("link") or ""
match = re.search(r"[?&]page=(\d+)>;\s*rel=\"last\"", link)
⋮----
def open_pull_request_count(self, full_name: str) -> int
⋮----
payload = self._get(f"/repos/{full_name}/pulls?state=open&per_page=100")
⋮----
def latest_release(self, full_name: str) -> dict[str, Any] | None
⋮----
payload = self._get(f"/repos/{full_name}/releases/latest")
⋮----
def latest_commit(self, full_name: str, branch: str) -> dict[str, Any] | None
⋮----
payload = self._get(f"/repos/{full_name}/commits?sha={encoded}&per_page=1")
⋮----
def latest_ci_status(self, full_name: str, branch: str) -> str | None
⋮----
run = self._latest_workflow_run(full_name, branch)
⋮----
ref_name = branch.removeprefix("refs/heads/")
ref = self._get(
base_commit_sha = str(ref.get("object", {}).get("sha") or "")
⋮----
base_commit = self._get(f"/repos/{full_name}/git/commits/{base_commit_sha}")
base_tree_sha = str(base_commit.get("tree", {}).get("sha") or "")
⋮----
tree = []
⋮----
normalized = path.strip().replace("\\", "/").lstrip("/")
⋮----
blob = self._request(
blob_sha = str(blob.get("sha") or "") if isinstance(blob, dict) else ""
⋮----
created_tree = self._request(
tree_sha = str(created_tree.get("sha") or "") if isinstance(created_tree, dict) else ""
⋮----
created_commit = self._request(
commit_sha = str(created_commit.get("sha") or "") if isinstance(created_commit, dict) else ""
⋮----
encoded_path = "/".join(
⋮----
existing = None
⋮----
existing = self._get(
⋮----
payload: dict[str, Any] = {
⋮----
result = self._request(
⋮----
encoded = urllib.parse.quote(workflow, safe="")
⋮----
payload = self._get(
runs = payload.get("workflow_runs", []) if isinstance(payload, dict) else []
⋮----
deadline = clock() + float(timeout_seconds)
⋮----
status = str(run.get("status") or "")
⋮----
artifacts = payload.get("artifacts", []) if isinstance(payload, dict) else []
⋮----
class StripCredentialRedirect(urllib.request.HTTPRedirectHandler)
⋮----
def redirect_request(self, req, fp, code, msg, headers, newurl)
⋮----
redirected = super().redirect_request(
⋮----
data = response.read(max_bytes + 1)
⋮----
encoded = urllib.parse.quote(branch, safe="")
⋮----
def get_issue(self, full_name: str, issue_number: int) -> dict[str, Any] | None
⋮----
payload = self._get(f"/repos/{full_name}/issues/{issue_number}")
⋮----
def get_pull_request(self, full_name: str, pr_number: int) -> dict[str, Any] | None
⋮----
payload = self._get(f"/repos/{full_name}/pulls/{pr_number}")
⋮----
def get_pull_request_reviews(self, full_name: str, pr_number: int) -> list[dict[str, Any]]
⋮----
payload = self._get(f"/repos/{full_name}/pulls/{pr_number}/reviews")
⋮----
"""Return every changed path in a pull request.

        Unlike informational GitHub reads, this method intentionally propagates
        API failures. Incremental pruning must fail closed when the changed-file
        set cannot be established reliably.
        """
files: list[str] = []
page = 1
⋮----
filename = str(item.get("filename") or "").strip()
⋮----
def get_commit_workflow_runs(self, full_name: str, commit_sha: str) -> list[dict[str, Any]]
⋮----
runs = payload.get("workflow_runs", [])
⋮----
def list_accessible_repositories(self, owner: str) -> list[dict[str, Any]]
⋮----
owner = str(owner or "").strip()
⋮----
repos: list[dict[str, Any]] = []
⋮----
def list_repositories(self, owner: str) -> list[dict[str, Any]]
⋮----
def _contents(self, full_name: str, path: str = "") -> list[dict[str, Any]]
⋮----
encoded_path = "/".join(urllib.parse.quote(part) for part in path.split("/") if part)
suffix = f"/{encoded_path}" if encoded_path else ""
⋮----
payload = self._get(f"/repos/{full_name}/contents{suffix}")
⋮----
def _read_text(self, full_name: str, path: str) -> str
⋮----
payload = self._get(f"/repos/{full_name}/contents/{encoded_path}")
⋮----
encoded = payload.get("content")
⋮----
def read_json_file(self, full_name: str, path: str) -> dict[str, Any] | None
⋮----
text = self._read_text(full_name, path)
⋮----
value = json.loads(text)
⋮----
def _latest_workflow_run(self, full_name: str, branch: str) -> dict[str, Any] | None
⋮----
def _recursive_tree_paths(self, full_name: str, ref: str) -> list[str]
⋮----
tree = payload.get("tree", []) if isinstance(payload, dict) else []
⋮----
policy = policy or TreeSamplePolicy()
candidates = [
docs: dict[str, str] = {}
⋮----
path = f".github/workflows/{workflow}"
⋮----
tree_paths = self._recursive_tree_paths(full_name, default_branch)
nested = [
⋮----
remaining = max(policy.max_files - len(docs), 0)
⋮----
def collect_evidence(self, repo: dict[str, Any]) -> RepoEvidence
⋮----
full_name = repo["full_name"]
default_branch = repo.get("default_branch") or "main"
root = self._contents(full_name)
names = {item.get("name", "") for item in root}
lower = {name.lower() for name in names}
⋮----
workflow_entries = self._contents(full_name, ".github/workflows")
workflow_names = sorted(
workflow_lower = {name.lower() for name in workflow_names}
github_entries = self._contents(full_name, ".github")
github_names = {item.get("name", "").lower() for item in github_entries}
latest_run = self._latest_workflow_run(full_name, default_branch) if workflow_names else None
⋮----
readme_name = next((n for n in names if n.lower().startswith("readme")), "")
readme = self._read_text(full_name, readme_name) if readme_name else ""
readme_lower = readme.lower()
source_documents = self._collect_source_documents(
⋮----
manifest_names = {
all_source_paths = {path.lower() for path in source_documents}
has_tests = (
release_words = ("release", "publish", "deploy", "play", "store")
roadmap_words = ("roadmap", "todo", "milestone")
```

## File: production_os/github_webhook.py
```python
SUPPORTED_PULL_REQUEST_ACTIONS = {
⋮----
class WebhookError(ValueError)
⋮----
prefix = "sha256="
⋮----
expected = hmac.new(
supplied = signature_header[len(prefix):]
⋮----
def parse_github_webhook(body: bytes) -> dict[str, Any]
⋮----
payload = json.loads(body.decode("utf-8"))
⋮----
action = str(payload.get("action") or "")
⋮----
repository = payload.get("repository")
pull_request = payload.get("pull_request")
⋮----
full_name = str(repository.get("full_name") or "").strip()
number = pull_request.get("number", payload.get("number"))
head = pull_request.get("head")
head_sha = (
⋮----
pr_number = int(number)
⋮----
class WebhookDeliveryStore
⋮----
def __init__(self, backend)
⋮----
delivery_id = str(delivery_id or "").strip()
⋮----
received_at = datetime.now(timezone.utc).isoformat()
⋮----
cursor = db.execute(
⋮----
def release(self, delivery_id: str) -> None
```

## File: production_os/github_work_state.py
```python
@dataclass(frozen=True, slots=True)
class GitHubWorkState
⋮----
repository: str
issue_number: int | None
pr_number: int | None
issue_state: str | None
pr_state: str | None
merged: bool
draft: bool
review_state: str | None
ci_state: str | None
head_sha: str | None
⋮----
def to_dict(self) -> dict
⋮----
def _review_state(reviews: list[dict[str, Any]]) -> str | None
⋮----
states = [str(r.get("state", "")).upper() for r in reviews]
⋮----
def _ci_state(runs: list[dict[str, Any]]) -> str | None
⋮----
conclusions = [str(r.get("conclusion") or "").lower() for r in runs]
statuses = [str(r.get("status") or "").lower() for r in runs]
⋮----
issue_state = None
pr_state = None
merged = False
draft = False
review_state = None
ci_state = None
head_sha = None
⋮----
issue = client.get_issue(repository, issue_number)
issue_state = str(issue.get("state")) if issue else None
⋮----
pr = client.get_pull_request(repository, pr_number)
⋮----
pr_state = str(pr.get("state")) if pr.get("state") is not None else None
merged = bool(pr.get("merged") or pr.get("merged_at"))
draft = bool(pr.get("draft"))
head = pr.get("head") or {}
head_sha = head.get("sha") if isinstance(head, dict) else None
⋮----
reviews = client.get_pull_request_reviews(repository, pr_number)
review_state = _review_state(reviews)
⋮----
runs = client.get_commit_workflow_runs(repository, head_sha)
ci_state = _ci_state(runs)
⋮----
def runtime_decision_from_github(state: GitHubWorkState) -> str
```

## File: production_os/governance.py
```python
@dataclass(frozen=True, slots=True)
class GovernanceAction
⋮----
repository: str
action: str
reason: str
⋮----
def to_dict(self) -> dict
⋮----
by_repo: dict[str, list] = {}
⋮----
actions: list[GovernanceAction] = []
⋮----
policy = policy_set.merged_for(repository)
threshold = int(policy.get("auto_quarantine_after_failures", 0) or 0)
slo = policy.get("slo", {}) or {}
⋮----
failures = max(
circuit_open = any(r.status == "circuit-open" for r in records)
⋮----
violations: list[str] = []
⋮----
max_attempts = int(slo.get("max_attempts", 0) or 0)
⋮----
attempts = max([int(r.attempts or 0) for r in records] or [0])
⋮----
max_failures = int(slo.get("max_consecutive_failures", 0) or 0)
⋮----
max_runtime = float(slo.get("max_runtime_minutes", 0) or 0)
⋮----
now = datetime.now(timezone.utc)
⋮----
started = datetime.fromisoformat(
runtime_minutes = (now - started).total_seconds() / 60.0
⋮----
reason = "; ".join(violations)
```

## File: production_os/graph.py
```python
@dataclass(frozen=True, slots=True)
class GraphEdge
⋮----
source: str
relation: str
target: str
confidence: float = 1.0
⋮----
def to_dict(self) -> dict
⋮----
def build_knowledge_graph(assessments: list[RepoAssessment]) -> dict
⋮----
nodes: dict[str, dict] = {}
edges: list[GraphEdge] = []
⋮----
repo_id = f"repo:{assessment.evidence.full_name}"
⋮----
profile_id = f"profile:{assessment.profile}"
⋮----
cap_id = f"capability:{capability.name}"
⋮----
component_lookup: dict[str, str] = {}
⋮----
component_id = (
⋮----
cap_id = f"capability:{capability}"
⋮----
dep_id = f"dependency:{dependency}"
⋮----
call_graph = build_call_import_graph(assessment)
⋮----
source_id = component_lookup.get(call["source_component"])
⋮----
symbol_id = f"symbol:{assessment.evidence.full_name}:{call['target_symbol']}"
```

## File: production_os/health_server.py
```python
class _Handler(BaseHTTPRequestHandler)
⋮----
health_path: Path
⋮----
def do_GET(self) -> None
⋮----
payload = {"status":"unknown","reason":"health file not found"}
body = json.dumps(payload).encode("utf-8")
⋮----
body = self.health_path.read_bytes()
⋮----
payload = json.loads(body.decode("utf-8"))
code = 200 if payload.get("status") == "healthy" else 503
⋮----
code = 503
⋮----
def log_message(self, format: str, *args) -> None
⋮----
handler = type(
server = ThreadingHTTPServer((host, port), handler)
```

## File: production_os/health.py
```python
def build_health(runtime_state: RuntimeState, metrics: dict) -> dict
⋮----
records = list(runtime_state.records.values())
running = sum(1 for r in records if r.status == "running")
circuits = sum(1 for r in records if r.status == "circuit-open")
failed = sum(1 for r in records if r.status == "failed")
status = "healthy"
⋮----
status = "degraded"
⋮----
def write_health(payload: dict, path: str | Path) -> None
⋮----
destination = Path(path)
```

## File: production_os/heartbeat_manager.py
```python
@dataclass(frozen=True, slots=True)
class HeartbeatResult
⋮----
repository: str
task: str
renewed: bool
owner: str | None
⋮----
def to_dict(self) -> dict
⋮----
results: list[HeartbeatResult] = []
```

## File: production_os/history.py
```python
@dataclass(frozen=True, slots=True)
class Regression
⋮----
repository: str
previous_score: int
current_score: int
delta: int
⋮----
def build_snapshot(owner: str, assessments: Iterable[RepoAssessment]) -> dict
⋮----
repos = {}
⋮----
def save_snapshot(snapshot: dict, path: str | Path) -> None
⋮----
destination = Path(path)
⋮----
def load_snapshot(path: str | Path) -> dict | None
⋮----
source = Path(path)
⋮----
def detect_regressions(previous: dict | None, current: dict, threshold: int = 5) -> list[Regression]
⋮----
regressions: list[Regression] = []
old_repos = previous.get("repositories", {})
⋮----
before = old_repos.get(name)
⋮----
old_score = int(before.get("score", 0))
new_score = int(now.get("score", 0))
delta = new_score - old_score
```

## File: production_os/journal.py
```python
class ExecutionJournal
⋮----
def __init__(self, path: str | Path)
⋮----
def _head_hash_unlocked(self) -> str
⋮----
head = "0" * 64
⋮----
row = json.loads(line)
⋮----
head = str(row["event_hash"])
⋮----
def append(self, event: dict) -> None
⋮----
payload = {
⋮----
previous_hash = self._head_hash_unlocked()
event_hash = hash_event(previous_hash, payload)
row = {
⋮----
def read(self) -> list[dict]
⋮----
rows = []
⋮----
line = line.strip()
⋮----
payload = json.loads(line)
```

## File: production_os/key_domains.py
```python
class KeyDomainError(ValueError)
⋮----
def private_key_id(private_key_pem: str | None) -> str | None
⋮----
private_key = load_private_key(private_key_pem)
⋮----
def registry_key_ids(entries: dict[str, Any] | None) -> set[str]
⋮----
registry = TrustedKeyRegistry(dict(entries or {}))
⋮----
domains: dict[str, set[str]] = {
⋮----
value = private_key_id(pem)
⋮----
owners: dict[str, str] = {}
⋮----
previous = owners.get(value)
```

## File: production_os/key_registry.py
```python
class KeyRegistryError(ValueError)
⋮----
def _parse_time(value: str | None) -> datetime | None
⋮----
parsed = datetime.fromisoformat(
⋮----
@dataclass(frozen=True)
class TrustedKey
⋮----
owner: str
public_key: str
key_id: str
not_before: datetime | None = None
not_after: datetime | None = None
revoked_at: datetime | None = None
compromised: bool = False
⋮----
public_key = str(payload.get("public_key") or "")
⋮----
computed = key_id(load_public_key(public_key))
supplied = str(payload.get("key_id") or computed)
⋮----
not_before = _parse_time(payload.get("not_before"))
not_after = _parse_time(payload.get("not_after"))
revoked_at = _parse_time(payload.get("revoked_at"))
compromised = bool(payload.get("compromised", False))
⋮----
def usable_at(self, when: datetime) -> tuple[bool, str | None]
⋮----
class TrustedKeyRegistry
⋮----
def __init__(self, entries: dict[str, Any] | None = None)
⋮----
rows = value if isinstance(value, list) else [value]
⋮----
row = {"public_key":row}
⋮----
item = TrustedKey.from_dict(str(owner), row)
owner_keys = self.by_owner.setdefault(
⋮----
item = self.by_owner.get(str(owner), {}).get(
⋮----
when = _parse_time(signed_at)
```

## File: production_os/learning.py
```python
@dataclass(frozen=True, slots=True)
class LearningSignal
⋮----
repository: str
task: str
executions: int
promotions: int
retries: int
rollbacks: int
replans: int
cumulative_delta: int
average_delta: float
success_rate: float
weight: float
⋮----
def to_dict(self) -> dict
⋮----
def build_learning_signals(events: list[dict]) -> list[LearningSignal]
⋮----
grouped: dict[tuple[str, str], list[dict]] = {}
⋮----
repo = str(event.get("repository", ""))
task = str(event.get("task", ""))
⋮----
signals: list[LearningSignal] = []
⋮----
promotions = sum(1 for r in rows if r.get("decision") == "promote")
retries = sum(1 for r in rows if r.get("decision") == "retry")
rollbacks = sum(1 for r in rows if r.get("decision") == "rollback")
replans = sum(1 for r in rows if r.get("decision") == "replan")
deltas = [int(r.get("score_delta", 0)) for r in rows]
executions = len(rows)
cumulative = sum(deltas)
avg = round(cumulative / executions, 2) if executions else 0.0
success = round(promotions / executions, 3) if executions else 0.0
⋮----
weight = (
weight = round(max(-25.0, min(25.0, weight)), 2)
⋮----
def learning_weight(signals: list[LearningSignal], repository: str, task: str) -> float
⋮----
exact = next((s for s in signals if s.repository == repository and s.task == task), None)
⋮----
repo_rows = [s for s in signals if s.repository == repository]
```

## File: production_os/locks.py
```python
class FileLock
⋮----
def acquire(self) -> None
⋮----
deadline = time.monotonic() + self.timeout_seconds
⋮----
fd = os.open(
payload = {
⋮----
age = time.time() - self.path.stat().st_mtime
⋮----
def release(self) -> None
⋮----
def __enter__(self)
⋮----
def __exit__(self, exc_type, exc, tb)
⋮----
def sidecar_lock(path: str | Path) -> FileLock
⋮----
target = Path(path)
```

## File: production_os/managed_projects.py
```python
MANAGED_PROJECT_SCHEMA = "production-os/managed-project/v3"
LEGACY_MANAGED_PROJECT_SCHEMA = "production-os/managed-project/v2"
ACTIVE = "ACTIVE"
REVIEW_REQUIRED = "REVIEW_REQUIRED"
NEEDS_ATTENTION = "NEEDS_ATTENTION"
DONE = "DONE"
PROJECT_STATES = {ACTIVE, REVIEW_REQUIRED, NEEDS_ATTENTION, DONE}
USAGE_KEYS = (
⋮----
def _now() -> str
⋮----
def _positive_int(value, *, field: str) -> int
⋮----
number = int(value)
⋮----
def _usage_from_result(result: dict | None) -> dict
⋮----
candidates = [result.get("usage")]
evidence = result.get("evidence")
⋮----
usage = next((item for item in candidates if isinstance(item, dict)), None)
⋮----
normalized: dict = {}
⋮----
value = usage.get(key)
⋮----
runs = usage.get("runs")
⋮----
run_count = int(runs)
⋮----
run_count = 0
⋮----
agents = usage.get("agents")
⋮----
clean = {}
⋮----
value = int(count)
⋮----
def _clean_commit_shas(values) -> list[str]
⋮----
clean: list[str] = []
⋮----
value = (
⋮----
def _outcome_from_workflow(workflow: dict | None) -> dict
⋮----
results = [
result = results[-1] if results else {}
evidence = (
summary = (
summary = str(summary).strip() if summary is not None else None
⋮----
summary = None
⋮----
validation = result.get("validation")
⋮----
validation = evidence.get("validation")
⋮----
validation = {}
validation_status = (
⋮----
raw_tests = (
validation_tests = (
⋮----
raw_commits = (
⋮----
raw_commits = [raw_commits]
commit_shas = _clean_commit_shas(raw_commits)
⋮----
artifacts = [
artifact_names = [
⋮----
changed_files = (
changed_file_count = (
⋮----
pr = result.get("pull_request") or evidence.get("pull_request")
pull_request = None
⋮----
number = pr.get("number")
state = str(pr.get("state") or "").strip() or None
⋮----
number = (
state = (
⋮----
number = int(number) if number is not None else None
⋮----
number = None
⋮----
pull_request = {"number":number, "state":state}
⋮----
workflow_status = str(workflow.get("status") or "").strip() or None
terminal = workflow_status in {"succeeded", "failed", "cancelled"}
available = terminal or any((
⋮----
class ManagedProjectService
⋮----
def __init__(self, workflows: WorkflowEngine)
⋮----
@staticmethod
    def _validate_repository(repository: str) -> str
⋮----
repository = str(repository or "").strip()
parts = repository.split("/")
⋮----
workflow = self.workflows.create(
⋮----
def _delete_unstarted_workflow(self, workflow_id: str) -> None
⋮----
repository = self._validate_repository(repository)
final_goal = str(final_goal or "").strip()
⋮----
budget = _positive_int(token_budget, field="token_budget")
agent = str(agent_preference or "auto").strip() or "auto"
actor = str(requested_by or "operator").strip() or "operator"
⋮----
project_id = uuid4().hex
⋮----
project_id = str(project_id or "").strip()
⋮----
now = _now()
⋮----
inserted = _execute(
created_row = inserted.rowcount == 1
⋮----
existing = _execute(
⋮----
matches = (
⋮----
workflow = self._create_workflow(
⋮----
def _resolve_project_id(self, identifier: str) -> str
⋮----
identifier = str(identifier)
⋮----
row = _execute(
⋮----
migrated = self._migrate_legacy_workflow(identifier)
⋮----
def _migrate_legacy_workflow(self, workflow_id: str) -> str | None
⋮----
workflow = self.workflows.get(workflow_id)
⋮----
metadata = dict(workflow.get("metadata") or {})
legacy = metadata.get("managed_project")
⋮----
final_goal = str(legacy.get("final_goal") or "")
budget = _positive_int(
agent = str(legacy.get("agent_preference") or "auto")
human_state = str(legacy.get("human_state") or "active")
⋮----
status = DONE
completed_at = legacy.get("approved_at") or now
completed_by = legacy.get("approved_by")
⋮----
status = REVIEW_REQUIRED
completed_at = None
completed_by = None
⋮----
status = NEEDS_ATTENTION
⋮----
status = ACTIVE
⋮----
def reconcile(self, identifier: str) -> dict
⋮----
project_id = self._resolve_project_id(identifier)
⋮----
project = _execute(
⋮----
current = dict(project)
⋮----
workflow_id = current.get("current_workflow_id")
⋮----
target = NEEDS_ATTENTION
⋮----
workflow = self.workflows.get(str(workflow_id))
⋮----
workflow_status = workflow.get("status")
⋮----
target = REVIEW_REQUIRED
⋮----
target = ACTIVE
⋮----
def _usage(self, runs: list[dict]) -> dict
⋮----
usage = {
⋮----
workflow = self.workflows.get(str(run["workflow_id"]))
⋮----
item = _usage_from_result(task.get("result"))
⋮----
value = item.get(key)
⋮----
def get(self, identifier: str) -> dict
⋮----
project = self.reconcile(identifier)
project_id = str(project["id"])
⋮----
run_rows = _execute(
runs = [dict(row) for row in run_rows]
current_workflow = None
⋮----
current_workflow = self.workflows.get(
⋮----
usage = self._usage(runs)
display_state = (
⋮----
def list(self, *, limit: int = 100) -> list[dict]
⋮----
bounded = max(1, min(500, int(limit)))
⋮----
rows = _execute(
⋮----
legacy_rows = _execute(
⋮----
current = self.get(identifier)
⋮----
instruction = str(instruction or "").strip()
⋮----
project_id = current["project_id"]
generation = int(current["generation"]) + 1
⋮----
updated = _execute(
⋮----
instruction = (
⋮----
actor = str(approved_by or "operator").strip() or "operator"
```

## File: production_os/metrics.py
```python
@dataclass(slots=True)
class ControlMetrics
⋮----
cycles: int = 0
scans: int = 0
dispatched: int = 0
dispatch_failures: int = 0
reconciliations: int = 0
github_reconciliations: int = 0
self_healing_actions: int = 0
heartbeats_renewed: int = 0
last_cycle_at: str | None = None
last_error: str | None = None
⋮----
def to_dict(self) -> dict
⋮----
class MetricsStore
⋮----
def __init__(self, path: str | Path)
⋮----
def load(self) -> None
⋮----
payload = json.loads(self.path.read_text(encoding="utf-8"))
data = payload.get("metrics", payload)
⋮----
def save(self) -> None
```

## File: production_os/migration_registry.py
```python
@dataclass(frozen=True, slots=True)
class MigrationResult
⋮----
path: str
migrated: bool
source_schema: str
target_schema: str
⋮----
def to_dict(self) -> dict
⋮----
def migrate_many(paths: list[str]) -> list[MigrationResult]
⋮----
results = []
⋮----
result = migrate_state_file(raw)
```

## File: production_os/migrations.py
```python
def migrate_state_file(path: str | Path) -> dict
⋮----
source = Path(path)
⋮----
payload = json.loads(source.read_text(encoding="utf-8"))
schema = str(payload.get("schema_version", ""))
```

## File: production_os/models.py
```python
@dataclass(slots=True)
class RepoEvidence
⋮----
name: str
full_name: str
html_url: str
default_branch: str = "main"
archived: bool = False
fork: bool = False
private: bool = False
language: str | None = None
stars: int = 0
forks: int = 0
open_issues: int = 0
pushed_at: str | None = None
has_readme: bool = False
has_tests: bool = False
has_ci: bool = False
latest_ci_status: str | None = None
latest_ci_conclusion: str | None = None
latest_ci_url: str | None = None
has_release_workflow: bool = False
has_manifest: bool = False
has_license: bool = False
has_security_policy: bool = False
has_dependency_automation: bool = False
has_roadmap: bool = False
readme_text: str = ""
detected_files: list[str] = field(default_factory=list)
workflow_names: list[str] = field(default_factory=list)
source_documents: dict[str, str] = field(default_factory=dict)
⋮----
def to_dict(self) -> dict[str, Any]
⋮----
@dataclass(slots=True)
class ScoreBreakdown
⋮----
total: int
documentation: int
tests: int
ci: int
release: int
build: int
security: int
license: int
activity: int
⋮----
def to_dict(self) -> dict[str, int]
⋮----
@dataclass(slots=True)
class ActionCandidate
⋮----
repository: str
task: str
rationale: str
acceptance_criteria: list[str]
evidence: list[str]
impact: int
urgency: int
risk_reduction: int
release_proximity: int
effort: int
priority: float = 0.0
⋮----
def compute_priority(self) -> float
⋮----
value = (
⋮----
@dataclass(slots=True)
class RepoAssessment
⋮----
evidence: RepoEvidence
score: ScoreBreakdown
actions: list[ActionCandidate]
profile: str = "generic"
profile_confidence: float = 0.0
profile_signals: list[str] = field(default_factory=list)
capabilities: list[Any] = field(default_factory=list)
source_signals: list[Any] = field(default_factory=list)
components: list[Any] = field(default_factory=list)
```

## File: production_os/observability.py
```python
def write_observability(payload: dict, path: str | Path) -> None
⋮----
destination = Path(path)
```

## File: production_os/policy_validation.py
```python
@dataclass(frozen=True, slots=True)
class PolicyValidation
⋮----
valid: bool
errors: tuple[str, ...]
⋮----
def to_dict(self) -> dict
⋮----
def validate_policy_payload(payload: dict) -> PolicyValidation
⋮----
errors: list[str] = []
⋮----
def validate_scope(scope: dict, label: str) -> None
⋮----
max_risk = scope.get("max_risk_class")
⋮----
approval = scope.get("approval_required_from")
⋮----
budgets = scope.get("budgets", {}) or {}
⋮----
value = str(freeze.get(key, ""))
⋮----
slo = scope.get("slo", {}) or {}
⋮----
value = slo[key]
⋮----
defaults = payload.get("defaults", {}) or {}
⋮----
repositories = payload.get("repositories", []) or []
⋮----
portfolio = payload.get("portfolio_budgets", {}) or {}
```

## File: production_os/policy.py
```python
RISK_ORDER = {"low":0, "medium":1, "high":2, "critical":3}
⋮----
@dataclass(frozen=True, slots=True)
class PolicyDecision
⋮----
allowed: bool
risk_class: str
requires_approval: bool
quarantined: bool
reasons: tuple[str, ...]
allowed_worker_classes: tuple[str, ...]
budgets: dict[str, float]
⋮----
def to_dict(self) -> dict
⋮----
class PolicySet
⋮----
def __init__(self, payload: dict[str, Any])
⋮----
@classmethod
    def load(cls, path: str | Path | None) -> "PolicySet"
⋮----
source = Path(path)
⋮----
def merged_for(self, repository: str) -> dict[str, Any]
⋮----
result = dict(self.payload.get("defaults", {}))
⋮----
pattern = str(rule.get("match", ""))
⋮----
def classify_risk(handoff: dict) -> str
⋮----
explicit = handoff.get("risk_class")
⋮----
task = str(handoff.get("task", "")).lower()
constraints = handoff.get("constraints", {}) or {}
⋮----
def _freeze_active(policy: dict[str, Any], now: datetime) -> bool
⋮----
freezes = policy.get("freeze_windows", [])
timezone_name = str(policy.get("freeze_timezone", "UTC"))
⋮----
local_now = now.astimezone(ZoneInfo(timezone_name))
⋮----
local_now = now
weekday = local_now.strftime("%a").lower()[:3]
hhmm = local_now.strftime("%H:%M")
⋮----
days = [str(x).lower()[:3] for x in freeze.get("days", [])]
⋮----
start = str(freeze.get("start", "00:00"))
end = str(freeze.get("end", "23:59"))
⋮----
now = now or datetime.now(timezone.utc)
repository = str(handoff.get("repository", ""))
policy = policy_set.merged_for(repository)
risk = classify_risk(handoff)
reasons: list[str] = []
allowed = True
quarantined = False
⋮----
allowed = False
⋮----
max_risk = str(policy.get("max_risk_class", "critical"))
⋮----
protected_for = set(
⋮----
quarantine = policy.get("quarantine", {}) or {}
⋮----
quarantined = True
⋮----
approval_from = str(policy.get("approval_required_from", "critical"))
requires_approval = (
⋮----
allowed_workers = tuple(
budgets = {
```

## File: production_os/portfolio_optimizer.py
```python
class PortfolioOptimizer
⋮----
def __init__(self, workflow_engine, execution_optimizer)
⋮----
@staticmethod
    def _descendant_counts(workflow: dict) -> dict[str, int]
⋮----
children: dict[str, set[str]] = {
⋮----
memo: dict[str, set[str]] = {}
⋮----
def descendants(task_id: str) -> set[str]
⋮----
result: set[str] = set()
⋮----
def rank(self, jobs: list[dict]) -> list[dict]
⋮----
now = datetime.now(timezone.utc)
workflow_cache: dict[str, dict] = {}
critical_cache: dict[str, set[str]] = {}
descendants_cache: dict[str, dict[str, int]] = {}
ranked: list[dict] = []
⋮----
payload = job.get("payload", {})
workflow_id = payload.get("workflow_id")
workflow_task_id = payload.get("workflow_task_id")
⋮----
critical = False
descendant_count = 0
⋮----
workflow_id = str(workflow_id)
⋮----
workflow = self.workflows.get(workflow_id)
⋮----
eta = self.execution.workflow_eta(workflow)
⋮----
critical = str(workflow_task_id) in critical_cache[
descendant_count = descendants_cache[
⋮----
prediction = self.execution.task_prediction(
⋮----
created_at = datetime.fromisoformat(
age_minutes = max(
predicted_minutes = float(
⋮----
score = (
```

## File: production_os/postgres_backend.py
```python
psycopg = None
dict_row = None
⋮----
def _utcnow() -> str
⋮----
class PostgresBackend
⋮----
SCHEMA_VERSION = 15
⋮----
def __init__(self, dsn: str)
⋮----
def connect(self)
⋮----
@contextmanager
    def transaction(self, *, immediate: bool = True) -> Iterator
⋮----
connection = psycopg.connect(
⋮----
def initialize(self) -> None
⋮----
row = cur.fetchone()
⋮----
def events_after(self, event_id: int = 0, limit: int = 100) -> list[dict]
⋮----
rows = cur.fetchall()
⋮----
class PostgresRuntimeState
⋮----
def __init__(self, backend: PostgresBackend)
⋮----
@staticmethod
    def _row(row: dict) -> RuntimeRecord
⋮----
def load(self) -> None
⋮----
def save(self) -> None
⋮----
@staticmethod
    def _parse(ts: str | None) -> datetime | None
⋮----
def is_leased(self, record: RuntimeRecord, now: datetime | None = None) -> bool
⋮----
now = now or datetime.now(timezone.utc)
expires = self._parse(record.lease_expires_at)
⋮----
def in_cooldown(self, record: RuntimeRecord, now: datetime | None = None) -> bool
⋮----
until = self._parse(record.cooldown_until)
⋮----
def get(self, repository: str, task: str) -> RuntimeRecord
⋮----
key = task_key(repository, task)
⋮----
record = self._row(row)
⋮----
now = datetime.now(timezone.utc)
expires = (now + timedelta(minutes=minutes)).isoformat()
⋮----
current = self._row(row)
⋮----
def release_lease(self, repository: str, task: str) -> RuntimeRecord
⋮----
now = _utcnow()
⋮----
status = (
⋮----
current = self.get(repository, task)
⋮----
attempts = current.attempts + 1
failures = current.consecutive_failures
status = "idle"
cooldown = current.cooldown_until
⋮----
status = "succeeded"
failures = 0
cooldown = None
⋮----
status = "failed"
⋮----
status = "circuit-open"
cooldown = (
⋮----
status = "replan"
⋮----
class PostgresWorkerRegistry
⋮----
@staticmethod
    def _row(row: dict) -> Worker
⋮----
worker = self._row(row)
⋮----
def heartbeat(self, worker_id: str, active_tasks: int | None = None) -> Worker
⋮----
active = (
⋮----
def adjust_active_tasks(self, worker_id: str, delta: int) -> Worker
⋮----
active = max(0, int(row["active_tasks"]) + int(delta))
⋮----
def detect_dead(self, timeout_seconds: int = 120) -> list[Worker]
⋮----
dead = []
⋮----
stale = True
⋮----
seen = datetime.fromisoformat(
stale = (now - seen).total_seconds() > timeout_seconds
⋮----
def available(self) -> list[Worker]
⋮----
class PostgresClaimStore
⋮----
@staticmethod
    def _row(row: dict) -> ClaimRecord
⋮----
deadline = (
⋮----
claim = self._row(row)
⋮----
def ack(self, key: str, worker_id: str) -> ClaimRecord
⋮----
def complete(self, key: str, worker_id: str) -> ClaimRecord
⋮----
def expired_unacked(self) -> list[ClaimRecord]
⋮----
class PostgresJobQueue
⋮----
@staticmethod
    def _job_dict(row: dict) -> dict
⋮----
def enqueue(self, payload: dict) -> dict
⋮----
handoff = payload.get("handoff", payload)
repository = str(handoff.get("repository", ""))
task = str(handoff.get("task", ""))
⋮----
key = str(payload.get("idempotency_key") or task_key(repository, task))
priority = float(handoff.get("priority", 0.0))
⋮----
normalized = {
⋮----
existing = cur.fetchone()
⋮----
def get(self, key: str) -> dict
⋮----
claimed = cur.fetchone()
⋮----
capabilities_set = set(capabilities or [])
⋮----
chosen = None
⋮----
payload = json.loads(row["payload_json"])
required = set(payload.get("required_capabilities", []))
⋮----
chosen = row
⋮----
def ack(self, key: str, worker_id: str) -> dict
⋮----
def complete(self, key: str, worker_id: str) -> dict
⋮----
def fail(self, key: str, worker_id: str, reason: str) -> dict
⋮----
def cancel_queued(self, key: str, reason: str = "operator cancel") -> dict
⋮----
def cancel(self, key: str, worker_id: str, reason: str = "operator cancel") -> dict
⋮----
def recover_job(self, key: str, *, max_attempts: int = 3) -> dict
⋮----
target = (
⋮----
action = {
⋮----
updated = cur.fetchone()
⋮----
def recover_expired(self, *, max_attempts: int = 3) -> list[dict]
⋮----
actions = []
```

## File: production_os/preemption.py
```python
@dataclass(frozen=True, slots=True)
class PreemptionDecision
⋮----
should_preempt: bool
victim_repository: str | None
victim_task: str | None
victim_worker: str | None
reason: str
⋮----
def to_dict(self) -> dict
⋮----
capable_workers = [
⋮----
candidates = []
⋮----
worker = workers.workers.get(record.lease_owner)
⋮----
current_priority = float(record.priority or 0.0)
gap = incoming_priority - current_priority
⋮----
victim = candidates[0][-1]
⋮----
record = runtime_state.get(repository, task)
```

## File: production_os/project_progress.py
```python
PROFILES = {
DIMENSIONS=("code","ui_ux","assets","tests","stability","release")
CALCULATION_VERSION="project-progress/v1"
CONFIDENCE_HIGH=.80
CONFIDENCE_MEDIUM=.50
_COMPLETE={"succeeded","impact_skipped"}
⋮----
def workflow_progress(workflow: dict) -> dict
⋮----
tasks=workflow.get("tasks") or []
total=0.0; completed=0.0
⋮----
try: weight=max(0.0,float(task.get("estimated_minutes") or 0))
except (TypeError,ValueError): weight=0.0
⋮----
def _execution_summary(rows)
⋮----
total=len(rows); succeeded=sum(str(x.get("status"))=="succeeded" for x in rows)
⋮----
def _relevant_progress_events(rows)
⋮----
def build_project_evidence(*,workflow,repository_snapshot,executions,events,visual_quality)
⋮----
executions=executions or []
out={"dimensions":{},"remaining_work":[],"blockers":[],
⋮----
progress=workflow_progress(workflow)
⋮----
repository={k:repository_snapshot.get(k) for k in
⋮----
passing=repository.get("tests_passing")
failing=repository.get("tests_failing")
⋮----
test_score=round(float(passing)/(float(passing)+float(failing))*100,2)
⋮----
ci_status=str(repository.get("ci_status") or "").lower()
⋮----
summary=out["execution_summary"]
⋮----
score=visual_quality.get("score")
⋮----
class ProjectProgressEngine
⋮----
def calculate(self,repository: str,evidence: dict,*,captured_at: str|None=None)->dict
⋮----
profile=str(evidence.get("profile") or "generic")
weights=PROFILES.get(profile,PROFILES["generic"])
supplied=evidence.get("dimensions") or {}
components={}
weighted=0.0; known_weight=0.0; fresh_weight=0.0
stale_critical=False
⋮----
item=supplied.get(name)
⋮----
score=max(0.0,min(100.0,float(item["score"])))
fresh=item.get("fresh") is True
⋮----
w=weights[name]; weighted+=score*w; known_weight+=w
⋮----
elif name in {"code","tests","stability","release"}: stale_critical=True
score=round(weighted/known_weight,2) if known_weight else None
coverage=fresh_weight/sum(weights.values()) if weights else 0.0
confidence=("high" if coverage>=CONFIDENCE_HIGH and not stale_critical
```

## File: production_os/quarantine.py
```python
class QuarantineStore
⋮----
def __init__(self, path: str | Path)
⋮----
def _load_unlocked(self) -> None
⋮----
payload=json.loads(self.path.read_text(encoding="utf-8"))
⋮----
def load(self) -> None
⋮----
def _save_unlocked(self) -> None
⋮----
def set(self, repository: str, *, active: bool, reason: str) -> dict
⋮----
def active(self, repository: str) -> tuple[bool, str | None]
⋮----
item=self.entries.get(repository) or {}
```

## File: production_os/queue_maintenance.py
```python
queue = Path(queue_dir)
archive = Path(archive_dir) if archive_dir else None
⋮----
actions: list[dict] = []
⋮----
payload = json.loads(source.read_text(encoding="utf-8"))
⋮----
key = str(payload.get("idempotency_key", ""))
claim = claims.claims.get(key)
⋮----
target = archive / source.name
⋮----
dead = Path(dead_letter_dir)
⋮----
attempt = int(payload.get("delivery_attempt", 0)) + 1
⋮----
target = queue / f"{key}.retry{attempt}.json"
```

## File: production_os/rate_limit.py
```python
@dataclass(frozen=True, slots=True)
class RateLimitDecision
⋮----
allowed: bool
count: int
limit: int
window_seconds: int
⋮----
def to_dict(self) -> dict
⋮----
now = datetime.now(timezone.utc)
cutoff = now - timedelta(seconds=window_seconds)
count = 0
⋮----
ts = datetime.fromisoformat(raw.replace("Z", "+00:00"))
⋮----
class RateLimitStore
⋮----
def __init__(self, path: str | Path)
⋮----
def _load_unlocked(self) -> None
⋮----
payload = json.loads(self.path.read_text(encoding="utf-8"))
raw = payload.get("events", {})
⋮----
def load(self) -> None
⋮----
def _save_unlocked(self) -> None
⋮----
timestamps = []
⋮----
decision = RateLimitDecision(
```

## File: production_os/receipts.py
```python
path=Path(directory)
⋮----
dest=path/f"{key}.receipt.json"
payload={
```

## File: production_os/reconciliation.py
```python
@dataclass(frozen=True, slots=True)
class ReconciliationAction
⋮----
key: str
repository: str
task: str
action: str
reason: str
⋮----
def to_dict(self) -> dict
⋮----
def reconcile_runtime_state(state: RuntimeState) -> list[ReconciliationAction]
⋮----
now = datetime.now(timezone.utc)
actions: list[ReconciliationAction] = []
⋮----
lease_expired = False
cooldown_expired = False
⋮----
lease_expired = not state.is_leased(record, now)
⋮----
cooldown_expired = not state.in_cooldown(record, now)
```

## File: production_os/rekor_checkpoint_state.py
```python
_HEX_64 = re.compile(r"^[0-9a-fA-F]{64}$")
_TREE_ID = re.compile(r" - ([0-9]+)$")
⋮----
class RekorCheckpointStateError(RuntimeError)
⋮----
def _utcnow() -> str
⋮----
def _hash_children(left: bytes, right: bytes) -> bytes
⋮----
def _decode_hash(value: str) -> bytes
⋮----
text = str(value).lower()
⋮----
def parse_checkpoint_identity(checkpoint: str) -> dict[str, Any]
⋮----
"""Extract the authenticated tree identity from a Rekor signed note.

    This function deliberately does not verify the note signature. Callers use
    it only after receipt verification has authenticated the checkpoint.
    """
⋮----
split = checkpoint.rfind("\n\n")
note = checkpoint if split < 0 else checkpoint[: split + 1]
lines = note.splitlines()
⋮----
tree_size = int(lines[1])
root = base64.b64decode(lines[2], validate=True)
⋮----
origin = lines[0]
match = _TREE_ID.search(origin)
⋮----
"""Verify an RFC6962 append-only Merkle-tree consistency proof."""
⋮----
first = int(previous_tree_size)
second = int(tree_size)
first_root = _decode_hash(previous_root_hash)
second_root = _decode_hash(root_hash)
path = [_decode_hash(item) for item in hashes]
⋮----
fn = first - 1
sn = second - 1
⋮----
first_hash = first_root
second_hash = first_root
⋮----
first_hash = path[0]
second_hash = path[0]
path = path[1:]
⋮----
first_hash = _hash_children(sibling, first_hash)
second_hash = _hash_children(sibling, second_hash)
⋮----
second_hash = _hash_children(second_hash, sibling)
⋮----
class RekorV1ConsistencyClient
⋮----
"""Fetch Rekor v1 Merkle consistency proofs."""
⋮----
url = str(base_url).rstrip("/")
⋮----
entries_suffix = "/api/v1/log/entries"
log_suffix = "/api/v1/log"
⋮----
url = url[: -len("/entries")]
⋮----
params = {
⋮----
request = Request(
⋮----
status = int(response.status)
raw = response.read()
⋮----
payload = json.loads(raw)
⋮----
root_hash = str(payload.get("rootHash") or "").lower()
hashes = payload.get("hashes")
⋮----
class RekorCheckpointStateStore
⋮----
"""Persist one latest authenticated checkpoint per Rekor log/origin."""
⋮----
def __init__(self, backend: Any) -> None
⋮----
def _is_postgres(self) -> bool
⋮----
def _sql(self, statement: str) -> str
⋮----
def _initialize(self) -> None
⋮----
def get(self, log_id: str, origin: str) -> dict[str, Any] | None
⋮----
row = db.execute(
⋮----
log_id_value = str(log_id).lower()
root_hash_value = str(root_hash).lower()
⋮----
values = self._validated_values(
⋮----
stored = self.get(values[0], values[1])
⋮----
cursor = db.execute(
inserted = cursor.rowcount == 1
⋮----
expected_root = str(expected_root_hash).lower()
⋮----
class RekorCheckpointMonitor
⋮----
def observe_verified_receipt(self, receipt: dict[str, Any]) -> dict[str, Any]
⋮----
log_id = str(receipt.get("log_id") or "").lower()
⋮----
proof = receipt.get("inclusion_proof")
⋮----
checkpoint = proof.get("checkpoint")
identity = parse_checkpoint_identity(checkpoint)
⋮----
proof_size = int(proof["treeSize"])
proof_root = str(proof["rootHash"]).lower()
⋮----
origin = str(identity["origin"])
previous = self.store.get(log_id, origin)
⋮----
current = self.store.bootstrap(
⋮----
previous_size = int(previous["tree_size"])
previous_root = str(previous["root_hash"]).lower()
⋮----
consistency = self.proof_fetcher(
⋮----
hashes = consistency.get("hashes")
response_root = str(consistency.get("rootHash") or "").lower()
⋮----
current = self.store.advance(
```

## File: production_os/rekor_witness_quorum.py
```python
REKOR_WITNESS_SCHEMA = "production-os/rekor-witness-observation/v1"
REKOR_WITNESS_REQUEST_SCHEMA = "production-os/rekor-witness-request/v1"
⋮----
class RekorWitnessQuorumError(RuntimeError)
⋮----
def _utcnow() -> str
⋮----
class RekorWitnessClient
⋮----
payload = {
request = Request(
⋮----
status = int(response.status)
raw = response.read()
⋮----
decoded = json.loads(raw)
⋮----
class RekorWitnessObservationStore
⋮----
def __init__(self, backend: Any) -> None
⋮----
def _is_postgres(self) -> bool
⋮----
def _sql(self, statement: str) -> str
⋮----
def _initialize(self) -> None
⋮----
observation = response.get("observation")
⋮----
witness_id = str(observation.get("witness_id") or "")
log_id = str(observation.get("log_id") or "").lower()
origin = str(observation.get("origin") or "")
root_hash = str(observation.get("root_hash") or "").lower()
⋮----
tree_size = int(observation.get("tree_size"))
⋮----
row = {
⋮----
rows = db.execute(
⋮----
def load_rekor_witness_config(path: str | Path) -> dict[str, Any]
⋮----
config_path = Path(path)
⋮----
payload = json.loads(config_path.read_text(encoding="utf-8"))
⋮----
threshold = int(payload.get("threshold"))
⋮----
raw_witnesses = payload.get("witnesses")
⋮----
witnesses: list[dict[str, str]] = []
seen_ids: set[str] = set()
⋮----
witness_id = str(item.get("id") or "").strip()
url = str(item.get("url") or "").strip()
⋮----
inline_key = item.get("public_key")
key_path_value = item.get("public_key_path")
⋮----
public_key = str(inline_key)
⋮----
key_path = Path(str(key_path_value))
⋮----
key_path = config_path.parent / key_path
⋮----
public_key = key_path.read_text(encoding="ascii")
⋮----
required = int(threshold)
⋮----
valid_witnesses: list[str] = []
rejected_witnesses: list[str] = []
conflicting_witnesses: list[str] = []
seen: set[str] = set()
⋮----
signature = response.get("signature")
⋮----
public_key = public_keys.get(witness_id)
⋮----
signature_valid = verify_payload(
⋮----
signature_valid = False
⋮----
same_tree_identity = (
⋮----
same_tree_identity = False
⋮----
valid = len(valid_witnesses) >= required
⋮----
raw_witnesses = config.get("witnesses")
⋮----
threshold = int(config.get("threshold"))
⋮----
public_keys: dict[str, str] = {}
responses: list[dict[str, Any]] = []
responses_by_id: dict[str, dict[str, Any]] = {}
errors: dict[str, str] = {}
⋮----
public_key = str(item.get("public_key") or "")
⋮----
response = RekorWitnessClient(url).observe(
⋮----
returned_id = (
⋮----
result = evaluate_rekor_witness_quorum(
⋮----
valid_ids = set(result["valid_witnesses"])
rejected_ids = set(result["rejected_witnesses"])
conflicting_ids = set(result["conflicting_witnesses"])
⋮----
verdict = "valid"
⋮----
verdict = "conflicting"
⋮----
verdict = "rejected"
```

## File: production_os/release_ledger.py
```python
def _now() -> str
⋮----
def _is_postgres(backend) -> bool
⋮----
def _sql(backend, statement: str) -> str
⋮----
def _execute(db, backend, statement: str, params: tuple = ())
⋮----
def _canonical_sha256(value: dict) -> str
⋮----
encoded = json.dumps(
⋮----
def _valid_sha256(value: str | None) -> bool
⋮----
class ReleaseLedger
⋮----
policy = str(validation_signature_policy).strip().lower()
⋮----
@staticmethod
    def _validation_passed(validation: dict) -> bool
⋮----
@staticmethod
    def _row(row) -> dict
⋮----
def get(self, release_id: str) -> dict
⋮----
row = _execute(
⋮----
def list_for_workflow(self, workflow_id: str) -> list[dict]
⋮----
rows = _execute(
⋮----
"""Re-evaluate promoted releases and report trust blast radius."""
⋮----
releases = []
affected = []
matched = 0
⋮----
release = self._row(row)
metadata = dict(release.get("metadata") or {})
attestation = dict(
slsa = dict(metadata.get("slsa_provenance") or {})
statement = dict(slsa.get("statement") or {})
predicate = dict(statement.get("predicate") or {})
run_details = dict(predicate.get("runDetails") or {})
builder = dict(run_details.get("builder") or {})
attestation_signature = dict(
slsa_signature = dict(slsa.get("signature") or {})
⋮----
release_validator = str(
release_builder = str(builder.get("id") or "")
release_keys = {
⋮----
verification = self.verify(release["id"])
item = {
⋮----
affected_count = len(affected)
severity = (
affected_repositories = sorted({
affected_validators = sorted({
affected_builders = sorted({
reasons: dict[str, int] = {}
⋮----
reason = str(item.get("reason") or "verification failed")
⋮----
"""Build a stable, machine-readable trust incident report."""
status = self.trust_status(
generated_at = _now()
fingerprint_payload = {
incident_id = "trust-" + _canonical_sha256(
⋮----
report = self.incident_report(
now = _now()
stable_report = dict(report)
⋮----
report_state_hash = _canonical_sha256(stable_report)
⋮----
latest = _execute(
⋮----
latest_report = json.loads(latest["report_json"])
latest_stable = dict(latest_report)
⋮----
previous = _execute(
previous_hash = (
entry_payload = {
report_hash = _canonical_sha256(entry_payload)
⋮----
# A concurrent writer may have persisted the exact same
# snapshot after our read. Resolve that race as a normal
# deduplication event; preserve all other failures.
existing = _execute(
⋮----
statement = """
params: tuple = ()
⋮----
params = (incident_id,)
⋮----
def verify_incident_history(self) -> dict
⋮----
entries = self.incident_history()
previous_hash = GENESIS_HASH
⋮----
expected = _canonical_sha256({
⋮----
previous_hash = entry["report_hash"]
⋮----
release_id = uuid.uuid4().hex
⋮----
workflow_row = _execute(
⋮----
workflow_metadata = json.loads(
⋮----
artifact_row = _execute(
⋮----
artifact_metadata = json.loads(
artifact_sha256 = artifact_row["sha256"]
⋮----
source_revision = artifact_metadata.get(
workflow_generation = artifact_metadata.get(
⋮----
attestation_schema = str(
dual_signed = attestation_schema == DUAL_SCHEMA
⋮----
asymmetric = (
⋮----
verified_bundle = verify_dual_attestation(
verified_attestation = (
⋮----
approval = dict(approval or {})
approved_by = str(
approval_role = str(
⋮----
computed_approval_key = release_approval_key(
supplied_approval_key = str(
⋮----
approval_record = {
⋮----
expected_revision = workflow_metadata.get(
expected_generation = workflow_metadata.get(
⋮----
base_metadata = {
release_preview = {
⋮----
provenance = create_release_provenance_with_signer(
statement = create_slsa_statement(
⋮----
signed_statement = sign_slsa_statement_with_signer(
⋮----
signed_statement = sign_slsa_statement(
⋮----
provenance = create_release_provenance(
release_metadata = {
⋮----
previous_row = _execute(
sequence = (
⋮----
transparency_entry = create_transparency_entry(
⋮----
def transparency_log(self) -> list[dict]
⋮----
def verify_transparency(self) -> dict
⋮----
def verify(self, release_id: str) -> dict
⋮----
release = self.get(release_id)
⋮----
provenance = dict(metadata.get("provenance") or {})
⋮----
verified = verified_bundle["ed25519"]
provenance_valid = verify_release_provenance_v2(
⋮----
verified = verify_validation_attestation_v2(
⋮----
verified = verify_validation_attestation(
provenance_valid = verify_release_provenance(
⋮----
signed_statement = dict(
⋮----
slsa_valid = verify_trusted_slsa_statement(
⋮----
slsa_valid = verify_signed_slsa_statement(
⋮----
expected_statement_digest = statement_digest(
⋮----
expected = {
⋮----
chain = self.verify_transparency()
⋮----
entries = self.transparency_log()
transparency_entry = next(
⋮----
signature = provenance["signature"]
⋮----
original = self.get(release_id)
⋮----
reason = str(reason or "").strip()
⋮----
rollback_id = uuid.uuid4().hex
```

## File: production_os/remote_worker_runner.py
```python
class RemoteWorkerRunner
⋮----
command = [str(part) for part in executor_command if str(part)]
⋮----
secret_names = {
⋮----
@staticmethod
    def _terminate(process: subprocess.Popen[str]) -> None
⋮----
def _heartbeat_active(self, key: str) -> dict
⋮----
def _acknowledge_cancel(self, key: str) -> None
⋮----
def _execute(self, job: RemoteJob) -> dict
⋮----
key = job.key
⋮----
heartbeat = self._heartbeat_active(key)
⋮----
request = json.dumps(
started = time.monotonic()
process = subprocess.Popen(
first_communicate = True
stdout = ""
⋮----
elapsed = time.monotonic() - started
remaining = self.executor_timeout_seconds - elapsed
⋮----
duration = time.monotonic() - started
⋮----
first_communicate = False
⋮----
controls = (
desired = str(
⋮----
reason = f"executor_exit_{process.returncode}"
⋮----
payload = json.loads(stdout)
⋮----
payload = None
⋮----
status = str(payload.get("status") or "")
result = payload.get("result", {})
⋮----
status = ""
⋮----
reason = str(
⋮----
outcomes: list[dict] = []
index = 0
⋮----
job = self.client.claim(
⋮----
outcome = self._execute(job)
```

## File: production_os/remote_worker.py
```python
@dataclass(frozen=True, slots=True)
class RemoteJob
⋮----
key: str
payload: dict
⋮----
def to_dict(self) -> dict
⋮----
class RemoteWorkerClient
⋮----
def _request(self, path: str, payload: dict | None = None) -> tuple[int, dict]
⋮----
body = None if payload is None else json.dumps(payload).encode("utf-8")
request = urllib.request.Request(
⋮----
raw = response.read()
⋮----
raw = exc.read()
payload = json.loads(raw or b"{}")
⋮----
payload = {"worker_id":self.worker_id}
⋮----
def claim(self, ack_timeout_seconds: int = 120) -> RemoteJob | None
⋮----
job = result["job"]
⋮----
def ack(self, key: str) -> dict
⋮----
jobs: list[RemoteJob] = []
⋮----
job = self.claim(ack_timeout_seconds=ack_timeout_seconds)
```

## File: production_os/resources.py
```python
def allocate_resources(schedule: dict, total_slots: int = 3) -> dict
⋮----
active = [
⋮----
allocations: list[dict] = []
remaining = total_slots
⋮----
slots = 1
⋮----
remaining = 0
```

## File: production_os/result_cache.py
```python
def _now() -> str
⋮----
def _pg(backend) -> bool
⋮----
def _sql(backend, statement: str) -> str
⋮----
def _execute(db, backend, statement: str, params: tuple = ())
⋮----
canonical = json.dumps(
⋮----
class ResultCache
⋮----
def __init__(self, backend)
⋮----
def get(self, key: str) -> dict | None
⋮----
row = _execute(
⋮----
now = _now()
⋮----
def prune(self, *, max_entries: int = 10000) -> int
⋮----
rows = _execute(
stale = rows[max(0, int(max_entries)):]
```

## File: production_os/reuse.py
```python
@dataclass(frozen=True, slots=True)
class ReuseOpportunity
⋮----
source: str
target: str
capability: str
confidence: float
rationale: str
evidence: tuple[str, ...] = ()
components: tuple[dict, ...] = ()
adaptation_plan: dict | None = None
⋮----
def to_dict(self) -> dict
⋮----
def _compatible(source: RepoAssessment, target: RepoAssessment) -> bool
⋮----
def _component_candidates(source: RepoAssessment, target: RepoAssessment, capability: str) -> tuple[dict, ...]
⋮----
matches = []
⋮----
adaptation = score_adaptation_risk(source, target, capability, component)
⋮----
def detect_reuse(assessments: list[RepoAssessment]) -> list[ReuseOpportunity]
⋮----
opportunities: list[ReuseOpportunity] = []
seen: set[tuple[str, str, str]] = set()
⋮----
target_caps = {cap.name for cap in target.capabilities}
⋮----
version_checks = [
⋮----
key = (source.evidence.full_name, target.evidence.full_name, capability.name)
⋮----
family_factor = 1.0 if source.profile == target.profile else 0.88
components = _component_candidates(source, target, capability.name)
⋮----
risk_factor = 1.0
⋮----
best_risk = components[0]["adaptation_risk"]
risk_factor = max(0.55, 1.0 - (best_risk / 150.0))
⋮----
confidence = round(capability.confidence * family_factor * risk_factor, 2)
⋮----
plan = build_adaptation_plan(
⋮----
dependency_checks = [
⋮----
relevant_versions = [
⋮----
validation_plan = [
⋮----
missing = [
major_mismatches = [
```

## File: production_os/runtime_state.py
```python
@dataclass(slots=True)
class RuntimeRecord
⋮----
key: str
repository: str
task: str
status: str
attempts: int = 0
consecutive_failures: int = 0
lease_owner: str | None = None
lease_expires_at: str | None = None
cooldown_until: str | None = None
last_decision: str | None = None
updated_at: str | None = None
priority: float = 0.0
interruptible: bool = False
preempt_requested: bool = False
checkpoint_ref: str | None = None
started_at: str | None = None
⋮----
def to_dict(self) -> dict
⋮----
def task_key(repository: str, task: str) -> str
⋮----
raw = f"{repository}\n{task}".encode("utf-8")
⋮----
class RuntimeState
⋮----
SCHEMA_VERSION = "production-os/runtime-state/v2"
⋮----
def __init__(self, path: str | Path)
⋮----
def _load_unlocked(self) -> None
⋮----
payload = json.loads(self.path.read_text(encoding="utf-8"))
⋮----
def load(self) -> None
⋮----
def _save_unlocked(self) -> None
⋮----
def save(self) -> None
⋮----
def get(self, repository: str, task: str) -> RuntimeRecord
⋮----
key = task_key(repository, task)
⋮----
@staticmethod
    def _parse(ts: str | None) -> datetime | None
⋮----
def is_leased(self, record: RuntimeRecord, now: datetime | None = None) -> bool
⋮----
now = now or datetime.now(timezone.utc)
expires = self._parse(record.lease_expires_at)
⋮----
def in_cooldown(self, record: RuntimeRecord, now: datetime | None = None) -> bool
⋮----
until = self._parse(record.cooldown_until)
⋮----
record = self.get(repository, task)
now = datetime.now(timezone.utc)
⋮----
def release_lease(self, repository: str, task: str) -> RuntimeRecord
```

## File: production_os/scheduler.py
```python
@dataclass(frozen=True, slots=True)
class ScheduledWork
⋮----
repository: str
task: str
lane: str
score: float
effort: int
rationale: str
blockers: tuple[str, ...] = ()
⋮----
def to_dict(self) -> dict
⋮----
def _repo_map(assessments: Iterable[RepoAssessment]) -> dict[str, RepoAssessment]
⋮----
blockers: list[str] = []
evidence = assessment.evidence
⋮----
policy_decision = evaluate_policy(
⋮----
record = runtime_state.get(action.repository, action.task)
⋮----
def _schedule_score(action: ActionCandidate, assessment: RepoAssessment | None, learning_signals: list[LearningSignal] | None = None) -> float
⋮----
maturity = assessment.score.total if assessment else 0
blocker_bonus = 0.0
⋮----
conclusion = str(assessment.evidence.latest_ci_conclusion).lower()
⋮----
release_bonus = action.release_proximity * 2.0
maturity_gap_bonus = max(0, 70 - maturity) * 0.15
effort_penalty = max(action.effort - 1, 0) * 2.5
learned = learning_weight(learning_signals or [], action.repository, action.task)
⋮----
repos = _repo_map(assessments)
ranked: list[tuple[ActionCandidate, RepoAssessment | None, float, tuple[str, ...]]] = []
⋮----
assessment = repos.get(action.repository)
⋮----
ranked = round_robin_by_repository(ranked)
⋮----
selected_repos: set[str] = set()
active = 0
work: list[ScheduledWork] = []
⋮----
hard_blocked = any(
⋮----
lane = "PAUSE"
⋮----
lane = "NEXT"
⋮----
lane = "NOW" if active == 0 else "PARALLEL"
⋮----
lane = "IGNORE"
⋮----
counts = {lane: sum(1 for item in work if item.lane == lane) for lane in ("NOW","PARALLEL","NEXT","PAUSE","IGNORE")}
```

## File: production_os/scoring.py
```python
def _recent_activity_points(pushed_at: str | None) -> int
⋮----
pushed = datetime.fromisoformat(pushed_at.replace("Z", "+00:00"))
⋮----
days = (datetime.now(timezone.utc) - pushed).days
⋮----
def score_repository(e: RepoEvidence) -> ScoreBreakdown
⋮----
documentation = 10 if e.has_readme else 0
tests = 15 if e.has_tests else 0
ci = 15 if e.has_ci else 0
⋮----
ci = 5
release = 15 if e.has_release_workflow else 0
build = 10 if e.has_manifest else 0
security = (5 if e.has_security_policy else 0) + (5 if e.has_dependency_automation else 0)
license_points = 5 if e.has_license else 0
activity = _recent_activity_points(e.pushed_at)
⋮----
total = documentation + tests + ci + release + build + security + license_points + activity
⋮----
def generate_actions(e: RepoEvidence, score: ScoreBreakdown, profile: str) -> list[ActionCandidate]
⋮----
actions: list[ActionCandidate] = []
⋮----
def add(task, rationale, criteria, evidence, *, impact, urgency, risk, release, effort)
⋮----
action = ActionCandidate(
⋮----
release_weight = 10 if profile in {"android-app", "android-game"} else 8
⋮----
missing = []
⋮----
def assess_repository(evidence: RepoEvidence) -> RepoAssessment
⋮----
score = score_repository(evidence)
profile = classify_repository(evidence)
capabilities = extract_capabilities(evidence)
source_signals = analyze_source_evidence(evidence)
components = extract_components(evidence)
```

## File: production_os/self_healing.py
```python
@dataclass(frozen=True, slots=True)
class HealingAction
⋮----
repository: str
task: str
action: str
reason: str
⋮----
def to_dict(self) -> dict
⋮----
def apply_self_healing(state: RuntimeState) -> list[HealingAction]
⋮----
now = datetime.now(timezone.utc)
actions: list[HealingAction] = []
```

## File: production_os/signer_factory.py
```python
class SignerConfigurationError(ValueError)
⋮----
class RemoteSignerError(RuntimeError)
⋮----
class RemoteHttpSigner(Signer)
⋮----
@property
    def key_id(self) -> str
⋮----
def sign(self, payload: dict[str, Any]) -> dict[str, str]
⋮----
now=time.monotonic()
⋮----
body=json.dumps(
headers={
⋮----
last_error: Exception | None=None
⋮----
request=Request(
⋮----
result=json.loads(response.read())
⋮----
signature=dict(result.get("signature") or result)
⋮----
last_error=exc
⋮----
value=str(uri or "").strip()
⋮----
target=value.removeprefix("vault+")
marker="/keys/"
⋮----
auth_method=str(vault_auth_method or "token").lower()
token=str(vault_token or bearer_token or "")
⋮----
token=login_approle(
⋮----
token=login_kubernetes(
⋮----
endpoint=value.removeprefix("remote+")
```

## File: production_os/signers.py
```python
class Signer(ABC)
⋮----
@property
@abstractmethod
    def key_id(self) -> str
⋮----
@abstractmethod
    def sign(self, payload: dict[str, Any]) -> dict[str, str]
⋮----
class PemSigner(Signer)
⋮----
def __init__(self, private_key_pem: str)
⋮----
private_key = load_private_key(private_key_pem)
⋮----
@property
    def key_id(self) -> str
⋮----
def sign(self, payload: dict[str, Any]) -> dict[str, str]
```

## File: production_os/signing.py
```python
SIGNATURE_ALGORITHM = "ed25519"
⋮----
class SigningError(ValueError)
⋮----
def canonical_bytes(payload: dict[str, Any]) -> bytes
⋮----
def canonical_json(payload: dict[str, Any]) -> str
⋮----
"""Return the canonical UTF-8 JSON representation used for signing."""
⋮----
def key_id(public_key: Ed25519PublicKey) -> str
⋮----
raw = public_key.public_bytes(
⋮----
def generate_keypair() -> tuple[str, str]
⋮----
private_key = Ed25519PrivateKey.generate()
public_key = private_key.public_key()
private_pem = private_key.private_bytes(
public_pem = public_key.public_bytes(
⋮----
def load_private_key(value: str) -> Ed25519PrivateKey
⋮----
key = serialization.load_pem_private_key(
⋮----
def load_public_key(value: str) -> Ed25519PublicKey
⋮----
key = serialization.load_pem_public_key(
⋮----
private_key = load_private_key(private_key_pem)
⋮----
signature = private_key.sign(canonical_bytes(payload))
⋮----
public_key = load_public_key(public_key_pem)
⋮----
raw = base64.b64decode(
```

## File: production_os/source_tree.py
```python
TEXT_EXTENSIONS = {
⋮----
PRIORITY_DIRS = (
⋮----
@dataclass(frozen=True, slots=True)
class TreeSamplePolicy
⋮----
max_depth: int = 3
max_files: int = 40
max_chars_per_file: int = 12000
⋮----
def is_candidate_file(path: str) -> bool
⋮----
lower = path.lower()
⋮----
filename = lower.rsplit("/", 1)[-1]
⋮----
def path_priority(path: str) -> tuple[int, int, str]
⋮----
parts = path.lower().split("/")
top = parts[0] if parts else ""
priority = PRIORITY_DIRS.index(top) if top in PRIORITY_DIRS else len(PRIORITY_DIRS)
```

## File: production_os/speculation.py
```python
def _now() -> str
⋮----
def _pg(backend) -> bool
⋮----
def _sql(backend, statement: str) -> str
⋮----
def _execute(db, backend, statement: str, params: tuple = ())
⋮----
class SpeculationManager
⋮----
def __init__(self, backend, queue)
⋮----
@staticmethod
    def _safe(payload: dict) -> bool
⋮----
constraints = (
⋮----
canonical = self.queue.get(canonical_job_key)
payload = dict(canonical["payload"])
⋮----
group_id = str(
duplicate_key = task_key(
now = _now()
⋮----
existing = _execute(
⋮----
duplicate_payload = {
job = self.queue.enqueue(duplicate_payload)
⋮----
def group_for_job(self, job_key: str) -> str | None
⋮----
row = _execute(
⋮----
def try_win(self, group_id: str, job_key: str) -> bool
⋮----
winner = row["winner_job_key"]
⋮----
cancelled: list[str] = []
⋮----
rows = _execute(
⋮----
key = str(row["job_key"])
current = _execute(
```

## File: production_os/sqlite_backend.py
```python
def _utcnow() -> str
⋮----
class SQLiteBackend
⋮----
SCHEMA_VERSION = 15
⋮----
def __init__(self, path: str | Path)
⋮----
def connect(self) -> sqlite3.Connection
⋮----
connection = sqlite3.connect(
⋮----
@contextmanager
    def transaction(self, *, immediate: bool = True) -> Iterator[sqlite3.Connection]
⋮----
connection = self.connect()
⋮----
def initialize(self) -> None
⋮----
managed_columns = {
⋮----
remediation_columns = {
⋮----
cursor = db.execute(
⋮----
def events_after(self, event_id: int = 0, limit: int = 100) -> list[dict]
⋮----
rows = db.execute(
⋮----
class SQLiteRuntimeState
⋮----
def __init__(self, backend: SQLiteBackend)
⋮----
@staticmethod
    def _row(row: sqlite3.Row) -> RuntimeRecord
⋮----
def load(self) -> None
⋮----
rows = db.execute("SELECT * FROM runtime_records").fetchall()
⋮----
def save(self) -> None
⋮----
def get(self, repository: str, task: str) -> RuntimeRecord
⋮----
key = task_key(repository, task)
⋮----
row = db.execute(
⋮----
record = self._row(row)
⋮----
@staticmethod
    def _parse(ts: str | None) -> datetime | None
⋮----
def is_leased(self, record: RuntimeRecord, now: datetime | None = None) -> bool
⋮----
now = now or datetime.now(timezone.utc)
expires = self._parse(record.lease_expires_at)
⋮----
def in_cooldown(self, record: RuntimeRecord, now: datetime | None = None) -> bool
⋮----
until = self._parse(record.cooldown_until)
⋮----
now = datetime.now(timezone.utc)
expires = (now + timedelta(minutes=minutes)).isoformat()
⋮----
current = self._row(row)
⋮----
def release_lease(self, repository: str, task: str) -> RuntimeRecord
⋮----
now = _utcnow()
⋮----
status = "idle" if row["status"] in {"running", "preempt-requested"} else row["status"]
⋮----
current = self.get(repository, task)
⋮----
attempts = current.attempts + 1
failures = current.consecutive_failures
status = "idle"
cooldown = current.cooldown_until
⋮----
status = "succeeded"
failures = 0
cooldown = None
⋮----
status = "failed"
⋮----
status = "circuit-open"
cooldown = (now + timedelta(minutes=cooldown_minutes)).isoformat()
⋮----
status = "replan"
cooldown = (
⋮----
class SQLiteWorkerRegistry
⋮----
@staticmethod
    def _row(row: sqlite3.Row) -> Worker
⋮----
rows = db.execute("SELECT * FROM workers").fetchall()
⋮----
worker = self._row(row)
⋮----
def heartbeat(self, worker_id: str, active_tasks: int | None = None) -> Worker
⋮----
active = row["active_tasks"] if active_tasks is None else max(0, active_tasks)
⋮----
def adjust_active_tasks(self, worker_id: str, delta: int) -> Worker
⋮----
active = max(0, int(row["active_tasks"]) + int(delta))
⋮----
def detect_dead(self, timeout_seconds: int = 120) -> list[Worker]
⋮----
dead: list[Worker] = []
⋮----
stale = True
⋮----
seen = datetime.fromisoformat(
stale = (now - seen).total_seconds() > timeout_seconds
⋮----
def available(self) -> list[Worker]
⋮----
class SQLiteClaimStore
⋮----
@staticmethod
    def _row(row: sqlite3.Row) -> ClaimRecord
⋮----
rows = db.execute("SELECT * FROM claims").fetchall()
⋮----
deadline = (now + timedelta(seconds=ack_timeout_seconds)).isoformat()
⋮----
row = db.execute("SELECT * FROM claims WHERE key=?", (key,)).fetchone()
⋮----
claim = self._row(row)
⋮----
def ack(self, key: str, worker_id: str) -> ClaimRecord
⋮----
def complete(self, key: str, worker_id: str) -> ClaimRecord
⋮----
def expired_unacked(self) -> list[ClaimRecord]
⋮----
class SQLiteJobQueue
⋮----
def enqueue(self, payload: dict) -> dict
⋮----
handoff = payload.get("handoff", payload)
repository = str(handoff.get("repository", ""))
task = str(handoff.get("task", ""))
⋮----
key = str(payload.get("idempotency_key") or task_key(repository, task))
priority = float(handoff.get("priority", 0.0))
⋮----
normalized = {
⋮----
existing = db.execute(
⋮----
def get(self, key: str) -> dict
⋮----
row = db.execute("SELECT * FROM jobs WHERE key=?", (key,)).fetchone()
⋮----
@staticmethod
    def _job_dict(row: sqlite3.Row) -> dict
⋮----
deadline = (
⋮----
updated = db.execute(
⋮----
claimed = db.execute(
⋮----
capabilities_set = set(capabilities or [])
⋮----
chosen = None
⋮----
payload = json.loads(row["payload_json"])
required = set(payload.get("required_capabilities", []))
⋮----
chosen = row
⋮----
def ack(self, key: str, worker_id: str) -> dict
⋮----
def complete(self, key: str, worker_id: str) -> dict
⋮----
def fail(self, key: str, worker_id: str, reason: str) -> dict
⋮----
def cancel_queued(self, key: str, reason: str = "operator cancel") -> dict
⋮----
def cancel(self, key: str, worker_id: str, reason: str = "operator cancel") -> dict
⋮----
def recover_job(self, key: str, *, max_attempts: int = 3) -> dict
⋮----
target = (
⋮----
action = {
⋮----
def recover_expired(self, *, max_attempts: int = 3) -> list[dict]
⋮----
actions = []
```

## File: production_os/sqlite_migration.py
```python
counts = {"runtime_records":0, "workers":0, "claims":0}
⋮----
payload = json.loads(
store = runtime_state_for(backend)
⋮----
normalized = {
record = RuntimeRecord(**normalized)
⋮----
payload = json.loads(Path(workers).read_text(encoding="utf-8"))
registry = worker_registry_for(backend)
⋮----
worker = Worker(
⋮----
payload = json.loads(Path(claims).read_text(encoding="utf-8"))
store = claim_store_for(backend)
⋮----
claim = ClaimRecord(
```

## File: production_os/starlist.py
```python
@dataclass(frozen=True, slots=True)
class ExternalReference
⋮----
capability: str
repository: str
confidence: float
rationale: str
star_score: float | None = None
tier: str | None = None
domain: str | None = None
⋮----
def to_dict(self) -> dict
⋮----
CAPABILITY_TERMS: dict[str, tuple[str, ...]] = {
⋮----
def _haystack(item: dict[str, Any]) -> str
⋮----
parts: list[str] = []
⋮----
value = item.get(key)
⋮----
terms = CAPABILITY_TERMS.get(capability, (capability.replace("-", " "),))
ranked: list[tuple[float, ExternalReference]] = []
⋮----
score = float(item.get("score") or 0)
⋮----
haystack = _haystack(item)
matches = sum(1 for term in terms if term in haystack)
⋮----
semantic = min(matches / max(len(terms), 1), 1.0)
quality = min(score / 10.0, 1.0)
confidence = round(0.55 * quality + 0.45 * semantic, 2)
ref = ExternalReference(
```

## File: production_os/storage.py
```python
def is_postgres(location: str) -> bool
⋮----
def open_backend(location: str)
⋮----
def runtime_state_for(backend)
⋮----
def worker_registry_for(backend)
⋮----
def claim_store_for(backend)
⋮----
def job_queue_for(backend)
```

## File: production_os/supply_chain.py
```python
STATEMENT_TYPE = "https://in-toto.io/Statement/v1"
PREDICATE_TYPE = "https://slsa.dev/provenance/v1"
⋮----
class SupplyChainError(ValueError)
⋮----
def _sha256_digest(value: str) -> str
⋮----
digest = str(value or "").lower()
⋮----
metadata = dict(release.get("metadata") or {})
digest = _sha256_digest(metadata.get("artifact_sha256"))
artifact_name = str(
source_revision = release.get("source_revision")
materials = []
⋮----
statement = envelope.get("statement")
signature = envelope.get("signature")
⋮----
subjects = statement.get("subject") or []
⋮----
digest = dict(subjects[0].get("digest") or {}).get(
⋮----
def statement_digest(statement: dict[str, Any]) -> str
⋮----
encoded = json.dumps(
⋮----
signed_at = str(envelope.get("signed_at") or "")
⋮----
predicate = dict(statement.get("predicate") or {})
run_details = dict(predicate.get("runDetails") or {})
builder = dict(run_details.get("builder") or {})
builder_id = str(builder.get("id") or "")
build_definition = dict(
external = dict(
repository = str(external.get("repository") or "")
⋮----
public_key = builder_policy.resolve(
```

## File: production_os/task_capabilities.py
```python
VISUAL_CAPABILITY = "visual-asset-production"
VISUAL_3D_CAPABILITY = "visual-asset-3d-production"
ASSET_FORGE_REQUEST_SCHEMA = "asset-forge/production-request/v1"
ASSET_FORGE_REPORT_SCHEMA = "asset-forge/production-report/v1"
⋮----
_VISUAL_PATTERNS = (
⋮----
def _handoff_text(handoff: dict) -> str
⋮----
fields = [
acceptance = handoff.get("acceptance_criteria")
⋮----
def is_visual_asset_task(handoff: dict) -> bool
⋮----
text = _handoff_text(handoff)
⋮----
def is_3d_generation_task(handoff: dict) -> bool
⋮----
has_3d = bool(
has_generation = bool(
⋮----
def inferred_required_capabilities(handoff: dict) -> list[str]
⋮----
explicit = handoff.get("required_capabilities", []) if isinstance(handoff, dict) else []
required = {
⋮----
def asset_forge_tool_contract(handoff: dict) -> dict | None
⋮----
required = set(inferred_required_capabilities(handoff))
```

## File: production_os/transparency_receipts.py
```python
RECEIPT_SCHEMA = "production-os/transparency-receipt/v1"
_HEX_64 = re.compile(r"^[0-9a-fA-F]{64}$")
_ENTRY_UUID = re.compile(r"^(?:[0-9a-fA-F]{64}|[0-9a-fA-F]{80})$")
⋮----
class TransparencyReceiptError(RuntimeError)
⋮----
class TransparencyPublisher(Protocol)
⋮----
def publish(self, envelope: dict[str, Any]) -> dict[str, Any]: ...
⋮----
def _canonical_json_bytes(value: Any) -> bytes
⋮----
def checkpoint_digest(envelope: dict[str, Any]) -> str
⋮----
def _hash_leaf(body: bytes) -> bytes
⋮----
def _hash_children(left: bytes, right: bytes) -> bytes
⋮----
index = int(log_index)
size = int(tree_size)
⋮----
path = [bytes.fromhex(str(item)) for item in hashes]
⋮----
fn = index
sn = size - 1
current = _hash_leaf(leaf_body)
⋮----
current = _hash_children(sibling, current)
⋮----
current = _hash_children(current, sibling)
⋮----
def _decode_entry_body(encoded: str) -> tuple[bytes, dict[str, Any]]
⋮----
raw = base64.b64decode(encoded, validate=True)
body = json.loads(raw)
⋮----
def _entry_checkpoint_digest(body: dict[str, Any]) -> str
⋮----
value = body["spec"]["data"]["hash"]["value"]
⋮----
value = body["HashedRekordObj"]["data"]["hash"]["value"]
⋮----
value = str(value).lower()
⋮----
def _rekor_log_id(public_key: Any) -> str
⋮----
der = public_key.public_bytes(
⋮----
"""Authenticate Rekor's SET and bind it to the configured log key."""
⋮----
verification = entry.get("verification")
⋮----
encoded = verification.get("signedEntryTimestamp")
⋮----
signature = base64.b64decode(encoded, validate=True)
public_key = serialization.load_pem_public_key(
⋮----
payload = {
canonical = _canonical_json_bytes(payload)
⋮----
"""Verify a Rekor v1 signed tree checkpoint and bind it to a proof."""
⋮----
split = checkpoint.rfind("\n\n")
⋮----
note = checkpoint[: split + 1]
signature_block = checkpoint[split + 2 :]
⋮----
lines = note.splitlines()
⋮----
tree_size = int(lines[1])
⋮----
expected_root = str(expected_root_hash).lower()
⋮----
root = base64.b64decode(lines[2], validate=True)
⋮----
key_hint = hashlib.sha256(der).digest()[:4]
note_bytes = note.encode("utf-8")
digest = hashlib.sha256(note_bytes).digest()
signature_lines = signature_block.splitlines()
⋮----
parts = signature_line.split(" ", 2)
⋮----
encoded = base64.b64decode(parts[2], validate=True)
⋮----
signature = encoded[4:]
⋮----
log_id = str(entry.get("logID") or "")
⋮----
log_index = int(entry["logIndex"])
integrated_time = int(entry["integratedTime"])
⋮----
body_encoded = entry.get("body")
⋮----
expected_digest = checkpoint_digest(envelope)
⋮----
proof = verification.get("inclusionProof")
⋮----
proof_index = int(proof["logIndex"])
tree_size = int(proof["treeSize"])
⋮----
hashes = proof.get("hashes")
root_hash = str(proof.get("rootHash") or "")
checkpoint = proof.get("checkpoint")
⋮----
signed_entry_timestamp = verification.get("signedEntryTimestamp")
⋮----
log_id = str(receipt.get("log_id") or "")
⋮----
body_encoded = receipt.get("entry_body")
⋮----
proof = receipt.get("inclusion_proof")
⋮----
proof_valid = verify_inclusion_proof(
⋮----
set_entry = {
⋮----
def _private_key_signer(private_key: Any) -> Callable[[bytes], bytes]
⋮----
class RekorV1Publisher
⋮----
"""Publish a checkpoint envelope through Rekor's stable v1 API.

    The supplied signer must produce a detached signature compatible with
    Rekor hashedrekord verification for the supplied public key.
    """
⋮----
url = str(base_url).rstrip("/")
⋮----
private_key = serialization.load_pem_private_key(
⋮----
signer = _private_key_signer(private_key)
public_key_pem = private_key.public_key().public_bytes(
⋮----
def publish(self, envelope: dict[str, Any]) -> dict[str, Any]
⋮----
payload = _canonical_json_bytes(envelope)
signature = self.signer(payload)
proposed = build_rekor_v1_hashedrekord(
request = Request(
⋮----
status = int(response.status)
raw = response.read()
⋮----
decoded = json.loads(raw)
⋮----
receipt = parse_rekor_v1_receipt(
```

## File: production_os/transparency.py
```python
LOG_SCHEMA = "production-os/transparency-entry/v1"
GENESIS_HASH = "0" * 64
⋮----
class TransparencyError(ValueError)
⋮----
def _canonical(payload: dict[str, Any]) -> bytes
⋮----
def entry_hash(payload: dict[str, Any]) -> str
⋮----
previous = previous_hash or GENESIS_HASH
⋮----
payload = {
⋮----
payload = dict(entry)
supplied = str(payload.pop("entry_hash", ""))
⋮----
def verify_chain(entries: list[dict[str, Any]]) -> dict[str, Any]
⋮----
previous = GENESIS_HASH
expected_sequence = 1
⋮----
previous = item["entry_hash"]
```

## File: production_os/trends.py
```python
@dataclass(frozen=True, slots=True)
class Trend
⋮----
repository: str
samples: int
first_score: int
latest_score: int
delta: int
direction: str
⋮----
def to_dict(self) -> dict
⋮----
def build_trends(snapshots: list[dict]) -> list[Trend]
⋮----
series: dict[str, list[int]] = {}
⋮----
trends: list[Trend] = []
⋮----
delta = scores[-1] - scores[0]
⋮----
direction = "improving"
⋮----
direction = "regressing"
⋮----
direction = "flat"
```

## File: production_os/trust_policy.py
```python
@dataclass(frozen=True)
class TrustPolicy
⋮----
validator_keys: dict[str, Any]
builder_keys: dict[str, Any]
builder_private_key: str | None = None
provenance_private_key: str | None = None
witness_private_key: str | None = None
builder_signer: Signer | None = None
provenance_signer: Signer | None = None
witness_signer: Signer | None = None
strict_key_domains: bool = False
⋮----
def validate(self) -> dict[str, str]
⋮----
mapping = assert_separate_key_domains(
⋮----
previous = mapping.get(signer.key_id)
⋮----
policy=cls(
```

## File: production_os/validation.py
```python
@dataclass(frozen=True, slots=True)
class ValidationStep
⋮----
order: int
kind: str
required: bool
description: str
⋮----
def to_dict(self) -> dict
⋮----
steps: list[ValidationStep] = []
order = 1
⋮----
def add(kind: str, description: str, required: bool = True) -> None
⋮----
missing = [
⋮----
reused_tests = adaptation_plan.get("reuse_tests", [])
```

## File: production_os/vault_auth.py
```python
class VaultAuthError(RuntimeError)
⋮----
@dataclass(frozen=True)
class VaultToken
⋮----
token: str
renewable: bool = False
lease_duration: int = 0
⋮----
headers={
⋮----
request=Request(
⋮----
result=json.loads(response.read())
⋮----
def _token(result: dict[str, Any]) -> VaultToken
⋮----
auth=dict(result.get("auth") or {})
value=str(auth.get("client_token") or "")
```

## File: production_os/vault_signer.py
```python
class VaultSignerError(RuntimeError)
⋮----
class VaultTransitSigner(Signer)
⋮----
@property
    def key_id(self) -> str
⋮----
def sign(self, payload: dict[str, Any]) -> dict[str, str]
⋮----
raw=canonical_json(payload).encode("utf-8")
request_body=json.dumps({
headers={
⋮----
url=(
⋮----
result=json.loads(response.read())
⋮----
signature=str(
⋮----
parts=signature.split(":",2)
```

## File: production_os/versioning.py
```python
@dataclass(frozen=True, slots=True)
class VersionCompatibility
⋮----
dependency: str
source_version: str | None
target_version: str | None
status: str
confidence: float
⋮----
def to_dict(self) -> dict
⋮----
def _extract_versions(assessment: RepoAssessment) -> dict[str, str]
⋮----
versions: dict[str, str] = {}
combined = "\n".join(assessment.evidence.source_documents.values())
⋮----
patterns = [
⋮----
groups = match.groups()
⋮----
key = f"{groups[0]}:{groups[1]}".lower()
version = groups[2]
⋮----
key = groups[0].lower()
version = groups[1]
⋮----
source_versions = _extract_versions(source)
target_versions = _extract_versions(target)
results: list[VersionCompatibility] = []
⋮----
target_version = target_versions.get(dep)
⋮----
status = "not-present-in-target"
confidence = 0.92
⋮----
status = "exact-match"
confidence = 0.99
⋮----
source_major = source_version.split(".", 1)[0]
target_major = target_version.split(".", 1)[0]
⋮----
status = "same-major-review-required"
confidence = 0.85
⋮----
status = "major-version-mismatch"
confidence = 0.95
```

## File: production_os/witness.py
```python
WITNESS_SCHEMA = "production-os/transparency-witness/v1"
⋮----
class WitnessError(RuntimeError)
⋮----
checkpoint = envelope.get("checkpoint")
signature = envelope.get("signature")
⋮----
body = json.dumps(
headers = {
⋮----
request = Request(
⋮----
raw = response.read()
status = int(response.status)
⋮----
payload = json.loads(raw)
```

## File: production_os/workers.py
```python
@dataclass(slots=True)
class Worker
⋮----
worker_id: str
capabilities: list[str]
max_concurrency: int
active_tasks: int = 0
status: str = "online"
last_heartbeat: str | None = None
⋮----
def to_dict(self) -> dict
⋮----
class WorkerRegistry
⋮----
SCHEMA_VERSION = "production-os/workers/v2"
⋮----
def __init__(self, path: str | Path)
⋮----
def _load_unlocked(self) -> None
⋮----
payload = json.loads(self.path.read_text(encoding="utf-8"))
⋮----
worker = Worker(**row)
⋮----
def load(self) -> None
⋮----
def _save_unlocked(self) -> None
⋮----
def save(self) -> None
⋮----
worker = self.workers.get(worker_id)
⋮----
worker = Worker(
⋮----
def heartbeat(self, worker_id: str, active_tasks: int | None = None) -> Worker
⋮----
worker = self.workers[worker_id]
⋮----
def adjust_active_tasks(self, worker_id: str, delta: int) -> Worker
⋮----
def detect_dead(self, timeout_seconds: int = 120) -> list[Worker]
⋮----
now = datetime.now(timezone.utc)
dead = []
⋮----
seen = datetime.fromisoformat(
⋮----
def available(self) -> list[Worker]
⋮----
required = set(required_capabilities or [])
allowed = set(allowed_worker_classes or [])
candidates = []
⋮----
caps = set(worker.capabilities)
⋮----
missing = len(required - caps)
load = worker.active_tasks / max(worker.max_concurrency, 1)
⋮----
best = candidates[0]
```

## File: production_os/workflow_engine.py
```python
TERMINAL_TASK_STATES = {"succeeded", "failed", "cancelled", "blocked"}
⋮----
def _now() -> str
⋮----
def _is_postgres(backend) -> bool
⋮----
def _sql(backend, statement: str) -> str
⋮----
def _execute(db, backend, statement: str, params: tuple = ())
⋮----
@dataclass(frozen=True, slots=True)
class WorkflowTaskSpec
⋮----
task_id: str
title: str
payload: dict
dependencies: tuple[str, ...] = ()
priority: float = 0.0
max_attempts: int = 1
estimated_minutes: float = 1.0
⋮----
@classmethod
    def from_dict(cls, payload: dict) -> "WorkflowTaskSpec"
⋮----
class WorkflowEngine
⋮----
expanded: list[WorkflowTaskSpec] = []
⋮----
payload = dict(task.payload)
⋮----
items = list(payload.get("split_items", []))
⋮----
split_size = max(1, int(payload.get("split_size", 1)))
shards = [
shard_ids: list[str] = []
⋮----
shard_id = f"{task.task_id}#shard-{index}"
⋮----
shard_payload = {
⋮----
def __init__(self, backend, queue)
⋮----
@staticmethod
    def _validate(tasks: list[WorkflowTaskSpec]) -> None
⋮----
ids = [task.task_id for task in tasks]
⋮----
known = set(ids)
⋮----
missing = set(task.dependencies) - known
⋮----
graph = {task.task_id: set(task.dependencies) for task in tasks}
visiting: set[str] = set()
visited: set[str] = set()
⋮----
def visit(task_id: str) -> None
⋮----
tasks = self._expand_splittable_tasks(tasks)
⋮----
workflow_id = workflow_id or uuid.uuid4().hex
now = _now()
⋮----
workflow = self.get(workflow_id)
⋮----
# Impact can be recomputed only before real execution starts.
# Prior impact-skips and virtual barriers are reversible because they
# have not consumed worker capacity or produced execution side effects.
⋮----
result = dict(task.get("result") or {})
reversible_success = (
⋮----
decisions = analyze_change_impact(
task_lookup = {
⋮----
# Reopen tasks skipped by a previous impact evaluation before
# applying the new decision set.
⋮----
task = task_lookup[decision.task_id]
⋮----
@staticmethod
    def _spec_from_task(task: dict) -> WorkflowTaskSpec
⋮----
source = self.get(source_workflow_id)
metadata = dict(source.get("metadata") or {})
current_generation = int(
⋮----
metadata = dict(workflow.get("metadata") or {})
⋮----
rows = _execute(
⋮----
cancelled_jobs: list[str] = []
⋮----
key = row["claimed_job_key"]
⋮----
job = _execute(
⋮----
metadata = json.loads(row["metadata_json"])
⋮----
template = self.find_pr_template(repository)
⋮----
metadata = dict(template.get("metadata") or {})
⋮----
@staticmethod
    def generation_refreshable(workflow: dict) -> bool
⋮----
status = str(task.get("status") or "")
⋮----
payload = dict(task.get("payload") or {})
⋮----
workflows = self.find_by_github_pr(
⋮----
latest = workflows[0]
latest_metadata = dict(latest.get("metadata") or {})
current_sha = str(
⋮----
generation = self.create_pr_generation(
superseded = []
⋮----
matches: list[dict] = []
⋮----
value = metadata.get("github_pr_number")
⋮----
bound_pr = int(value)
⋮----
def get(self, workflow_id: str) -> dict
⋮----
workflow = _execute(
⋮----
tasks = _execute(
artifacts = _execute(
⋮----
@staticmethod
    def _task_dict(row) -> dict
⋮----
@staticmethod
    def _artifact_dict(row) -> dict
⋮----
row = _execute(
⋮----
existing = _execute(
⋮----
known_rows = _execute(
known = {str(row["task_id"]) for row in known_rows}
missing = [
⋮----
def refresh(self, workflow_id: str) -> dict
⋮----
exists = _execute(
⋮----
status_by_id = {
⋮----
changed = True
⋮----
changed = False
⋮----
current = status_by_id[row["task_id"]]
⋮----
deps = json.loads(row["dependencies_json"])
dep_states = [
new_status = current
payload = json.loads(row["payload_json"])
⋮----
new_status = "blocked"
⋮----
new_status = (
⋮----
statuses = list(status_by_id.values())
⋮----
workflow_status = "succeeded"
⋮----
workflow_status = "failed"
⋮----
workflow_status = "running"
⋮----
workflow_status = "cancelled"
⋮----
workflow_status = "pending"
⋮----
ready = [
⋮----
dispatched = []
cache_hits = 0
⋮----
payload = dict(task["payload"])
⋮----
cache_inputs = dict(
cache_key = fingerprint(
cached = self.cache.get(cache_key)
⋮----
updated = _execute(
⋮----
handoff = dict(payload.get("handoff") or payload)
⋮----
asset_forge = asset_forge_tool_contract(handoff)
⋮----
contracts = dict(handoff.get("tool_contracts") or {})
⋮----
attempt_number = int(task["attempts"]) + 1
⋮----
queue_payload = {
job = self.queue.enqueue(queue_payload)
⋮----
remaining = max(0, limit - len(dispatched))
⋮----
status = "succeeded"
⋮----
status = "ready"
⋮----
status = "failed"
⋮----
task_payload = json.loads(row["payload_json"])
⋮----
refreshed = self.refresh(workflow_id)
⋮----
dispatched = self.dispatch_ready(
⋮----
payload = job.get("payload") or {}
⋮----
current = self.get(workflow_id)
task = next(
key = task.get("claimed_job_key")
⋮----
def cancel(self, workflow_id: str) -> dict
⋮----
expected_revision = metadata.get("github_pr_head_sha")
⋮----
expected_generation = metadata.get("github_pr_generation")
⋮----
def job_generation_current(self, job: dict) -> bool
⋮----
payload = dict(job.get("payload") or {})
workflow_id = payload.get("workflow_id")
⋮----
metadata = dict(metadata or {})
⋮----
workflow_metadata = dict(workflow.get("metadata") or {})
⋮----
artifact_id = uuid.uuid4().hex
⋮----
def critical_path(self, workflow_id: str) -> dict
⋮----
tasks = {task["task_id"]:task for task in workflow["tasks"]}
memo: dict[str, tuple[float, list[str]]] = {}
⋮----
def longest(task_id: str) -> tuple[float, list[str]]
⋮----
task = tasks[task_id]
weight = float(task["estimated_minutes"])
deps = task["dependencies"]
⋮----
result = (weight, [task_id])
⋮----
best = max(
result = (best[0] + weight, best[1] + [task_id])
```
