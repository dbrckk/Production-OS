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
  test_dashboard_alerts.py
  test_dashboard_api.py
  test_dashboard_backup_api.py
  test_dashboard_backups.py
  test_dashboard_control_api.py
  test_dashboard_control_audit.py
  test_dashboard_control_e2e.py
  test_dashboard_control.py
  test_dashboard_github.py
  test_dashboard_health.py
  test_dashboard_incident_signals.py
  test_dashboard_incidents.py
  test_dashboard_launch_ux.py
  test_dashboard_launch.py
  test_dashboard_maintenance.py
  test_dashboard_observability_e2e.py
  test_dashboard_playbook_api.py
  test_dashboard_playbooks.py
  test_dashboard_remediation_api.py
  test_dashboard_remediation_history.py
  test_dashboard_remediation_metrics.py
  test_dashboard_retention_prune.py
  test_dashboard_security.py
  test_dashboard_store_postgres.py
  test_dashboard_store.py
  test_dashboard_ui_v3.py
  test_dashboard_usage.py
  test_database_maintenance_lock.py
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
  test_managed_projects_http_v4.py
  test_managed_projects_v4.py
  test_observability.py
  test_p6_hardening.py
  test_policy_budgets.py
  test_policy_validation.py
  test_portfolio_claim_api.py
  test_portfolio_optimizer.py
  test_postgres_backend.py
  test_preemption.py
  test_production_stack_e2e.py
  test_project_progress.py
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
  test_release16_operations_e2e.py
  test_release18_managed_projects_e2e.py
  test_release19_restore_staging_e2e.py
  test_release21_offline_restore_e2e.py
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
github_token = str(os.getenv("GITHUB_TOKEN") or "").strip()
actions_repository = str(
actions_workflow = str(
actions_ref = str(
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
rows = db.execute(
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
worker = control.workers.register(
⋮----
principal = self._require("worker")
⋮----
worker = control.workers.heartbeat(
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
worker_id = str(body["worker_id"])
capabilities = [
⋮----
desired = control.dashboard_control.worker_state(worker_id)
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

## File: src/production_os/dashboard_alerts.py
````python
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
````

## File: src/production_os/dashboard_backups.py
````python
BACKUP_ID_RE = re.compile(r"^\d{8}T\d{6}Z-[0-9a-f]{12}$")
⋮----
class BackupError(RuntimeError)
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
manifest_path = directory / f"{backup_id}.json"
backup_path = directory / f"{backup_id}.sqlite"
manifest = _safe_manifest(manifest_path)
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
````

## File: src/production_os/dashboard_control.py
````python
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
````

## File: src/production_os/dashboard_github.py
````python
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
````

## File: src/production_os/dashboard_health.py
````python
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
````

## File: src/production_os/dashboard_incidents.py
````python
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
worker_id = str(worker.get("worker_id") or "")
⋮----
age = worker.get("age_seconds")
⋮----
job_key = str(execution.get("job_key") or "")
⋮----
age = execution.get("age_seconds")
⋮----
def dedupe_key(signal: dict) -> str
````

## File: src/production_os/dashboard_maintenance.py
````python
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
````

## File: src/production_os/dashboard_playbooks.py
````python
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
````

## File: src/production_os/dashboard_remediation_metrics.py
````python
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
````

## File: src/production_os/dashboard_security.py
````python
_SENSITIVE_KEYS = {
⋮----
_PATTERNS = (
⋮----
def _scrub_secret_patterns(value: str) -> str
⋮----
value = pattern.sub(r"\1[REDACTED]", value)
⋮----
def redact_log_value(value: object) -> object
````

## File: src/production_os/dashboard_service.py
````python
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
````

## File: src/production_os/dashboard_store.py
````python
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
````

## File: src/production_os/dashboard_ui.py
````python
DASHBOARD_HTML = """<!doctype html>
````

## File: src/production_os/dashboard_usage.py
````python
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
````

## File: src/production_os/database_maintenance_lock.py
````python
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

## File: src/production_os/managed_projects.py
````python
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
project_id = uuid4().hex
now = _now()
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
existing = _execute(
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

## File: src/production_os/project_progress.py
````python
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
def wait_for_workflow_run(self, repository, workflow, *, display_title, timeout_seconds, poll_seconds)
⋮----
def workflow_run_artifacts(self, repository, run_id)
⋮----
def download_workflow_artifact(self, repository, artifact_id)
⋮----
def put_file(self, repository, path, content, *, message, branch)
⋮----
def read_json_file(self, repository, path)
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
⋮----
def test_batch_receipt_surfaces_visual_similarity_quality_summary(tmp_path)
⋮----
artifact = output / "character.png"
⋮----
def test_execute_asset_forge_batch_remote_fallback_downloads_and_delivers(tmp_path)
⋮----
artifact_bytes = b"remote-png"
digest = hashlib.sha256(artifact_bytes).hexdigest()
result = {
archive = io.BytesIO()
⋮----
receipt = execute_asset_forge_batch(
⋮----
dispatch = next(call for call in fake.calls if "inputs" in call)
⋮----
def test_execute_asset_forge_batch_rejects_duplicate_target_paths(tmp_path)
⋮----
request_a = build_asset_forge_request(
request_b = build_asset_forge_request(
⋮----
def test_asset_batch_reuses_identical_worktree_asset_from_version_sidecar(tmp_path)
⋮----
calls = []
⋮----
artifact = output / "cache-hero.png"
⋮----
first = execute_asset_forge_batch(
request2 = build_asset_forge_request(
second = execute_asset_forge_batch(
⋮----
sidecar = json.loads(
⋮----
def test_asset_version_sidecar_increments_when_semantic_request_changes(tmp_path)
⋮----
payload = json.loads(request_path.read_text())
⋮----
artifact = output / "hero.png"
⋮----
def make(instruction, rid)
⋮----
def test_dedup_summary_reports_exact_and_near_duplicates_without_mutation()
⋮----
base_art = {
near_art = {
produced = [
result = _dedup_summary(produced)
⋮----
def test_dedup_summary_ignores_parent_child_visual_similarity()
⋮----
art = {
result = _dedup_summary([
⋮----
def test_batch_receipt_preserves_asset_library_version_metadata(tmp_path)
⋮----
library = result["items"][0]["library"]
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
⋮----
def test_asset_forge_batch_parser_accepts_result_file()
⋮----
def test_asset_forge_batch_writes_visual_quality_failure_receipt()
⋮----
root = Path(td)
spec = root / "batch.json"
receipt = root / "receipt.json"
⋮----
rc = run_asset_forge_batch(args)
⋮----
payload = json.loads(receipt.read_text())
⋮----
def test_asset_forge_batch_writes_success_receipt()
⋮----
expected = {
⋮----
def test_restore_activate_parser_requires_explicit_activation_fields()
⋮----
backup_dir = tmp_path / "backups"
⋮----
database = tmp_path / "production.sqlite"
backend = SQLiteBackend(database)
backup = create_verified_sqlite_backup(backend)
staged = stage_verified_sqlite_restore(backend, backup["backup_id"])
⋮----
lock = SQLiteDatabaseProcessLock(str(database))
⋮----
rc = run_restore_activate(args)
⋮----
payload = json.loads(capsys.readouterr().err)
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

## File: tests/test_dashboard_alerts.py
````python
def test_offline_worker_with_queued_work_is_high_alert()
⋮----
alerts = derive_alerts({
⋮----
def test_three_consecutive_failures_are_high_alert()
⋮----
def test_cost_spike_requires_real_baseline()
⋮----
no_baseline = derive_alerts({
⋮----
spike = next(item for item in alerts if item["code"] == "cost_spike")
⋮----
def test_stale_busy_worker_is_medium_alert()
⋮----
stale = next(item for item in alerts if item["code"] == "stale_busy_worker")
⋮----
def test_previous_window_cost_uses_observed_historical_cost_only()
⋮----
now = datetime.now(timezone.utc)
rows = [
````

## File: tests/test_dashboard_api.py
````python
def _auth()
⋮----
@pytest.fixture()
def running_control_plane(tmp_path)
⋮----
control = ControlPlane(str(tmp_path / "db.sqlite"), authorizer=_auth())
server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(control))
thread = threading.Thread(target=server.serve_forever, daemon=True)
⋮----
def get_api(base, path, token)
⋮----
req = Request(base + path, method="GET", headers=(
⋮----
def api(base, path, token, body)
⋮----
data = json.dumps(body).encode()
req = Request(base + path, data=data, method="POST", headers={
⋮----
def _owned_execution(control)
⋮----
job = control.queue.enqueue({"idempotency_key":"job-telemetry", "handoff":{"repository":"dbrckk/example","task":"ship"}, "workflow_id":"wf"})
claimed = control.queue.claim_next("worker-a", capabilities=["python"])
acked = control.queue.ack(claimed["key"], "worker-a")
⋮----
def test_worker_can_publish_owned_job_telemetry(running_control_plane)
⋮----
job = _owned_execution(control)
⋮----
def test_other_worker_and_viewer_cannot_publish_telemetry(running_control_plane)
⋮----
def test_heartbeat_persists_only_authenticated_quota_values(running_control_plane)
⋮----
quota = control.dashboard_store.latest_provider_quota_snapshots()[0]
⋮----
def test_dashboard_overview_requires_viewer_and_has_stable_envelope(running_control_plane)
⋮----
def test_dashboard_rejects_invalid_window(running_control_plane)
⋮----
def test_dashboard_worker_routes_and_unknown_worker(running_control_plane)
⋮----
def test_dashboard_project_and_activity_routes(running_control_plane)
⋮----
low = control.queue.enqueue({
high = control.queue.enqueue({
⋮----
paused_job = control.queue.enqueue({
missing_job = control.queue.enqueue({
⋮----
rows = {row["job_key"]:row for row in payload["jobs"]}
⋮----
job = control.queue.enqueue({
⋮----
row = next(item for item in payload["jobs"] if item["job_key"] == job["key"])
⋮----
stale = control.queue.enqueue({
healthy = control.queue.enqueue({
⋮----
summary = payload["summary"]
⋮----
def test_dashboard_health_requires_viewer_and_has_stable_shape(running_control_plane)
⋮----
def test_worker_detail_includes_recoverable_jobs(running_control_plane)
````

## File: tests/test_dashboard_backup_api.py
````python
def _auth()
⋮----
def _request(base, path, token, *, method="GET", body=None)
⋮----
data = None if body is None else json.dumps(body).encode("utf-8")
request = urllib.request.Request(
⋮----
def _server(control)
⋮----
server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(control))
thread = threading.Thread(target=server.serve_forever, daemon=True)
⋮----
def test_backup_catalog_is_viewer_readable_and_worker_forbidden(tmp_path, monkeypatch)
⋮----
backup_dir = tmp_path / "backups"
⋮----
control = ControlPlane(str(tmp_path / "control.sqlite"), authorizer=_auth())
⋮----
def test_backup_creation_requires_operator_and_exact_confirmation(tmp_path, monkeypatch)
⋮----
audit = control.dashboard_store.control_audit_events(limit=10)
⋮----
def test_unconfigured_backup_returns_conflict_and_failed_audit(tmp_path, monkeypatch)
⋮----
created = control.dashboard.create_verified_backup()
backup_id = created["backup_id"]
⋮----
path = f"/v1/dashboard/backups/{backup_id}/verify"
⋮----
verify = next(row for row in audit if row["action"] == "backup-verify")
⋮----
backup_file = backup_dir / f"{backup_id}.sqlite"
⋮----
path = f"/v1/dashboard/backups/{backup_id}/stage-restore"
⋮----
before = sorted(p.name for p in backup_dir.iterdir())
⋮----
audit = control.dashboard_store.control_audit_events(limit=20)
event = next(
⋮----
source = backup_dir / f"{backup_id}.sqlite"
⋮----
receipt = {
⋮----
def test_backup_http_surface_has_no_restore_activation_route(tmp_path, monkeypatch)
````

## File: tests/test_dashboard_backups.py
````python
def test_sqlite_backup_contains_committed_durable_data(tmp_path, monkeypatch)
⋮----
db_path = tmp_path / "production.sqlite"
backup_dir = tmp_path / "backups"
⋮----
backend = SQLiteBackend(db_path)
⋮----
manifest = create_verified_sqlite_backup(backend)
backup_file = backup_dir / f"{manifest['backup_id']}.sqlite"
⋮----
value = db.execute(
integrity = db.execute("PRAGMA integrity_check").fetchone()[0]
⋮----
def test_backup_hash_and_size_match_file_bytes(tmp_path, monkeypatch)
⋮----
backend = SQLiteBackend(tmp_path / "production.sqlite")
⋮----
payload = (backup_dir / f"{manifest['backup_id']}.sqlite").read_bytes()
⋮----
def test_manifest_contains_only_safe_metadata(tmp_path, monkeypatch)
⋮----
backend = SQLiteBackend(tmp_path / "secret-source.sqlite")
⋮----
on_disk = json.loads(
⋮----
encoded = json.dumps(on_disk).lower()
⋮----
def test_missing_backup_directory_configuration_writes_nothing(tmp_path, monkeypatch)
⋮----
readiness = backup_readiness(backend)
⋮----
class _FakePostgres
⋮----
def test_postgres_readiness_is_truthfully_unsupported(tmp_path, monkeypatch)
⋮----
readiness = backup_readiness(_FakePostgres())
⋮----
def test_backup_readiness_does_not_create_configured_directory(tmp_path, monkeypatch)
⋮----
def test_valid_backup_reports_restore_readiness_and_schema(tmp_path, monkeypatch)
⋮----
result = verify_backup_for_restore(backend, manifest["backup_id"])
⋮----
def test_tampered_backup_file_is_rejected(tmp_path, monkeypatch)
⋮----
path = backup_dir / f"{manifest['backup_id']}.sqlite"
⋮----
def test_tampered_manifest_is_rejected(tmp_path, monkeypatch)
⋮----
manifest_path = backup_dir / f"{manifest['backup_id']}.json"
payload = json.loads(manifest_path.read_text())
⋮----
def test_restore_verification_rejects_missing_backup_file(tmp_path, monkeypatch)
⋮----
def test_restore_verification_never_changes_live_database(tmp_path, monkeypatch)
⋮----
def test_stage_verified_restore_creates_isolated_candidate(tmp_path, monkeypatch)
⋮----
live_before = db_path.read_bytes()
⋮----
staged = stage_verified_sqlite_restore(backend, manifest["backup_id"])
⋮----
candidate = backup_dir / f"restore-{staged['candidate_id']}.sqlite"
⋮----
live_value = db.execute(
⋮----
def test_stage_restore_rejects_tampered_source_without_candidate(tmp_path, monkeypatch)
⋮----
source = backup_dir / f"{manifest['backup_id']}.sqlite"
⋮----
def test_stage_restore_manifest_contains_only_safe_metadata(tmp_path, monkeypatch)
⋮----
backup = create_verified_sqlite_backup(backend)
staged = stage_verified_sqlite_restore(backend, backup["backup_id"])
⋮----
result = activate_staged_sqlite_restore(
⋮----
rollback_path = backup_dir / f"{result['rollback_backup_id']}.sqlite"
⋮----
rollback_value = db.execute(
⋮----
def test_restore_activation_wrong_confirmation_changes_nothing(tmp_path, monkeypatch)
⋮----
before = db_path.read_bytes()
⋮----
def test_restore_activation_rejects_tampered_candidate(tmp_path, monkeypatch)
⋮----
def test_restore_activation_rejects_schema_mismatch(tmp_path, monkeypatch)
⋮----
payload = candidate.read_bytes()
manifest_path = backup_dir / f"restore-{staged['candidate_id']}.json"
manifest = json.loads(manifest_path.read_text())
⋮----
real_connect = backups_module.sqlite3.connect
live_verification_failed = {"done": False}
⋮----
def failing_connect(target, *args, **kwargs)
⋮----
def test_successful_restore_candidate_cannot_be_replayed(tmp_path, monkeypatch)
⋮----
receipt = json.loads(
⋮----
encoded = json.dumps(receipt).lower()
⋮----
manifest = json.loads(
⋮----
failed = {"done":False}
⋮----
verified = verify_staged_restore_candidate(
⋮----
older = {
newer = {
⋮----
rows = restore_activation_history(backend)
````

## File: tests/test_dashboard_control_api.py
````python
def _post(base, path, token, payload)
⋮----
request = urllib.request.Request(
⋮----
raw = response.read()
⋮----
raw = exc.read()
⋮----
def _fixture(tmp_path)
⋮----
auth = TokenAuthorizer([
control = ControlPlane(str(tmp_path / "db.sqlite"), authorizer=auth)
⋮----
server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(control))
thread = threading.Thread(target=server.serve_forever, daemon=True)
⋮----
def test_worker_control_requires_operator(tmp_path)
⋮----
def test_pause_returns_requested_state_not_fake_remote_ack(tmp_path)
⋮----
def test_resume_and_drain_map_to_durable_states(tmp_path)
⋮----
def test_invalid_worker_control_action_is_rejected(tmp_path)
⋮----
def test_cancel_current_requires_explicit_job_key(tmp_path)
⋮----
def test_cancel_current_targets_only_named_active_job(tmp_path)
⋮----
job = control.queue.enqueue({
claimed = control.queue.claim_key(job["key"], "worker-a")
⋮----
sibling = control.queue.enqueue({
⋮----
def test_worker_heartbeat_acknowledges_and_cancels_target_job(tmp_path)
⋮----
state = control.dashboard_control.job_state(job["key"])
⋮----
def test_late_complete_after_cancel_is_rejected_and_job_stays_cancelled(tmp_path)
⋮----
def test_cancel_request_after_complete_is_rejected(tmp_path)
⋮----
def test_cancel_current_converges_workflow_task_without_auto_retry(tmp_path)
⋮----
workflow = control.workflows.create(
dispatched = control.workflows.dispatch_ready(workflow["id"])
⋮----
job = dispatched[0]
⋮----
current = control.workflows.get(workflow["id"])
task = next(item for item in current["tasks"] if item["task_id"] == "task-a")
⋮----
def test_retry_cancelled_workflow_task_creates_new_attempt_once(tmp_path)
⋮----
first = control.workflows.dispatch_ready(workflow["id"])[0]
⋮----
first_execution = control.dashboard_store.latest_execution(first["key"])
⋮----
second = retried["job"]
⋮----
task = control.workflows.get(workflow["id"])["tasks"][0]
⋮----
def test_retry_refuses_exhausted_attempt_budget(tmp_path)
⋮----
def test_retry_rejects_superseded_workflow_generation_without_new_job(tmp_path)
⋮----
before = {
⋮----
after = {
⋮----
def test_retry_allows_current_pr_workflow_generation(tmp_path)
⋮----
head_sha = "b" * 40
⋮----
def test_retry_dispatches_only_targeted_task(tmp_path)
⋮----
first = control.workflows.dispatch_ready(workflow["id"], limit=1)[0]
⋮----
before = control.workflows.get(workflow["id"])
task_b = next(x for x in before["tasks"] if x["task_id"] == "task-b")
⋮----
after = control.workflows.get(workflow["id"])
task_b = next(x for x in after["tasks"] if x["task_id"] == "task-b")
⋮----
queued = control.queue.peek_candidates(limit=100)
⋮----
def test_recover_stuck_requires_expired_claim_and_is_audited(tmp_path)
⋮----
failed = control.dashboard_store.control_audit_events(limit=1)[0]
⋮----
audit = control.dashboard_store.control_audit_events(limit=1)[0]
⋮----
def test_recover_stuck_respects_max_attempts(tmp_path)
````

## File: tests/test_dashboard_control_audit.py
````python
def test_control_audit_is_durable_and_newest_first(tmp_path)
⋮----
store = DashboardStore(SQLiteBackend(tmp_path / "db.sqlite"))
first = store.append_control_audit(
second = store.append_control_audit(
rows = store.control_audit_events(limit=10)
⋮----
def test_control_audit_schema_cannot_store_credentials(tmp_path)
⋮----
row = store.append_control_audit(
forbidden = {"token", "authorization", "headers", "secret", "github_token"}
⋮----
def test_control_audit_limit_is_bounded(tmp_path)
⋮----
def _auth()
⋮----
def _request(base, path, token, *, method="GET", body=None)
⋮----
data = None if body is None else json.dumps(body).encode("utf-8")
request = urllib.request.Request(
⋮----
raw = response.read()
⋮----
raw = exc.read()
⋮----
def test_operator_control_api_writes_success_and_failure_audit(tmp_path)
⋮----
control = ControlPlane(str(tmp_path / "api.sqlite"), authorizer=_auth())
⋮----
server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(control))
thread = threading.Thread(target=server.serve_forever, daemon=True)
⋮----
base = f"http://127.0.0.1:{server.server_port}"
⋮----
events = payload["events"]
⋮----
def test_release17_schema_is_v15_and_contains_managed_project_tables(tmp_path)
⋮----
backend = SQLiteBackend(tmp_path / "schema.sqlite")
⋮----
version = db.execute(
table = db.execute(
remediation = db.execute(
remediation_columns = {
⋮----
managed = db.execute(
runs = db.execute(
⋮----
def test_control_action_remains_traced_if_audit_finalization_fails(tmp_path)
⋮----
control = ControlPlane(str(tmp_path / "audit-failure.sqlite"), authorizer=_auth())
⋮----
original = control.dashboard_store.update_control_audit
⋮----
def fail_finalize(*args, **kwargs)
⋮----
rows = control.dashboard_store.control_audit_events(limit=1)
⋮----
def test_control_audit_does_not_echo_reason_or_credentials(tmp_path)
⋮----
control = ControlPlane(str(tmp_path / "secret-audit.sqlite"), authorizer=_auth())
⋮----
secret = "Bearer super-secret-token"
⋮----
serialized = json.dumps(payload, sort_keys=True)
````

## File: tests/test_dashboard_control_e2e.py
````python
def _auth()
⋮----
def _post(base, path, token, payload)
⋮----
request = urllib.request.Request(
⋮----
raw = response.read()
⋮----
raw = exc.read()
⋮----
class _FakeGitHub
⋮----
def __init__(self)
⋮----
def dispatch_workflow(self, repository, workflow, *, ref="main", inputs=None)
⋮----
def _server(control)
⋮----
server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(control))
thread = threading.Thread(target=server.serve_forever, daemon=True)
⋮----
def test_paused_state_survives_control_plane_restart(tmp_path)
⋮----
database = str(tmp_path / "production.db")
first = ControlPlane(database, authorizer=_auth())
⋮----
second = ControlPlane(database, authorizer=_auth())
⋮----
def test_release2_control_flow_pause_drain_cancel_retry_complete(tmp_path)
⋮----
control = ControlPlane(str(tmp_path / "production.db"), authorizer=_auth())
⋮----
workflow = control.workflows.create(
first = control.workflows.dispatch_ready(workflow["id"])[0]
⋮----
second = retried["job"]
⋮----
current = control.workflows.get(workflow["id"])
task = current["tasks"][0]
⋮----
github = _FakeGitHub()
⋮----
def test_release3_audit_and_recovery_survive_control_plane_restart(tmp_path)
⋮----
database = str(tmp_path / "release3.db")
⋮----
job = first.queue.enqueue({
⋮----
persisted = second.dashboard_store.control_audit_events(limit=10)
⋮----
latest = second.dashboard_store.control_audit_events(limit=1)[0]
⋮----
def test_release4_incident_lifecycle_survives_restart(tmp_path)
⋮----
database = str(tmp_path / "release4-incidents.db")
⋮----
incident = first.dashboard.incidents()["incidents"][0]
⋮----
persisted = second.dashboard_store.dashboard_incidents(limit=10)
⋮----
reconciled = second.dashboard.incidents()["incidents"]
resolved = next(row for row in reconciled if row["id"] == incident["id"])
⋮----
third = ControlPlane(database, authorizer=_auth())
final = third.dashboard_store.dashboard_incidents(limit=10)
````

## File: tests/test_dashboard_control.py
````python
def _store(tmp_path)
⋮----
def test_missing_worker_control_row_defaults_to_active(tmp_path)
⋮----
control = DashboardControl(_store(tmp_path), None, None)
state = control.worker_state("worker-a")
⋮----
def test_pause_and_drain_are_durable(tmp_path)
⋮----
paused = control.set_worker_state(
⋮----
drained = control.set_worker_state(
⋮----
def test_invalid_worker_desired_state_is_rejected(tmp_path)
⋮----
def test_worker_acknowledgement_requires_current_desired_state(tmp_path)
⋮----
ack = control.acknowledge_worker_state("worker-a", "paused")
⋮----
def test_missing_job_control_row_defaults_to_active(tmp_path)
⋮----
state = control.job_state("job-a")
⋮----
def test_job_cancel_request_and_acknowledgement_are_durable(tmp_path)
⋮----
requested = control.request_job_cancel(
⋮----
acknowledged = control.acknowledge_job_cancel("job-a")
⋮----
class _FakeGitHub
⋮----
def __init__(self, fail=False)
⋮----
def dispatch_workflow(self, repository, workflow, *, ref="main", inputs=None)
⋮----
def test_kick_dispatches_actions_worker_when_configured(tmp_path)
⋮----
github = _FakeGitHub()
control = DashboardControl(
result = control.kick_worker("github-actions-worker")
⋮----
def test_kick_reports_scheduled_fallback_without_dispatch_credentials(tmp_path)
⋮----
def test_kick_reports_failed_when_dispatch_errors(tmp_path)
````

## File: tests/test_dashboard_github.py
````python
class FakeGitHub
⋮----
def __init__(self)
def repository(self, repository)
def default_branch_commit_count(self, repository, branch)
def open_pull_request_count(self, repository)
def latest_release(self, repository)
def latest_commit(self, repository, branch)
def latest_ci_status(self, repository, branch)
⋮----
def test_snapshotter_returns_cached_snapshot_as_degraded_on_github_failure(tmp_path)
⋮----
store = DashboardStore(SQLiteBackend(tmp_path / "production.db"))
github = FakeGitHub()
snapshotter = RepositorySnapshotter(github, store)
cached = snapshotter.refresh("dbrckk/example")
⋮----
result = snapshotter.get("dbrckk/example", max_age_seconds=0)
⋮----
def test_snapshotter_raises_typed_error_without_cache(tmp_path)
⋮----
github = FakeGitHub(); github.fail = True
⋮----
def test_snapshotter_rejects_invalid_repository(tmp_path)
⋮----
def test_snapshotter_counts_distinct_production_os_commits(tmp_path)
⋮----
snapshot = RepositorySnapshotter(FakeGitHub(), store).refresh("dbrckk/example")
````

## File: tests/test_dashboard_health.py
````python
def test_health_is_healthy_without_operational_problems()
⋮----
result = derive_control_health({
⋮----
def test_queue_without_worker_degrades_health()
⋮----
def test_stale_busy_worker_and_running_execution_are_explained()
⋮----
codes = {item["code"] for item in result["reasons"]}
````

## File: tests/test_dashboard_incident_signals.py
````python
def test_health_signals_expand_to_targeted_incidents()
⋮----
signals = signals_from_health({
⋮----
keys = {dedupe_key(item) for item in signals}
````

## File: tests/test_dashboard_incidents.py
````python
def _store(tmp_path)
⋮----
def test_incident_upsert_deduplicates_and_counts_occurrences(tmp_path)
⋮----
store = _store(tmp_path)
first = store.upsert_dashboard_incident(
second = store.upsert_dashboard_incident(
⋮----
rows = store.dashboard_incidents(limit=10)
⋮----
def test_incident_acknowledgement_is_durable(tmp_path)
⋮----
incident = store.upsert_dashboard_incident(
acknowledged = store.acknowledge_dashboard_incident(
⋮----
def test_incident_schema_has_no_freeform_secret_payload(tmp_path)
⋮----
row = store.upsert_dashboard_incident(
forbidden = {"token", "authorization", "headers", "secret", "payload", "metadata"}
⋮----
def _auth()
⋮----
def _request(base, path, token, *, method="GET", body=None)
⋮----
data = None if body is None else json.dumps(body).encode("utf-8")
request = urllib.request.Request(
⋮----
raw = response.read()
⋮----
raw = exc.read()
⋮----
def test_incident_api_acknowledges_and_resolves_when_health_clears(tmp_path)
⋮----
control = ControlPlane(str(tmp_path / "api-incidents.sqlite"), authorizer=_auth())
⋮----
server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(control))
thread = threading.Thread(target=server.serve_forever, daemon=True)
⋮----
base = f"http://127.0.0.1:{server.server_port}"
⋮----
incident = payload["incidents"][0]
⋮----
def test_incident_polling_does_not_inflate_unchanged_occurrence_count(tmp_path)
⋮----
control = ControlPlane(str(tmp_path / "polling-incidents.sqlite"), authorizer=_auth())
⋮----
first = control.dashboard.incidents()["incidents"][0]
second = control.dashboard.incidents()["incidents"][0]
⋮----
def test_resolved_incident_reopens_without_stale_acknowledgement(tmp_path)
⋮----
resolved = store.dashboard_incidents(limit=1)[0]
⋮----
reopened = store.upsert_dashboard_incident(
⋮----
def test_incident_api_rejects_invalid_status_filter(tmp_path)
⋮----
control = ControlPlane(str(tmp_path / "bad-status.sqlite"), authorizer=_auth())
⋮----
def test_resolved_incident_cannot_be_acknowledged(tmp_path)
⋮----
control = ControlPlane(str(tmp_path / "resolved-ack.sqlite"), authorizer=_auth())
⋮----
incident = control.dashboard.incidents()["incidents"][0]
⋮----
resolved = control.dashboard.incidents(status="resolved")["incidents"][0]
⋮----
current = control.dashboard_store.dashboard_incidents(limit=1)[0]
⋮----
def test_stale_incident_age_updates_do_not_create_new_occurrences(tmp_path)
````

## File: tests/test_dashboard_launch_ux.py
````python
def _auth()
⋮----
def _server(control)
⋮----
server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(control))
thread = threading.Thread(target=server.serve_forever, daemon=True)
⋮----
def _get(url, token=None, *, follow_redirects=True)
⋮----
request = urllib.request.Request(
opener = urllib.request.build_opener()
⋮----
class NoRedirect(urllib.request.HTTPRedirectHandler)
⋮----
def redirect_request(self, req, fp, code, msg, headers, newurl)
opener = urllib.request.build_opener(NoRedirect())
⋮----
raw = response.read()
content_type = response.headers.get("Content-Type", "")
⋮----
raw = exc.read()
⋮----
payload = json.loads(raw or b"{}")
⋮----
payload = raw.decode("utf-8", errors="replace")
⋮----
def test_root_redirects_to_dashboard_and_health_stays_json(tmp_path)
⋮----
control = ControlPlane(str(tmp_path / "launch-ux.sqlite"), authorizer=_auth())
⋮----
control = ControlPlane(str(tmp_path / "repos.sqlite"), authorizer=_auth())
⋮----
def fake_repos(self, owner)
⋮----
control = ControlPlane(
⋮----
def fail_repos(self, owner)
````

## File: tests/test_dashboard_launch.py
````python
def test_dashboard_daily_surface_is_repo_instruction_only()
⋮----
def test_dashboard_pairing_is_hidden_from_normal_surface()
⋮----
def test_dashboard_surfaces_visual_quality_without_extra_controls()
⋮----
def test_dashboard_visual_quality_follows_selected_repository()
⋮----
def test_dashboard_lists_per_asset_visual_quality_details()
⋮----
def test_dashboard_visual_quality_has_previews_and_history()
⋮----
def test_dashboard_lists_semantic_art_score_per_asset()
⋮----
def test_dashboard_surfaces_asset_library_version_and_preference()
⋮----
def test_dashboard_pairing_modal_is_mobile_visible_and_closable()
⋮----
def test_dashboard_worker_status_uses_authenticated_api()
⋮----
def test_dashboard_launch_opens_pairing_when_token_missing()
⋮----
def test_dashboard_pairing_validates_operator_token_before_accepting()
⋮----
def test_dashboard_v2_surfaces_runtime_health_and_recent_runs()
⋮----
def test_dashboard_v2_explains_offline_worker_and_queued_launch()
⋮----
def test_dashboard_v2_has_readable_auth_errors()
⋮----
def test_dashboard_v2_has_mobile_primary_launch_action()
````

## File: tests/test_dashboard_maintenance.py
````python
NOW = datetime(2026, 9, 24, 18, 0, tzinfo=timezone.utc)
⋮----
def _auth()
⋮----
def _get(base, path, token)
⋮----
request = urllib.request.Request(
⋮----
def test_sqlite_maintenance_counts_only_valid_old_rows(tmp_path)
⋮----
backend = SQLiteBackend(tmp_path / "maintenance.sqlite")
⋮----
payload = storage_maintenance_snapshot(backend, now=NOW)
logs = next(row for row in payload["tables"] if row["name"] == "worker_logs")
⋮----
serialized = json.dumps(payload)
⋮----
backend = SQLiteBackend(tmp_path / "retention.sqlite")
⋮----
def test_maintenance_api_is_viewer_readable_and_worker_forbidden(tmp_path)
⋮----
control = ControlPlane(
server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(control))
thread = threading.Thread(target=server.serve_forever, daemon=True)
⋮----
base = f"http://127.0.0.1:{server.server_port}"
⋮----
calls = []
⋮----
def fake_snapshot(backend)
⋮----
moments = iter([100.0, 101.0])
⋮----
first = control.dashboard.maintenance()
second = control.dashboard.maintenance()
````

## File: tests/test_dashboard_observability_e2e.py
````python
def _auth()
⋮----
def test_observability_lifecycle_uses_final_usage_and_attributed_commits(tmp_path)
⋮----
control=ControlPlane(str(tmp_path/"db.sqlite"),authorizer=_auth())
workflow=control.workflows.create(
⋮----
job=control.queue.claim_next("worker-a",capabilities=["python"])
job=control.queue.ack(job["key"],"worker-a")
⋮----
result={"usage":{"total_tokens":900,"providers":[{"provider":"test-provider","model":"test-model","api_calls":1,"input_tokens":700,"cached_input_tokens":0,"output_tokens":200,"reasoning_tokens":0,"total_tokens":900}]},"commits":{"count":1,"shas":["a"*40]}}
⋮----
def test_attributed_commit_count_deduplicates_sha_across_executions(tmp_path)
⋮----
control=ControlPlane(str(tmp_path/"db.sqlite"),authorizer=_auth()); store=control.dashboard_store
⋮----
job={"key":f"job-{index}","repository":"dbrckk/example","task":"ship","delivery_attempt":1,"payload":{}}
⋮----
def test_secret_like_log_values_are_redacted_before_persistence(tmp_path)
⋮----
row=control.dashboard_store.logs_for_worker("worker-a")[0]
⋮----
def test_project_progress_exposes_weighted_current_workflow(tmp_path)
⋮----
workflow=control.workflows.create(name="progress-e2e",repository="dbrckk/example",tasks=[WorkflowTaskSpec(task_id="done",title="Done",payload={},estimated_minutes=10),WorkflowTaskSpec(task_id="todo",title="Todo",payload={},estimated_minutes=30)])
⋮----
progress=control.dashboard.project_progress("dbrckk/example")
⋮----
def test_activity_worker_filter_uses_event_payload(tmp_path)
⋮----
rows=control.dashboard.activity(worker_id="worker-a")["events"]
⋮----
def test_project_history_marks_legacy_backfill_partial(tmp_path)
⋮----
history=control.dashboard.project_history("dbrckk/example")
⋮----
def test_project_usage_backfills_legacy_workflow_result_usage(tmp_path)
⋮----
workflow=control.workflows.create(name="legacy-usage",repository="dbrckk/example",tasks=[WorkflowTaskSpec(task_id="done",title="Done",payload={})])
result_json=json.dumps({"usage":{"providers":[{"provider":"legacy-provider","model":"legacy-model","api_calls":1,"input_tokens":200,"cached_input_tokens":0,"output_tokens":100,"reasoning_tokens":0,"total_tokens":300}]}})
⋮----
usage=control.dashboard.project_usage("dbrckk/example","all")
⋮----
def test_project_progress_persists_snapshot_only_when_meaningful_state_changes(tmp_path)
⋮----
workflow=control.workflows.create(name="snapshot-progress",repository="dbrckk/example",tasks=[WorkflowTaskSpec(task_id="build",title="Build",payload={},estimated_minutes=10)])
first=control.dashboard.project_progress("dbrckk/example"); second=control.dashboard.project_progress("dbrckk/example")
history=control.dashboard_store.progress_history("dbrckk/example")
⋮----
changed=control.dashboard.project_progress("dbrckk/example"); history=control.dashboard_store.progress_history("dbrckk/example")
⋮----
def test_project_progress_persists_when_auditable_evidence_changes(tmp_path)
⋮----
before=control.dashboard_store.progress_history("dbrckk/example")
⋮----
after=control.dashboard_store.progress_history("dbrckk/example")
⋮----
def test_project_progress_snapshot_persists_selected_profile(tmp_path)
⋮----
snapshot=control.dashboard_store.latest_progress_snapshot("dbrckk/example")
````

## File: tests/test_dashboard_playbook_api.py
````python
def _control(tmp_path)
⋮----
def test_queue_incident_exposes_truthful_scheduled_kick_fallback(tmp_path)
⋮----
control = _control(tmp_path)
⋮----
incidents = control.dashboard.incidents()["incidents"]
incident = next(x for x in incidents if x["code"] == "queue_without_worker")
suggestion = incident["playbook"]["suggestions"][0]
⋮----
def test_queue_incident_exposes_immediate_kick_only_when_dispatch_is_configured(tmp_path)
⋮----
incident = next(
⋮----
def test_stale_worker_playbook_only_offers_recovery_for_expired_claim(tmp_path)
⋮----
job = control.queue.enqueue({
⋮----
recovery = [
⋮----
def test_stale_execution_playbook_offers_cancel_only_for_active_owned_job(tmp_path)
⋮----
cancel = next(
````

## File: tests/test_dashboard_playbooks.py
````python
def test_queue_without_worker_playbook_is_truthful_about_kick_mode()
⋮----
incident = {
immediate = derive_incident_playbook(
fallback = derive_incident_playbook(
⋮----
def test_stale_worker_recovery_is_suggested_only_for_server_recoverable_jobs()
⋮----
result = derive_incident_playbook(
actions = [(x["action"], x["job_key"]) for x in result["suggestions"]]
⋮----
def test_stale_job_cancel_requires_active_owned_job()
⋮----
active = derive_incident_playbook(
cancel = next(x for x in active["suggestions"] if x["action"] == "cancel-current")
⋮----
terminal = derive_incident_playbook(
cancel = next(x for x in terminal["suggestions"] if x["action"] == "cancel-current")
⋮----
def test_playbook_derivation_has_no_execution_side_effect_contract()
⋮----
result = derive_incident_playbook({
⋮----
def test_resolved_incident_has_no_remediation_actions()
⋮----
def test_stale_job_inspection_is_unavailable_without_owner()
⋮----
inspect = next(x for x in result["suggestions"] if x["action"] == "inspect-job")
cancel = next(x for x in result["suggestions"] if x["action"] == "cancel-current")
````

## File: tests/test_dashboard_remediation_api.py
````python
def _auth()
⋮----
def _request(base, path, token, *, method="POST", body=None)
⋮----
data = None if body is None else json.dumps(body).encode("utf-8")
request = urllib.request.Request(
⋮----
raw = response.read()
⋮----
raw = exc.read()
⋮----
def _server(control)
⋮----
server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(control))
thread = threading.Thread(target=server.serve_forever, daemon=True)
⋮----
def _queue_incident(control)
⋮----
def test_valid_incident_linked_kick_is_traced(tmp_path)
⋮----
control = ControlPlane(str(tmp_path / "remediation-api.sqlite"), authorizer=_auth())
incident = _queue_incident(control)
⋮----
rows = control.dashboard_store.remediation_events(limit=10)
⋮----
def test_incident_link_rejects_unsuggested_control_before_mutation(tmp_path)
⋮----
control = ControlPlane(str(tmp_path / "remediation-reject.sqlite"), authorizer=_auth())
⋮----
def test_incident_link_rejects_wrong_worker_target(tmp_path)
⋮----
control = ControlPlane(str(tmp_path / "remediation-target.sqlite"), authorizer=_auth())
⋮----
def test_direct_control_without_incident_remains_compatible(tmp_path)
⋮----
control = ControlPlane(str(tmp_path / "direct-control.sqlite"), authorizer=_auth())
⋮----
audit = control.dashboard_store.control_audit_events(limit=10)
⋮----
def test_remediation_history_is_viewer_readable_and_worker_forbidden(tmp_path)
⋮----
control = ControlPlane(str(tmp_path / "remediation-read.sqlite"), authorizer=_auth())
⋮----
def test_remediation_history_filters_by_incident_query(tmp_path)
⋮----
control = ControlPlane(str(tmp_path / "remediation-filter.sqlite"), authorizer=_auth())
first = _queue_incident(control)
⋮----
second = control.dashboard_store.upsert_dashboard_incident(
⋮----
def test_remediation_history_verifies_active_then_resolved_incident(tmp_path)
⋮----
control = ControlPlane(
⋮----
event = control.dashboard_store.append_remediation_event(
⋮----
active = control.dashboard.remediation_history(limit=10)["events"][0]
⋮----
resolved = control.dashboard.remediation_history(limit=10)["events"][0]
⋮----
def test_remediation_history_does_not_verify_incomplete_request(tmp_path)
⋮----
payload = control.dashboard.remediation_history(limit=10)
row = next(item for item in payload["events"] if item["id"] == event["id"])
⋮----
def test_remediation_analytics_api_is_viewer_readable_and_worker_forbidden(tmp_path)
⋮----
def test_remediation_analytics_api_rejects_invalid_window(tmp_path)
````

## File: tests/test_dashboard_remediation_history.py
````python
def _store(path)
⋮----
def _incident(store)
⋮----
def test_remediation_event_is_durable_across_restart(tmp_path)
⋮----
path = tmp_path / "remediation.sqlite"
first = _store(path)
incident = _incident(first)
event = first.append_remediation_event(
⋮----
second = _store(path)
rows = second.remediation_events(limit=10)
⋮----
def test_remediation_event_outcome_can_be_finalized(tmp_path)
⋮----
store = _store(tmp_path / "remediation.sqlite")
incident = _incident(store)
event = store.append_remediation_event(
done = store.update_remediation_event(
⋮----
def test_remediation_history_filters_by_incident(tmp_path)
⋮----
first = _incident(store)
second = store.upsert_dashboard_incident(
⋮----
rows = store.remediation_events(limit=10, incident_id=second["id"])
⋮----
def test_remediation_ledger_has_no_freeform_secret_payload(tmp_path)
⋮----
row = store.append_remediation_event(
forbidden = {
⋮----
def test_failed_remediation_is_not_applicable_for_verification(tmp_path)
⋮----
store = _store(tmp_path / "failed.sqlite")
⋮----
failed = store.update_remediation_event(
⋮----
def test_completed_remediation_tracks_active_then_resolved_incident(tmp_path)
⋮----
store = _store(tmp_path / "verification.sqlite")
⋮----
active = store.verify_remediation_events()
⋮----
resolved = store.verify_remediation_events()
⋮----
def test_resolved_verification_never_regresses_after_incident_reopens(tmp_path)
⋮----
store = _store(tmp_path / "terminal.sqlite")
⋮----
before = store.remediation_events(limit=1)[0]
⋮----
reopened = store.upsert_dashboard_incident(
⋮----
after = store.remediation_events(limit=1)[0]
⋮----
def test_sqlite_v14_database_is_migrated_additively_to_v15(tmp_path)
⋮----
path = tmp_path / "migration.sqlite"
db = sqlite3.connect(path)
⋮----
backend = SQLiteBackend(path)
⋮----
version = conn.execute(
columns = {
row = conn.execute(
managed = conn.execute(
runs = conn.execute(
⋮----
def test_repeated_active_verification_is_idempotent(tmp_path)
⋮----
store = _store(tmp_path / "idempotent.sqlite")
⋮----
first = store.verify_remediation_events()
⋮----
row = store.remediation_events(limit=1)[0]
⋮----
verified_at = row["verified_at"]
⋮----
second = store.verify_remediation_events()
⋮----
def test_resolved_remediation_snapshots_occurrence_and_watches_recurrence(tmp_path)
⋮----
store = _store(tmp_path / "recurrence-watch.sqlite")
⋮----
resolved = store.verify_remediation_events()[0]
⋮----
def test_reopened_incident_marks_resolved_remediation_recurred(tmp_path)
⋮----
store = _store(tmp_path / "recurrence-reopen.sqlite")
⋮----
updated = store.verify_remediation_recurrence()
⋮----
def test_recurrence_watching_is_idempotent_until_reopen(tmp_path)
⋮----
store = _store(tmp_path / "recurrence-idempotent.sqlite")
⋮----
def test_recurred_state_is_terminal(tmp_path)
⋮----
store = _store(tmp_path / "recurrence-terminal.sqlite")
⋮----
first = store.verify_remediation_recurrence()[0]
⋮----
recurred_at = first["recurred_at"]
````

## File: tests/test_dashboard_remediation_metrics.py
````python
NOW = datetime(2026, 9, 24, 17, 0, tzinfo=timezone.utc)
⋮----
def test_effectiveness_denominator_excludes_pending_and_not_applicable()
⋮----
rows = [
result = aggregate_remediation_analytics(
summary = result["summary"]
⋮----
def test_median_resolution_detection_uses_only_valid_resolved_rows()
⋮----
def test_window_filter_and_breakdowns_are_deterministic()
⋮----
def test_zero_denominator_has_no_resolution_rate()
⋮----
def test_invalid_window_is_rejected()
⋮----
def test_recurrence_denominator_excludes_unresolved_remediations()
⋮----
result = aggregate_remediation_analytics(rows, window="24h", now=NOW)
⋮----
def test_zero_recurrence_denominator_has_no_rate()
⋮----
def test_durability_timing_uses_only_valid_recurred_rows()
⋮----
def test_watching_age_is_observed_not_final_durability()
⋮----
def test_invalid_durability_timestamps_are_ignored()
⋮----
rows = [{
````

## File: tests/test_dashboard_retention_prune.py
````python
OLD = "2020-01-01T00:00:00+00:00"
RECENT = "2099-01-01T00:00:00+00:00"
⋮----
def _auth()
⋮----
def _post(base, path, token, body)
⋮----
request = urllib.request.Request(
⋮----
def _server(control)
⋮----
server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(control))
thread = threading.Thread(target=server.serve_forever, daemon=True)
⋮----
def _seed_retention_rows(backend)
⋮----
def _seed_old_remediation(control)
⋮----
incident = control.dashboard_store.upsert_dashboard_incident(
⋮----
def test_snapshot_separates_prunable_and_protected_candidates(tmp_path)
⋮----
backend = SQLiteBackend(tmp_path / "retention.sqlite")
⋮----
control = ControlPlane(
⋮----
snapshot = storage_maintenance_snapshot(backend)
logs = next(row for row in snapshot["tables"] if row["name"] == "worker_logs")
executions = next(row for row in snapshot["tables"] if row["name"] == "executions")
⋮----
def test_prune_deletes_only_valid_old_prunable_rows(tmp_path)
⋮----
remediation = _seed_old_remediation(control)
⋮----
before = storage_maintenance_snapshot(control.backend)
⋮----
result = prune_expired_history(
⋮----
log_ids = {
executions = {
remediation_row = db.execute(
⋮----
def test_stale_candidate_count_rolls_back_without_deletion(tmp_path)
⋮----
backend = SQLiteBackend(tmp_path / "conflict.sqlite")
⋮----
before = storage_maintenance_snapshot(backend)
expected = before["prunable_candidate_rows"]
⋮----
def test_prune_api_requires_operator_exact_phrase_and_audits_success(tmp_path)
⋮----
snapshot = storage_maintenance_snapshot(control.backend)
expected = snapshot["prunable_candidate_rows"]
⋮----
audit = control.dashboard_store.control_audit_events(limit=10)
⋮----
def test_prune_api_stale_expected_count_returns_409_and_zero_deletion(tmp_path)
⋮----
expected = storage_maintenance_snapshot(
⋮----
ids = {
````

## File: tests/test_dashboard_security.py
````python
def test_recursive_redaction_removes_sensitive_values()
⋮----
value = {
redacted = redact_log_value(value)
````

## File: tests/test_dashboard_store_postgres.py
````python
DSN = os.getenv("PRODUCTION_OS_TEST_POSTGRES")
⋮----
pytestmark = pytest.mark.skipif(
⋮----
REQUIRED_EXECUTION_COLUMNS = {
⋮----
def test_postgres_schema_v15_has_managed_project_generation_tables()
⋮----
backend = PostgresBackend(DSN)
⋮----
columns = {row["column_name"] for row in cur.fetchall()}
⋮----
audit_table = cur.fetchone()
⋮----
incident_table = cur.fetchone()
⋮----
remediation_table = cur.fetchone()
⋮----
remediation_columns = {
⋮----
managed_tables = {row["table_name"] for row in cur.fetchall()}
⋮----
managed_columns = {row["column_name"] for row in cur.fetchall()}
⋮----
def test_dashboard_service_project_queries_work_on_postgres()
⋮----
control = ControlPlane(DSN)
repository = "dbrckk/postgres-dashboard"
workflow = control.workflows.create(
payload = control.dashboard.project_workflows(repository)
⋮----
progress = control.dashboard.project_progress(repository)
⋮----
def test_postgres_storage_maintenance_snapshot_has_size_and_no_dsn()
⋮----
payload = storage_maintenance_snapshot(backend)
⋮----
names = {row["name"] for row in payload["tables"]}
⋮----
def test_postgres_retention_classifies_terminal_and_running_executions_safely()
⋮----
suffix = uuid4().hex
old = "2020-01-01T00:00:00+00:00"
running_id = "retention-running-" + suffix
terminal_id = "retention-terminal-" + suffix
⋮----
executions = next(
````

## File: tests/test_dashboard_store.py
````python
def _store(tmp_path): return DashboardStore(SQLiteBackend(tmp_path/"db.sqlite"))
⋮----
def _sample_job()
⋮----
def test_execution_lifecycle_and_attempt_identity(tmp_path)
⋮----
store=_store(tmp_path); job=_sample_job()
first=store.start_execution(job,"worker-a")
duplicate=store.start_execution(job,"worker-a")
⋮----
live=store.update_live_execution("job-1","worker-a",{"stage":"tests","progress":50,"usage":{"total_tokens":10}})
⋮----
result={"usage":{"api_calls":1,"input_tokens":4,"cached_input_tokens":1,"output_tokens":3,
done=store.finish_execution("job-1","worker-a",status="succeeded",duration_seconds=12,result=result)
⋮----
retry={**job,"delivery_attempt":2}
⋮----
def test_live_progress_cannot_move_backward_in_same_stage(tmp_path)
⋮----
store=_store(tmp_path); store.start_execution(_sample_job(),"worker-a")
⋮----
def test_finish_execution_is_idempotent(tmp_path)
⋮----
first=store.finish_execution("job-1","worker-a",status="succeeded",duration_seconds=2,result={})
second=store.finish_execution("job-1","worker-a",status="failed",duration_seconds=9,result={})
⋮----
def test_log_cursor_is_deterministic(tmp_path)
⋮----
store=_store(tmp_path)
⋮----
rows=store.logs_for_worker("worker-a",limit=1)
⋮----
older=store.logs_for_worker("worker-a",after="b",limit=10)
⋮----
def test_snapshot_roundtrip_and_usage_query(tmp_path)
⋮----
repo=store.save_repository_snapshot({"id":"r1","repository":"dbrckk/example","default_branch":"main",
⋮----
progress=store.save_progress_snapshot({"id":"p1","repository":"dbrckk/example","confidence":"high",
⋮----
def test_append_logs_generates_collision_safe_ids(tmp_path)
⋮----
store=_store(tmp_path); at="2026-09-22T10:00:00+00:00"
rows=store.append_logs("worker-a",[{"created_at":at,"message":"same"},{"created_at":at,"message":"same"}])
⋮----
def test_finish_execution_ignores_malformed_commit_shas(tmp_path)
⋮----
store=_store(tmp_path); store.start_execution(_sample_job(),"worker-a"); valid="a"*40
row=store.finish_execution("job-1","worker-a",status="succeeded",duration_seconds=1,result={
⋮----
def test_progress_snapshot_order_is_deterministic_when_timestamps_tie(tmp_path)
⋮----
store=_store(tmp_path); captured="2026-09-24T04:00:00+00:00"
base={"repository":"dbrckk/example","captured_at":captured,"calculation_version":"project-progress/v1","confidence":"low"}
````

## File: tests/test_dashboard_ui_v3.py
````python
def test_dashboard_has_primary_views_and_clickable_entities()
⋮----
def test_polling_does_not_reload_or_replace_location()
⋮----
def test_dashboard_has_worker_and_project_detail_tabs()
⋮----
def test_dashboard_preserves_launch_and_mobile_accessibility()
⋮----
def test_dashboard_overview_is_bound_to_observability_api()
⋮----
def test_dashboard_v3_has_usage_window_controls()
⋮----
def test_dashboard_workers_view_is_bound_to_observability_api()
⋮----
def test_dashboard_projects_view_is_bound_to_observability_api()
⋮----
def test_dashboard_activity_view_is_bound_to_observability_api()
⋮----
def test_worker_detail_exposes_live_task_and_health_information()
⋮----
def test_worker_detail_exposes_api_usage_breakdown()
⋮----
def test_worker_detail_exposes_execution_history()
⋮----
def test_worker_detail_exposes_structured_recent_logs()
⋮----
def test_worker_detail_exposes_capabilities_and_health()
⋮----
def test_project_detail_exposes_progress_evidence()
⋮----
def test_project_detail_exposes_progress_components()
⋮----
def test_project_detail_exposes_commit_window_and_sources()
⋮----
def test_project_detail_exposes_api_usage_breakdown()
⋮----
def test_worker_control_tab_has_safe_actions()
⋮----
html = DASHBOARD_HTML
⋮----
def test_ui_distinguishes_requested_from_acknowledged()
⋮----
def test_control_refresh_preserves_navigation_and_scroll_contract()
⋮----
def test_overview_renders_operational_alerts()
⋮----
def test_dashboard_has_autopilot_primary_view()
⋮----
def test_autopilot_view_exposes_queue_explanations()
⋮----
def test_autopilot_navigation_preserves_polling_scroll_contract()
⋮----
def test_autopilot_surfaces_degraded_ranking_state()
⋮----
def test_autopilot_view_shows_capacity_summary()
⋮----
def test_activity_view_renders_operator_control_audit()
⋮----
def test_overview_renders_operational_health()
⋮----
def test_worker_control_exposes_recover_stuck_only_from_recoverable_jobs()
⋮----
def test_overview_renders_and_acknowledges_durable_incidents()
⋮----
def test_overview_renders_server_backed_incident_playbooks()
⋮----
def test_incident_playbook_actions_are_explicit_and_reuse_control_api()
⋮----
def test_incident_inspection_playbooks_only_navigate()
⋮----
def test_incident_playbook_actions_send_incident_id()
⋮----
def test_activity_view_renders_remediation_history()
⋮----
def test_direct_worker_controls_do_not_require_incident_id()
⋮----
def test_activity_view_renders_remediation_verification_status()
⋮----
def test_activity_view_renders_remediation_analytics_with_sample_sizes()
⋮----
def test_activity_view_renders_remediation_recurrence_status()
⋮----
def test_activity_view_renders_remediation_durability_timing()
⋮----
def test_launch_repository_picker_is_server_backed()
⋮----
def test_mobile_launch_flow_remains_repo_plus_instruction()
⋮----
def test_overview_renders_storage_maintenance_card()
⋮----
def test_storage_maintenance_failure_does_not_break_overview()
⋮----
def test_storage_retention_ui_separates_prunable_and_protected_rows()
⋮----
def test_retention_prune_requires_explicit_confirmation_and_exact_phrase()
⋮----
def test_retention_prune_button_only_renders_for_positive_prunable_count()
⋮----
def test_overview_renders_backup_readiness_and_safe_create_button()
⋮----
def test_backup_ui_does_not_render_server_paths()
⋮----
def test_backup_catalog_exposes_restore_readiness_and_safe_staging()
⋮----
def test_restore_staging_ui_never_exposes_live_activation_or_paths()
⋮----
def test_dashboard_has_managed_projects_view()
⋮----
def test_managed_projects_view_exposes_safe_review_and_attention_actions()
⋮----
def test_managed_projects_navigation_preserves_existing_polling_contract()
⋮----
def test_managed_projects_mobile_creation_form_is_inline_and_server_backed()
⋮----
def test_managed_project_instruction_uses_inline_textarea_not_prompt()
⋮----
def test_managed_projects_mobile_view_renders_generation_history()
⋮----
def test_managed_repository_picker_reuses_server_repository_discovery()
⋮----
def test_backup_overview_renders_restore_activation_history()
````

## File: tests/test_dashboard_usage.py
````python
def test_pricing_returns_unknown_for_unlisted_model()
⋮----
catalog = PricingCatalog.from_mapping({"version":"2026-09-22","rules":[]})
⋮----
def test_pricing_uses_exact_versioned_rule_and_zero_is_zero()
⋮----
catalog = PricingCatalog.from_mapping({
⋮----
def test_pricing_missing_token_field_is_unknown()
⋮----
def test_usage_aggregation_does_not_mix_live_snapshot_with_final_events()
⋮----
rows = [{
result = aggregate_usage(
⋮----
def test_usage_aggregation_hides_unauthenticated_quota_numbers()
⋮----
quotas = {row["provider"]: row for row in result["quotas"]}
⋮----
def test_usage_aggregation_rejects_unknown_window()
````

## File: tests/test_database_maintenance_lock.py
````python
def test_sqlite_database_lock_blocks_second_live_owner(tmp_path)
⋮----
database = tmp_path / "production.sqlite"
first = SQLiteDatabaseProcessLock(str(database))
second = SQLiteDatabaseProcessLock(str(database))
⋮----
metadata = json.loads(
⋮----
def test_sqlite_database_lock_can_be_reacquired_after_release(tmp_path)
⋮----
def test_lock_file_persistence_does_not_mean_database_is_locked(tmp_path)
⋮----
path = tmp_path / "production.sqlite.maintenance.lock"
⋮----
lock = SQLiteDatabaseProcessLock(str(database))
⋮----
metadata = json.loads(path.read_text())
⋮----
def test_postgres_database_server_lock_is_noop()
⋮----
events = []
⋮----
@contextmanager
    def fake_lock(database)
⋮----
class FakeServer
⋮----
def __init__(self, address, handler)
⋮----
def serve_forever(self)
⋮----
def server_close(self)
⋮----
database = str(tmp_path / "production.sqlite")
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
⋮----
def test_default_branch_commit_count_uses_last_link_page()
⋮----
client = GitHubClient("token")
⋮----
def test_default_branch_commit_count_handles_single_and_empty()
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

## File: tests/test_managed_projects_http_v4.py
````python
def _auth()
⋮----
def _request(base, path, token, *, method="GET", body=None)
⋮----
data = None if body is None else json.dumps(body).encode("utf-8")
req = urllib.request.Request(
⋮----
raw = response.read()
⋮----
raw = exc.read()
⋮----
def _server(control)
⋮----
server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(control))
thread = threading.Thread(target=server.serve_forever, daemon=True)
⋮----
def test_operator_can_create_and_viewer_can_list_managed_projects(tmp_path)
⋮----
control = ControlPlane(str(tmp_path / "db.sqlite"), authorizer=_auth())
⋮----
project = created["project"]
⋮----
def test_viewer_cannot_create_managed_project(tmp_path)
⋮----
def test_managed_project_http_generations_and_explicit_completion(tmp_path)
⋮----
project_id = project["project_id"]
first_workflow = project["workflow_id"]
⋮----
second_workflow = resumed["project"]["workflow_id"]
⋮----
third_workflow = verifying["project"]["workflow_id"]
⋮----
def test_managed_project_persists_across_control_plane_restart(tmp_path)
⋮----
database = str(tmp_path / "managed-restart.sqlite")
first = ControlPlane(database, authorizer=_auth())
created = first.managed_projects.create(
first_workflow = created["workflow_id"]
⋮----
second = ControlPlane(database, authorizer=_auth())
restored = second.managed_projects.get(created["project_id"])
⋮----
resumed = second.managed_projects.add_instruction(
⋮----
def test_worker_cannot_read_managed_projects(tmp_path)
⋮----
control = ControlPlane(str(tmp_path / "worker-read.sqlite"), authorizer=_auth())
````

## File: tests/test_managed_projects_v4.py
````python
def service(tmp_path)
⋮----
backend = SQLiteBackend(tmp_path / "db.sqlite")
queue = SQLiteJobQueue(backend)
workflows = WorkflowEngine(backend, queue)
⋮----
def test_managed_project_requires_human_completion_after_execution(tmp_path)
⋮----
created = projects.create(
⋮----
review = projects.get(created["project_id"])
⋮----
done = projects.mark_done(created["project_id"], approved_by="operator:test")
⋮----
def test_followup_instruction_creates_new_immutable_workflow_generation(tmp_path)
⋮----
first_workflow_id = created["workflow_id"]
⋮----
first_before = workflows.get(first_workflow_id)
⋮----
resumed = projects.add_instruction(
⋮----
first_after = workflows.get(first_workflow_id)
⋮----
second = workflows.get(resumed["workflow_id"])
task = second["tasks"][0]
⋮----
def test_retest_creates_new_generation_with_original_final_goal(tmp_path)
⋮----
running = projects.request_verification(
⋮----
task = workflows.get(running["workflow_id"])["tasks"][0]
⋮----
def test_failed_generation_maps_to_needs_attention_and_allows_followup(tmp_path)
⋮----
attention = projects.get(created["project_id"])
⋮----
def test_active_generation_rejects_followup(tmp_path)
⋮----
def test_managed_project_list_excludes_normal_workflows(tmp_path)
⋮----
listed = projects.list()
⋮----
def test_managed_project_rejects_invalid_budget_and_repository(tmp_path)
⋮----
def test_legacy_v4_workflow_is_migrated_on_first_read(tmp_path)
⋮----
legacy = workflows.create(
⋮----
migrated = projects.get(legacy["id"])
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
⋮----
def test_paused_worker_cannot_claim_but_can_heartbeat(tmp_path)
⋮----
def test_heartbeat_acknowledges_current_worker_desired_state(tmp_path)
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

## File: tests/test_project_progress.py
````python
def test_workflow_progress_is_weighted_by_estimated_minutes()
⋮----
workflow={"tasks":[{"status":"succeeded","estimated_minutes":10},{"status":"running","estimated_minutes":30}]}
result=workflow_progress(workflow)
⋮----
def test_zero_minute_virtual_barrier_does_not_distort_progress()
⋮----
workflow={"tasks":[{"status":"succeeded","estimated_minutes":10},{"status":"pending","estimated_minutes":0}]}
⋮----
def test_terminal_semantics_and_no_executable_weight()
⋮----
def test_backend_profile_marks_ui_and_assets_not_applicable()
⋮----
engine=ProjectProgressEngine()
result=engine.calculate("dbrckk/api",{"profile":"backend","dimensions":{
⋮----
def test_confidence_thresholds_are_stable()
⋮----
def test_build_project_evidence_derives_dimensions_from_observed_facts()
⋮----
evidence = build_project_evidence(
⋮----
def test_build_project_evidence_keeps_missing_facts_unknown()
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

## File: tests/test_release16_operations_e2e.py
````python
def _auth()
⋮----
def _request(base, path, token, *, method="GET", body=None)
⋮----
data = None if body is None else json.dumps(body).encode("utf-8")
request = urllib.request.Request(
⋮----
raw = response.read()
⋮----
def _server(control)
⋮----
server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(control))
thread = threading.Thread(target=server.serve_forever, daemon=True)
⋮----
def test_release16_operator_path_survives_restart(tmp_path, monkeypatch)
⋮----
database = str(tmp_path / "production.sqlite")
backup_dir = tmp_path / "backups"
⋮----
first = ControlPlane(database, authorizer=_auth())
⋮----
workflow_id = created["workflow"]["id"]
⋮----
job_key = dispatched["jobs"][0]["key"]
⋮----
incident = next(
kick = next(
⋮----
backup_id = backup["backup_id"]
⋮----
remediation_rows = first.dashboard_store.remediation_events(limit=10)
⋮----
audit = first.dashboard_store.control_audit_events(limit=50)
actions = {row["action"] for row in audit}
⋮----
second = ControlPlane(database, authorizer=_auth())
⋮----
catalog = second.dashboard.backups()
````

## File: tests/test_release18_managed_projects_e2e.py
````python
def _auth()
⋮----
def _request(base, path, token, *, method="GET", body=None)
⋮----
data = None if body is None else json.dumps(body).encode("utf-8")
request = urllib.request.Request(
⋮----
raw = response.read()
⋮----
raw = exc.read()
⋮----
def _server(control)
⋮----
server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(control))
thread = threading.Thread(target=server.serve_forever, daemon=True)
⋮----
def test_release18_managed_project_generations_survive_restart(tmp_path)
⋮----
database = str(tmp_path / "managed-e2e.sqlite")
first = ControlPlane(database, authorizer=_auth())
⋮----
project = created["project"]
project_id = project["project_id"]
first_workflow_id = project["workflow_id"]
⋮----
first_snapshot = first.workflows.get(first_workflow_id)
⋮----
second = instructed["project"]
second_workflow_id = second["workflow_id"]
⋮----
third = retested["project"]
third_workflow_id = third["workflow_id"]
⋮----
final = completed["project"]
⋮----
second = ControlPlane(database, authorizer=_auth())
restored = second.managed_projects.get(project_id)
⋮----
listed = second.managed_projects.list()
````

## File: tests/test_release19_restore_staging_e2e.py
````python
def _auth()
⋮----
def _request(base, path, token, *, method="GET", body=None)
⋮----
data = None if body is None else json.dumps(body).encode("utf-8")
request = urllib.request.Request(
⋮----
raw = response.read()
⋮----
def _server(control)
⋮----
server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(control))
thread = threading.Thread(target=server.serve_forever, daemon=True)
⋮----
database = tmp_path / "production.sqlite"
backup_dir = tmp_path / "backups"
⋮----
first = ControlPlane(str(database), authorizer=_auth())
⋮----
backup_id = backup["backup_id"]
⋮----
candidate = (
⋮----
candidate_probe = db.execute(
⋮----
live_probe = db.execute(
⋮----
audit = first.dashboard_store.control_audit_events(limit=20)
stage_event = next(
⋮----
second = ControlPlane(str(database), authorizer=_auth())
⋮----
restarted_probe = db.execute(
````

## File: tests/test_release21_offline_restore_e2e.py
````python
database = tmp_path / "production.sqlite"
backup_dir = tmp_path / "backups"
⋮----
backend = SQLiteBackend(database)
⋮----
backup = create_verified_sqlite_backup(backend)
staged = stage_verified_sqlite_restore(backend, backup["backup_id"])
⋮----
args = _parse_args([
⋮----
payload = json.loads(capsys.readouterr().out)
⋮----
restarted = ControlPlane(str(database))
⋮----
value = db.execute(
⋮----
rollback = backup_dir / f"{payload['rollback_backup_id']}.sqlite"
⋮----
rollback_value = db.execute(
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
⋮----
def test_workflow_metadata_can_be_updated_without_recreating_workflow(tmp_path)
⋮----
updated=wf.update_metadata(
⋮----
def test_workflow_add_task_validates_dependencies_and_becomes_dispatchable(tmp_path)
⋮----
updated=wf.add_task(
task=next(item for item in updated["tasks"] if item["task_id"]=="follow-up")
⋮----
jobs=wf.dispatch_ready(created["id"],task_id="follow-up")
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
⋮----
def test_postgres_managed_project_review_lifecycle()
⋮----
projects=ManagedProjectService(engine)
project=projects.create(
⋮----
first_workflow=project["workflow_id"]
⋮----
review=projects.get(project["project_id"])
⋮----
resumed=projects.add_instruction(
⋮----
second_workflow=resumed["workflow_id"]
⋮----
done=projects.mark_done(
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

## Dashboard Control Center Release 2

The dashboard control center separates **desired control intent** from **observed worker state**.

Worker controls:

- `pause`: blocks new claims and lets the current task continue;
- `drain`: blocks new claims and lets active tasks finish before the worker becomes drained;
- `resume`: returns the worker desired state to `active`;
- `cancel-current`: cooperatively cancels one explicitly named active `job_key`;
- `retry`: creates a new workflow attempt with a new job key while preserving prior execution history;
- `kick`: requests an immediate GitHub Actions worker run only when server-side GitHub dispatch credentials are configured.

All dashboard control endpoints require the `operator` role.

Cancellation is job-scoped rather than worker-wide. A cancellation request is not considered acknowledged until the worker reports the matching `cancel_requested` state. Terminal job transitions are exclusive: once cancellation wins, a late completion is rejected; once completion wins, a later cancel-current request is rejected.

Retries preserve lineage. The previous failed or cancelled execution remains immutable, the replacement receives a new idempotency/job key, workflow generation checks still apply, and `max_attempts` cannot be bypassed by repeated control requests.

GitHub Actions kick outcomes are reported honestly:

```text
dispatched
scheduled_fallback
failed
```

`scheduled_fallback` means no immediate dispatch was possible and the existing five-minute scheduled worker poll remains the next wake-up path. It must not be presented as a started worker.

The UI separately presents:

```text
Action demandée
Confirmée par le worker
```

so operator intent is never displayed as runtime acknowledgement before heartbeat evidence exists.

Optional server-side configuration:

```text
PRODUCTION_OS_ACTIONS_REPOSITORY=dbrckk/ai-dev-server
PRODUCTION_OS_ACTIONS_WORKFLOW=production-os-actions-worker.yml
PRODUCTION_OS_ACTIONS_REF=main
```

The GitHub token remains server-side and is never returned to dashboard JavaScript.

## Dashboard Control Center Release 3

Release 3 hardens day-to-day operation of the control center.

### Operator audit

Every operator control action is written to a dedicated durable audit log with:

```text
action
worker_id
optional job_key
requested_by
outcome
optional error_code
requested_at
```

The audit schema intentionally has no columns for bearer tokens, authorization headers, GitHub tokens, or arbitrary secret metadata.

Dashboard viewers can inspect:

```text
GET /v1/dashboard/control-audit?limit=100
```

Worker credentials cannot read dashboard audit history.

### Operational health

The liveness endpoint `/health` only answers whether the HTTP service is alive.

Operational health is separate:

```text
GET /v1/dashboard/health
```

It reports `healthy` or `degraded` with explicit reasons such as:

- queued work with no online worker;
- a busy worker whose heartbeat is stale;
- a running execution whose telemetry is stale.

These diagnostics do not automatically cancel or mutate work.

### Targeted stuck-job recovery

The dashboard exposes a recovery action only for jobs that are still in `claimed` state and whose acknowledgement deadline has expired.

```text
recover-stuck
```

Recovery is job-scoped and requires an explicit `job_key`. A non-expired claim is rejected. The attempt budget is preserved:

- below `max_attempts` → return the job to `queued`;
- at or above `max_attempts` → move the job to `dead-letter`.

The action is audited whether it succeeds or is rejected.

## Dashboard Control Center Release 4

Release 4 adds durable operational incident management on top of Release 3 health diagnostics.

Incidents follow the lifecycle:

```text
open → acknowledged → resolved
```

Health diagnostics are converted into targeted incidents for:

- the global control plane;
- an individual worker;
- an individual job.

Repeated polling does not inflate the occurrence counter when the evidence is unchanged. If an incident clears, it is marked `resolved` rather than deleted. If the same condition later returns, the incident reopens as `open`, increments its occurrence count, and clears the previous acknowledgement.

Dashboard endpoints:

```text
GET  /v1/dashboard/incidents
POST /v1/dashboard/incidents/{incident_id}/acknowledge
```

Viewer and operator roles may read incidents. Acknowledgement requires operator. Worker credentials cannot read dashboard incident history.

Acknowledgement records the operator identity and timestamp. Incident records deliberately avoid arbitrary payload, metadata, authorization headers, or credential fields.

Incident reconciliation is observational only. It does not automatically pause workers, cancel jobs, retry work, or run stuck-job recovery.

## Dashboard Control Center Release 5 — Safe remediation playbooks

Durable incidents can now expose deterministic remediation guidance derived from current server facts.

The dashboard never decides availability on its own. Each playbook suggestion includes:

```text
action
worker_id
job_key
availability
reason
interrupting
```

Availability values are:

```text
available
fallback
unavailable
```

Examples:

- `queue_without_worker` may suggest a GitHub Actions `kick`;
- `stale_busy_workers` may suggest inspection and a targeted `recover-stuck` only for an expired claimed job;
- `stale_running_executions` may suggest inspection and an explicit `cancel-current` only while the named job is still active and owned by the named worker.

Resolved incidents expose no remediation actions.

Playbook generation is read-only and deterministic. It does not mutate the queue, pause workers, cancel jobs, retry work, or recover claims.

Interrupting remediation always requires an explicit operator action and reuses the existing validated control API, including the same confirmation flow used by direct worker controls. Inspection suggestions are navigation-only.

The browser receives no GitHub, worker, or operator credentials from playbook generation.

## Dashboard Control Center Release 6 — Remediation history

Incident-linked remediation actions now have durable lineage in a dedicated remediation ledger.

This ledger is separate from the generic control audit and records only structured fields:

```text
incident_id
action
worker_id
job_key
requested_by
outcome
error_code
requested_at
completed_at
```

No credentials, authorization headers, tokens, arbitrary metadata or free-form request payloads are stored.

When a playbook action is executed from the dashboard, the browser sends the incident id together with the existing worker control request. The server then re-derives the current incident playbook and verifies the exact action, worker target, job target and availability before any control mutation occurs.

If the incident is stale, resolved, the target changed, or the suggested action is no longer available, the server returns a conflict and does not create control or remediation state.

Direct operator controls remain supported without an incident id and continue to use the existing control audit only.

The dashboard Activity view exposes both:

```text
Audit des contrôles
Historique des remédiations
```

so operators can distinguish ordinary control actions from incident-driven remediation.

## Dashboard Control Center Release 7 — Remediation verification

Incident-linked remediation history now distinguishes the control result from whether the incident was actually cleared.

Verification states are:

```text
pending
still_active
resolved
not_applicable
```

Semantics:

- `pending`: the remediation request completed but has not yet been checked against refreshed incident state;
- `still_active`: the related incident remains open or acknowledged after a verification refresh;
- `resolved`: the related incident is durably resolved;
- `not_applicable`: the remediation action itself failed, so effectiveness verification does not apply.

Verification is observational only. It never triggers another kick, retry, cancellation, recovery, pause, resume or drain action.

The verification engine runs from current durable incident state. A resolved verification is terminal and does not regress if the same incident later reopens as a new occurrence.

To avoid write amplification from dashboard polling, repeated checks that would keep the same verification state do not rewrite the remediation ledger or increment the verification counter.

Existing schema v12 databases are migrated additively to schema v13 with:

```text
verification_state
verification_checks
verified_at
```

The Activity view shows control outcome and remediation verification separately.

## Dashboard Control Center Release 8 — Remediation analytics

The dashboard can summarize observed remediation effectiveness without turning historical metrics into automatic control decisions.

Analytics support the existing dashboard windows:

```text
24h
7d
30d
all
```

The summary exposes:

```text
total
resolved
still_active
pending
not_applicable
effectiveness_denominator
observed_resolution_rate
median_resolution_detection_seconds
```

The observed resolution rate uses only remediation events with a verification state of `resolved` or `still_active`:

```text
resolved / (resolved + still_active)
```

Pending and not-applicable events are excluded from that denominator.

The median resolution-detection duration is calculated only from resolved events with valid `completed_at` and `verified_at` timestamps.

Breakdowns are available by control action and by incident code. Every rate is displayed with its observed sample size. A zero-size effectiveness sample produces no rate rather than an inferred value.

These analytics are read-only. They never rank playbooks, launch controls, or change worker, job, workflow, incident, or remediation state beyond the existing incident refresh needed to read current verification facts.

## Dashboard Control Center Release 9 — Remediation recurrence

Resolved remediation events are now monitored for incident recurrence.

When a remediation verification becomes `resolved`, Production-OS stores the incident's current `occurrence_count` and starts a read-only recurrence watch.

If the same durable incident later reopens and its `occurrence_count` becomes greater than the stored resolution snapshot, the remediation event is marked:

```text
recurrence_state = recurred
```

The recurrence lifecycle is:

```text
not_evaluated -> watching -> recurred
```

`recurred` is terminal for that remediation event. Pending, still-active and not-applicable remediations do not enter recurrence tracking.

Recurrence is observational only. It never triggers retry, cancellation, recovery, pause, drain, kick or any other control action.

Remediation analytics expose recurrence with explicit denominators:

```text
watching_recurrence
recurred
recurrence_denominator
observed_recurrence_rate
```

The dashboard Activity view presents recurrence separately from control outcome and remediation verification.

## Dashboard Control Center Release 10 — Remediation durability

Remediation analytics now measure observed durability after a verified resolution.

For remediations that later recur, Production-OS derives:

```text
median_time_to_recurrence_seconds
min_time_to_recurrence_seconds
max_time_to_recurrence_seconds
```

For resolved remediations that remain under recurrence watch, Production-OS exposes:

```text
median_watching_age_seconds
```

These metrics are descriptive only. They never trigger retry, cancel, recovery, pause, drain, kick or any other control action.

Invalid or chronologically inconsistent timestamps are ignored instead of being converted into misleading durations.

## Dashboard Control Center Release 11 — Simplified launch UX

The default operator workflow is intentionally minimal:

```text
select repository
enter instruction
launch production
```

Opening the Production-OS service root redirects to `/dashboard`. Machine health checks remain available at `/health` and `/healthz`.

Repository discovery is performed by Production-OS on the server through `GitHubClient`. The browser no longer calls GitHub's repository API directly.

When a server-side GitHub token is available, Production-OS lists repositories accessible to that credential for the configured owner. If not, it falls back to the owner's public repositories. If GitHub itself is unavailable, the picker degrades to repositories already observed locally by Production-OS.

No additional operator credential, token field or launch parameter is introduced.

## Dashboard Control Center Release 12 — Storage maintenance visibility

Production-OS exposes a read-only storage maintenance snapshot at:

```text
GET /v1/dashboard/maintenance
```

It reports:

- backend kind (SQLite or PostgreSQL);
- measurable database size in bytes;
- row counts for durable operational tables;
- oldest/newest valid timestamps;
- invalid timestamp counts;
- configured retention days and cutoffs;
- rows currently older than each retention window;
- total retention candidates;
- a maintenance status: `healthy`, `attention`, or `unknown`.

Default retention windows are currently diagnostic only:

```text
worker logs                  30 days
API usage                    90 days
job executions               90 days
control audit               180 days
remediation history         180 days
repository/progress snapshots 90 days
generic event stream         90 days
```

Release 12 performs no deletion, VACUUM, backup mutation or restore action. It deliberately establishes visibility before destructive maintenance is introduced. Timestamp scans are streamed row by row so large history tables do not need to be loaded fully into memory. The resulting maintenance snapshot is cached server-side for five minutes (30 seconds after an unknown/error state), so normal dashboard polling does not repeatedly rescan large tables.

The dashboard never exposes the SQLite path, PostgreSQL DSN, credentials or tokens. If maintenance diagnostics fail, the rest of the Overview remains available and the storage card degrades to `unknown`.

## Dashboard Control Center Release 13 — Safe retention cleanup

Expired historical data can now be pruned explicitly by an operator from the Storage & retention card.

The cleanup endpoint is:

```text
POST /v1/dashboard/maintenance/prune
```

and requires both:

```text
confirm = PRUNE_EXPIRED_HISTORY
expected_candidate_rows = <fresh prunable count observed by the operator>
```

The server recomputes every eligible row inside the cleanup transaction. If the current prunable count differs from the operator's expected count, cleanup returns a conflict and deletes nothing.

Prunable history includes expired:

- API usage events;
- worker log events;
- terminal job executions (`succeeded`, `failed`, `cancelled`);
- control audit events;
- repository/progress snapshots;
- generic event-stream entries.

Protected data includes:

- running/non-terminal executions;
- incident records;
- remediation history;
- workflows and workflow tasks;
- jobs and workers;
- worker/job desired control state;
- release/trust history;
- invalid timestamps and rows newer than their retention cutoff.

Cleanup is never automatic. It is not triggered by alerts, health checks, analytics or dashboard polling. The UI requires an explicit browser confirmation, and every accepted/conflicted cleanup request is recorded in the control audit.

Release 13 does not run `VACUUM` in the request path and does not mutate backup/restore state.

## Dashboard Control Center Release 14 — Backup readiness

Production-OS can create verified server-side SQLite backups before any restore capability is enabled.

SQLite backup creation uses the online SQLite backup API, then performs:

```text
online backup
-> PRAGMA integrity_check
-> SHA-256 + size
-> atomic rename
-> safe manifest
```

The backup directory is configured only on the server through:

```text
PRODUCTION_OS_BACKUP_DIR
```

No filesystem path, database path, DSN, token, password, or secret is returned by the dashboard API or stored in the backup manifest.

Backup creation is operator-only and requires the exact confirmation phrase:

```text
CREATE_VERIFIED_BACKUP
```

Viewer access is limited to backup readiness and verified catalog metadata.

PostgreSQL backup creation is intentionally not claimed in Release 14. The dashboard reports it as unsupported until qualified external `pg_dump` tooling is explicitly integrated.

Restore remains disabled.

## Dashboard Control Center Release 15 — Restore readiness

Production-OS can verify that a server-created SQLite backup is genuinely restorable without modifying the live database.

Restore-readiness verification accepts only the server-issued `backup_id`; clients never provide filesystem paths. The server derives the backup and manifest locations from `PRODUCTION_OS_BACKUP_DIR`, then verifies:

```text
manifest identity
-> exact file size
-> SHA-256
-> read-only SQLite open
-> PRAGMA integrity_check
-> schema_meta schema_version
```

Verification is operator-only and requires the exact confirmation:

```text
VERIFY_BACKUP_FOR_RESTORE
```

The operation is audit logged. It does not write to the live database or the backup database.

Restore remains disabled in Release 15. PostgreSQL restore verification remains unsupported until qualified `pg_dump` / `pg_restore` tooling is integrated.

No database path, backup path, DSN, token, password or secret is returned by the API or rendered in the dashboard.

## Release 19 — Safe restore staging

Verified SQLite backups can be materialized into an isolated restore candidate without mutating the live database.

The operator action:

```text
POST /v1/dashboard/backups/{backup_id}/stage-restore
confirm = STAGE_VERIFIED_RESTORE
```

performs:

1. Existing backup manifest, size, SHA-256 and SQLite integrity verification.
2. SQLite backup-copy into a server-generated temporary candidate.
3. Candidate `PRAGMA integrity_check`.
4. Candidate schema version read.
5. Candidate SHA-256 and size calculation.
6. Atomic rename inside `PRODUCTION_OS_BACKUP_DIR`.

The browser never provides or receives filesystem paths.

The returned candidate metadata includes:

```text
candidate_id
source_backup_id
backend_kind
verified
integrity
schema_version
size_bytes
sha256
staged_at
activation_enabled = false
```

Restore staging is deliberately non-destructive. It never swaps or overwrites the active Production-OS database. Live activation remains disabled and must be designed as a separate maintenance-mode operation.

## Release 20 — Exclusive SQLite maintenance lock

The long-running control-plane server now owns an exclusive operating-system lock for the lifetime of a SQLite database process.

The lock is based on POSIX `flock(LOCK_EX | LOCK_NB)`, not file age. This means:

- a second control-plane process fails fast while the first process holds the lock;
- the kernel automatically releases ownership if the process exits or crashes;
- the metadata file may remain on disk without blocking future acquisition;
- no time-based stale-lock deletion can accidentally evict a healthy server.

The lock file is derived server-side from the SQLite database path and contains only diagnostic metadata such as PID, timestamp and purpose. It is never returned through the HTTP API.

PostgreSQL is unchanged because database-level maintenance coordination must use PostgreSQL-native mechanisms rather than a local filesystem lock.

This lock is a prerequisite for any future destructive SQLite restore activation. Release 20 itself performs no restore and no live database replacement.

## Release 21 — Offline SQLite restore activation

A staged SQLite restore candidate can be activated only through the CLI while the live control plane is offline.

Example:

```bash
production-os restore-activate \
  --database /path/to/production.sqlite \
  --candidate-id <candidate-id> \
  --confirm ACTIVATE_STAGED_RESTORE
```

Activation safety sequence:

1. Revalidate the staged candidate manifest, SHA-256, size, integrity and schema.
2. Acquire the exclusive Release 20 SQLite maintenance lock.
3. Revalidate the candidate after the lock is held.
4. Create a verified rollback backup of the current live database.
5. Copy the candidate to a temporary file beside the live database.
6. Verify the temporary candidate.
7. Remove only the target database WAL/SHM sidecars.
8. Atomically replace the live SQLite file.
9. Verify integrity and schema on the restored live database.
10. If post-replacement verification fails, atomically restore the verified rollback backup.

There is intentionally no HTTP endpoint for restore activation. If the control plane is still running, the CLI fails because it cannot acquire the exclusive database lock.

PostgreSQL restore activation remains unsupported.

## Release 22 — One-shot restore activation

Successful staged SQLite restore candidates are now one-shot.

After the restored live database passes integrity and schema verification:

- the candidate manifest is atomically marked `activation_state=activated`;
- `activated_at` and the verified rollback backup id are persisted;
- a separate activation receipt is written with only structured safe metadata;
- any later attempt to activate the same candidate is rejected before database mutation.

If activation fails and the previous live database is restored successfully, the candidate remains staged and may be retried.

Activation receipts contain only:

```text
candidate_id
source_backup_id
rollback_backup_id
activated_at
schema_version
sha256
```

No credentials, paths, DSNs, authorization headers or arbitrary request payloads are stored.

## Release 23 — Restore activation history

The existing backups dashboard now exposes successful offline restore activations as read-only history.

History is derived only from Release 22 activation receipts and contains:

```text
candidate_id
source_backup_id
rollback_backup_id
activated_at
schema_version
sha256
```

Malformed receipts are ignored. No paths, DSNs, credentials, tokens or arbitrary payloads are exposed.

This is visibility only. Restore activation remains unavailable over HTTP and continues to require the offline CLI path, exact confirmation and exclusive maintenance lock.

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


## Dashboard observability — Release 1

The authenticated workspace remains available at `/dashboard`. Pair the browser
with a viewer or operator credential to read observability data; worker-only
credentials cannot read dashboard routes. The workspace provides **Vue générale**,
**Projets**, **Workers**, and **Activité**, while the existing repository +
instruction launch form remains available.

Project pages distinguish **Production actuelle** from **Projet estimé**. The
first is deterministic workflow progress weighted by task estimates. The second
is a versioned evidence-based estimate and is always accompanied by confidence
and evidence coverage; unavailable evidence stays unknown rather than being
invented.

API cost is an estimate only when an exact provider/model price is known for the
execution date. Token totals remain useful when cost cannot be calculated.
Production-OS-attributed commits are reported separately from total commits on
the repository default branch; the latter comes from GitHub snapshots and may be
marked degraded when cached data is used.

Workers publish live execution telemetry through
`POST /v1/jobs/{job_key}/telemetry`; this endpoint requires the owning worker
credential. Release 1 dashboard observability is read-only: pause, drain,
cancellation, retry and kick controls belong to Release 2.
````
