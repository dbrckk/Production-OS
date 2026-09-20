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
- Only files matching these patterns are included: **/*.{py,js,mjs,cjs,ts,tsx,jsx,java,kt,kts,gd,groovy,gradle,toml,json,yaml,yml,sql,sh}, README.md, AGENTS.md, PROJECT_*.md
- Files matching these patterns are excluded: .ai/**, **/node_modules/**, **/.gradle/**, **/build/**, **/dist/**, **/.venv/**, **/__pycache__/**, **/.pytest_cache/**, **/.git/**, **/coverage/**, **/*.lock, **/*.min.js, **/*.map, assets/**, art/**, art_sources/**, marketing/**, colab/**, kaggle/**, discovery-cache.json, health-snapshot.json, history.json
- Files matching patterns in .gitignore are excluded
- Files matching default ignore patterns are excluded
- Content has been compressed - code blocks are separated by ⋮---- delimiter
- Files are sorted by Git change count (files with more changes are at the bottom)

# Directory Structure
````
.github/
  workflows/
    ai-repo-map.yml
    ci.yml
    semantic-refresh.yml
  dependabot.yml
.serena/
  project.yml
config/
  auth.example.json
  policy.example.json
  workflow.example.json
scripts/
  render-start.py
src/
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
    quarantine.py
    queue_maintenance.py
    rate_limit.py
    receipts.py
    reconciliation.py
    rekor_checkpoint_state.py
    rekor_witness_quorum.py
    release_ledger.py
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
tests/
  test_adaptation_plan.py
  test_adaptation.py
  test_api_auth.py
  test_approvals_migrations.py
  test_asset_forge.py
  test_asymmetric_attestations.py
  test_attestations.py
  test_builder_identity_validation.py
  test_builder_identity.py
  test_builder_trust_rotation.py
  test_callgraph_versioning_feedback.py
  test_capabilities_graph.py
  test_change_impact.py
  test_claims_delivery.py
  test_classification_history_reuse.py
  test_cli.py
  test_compatibility_validation.py
  test_components.py
  test_control_plane_pr_impact.py
  test_control_plane_release.py
  test_control_plane_webhook.py
  test_control_plane.py
  test_controller_asset_capabilities.py
  test_dashboard_launch.py
  test_deep_fingerprint_starlist.py
  test_emergency_key_revocation.py
  test_execution_feedback_trends.py
  test_execution_optimizer_postgres.py
  test_execution_optimizer.py
  test_fairness.py
  test_github_client_pr_files.py
  test_github_client_put_file.py
  test_github_webhook.py
  test_github_work_state.py
  test_governance.py
  test_health_metrics.py
  test_http_security_headers.py
  test_incident_history.py
  test_key_domains.py
  test_key_registry_validation.py
  test_key_rotation.py
  test_learning_control_surface.py
  test_observability.py
  test_p6_hardening.py
  test_policy_budgets.py
  test_policy_validation.py
  test_portfolio_claim_api.py
  test_portfolio_optimizer.py
  test_postgres_backend.py
  test_preemption.py
  test_production_stack_e2e.py
  test_provenance_signer.py
  test_queue_audit_checkpoint.py
  test_reconciliation_dispatch.py
  test_rekor_checkpoint_state_cli.py
  test_rekor_checkpoint_state_concurrency.py
  test_rekor_checkpoint_state_postgres.py
  test_rekor_checkpoint_state.py
  test_rekor_consistency_client.py
  test_rekor_signed_checkpoint_receipt.py
  test_rekor_signed_checkpoint.py
  test_rekor_v1_key_compatibility.py
  test_rekor_witness_quorum_cli.py
  test_rekor_witness_quorum.py
  test_release_ledger.py
  test_remote_worker.py
  test_render_start.py
  test_result_cache.py
  test_runtime_state.py
  test_scheduler.py
  test_scoring.py
  test_secure_release_e2e.py
  test_self_healing_heartbeat.py
  test_signer_factory.py
  test_signers.py
  test_source_tree.py
  test_speculation_api.py
  test_speculation.py
  test_sqlite_backend.py
  test_sqlite_migration.py
  test_stragglers.py
  test_supply_chain.py
  test_task_capabilities.py
  test_transparency_cli.py
  test_transparency_receipts.py
  test_trust_policy.py
  test_trust_status_summary.py
  test_vault_auth.py
  test_vault_signer.py
  test_witness.py
  test_workers.py
  test_workflow_api.py
  test_workflow_cache.py
  test_workflow_change_impact.py
  test_workflow_engine.py
  test_workflow_postgres.py
  test_workflow_splitting.py
.repo-standards.yml
AGENTS.md
compose.postgres.yaml
compose.tls.yaml
compose.yaml
pyproject.toml
README.md
````

# Files

## File: .github/workflows/ai-repo-map.yml
````yaml
name: Repository standards

on:
  push:
    branches: [main]
    paths-ignore:
      - ".ai/**"
  workflow_dispatch:

permissions:
  contents: write
  actions: read

concurrency:
  group: repo-standards-${{ github.repository }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  repository-standards:
    uses: dbrckk/repo-standards/.github/workflows/reusable-unified.yml@main
````

## File: .github/workflows/ci.yml
````yaml
name: CI

# Canonical verification gate. One-shot repair workflows must not persist on main.
on:
  push:
    branches: [main]
  pull_request:
  workflow_dispatch:

permissions:
  contents: read

jobs:
  python-compat:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    strategy:
      fail-fast: false
      matrix:
        python-version: ["3.11", "3.12"]
    steps:
      - name: Checkout
        uses: actions/checkout@v7

      - name: Set up Python
        uses: actions/setup-python@v7
        with:
          python-version: ${{ matrix.python-version }}
          cache: pip

      - name: Install
        run: python -m pip install -e ".[dev,postgres]"

      - name: Compile
        run: python -m compileall -q src

      - name: Compatibility tests
        run: pytest -q -m "not e2e"

  test:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_USER: production_os
          POSTGRES_PASSWORD: production_os
          POSTGRES_DB: production_os_test
        ports:
          - 5432:5432
        options: >-
          --health-cmd "pg_isready -U production_os -d production_os_test"
          --health-interval 5s
          --health-timeout 5s
          --health-retries 10
    env:
      PRODUCTION_OS_TEST_POSTGRES: postgresql://production_os:production_os@127.0.0.1:5432/production_os_test

    steps:
      - name: Checkout
        uses: actions/checkout@v7

      - name: Set up Python
        uses: actions/setup-python@v7
        with:
          python-version: "3.12"
          cache: pip

      - name: Install
        run: python -m pip install -e ".[dev,postgres]"

      - name: Compile
        run: python -m compileall -q src

      - name: Unit tests
        run: pytest -q -m "not e2e"

      - name: Production E2E
        run: pytest -q -m e2e

      - name: Build distribution
        run: python -m build

      - name: Verify wheel install
        run: |
          python -m venv /tmp/production-os-wheel
          /tmp/production-os-wheel/bin/python -m pip install --upgrade pip
          /tmp/production-os-wheel/bin/python -m pip install dist/*.whl
          /tmp/production-os-wheel/bin/production-os --help

      - name: Docker image smoke test
        run: |
          docker build -t production-os:ci .
          docker run --rm production-os:ci --help

      - name: CLI smoke test
        run: production-os --help
````

## File: .github/workflows/semantic-refresh.yml
````yaml
name: Precise semantic refresh

on:
  workflow_dispatch:
  schedule:
    - cron: "23 3 * * 1"

permissions:
  contents: write

concurrency:
  group: semantic-refresh-${{ github.repository }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  semantic:
    uses: dbrckk/repo-brain/.github/workflows/reusable-semantic.yml@main
    with:
      commit_changes: true
````

## File: .github/dependabot.yml
````yaml
version: 2
updates:
  - package-ecosystem: pip
    directory: "/"
    schedule:
      interval: weekly
    open-pull-requests-limit: 5

  - package-ecosystem: github-actions
    directory: "/"
    schedule:
      interval: weekly
    open-pull-requests-limit: 5
````

## File: .serena/project.yml
````yaml
project_name: "Production-OS"
language_servers:
  - python
ls_workspace_folders:
  - "."
ignore_all_files_in_gitignore: true
ignored_paths:
  - "**/.venv/**"
  - "**/__pycache__/**"
  - "**/.pytest_cache/**"
  - "**/dist/**"
  - "**/build/**"
read_only: false
encoding: utf-8
symbol_info_budget: 8
initial_prompt: |
  Use Serena's symbol and reference tools before reading whole files. Start with symbol overviews, find_symbol and find_referencing_symbols; fetch full file bodies only when required for the task. Prefer targeted edits and preserve the existing architecture.
````

## File: config/auth.example.json
````json
{
  "tokens": [
    {
      "name": "dashboard",
      "role": "viewer",
      "sha256": "<sha256-of-token>"
    },
    {
      "name": "worker-1",
      "role": "worker",
      "sha256": "<sha256-of-token>"
    },
    {
      "name": "operator",
      "role": "operator",
      "sha256": "<sha256-of-token>"
    }
  ]
}
````

## File: config/policy.example.json
````json
{
  "defaults": {
    "max_risk_class": "critical",
    "approval_required_from": "high",
    "allowed_worker_classes": ["python", "node", "android"],
    "freeze_timezone": "Europe/Paris",
    "freeze_windows": [
      {
        "days": ["fri", "sat", "sun"],
        "start": "18:00",
        "end": "08:00"
      }
    ],
    "freeze_risk_classes": ["high", "critical"],
    "require_branch_protection_for": ["high", "critical"],
    "auto_quarantine_after_failures": 3,
    "budgets": {
      "tokens": 1000000,
      "cost": 20,
      "minutes": 600
    },
    "slo": {
      "max_runtime_minutes": 120,
      "max_attempts": 5,
      "max_consecutive_failures": 3
    }
  },
  "portfolio_budgets": {
    "tokens": 5000000,
    "cost": 100,
    "minutes": 3000
  },
  "repositories": [
    {
      "match": "dbrckk/deadline-zero",
      "approval_required_from": "critical",
      "allowed_worker_classes": ["android"],
      "budgets": {
        "tokens": 1500000,
        "minutes": 900
      }
    },
    {
      "match": "dbrckk/ai-dev-server",
      "allowed_worker_classes": ["python", "node"]
    }
  ]
}
````

## File: config/workflow.example.json
````json
{
  "name": "android-release",
  "repository": "dbrckk/deadline-zero",
  "metadata": {
    "purpose": "Example fan-out/fan-in production workflow"
  },
  "tasks": [
    {
      "task_id": "build",
      "title": "Build debug and release artifacts",
      "priority": 100,
      "max_attempts": 2,
      "estimated_minutes": 8,
      "payload": {
        "required_capabilities": [
          "android"
        ],
        "handoff": {
          "task": "Build debug and release artifacts",
          "constraints": {
            "verify_before_completion": true
          }
        }
      }
    },
    {
      "task_id": "unit-tests",
      "title": "Run unit tests",
      "dependencies": [
        "build"
      ],
      "priority": 90,
      "max_attempts": 2,
      "estimated_minutes": 5,
      "payload": {
        "required_capabilities": [
          "android"
        ]
      }
    },
    {
      "task_id": "lint",
      "title": "Run Android lint",
      "dependencies": [
        "build"
      ],
      "priority": 80,
      "max_attempts": 2,
      "estimated_minutes": 4,
      "payload": {
        "required_capabilities": [
          "android"
        ]
      }
    },
    {
      "task_id": "package",
      "title": "Package release candidate",
      "dependencies": [
        "unit-tests",
        "lint"
      ],
      "priority": 70,
      "max_attempts": 1,
      "estimated_minutes": 3,
      "payload": {
        "required_capabilities": [
          "android"
        ]
      }
    }
  ]
}
````

## File: scripts/render-start.py
````python
#!/usr/bin/env python3
⋮----
def _required(name: str) -> str
⋮----
value = str(os.environ.get(name) or "").strip()
⋮----
def _auth_payload(worker_token: str, operator_token: str) -> dict
⋮----
def digest(value: str) -> str
⋮----
def main() -> None
⋮----
database_url = _required("DATABASE_URL")
worker_token = _required("PRODUCTION_OS_WORKER_TOKEN")
operator_token = _required("PRODUCTION_OS_OPERATOR_TOKEN")
port = str(os.environ.get("PORT") or "8787").strip()
⋮----
runtime_dir = Path(os.environ.get("PRODUCTION_OS_RUNTIME_DIR") or "/tmp/production-os")
⋮----
auth_path = runtime_dir / "auth.json"
⋮----
argv = [
````

## File: src/production_os/__init__.py
````python
"""Production-OS portfolio control plane."""
⋮----
__version__ = "0.1.0"
````

## File: src/production_os/adaptation_plan.py
````python
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
````

## File: src/production_os/adaptation.py
````python
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
````

## File: src/production_os/api_auth.py
````python
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
````

## File: src/production_os/approvals.py
````python
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
````

## File: src/production_os/asset_forge.py
````python
ASSET_FORGE_REPOSITORY = "dbrckk/asset-forge"
ASSET_FORGE_WORKFLOW = "production-os-dispatch.yml"
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
normalized = target_path.strip().replace("\\", "/").lstrip("/")
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
root = Path(output_root)
⋮----
produced: list[dict[str, Any]] = []
produced_by_id: dict[str, dict[str, Any]] = {}
ordered_items = _order_asset_batch(items)
⋮----
dependency_artifacts = []
⋮----
dependency = produced_by_id.get(dependency_id)
⋮----
target_path = str(item.get("target_path") or "").strip()
⋮----
source_path = str(item.get("source_path") or "").strip() or None
request_id = str(request.get("requestId") or f"item-{index+1}")
out = root / request_id
⋮----
raster_reference_suffixes = {".png", ".webp", ".jpg", ".jpeg"}
visual_reference_paths = [
⋮----
receipt = execute_asset_forge(
⋮----
report_path = Path(str(receipt.report_path))
⋮----
artifact = _validated_artifact(report, out)
produced_item = {
⋮----
delivered_to: list[str] = []
⋮----
root_worktree = Path(target_worktree).resolve()
staged = []
⋮----
normalized = item["target_path"].replace("\\", "/").lstrip("/")
destination = (root_worktree / normalized).resolve()
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
payload = {
result = gh.commit_files(
delivered_to = [
delivery_mode = "github"
⋮----
inputs = {
````

## File: src/production_os/asymmetric_attestations.py
````python
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
````

## File: src/production_os/atomic_io.py
````python
def atomic_write_text(path: str | Path, text: str) -> None
⋮----
destination = Path(path)
⋮----
def atomic_write_json(path: str | Path, payload: Any) -> None
````

## File: src/production_os/attestations.py
````python
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
````

## File: src/production_os/audit_checkpoint.py
````python
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
````

## File: src/production_os/audit_integrity.py
````python
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
````

## File: src/production_os/backup.py
````python
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
````

## File: src/production_os/budgets.py
````python
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
````

## File: src/production_os/builder_identity.py
````python
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
````

## File: src/production_os/callgraph.py
````python
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
````

## File: src/production_os/capabilities.py
````python
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
````

## File: src/production_os/change_impact.py
````python
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
````

## File: src/production_os/claims.py
````python
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
````

## File: src/production_os/classification.py
````python
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
````

## File: src/production_os/cli.py
````python
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
def run_asset_forge_dispatch(args: argparse.Namespace) -> int
⋮----
request = build_asset_forge_request(
receipt = execute_asset_forge(
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
````

## File: src/production_os/compatibility.py
````python
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
````

## File: src/production_os/components.py
````python
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
````

## File: src/production_os/control_plane.py
````python
class ControlPlane
⋮----
def _json_bytes(payload: dict | list) -> bytes
⋮----
DASHBOARD_HTML = """<!doctype html>
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
rows = db.execute(
workers = db.execute(
workflow_rows = db.execute(
⋮----
query = parse_qs(parsed.query)
⋮----
after = int(query.get("after", ["0"])[0])
limit = int(query.get("limit", ["100"])[0])
⋮----
key = parsed.path.split("/", 3)[-1]
⋮----
job = control.queue.get(key)
⋮----
parts = [part for part in parsed.path.split("/") if part]
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
def do_POST(self) -> None
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
body = self._read_json()
⋮----
principal = self._require("operator")
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
action = parts[3]
⋮----
workflow = control.workflows.cancel(workflow_id)
⋮----
release = control.releases.promote(
⋮----
artifact = control.workflows.add_artifact(
⋮----
worker = control.workers.register(
⋮----
principal = self._require("worker")
⋮----
worker = control.workers.heartbeat(
active_job_keys = body.get(
⋮----
stale_job_keys = []
⋮----
job = control.queue.get(str(key))
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
worker_id = str(body["worker_id"])
capabilities = [
⋮----
compatible = []
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
job = control.queue.ack(
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
````

## File: src/production_os/control_surface.py
````python
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
````

## File: src/production_os/controller.py
````python
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
````

## File: src/production_os/deep_fingerprint.py
````python
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
````

## File: src/production_os/delivery.py
````python
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
````

## File: src/production_os/dispatch.py
````python
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
````

## File: src/production_os/dual_sign.py
````python
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
````

## File: src/production_os/emergency.py
````python
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
````

## File: src/production_os/execution_feedback.py
````python
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
````

## File: src/production_os/execution_optimizer.py
````python
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
````

## File: src/production_os/fairness.py
````python
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
````

## File: src/production_os/feedback.py
````python
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
````

## File: src/production_os/github_client.py
````python
class GitHubAPIError(RuntimeError)
⋮----
class GitHubClient
⋮----
API = "https://api.github.com"
⋮----
def __init__(self, token: str | None = None, timeout: float = 20.0)
⋮----
def _get(self, path: str) -> Any
⋮----
request = urllib.request.Request(
⋮----
body = exc.read().decode("utf-8", errors="replace")
⋮----
def _request(self, method: str, path: str, payload: dict[str, Any] | None = None) -> Any
⋮----
data = None
⋮----
data = json.dumps(payload, separators=(",", ":")).encode("utf-8")
⋮----
body = response.read()
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
encoded = urllib.parse.quote(branch, safe="")
⋮----
payload = self._get(
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
def list_repositories(self, owner: str) -> list[dict[str, Any]]
⋮----
repos: list[dict[str, Any]] = []
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
runs = payload.get("workflow_runs", []) if isinstance(payload, dict) else []
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
````

## File: src/production_os/github_webhook.py
````python
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
````

## File: src/production_os/github_work_state.py
````python
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
````

## File: src/production_os/governance.py
````python
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
````

## File: src/production_os/graph.py
````python
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
````

## File: src/production_os/health_server.py
````python
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
````

## File: src/production_os/health.py
````python
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
````

## File: src/production_os/heartbeat_manager.py
````python
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
````

## File: src/production_os/history.py
````python
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
````

## File: src/production_os/journal.py
````python
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
````

## File: src/production_os/key_domains.py
````python
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
````

## File: src/production_os/key_registry.py
````python
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
````

## File: src/production_os/learning.py
````python
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
````

## File: src/production_os/locks.py
````python
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
````

## File: src/production_os/metrics.py
````python
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
````

## File: src/production_os/migration_registry.py
````python
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
````

## File: src/production_os/migrations.py
````python
def migrate_state_file(path: str | Path) -> dict
⋮----
source = Path(path)
⋮----
payload = json.loads(source.read_text(encoding="utf-8"))
schema = str(payload.get("schema_version", ""))
````

## File: src/production_os/models.py
````python
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
````

## File: src/production_os/observability.py
````python
def write_observability(payload: dict, path: str | Path) -> None
⋮----
destination = Path(path)
````

## File: src/production_os/policy_validation.py
````python
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
````

## File: src/production_os/policy.py
````python
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
````

## File: src/production_os/portfolio_optimizer.py
````python
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
````

## File: src/production_os/postgres_backend.py
````python
psycopg = None
dict_row = None
⋮----
def _utcnow() -> str
⋮----
class PostgresBackend
⋮----
SCHEMA_VERSION = 8
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
def recover_expired(self, *, max_attempts: int = 3) -> list[dict]
⋮----
actions = []
⋮----
target = (
⋮----
action = {
````

## File: src/production_os/preemption.py
````python
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
````

## File: src/production_os/quarantine.py
````python
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
````

## File: src/production_os/queue_maintenance.py
````python
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
````

## File: src/production_os/rate_limit.py
````python
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
````

## File: src/production_os/receipts.py
````python
path=Path(directory)
⋮----
dest=path/f"{key}.receipt.json"
payload={
````

## File: src/production_os/reconciliation.py
````python
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
````

## File: src/production_os/rekor_checkpoint_state.py
````python
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
````

## File: src/production_os/rekor_witness_quorum.py
````python
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
````

## File: src/production_os/release_ledger.py
````python
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
````

## File: src/production_os/remote_worker.py
````python
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
````

## File: src/production_os/resources.py
````python
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
````

## File: src/production_os/result_cache.py
````python
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
````

## File: src/production_os/reuse.py
````python
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
````

## File: src/production_os/runtime_state.py
````python
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
````

## File: src/production_os/scheduler.py
````python
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
````

## File: src/production_os/scoring.py
````python
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
````

## File: src/production_os/self_healing.py
````python
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
````

## File: src/production_os/signer_factory.py
````python
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
````

## File: src/production_os/signers.py
````python
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
````

## File: src/production_os/signing.py
````python
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
````

## File: src/production_os/source_tree.py
````python
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
````

## File: src/production_os/speculation.py
````python
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
````

## File: src/production_os/sqlite_backend.py
````python
def _utcnow() -> str
⋮----
class SQLiteBackend
⋮----
SCHEMA_VERSION = 8
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
def recover_expired(self, *, max_attempts: int = 3) -> list[dict]
⋮----
actions = []
⋮----
target = (
⋮----
action = {
````

## File: src/production_os/sqlite_migration.py
````python
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
````

## File: src/production_os/starlist.py
````python
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
````

## File: src/production_os/storage.py
````python
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
````

## File: src/production_os/supply_chain.py
````python
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
````

## File: src/production_os/task_capabilities.py
````python
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
````

## File: src/production_os/transparency_receipts.py
````python
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
````

## File: src/production_os/transparency.py
````python
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
````

## File: src/production_os/trends.py
````python
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
````

## File: src/production_os/trust_policy.py
````python
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
````

## File: src/production_os/validation.py
````python
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
````

## File: src/production_os/vault_auth.py
````python
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
````

## File: src/production_os/vault_signer.py
````python
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
````

## File: src/production_os/versioning.py
````python
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
````

## File: src/production_os/witness.py
````python
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
````

## File: src/production_os/workers.py
````python
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
````

## File: src/production_os/workflow_engine.py
````python
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
row = _execute(
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
````

## File: tests/test_adaptation_plan.py
````python
def assessment(name, profile, language)
⋮----
def test_plan_separates_reusable_and_coupled_components()
⋮----
source = assessment("source", "android-app", "Kotlin")
target = assessment("target", "android-game", "Kotlin")
⋮----
components = [
⋮----
plan = build_adaptation_plan(source, target, "android-play-billing", components)
⋮----
def test_plan_falls_back_to_architecture_pattern()
⋮----
source = assessment("source", "python-service", "Python")
target = assessment("target", "automation-platform", "Python")
components = [{
plan = build_adaptation_plan(source, target, "audit-trail", components)
````

## File: tests/test_adaptation.py
````python
def assessment(name, profile, language, components)
⋮----
def test_links_component_to_matching_test()
⋮----
component = Component(
test = Component(
src = assessment("source", "android-app", "Kotlin", [component, test])
links = link_tests(src, component)
⋮----
def test_tests_reduce_adaptation_risk()
⋮----
source = assessment("source", "android-app", "Kotlin", [component, test])
target = assessment("target", "android-game", "Kotlin", [])
scored = score_adaptation_risk(source, target, "android-play-billing", component)
````

## File: tests/test_api_auth.py
````python
def test_token_authorizer_roles()
⋮----
auth=TokenAuthorizer([
principal=auth.authenticate("secret")
````

## File: tests/test_approvals_migrations.py
````python
def test_approval_store(tmp_path)
⋮----
store=ApprovalStore(tmp_path/"approvals.json")
item=store.set("task-key",approved=True,approved_by="human",reason="ok")
⋮----
def test_runtime_state_v1_migration(tmp_path)
⋮----
path=tmp_path/"state.json"
⋮----
result=migrate_state_file(path)
````

## File: tests/test_asset_forge.py
````python
class FakeGitHub
⋮----
def __init__(self)
⋮----
def dispatch_workflow(self, repository, workflow, *, ref, inputs)
⋮----
def put_file(self, repository, path, content, *, message, branch)
⋮----
def commit_files(self, repository, files, *, message, branch)
⋮----
def test_build_asset_forge_request()
⋮----
request = build_asset_forge_request(
⋮----
def test_dispatch_asset_forge_uses_existing_workflow_contract()
⋮----
fake = FakeGitHub()
⋮----
receipt = dispatch_asset_forge(request, client=fake)
⋮----
def test_execute_asset_forge_auto_prefers_local_cli(tmp_path)
⋮----
out = tmp_path / "out"
⋮----
def fake_run(cmd, check=False, **kwargs)
⋮----
artifact = out / "hud-icon.svg"
⋮----
class Result
⋮----
returncode = 0
⋮----
receipt = execute_asset_forge(request, output_dir=str(out), mode="auto")
⋮----
def test_execute_asset_forge_auto_falls_back_to_github()
⋮----
receipt = execute_asset_forge(request, client=fake, mode="auto")
⋮----
def test_execute_asset_forge_delivers_to_worktree(tmp_path)
⋮----
worktree = tmp_path / "repo"
⋮----
receipt = execute_asset_forge(
⋮----
delivered = worktree / "assets/art/hud-icon.svg"
⋮----
def test_execute_asset_forge_delivers_with_existing_github_client(tmp_path)
⋮----
write = [call for call in fake.calls if "path" in call][0]
⋮----
def test_execute_asset_forge_batch_delivers_only_after_all_validate(tmp_path)
⋮----
out = tmp_path / "batch"
⋮----
requests = [
⋮----
request_path = Path(cmd[cmd.index("fulfill") + 1])
request = __import__("json").loads(request_path.read_text())
output = Path(cmd[cmd.index("--output-dir") + 1])
⋮----
artifact = output / f'{request["manifest"]["id"]}.svg'
⋮----
result = execute_asset_forge_batch(
⋮----
def test_execute_asset_forge_batch_aborts_delivery_when_one_asset_fails(tmp_path)
⋮----
existing = worktree / "assets/art/a.svg"
⋮----
calls = 0
⋮----
class Failed
⋮----
returncode = 1
⋮----
artifact = output / "a.svg"
⋮----
def test_execute_asset_forge_batch_uses_single_github_commit(tmp_path)
⋮----
asset_id = request["manifest"]["id"]
artifact = output / f"{asset_id}.svg"
⋮----
commits = [call for call in fake.calls if "files" in call]
⋮----
def test_execute_asset_forge_batch_respects_dependency_order(tmp_path)
⋮----
items = []
chain = [
⋮----
seen = []
⋮----
dependency = result["items"][-1]["dependency_artifacts"][0]
⋮----
def test_execute_asset_forge_batch_rejects_dependency_cycles(tmp_path)
⋮----
items = [
⋮----
def test_execute_asset_forge_batch_rejects_unknown_dependency(tmp_path)
⋮----
item = {
⋮----
def test_dependent_raster_asset_receives_validated_parent_reference(tmp_path)
⋮----
commands = []
⋮----
artifact = output / f"{asset_id}.png"
⋮----
child = commands[1]
⋮----
reference = Path(child[child.index("--reference") + 1])
````

## File: tests/test_asymmetric_attestations.py
````python
def validation()
⋮----
def test_public_key_validation_attestation()
⋮----
attestation=create_validation_attestation(
⋮----
verified=verify_validation_attestation(
⋮----
def test_release_provenance_is_offline_publicly_verifiable()
⋮----
approval_key=release_approval_key(
release={
provenance=create_release_provenance(
⋮----
def test_rotated_validator_keys_are_selected_by_key_id()
⋮----
def test_revoked_validator_key_is_rejected()
⋮----
def test_key_outside_validity_window_is_rejected()
````

## File: tests/test_attestations.py
````python
def validation()
⋮----
def test_validation_attestation_verifies_exact_bindings()
⋮----
attestation=create_validation_attestation(
⋮----
verified=verify_validation_attestation(
⋮----
def test_validation_attestation_rejects_binding_change()
⋮----
def test_validation_attestation_rejects_untrusted_validator()
⋮----
def test_release_provenance_detects_tampering()
⋮----
release={
provenance=create_release_provenance(
⋮----
def test_validation_attestation_rejects_expired_signature()
````

## File: tests/test_builder_identity_validation.py
````python
def policy(builder)
⋮----
def test_builder_identity_rejects_naive_not_before()
⋮----
def test_builder_identity_rejects_naive_not_after()
⋮----
def test_builder_identity_rejects_invalid_timestamp()
⋮----
def test_builder_identity_rejects_inverted_validity_window()
````

## File: tests/test_builder_identity.py
````python
def release(repository="owner/repo")
⋮----
def provenance()
⋮----
def policy(public_key)
⋮----
def test_trusted_builder_can_sign_authorized_repository()
⋮----
statement=create_slsa_statement(
envelope=sign_slsa_statement(
⋮----
def test_builder_is_rejected_for_other_repository()
````

## File: tests/test_builder_trust_rotation.py
````python
def release(repository, created_at)
⋮----
def provenance()
⋮----
def envelope(private_key, repository, signed_at, builder_id)
⋮----
item = release(repository, signed_at)
statement = create_slsa_statement(
⋮----
def test_builder_key_rotation_accepts_each_key_only_in_its_window()
⋮----
now = datetime.now(timezone.utc)
rotation = now - timedelta(minutes=20)
builder_id = "https://builder.example/prod"
repository = "dbrckk/example"
policy = BuilderTrustPolicy(
⋮----
old = envelope(
new = envelope(
stale = envelope(
⋮----
def test_revoked_builder_key_cannot_validate_new_slsa_statement()
⋮----
revoked_at = now - timedelta(minutes=10)
⋮----
signed = envelope(
⋮----
def test_builder_cannot_cross_repository_trust_boundary()
⋮----
now = datetime.now(timezone.utc).isoformat()
````

## File: tests/test_callgraph_versioning_feedback.py
````python
def assessment(name, docs, components=None)
⋮----
def test_version_compatibility_detects_major_mismatch()
⋮----
src = assessment("src", {"build.gradle.kts": 'implementation("com.example:lib:2.1.0")'})
dst = assessment("dst", {"build.gradle.kts": 'implementation("com.example:lib:1.9.0")'})
rows = compare_dependency_versions(src, dst)
⋮----
def test_feedback_blocks_required_failure()
⋮----
plan = [
result = summarize_validation_results(
````

## File: tests/test_capabilities_graph.py
````python
def evidence(name="demo", **kwargs)
⋮----
base = dict(
⋮----
def test_android_product_capabilities_are_extracted()
⋮----
caps = extract_capabilities(
names = {cap.name for cap in caps}
⋮----
def test_knowledge_graph_contains_repo_capability_edges()
⋮----
assessment = assess_repository(
graph = build_knowledge_graph([assessment])
⋮----
def test_visual_asset_platform_capabilities_are_extracted()
````

## File: tests/test_change_impact.py
````python
def _result(tasks, changed_paths)
⋮----
def test_change_impact_skips_unrelated_opt_in_tasks()
⋮----
tasks=[
result=_result(tasks,["android/app/Main.kt"])
⋮----
def test_change_impact_defaults_to_fail_safe_execution()
⋮----
rows=analyze_change_impact(
⋮----
def test_change_impact_empty_change_set_is_fail_closed()
⋮----
tasks=[{
row=analyze_change_impact(tasks,[])[0]
⋮----
def test_change_impact_can_explicitly_allow_empty_change_skip()
⋮----
def test_change_impact_excludes_generated_paths()
⋮----
row=analyze_change_impact(
⋮----
def test_change_impact_normalizes_windows_and_dot_paths()
⋮----
result=_result(
⋮----
def test_change_impact_propagates_to_downstream_tasks()
⋮----
result=_result(tasks,["src/core.py"])
````

## File: tests/test_claims_delivery.py
````python
def test_claim_ack_complete(tmp_path)
⋮----
store=ClaimStore(tmp_path/"claims.json")
claim=store.claim(
⋮----
def test_recover_unacked_job_releases_capacity(tmp_path)
⋮----
claims=ClaimStore(tmp_path/"claims.json")
runtime=RuntimeState(tmp_path/"runtime.json")
workers=WorkerRegistry(tmp_path/"workers.json")
⋮----
claim=claims.claim(
⋮----
queue=tmp_path/"queue"
⋮----
rows=recover_unacked_jobs(
````

## File: tests/test_classification_history_reuse.py
````python
def ev(name="demo", **kwargs)
⋮----
base = dict(
⋮----
def test_android_game_classification()
⋮----
profile = classify_repository(
⋮----
def test_regression_detection()
⋮----
old = {"repositories": {"owner/demo": {"score": 80}}}
assessment = assess_repository(ev())
current = build_snapshot("owner", [assessment])
regressions = detect_regressions(old, current, threshold=5)
⋮----
def test_cross_repo_reuse_detection()
⋮----
source = assess_repository(
target = assess_repository(
opportunities = detect_reuse([source, target])
capabilities = {item.capability for item in opportunities}
⋮----
def test_asset_production_platform_classification()
⋮----
def test_asset_production_capabilities_are_reusable_cross_profile()
⋮----
pairs = {(item.source, item.target, item.capability) for item in opportunities}
````

## File: tests/test_cli.py
````python
def test_control_plane_builder_trust_options_are_registered()
⋮----
args = _parse_args([
⋮----
def test_builder_trust_options_are_scoped_to_control_plane()
⋮----
def test_trust_status_parser_accepts_incident_filters()
⋮----
def test_trust_status_requires_database()
⋮----
def test_transparency_checkpoint_parser_accepts_rekor_publication_options()
⋮----
def test_transparency_checkpoint_verify_parser_accepts_rekor_receipt()
````

## File: tests/test_compatibility_validation.py
````python
def assessment(name, language="Kotlin", docs=None, signals=None)
⋮----
def test_dependency_compatibility_detects_target_dependency()
⋮----
target = assessment(
checks = check_dependency_compatibility(target, ["BillingClient", "UnknownDep"])
by_name = {item.dependency: item.status for item in checks}
⋮----
def test_android_validation_plan_is_complete()
⋮----
target = assessment("target")
plan = {
checks = [{"dependency": "BillingClient", "status": "available"}]
steps = build_validation_plan(target, "android-play-billing", plan, checks)
kinds = [step.kind for step in steps]
````

## File: tests/test_components.py
````python
def evidence(source_documents)
⋮----
def test_extracts_python_components_and_dependencies()
⋮----
components = extract_components(
billing = next(item for item in components if item.name == "BillingManager")
⋮----
def test_extracts_kotlin_class_with_capability_hint()
⋮----
component = next(item for item in components if item.name == "BillingManager")
````

## File: tests/test_control_plane_pr_impact.py
````python
def request(url, token, payload)
⋮----
req=urllib.request.Request(
⋮----
def test_control_plane_applies_pr_changed_paths(tmp_path, monkeypatch)
⋮----
class FakeGitHubClient
⋮----
def list_pull_request_files(self, repository, pr_number)
⋮----
auth=TokenAuthorizer([
control=ControlPlane(str(tmp_path/"db.sqlite"),authorizer=auth)
workflow=control.workflows.create(
⋮----
server=ThreadingHTTPServer(
thread=threading.Thread(target=server.serve_forever,daemon=True)
⋮----
base=f"http://127.0.0.1:{server.server_port}"
⋮----
tasks={
````

## File: tests/test_control_plane_release.py
````python
def get_request(url, token)
⋮----
req=urllib.request.Request(
⋮----
def request(url, token, payload)
⋮----
def test_control_plane_promote_and_rollback_release(tmp_path)
⋮----
auth=TokenAuthorizer([
control=ControlPlane(
workflow=control.workflows.create(
⋮----
artifact=control.workflows.add_artifact(
⋮----
server=ThreadingHTTPServer(
thread=threading.Thread(target=server.serve_forever,daemon=True)
⋮----
base=f"http://127.0.0.1:{server.server_port}"
⋮----
validation={
attestation=create_validation_attestation(
⋮----
promoted=payload["release"]
⋮----
rollback=payload["release"]
⋮----
ledger=control.releases.list_for_workflow(workflow["id"])
````

## File: tests/test_control_plane_webhook.py
````python
def signed_request(url, payload, delivery="delivery-1", secret="secret")
⋮----
body=json.dumps(payload).encode()
sig="sha256="+hmac.new(
req=urllib.request.Request(
⋮----
def test_signed_pr_webhook_refreshes_and_dispatches(tmp_path, monkeypatch)
⋮----
class FakeGitHubClient
⋮----
calls=0
⋮----
def list_pull_request_files(self, repository, pr_number)
⋮----
control=ControlPlane(
workflow=control.workflows.create(
⋮----
server=ThreadingHTTPServer(
thread=threading.Thread(target=server.serve_forever,daemon=True)
⋮----
base=f"http://127.0.0.1:{server.server_port}"
payload={
⋮----
new_workflow_id=result["workflows"][0]["workflow_id"]
⋮----
old=control.workflows.get(workflow["id"])
⋮----
def test_webhook_rejects_bad_signature(tmp_path)
⋮----
body=b'{"action":"opened"}'
⋮----
def test_webhook_creates_unseen_pr_from_template(tmp_path, monkeypatch)
⋮----
template=control.workflows.create(
⋮----
workflow=result["workflows"][0]["workflow"]
````

## File: tests/test_control_plane.py
````python
def request(url, token, payload=None)
⋮----
data=None if payload is None else json.dumps(payload).encode()
req=urllib.request.Request(
⋮----
body=response.read()
⋮----
def test_control_plane_worker_and_queue(tmp_path)
⋮----
auth=TokenAuthorizer([
control=ControlPlane(str(tmp_path/"db.sqlite"),authorizer=auth)
server=ThreadingHTTPServer(("127.0.0.1",0),make_handler(control))
thread=threading.Thread(target=server.serve_forever,daemon=True)
⋮----
base=f"http://127.0.0.1:{server.server_port}"
⋮----
key=claimed["job"]["key"]
⋮----
def test_trust_status_endpoint_requires_auth_and_forwards_filters(tmp_path)
⋮----
captured={}
⋮----
def trust_status(**kwargs)
⋮----
url=(
⋮----
req=urllib.request.Request(base+"/v1/trust-status",method="GET")
⋮----
payload=json.loads(exc.read())
⋮----
def test_incident_history_endpoints_require_auth_and_forward_filter(tmp_path)
⋮----
req=urllib.request.Request(base+path,method="GET")
⋮----
def test_incident_snapshot_requires_operator_and_reports_dedup(tmp_path)
⋮----
calls=[]
def snapshot(**kwargs)
⋮----
payload=json.dumps({
⋮----
body=json.loads(response.read())
⋮----
def test_incident_snapshot_rejects_invalid_payload_shapes(tmp_path)
⋮----
def post(payload)
⋮----
body=post({"unexpected":"value"})
⋮----
def test_http_body_parser_rejects_invalid_json_and_oversized_payload(tmp_path)
⋮----
def test_github_webhook_returns_413_for_oversized_body(tmp_path)
⋮----
control=ControlPlane(
⋮----
def test_generic_post_returns_413_before_endpoint_processing(tmp_path)
````

## File: tests/test_controller_asset_capabilities.py
````python
def _assessment(profile="android-game", language="Kotlin")
⋮----
def test_visual_task_requires_visual_asset_worker()
⋮----
handoff = {
required = _required_capabilities_for(_assessment(), handoff)
⋮----
def test_asset_forge_availability_alone_does_not_require_visual_worker()
⋮----
def test_visual_handoff_declares_asset_forge_machine_contract()
⋮----
action = SimpleNamespace(
⋮----
handoff = _handoff_for_action(action, [])
⋮----
contract = handoff["tool_contracts"]["asset_forge"]
⋮----
def test_3d_generation_handoff_declares_3d_worker_capability()
⋮----
def test_android_visual_job_selects_ai_dev_style_worker()
⋮----
handoff = {"task": "Create and integrate new enemy sprites"}
⋮----
registry = WorkerRegistry(Path(td) / "workers.json")
⋮----
worker = select_worker(registry, required)
````

## File: tests/test_dashboard_launch.py
````python
def test_dashboard_daily_surface_is_repo_instruction_only()
⋮----
def test_dashboard_pairing_is_hidden_from_normal_surface()
````

## File: tests/test_deep_fingerprint_starlist.py
````python
def test_deep_fingerprint_detects_real_dependencies()
⋮----
evidence = RepoEvidence(
signals = analyze_source_evidence(evidence)
values = {(signal.kind, signal.value) for signal in signals}
⋮----
def test_starlist_catalog_is_ranked_by_score_and_match()
⋮----
catalog = {
refs = suggest_external_references("backtesting", catalog)
````

## File: tests/test_emergency_key_revocation.py
````python
def test_compromised_key_is_rejected_even_for_precompromise_signature()
⋮----
registry = TrustedKeyRegistry({
kid = key_id(load_public_key(public_key))
historical = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
⋮----
def test_normal_revocation_preserves_pre_revocation_history()
⋮----
now = datetime.now(timezone.utc)
revoked_at = now - timedelta(days=1)
⋮----
resolved = registry.resolve(
⋮----
def test_compromise_semantics_apply_to_builder_key_registry()
````

## File: tests/test_execution_feedback_trends.py
````python
def test_blocked_validation_rolls_back()
⋮----
decision = decide_execution_outcome(70, 75, {"status":"blocked"})
⋮----
def test_validated_improvement_promotes()
⋮----
decision = decide_execution_outcome(70, 80, {"status":"passed"})
⋮----
def test_trend_detects_regression()
⋮----
snapshots = [
trends = build_trends(snapshots)
````

## File: tests/test_execution_optimizer_postgres.py
````python
DSN=os.getenv("PRODUCTION_OS_TEST_POSTGRES")
pytestmark=pytest.mark.skipif(not DSN,reason="postgres not configured")
⋮----
def test_optimizer_postgres()
⋮----
backend=PostgresBackend(DSN)
⋮----
opt=ExecutionOptimizer(backend)
⋮----
placement=opt.choose_worker(
````

## File: tests/test_execution_optimizer.py
````python
def test_predictions_and_worker_placement(tmp_path)
⋮----
backend=SQLiteBackend(tmp_path/"db.sqlite")
opt=ExecutionOptimizer(backend)
⋮----
prediction=opt.task_prediction("o/a","Build")
⋮----
workers=[
placement=opt.choose_worker(
⋮----
def test_reliability_penalizes_flaky_worker(tmp_path)
````

## File: tests/test_fairness.py
````python
class Action
⋮----
def __init__(self, repository, task)
⋮----
def test_round_robin_preserves_repo_internal_order()
⋮----
rows=[
result=round_robin_by_repository(rows)
````

## File: tests/test_github_client_pr_files.py
````python
class FakeGitHubClient(GitHubClient)
⋮----
def __init__(self, pages)
⋮----
def _get(self, path)
⋮----
page = int(path.rsplit("page=", 1)[1])
value = self.pages[page - 1]
⋮----
def test_list_pull_request_files_collects_and_deduplicates()
⋮----
first = [
second = [
client = FakeGitHubClient([first, second])
⋮----
files = client.list_pull_request_files("o/a", 7)
⋮----
def test_list_pull_request_files_ignores_empty_rows()
⋮----
client = FakeGitHubClient([[
⋮----
def test_list_pull_request_files_fails_closed_on_api_error()
⋮----
client = FakeGitHubClient([
⋮----
def test_list_pull_request_files_rejects_invalid_payload()
⋮----
client = FakeGitHubClient([{"files":[]}])
````

## File: tests/test_github_client_put_file.py
````python
class FakeWriteClient(GitHubClient)
⋮----
def __init__(self, existing=None)
⋮----
def _get(self, path)
⋮----
def _request(self, method, path, payload=None)
⋮----
def test_put_file_creates_new_content_without_sha()
⋮----
client = FakeWriteClient()
result = client.put_file(
⋮----
def test_put_file_updates_existing_content_with_sha()
⋮----
client = FakeWriteClient({"sha": "existing-sha"})
⋮----
payload = client.requests[0][2]
````

## File: tests/test_github_webhook.py
````python
def signature(secret, body)
⋮----
def test_verify_github_signature()
⋮----
body=b'{"x":1}'
sig=signature("secret",body)
⋮----
def test_parse_and_target_supported_pr_event()
⋮----
payload={
body=json.dumps(payload).encode()
parsed=parse_github_webhook(body)
⋮----
def test_unsupported_pr_action_is_ignored()
⋮----
def test_invalid_pr_payload_fails_closed()
⋮----
def test_delivery_store_is_idempotent_and_releasable(tmp_path)
⋮----
backend=SQLiteBackend(tmp_path/"db.sqlite")
store=WebhookDeliveryStore(backend)
````

## File: tests/test_github_work_state.py
````python
def state(**kwargs)
⋮----
base = dict(
⋮----
def test_merged_pr_promotes()
⋮----
def test_failed_ci_retries()
⋮----
def test_closed_unmerged_pr_replans()
````

## File: tests/test_governance.py
````python
def test_auto_quarantine_after_failures(tmp_path)
⋮----
runtime=RuntimeState(tmp_path/"runtime.json")
rec=runtime.get("o/a","task")
⋮----
quarantine=QuarantineStore(tmp_path/"quarantine.json")
policies=PolicySet({
actions=apply_governance(runtime,policies,quarantine)
````

## File: tests/test_health_metrics.py
````python
def test_health_degrades_with_open_circuit(tmp_path)
⋮----
state = RuntimeState(tmp_path / "state.json")
rec = state.get("o/a","task")
⋮----
health = build_health(state, {"last_error":None})
⋮----
def test_metrics_persist(tmp_path)
⋮----
store = MetricsStore(tmp_path / "metrics.json")
⋮----
loaded = MetricsStore(tmp_path / "metrics.json")
````

## File: tests/test_http_security_headers.py
````python
SECURITY_HEADERS = {
⋮----
def _server(tmp_path)
⋮----
control = ControlPlane(
server = ThreadingHTTPServer(
thread = threading.Thread(
⋮----
def _assert_security_headers(response)
⋮----
def test_json_health_response_has_security_headers(tmp_path)
⋮----
server = _server(tmp_path)
⋮----
url = f"http://127.0.0.1:{server.server_port}/health"
⋮----
def test_dashboard_html_response_has_security_headers(tmp_path)
⋮----
url = f"http://127.0.0.1:{server.server_port}/dashboard"
⋮----
def test_server_header_avoids_version_fingerprinting(tmp_path)
⋮----
url = f"http://127.0.0.1:{server.server_port}/healthz"
⋮----
def test_unsupported_write_methods_return_json_405(tmp_path)
⋮----
request = urllib.request.Request(
````

## File: tests/test_incident_history.py
````python
def ledger(tmp_path)
⋮----
backend = SQLiteBackend(tmp_path / "state.sqlite")
⋮----
def test_incident_history_is_hash_chained_and_verifiable(tmp_path, monkeypatch)
⋮----
item = ledger(tmp_path)
reports = iter([
⋮----
first = item.record_incident_report()
second = item.record_incident_report()
⋮----
verification = item.verify_incident_history()
⋮----
def test_incident_history_detects_report_tampering(tmp_path, monkeypatch)
⋮----
report = {
⋮----
row = db.execute(
⋮----
payload = json.loads(row["report_json"])
⋮----
def test_incident_snapshot_deduplicates_unchanged_state(tmp_path, monkeypatch)
⋮----
counter = {"n": 0}
⋮----
def report(**kwargs)
⋮----
def test_incident_snapshot_records_changed_blast_radius(tmp_path, monkeypatch)
⋮----
state = {"affected": 1}
⋮----
n = state["affected"]
releases = [
⋮----
def test_concurrent_identical_incident_snapshots_preserve_single_chain_entry(tmp_path, monkeypatch)
⋮----
barrier = threading.Barrier(4)
results = []
errors = []
⋮----
def worker()
⋮----
threads = [threading.Thread(target=worker) for _ in range(4)]
⋮----
history = item.incident_history()
⋮----
def test_concurrent_distinct_incident_snapshots_keep_linear_hash_chain(tmp_path, monkeypatch)
⋮----
local = threading.local()
⋮----
key = kwargs["key_id"]
suffix = key.rsplit(":", 1)[-1]
⋮----
barrier = threading.Barrier(2)
⋮----
def worker(key)
⋮----
threads = [
⋮----
def test_failed_incident_insert_rolls_back_without_corrupting_chain(tmp_path, monkeypatch)
⋮----
reports = {
⋮----
first = item.record_incident_report(key_id="sha256:one")
⋮----
original_execute = module._execute
failed = {"done": False}
⋮----
def fail_insert(db, backend, statement, params=())
⋮----
second = item.record_incident_report(key_id="sha256:two")
````

## File: tests/test_key_domains.py
````python
def test_distinct_key_domains_are_accepted()
⋮----
result=assert_separate_key_domains(
⋮----
def test_validator_builder_key_reuse_is_rejected()
⋮----
def test_builder_provenance_private_key_reuse_is_rejected()
````

## File: tests/test_key_registry_validation.py
````python
def entry(public_key, **extra)
⋮----
def test_registry_rejects_inverted_key_validity_window()
⋮----
def test_registry_rejects_revocation_before_activation()
⋮----
def test_registry_rejects_duplicate_key_for_same_owner()
⋮----
def test_same_public_key_can_be_explicitly_trusted_by_different_owners()
⋮----
registry = TrustedKeyRegistry({
````

## File: tests/test_key_rotation.py
````python
def validation()
⋮----
def make_attestation(private_key, *, issued_at)
⋮----
def verify(attestation, registry)
⋮----
def test_validator_key_rotation_accepts_old_and_new_keys_in_their_windows()
⋮----
now = datetime.now(timezone.utc)
rotation = now - timedelta(minutes=20)
⋮----
registry = {
⋮----
old_attestation = make_attestation(
new_attestation = make_attestation(
⋮----
def test_validator_key_rotation_rejects_old_key_after_cutover()
⋮----
attestation = make_attestation(
⋮----
def test_revoked_validator_key_is_rejected_at_and_after_revocation()
⋮----
revoked_at = now - timedelta(minutes=20)
⋮----
def test_registry_rejects_key_id_that_does_not_match_public_key()
⋮----
def test_generated_signature_key_id_matches_registry_identity()
````

## File: tests/test_learning_control_surface.py
````python
def test_learning_rewards_successful_history()
⋮----
events = [
signals = build_learning_signals(events)
⋮----
def test_control_surface_contains_schedule()
⋮----
html = render_control_surface({
````

## File: tests/test_observability.py
````python
def test_observability_payload_contains_all_sections()
⋮----
payload = build_observability_payload(
````

## File: tests/test_p6_hardening.py
````python
def test_atomic_write_and_lock(tmp_path)
⋮----
path = tmp_path / "state.json"
⋮----
def test_emergency_stop(tmp_path)
⋮----
path = tmp_path / "stop.json"
⋮----
def test_audit_hash_chain(tmp_path)
⋮----
path = tmp_path / "audit.jsonl"
prev = "0" * 64
event = {"x": 1}
h = hash_event(prev, event)
⋮----
def test_rate_limit()
⋮----
result = check_rate_limit([], limit=2, window_seconds=60)
````

## File: tests/test_policy_budgets.py
````python
def test_high_risk_requires_approval()
⋮----
policies=PolicySet({
decision=evaluate_policy(
⋮----
def test_budget_blocks_projected_usage(tmp_path)
⋮----
ledger=BudgetLedger(tmp_path/"budget.json")
⋮----
decision=ledger.check("o/a",{"tokens":100},{"tokens":20})
````

## File: tests/test_policy_validation.py
````python
def test_valid_policy_payload()
⋮----
result=validate_policy_payload({
⋮----
def test_invalid_policy_payload()
````

## File: tests/test_portfolio_claim_api.py
````python
def api(base, path, token, payload=None)
⋮----
data=None if payload is None else json.dumps(payload).encode("utf-8")
request=urllib.request.Request(
⋮----
raw=response.read()
⋮----
def test_claim_uses_portfolio_criticality(tmp_path)
⋮----
auth=TokenAuthorizer([
control=ControlPlane(str(tmp_path/"db.sqlite"),authorizer=auth)
⋮----
workflow=control.workflows.create(
⋮----
independent=control.queue.enqueue({
⋮----
server=ThreadingHTTPServer(("127.0.0.1",0),make_handler(control))
thread=threading.Thread(target=server.serve_forever,daemon=True)
⋮----
base=f"http://127.0.0.1:{server.server_port}"
````

## File: tests/test_portfolio_optimizer.py
````python
def test_critical_blocking_job_is_ranked_first(tmp_path)
⋮----
backend=SQLiteBackend(tmp_path/"db.sqlite")
queue=SQLiteJobQueue(backend)
workflows=WorkflowEngine(backend,queue)
execution=ExecutionOptimizer(backend)
optimizer=PortfolioOptimizer(workflows,execution)
⋮----
wf=workflows.create(
⋮----
critical_job=queue.peek_candidates()[0]
⋮----
independent=queue.enqueue({
⋮----
ranked=optimizer.rank([independent,critical_job])
````

## File: tests/test_postgres_backend.py
````python
DSN=os.getenv("PRODUCTION_OS_TEST_POSTGRES")
⋮----
pytestmark=pytest.mark.skipif(
⋮----
def reset(backend)
⋮----
def test_postgres_runtime_workers_and_queue()
⋮----
backend=PostgresBackend(DSN)
⋮----
state=PostgresRuntimeState(backend)
lease=state.acquire_lease("o/a","task","worker-1")
⋮----
workers=PostgresWorkerRegistry(backend)
⋮----
queue=PostgresJobQueue(backend)
queued=queue.enqueue({
claimed=queue.claim_next("worker-1",capabilities=["python"])
````

## File: tests/test_preemption.py
````python
def test_safe_preemption_requires_interruptible_and_priority_gap(tmp_path)
⋮----
state = RuntimeState(tmp_path/"state.json")
workers = WorkerRegistry(tmp_path/"workers.json")
⋮----
rec = state.get("o/a","low")
⋮----
decision = choose_preemption_victim(
⋮----
paused = confirm_checkpoint_and_release(
````

## File: tests/test_production_stack_e2e.py
````python
def _api(base: str, path: str, token: str, payload=None)
⋮----
data = None if payload is None else json.dumps(payload).encode("utf-8")
request = urllib.request.Request(
⋮----
raw = response.read()
⋮----
@contextmanager
def _isolated_postgres_database(base_dsn: str, run_id: str)
⋮----
database_name = f"production_os_e2e_{run_id[:24]}"
admin_dsn = make_conninfo(base_dsn, dbname="postgres")
test_dsn = make_conninfo(base_dsn, dbname=database_name)
⋮----
@pytest.mark.e2e
def test_postgres_http_worker_workflow_release_pipeline_end_to_end()
⋮----
base_database = os.getenv("PRODUCTION_OS_TEST_POSTGRES")
⋮----
run_id = uuid.uuid4().hex
operator_token = f"operator-{run_id}"
worker_token = f"worker-{run_id}"
worker_id = f"python-e2e-{run_id}"
repository = f"e2e/production-stack-{run_id}"
source_revision = f"revision-{run_id}"
validator_id = f"validator-{run_id}"
validator_secret = f"validator-secret-{run_id}"
provenance_secret = f"provenance-secret-{run_id}"
⋮----
auth = TokenAuthorizer(
⋮----
control = ControlPlane(
server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(control))
thread = threading.Thread(target=server.serve_forever, daemon=True)
⋮----
base = f"http://127.0.0.1:{server.server_port}"
⋮----
workflow_id = created["workflow"]["id"]
⋮----
worker = RemoteWorkerClient(
⋮----
build_job = worker.claim()
⋮----
package_job = worker.claim()
⋮----
artifact_sha256 = hashlib.sha256(run_id.encode("utf-8")).hexdigest()
⋮----
artifact = artifact_payload["artifact"]
⋮----
validation = {
attestation = create_validation_attestation(
⋮----
release = promoted_payload["release"]
⋮----
verification = verified_payload["verification"]
````

## File: tests/test_provenance_signer.py
````python
def test_release_provenance_can_be_signed_via_signer()
⋮----
signer=PemSigner(private_key)
approval_key=release_approval_key(
release={
attestation={
provenance=create_release_provenance_with_signer(
````

## File: tests/test_queue_audit_checkpoint.py
````python
def test_compact_completed_queue(tmp_path)
⋮----
claims=ClaimStore(tmp_path/"claims.json")
claim=claims.claim(key="k1",worker_id="w",repository="o/a",task="t")
⋮----
queue=tmp_path/"queue"
⋮----
rows=compact_queue(queue_dir=queue,claims=claims)
⋮----
def test_retry_dead_letter(tmp_path)
⋮----
dead=tmp_path/"dead"
⋮----
rows=retry_dead_letters(
⋮----
def test_signed_audit_checkpoint(tmp_path)
⋮----
journal=ExecutionJournal(tmp_path/"audit.jsonl")
⋮----
checkpoint=tmp_path/"checkpoint.json"
````

## File: tests/test_reconciliation_dispatch.py
````python
def test_reconcile_expired_running_lease(tmp_path)
⋮----
state = RuntimeState(tmp_path / "state.json")
rec = state.get("o/a", "task")
⋮----
actions = reconcile_runtime_state(state)
⋮----
def test_dispatch_is_idempotent_guarded(tmp_path)
⋮----
result = dispatch_handoff(
````

## File: tests/test_rekor_checkpoint_state_cli.py
````python
def _receipt() -> dict
⋮----
root_hash = hashlib.sha256(b"rekor-root").hexdigest()
root_b64 = base64.b64encode(bytes.fromhex(root_hash)).decode("ascii")
checkpoint = (
⋮----
database = tmp_path / "state.db"
backend = SQLiteBackend(database)
⋮----
class Ledger
⋮----
def __init__(self)
⋮----
def verify_transparency(self)
⋮----
receipt = _receipt()
⋮----
class FakePublisher
⋮----
timeout_seconds = 10.0
⋮----
@classmethod
        def from_private_key(cls, *args, **kwargs)
⋮----
def publish(self, envelope)
⋮----
witness_key = tmp_path / "witness.pem"
⋮----
rekor_key = tmp_path / "rekor.pem"
⋮----
log_key = tmp_path / "rekor-log.pem"
⋮----
receipt_output = tmp_path / "receipt.json"
⋮----
args = argparse.Namespace(
⋮----
result = json.loads(capsys.readouterr().out)
⋮----
stored = RekorCheckpointStateStore(backend).get(
````

## File: tests/test_rekor_checkpoint_state_concurrency.py
````python
def _leaf(payload: bytes) -> bytes
⋮----
def _node(left: bytes, right: bytes) -> bytes
⋮----
def _checkpoint(root_hash: str, tree_size: int) -> str
⋮----
root_b64 = base64.b64encode(bytes.fromhex(root_hash)).decode("ascii")
⋮----
def _receipt(root_hash: str, tree_size: int) -> dict
⋮----
def test_slow_observer_cannot_overwrite_newer_checkpoint_state(tmp_path)
⋮----
backend = SQLiteBackend(tmp_path / "state.db")
store = RekorCheckpointStateStore(backend)
first = _leaf(b"first")
second = _leaf(b"second")
third = _leaf(b"third")
size_two_root = _node(first, second)
size_three_root = _node(size_two_root, third)
⋮----
def proof_fetcher(**_)
⋮----
monitor = RekorCheckpointMonitor(store, proof_fetcher=proof_fetcher)
⋮----
persisted = store.get("a" * 64, "rekor.example - 42")
⋮----
def test_concurrent_first_observation_cannot_replace_bootstrap_state(tmp_path)
⋮----
trusted_root = _leaf(b"trusted").hex()
competing_root = _leaf(b"competing").hex()
⋮----
class RacingStore(RekorCheckpointStateStore)
⋮----
raced = False
⋮----
def get(self, log_id, origin)
⋮----
current = super().get(log_id, origin)
⋮----
store = RacingStore(backend)
monitor = RekorCheckpointMonitor(
⋮----
persisted = RekorCheckpointStateStore(backend).get(
````

## File: tests/test_rekor_checkpoint_state_postgres.py
````python
DSN = os.getenv("PRODUCTION_OS_TEST_POSTGRES")
⋮----
pytestmark = pytest.mark.skipif(
⋮----
def test_rekor_checkpoint_state_round_trips_on_postgres()
⋮----
backend = PostgresBackend(DSN)
store = RekorCheckpointStateStore(backend)
log_id = hashlib.sha256(b"rekor-checkpoint-state-postgres").hexdigest()
origin = "rekor.example - 4242"
root_hash = hashlib.sha256(b"root").hexdigest()
⋮----
stored = store.put(
loaded = store.get(log_id, origin)
````

## File: tests/test_rekor_checkpoint_state.py
````python
def _leaf(payload: bytes) -> bytes
⋮----
def _node(left: bytes, right: bytes) -> bytes
⋮----
def _checkpoint(root_hash: str, tree_size: int, tree_id: int = 42) -> str
⋮----
root_b64 = base64.b64encode(bytes.fromhex(root_hash)).decode("ascii")
⋮----
def _receipt(root_hash: str, tree_size: int, *, log_id: str = "a" * 64) -> dict
⋮----
def test_verify_consistency_proof_accepts_one_to_two_leaf_growth()
⋮----
first = _leaf(b"first")
second = _leaf(b"second")
new_root = _node(first, second)
⋮----
def test_monitor_bootstraps_and_persists_first_verified_checkpoint(tmp_path)
⋮----
backend = SQLiteBackend(tmp_path / "state.db")
store = RekorCheckpointStateStore(backend)
⋮----
monitor = RekorCheckpointMonitor(
root = _leaf(b"first").hex()
⋮----
result = monitor.observe_verified_receipt(_receipt(root, 1))
persisted = store.get("a" * 64, "rekor.example - 42")
⋮----
def test_monitor_advances_only_with_valid_consistency_proof(tmp_path)
⋮----
bootstrap = RekorCheckpointMonitor(
⋮----
observed = {}
⋮----
def proof_fetcher(**kwargs)
⋮----
monitor = RekorCheckpointMonitor(store, proof_fetcher=proof_fetcher)
result = monitor.observe_verified_receipt(_receipt(new_root.hex(), 2))
⋮----
def test_monitor_rejects_split_view_without_overwriting_state(tmp_path)
⋮----
original_root = _leaf(b"first").hex()
⋮----
def test_monitor_rejects_invalid_growth_proof_without_overwriting_state(tmp_path)
⋮----
def test_monitor_rejects_tree_rollback(tmp_path)
````

## File: tests/test_rekor_consistency_client.py
````python
def test_consistency_client_calls_rekor_v1_proof_endpoint(monkeypatch)
⋮----
observed = {}
⋮----
class Response
⋮----
status = 200
⋮----
def __enter__(self)
⋮----
def __exit__(self, *args)
⋮----
def read(self)
⋮----
def fake_urlopen(request, timeout)
⋮----
client = RekorV1ConsistencyClient(
result = client.fetch(first_size=10, last_size=20, tree_id="42")
````

## File: tests/test_rekor_signed_checkpoint_receipt.py
````python
def _envelope()
⋮----
def _canonical(value)
⋮----
def _leaf_hash(payload: bytes) -> str
⋮----
def _signed_checkpoint(private_key, public_key, root_hash: str) -> str
⋮----
note = (
der = public_key.public_bytes(
key_hint = hashlib.sha256(der).digest()[:4]
digest = hashlib.sha256(note.encode("utf-8")).digest()
signature = private_key.sign(
encoded = base64.b64encode(key_hint + signature).decode("ascii")
⋮----
def _receipt()
⋮----
envelope = _envelope()
log_private = ec.generate_private_key(ec.SECP256R1())
log_public = log_private.public_key()
log_public_pem = log_public.public_bytes(
log_public_der = log_public.public_bytes(
log_id = hashlib.sha256(log_public_der).hexdigest()
⋮----
proposed = build_rekor_v1_hashedrekord(
body = _canonical(proposed)
root_hash = _leaf_hash(body)
checkpoint = _signed_checkpoint(log_private, log_public, root_hash)
entry = {
set_signature = log_private.sign(
⋮----
receipt = parse_rekor_v1_receipt(
⋮----
def test_verified_receipt_rejects_tampered_signed_checkpoint()
⋮----
tampered = copy.deepcopy(receipt)
````

## File: tests/test_rekor_signed_checkpoint.py
````python
def _log_keypair()
⋮----
private_key = ec.generate_private_key(ec.SECP256R1())
public_key = private_key.public_key()
public_pem = public_key.public_bytes(
public_der = public_key.public_bytes(
key_hint = hashlib.sha256(public_der).digest()[:4]
⋮----
note = (
digest = hashlib.sha256(note.encode("utf-8")).digest()
signature = private_key.sign(
encoded = base64.b64encode(key_hint + signature).decode("ascii")
⋮----
def test_verify_rekor_signed_checkpoint_authenticates_root_and_tree_size()
⋮----
root_hash = hashlib.sha256(b"root").hexdigest()
checkpoint = _signed_checkpoint(
````

## File: tests/test_rekor_v1_key_compatibility.py
````python
def _ec_private_pem()
⋮----
private_key = ec.generate_private_key(ec.SECP256R1())
⋮----
def test_rekor_v1_hashedrekord_accepts_ecdsa_pkix_signing_key()
⋮----
private_pem = _ec_private_pem()
publisher = RekorV1Publisher.from_private_key(
⋮----
public_key = serialization.load_pem_public_key(
signature = publisher.signer(b"checkpoint")
⋮----
def test_rekor_v1_hashedrekord_rejects_ed25519_key()
````

## File: tests/test_rekor_witness_quorum_cli.py
````python
def _receipt() -> dict
⋮----
root_hash = hashlib.sha256(b"rekor-root").hexdigest()
root_b64 = base64.b64encode(bytes.fromhex(root_hash)).decode("ascii")
checkpoint = (
⋮----
def test_checkpoint_parser_accepts_rekor_witness_config()
⋮----
args = cli._parse_args(
⋮----
database = tmp_path / "state.db"
backend = SQLiteBackend(database)
⋮----
class Ledger
⋮----
def __init__(self)
⋮----
def verify_transparency(self)
⋮----
class FakePublisher
⋮----
@classmethod
        def from_private_key(cls, *args, **kwargs)
⋮----
def publish(self, envelope)
⋮----
observed = {}
⋮----
def fake_collect(config, **kwargs)
⋮----
witness_key = tmp_path / "witness.pem"
⋮----
rekor_key = tmp_path / "rekor.pem"
⋮----
log_key = tmp_path / "rekor-log.pem"
⋮----
receipt_output = tmp_path / "receipt.json"
⋮----
args = argparse.Namespace(
````

## File: tests/test_rekor_witness_quorum.py
````python
observation = {
⋮----
def test_quorum_accepts_two_matching_valid_witnesses_out_of_three()
⋮----
keypairs = [generate_keypair() for _ in range(3)]
responses = [
public_keys = {
⋮----
result = evaluate_rekor_witness_quorum(
⋮----
def test_quorum_rejects_invalid_signature_and_fails_below_threshold()
⋮----
first = _signed_observation("w1", private1)
second = _signed_observation("w2", private2)
⋮----
def test_quorum_fails_closed_on_valid_same_size_conflicting_root()
⋮----
signed = _signed_observation("w1", private_key)
observed = {}
⋮----
class Response
⋮----
status = 200
⋮----
def __enter__(self)
⋮----
def __exit__(self, *args)
⋮----
def read(self)
⋮----
def fake_urlopen(request, timeout)
⋮----
result = RekorWitnessClient(
⋮----
def test_witness_observation_store_persists_signed_audit_record(tmp_path)
⋮----
response = _signed_observation("w1", private_key)
store = RekorWitnessObservationStore(
⋮----
stored = store.record(
rows = store.list_for_tree(
⋮----
def test_load_witness_config_resolves_relative_public_key_paths(tmp_path)
⋮----
config_path = tmp_path / "witnesses.json"
⋮----
config = load_rekor_witness_config(config_path)
⋮----
signed = {
⋮----
def fake_observe(self, **kwargs)
⋮----
config = {
⋮----
result = collect_rekor_witness_quorum(
````

## File: tests/test_release_ledger.py
````python
def setup_release(tmp_path)
⋮----
backend=SQLiteBackend(tmp_path/"db.sqlite")
workflows=WorkflowEngine(backend,SQLiteJobQueue(backend))
releases=ReleaseLedger(
⋮----
workflow=workflows.create(
⋮----
artifact=workflows.add_artifact(
⋮----
def passed_validation()
⋮----
def approval()
⋮----
def signed_attestation(workflow, artifact, validation=None)
⋮----
validation=validation or passed_validation()
⋮----
def test_promote_creates_immutable_release_record(tmp_path)
⋮----
release=releases.promote(
⋮----
def test_promotion_rejects_failed_validation(tmp_path)
⋮----
def test_promotion_rejects_duplicate_artifact(tmp_path)
⋮----
def test_promotion_rejects_superseded_workflow(tmp_path)
⋮----
def test_release_rollback_is_append_only(tmp_path)
⋮----
promoted=releases.promote(
⋮----
rollback=releases.rollback(
⋮----
def test_promotion_requires_artifact_sha256(tmp_path)
⋮----
def test_promotion_rejects_invalid_attestation_signature(tmp_path)
⋮----
attestation=signed_attestation(workflow,artifact)
⋮----
def test_promoted_release_contains_signed_provenance(tmp_path)
⋮----
def test_release_verification_checks_full_chain(tmp_path)
⋮----
verification=releases.verify(release["id"])
⋮----
def test_promotion_requires_operator_approval(tmp_path)
⋮----
def test_release_ledger_promotes_ed25519_attestation(tmp_path)
⋮----
attestation=create_validation_attestation_v2(
⋮----
def test_release_is_anchored_in_transparency_chain(tmp_path)
⋮----
chain=releases.verify_transparency()
⋮----
def test_release_ledger_promotes_strict_dual_sign_bundle(tmp_path)
⋮----
attestation=create_dual_attestation(
⋮----
def test_ed25519_only_policy_rejects_legacy_hmac(tmp_path)
⋮----
def test_dual_required_policy_rejects_pure_ed25519(tmp_path)
⋮----
def test_release_verify_enforces_trusted_builder_repository(tmp_path)
⋮----
builder_id="https://builder.example/prod"
⋮----
def test_release_verify_rejects_untrusted_builder_repository(tmp_path)
⋮----
def test_trusted_builder_requires_dedicated_signing_key(tmp_path)
````

## File: tests/test_remote_worker.py
````python
def test_remote_worker_claim_ack_complete(tmp_path)
⋮----
auth=TokenAuthorizer([
control=ControlPlane(str(tmp_path/"db.sqlite"),authorizer=auth)
⋮----
server=ThreadingHTTPServer(("127.0.0.1",0),make_handler(control))
thread=threading.Thread(target=server.serve_forever,daemon=True)
⋮----
client=RemoteWorkerClient(
job=client.claim()
⋮----
def test_remote_worker_detects_superseded_generation(tmp_path)
⋮----
original=control.workflows.create(
jobs=control.workflows.dispatch_ready(original["id"])
⋮----
server=ThreadingHTTPServer(
⋮----
heartbeat=client.heartbeat(
⋮----
checkpoint=client.checkpoint_stale(
⋮----
events=control.backend.events_after(0,1000)
checkpoint_events=[
````

## File: tests/test_render_start.py
````python
ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "render-start.py"
SPEC = importlib.util.spec_from_file_location("render_start", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
⋮----
class RenderStartTests(unittest.TestCase)
⋮----
def test_auth_payload_hashes_tokens_without_storing_plaintext(self)
⋮----
payload = MODULE._auth_payload("worker-secret", "operator-secret")
rendered = json.dumps(payload)
⋮----
entries = {entry["role"]: entry for entry in payload["tokens"]}
⋮----
def test_main_builds_control_plane_command_from_environment(self)
⋮----
argv = execvp.call_args.args[1]
⋮----
auth_path = Path(td) / "auth.json"
payload = json.loads(auth_path.read_text(encoding="utf-8"))
⋮----
def test_invalid_port_fails_closed(self)
````

## File: tests/test_result_cache.py
````python
def test_result_cache_roundtrip(tmp_path)
⋮----
backend=SQLiteBackend(tmp_path/"db.sqlite")
cache=ResultCache(backend)
key=fingerprint(repository="o/a",task="Build",inputs={"commit":"abc"})
⋮----
hit=cache.get(key)
````

## File: tests/test_runtime_state.py
````python
def test_lease_and_release(tmp_path)
⋮----
state = RuntimeState(tmp_path / "state.json")
rec = state.acquire_lease("o/a", "task", "worker-1", minutes=5)
⋮----
rec = state.release_lease("o/a", "task")
⋮----
def test_circuit_breaker_opens_after_repeated_failures(tmp_path)
⋮----
rec = state.record_outcome("o/a", "task", "rollback", retry_budget=10, circuit_breaker_failures=2, cooldown_minutes=30)
````

## File: tests/test_scheduler.py
````python
def action(repo, task, priority, effort=1, release=5)
⋮----
def assessment(repo, score=50)
⋮----
def test_schedule_respects_capacity_and_repo_focus()
⋮----
assessments = [assessment("o/a"), assessment("o/b"), assessment("o/c")]
actions = [action("o/a","A",60), action("o/b","B",50), action("o/c","C",40)]
schedule = build_schedule(assessments, actions, capacity=2)
active = [x for x in schedule["work"] if x["lane"] in {"NOW","PARALLEL"}]
⋮----
def test_resource_allocation_never_exceeds_slots()
⋮----
schedule = {"work": [
allocation = allocate_resources(schedule, total_slots=3)
````

## File: tests/test_scoring.py
````python
def evidence(**overrides)
⋮----
data = dict(
⋮----
def test_empty_repository_generates_foundational_actions()
⋮----
assessment = assess_repository(evidence())
tasks = {action.task for action in assessment.actions}
⋮----
def test_mature_repository_scores_full_points()
⋮----
repo = evidence(
⋮----
score = score_repository(repo)
⋮----
def test_failed_ci_is_penalized_and_prioritized()
⋮----
assessment = assess_repository(
⋮----
def test_priority_is_effort_adjusted()
⋮----
assessment = assess_repository(evidence(has_readme=True, has_manifest=True))
````

## File: tests/test_secure_release_e2e.py
````python
def test_secure_release_pipeline_end_to_end(tmp_path)
⋮----
backend = SQLiteBackend(tmp_path / "production-os.sqlite")
queue = SQLiteJobQueue(backend)
workflows = WorkflowEngine(backend, queue)
⋮----
builder_id = "https://builder.example/production"
repository = "dbrckk/example"
⋮----
releases = ReleaseLedger(
⋮----
workflow = workflows.create(
⋮----
artifact = workflows.add_artifact(
⋮----
validation = {
attestation = create_validation_attestation(
⋮----
release = releases.promote(
⋮----
verification = releases.verify(release["id"])
transparency = releases.verify_transparency()
⋮----
metadata = release["metadata"]
⋮----
def test_secure_release_rejects_attestation_bound_to_other_artifact(tmp_path)
⋮----
workflows = WorkflowEngine(backend, SQLiteJobQueue(backend))
⋮----
def test_secure_release_rejects_tampered_artifact_digest(tmp_path)
⋮----
def test_secure_release_rejects_attestation_replay_across_workflows(tmp_path)
⋮----
first = workflows.create(
⋮----
first_artifact = workflows.add_artifact(
⋮----
replayed = create_validation_attestation(
⋮----
second = workflows.create(
⋮----
second_artifact = workflows.add_artifact(
⋮----
def test_secure_release_verification_detects_provenance_tampering(tmp_path)
⋮----
row = db.execute(
⋮----
metadata = json.loads(row["metadata_json"])
⋮----
def test_release_becomes_untrusted_after_validator_key_compromise(tmp_path)
⋮----
initial = ReleaseLedger(
release = initial.promote(
⋮----
compromised = ReleaseLedger(
verification = compromised.verify(release["id"])
⋮----
def test_release_becomes_untrusted_after_builder_key_compromise(tmp_path)
⋮----
builder_id = "https://builder.example/prod"
⋮----
builders = {
````

## File: tests/test_self_healing_heartbeat.py
````python
def test_self_healing_replans_lost_lease(tmp_path)
⋮----
state = RuntimeState(tmp_path / "state.json")
rec = state.get("o/a", "task")
⋮----
actions = apply_self_healing(state)
⋮----
def test_heartbeat_manager_renews_matching_owner(tmp_path)
⋮----
results = renew_active_leases(state, owner="controller", minutes=10)
````

## File: tests/test_signer_factory.py
````python
def test_factory_creates_pem_signer()
⋮----
signer=create_signer("pem:",pem_value=private_key)
⋮----
def test_remote_signer_requires_key_id()
⋮----
def test_factory_rejects_unknown_scheme()
⋮----
def test_remote_signer_exposes_configured_public_identity()
⋮----
signer=create_signer(
⋮----
def test_remote_signer_rejects_non_https_endpoint_shape()
⋮----
def test_pem_factory_fails_closed_without_key_material()
⋮----
def test_remote_signer_requires_https_by_default()
⋮----
def test_remote_http_can_be_explicitly_enabled_for_development()
⋮----
signer=RemoteHttpSigner(
⋮----
def test_factory_requires_https_for_remote_backend()
````

## File: tests/test_signers.py
````python
def test_pem_signer_signs_without_exposing_key_to_callers()
⋮----
signer=PemSigner(private_key)
payload={"release_id":"release-1"}
signature=signer.sign(payload)
⋮----
def test_coerce_signer_preserves_explicit_signer()
⋮----
def test_slsa_and_witness_accept_signer_interface()
⋮----
statement={
slsa=sign_slsa_statement_with_signer(
witness=sign_checkpoint_with_signer(
````

## File: tests/test_source_tree.py
````python
def test_candidate_source_filter()
⋮----
def test_priority_prefers_source_dirs()
````

## File: tests/test_speculation_api.py
````python
def api(base, path, token, payload=None)
⋮----
data=None if payload is None else json.dumps(payload).encode("utf-8")
req=urllib.request.Request(
⋮----
raw=response.read()
⋮----
def test_first_success_wins_over_speculative_copy(tmp_path)
⋮----
auth=TokenAuthorizer([
control=ControlPlane(str(tmp_path/"db.sqlite"),authorizer=auth)
⋮----
original=control.queue.enqueue({
⋮----
duplicate=control.speculation.spawn(
⋮----
server=ThreadingHTTPServer(("127.0.0.1",0),make_handler(control))
thread=threading.Thread(target=server.serve_forever,daemon=True)
⋮----
base=f"http://127.0.0.1:{server.server_port}"
````

## File: tests/test_speculation.py
````python
def test_speculative_first_success_wins(tmp_path)
⋮----
backend=SQLiteBackend(tmp_path/"db.sqlite")
queue=SQLiteJobQueue(backend)
manager=SpeculationManager(backend,queue)
⋮----
original=queue.enqueue({
⋮----
duplicate=manager.spawn(
⋮----
group=manager.group_for_job(duplicate["key"])
⋮----
losers=manager.cancel_losers(group,duplicate["key"])
````

## File: tests/test_sqlite_backend.py
````python
def test_sqlite_runtime_lease_is_transactional(tmp_path)
⋮----
backend=SQLiteBackend(tmp_path/"production.db")
state=SQLiteRuntimeState(backend)
first=state.acquire_lease("o/a","task","w1")
⋮----
other=SQLiteRuntimeState(backend)
⋮----
def test_sqlite_worker_registry(tmp_path)
⋮----
workers=SQLiteWorkerRegistry(backend)
worker=workers.register("python-1",["python"],2)
⋮----
def test_durable_queue_claim_and_complete(tmp_path)
⋮----
queue=SQLiteJobQueue(backend)
queued=queue.enqueue({
claimed=queue.claim_next("w1",capabilities=["python"])
````

## File: tests/test_sqlite_migration.py
````python
def test_import_runtime_json(tmp_path)
⋮----
source=tmp_path/"runtime.json"
⋮----
backend=SQLiteBackend(tmp_path/"db.sqlite")
result=import_json_state(backend,runtime_state=str(source))
⋮----
state=SQLiteRuntimeState(backend)
````

## File: tests/test_stragglers.py
````python
def test_straggler_detection_with_alternate_worker(tmp_path)
⋮----
backend=SQLiteBackend(tmp_path/"db.sqlite")
opt=ExecutionOptimizer(backend)
⋮----
queue=SQLiteJobQueue(backend)
job=queue.enqueue({
⋮----
old=(datetime.now(timezone.utc)-timedelta(minutes=4)).isoformat()
⋮----
rows=opt.stragglers(
````

## File: tests/test_supply_chain.py
````python
def release()
⋮----
def provenance()
⋮----
def test_slsa_statement_contains_subject_and_material()
⋮----
statement=create_slsa_statement(
⋮----
dependency=statement["predicate"]["buildDefinition"][
⋮----
def test_signed_slsa_statement_is_offline_verifiable()
⋮----
envelope=sign_slsa_statement(
⋮----
def test_slsa_tampering_is_detected()
````

## File: tests/test_task_capabilities.py
````python
def test_visual_tasks_are_detected_from_task_text()
⋮----
def test_3d_generation_requires_dedicated_3d_worker()
⋮----
required = inferred_required_capabilities(
⋮----
def test_3d_validation_only_does_not_require_generation_capability()
⋮----
def test_french_visual_and_3d_generation_tasks_are_detected()
⋮----
visual = inferred_required_capabilities(
⋮----
three_d = inferred_required_capabilities(
⋮----
def test_non_visual_software_task_is_not_misclassified()
⋮----
def test_inferred_capabilities_preserve_explicit_requirements()
````

## File: tests/test_transparency_cli.py
````python
def _signed_rekor_receipt(envelope)
⋮----
log_private = ec.generate_private_key(ec.SECP256R1())
log_public = log_private.public_key()
log_public_pem = log_public.public_bytes(
log_public_der = log_public.public_bytes(
log_id = hashlib.sha256(log_public_der).hexdigest()
⋮----
proposed = build_rekor_v1_hashedrekord(
body = json.dumps(
entry = {
root_hash = hashlib.sha256(b"\x00" + body).hexdigest()
note = (
key_hint = hashlib.sha256(log_public_der).digest()[:4]
note_digest = hashlib.sha256(note.encode("utf-8")).digest()
checkpoint_signature = log_private.sign(
checkpoint = (
canonical = json.dumps(
set_signature = log_private.sign(
⋮----
receipt = parse_rekor_v1_receipt(
⋮----
def test_checkpoint_verify_combines_witness_and_rekor_receipt(tmp_path, capsys)
⋮----
envelope = sign_checkpoint(
⋮----
checkpoint_path = tmp_path / "checkpoint.json"
witness_key_path = tmp_path / "witness.pub.pem"
receipt_path = tmp_path / "receipt.json"
log_key_path = tmp_path / "rekor-log.pem"
⋮----
args = argparse.Namespace(
exit_code = cli.run_transparency_checkpoint_verify(args)
result = json.loads(capsys.readouterr().out)
⋮----
def test_checkpoint_publication_writes_rekor_receipt(tmp_path, monkeypatch, capsys)
⋮----
witness_key_path = tmp_path / "witness.pem"
rekor_key_path = tmp_path / "rekor.pem"
⋮----
publication_state = SQLiteBackend(tmp_path / "publication-state.db")
⋮----
class Ledger
⋮----
backend = publication_state
⋮----
def verify_transparency(self)
⋮----
observed = {}
⋮----
class FakePublisher
⋮----
def publish(self, envelope)
⋮----
root_hash = hashlib.sha256(b"fake-rekor-root").hexdigest()
root_b64 = base64.b64encode(bytes.fromhex(root_hash)).decode("ascii")
⋮----
exit_code = cli.run_transparency_checkpoint(args)
````

## File: tests/test_transparency_receipts.py
````python
def _envelope()
⋮----
def _leaf_hash(payload: bytes) -> str
⋮----
def _rekor_signing_private_pem() -> str
⋮----
private_key = ec.generate_private_key(ec.SECP256R1())
⋮----
def test_checkpoint_digest_is_deterministic()
⋮----
envelope = _envelope()
reordered = {
⋮----
def test_build_rekor_v1_hashedrekord_binds_checkpoint_digest()
⋮----
proposed = build_rekor_v1_hashedrekord(
⋮----
def test_verify_inclusion_proof_accepts_single_leaf()
⋮----
leaf = b'{"entry":"checkpoint"}'
⋮----
def test_verify_inclusion_proof_detects_tampered_leaf()
⋮----
def test_verify_inclusion_proof_accepts_two_leaf_tree()
⋮----
left = b"left"
right = b"right"
left_hash = hashlib.sha256(b"\x00" + left).digest()
right_hash = hashlib.sha256(b"\x00" + right).digest()
root = hashlib.sha256(
⋮----
def _rekor_response(envelope, *, digest=None, log_id=None)
⋮----
body = json.dumps(
⋮----
def _signed_rekor_response(envelope)
⋮----
public_key = private_key.public_key()
public_pem = public_key.public_bytes(
public_der = public_key.public_bytes(
log_id = hashlib.sha256(public_der).hexdigest()
response = _rekor_response(envelope, log_id=log_id)
entry = response["b" * 64]
proof = entry["verification"]["inclusionProof"]
note = (
key_hint = hashlib.sha256(public_der).digest()[:4]
checkpoint_digest = hashlib.sha256(note.encode("utf-8")).digest()
checkpoint_signature = private_key.sign(
checkpoint_encoded = base64.b64encode(
⋮----
signed_payload = {
canonical = json.dumps(
signature = private_key.sign(
⋮----
def test_parse_rekor_v1_receipt_requires_bound_inclusion_proof()
⋮----
receipt = parse_rekor_v1_receipt(
⋮----
def test_parse_rekor_v1_receipt_rejects_wrong_checkpoint_digest()
⋮----
def test_verify_rekor_signed_entry_timestamp_binds_log_identity_and_entry()
⋮----
def test_verify_rekor_v1_receipt_rejects_wrong_log_id_or_envelope()
⋮----
tampered = _envelope()
⋮----
def test_verify_rekor_v1_receipt_can_authenticate_rekor_set()
⋮----
def test_rekor_v1_publisher_posts_hashedrekord_and_returns_receipt(monkeypatch)
⋮----
observed = {}
⋮----
class Response
⋮----
status = 201
⋮----
def __init__(self, payload)
⋮----
def __enter__(self)
⋮----
def __exit__(self, *args)
⋮----
def read(self)
⋮----
def fake_urlopen(request, timeout)
⋮----
proposed = json.loads(request.data)
⋮----
payload = {
⋮----
publisher = RekorV1Publisher(
⋮----
receipt = publisher.publish(envelope)
⋮----
def test_rekor_v1_publisher_from_private_key_derives_signing_identity()
⋮----
private_pem = _rekor_signing_private_pem()
publisher = RekorV1Publisher.from_private_key(
⋮----
signature = publisher.signer(b"checkpoint")
public_key = serialization.load_pem_public_key(
⋮----
def test_rekor_v1_publisher_with_log_key_fails_closed_on_bad_set(monkeypatch)
⋮----
log_private = ec.generate_private_key(ec.SECP256R1())
log_public = log_private.public_key()
log_public_pem = log_public.public_bytes(
log_id = hashlib.sha256(log_public.public_bytes(
⋮----
proposed = json.loads(self.request.data)
⋮----
response = Response()
````

## File: tests/test_trust_policy.py
````python
def test_strict_policy_accepts_four_distinct_domains()
⋮----
policy=TrustPolicy.create(
mapping=policy.validate()
⋮----
def test_witness_cannot_reuse_provenance_key()
⋮----
def test_witness_cannot_reuse_builder_key()
````

## File: tests/test_trust_status_summary.py
````python
def test_trust_status_aggregates_affected_entities_and_reasons(monkeypatch)
⋮----
ledger = object.__new__(ReleaseLedger)
rows = [
⋮----
class Result
⋮----
def fetchall(self)
⋮----
class DB
⋮----
def __enter__(self)
def __exit__(self, *args)
⋮----
class Backend
⋮----
def connect(self)
⋮----
outcomes = {
⋮----
result = ledger.trust_status()
⋮----
def test_incident_report_id_is_stable_for_same_blast_radius(monkeypatch)
⋮----
row = {
⋮----
first = ledger.incident_report(key_id="sha256:deadbeef")
second = ledger.incident_report(key_id="sha256:deadbeef")
````

## File: tests/test_vault_auth.py
````python
def test_vault_approle_requires_credentials(monkeypatch)
⋮----
def test_vault_kubernetes_requires_role_and_jwt()
⋮----
def test_vault_rejects_unknown_auth_method()
````

## File: tests/test_vault_signer.py
````python
def test_vault_requires_https()
⋮----
def test_vault_requires_credentials()
⋮----
def test_factory_creates_vault_transit_signer()
⋮----
signer=create_signer(
⋮----
def test_factory_rejects_vault_uri_without_key()
````

## File: tests/test_witness.py
````python
def test_signed_transparency_checkpoint_verifies()
⋮----
checkpoint=create_checkpoint(
envelope=sign_checkpoint(
⋮----
def test_checkpoint_root_tampering_is_detected()
⋮----
def test_checkpoint_expected_root_mismatch_fails()
````

## File: tests/test_workers.py
````python
def test_selects_least_loaded_capable_worker(tmp_path)
⋮----
registry=WorkerRegistry(tmp_path/"workers.json")
a=registry.register("a",["python","android"],2)
b=registry.register("b",["python"],2)
⋮----
selected=select_worker(registry,["python"])
⋮----
def test_rejects_worker_without_required_capability(tmp_path)
````

## File: tests/test_workflow_api.py
````python
def api(base, path, token, payload=None)
⋮----
data = None if payload is None else json.dumps(payload).encode("utf-8")
request = urllib.request.Request(
⋮----
raw = response.read()
⋮----
def test_workflow_api_end_to_end(tmp_path)
⋮----
auth=TokenAuthorizer([
control=ControlPlane(str(tmp_path/"db.sqlite"),authorizer=auth)
⋮----
server=ThreadingHTTPServer(("127.0.0.1",0),make_handler(control))
thread=threading.Thread(target=server.serve_forever,daemon=True)
⋮----
base=f"http://127.0.0.1:{server.server_port}"
⋮----
workflow_id=created["workflow"]["id"]
⋮----
first_key=claimed["job"]["key"]
⋮----
second_key=claimed2["job"]["key"]
````

## File: tests/test_workflow_cache.py
````python
def test_cacheable_workflow_task_reuses_result(tmp_path)
⋮----
backend=SQLiteBackend(tmp_path/"db.sqlite")
engine=WorkflowEngine(backend,SQLiteJobQueue(backend))
⋮----
first=engine.create(
⋮----
second=engine.create(
jobs=engine.dispatch_ready(second["id"])
⋮----
current=engine.get(second["id"])
⋮----
result=current["tasks"][0]["result"]
````

## File: tests/test_workflow_change_impact.py
````python
def test_workflow_change_impact_skips_unaffected_tasks(tmp_path)
⋮----
backend=SQLiteBackend(tmp_path/"db.sqlite")
engine=WorkflowEngine(backend,SQLiteJobQueue(backend))
⋮----
workflow=engine.create(
⋮----
tasks={task["task_id"]:task for task in workflow["tasks"]}
⋮----
jobs=engine.dispatch_ready(workflow["id"])
````

## File: tests/test_workflow_engine.py
````python
def engine(tmp_path)
⋮----
backend=SQLiteBackend(tmp_path/"db.sqlite")
⋮----
def test_workflow_fanout_fanin(tmp_path)
⋮----
wf=engine(tmp_path)
created=wf.create(
⋮----
jobs=wf.dispatch_ready(created["id"])
⋮----
current=wf.get(created["id"])
ready={
⋮----
def test_workflow_dispatch_infers_visual_worker_requirement(tmp_path)
⋮----
contract = jobs[0]["payload"]["handoff"]["tool_contracts"]["asset_forge"]
⋮----
def test_workflow_rejects_cycle(tmp_path)
⋮----
def test_workflow_retry_budget(tmp_path)
⋮----
current=wf.get(created["id"])["tasks"][0]
⋮----
def test_critical_path(tmp_path)
⋮----
path=wf.critical_path(created["id"])
⋮----
def test_change_impact_can_be_recomputed_before_execution(tmp_path)
⋮----
first={task["task_id"]:task for task in created["tasks"]}
⋮----
current={
⋮----
def test_change_impact_recompute_rejected_after_dispatch(tmp_path)
⋮----
def test_find_workflows_bound_to_github_pr(tmp_path)
⋮----
first=wf.create(
⋮----
matches=wf.find_by_github_pr("o/a",12)
⋮----
def test_find_workflows_bound_to_github_pr_accepts_string_metadata(tmp_path)
⋮----
def test_pr_generation_supersedes_old_workflow_and_jobs(tmp_path)
⋮----
original=wf.create(
jobs=wf.dispatch_ready(original["id"])
⋮----
old=wf.get(original["id"])
⋮----
def test_pr_generation_reuses_same_workflow_for_same_head_sha(tmp_path)
⋮----
def test_pr_generation_binds_initial_head_in_place(tmp_path)
⋮----
def test_dispatched_job_carries_pr_generation_and_revision(tmp_path)
⋮----
payload=jobs[0]["payload"]
⋮----
def test_create_unseen_pr_from_repository_template(tmp_path)
⋮----
template=wf.create(
⋮----
created=wf.create_from_pr_template(
⋮----
def test_create_unseen_pr_without_template_returns_none(tmp_path)
⋮----
def test_pr_artifact_requires_current_revision_and_generation(tmp_path)
⋮----
artifact=wf.add_artifact(
⋮----
def test_superseded_pr_rejects_artifact_promotion(tmp_path)
````

## File: tests/test_workflow_postgres.py
````python
DSN=os.getenv("PRODUCTION_OS_TEST_POSTGRES")
⋮----
pytestmark=pytest.mark.skipif(
⋮----
def test_postgres_workflow_engine()
⋮----
backend=PostgresBackend(DSN)
⋮----
engine=WorkflowEngine(backend,PostgresJobQueue(backend))
workflow=engine.create(
⋮----
first=engine.dispatch_ready(workflow["id"])
⋮----
current=engine.get(workflow["id"])
````

## File: tests/test_workflow_splitting.py
````python
def test_splittable_task_expands_into_parallel_shards(tmp_path)
⋮----
backend=SQLiteBackend(tmp_path/"db.sqlite")
engine=WorkflowEngine(backend,SQLiteJobQueue(backend))
⋮----
workflow=engine.create(
⋮----
tasks={task["task_id"]:task for task in workflow["tasks"]}
shard_ids=sorted(
⋮----
jobs=engine.dispatch_ready(workflow["id"],limit=10)
⋮----
current=engine.get(workflow["id"])
tasks={task["task_id"]:task for task in current["tasks"]}
````

## File: .repo-standards.yml
````yaml
source: dbrckk/repo-standards
ref: main
version: 20
adopted: true
workflow_mode: unified-single-commit
repo_brain: dbrckk/repo-brain@main
repo_brain_fallback: portable-full-rebuild
hotset_fallback: recent-project-state
graph_routing: compact-sharded-reverse-deps
graph_resolver: java-kotlin-tail-v2
graph_enrichment: unique-type-symbol-references-v1
context_budget: confidence-dynamic-3-6-12
routing_learning: deterministic-term-feedback-v1
auto_routing_learning: source-diff-success-v1
validation_memory: passed-failed-test-history-v1
regression_gate: repo-brain-core-tests-v1
benchmark: routing-benchmark-v1
stability_profile: stable-v1
benchmark_guard: avg-files-le-6-cache-required-v1
ai_context:
  index: .ai/index.md
  project_state: .ai/project-state.md
  change_impact: .ai/change-impact.md
  architecture: .ai/architecture.json
  dependency_map: .ai/dependency-map.json
  commands: .ai/commands.json
  ci_status: .ai/ci-status.md
  security_signals: .ai/security-signals.json
  repo_health: .ai/repo-health.md
  brain_summary: .ai/brain/summary.md
  brain_incremental_state: .ai/brain/incremental-state.json
  brain_impact: .ai/brain/impact.json
  brain_selected_tests: .ai/brain/selected-tests.json
  brain_references: .ai/brain/references.json
  brain_symbol_dependencies: .ai/brain/symbol-dependencies.json
  brain_capabilities: .ai/brain/capabilities.json
  brain_ast_routing: .ai/brain/ast-routing.json
  brain_ast_symbols: .ai/brain/ast-symbols/
  brain_file_outlines: .ai/brain/file-outlines/
  brain_lookup: .ai/brain/lookup.json
  brain_symbols: .ai/brain/symbols.json
  brain_graph: .ai/brain/code-graph.json
  brain_graph_index: .ai/brain/graph-index.json
  brain_graph_enrichment: .ai/brain/graph-enrichment.json
  brain_graph_manifest: .ai/brain/graph-manifest.json
  brain_graph_shards: .ai/brain/graph-shards/
  brain_reverse_deps: .ai/brain/reverse-deps.json
  brain_architecture_mermaid: .ai/brain/architecture.mmd
  brain_semantic_plan: .ai/brain/semantic-plan.json
  brain_semantic_index: .ai/brain/semantic-index.json
  brain_search_manifest: .ai/brain/search-manifest.json
  brain_search_shards: .ai/brain/search-shards/
  brain_query_cache: .ai/brain/query-cache.json
  brain_routing_learning: .ai/brain/routing-learning.json
  brain_auto_learning: .ai/brain/auto-learning.json
  brain_validation_memory: .ai/brain/validation-memory.json
  brain_benchmark: .ai/brain/benchmark.json
  brain_benchmark_health: .ai/brain/benchmark-health.json
  brain_hotset: .ai/brain/hotset.json
  brain_context_manifest: .ai/brain/context-manifest.json
  brain_context_packets: .ai/brain/context/
  brain_hash_cache: .ai/brain/hash-cache.json
  session_state: .ai/session-state.json
  repo_map: .ai/repo-map.md
  segmented_maps: .ai/maps/
workflow:
  file: .github/workflows/ai-repo-map.yml
  reusable_unified: .github/workflows/reusable-unified.yml
  semantic_refresh: .github/workflows/semantic-refresh.yml
````

## File: AGENTS.md
````markdown
# Repository agent instructions

This repository adopts shared standards from `dbrckk/repo-standards` at the release recorded in `.repo-standards.yml`.

Before substantial work:
1. Read the central `AGENTS.md` and relevant standards at the configured ref.
2. Read `.ai/session-state.json` when present.
3. Read `.ai/project-state.md`.
4. Read `.ai/brain/hotset.json`.
5. Read `.ai/brain/context-manifest.json` and only the relevant `.ai/brain/context/<area>.json` packet.
6. Read `.ai/brain/graph-index.json` and the relevant `.ai/brain/graph-shards/<area>.json` when dependency routing matters.
7. Use `.ai/brain/reverse-deps.json` for upstream/downstream file impact.
8. Read `.ai/brain/impact.json` and `.ai/brain/selected-tests.json`.
9. Read `.ai/brain/references.json` and `.ai/brain/symbol-dependencies.json` only when symbol routing requires them.
10. Read `.ai/change-impact.md` and `.ai/architecture.json` when broader structure is needed.
11. Read `.ai/brain/summary.md`, `.ai/brain/incremental-state.json`, and `.ai/brain/capabilities.json` when index freshness/capabilities matter.
12. If ast-grep enrichment is available, route named symbols through `.ai/brain/ast-routing.json` and one `.ai/brain/ast-symbols/<initial>.json` shard.
13. Fall back to `.ai/brain/lookup.json` when AST routing is unavailable or insufficient.
14. Use `.ai/brain/code-graph.json` and `.ai/brain/imports.json` for cross-module context.
15. Read `.ai/dependency-map.json` when dependency context matters.
16. Read `.ai/commands.json`, `.ai/ci-status.md`, and security signals when relevant.
17. Read `.ai/repo-health.md`.
18. Use `.ai/index.md` and segmented maps only if bounded context is insufficient.
19. Read `.ai/repo-map.md` only as a final broad-context fallback.
20. Fetch only task-relevant source files or line ranges.

Repository-specific rules:
- Preserve existing architecture and public interfaces unless the task requires a change.
- Prefer the smallest coherent change.
- Prefer targeted tests from `.ai/brain/selected-tests.json`; expand validation when impact is ambiguous or targeted tests fail.
- Treat hotset/context packets and graph shards as routing hints, not authoritative source.
- Verify reference/dependency/impact/AST hits against authoritative source before editing.
- Treat security signals and static graph edges as heuristics, not proof.
- Never reproduce suspected secret values.
- Update manual project-state sections when status, blockers, or next priority materially changes.
- Maintain `.ai/session-state.json` for substantial multi-turn work so a later "Continue" can resume without reconstructing the repository.
````

## File: compose.postgres.yaml
````yaml
services:
  postgres:
    image: postgres:16-alpine
    restart: unless-stopped
    environment:
      POSTGRES_USER: production_os
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: production_os
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U production_os -d production_os"]
      interval: 5s
      timeout: 5s
      retries: 10

  production-os:
    build: .
    restart: unless-stopped
    depends_on:
      postgres:
        condition: service_healthy
    ports:
      - "8787:8787"
    environment:
      PRODUCTION_OS_GITHUB_WEBHOOK_SECRET: ${PRODUCTION_OS_GITHUB_WEBHOOK_SECRET:-}
      PRODUCTION_OS_VALIDATION_ATTESTATION_KEYS: ${PRODUCTION_OS_VALIDATION_ATTESTATION_KEYS:-{}}
      PRODUCTION_OS_RELEASE_PROVENANCE_SECRET: ${PRODUCTION_OS_RELEASE_PROVENANCE_SECRET:-}
      PRODUCTION_OS_VALIDATION_PUBLIC_KEYS: ${PRODUCTION_OS_VALIDATION_PUBLIC_KEYS:-{}}
      PRODUCTION_OS_RELEASE_PROVENANCE_PRIVATE_KEY: ${PRODUCTION_OS_RELEASE_PROVENANCE_PRIVATE_KEY:-}
      PRODUCTION_OS_RELEASE_PROVENANCE_PUBLIC_KEY: ${PRODUCTION_OS_RELEASE_PROVENANCE_PUBLIC_KEY:-}
      PRODUCTION_OS_PROVENANCE_SIGNER_URI: ${PRODUCTION_OS_PROVENANCE_SIGNER_URI:-}
      PRODUCTION_OS_PROVENANCE_SIGNER_KEY_ID: ${PRODUCTION_OS_PROVENANCE_SIGNER_KEY_ID:-}
      PRODUCTION_OS_PROVENANCE_SIGNER_TOKEN: ${PRODUCTION_OS_PROVENANCE_SIGNER_TOKEN:-}
      PRODUCTION_OS_VALIDATION_SIGNATURE_POLICY: ${PRODUCTION_OS_VALIDATION_SIGNATURE_POLICY:-compatible}
      PRODUCTION_OS_BUILDER_ID: ${PRODUCTION_OS_BUILDER_ID:-https://production-os.local/builder}
      PRODUCTION_OS_BUILDER_PRIVATE_KEY: ${PRODUCTION_OS_BUILDER_PRIVATE_KEY:-}
      PRODUCTION_OS_BUILDER_SIGNER_URI: ${PRODUCTION_OS_BUILDER_SIGNER_URI:-}
      PRODUCTION_OS_BUILDER_SIGNER_KEY_ID: ${PRODUCTION_OS_BUILDER_SIGNER_KEY_ID:-}
      PRODUCTION_OS_BUILDER_SIGNER_TOKEN: ${PRODUCTION_OS_BUILDER_SIGNER_TOKEN:-}
      PRODUCTION_OS_TRUSTED_BUILDERS: ${PRODUCTION_OS_TRUSTED_BUILDERS:-{}}
      PRODUCTION_OS_TRUSTED_BUILDER_KEYS: ${PRODUCTION_OS_TRUSTED_BUILDER_KEYS:-{}}
      PRODUCTION_OS_REQUIRE_TRUSTED_BUILDER: ${PRODUCTION_OS_REQUIRE_TRUSTED_BUILDER:-false}
    volumes:
      - ./artifacts:/data
    command:
      - control-plane
      - --database
      - postgresql://production_os:${POSTGRES_PASSWORD}@postgres:5432/production_os
      - --auth-config
      - /data/auth.json
      - --host
      - 0.0.0.0
      - --port
      - "8787"

volumes:
  postgres_data:
````

## File: compose.tls.yaml
````yaml
services:
  production-os:
    build: .
    restart: unless-stopped
    expose:
      - "8787"
    environment:
      PRODUCTION_OS_GITHUB_WEBHOOK_SECRET: ${PRODUCTION_OS_GITHUB_WEBHOOK_SECRET:-}
      PRODUCTION_OS_VALIDATION_ATTESTATION_KEYS: ${PRODUCTION_OS_VALIDATION_ATTESTATION_KEYS:-{}}
      PRODUCTION_OS_RELEASE_PROVENANCE_SECRET: ${PRODUCTION_OS_RELEASE_PROVENANCE_SECRET:-}
      PRODUCTION_OS_VALIDATION_PUBLIC_KEYS: ${PRODUCTION_OS_VALIDATION_PUBLIC_KEYS:-{}}
      PRODUCTION_OS_RELEASE_PROVENANCE_PRIVATE_KEY: ${PRODUCTION_OS_RELEASE_PROVENANCE_PRIVATE_KEY:-}
      PRODUCTION_OS_RELEASE_PROVENANCE_PUBLIC_KEY: ${PRODUCTION_OS_RELEASE_PROVENANCE_PUBLIC_KEY:-}
      PRODUCTION_OS_PROVENANCE_SIGNER_URI: ${PRODUCTION_OS_PROVENANCE_SIGNER_URI:-}
      PRODUCTION_OS_PROVENANCE_SIGNER_KEY_ID: ${PRODUCTION_OS_PROVENANCE_SIGNER_KEY_ID:-}
      PRODUCTION_OS_PROVENANCE_SIGNER_TOKEN: ${PRODUCTION_OS_PROVENANCE_SIGNER_TOKEN:-}
      PRODUCTION_OS_VALIDATION_SIGNATURE_POLICY: ${PRODUCTION_OS_VALIDATION_SIGNATURE_POLICY:-compatible}
      PRODUCTION_OS_BUILDER_ID: ${PRODUCTION_OS_BUILDER_ID:-https://production-os.local/builder}
      PRODUCTION_OS_BUILDER_PRIVATE_KEY: ${PRODUCTION_OS_BUILDER_PRIVATE_KEY:-}
      PRODUCTION_OS_BUILDER_SIGNER_URI: ${PRODUCTION_OS_BUILDER_SIGNER_URI:-}
      PRODUCTION_OS_BUILDER_SIGNER_KEY_ID: ${PRODUCTION_OS_BUILDER_SIGNER_KEY_ID:-}
      PRODUCTION_OS_BUILDER_SIGNER_TOKEN: ${PRODUCTION_OS_BUILDER_SIGNER_TOKEN:-}
      PRODUCTION_OS_TRUSTED_BUILDERS: ${PRODUCTION_OS_TRUSTED_BUILDERS:-{}}
      PRODUCTION_OS_TRUSTED_BUILDER_KEYS: ${PRODUCTION_OS_TRUSTED_BUILDER_KEYS:-{}}
      PRODUCTION_OS_REQUIRE_TRUSTED_BUILDER: ${PRODUCTION_OS_REQUIRE_TRUSTED_BUILDER:-false}
    volumes:
      - ./artifacts:/data
    command:
      - control-plane
      - --database
      - /data/production.db
      - --auth-config
      - /data/auth.json
      - --host
      - 0.0.0.0
      - --port
      - "8787"

  caddy:
    image: caddy:2-alpine
    restart: unless-stopped
    depends_on:
      - production-os
    ports:
      - "80:80"
      - "443:443"
    environment:
      DOMAIN: ${DOMAIN}
      ACME_EMAIL: ${ACME_EMAIL}
    volumes:
      - ./deploy/Caddyfile:/etc/caddy/Caddyfile:ro
      - caddy_data:/data
      - caddy_config:/config

volumes:
  caddy_data:
  caddy_config:
````

## File: compose.yaml
````yaml
services:
  production-os:
    build: .
    restart: unless-stopped
    ports:
      - "8787:8787"
    environment:
      PRODUCTION_OS_GITHUB_WEBHOOK_SECRET: ${PRODUCTION_OS_GITHUB_WEBHOOK_SECRET:-}
      PRODUCTION_OS_VALIDATION_ATTESTATION_KEYS: ${PRODUCTION_OS_VALIDATION_ATTESTATION_KEYS:-{}}
      PRODUCTION_OS_RELEASE_PROVENANCE_SECRET: ${PRODUCTION_OS_RELEASE_PROVENANCE_SECRET:-}
      PRODUCTION_OS_VALIDATION_PUBLIC_KEYS: ${PRODUCTION_OS_VALIDATION_PUBLIC_KEYS:-{}}
      PRODUCTION_OS_RELEASE_PROVENANCE_PRIVATE_KEY: ${PRODUCTION_OS_RELEASE_PROVENANCE_PRIVATE_KEY:-}
      PRODUCTION_OS_RELEASE_PROVENANCE_PUBLIC_KEY: ${PRODUCTION_OS_RELEASE_PROVENANCE_PUBLIC_KEY:-}
      PRODUCTION_OS_PROVENANCE_SIGNER_URI: ${PRODUCTION_OS_PROVENANCE_SIGNER_URI:-}
      PRODUCTION_OS_PROVENANCE_SIGNER_KEY_ID: ${PRODUCTION_OS_PROVENANCE_SIGNER_KEY_ID:-}
      PRODUCTION_OS_PROVENANCE_SIGNER_TOKEN: ${PRODUCTION_OS_PROVENANCE_SIGNER_TOKEN:-}
      PRODUCTION_OS_VALIDATION_SIGNATURE_POLICY: ${PRODUCTION_OS_VALIDATION_SIGNATURE_POLICY:-compatible}
      PRODUCTION_OS_BUILDER_ID: ${PRODUCTION_OS_BUILDER_ID:-https://production-os.local/builder}
      PRODUCTION_OS_BUILDER_PRIVATE_KEY: ${PRODUCTION_OS_BUILDER_PRIVATE_KEY:-}
      PRODUCTION_OS_BUILDER_SIGNER_URI: ${PRODUCTION_OS_BUILDER_SIGNER_URI:-}
      PRODUCTION_OS_BUILDER_SIGNER_KEY_ID: ${PRODUCTION_OS_BUILDER_SIGNER_KEY_ID:-}
      PRODUCTION_OS_BUILDER_SIGNER_TOKEN: ${PRODUCTION_OS_BUILDER_SIGNER_TOKEN:-}
      PRODUCTION_OS_TRUSTED_BUILDERS: ${PRODUCTION_OS_TRUSTED_BUILDERS:-{}}
      PRODUCTION_OS_TRUSTED_BUILDER_KEYS: ${PRODUCTION_OS_TRUSTED_BUILDER_KEYS:-{}}
      PRODUCTION_OS_REQUIRE_TRUSTED_BUILDER: ${PRODUCTION_OS_REQUIRE_TRUSTED_BUILDER:-false}
    volumes:
      - ./artifacts:/data
    command:
      - control-plane
      - --database
      - /data/production.db
      - --auth-config
      - /data/auth.json
      - --host
      - 0.0.0.0
      - --port
      - "8787"
````

## File: pyproject.toml
````toml
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "production-os"
version = "1.0.0"
description = "Portfolio control plane for autonomous software production"
readme = "README.md"
requires-python = ">=3.11"
license = { text = "MIT" }
authors = [{ name = "dbrckk" }]
dependencies = ["cryptography>=43.0"]
classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Environment :: Console",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]

[project.optional-dependencies]
dev = ["pytest>=8.0", "build>=1.2"]
postgres = ["psycopg[binary]>=3.2"]

[project.scripts]
production-os = "production_os.cli:main"

[tool.setuptools]
package-dir = {"" = "src"}

[tool.setuptools.packages.find]
where = ["src"]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
markers = [
    "e2e: production-stack end-to-end tests requiring PostgreSQL",
]
````

## File: README.md
````markdown
# Production-OS

Portfolio control plane for autonomous software production.

Production-OS manages portfolio state, prioritization, reuse, compatibility, validation, and execution feedback before handing work to `ai-dev-server`.

## Current capabilities

- GitHub portfolio discovery
- deterministic maturity scoring
- project classification
- GitHub Actions runtime-state ingestion
- bounded recursive source-tree sampling
- deep source fingerprinting
- capability fingerprinting
- source-symbol/component extraction
- component provenance
- component→dependency→capability graph
- **call/import graph refinement**
- test-to-component linking
- adaptation risk scoring
- reusable boundary detection
- automatic adaptation plans
- target-side dependency compatibility checks
- **dependency version compatibility**
- automatic validation-plan generation
- **validation-result ingestion**
- **autonomous portfolio scheduling**
- **execution-slot resource allocation**
- live `dbrckk/star-list` ranking
- portfolio-wide **Next Best Action**
- direct `ai-dev-server` handoff

## Knowledge graph V3

The graph now includes:

```text
repository --contains------> component
component  --depends_on----> dependency
component  --implements----> capability
component  --calls---------> symbol
repository --provides------> capability
repository --classified_as-> profile
```

This improves reusable-boundary reasoning and makes hidden coupling more visible.

## Dependency version compatibility

Production-OS compares source and target dependency versions where version evidence can be extracted.

Statuses include:

```text
exact-match
same-major-review-required
major-version-mismatch
not-present-in-target
```

A major-version mismatch blocks direct adaptation until resolved.

## Validation feedback loop

After `ai-dev-server` executes an adaptation plan, validation results can be fed back into Production-OS:

```bash
production-os validation-results \
  --plan adaptation-plan.json \
  --results validation-results.json \
  --output validation-summary.json
```

The summary reports:

```text
passed
failed
pending
blocking_failures
promotion_allowed
```

Promotion is allowed only when every required validation step has passed.

Example result:

```json
{
  "summary": {
    "status": "blocked",
    "passed": 4,
    "failed": 1,
    "pending": 0,
    "blocking_failures": ["ci"]
  },
  "promotion_allowed": false
}
```

## ai-dev-server handoff V9

The handoff now includes:

- prioritized task
- repo/component reuse candidates
- adaptation risk
- reusable boundaries
- dependency compatibility
- dependency version compatibility
- missing dependencies
- major-version mismatches
- validation plan
- executable adaptation plans
- external star-list references

Promotion constraints include:

```text
resolve_missing_dependencies_before_promotion = true
reject_major_version_mismatch_before_promotion = true
complete_validation_plan_before_promotion = true
```

## Portfolio JSON V10

The full scan exports the same evidence and decisions used by the handoff, including Knowledge Graph V3 and version-aware adaptation plans.

## P1 status

### P0
- [x] Portfolio discovery
- [x] evidence model
- [x] maturity score
- [x] Next Best Action
- [x] ai-dev-server handoff
- [x] CI gate
- [x] snapshots
- [x] regressions
- [x] project classification

### P1
- [x] GitHub Actions state
- [x] capability fingerprints
- [x] deep source fingerprinting
- [x] recursive source-tree sampling
- [x] live star-list ingestion
- [x] source-symbol/component extraction
- [x] reusable component provenance
- [x] dependency graph
- [x] call/import graph refinement
- [x] component-aware reuse handoff
- [x] test-to-component linking
- [x] adaptation risk scoring
- [x] reusable boundary detection
- [x] automatic adaptation plans
- [x] target dependency compatibility
- [x] dependency version compatibility
- [x] automatic validation plans
- [x] validation-result ingestion

## Autonomous portfolio control

Production-OS can now convert the ranked action backlog into execution lanes:

```bash
production-os scan --owner dbrckk --schedule --capacity 3 --slots 3
```

The scheduler emits:

```text
NOW       highest-value primary task
PARALLEL  other repositories that fit current capacity
NEXT      queued high-value work
PAUSE     lower-value work
IGNORE    work below the current scheduling threshold
```

The resource allocator then assigns bounded execution slots to active repositories. This creates the first P2 control loop between portfolio priority and actual execution capacity.

## Execution feedback loop

After an `ai-dev-server` run, Production-OS can compare before/after snapshots plus validation status:

```bash
production-os execution-feedback \
  --before before.json \
  --after after.json \
  --repository dbrckk/deadline-zero \
  --validation-summary validation-summary.json
```

Possible decisions:

```text
promote
retry
rollback
replan
```

The decision is driven by validation status and measured maturity delta.

## Long-term trends

Multiple snapshots can now be aggregated:

```bash
production-os trends snapshots/2026-09-01.json snapshots/2026-09-14.json
```

Each repository receives a direction:

```text
improving
flat
regressing
```

These trend signals now feed the learning scheduler.

## Learning scheduler

Execution history can be supplied to scheduling:

```bash
production-os scan \
  --owner dbrckk \
  --schedule \
  --learning-events execution-events.json \
  --capacity 3 \
  --slots 3
```

Historical `promote / retry / rollback / replan` outcomes and measured score deltas produce a bounded learning weight. Successful high-yield work is favored; repeated rollbacks and low-yield loops are penalized.

## Control surface

The same scheduling command can emit a standalone HTML dashboard:

```bash
production-os scan \
  --owner dbrckk \
  --schedule \
  --dashboard artifacts/control.html
```

The control surface shows execution lanes, repository/task priorities, blockers, slot allocation, and the raw machine-readable payload. It has no runtime web-framework dependency.

### P2
- [x] autonomous scheduling
- [x] portfolio resource allocation
- [x] long-term trend history
- [x] automatic execution feedback loop
- [x] mobile/dashboard control surface

## Design principles

- Evidence over assumptions
- Deterministic decisions before LLM judgment
- Fail closed on missing evidence
- Reuse before rebuild
- Prefer low-risk tested components
- Adapt rather than blindly copy
- Validate before promotion
- Human approval for destructive or externally privileged actions


## P3 runtime safety

Production-OS now includes persistent execution safety primitives:

```text
execution journal
idempotency keys
leases
retry budgets
circuit breakers
cooldowns
duplicate-execution guards
```

Use persistent runtime state during scheduling:

```bash
production-os scan \
  --owner dbrckk \
  --schedule \
  --runtime-state artifacts/runtime-state.json
```

When a task is already leased, in cooldown, has an open circuit, or was already marked succeeded, the scheduler does not place it in an active execution lane.

Execution feedback can also persist the outcome:

```bash
production-os execution-feedback \
  --before before.json \
  --after after.json \
  --repository dbrckk/deadline-zero \
  --task "Restore the default branch CI to green" \
  --validation-summary validation-summary.json \
  --runtime-state artifacts/runtime-state.json \
  --journal artifacts/execution.jsonl
```

Repeated failures eventually open a circuit and start a cooldown instead of retrying indefinitely.

### P3

- [x] persistent execution journal
- [x] scheduler state persistence
- [x] task idempotency keys
- [x] execution leases
- [x] retry budgets
- [x] circuit breakers
- [x] cooldowns
- [x] duplicate-execution guards
- [x] GitHub issue/PR state ingestion
- [x] automatic dispatch to ai-dev-server
- [x] lease renewal/heartbeat
- [x] crash recovery reconciliation


### Operational P3 commands

Renew a lease:

```bash
production-os heartbeat \
  --runtime-state artifacts/runtime-state.json \
  --repository dbrckk/deadline-zero \
  --task "Restore the default branch CI to green" \
  --owner worker-1
```

Recover stale runtime state after restart/crash:

```bash
production-os reconcile \
  --runtime-state artifacts/runtime-state.json
```

Dispatch a generated handoff into the ai-dev-server file queue:

```bash
production-os dispatch \
  --handoff artifacts/handoff.json \
  --runtime-state artifacts/runtime-state.json \
  --queue-dir artifacts/ai-dev-server-queue \
  --owner production-os
```

Dispatch is guarded by the same idempotency key, lease, cooldown and circuit-breaker state used by the scheduler. Expired running leases are reconciled to `replan` rather than silently duplicated.


### GitHub work-state reconciliation

Production-OS can now reconcile runtime tasks against explicitly linked GitHub issues and pull requests.

Example mapping:

```json
{
  "mappings": [
    {
      "repository": "dbrckk/deadline-zero",
      "task": "Restore the default branch CI to green",
      "issue_number": 42,
      "pr_number": 57
    }
  ]
}
```

Run:

```bash
production-os github-reconcile \
  --mapping artifacts/github-mapping.json \
  --runtime-state artifacts/runtime-state.json \
  --journal artifacts/execution.jsonl
```

The reconciler reads:

```text
issue state
PR state
merged state
draft state
review state
head SHA
GitHub Actions state for the PR head
```

Decision mapping:

```text
PR merged
→ promote

CI failed
→ retry

review changes requested
→ retry

PR closed without merge
→ replan

PR still open / CI running
→ keep running
```

Mappings are explicit by design; Production-OS does not guess that an unrelated PR belongs to a runtime task.


## P4 continuous autonomous operation

Production-OS now includes a bounded continuous controller.

One safe cycle:

```bash
production-os controller \
  --owner dbrckk \
  --runtime-state artifacts/runtime-state.json \
  --queue-dir artifacts/ai-dev-server-queue \
  --snapshot-dir artifacts/snapshots \
  --metrics artifacts/metrics.json \
  --health artifacts/health.json \
  --journal artifacts/execution.jsonl \
  --cycles 1
```

Multiple bounded cycles:

```bash
production-os controller \
  --owner dbrckk \
  --runtime-state artifacts/runtime-state.json \
  --queue-dir artifacts/ai-dev-server-queue \
  --snapshot-dir artifacts/snapshots \
  --metrics artifacts/metrics.json \
  --health artifacts/health.json \
  --journal artifacts/execution.jsonl \
  --cycles 12 \
  --interval-seconds 300
```

Each cycle performs:

```text
runtime reconciliation
        ↓
portfolio scan
        ↓
assessment / action ranking
        ↓
schedule
        ↓
resource allocation
        ↓
guarded dispatch
        ↓
snapshot
        ↓
metrics
        ↓
health state
```

Health output includes:

```text
healthy / degraded
running task count
open circuit count
failed task count
controller metrics
last error
```

Metrics persist:

```text
cycles
scans
dispatches
dispatch failures
reconciliations
last cycle
last error
```

The controller is intentionally bounded by `--cycles`; continuous deployment environments can supervise/restart it rather than relying on an opaque infinite loop.

### P4

- [x] bounded autonomous control loop
- [x] periodic portfolio scans
- [x] automatic schedule refresh
- [x] guarded automatic dispatch
- [x] runtime reconciliation each cycle
- [x] per-cycle snapshots
- [x] persistent metrics
- [x] persistent health state
- [x] automatic GitHub reconciliation inside controller
- [x] lease heartbeat manager for active workers
- [x] self-healing policy engine
- [x] service/HTTP health endpoint
- [x] structured observability export


### P4 integrated supervision

The controller can now ingest explicit GitHub task mappings on every cycle:

```bash
production-os controller \
  --owner dbrckk \
  --runtime-state artifacts/runtime-state.json \
  --queue-dir artifacts/ai-dev-server-queue \
  --snapshot-dir artifacts/snapshots \
  --metrics artifacts/metrics.json \
  --health artifacts/health.json \
  --observability artifacts/observability.json \
  --journal artifacts/execution.jsonl \
  --github-mapping artifacts/github-mapping.json \
  --cycles 12 \
  --interval-seconds 300
```

Each cycle now performs:

```text
runtime reconciliation
→ self-healing
→ heartbeat renewal
→ GitHub issue/PR/CI reconciliation
→ portfolio scan
→ scheduling
→ guarded dispatch
→ snapshot
→ metrics
→ health
→ observability export
```

The self-healing policy handles:

```text
lost lease        → replan
repeated failure  → circuit-open
replan loop       → circuit-open
expired cooldown  → circuit recovery
```

A lightweight HTTP health endpoint is also available:

```bash
production-os health-server \
  --health artifacts/health.json \
  --host 127.0.0.1 \
  --port 8765
```

Endpoints:

```text
/
/health
/healthz
```

Healthy state returns HTTP 200. Degraded or missing health state returns HTTP 503.

Structured observability can be emitted to JSON and includes:

```text
health
metrics
runtime records
timestamp
```


## P5 multi-worker orchestration

Production-OS now supports a persistent worker registry with capability-aware routing and backpressure.

Register workers:

```bash
production-os worker-register \
  --registry artifacts/workers.json \
  --worker-id android-1 \
  --capability android \
  --max-concurrency 2

production-os worker-register \
  --registry artifacts/workers.json \
  --worker-id python-1 \
  --capability python \
  --max-concurrency 3
```

Worker heartbeat:

```bash
production-os worker-heartbeat \
  --registry artifacts/workers.json \
  --worker-id android-1 \
  --active-tasks 1
```

Inspect workers and detect stale/dead workers:

```bash
production-os worker-list \
  --registry artifacts/workers.json \
  --dead-timeout-seconds 120
```

Worker selection considers:

```text
required capabilities
current load
max concurrency
worker liveness
stable worker ID tie-break
```

If no capable worker is available, dispatch fails closed with backpressure rather than overloading an incompatible worker.

Direct worker-aware dispatch:

```bash
production-os dispatch \
  --handoff artifacts/handoff.json \
  --runtime-state artifacts/runtime-state.json \
  --queue-dir artifacts/queue \
  --worker-registry artifacts/workers.json \
  --required-capability android \
  --receipt-dir artifacts/receipts
```

The controller can also route automatically:

```bash
production-os controller \
  --owner dbrckk \
  --runtime-state artifacts/runtime-state.json \
  --queue-dir artifacts/queue \
  --snapshot-dir artifacts/snapshots \
  --metrics artifacts/metrics.json \
  --health artifacts/health.json \
  --journal artifacts/execution.jsonl \
  --worker-registry artifacts/workers.json \
  --receipt-dir artifacts/receipts \
  --cycles 12
```

Current routing rules infer a first-pass worker affinity from repository profile/language:

```text
android-app / android-game → android worker
Python repository          → python worker
JavaScript/TypeScript      → node worker
```

Dispatch receipts persist:

```text
idempotency key
worker ID
repository
task
status
timestamp
```

### P5

- [x] persistent worker registry
- [x] worker capabilities
- [x] worker load tracking
- [x] capability/task affinity
- [x] dead-worker detection
- [x] max-concurrency backpressure
- [x] worker-aware dispatch
- [x] dispatch receipts
- [x] acknowledgement/claim protocol
- [x] worker completion accounting
- [x] priority preemption
- [x] queue fairness
- [x] at-least-once delivery recovery


### P5 delivery protocol

Worker claim:

```bash
production-os job-claim \
  --claims artifacts/claims.json \
  --queue-file artifacts/queue/<job>.json \
  --worker-id python-1
```

Acknowledge:

```bash
production-os job-ack \
  --claims artifacts/claims.json \
  --key <idempotency-key> \
  --worker-id python-1
```

Complete and release accounting:

```bash
production-os job-complete \
  --claims artifacts/claims.json \
  --key <idempotency-key> \
  --worker-id python-1 \
  --registry artifacts/workers.json \
  --runtime-state artifacts/runtime-state.json
```

Expired unacknowledged jobs can be recovered:

```bash
production-os delivery-recover \
  --claims artifacts/claims.json \
  --registry artifacts/workers.json \
  --runtime-state artifacts/runtime-state.json \
  --queue-dir artifacts/queue \
  --dead-letter-dir artifacts/dead-letter
```

The continuous controller can perform the same recovery every cycle with:

```text
--claims artifacts/claims.json
--dead-letter-dir artifacts/dead-letter
```

Delivery semantics are now at-least-once with explicit idempotency guards. An expired unacked delivery releases the worker slot and task lease before redelivery/dead-letter handling.

Queue ordering now uses round-robin inter-repository fairness while preserving score order inside each repository. This prevents one repository with many high-ranked actions from monopolizing the pending queue.


### P5 cooperative priority preemption

Preemption is cooperative and checkpoint-based. Production-OS never force-kills an arbitrary running task.

Only tasks explicitly marked interruptible can be preempted.

Request:

```bash
production-os preempt-request \
  --runtime-state artifacts/runtime-state.json \
  --repository dbrckk/ai-dev-server \
  --task "Lower priority task"
```

The worker checkpoints, then confirms:

```bash
production-os preempt-checkpoint \
  --runtime-state artifacts/runtime-state.json \
  --registry artifacts/workers.json \
  --repository dbrckk/ai-dev-server \
  --task "Lower priority task" \
  --worker-id python-1 \
  --checkpoint-ref checkpoint://run-123
```

The task transitions:

```text
running
→ preempt-requested
→ checkpoint persisted
→ paused
→ worker slot released
→ task becomes eligible for later resume/replan
```

Safe victim selection considers:

```text
worker capability compatibility
task interruptibility
incoming vs running priority gap
lowest running priority first
```

A task without an explicit checkpoint is never released merely because a higher-priority task exists.

## P6 production hardening

Production-OS now adds stronger multi-process safety and operator controls.

### Atomic state + inter-process locks

Critical stores now use atomic replace semantics and sidecar locks:

```text
runtime-state.json
workers.json
claims.json
```

Critical mutations use a read-modify-write transaction under lock instead of loading stale state and overwriting another process.

Current persistent schemas:

```text
production-os/runtime-state/v2
production-os/workers/v2
production-os/claims/v2
```

Upgrade older v1 state:

```bash
production-os migrate-state --path artifacts/runtime-state.json
```

### Transactional dispatch

Dispatch now checks emergency stop, rate limits and approval gates before lease acquisition; queue writes are atomic and partial failures roll back worker load and lease state.

### Global emergency stop

```bash
production-os emergency-stop --state artifacts/emergency-stop.json --reason "operator intervention"
production-os emergency-resume --state artifacts/emergency-stop.json
```

Controller option:

```text
--emergency-stop artifacts/emergency-stop.json
```

When active, new dispatches are blocked while reconciliation and observability can continue.

### Persistent rate limits

```text
--rate-limit-state artifacts/rate-limits.json
```

Dispatch volume is bounded per repository and per worker over a rolling window.

### Human approval gates

A handoff may declare requires_human_approval=true. Such a task is blocked until its idempotency key is explicitly approved.

```bash
production-os approve --store artifacts/approvals.json --key <task-key> --approved-by operator --reason reviewed
production-os revoke --store artifacts/approvals.json --key <task-key> --approved-by operator
```

Controller option:

```text
--approvals artifacts/approvals.json
```

### Audit integrity

The execution journal now uses a SHA-256 hash chain.

```bash
production-os audit-verify --journal artifacts/execution.jsonl
```

### Backup / restore

```bash
production-os backup --destination-dir artifacts/backups artifacts/runtime-state.json artifacts/workers.json artifacts/claims.json artifacts/approvals.json
production-os restore --manifest artifacts/backups/<timestamp>/manifest.json --verify-only
production-os restore --manifest artifacts/backups/<timestamp>/manifest.json
```

### P6

- [x] atomic state writes
- [x] inter-process sidecar locks
- [x] read-modify-write locking on critical stores
- [x] transactional dispatch rollback
- [x] persistent rate limits
- [x] global emergency stop
- [x] manual approval gates
- [x] audit hash chain
- [x] backup with checksums
- [x] checksum-verified restore
- [x] explicit state migrations v1→v2
- [x] queue compaction
- [x] dead-letter retry policy
- [x] richer migration registry
- [x] signed audit checkpoints

### P6 maintenance commands

Compact completed queue entries:

```bash
production-os queue-compact --queue-dir artifacts/queue --claims artifacts/claims.json --archive-dir artifacts/queue-archive
```

Retry dead-letter jobs within a bounded attempt budget:

```bash
production-os dead-letter-retry --dead-letter-dir artifacts/dead-letter --queue-dir artifacts/queue --max-attempts 3
```

Batch state migrations:

```bash
production-os migrate-many artifacts/runtime-state.json artifacts/workers.json artifacts/claims.json
```

Create and verify an HMAC-signed audit checkpoint:

```bash
production-os audit-checkpoint-create --journal artifacts/execution.jsonl --checkpoint artifacts/audit-checkpoint.json --secret <secret>
production-os audit-checkpoint-verify --checkpoint artifacts/audit-checkpoint.json --secret <secret>
```

Legacy unchained journal rows are reported as unverified legacy history; once the hash chain starts, any later unchained/tampered row invalidates verification.

## P7 policy and governance

Production-OS now supports policy-as-code with global defaults and per-repository overrides.

Example configuration:

```text
config/policy.example.json
```

Validate before use:

```bash
production-os policy-validate --policy config/policy.example.json
```

Explain one handoff decision:

```bash
production-os policy-check --policy config/policy.example.json --handoff artifacts/handoff.json
```

### Governed controls

Policies can define:

```text
max_risk_class
approval_required_from
allowed_worker_classes
freeze_timezone
freeze_windows
freeze_risk_classes
require_branch_protection_for
auto_quarantine_after_failures
budgets
slo.max_runtime_minutes
slo.max_attempts
slo.max_consecutive_failures
```

Portfolio-wide budgets are also supported through `portfolio_budgets`.

### Risk classes

```text
low
medium
high
critical
```

Release/deploy/publish-style work is classified high by default; destructive or externally privileged work is critical unless an explicit risk class is supplied.

### Scheduling and dispatch enforcement

The scheduler applies policy/freeze/quarantine blockers before allocating active lanes. Runtime evidence gates such as branch protection are intentionally deferred until dispatch, where they fail closed.

For policies that require branch protection, the controller reads the default branch protection state from GitHub. A false or unavailable protection result blocks a governed high/critical dispatch.

### Budgets

Persistent ledger:

```text
--budgets artifacts/budgets.json
```

Supported budget dimensions are generic numeric keys; the standard policy example uses:

```text
tokens
cost
minutes
```

A handoff may provide projected usage:

```json
{
  "resource_request": {
    "tokens": 120000,
    "cost": 2.5,
    "minutes": 30
  }
}
```

When a projected request is present it is checked against both repository and portfolio budgets before dispatch and recorded on successful dispatch. Without a projected request, existing ledger exhaustion is still enforceable but future consumption cannot be predicted; actual usage can be recorded explicitly:

```bash
production-os budget-record --ledger artifacts/budgets.json --repository dbrckk/ai-dev-server --tokens 120000 --cost 2.5 --minutes 30
```

### Quarantine

Manual quarantine:

```bash
production-os quarantine --store artifacts/quarantine.json --repository dbrckk/deadline-zero --reason "operator review"
production-os unquarantine --store artifacts/quarantine.json --repository dbrckk/deadline-zero
```

Automatic quarantine can trigger from repeated failures, circuit-open state, excessive attempts, excessive consecutive failures, or max runtime SLO violations.

### Continuous controller

```bash
production-os controller \
  --owner dbrckk \
  --runtime-state artifacts/runtime-state.json \
  --queue-dir artifacts/queue \
  --snapshot-dir artifacts/snapshots \
  --metrics artifacts/metrics.json \
  --health artifacts/health.json \
  --journal artifacts/execution.jsonl \
  --worker-registry artifacts/workers.json \
  --policy config/policy.example.json \
  --budgets artifacts/budgets.json \
  --quarantine artifacts/quarantine.json \
  --approvals artifacts/approvals.json \
  --cycles 12
```

### P7

- [x] policy-as-code
- [x] global defaults + per-repo overrides
- [x] risk classification
- [x] mandatory approval by risk
- [x] allowed worker classes
- [x] repository budgets
- [x] portfolio-wide budgets
- [x] timezone-aware freeze windows
- [x] branch protection awareness
- [x] fail-closed runtime evidence gates
- [x] SLO runtime/attempt/failure limits
- [x] automatic quarantine
- [x] manual quarantine controls
- [x] policy validation
- [x] explainable policy decisions

## P8 distributed runtime

Production-OS now includes a dependency-free distributed runtime based on SQLite WAL and the Python standard library.

### SQLite backend

Initialize:

```bash
production-os db-init --database artifacts/production.db
```

Import legacy JSON state:

```bash
production-os db-import \
  --database artifacts/production.db \
  --runtime-state artifacts/runtime-state.json \
  --workers artifacts/workers.json \
  --claims artifacts/claims.json
```

SQLite stores:

```text
runtime records
workers
claims
durable jobs
event stream
schema metadata
```

The database runs with WAL, foreign keys, NORMAL synchronous mode and a 30-second busy timeout.

### Durable dispatch

Direct durable dispatch:

```bash
production-os dispatch \
  --handoff artifacts/handoff.json \
  --queue-dir artifacts/queue \
  --database artifacts/production.db
```

Continuous controller on SQLite:

```bash
production-os controller \
  --owner dbrckk \
  --database artifacts/production.db \
  --queue-dir artifacts/queue \
  --snapshot-dir artifacts/snapshots \
  --metrics artifacts/metrics.json \
  --health artifacts/health.json \
  --journal artifacts/execution.jsonl \
  --policy config/policy.example.json \
  --budgets artifacts/budgets.json \
  --quarantine artifacts/quarantine.json \
  --approvals artifacts/approvals.json \
  --cycles 12
```

When `--database` is used, runtime state, workers, claims and the execution queue use SQLite. Existing JSON mode remains supported.

### API authentication and RBAC

Generate a token digest:

```bash
production-os token-hash --token '<secret>'
```

Copy `config/auth.example.json`, replace the placeholder digest, and assign a role:

```text
viewer
worker
operator
admin
```

Role ordering:

```text
viewer < worker < operator < admin
```

Raw tokens are not stored in the auth configuration; only SHA-256 digests are stored.

### Control-plane API

```bash
production-os control-plane \
  --database artifacts/production.db \
  --auth-config artifacts/auth.json \
  --host 0.0.0.0 \
  --port 8787
```

Endpoints:

```text
GET  /health
GET  /dashboard
GET  /v1/stats
GET  /v1/events
GET  /v1/workers
GET  /v1/jobs/<key>
POST /v1/workers/register
POST /v1/workers/heartbeat
POST /v1/jobs/enqueue
POST /v1/jobs/claim
POST /v1/jobs/ack
POST /v1/jobs/complete
POST /v1/jobs/fail
POST /v1/jobs/recover
```

The dashboard shell is served from `/dashboard`. It asks for a Bearer token locally and sends it only in the Authorization header.

### Remote workers

A remote worker can poll the control plane:

```bash
production-os remote-worker-poll \
  --url http://127.0.0.1:8787 \
  --token '<worker-token>' \
  --worker-id python-1 \
  --capability python \
  --cycles 10
```

The worker protocol supports heartbeat, capability-aware claim, acknowledgement, completion and failure reporting.

### Docker

Prepare `artifacts/auth.json`, then:

```bash
docker compose up --build
```

The service exposes port `8787` and persists the SQLite database in `./artifacts`.

### P8

- [x] SQLite WAL transactional backend
- [x] legacy JSON import
- [x] runtime-state compatibility layer
- [x] worker-registry compatibility layer
- [x] claims compatibility layer
- [x] durable job queue
- [x] transactional job claiming
- [x] expired claim recovery
- [x] HTTP control-plane API
- [x] bearer-token authentication
- [x] RBAC
- [x] remote worker protocol
- [x] persistent event stream
- [x] live dashboard
- [x] Docker image
- [x] Docker Compose startup
- [x] optional PostgreSQL backend
- [x] TLS termination / reverse-proxy reference config

### PostgreSQL deployment

Production-OS accepts either a SQLite path or a PostgreSQL DSN through the same `--database` option.

Example:

```bash
production-os db-init \
  --database postgresql://production_os:password@127.0.0.1:5432/production_os
```

Control plane:

```bash
production-os control-plane \
  --database postgresql://production_os:password@127.0.0.1:5432/production_os \
  --auth-config artifacts/auth.json \
  --host 0.0.0.0 \
  --port 8787
```

Docker Compose:

```bash
cp deploy/.env.postgres.example .env
# edit POSTGRES_PASSWORD
docker compose -f compose.postgres.yaml up --build
```

The PostgreSQL queue uses transactional row locks and `FOR UPDATE SKIP LOCKED` for concurrent worker claims.

### TLS deployment

Reference files:

```text
deploy/Caddyfile
compose.tls.yaml
deploy/.env.example
```

Start:

```bash
cp deploy/.env.example .env
# edit DOMAIN and ACME_EMAIL
docker compose -f compose.tls.yaml up --build
```

Caddy terminates HTTPS, applies security headers and proxies to the Production-OS control plane health-checked through `/healthz`.

## P9 persistent workflow engine

Production-OS now supports persistent multi-step DAG workflows on both SQLite and PostgreSQL.

Example workflow:

```text
config/workflow.example.json
```

Create:

```bash
production-os workflow-create \
  --database artifacts/production.db \
  --spec config/workflow.example.json
```

Inspect:

```bash
production-os workflow-status \
  --database artifacts/production.db \
  --workflow-id <workflow-id>
```

Dispatch currently ready tasks:

```bash
production-os workflow-dispatch \
  --database artifacts/production.db \
  --workflow-id <workflow-id>
```

Critical path:

```bash
production-os workflow-critical-path \
  --database artifacts/production.db \
  --workflow-id <workflow-id>
```

Cancel:

```bash
production-os workflow-cancel \
  --database artifacts/production.db \
  --workflow-id <workflow-id>
```

Register an artifact:

```bash
production-os artifact-add \
  --database artifacts/production.db \
  --workflow-id <workflow-id> \
  --task-id package \
  --name app-release.aab \
  --uri artifact://release/app-release.aab \
  --sha256 <sha256>
```

### Workflow semantics

Task lifecycle:

```text
pending
→ ready
→ queued
→ succeeded
```

Failure with retry budget:

```text
queued
→ failed attempt
→ automatic redispatch
→ queued
```

Terminal failure:

```text
retry budget exhausted
→ failed
→ dependent tasks blocked
→ workflow failed
```

Each retry uses a unique per-attempt idempotency key, while duplicate dispatch inside the same attempt remains guarded.

### Fan-out / fan-in

Dependencies are explicit. Multiple children can become ready after one task succeeds, and a downstream task becomes ready only when all of its dependencies have succeeded.

Example:

```text
build
 ├─ unit-tests
 └─ lint
      ↓
   package
```

### API

```text
GET  /v1/workflows
GET  /v1/workflows/<id>
GET  /v1/workflows/<id>/critical-path
POST /v1/workflows
POST /v1/workflows/<id>/dispatch
POST /v1/workflows/<id>/cancel
POST /v1/workflows/<id>/artifacts
```

Worker job completion/failure automatically updates the linked workflow task and dispatches newly unblocked tasks.

### Critical path

Each task can define `estimated_minutes`. Production-OS computes the longest dependency path, giving a first deterministic estimate of the workflow bottleneck.

### Artifacts

Artifacts persist:

```text
workflow
task
name
URI
SHA-256
metadata
timestamp
```

### P9

- [x] persistent workflows
- [x] DAG validation
- [x] cycle detection
- [x] explicit task dependencies
- [x] fan-out
- [x] fan-in
- [x] automatic downstream dispatch
- [x] bounded retries
- [x] per-attempt idempotency
- [x] dependent-task blocking
- [x] workflow cancellation
- [x] critical-path calculation
- [x] artifact registry
- [x] SQLite support
- [x] PostgreSQL support
- [x] control-plane API
- [x] CLI controls
- [x] remote-worker result propagation
- [x] dashboard workflow visibility


## P10 adaptive execution optimizer

Production-OS now learns from historical execution telemetry instead of relying only on static task estimates.

### Learned execution history

Workers can report duration and capability telemetry on job completion or failure. Production-OS persists:

```text
repository
task
worker
duration
success/failure
worker capabilities
timestamp
```

The history is available on both SQLite and PostgreSQL.

### Duration prediction

Predictions use successful historical observations with a robust trimmed mean when enough samples exist. Static `estimated_minutes` remains the cold-start fallback.

### Reliability-aware worker placement

The optimizer scores eligible workers using:

```text
predicted task duration
× current worker load
÷ historical reliability
```

A fast but repeatedly failing worker is therefore penalized against a slightly slower stable worker.

### Workflow ETA

```bash
production-os workflow-eta \
  --database artifacts/production.db \
  --workflow-id <workflow-id>
```

API:

```text
GET /v1/workflows/<id>/eta
```

The result contains the predicted remaining duration and learned critical task path.

### P10 progress

- [x] execution-history persistence
- [x] SQLite telemetry
- [x] PostgreSQL telemetry
- [x] robust task-duration prediction
- [x] prediction confidence
- [x] worker performance profiles
- [x] reliability-aware worker ranking
- [x] worker-load penalty
- [x] capability-aware placement
- [x] learned workflow ETA
- [x] learned critical path
- [x] remote-worker telemetry protocol
- [x] API ETA endpoint
- [x] CLI ETA command
- [x] SQLite optimizer tests
- [x] PostgreSQL optimizer tests
- [x] automatic placement in queue claiming
- [x] cache/reuse detection
- [x] redundant-work elimination
- [x] speculative execution
- [x] straggler detection
- [x] automatic task splitting
- [x] portfolio-wide throughput optimizer


### Automatic worker placement

Job claims now use a two-stage optimizer:

```text
portfolio job ranking
→ capability filter
→ learned worker placement
→ exact transactional claim
```

A polling worker receives a job only when it is both:

1. the highest-value compatible queued job for the portfolio;
2. assigned to the best currently available worker according to learned execution history.

### Result cache and redundant-work elimination

Workflow tasks can opt in:

```json
{
  "cacheable": true,
  "cache_inputs": {
    "commit": "abc123",
    "toolchain": "android-35"
  }
}
```

The cache fingerprint covers repository, task and canonicalized cache inputs.

On a cache hit:

```text
ready
→ cache lookup
→ succeeded
→ downstream dependencies unlocked
```

No worker slot is consumed.

### Straggler detection

```bash
production-os stragglers \
  --database artifacts/production.db \
  --threshold-factor 1.75 \
  --min-runtime-seconds 60 \
  --min-samples 2
```

API:

```text
GET /v1/stragglers
```

A straggler is compared against learned historical duration. Production-OS can also recommend a faster eligible alternate worker.

### Safe speculative execution

Only explicitly safe jobs can be duplicated:

```json
{
  "constraints": {
    "speculative_safe": true
  }
}
```

Operator command:

```bash
production-os speculate-stragglers \
  --database artifacts/production.db
```

Control-plane endpoint:

```text
POST /v1/stragglers/speculate
```

Speculative copies use a persistent speculation group:

```text
slow original ─┐
               ├→ first successful completion wins
fast duplicate ─┘
                         ↓
                  losing copies cancelled
```

An individual speculative failure does not fail the workflow while another copy is still viable.

### Automatic task splitting

A workflow task may opt into deterministic sharding:

```json
{
  "splittable": true,
  "split_items": [1, 2, 3, 4, 5],
  "split_size": 2
}
```

Production-OS expands it into:

```text
task#shard-1 ─┐
task#shard-2 ─┼→ virtual barrier → downstream task
task#shard-3 ─┘
```

The virtual barrier consumes no worker and succeeds automatically once every shard succeeds.

### Portfolio throughput optimizer

Queued work is no longer ordered only by static priority.

The runtime score considers:

```text
business priority
+ critical-path membership
+ number of downstream tasks unlocked
+ queue age / anti-starvation
- predicted execution duration
```

This ordering is combined with exact-key transactional claims, so SQLite and PostgreSQL preserve concurrency safety while using the adaptive ranking.

## P11 incremental workflow execution

Production-OS can now prune workflow work deterministically from an explicit changed-path set.

A task opts in through its payload:

    {
      "impact": {
        "paths": ["src/**", "tests/**"],
        "exclude_paths": ["src/generated/**"],
        "skip_when_unaffected": true
      }
    }

Tasks that do not explicitly opt in continue to execute. Missing impact patterns and unknown or empty change sets are fail-closed by default.

To intentionally treat an empty change set as safe to skip:

    {
      "impact": {
        "paths": ["docs/**"],
        "skip_when_unaffected": true,
        "allow_empty_changes": true
      }
    }

Tasks can also force execution with:

    {
      "impact": {
        "always_run": true
      }
    }

Impact propagation is dependency-aware: once a task is affected, all downstream tasks are considered affected even when their own direct path patterns do not match.

CLI:

    production-os workflow-impact \
      --database artifacts/production.db \
      --workflow-id <workflow-id> \
      --changed-path src/core.py \
      --changed-path tests/test_core.py

A workflow may also provide changed paths at creation time through metadata. Unaffected opt-in tasks are recorded as successful skips with the reason and changed-path evidence persisted in their result.

Control-plane API:

    POST /v1/workflows/<id>/impact

Request body:

    {
      "changed_paths": ["src/core.py", "tests/test_core.py"]
    }

### P11

- [x] deterministic changed-path analysis
- [x] explicit opt-in task pruning
- [x] fail-closed defaults
- [x] empty-change safety
- [x] path normalization
- [x] include patterns
- [x] exclude patterns
- [x] always-run tasks
- [x] downstream dependency propagation
- [x] persisted skip evidence
- [x] workflow-create integration
- [x] CLI impact command
- [x] control-plane impact API
- [x] regression tests

## P12 GitHub-driven incremental execution

Production-OS can now derive workflow impact directly from a GitHub pull request instead of requiring a manually assembled changed-path list.

CLI:

    production-os workflow-impact-pr \
      --database artifacts/production.db \
      --workflow-id <workflow-id> \
      --repository dbrckk/project \
      --pr-number 123

The GitHub client paginates the pull-request files API and deduplicates changed paths before impact analysis.

Control-plane API:

    POST /v1/workflows/<id>/impact-pr

Request:

    {
      "repository": "dbrckk/project",
      "pr_number": 123
    }

The response includes the authoritative changed-path set, impact decisions, and updated workflow state.

Safety semantics:

- GitHub changed-file retrieval is fail-closed.
- API failures do not degrade into an empty change set.
- malformed GitHub responses are rejected.
- workflow impact still uses the P11 fail-closed rules.
- impact recomputation is refused after actual execution has started.
- large pull requests are paginated beyond the first 100 files.

Automatic refresh for every workflow bound to the same PR is available through metadata:

    {
      "github_pr_number": 123
    }

Then run:

    production-os pr-refresh \
      --database artifacts/production.db \
      --repository dbrckk/project \
      --pr-number 123

Control-plane equivalent:

    POST /v1/github/pr-refresh

### Signed GitHub webhook

Set a shared webhook secret in the control-plane environment:

    export PRODUCTION_OS_GITHUB_WEBHOOK_SECRET='<strong-random-secret>'

Configure the GitHub webhook target:

    POST https://<production-os-host>/v1/github/webhook

The endpoint validates `X-Hub-Signature-256` against the exact raw request body. It does not use bearer authentication because GitHub authenticates the request with the HMAC signature.

Supported pull-request actions:

    opened
    reopened
    synchronize

For a supported delivery:

    signed webhook
        ↓
    durable X-GitHub-Delivery claim
        ↓
    repository + PR workflow binding
        ↓
    authoritative changed-file retrieval
        ↓
    P11 impact pruning
        ↓
    minimal ready-task dispatch

Delivery IDs are persisted in SQLite/PostgreSQL, so GitHub retries cannot duplicate production work. If processing fails before completion, the delivery claim is released so a legitimate GitHub retry can be processed.

Unsupported GitHub events/actions are acknowledged and ignored after signature verification.

### P12 progress

- [x] GitHub PR changed-file ingestion
- [x] pagination for large pull requests
- [x] changed-path deduplication
- [x] fail-closed GitHub retrieval
- [x] CLI PR impact command
- [x] authenticated control-plane PR impact endpoint
- [x] GitHub ingestion regression tests
- [x] control-plane integration test
- [x] automatic workflow binding from repository + PR
- [x] PR-bound workflow refresh command/API
- [x] signed GitHub webhook ingestion
- [x] HMAC SHA-256 signature validation
- [x] durable event idempotency / delivery replay guard
- [x] SQLite webhook delivery persistence
- [x] PostgreSQL webhook delivery persistence
- [x] automatic refresh for opened/reopened/synchronize
- [x] automatic minimal dispatch after impact refresh
- [x] webhook signature/idempotency integration tests
- [x] Docker/deployment secret wiring
- [ ] automatic workflow creation for previously unseen PRs
- [ ] PR head-SHA generation binding
- [ ] superseded-generation cancellation/checkpoint handoff

## P13 PR workflow generations

Production-OS now binds incremental execution to the exact pull-request head SHA.

Each PR workflow carries:

    github_pr_number
    github_pr_head_sha
    github_pr_generation

Jobs dispatched from the workflow also carry:

    workflow_generation
    source_revision

This prevents workers from treating work produced for an older PR revision as current.

### Generation rotation

When GitHub sends a supported pull-request webhook with a new head SHA:

    generation N / sha-A
        ↓
    synchronize webhook / sha-B
        ↓
    clone DAG as generation N+1
        ↓
    mark generation N superseded
        ↓
    cancel queued / claimed / acked jobs from generation N
        ↓
    recompute changed-path impact for sha-B
        ↓
    dispatch only the minimal ready sub-DAG

The superseded workflow remains persisted for auditability and records:

    superseded = true
    superseded_by_workflow_id
    superseded_by_head_sha

A first webhook for a PR-bound workflow that does not yet have a head SHA binds the SHA in place as generation 1 instead of creating an artificial generation 2.

### Same-SHA idempotency

A separate GitHub delivery for a head SHA that is already executing or completed is treated as a generation no-op.

Production-OS does not:

- recompute impact;
- refetch PR files;
- enqueue duplicate jobs.

This is independent from the X-GitHub-Delivery replay guard and protects against logically duplicate events with different delivery IDs.

### Automatic workflows for unseen PRs

A repository can define a reusable PR workflow template with:

    {
      "github_pr_template": true
    }

When an opened/reopened/synchronize webhook arrives for a PR with no bound workflow, Production-OS clones the latest repository template and binds:

    github_pr_number
    github_pr_head_sha
    github_pr_generation = 1
    github_pr_template_workflow_id

The resulting workflow then enters the normal P11/P12 incremental path.

### P13 progress

- [x] PR head-SHA binding
- [x] explicit workflow generation numbers
- [x] generation N→N+1 DAG cloning
- [x] superseded workflow metadata
- [x] cancellation of superseded queued jobs
- [x] cancellation of superseded claimed/acked jobs
- [x] source revision stamped into dispatched jobs
- [x] workflow generation stamped into dispatched jobs
- [x] same-SHA generation no-op
- [x] skip redundant GitHub changed-file fetches
- [x] initial generation-1 binding without artificial clone
- [x] repository PR workflow templates
- [x] automatic workflow creation for unseen PRs
- [x] generation rotation regression tests
- [x] webhook template auto-creation tests
- [x] cooperative checkpoint acknowledgement from workers on supersession
- [x] worker-side stale-generation heartbeat rejection
- [x] artifact promotion guard against superseded source revisions

### P13 stale-generation enforcement

Generation freshness is enforced across the worker and artifact lifecycle.

Worker heartbeat may report active job keys:

    POST /v1/workers/heartbeat

    {
      "worker_id": "python-1",
      "active_tasks": 1,
      "active_job_keys": ["<job-key>"]
    }

The response contains:

    {
      "stale_job_keys": ["<job-key>"]
    }

A superseded job is rejected from:

- queue candidate selection;
- acknowledgement;
- completion;
- failure reporting.

A worker can checkpoint useful partial state before stopping:

    POST /v1/jobs/stale-checkpoint

    {
      "key": "<job-key>",
      "worker_id": "python-1",
      "checkpoint_ref": "checkpoint://..."
    }

The checkpoint is persisted in the durable event stream as `stale-job-checkpointed` with workflow generation and source revision evidence.

Artifacts belonging to PR workflows must carry:

    source_revision
    workflow_generation

Artifact registration fails closed when:

- the workflow was superseded;
- source_revision differs from the workflow head SHA;
- workflow_generation differs from the current generation;
- revision/generation evidence is missing for a PR workflow.

This prevents stale results from being promoted even if a worker finishes after a new commit reaches the PR.

## P14 transactional release promotion

Production-OS now separates successful execution from release promotion.

A successful job or workflow is not sufficient to create a release. Promotion requires:

    workflow status = succeeded
    validation status = passed
    promotion_allowed != false
    blocking_failures = []
    artifact SHA-256 = valid 64-character digest
    PR source_revision = current head SHA
    workflow_generation = current generation
    workflow not superseded

The freshness checks and release insert execute in the same database transaction. PostgreSQL additionally locks the workflow and artifact rows during promotion.

### Immutable release ledger

Promotions are append-only records containing:

    release ID
    workflow ID
    artifact ID
    repository
    source revision
    workflow generation
    validation evidence
    artifact SHA-256
    release metadata
    status
    timestamp

The original artifact is never mutated into a release.

Each artifact may be promoted only once.

SQLite and PostgreSQL both enforce this with a unique release constraint.

### Promotion API

    POST /v1/workflows/<workflow-id>/promote

Example:

    {
      "artifact_id": "<artifact-id>",
      "validation": {
        "status": "passed",
        "promotion_allowed": true,
        "blocking_failures": []
      },
      "metadata": {
        "channel": "internal"
      }
    }

Read releases:

    GET /v1/workflows/<workflow-id>/releases
    GET /v1/releases/<release-id>

### CLI

Promote:

    production-os release-promote \
      --database artifacts/production.db \
      --workflow-id <workflow-id> \
      --artifact-id <artifact-id> \
      --validation validation-summary.json

Optional release metadata:

    --metadata release-metadata.json

PR artifacts can be registered with explicit provenance:

    production-os artifact-add \
      --database artifacts/production.db \
      --workflow-id <workflow-id> \
      --name app.aab \
      --uri artifact://app.aab \
      --sha256 <64-char-sha256> \
      --source-revision <git-sha> \
      --workflow-generation 3

### Append-only rollback

A rollback never edits or deletes the promoted release.

It appends a separate immutable record:

    POST /v1/releases/<release-id>/rollback

Request:

    {
      "reason": "regression detected",
      "metadata": {
        "incident": "INC-123"
      }
    }

CLI:

    production-os release-rollback \
      --database artifacts/production.db \
      --release-id <release-id> \
      --reason "regression detected"

The rollback record points to the original release through `rollback_of`. Only one rollback record is allowed per promoted release.

### P14 progress

- [x] immutable release ledger
- [x] SQLite release persistence
- [x] PostgreSQL release persistence
- [x] schema version 7
- [x] atomic promotion transaction
- [x] PostgreSQL row locking during promotion
- [x] workflow-success gate
- [x] validation-pass gate
- [x] blocking-failure gate
- [x] valid SHA-256 artifact gate
- [x] PR source-revision gate
- [x] PR generation gate
- [x] superseded-workflow rejection
- [x] single-promotion constraint per artifact
- [x] append-only rollback records
- [x] single-rollback constraint
- [x] release audit events
- [x] control-plane promotion API
- [x] control-plane rollback API
- [x] release read API
- [x] promotion/rollback CLI
- [x] artifact provenance CLI flags
- [x] promotion ledger tests
- [x] API integration test
- [ ] cryptographic attestation of validation producer
- [ ] signed provenance envelope
- [ ] policy approval binding to release record

## P15 signed validation and provenance attestations

Release promotion now requires cryptographic validation evidence.

Production-OS uses canonical JSON + HMAC-SHA256 for two independent trust boundaries:

    validator secret
        ↓
    validation attestation
        ↓
    transactional release promotion
        ↓
    release provenance secret
        ↓
    signed release provenance

No validation or provenance signing secret is persisted in workflow, artifact, release, or audit records.

### Trusted validator configuration

The control plane reads trusted validator identities from:

    PRODUCTION_OS_VALIDATION_ATTESTATION_KEYS

Example:

    {
      "validator-1": "strong-validator-secret"
    }

Release provenance uses a separate secret:

    PRODUCTION_OS_RELEASE_PROVENANCE_SECRET

A validator key and the release provenance key should not be the same secret.

### Validation attestation

Generate a signed attestation for one exact artifact:

    export PRODUCTION_OS_VALIDATION_ATTESTATION_SECRET='<validator-secret>'

    production-os validation-attest \
      --database artifacts/production.db \
      --workflow-id <workflow-id> \
      --artifact-id <artifact-id> \
      --validation validation-summary.json \
      --validator-id validator-1 \
      --output validation-attestation.json

The attestation is bound to:

    validator_id
    workflow_id
    artifact_id
    artifact_sha256
    source_revision
    workflow_generation
    validation payload
    issued_at

Changing any bound value invalidates the attestation.

Attestations are accepted only from configured validator identities and are fresh for one hour by default. Excessively future-dated attestations are rejected.

### Signed promotion

CLI promotion now requires both the validation result and its attestation:

    production-os release-promote \
      --database artifacts/production.db \
      --workflow-id <workflow-id> \
      --artifact-id <artifact-id> \
      --validation validation-summary.json \
      --attestation validation-attestation.json \
      --approved-by local-operator \
      --approval-role operator

Control-plane promotion:

    POST /v1/workflows/<workflow-id>/promote

The authenticated bearer principal is used as the release approver. The client cannot choose a different approved_by identity through the API.

### Approval binding

Every promoted release records an approval bound to:

    workflow_id
    artifact_id
    artifact_sha256
    source_revision
    workflow_generation

Production-OS computes a deterministic SHA-256 approval key for this tuple.

The signed provenance envelope includes:

    approval_key
    approved_by
    approval_role

Changing the artifact, source revision, or workflow generation therefore changes the approval key and invalidates reuse of the old approval.

### Signed release provenance

The immutable release stores a signed provenance envelope containing:

    release_id
    workflow_id
    artifact_id
    repository
    artifact_sha256
    source_revision
    workflow_generation
    validator_id
    validation attestation signature
    approval_key
    approved_by
    approval_role
    release creation timestamp

The provenance envelope and the release row are persisted in the same database transaction.

### Release verification

CLI:

    production-os release-verify \
      --database artifacts/production.db \
      --release-id <release-id>

API:

    GET /v1/releases/<release-id>/verify

Verification checks:

    trusted validator identity
    validation attestation signature
    exact attestation bindings
    release provenance signature
    exact provenance bindings
    artifact digest
    source revision
    workflow generation
    operator approval identity

A release remains independently auditable after promotion even if the workflow has already completed.

### Deployment variables

    PRODUCTION_OS_VALIDATION_ATTESTATION_KEYS
    PRODUCTION_OS_RELEASE_PROVENANCE_SECRET

The example Docker, PostgreSQL and TLS compose configurations pass both variables into the Production-OS service.

### P15 progress

- [x] canonical validation attestation schema
- [x] HMAC-SHA256 validator signatures
- [x] trusted validator identity map
- [x] exact workflow binding
- [x] exact artifact binding
- [x] artifact SHA-256 binding
- [x] source revision binding
- [x] workflow generation binding
- [x] validation payload binding
- [x] issued-at freshness enforcement
- [x] future timestamp skew rejection
- [x] untrusted validator rejection
- [x] invalid signature rejection
- [x] mandatory signed attestation for promotion
- [x] authenticated operator approval binding
- [x] deterministic approval key
- [x] signed immutable release provenance
- [x] atomic provenance persistence
- [x] full post-release verification
- [x] CLI validation-attest command
- [x] CLI release-verify command
- [x] control-plane release verification endpoint
- [x] Docker/PostgreSQL/TLS secret wiring
- [x] tamper-detection tests
- [x] expired-attestation tests
- [x] API approval identity test
- [ ] asymmetric signing / offline public-key verification
- [ ] key rotation metadata and key IDs
- [x] internal append-only transparency hash-chain anchoring
- [x] signed external transparency checkpoints
- [x] generic HTTP witness publication
- [ ] provider-specific transparency service integration

## P16 asymmetric signing and offline verification

P16 introduces Ed25519 public-key signatures alongside the P15 HMAC compatibility path.

The security boundary changes from:

    shared secret -> sign + verify

to:

    private key -> sign
    public key  -> verify

This allows validators and external auditors to verify evidence without receiving a signing secret.

### Generate a signing key pair

    production-os signing-keygen \
      --private-key validator-private.pem \
      --public-key validator-public.pem

Private keys must remain restricted to the signer. Public keys may be distributed to control planes and auditors.

### Ed25519 validation attestation

    production-os validation-attest-v2 \
      --database artifacts/production.db \
      --workflow-id <workflow-id> \
      --artifact-id <artifact-id> \
      --validation validation-summary.json \
      --validator-id validator-1 \
      --private-key validator-private.pem \
      --output validation-attestation-v2.json

The v2 signature envelope contains:

    algorithm = ed25519
    key_id = sha256:<public-key-digest>
    signature = base64(...)

The key ID makes future key rotation and historical verification deterministic.

### Offline provenance verification

A v2 provenance envelope can be verified with only its public key:

    production-os provenance-verify-v2 \
      --provenance release-provenance-v2.json \
      --public-key release-public.pem

No database, control-plane access, validator private key, or shared HMAC secret is required for cryptographic signature verification.

### P16 progress

- [x] Ed25519 signing primitives
- [x] PEM PKCS8 private keys
- [x] PEM SubjectPublicKeyInfo public keys
- [x] deterministic SHA-256 key IDs
- [x] canonical JSON signing
- [x] v2 validation attestation schema
- [x] validator public-key verification
- [x] v2 release provenance schema
- [x] offline public-key provenance verification
- [x] key-pair generation CLI
- [x] Ed25519 validation-attest CLI
- [x] offline provenance verification CLI
- [x] tamper-detection tests
- [x] artifact/source/generation approval binding retained
- [x] integrate v2 signatures into ReleaseLedger promotion path
- [x] trusted public-key registry in control plane
- [x] strict dual-sign migration from P15 HMAC to P16 Ed25519
- [x] key validity windows and revocation metadata
- [x] SLSA/in-toto compatible statement envelope
- [ ] external transparency-log anchoring

### Integrated v2 promotion

The ReleaseLedger now selects the verification path from the attestation schema.

For `production-os/validation-attestation/v2`:

    validator private key
        ↓
    Ed25519 validation attestation
        ↓
    trusted validator public-key registry
        ↓
    ReleaseLedger freshness + binding checks
        ↓
    operator approval binding
        ↓
    Ed25519 release provenance
        ↓
    immutable release record

Control-plane trust configuration:

    PRODUCTION_OS_VALIDATION_PUBLIC_KEYS
    PRODUCTION_OS_RELEASE_PROVENANCE_PRIVATE_KEY
    PRODUCTION_OS_RELEASE_PROVENANCE_PUBLIC_KEY

`PRODUCTION_OS_VALIDATION_PUBLIC_KEYS` is a JSON object mapping validator IDs to PEM public keys.

The legacy P15 HMAC path remains accepted for migration compatibility. A v2 attestation never falls back to HMAC if its public-key verification fails.

`GET /v1/releases/<release-id>/verify` automatically verifies the correct chain and reports:

    signature_scheme = ed25519

or:

    signature_scheme = hmac-sha256

This allows controlled migration without making existing P15 releases unverifiable.

### Key rotation and revocation

The Ed25519 validator trust registry supports multiple simultaneous keys per validator.

Example:

    {
      "validator-1": [
        {
          "public_key": "<old PEM>",
          "not_after": "2026-10-01T00:00:00+00:00"
        },
        {
          "public_key": "<new PEM>",
          "not_before": "2026-09-15T00:00:00+00:00"
        }
      ]
    }

Each key is addressed by the SHA-256 key ID already embedded in the Ed25519 signature envelope.

Optional policy fields:

    key_id
    not_before
    not_after
    revoked_at

If key_id is supplied in configuration, it must exactly match the public key fingerprint.

Verification resolves the exact signing key from:

    validator_id + signature.key_id

and evaluates the key policy at the attestation's signed issued_at timestamp.

This permits overlap during planned rotation while preventing an expired or revoked key from signing new accepted validation evidence.

Legacy shorthand remains valid:

    {
      "validator-1": "<PEM public key>"
    }

The registry therefore supports staged migration without invalidating existing configuration.

### SLSA / in-toto provenance

Every Ed25519-promoted release now carries a signed supply-chain statement using:

    _type = https://in-toto.io/Statement/v1
    predicateType = https://slsa.dev/provenance/v1

The statement subject binds the released artifact name and SHA-256 digest.

The build definition records:

    repository
    workflow_id
    workflow_generation
    source revision as a resolved dependency

Run details bind the Production-OS builder and the immutable release provenance through byproducts containing:

    release_id
    provenance schema
    provenance signing key ID
    approval key
    validator ID

The statement is independently signed with the release Ed25519 private key and its canonical SHA-256 digest is stored beside the release.

Release verification checks both:

    Production-OS release provenance signature
    SLSA/in-toto statement signature + artifact digest

Offline verification:

    production-os slsa-verify \
      --statement signed-slsa.json \
      --public-key release-public.pem \
      --artifact-sha256 <64-char-sha256>

This does not require access to the Production-OS database or control plane.

### Append-only transparency log

Every promoted release is now atomically appended to the Production-OS transparency log in the same database transaction as release creation.

Each entry contains:

    sequence
    release_id
    release_provenance_sha256
    slsa_statement_sha256
    previous_hash
    created_at
    entry_hash

The first entry is linked to a 64-zero genesis hash. Every later entry commits to the previous entry hash.

This provides deletion, insertion, reordering and mutation detection for the local release history.

Release verification now checks:

    cryptographic validation attestation
    release provenance
    SLSA statement
    transparency-chain integrity
    release inclusion
    release provenance digest

The verification result includes:

    transparency_sequence
    transparency_entry_hash
    transparency_root_hash

Audit endpoint:

    GET /v1/transparency

It returns the ordered append-only entries and current chain verification/root hash.

The internal chain is intentionally separate from the remaining external anchoring milestone. A database administrator who can rewrite the complete database could still replace the entire local history and recompute the chain. The next stage therefore publishes periodic roots to an independent external transparency service or immutable witness.

### External transparency witness

Production-OS can now export the current append-only transparency root as an independently signed checkpoint.

Create a checkpoint:

    production-os transparency-checkpoint \
      --database artifacts/production.db \
      --private-key witness-private.pem \
      --output checkpoint.json

The signed checkpoint commits to:

    schema version
    transparency root hash
    number of entries
    checkpoint timestamp

It is signed with Ed25519 and can be archived outside the Production-OS database.

Offline verification:

    production-os transparency-checkpoint-verify \
      --checkpoint checkpoint.json \
      --public-key witness-public.pem \
      --root-hash <expected-root>

A checkpoint may also be published to an independent HTTP witness:

    production-os transparency-checkpoint \
      --database artifacts/production.db \
      --private-key witness-private.pem \
      --publish-url https://witness.example/checkpoints \
      --bearer-token-env WITNESS_TOKEN

The HTTP body is the complete signed checkpoint envelope.

This closes the local-only trust gap when the receiving witness stores checkpoints independently. A later full database rewrite can then be detected by comparing its recomputed root against a previously published checkpoint.

The generic witness protocol deliberately avoids coupling Production-OS to one provider. Provider-specific Rekor or equivalent transparency integrations remain a separate milestone.

### Dual-sign migration

Production-OS now supports a strict migration bundle containing both legacy HMAC-SHA256 and Ed25519 validation attestations for the same validation decision.

Schema:

    production-os/validation-attestation-bundle/v1

A dual-sign bundle is accepted only when both signatures independently verify against their configured trust stores.

The two attestations must bind the same:

    validator identity
    workflow
    artifact
    artifact SHA-256
    source revision
    workflow generation
    validation result

The ReleaseLedger uses the verified Ed25519 attestation as the canonical input for v2 release provenance and SLSA generation, while retaining the complete dual-sign bundle in immutable release metadata.

Post-release verification repeats both validation checks and reports:

    signature_scheme = hmac-sha256+ed25519

This provides an explicit migration period where existing P15 HMAC validators and P16 public-key infrastructure must agree before a release can be promoted.

Once all validators and auditors have migrated, deployments can stop producing dual-sign bundles and use pure v2 Ed25519 attestations without changing the release provenance format.

### Cryptographic migration policy

Deployments can now explicitly control which validation signature generation is accepted:

    PRODUCTION_OS_VALIDATION_SIGNATURE_POLICY=compatible
    PRODUCTION_OS_VALIDATION_SIGNATURE_POLICY=dual-required
    PRODUCTION_OS_VALIDATION_SIGNATURE_POLICY=ed25519-only

Modes:

    compatible
        Accept legacy HMAC, strict dual-sign, and pure Ed25519.

    dual-required
        Reject legacy HMAC and pure Ed25519.
        Both HMAC and Ed25519 must independently verify.

    ed25519-only
        Reject HMAC and dual-sign bundles.
        Only validation-attestation/v2 is accepted.

Recommended staged migration:

    Stage 1  compatible
    Stage 2  dual-required
    Stage 3  ed25519-only

This turns HMAC retirement into an enforceable deployment policy rather than an operational convention. Historical releases remain verifiable with the cryptographic material required by their original signature scheme.

### Trusted builder identities

SLSA verification can now enforce builder identity independently from the artifact and release signature.

A builder trust policy binds:

    builder ID
    signing key owner
    signing key ID
    repository allowlist
    builder validity window
    signing-key validity / revocation policy

Example policy:

    builders = {
      "https://builder.example/prod": {
        "key_owner": "prod-builder",
        "allowed_repositories": ["owner/repo"]
      }
    }

    signing_keys = {
      "prod-builder": {
        "public_key": "<PEM>",
        "not_before": "2026-09-01T00:00:00+00:00",
        "not_after": "2027-09-01T00:00:00+00:00"
      }
    }

Trusted SLSA verification resolves the public key from the builder identity and signature key ID, then checks repository authorization before accepting the statement.

This prevents a cryptographically valid builder key from being reused to attest an unauthorized repository.

Signed SLSA envelopes now also carry the statement signing timestamp, allowing builder/key validity policy to be evaluated at signing time.

### Production builder enforcement

Trusted builder identity can now be made mandatory in the ReleaseLedger and control plane.

Configuration:

    PRODUCTION_OS_BUILDER_ID=https://builder.example/prod
    PRODUCTION_OS_TRUSTED_BUILDERS=<JSON>
    PRODUCTION_OS_TRUSTED_BUILDER_KEYS=<JSON>
    PRODUCTION_OS_REQUIRE_TRUSTED_BUILDER=true

When enforcement is enabled, release verification fails unless the SLSA statement:

    has a trusted builder ID
    is signed by a key assigned to that builder
    uses a currently valid/non-revoked key
    targets a repository authorized for that builder
    retains a valid artifact SHA-256 binding

The builder ID used during SLSA statement creation is configurable rather than hard-coded.

Recommended production configuration combines:

    PRODUCTION_OS_VALIDATION_SIGNATURE_POLICY=ed25519-only
    PRODUCTION_OS_REQUIRE_TRUSTED_BUILDER=true

This makes public-key validator identity and repository-scoped builder identity mandatory for newly verified production releases.

### Builder / provenance key separation

Production deployments can now use distinct Ed25519 keys for two separate trust domains:

    PRODUCTION_OS_RELEASE_PROVENANCE_PRIVATE_KEY
        signs the immutable Production-OS release provenance

    PRODUCTION_OS_BUILDER_PRIVATE_KEY
        signs the SLSA/in-toto builder statement

When trusted builder enforcement is enabled, a dedicated builder private key is mandatory. Production-OS no longer falls back to the release provenance key for SLSA signing in that mode.

Recommended production topology:

    validator key
        validation identity only

    builder key
        SLSA build identity only

    release provenance key
        ReleaseLedger provenance only

    witness key
        external transparency checkpoint only

This reduces cross-domain key reuse and limits the blast radius of a compromised signing credential.

Legacy/non-strict deployments retain the previous provenance-key fallback for compatibility.

### Key-purpose invariant

Strict trusted-builder deployments now enforce key-purpose separation by fingerprint.

Production-OS computes the Ed25519 key ID for configured validator, builder and release-provenance credentials and rejects startup/configuration when the same key appears in multiple trust domains.

Rejected examples:

    validator key == builder key
    builder key == release provenance key
    validator key == release provenance key

The comparison uses the public-key SHA-256 fingerprint, so re-encoding the same underlying private/public key does not bypass the invariant.

This converts key separation from a deployment recommendation into an enforced cryptographic property whenever trusted builder enforcement is enabled.

### Unified trust policy

Cryptographic domain separation is now centralized in TrustPolicy.

The policy covers four independent signing authorities:

    validator
    builder
    release provenance
    transparency witness

With strict key domains enabled, the same Ed25519 fingerprint cannot appear in more than one authority.

    PRODUCTION_OS_STRICT_KEY_DOMAINS=true

Witness checkpoint creation validates this policy before signing, preventing a witness credential from reusing a configured builder, validator or release-provenance key.

ReleaseLedger uses the same centralized policy for validator/builder/provenance separation.

This removes duplicated domain-separation logic and establishes one reusable trust-policy boundary for future KMS/HSM and external transparency integrations.

### Pluggable signing boundary

Production-OS now has a Signer interface for operations that require private-key signatures.

Current backend:

    PemSigner
        local Ed25519 PEM compatibility backend

Signer exposes only:

    key_id
    sign(payload)

SLSA builder statements and transparency witness checkpoints can now be signed through this interface instead of requiring direct access to PEM key material.

Strict trusted-builder ReleaseLedger operation uses the Signer boundary for builder signing. Existing PEM configuration is automatically wrapped in PemSigner, preserving deployment compatibility.

This creates the integration boundary required for future:

    cloud KMS
    HSM
    Vault Transit
    PKCS#11
    remote signing services

Those backends can implement Signer without exposing private key bytes to ReleaseLedger or SLSA code.

The local PEM backend remains appropriate for development and migration, while production can progressively move signing authority outside the Production-OS process.

### Signer-backed release provenance

Release provenance v2 signing now supports the same Signer boundary as SLSA builder and witness signing.

The strict cryptographic path is therefore:

    builder statement -> Signer
    release provenance -> Signer
    transparency checkpoint -> Signer

ReleaseLedger accepts a provenance_signer and no longer requires direct private-key access for v2 provenance creation when a signer is supplied.

TrustPolicy can evaluate signer key IDs directly, so domain separation remains enforceable even when the underlying private key is held by a remote KMS/HSM implementation and no PEM material exists in the Production-OS process.

PEM configuration remains supported through automatic PemSigner wrapping.

This completes the core abstraction needed to move builder and release-provenance private keys out of process. Witness already exposes the same signing boundary; the remaining deployment work is adding concrete remote signer providers and configuration/factory support.

### Remote signer factory

Production-OS now includes a fail-closed Signer factory.

Supported signer URIs:

    pem:
        local compatibility backend

    remote+https://host/path
        generic remote Ed25519 signing service

Remote signing requests contain only:

    key_id
    canonical payload object

The configured private key never needs to enter the Production-OS process.

Remote signer responses must contain:

    algorithm = ed25519
    matching key_id
    signature

Algorithm mismatch, key-ID mismatch, malformed JSON, network errors and timeouts fail closed.

Builder configuration:

    PRODUCTION_OS_BUILDER_SIGNER_URI=remote+https://signer.example/sign
    PRODUCTION_OS_BUILDER_SIGNER_KEY_ID=sha256:<fingerprint>
    PRODUCTION_OS_BUILDER_SIGNER_TOKEN=<secret>

The existing PRODUCTION_OS_BUILDER_PRIVATE_KEY remains available for the local PemSigner migration path.

The generic remote backend is intentionally provider-neutral. Future KMS, Vault Transit and PKCS#11 adapters can be registered behind the same factory without changing ReleaseLedger.

### Out-of-process signing for all release authorities

The SignerFactory path now covers builder, release-provenance and transparency-witness signing.

Builder:

    PRODUCTION_OS_BUILDER_SIGNER_URI=remote+https://signer.example/builder
    PRODUCTION_OS_BUILDER_SIGNER_KEY_ID=sha256:<builder>
    PRODUCTION_OS_BUILDER_SIGNER_TOKEN=<secret>

Release provenance:

    PRODUCTION_OS_PROVENANCE_SIGNER_URI=remote+https://signer.example/provenance
    PRODUCTION_OS_PROVENANCE_SIGNER_KEY_ID=sha256:<provenance>
    PRODUCTION_OS_PROVENANCE_SIGNER_TOKEN=<secret>

Witness CLI:

    production-os transparency-checkpoint \
      --database artifacts/production.db \
      --witness-signer-uri remote+https://signer.example/witness \
      --witness-signer-key-id sha256:<witness> \
      --witness-signer-token-env WITNESS_SIGNER_TOKEN

A local --private-key remains supported for witness migration and is wrapped as a PemSigner.

With remote signers configured, the Production-OS control plane no longer needs the builder or release-provenance private key material. Witness checkpoint signing can likewise be performed without loading its private key.

TrustPolicy continues to enforce domain separation from Signer.key_id values.

### Remote signer transport hardening

RemoteHttpSigner now defaults to HTTPS-only operation and fails configuration when a plain HTTP endpoint is supplied.

Transport controls include:

    system or custom CA validation
    optional client certificate + private key for mTLS
    bounded request timeout
    bounded retries
    exponential retry backoff
    circuit breaker after repeated failed signing operations
    automatic circuit reset window

Default retry policy:

    retries = 2
    backoff = 0.25 seconds
    circuit failure threshold = 3
    circuit reset = 30 seconds

All terminal failures remain fail-closed: Production-OS does not create a substitute signature or silently fall back to a local signing key.

Plain HTTP can only be enabled explicitly through the Python signer configuration and is intended for isolated development environments.

Remote response validation still requires Ed25519, the exact configured key ID, and a non-empty signature.

### Vault Transit signer

Production-OS now has a native HashiCorp Vault Transit signing backend behind the existing Signer interface.

Signer URI:

    vault+https://vault.example/keys/<transit-key>

Required configuration:

    key_id
    Vault token

Optional controls:

    Vault namespace
    custom Transit mount
    custom CA
    mTLS client certificate/key
    request timeout

The signer canonicalizes the Production-OS payload, base64-encodes it, and asks Vault Transit to sign with Ed25519. Production-OS never receives the Transit private key.

The returned Vault signature is validated structurally and normalized to the common Signer response while preserving the original provider signature for audit metadata.

Example factory configuration:

    create_signer(
        "vault+https://vault.example/keys/production-builder",
        key_id="sha256:<public-key-fingerprint>",
        vault_token="<token>",
    )

The same backend can be supplied as builder_signer, provenance_signer or witness_signer, while TrustPolicy continues to enforce distinct key IDs between those domains.

### Dynamic Vault authentication

Vault-backed signers no longer require a long-lived static Vault token.

SignerFactory supports three Vault authentication modes:

    token
        existing compatibility mode

    approle
        exchanges role_id + secret_id for a Vault client token

    kubernetes
        exchanges a Kubernetes service-account JWT + Vault role
        for a Vault client token

Both dynamic flows use Vault's HTTPS auth endpoints and fail closed when credentials are missing, the auth method is unknown, Vault is unavailable, or no client token is returned.

Relevant factory options:

    vault_auth_method
    vault_role_id
    vault_secret_id
    vault_kubernetes_role
    vault_kubernetes_jwt
    vault_auth_mount
    vault_namespace

The resulting short-lived Vault token is passed only to VaultTransitSigner and is not exposed through the common Signer interface.

Recommended Kubernetes deployment:

    Pod service account
          ↓
    Kubernetes JWT
          ↓
    Vault Kubernetes auth
          ↓
    short-lived Vault token
          ↓
    Transit Ed25519 signing

This removes the need to provision a permanent Vault token into the Production-OS container.


## Trust incident response

Production-OS can re-evaluate promoted releases against the current validator
and builder trust policy. This is intended for key compromise, emergency
revocation, and supply-chain incident response.

Inspect the current blast radius:

```bash
production-os trust-status --database production.db --key-id sha256:...
```

Generate a machine-readable report without mutating audit history:

```bash
production-os incident-report --database production.db --key-id sha256:...
```

Persist a deduplicated snapshot in the immutable incident ledger:

```bash
production-os incident-snapshot --database production.db --key-id sha256:...
```

`incident-snapshot` exits with 0 for a healthy scope, 2 when a new active
incident state was recorded, and 3 when the active state was already recorded.

The authenticated control plane exposes the same incident surfaces:

```text
GET  /v1/trust-status
GET  /v1/incident-report
GET  /v1/incident-history
GET  /v1/incident-history/verify
POST /v1/incident-snapshot
```

Read endpoints require an authenticated viewer. The snapshot endpoint mutates
the append-only audit ledger and therefore requires the `operator` role.

Incident history entries are SHA-256 hash chained. Rewriting a persisted report
or breaking the previous-hash chain causes verification to fail. Unchanged
snapshots are deduplicated while genuine blast-radius changes append a new
entry.
````
