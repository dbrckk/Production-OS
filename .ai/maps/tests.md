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
test_adaptation_plan.py
test_adaptation.py
test_agent_benchmark.py
test_agent_plan.py
test_agent_planning_policy.py
test_api_auth.py
test_approvals_migrations.py
test_asset_forge.py
test_asymmetric_attestations.py
test_attestations.py
test_autonomous_admission.py
test_autonomous_projects.py
test_browser_computer.py
test_browser_loop.py
test_browser_worker_image.py
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
test_controller_daemon_deployment.py
test_controller_daemon.py
test_controller_leader.py
test_controller_managed_projects.py
test_cooperative_managed_projects.py
test_cooperative_specialist_e2e.py
test_dashboard_alerts.py
test_dashboard_api.py
test_dashboard_attention.py
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
test_dashboard_launch_readiness.py
test_dashboard_launch_ux.py
test_dashboard_launch.py
test_dashboard_maintenance.py
test_dashboard_mobile_stability.py
test_dashboard_observability_e2e.py
test_dashboard_playbook_api.py
test_dashboard_playbooks.py
test_dashboard_production_inbox_filters_ui.py
test_dashboard_production_inbox.py
test_dashboard_production_status.py
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
test_dynamic_agent_fanout.py
test_emergency_key_revocation.py
test_execution_feedback_trends.py
test_execution_optimizer_postgres.py
test_execution_optimizer.py
test_executor_worktree.py
test_fairness.py
test_fanout_learning.py
test_filesystem_lock.py
test_github_automerge.py
test_github_change_review.py
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
test_managed_dynamic_plan_outcome.py
test_managed_github_reconciliation.py
test_managed_project_outcome.py
test_managed_projects_http_v4.py
test_managed_projects_v4.py
test_mobile_worker_image.py
test_model_router.py
test_native_browser_worker_e2e.py
test_native_executor.py
test_observability.py
test_p6_hardening.py
test_persistent_agent_runtime.py
test_policy_budgets.py
test_policy_validation.py
test_portfolio_claim_api.py
test_portfolio_optimizer.py
test_postgres_backend.py
test_preemption.py
test_production_stack_e2e.py
test_project_memory.py
test_project_progress.py
test_provenance_signer.py
test_queue_audit_checkpoint.py
test_reconciliation_dispatch.py
test_regression_bisect.py
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
test_release32_one_tap_e2e.py
test_release33_auto_worker_recovery_e2e.py
test_release34_safe_running_recovery_e2e.py
test_release35_control_plane_restart_e2e.py
test_release36_worker_session_reconciliation_e2e.py
test_release41_live_production_tracking_e2e.py
test_release42_idempotent_launch_e2e.py
test_release43_safe_production_cancel_e2e.py
test_release44_one_tap_recovery_actions_e2e.py
test_release45_production_inbox_e2e.py
test_release51_one_tap_runner_e2e.py
test_release55_worker_operations.py
test_remote_worker_runner.py
test_remote_worker.py
test_render_start.py
test_repository_cache.py
test_result_cache.py
test_rollback_plan.py
test_runtime_contract.py
test_runtime_state.py
test_scheduler.py
test_scoring.py
test_secure_release_e2e.py
test_self_healing_heartbeat.py
test_signer_factory.py
test_signers.py
test_skill_memory.py
test_source_tree.py
test_specialist_job_preferences.py
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
test_worker_compose_deployment.py
test_workers.py
test_workflow_api.py
test_workflow_cache.py
test_workflow_change_impact.py
test_workflow_engine.py
test_workflow_postgres.py
test_workflow_splitting.py
test_worktree_contract.py
```

# Files

## File: test_adaptation_plan.py
```python
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
```

## File: test_adaptation.py
```python
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
```

## File: test_agent_benchmark.py
```python
def _build(tmp_path)
⋮----
backend = SQLiteBackend(tmp_path / "benchmark.sqlite")
queue = SQLiteJobQueue(backend)
⋮----
def _execution_job(job, *, attempt=1)
⋮----
def test_benchmark_reads_real_workflow_execution_history(tmp_path)
⋮----
workflow = engine.create(
code_job = engine.dispatch_ready(workflow["id"], limit=1)[0]
⋮----
current = engine.get(workflow["id"])
validate_task = next(
validate_job = engine.queue.get(validate_task["claimed_job_key"])
⋮----
row = AutonomousBenchmark(backend).workflow(workflow["id"])
⋮----
def test_benchmark_counts_retry_failures_and_operator_controls(tmp_path)
⋮----
first = engine.dispatch_ready(workflow["id"], limit=1)[0]
⋮----
retry_task = next(
retry_job = queue.get(retry_task["claimed_job_key"])
⋮----
def test_benchmark_report_aggregates_without_inventing_unknown_cost(tmp_path)
⋮----
successful = engine.create(
⋮----
failed = engine.create(
⋮----
report = AutonomousBenchmark(backend).report([
⋮----
def test_compare_reports_returns_metric_deltas_without_declaring_winner()
⋮----
candidate = {
baseline = {
⋮----
comparison = compare_reports(candidate, baseline)
⋮----
def test_agent_benchmark_cli_parses_multiple_workflows_and_baseline()
⋮----
args = _parse_args([
⋮----
def test_benchmark_records_dynamic_planner_policy_and_actual_fanout(tmp_path)
⋮----
payload = row.to_dict()
⋮----
def test_benchmark_report_aggregates_planner_policy_observability(tmp_path)
⋮----
ids = []
⋮----
report = AutonomousBenchmark(backend).report(ids)
```

## File: test_agent_plan.py
```python
def test_agent_plan_accepts_bounded_ordered_dependency_graph()
⋮----
tasks = validate_agent_plan(
⋮----
def test_agent_plan_rejects_budget_overflow()
⋮----
def test_agent_plan_rejects_too_many_agents()
⋮----
def test_agent_plan_rejects_unsafe_graph_shapes(payload, match)
⋮----
@pytest.mark.parametrize("token_budget", [True, False, 1.0, 1.9, "2"])
def test_agent_plan_rejects_non_integer_token_budget_types(token_budget)
⋮----
def test_agent_plan_rejects_supplied_non_list_collection_values(field, value)
⋮----
task = {
⋮----
def test_agent_plan_allows_null_optional_collections_as_empty()
```

## File: test_agent_planning_policy.py
```python
def _build(tmp_path)
⋮----
backend = SQLiteBackend(tmp_path / "planning-policy.sqlite")
queue = SQLiteJobQueue(backend)
engine = WorkflowEngine(backend, queue)
⋮----
def _completed_workflow(engine, repository: str, *, succeeded: bool)
⋮----
workflow = engine.create(
⋮----
def test_planning_policy_keeps_default_without_enough_history(tmp_path)
⋮----
policy = planning_policy_for_repository(
⋮----
def test_planning_policy_reduces_fanout_for_risky_history(tmp_path)
⋮----
def test_planning_policy_uses_moderate_fanout_for_mixed_history(tmp_path)
⋮----
def test_managed_project_embeds_evidence_policy_in_planner_contract(tmp_path)
⋮----
managed = ManagedProjectService(engine)
specs = managed._cooperative_workflow_specs(
⋮----
planner = specs[0]
config = planner.payload["dynamic_agent_planner"]
handoff = planner.payload["handoff"]
⋮----
def test_planning_policy_is_repository_scoped(tmp_path)
⋮----
risky = planning_policy_for_repository(backend, "owner/risky")
strong = planning_policy_for_repository(backend, "owner/strong")
```

## File: test_api_auth.py
```python
def test_token_authorizer_roles()
⋮----
auth=TokenAuthorizer([
principal=auth.authenticate("secret")
```

## File: test_approvals_migrations.py
```python
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
```

## File: test_asset_forge.py
```python
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
```

## File: test_asymmetric_attestations.py
```python
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
```

## File: test_attestations.py
```python
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
```

## File: test_autonomous_admission.py
```python
def _request(**overrides)
⋮----
values = {
⋮----
state = state or RuntimeState(tmp_path / "runtime.json")
⋮----
def test_managed_admission_uses_same_runtime_key_as_legacy_dispatch(tmp_path)
⋮----
decision = _evaluate(tmp_path)
⋮----
def test_managed_admission_rate_limit_check_is_read_only_until_commit(tmp_path)
⋮----
path = tmp_path / "rate.json"
store = RateLimitStore(path)
⋮----
decision = _evaluate(tmp_path, rate_limits=store)
⋮----
def test_autonomous_admission_blocks_emergency_stop(tmp_path)
⋮----
stop = tmp_path / "stop.json"
⋮----
def test_autonomous_admission_blocks_policy(tmp_path)
⋮----
policies = PolicySet({
⋮----
def test_autonomous_admission_blocks_quarantine(tmp_path)
⋮----
store = QuarantineStore(tmp_path / "quarantine.json")
⋮----
def test_autonomous_admission_blocks_repository_budget(tmp_path)
⋮----
ledger = BudgetLedger(tmp_path / "budget.json")
⋮----
def test_autonomous_admission_blocks_portfolio_budget(tmp_path)
⋮----
def test_autonomous_admission_requires_human_approval(tmp_path)
⋮----
def test_autonomous_admission_accepts_same_canonical_approval_key(tmp_path)
⋮----
approvals = ApprovalStore(tmp_path / "approvals.json")
⋮----
decision = _evaluate(
⋮----
def test_autonomous_admission_blocks_repository_rate_limit(tmp_path)
⋮----
store = RateLimitStore(tmp_path / "rate.json")
⋮----
request = _request(repo_rate_limit=1)
⋮----
def test_autonomous_admission_blocks_no_capable_worker(tmp_path)
⋮----
workers = WorkerRegistry(tmp_path / "workers.json")
⋮----
request = _request(required_capabilities=("android",))
⋮----
def test_autonomous_admission_blocks_active_lease(tmp_path)
⋮----
state = RuntimeState(tmp_path / "runtime.json")
⋮----
def test_autonomous_admission_blocks_cooldown(tmp_path)
⋮----
record = state.get("owner/repo", "Improve login tests")
⋮----
@pytest.mark.parametrize("status", ["circuit-open", "succeeded"])
def test_autonomous_admission_blocks_terminal_runtime_state(tmp_path, status)
```

## File: test_autonomous_projects.py
```python
def _fingerprint(**overrides)
⋮----
payload = {
⋮----
def test_autonomous_project_id_is_deterministic()
⋮----
first = autonomous_project_id(
second = autonomous_project_id(
⋮----
def test_action_fingerprint_normalizes_evidence_order()
⋮----
first = _fingerprint(
second = _fingerprint(
⋮----
def test_action_fingerprint_changes_on_task_change()
⋮----
def test_action_fingerprint_changes_on_acceptance_change()
⋮----
def test_action_fingerprint_changes_on_trigger_evidence_change()
⋮----
def test_action_fingerprint_excludes_score_and_lane_metadata()
⋮----
baseline = _fingerprint()
⋮----
first = autonomous_action_fingerprint(
second = autonomous_action_fingerprint(
⋮----
def test_autonomous_project_id_rejects_invalid_repository(repository)
⋮----
def _service(tmp_path)
⋮----
backend = SQLiteBackend(tmp_path / "autonomous.sqlite")
⋮----
def _request(**overrides)
⋮----
fingerprint = _fingerprint(
values = {
⋮----
def test_launch_creates_managed_project_once(tmp_path)
⋮----
managed = _service(tmp_path)
⋮----
launch = launch_autonomous_project(managed, _request())
⋮----
def test_repeated_identical_launch_reuses_existing_project(tmp_path)
⋮----
first = launch_autonomous_project(managed, _request())
⋮----
second = launch_autonomous_project(managed, _request())
⋮----
def test_reuse_does_not_create_second_workflow(tmp_path)
⋮----
first_workflow = first.project["current_workflow_id"]
⋮----
workflow_count = db.execute(
⋮----
def test_successful_terminal_identical_project_is_skipped(tmp_path)
⋮----
def test_changed_trigger_evidence_creates_new_project(tmp_path)
⋮----
first = launch_autonomous_project(
⋮----
second = launch_autonomous_project(
⋮----
def test_partial_initialization_retry_uses_same_project_id(tmp_path, monkeypatch)
⋮----
request = _request()
seen = []
real_create = managed.create
⋮----
def flaky_create(**kwargs)
⋮----
second = launch_autonomous_project(managed, request)
```

## File: test_browser_loop.py
```python
def _config(**overrides)
⋮----
payload = {
⋮----
def _turn(turn_id, actions)
⋮----
def test_browser_loop_executes_multiple_turns_with_fixed_host_policy(tmp_path)
⋮----
seen = []
⋮----
def fake_execute(plan, **kwargs)
⋮----
input_stream = io.StringIO(
output_stream = io.StringIO()
summary = run_browser_turn_loop(
⋮----
rows = [
⋮----
def test_browser_loop_rejects_turn_that_expands_navigation_host(tmp_path)
⋮----
calls = []
⋮----
def fake_execute(plan, **_kwargs)
⋮----
def test_browser_loop_stops_after_failed_turn_to_preserve_recovery_fence(tmp_path)
⋮----
def fail_execute(plan, **kwargs)
⋮----
def test_browser_loop_requires_durable_paths_when_persistent(tmp_path)
⋮----
def test_browser_loop_enforces_max_turns(tmp_path)
⋮----
def fake_execute(_plan, **_kwargs)
⋮----
def test_turn_checkpoint_path_is_stable_and_turn_scoped(tmp_path)
⋮----
base = tmp_path / "browser-checkpoint.json"
first = _turn_checkpoint_path(base, "turn-a")
again = _turn_checkpoint_path(base, "turn-a")
other = _turn_checkpoint_path(base, "turn-b")
⋮----
def test_browser_loop_config_reuses_browser_safety_validation(payload, match)
⋮----
def test_browser_loop_cli_parses_jsonl_runtime_paths()
⋮----
args = _parse_args([
⋮----
def test_completed_turn_is_idempotently_deduplicated(tmp_path)
⋮----
config = _config()
checkpoint = tmp_path / "checkpoint.json"
turn = json.loads(
⋮----
manifest_path = _turn_manifest_path(checkpoint, "stable-turn")
⋮----
def must_not_execute(_plan, **_kwargs)
⋮----
output = io.StringIO()
⋮----
row = json.loads(output.getvalue().splitlines()[0])
⋮----
def test_turn_id_cannot_be_rebound_to_different_plan(tmp_path)
⋮----
first = json.loads(
second = json.loads(
⋮----
manifest_path = _turn_manifest_path(checkpoint, "same-turn")
⋮----
def test_inflight_turn_with_tampered_checkpoint_fails_closed(tmp_path)
⋮----
manifest_path = _turn_manifest_path(checkpoint, "uncertain-turn")
⋮----
turn_checkpoint = _turn_checkpoint_path(checkpoint, "uncertain-turn")
⋮----
def test_successful_turn_persists_completed_manifest(tmp_path)
⋮----
turn_id = "complete-me"
⋮----
manifest = _read_turn_manifest(
⋮----
def test_turn_manifest_does_not_store_turn_id_or_fill_secret(tmp_path)
⋮----
turn_id = "private-turn-id"
⋮----
manifest_path = _turn_manifest_path(checkpoint, turn_id)
serialized = manifest_path.read_text(encoding="utf-8")
⋮----
def test_completed_manifest_is_committed_before_executor_returns(tmp_path)
⋮----
turn = _turn(
⋮----
def crash_after_durable_completion(_plan, **kwargs)
⋮----
on_complete = kwargs["on_complete"]
⋮----
first_output = io.StringIO()
first = run_browser_turn_loop(
⋮----
second_output = io.StringIO()
second = run_browser_turn_loop(
⋮----
row = json.loads(second_output.getvalue().splitlines()[0])
⋮----
def test_invalid_existing_turn_manifest_fails_closed_without_rebinding(tmp_path)
⋮----
turn_id = "bound-turn"
⋮----
def test_browser_loop_stops_before_next_turn_when_cancelled(tmp_path)
⋮----
cancel = threading.Event()
```

## File: test_browser_worker_image.py
```python
def test_browser_worker_image_pins_playwright_and_installs_chromium()
⋮----
payload = Path("Dockerfile.browser-worker").read_text(encoding="utf-8")
⋮----
def test_browser_worker_image_includes_git_for_repository_materialization()
```

## File: test_builder_identity_validation.py
```python
def policy(builder)
⋮----
def test_builder_identity_rejects_naive_not_before()
⋮----
def test_builder_identity_rejects_naive_not_after()
⋮----
def test_builder_identity_rejects_invalid_timestamp()
⋮----
def test_builder_identity_rejects_inverted_validity_window()
```

## File: test_builder_identity.py
```python
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
```

## File: test_builder_trust_rotation.py
```python
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
```

## File: test_callgraph_versioning_feedback.py
```python
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
```

## File: test_capabilities_graph.py
```python
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
```

## File: test_change_impact.py
```python
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
```

## File: test_claims_delivery.py
```python
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
```

## File: test_classification_history_reuse.py
```python
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
```

## File: test_cli.py
```python
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
⋮----
def test_remote_worker_run_requires_token_from_environment(monkeypatch, capsys)
⋮----
installed = {}
restored = []
old_handlers = {
⋮----
def fake_signal(signum, handler)
⋮----
runners = []
⋮----
class FakeRunner
⋮----
def __init__(self, *_args, **_kwargs)
⋮----
def request_stop(self)
⋮----
def run(self, **_kwargs)
⋮----
class FakeClient
```

## File: test_compatibility_validation.py
```python
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
```

## File: test_components.py
```python
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
```

## File: test_control_plane_pr_impact.py
```python
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
```

## File: test_control_plane_release.py
```python
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
```

## File: test_control_plane_webhook.py
```python
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
```

## File: test_control_plane.py
```python
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
```

## File: test_controller_asset_capabilities.py
```python
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
```

## File: test_controller_daemon_deployment.py
```python
def test_controller_daemon_compose_service_is_resilient_and_persistent()
⋮----
payload = Path("compose.yaml").read_text(encoding="utf-8")
⋮----
def test_controller_deployment_defaults_to_managed_execution()
```

## File: test_controller_daemon.py
```python
class FakeStopEvent
⋮----
def __init__(self, stop_after_waits: int)
⋮----
def is_set(self) -> bool
⋮----
def wait(self, seconds: int) -> bool
⋮----
def test_controller_daemon_runs_until_cooperative_stop(monkeypatch)
⋮----
calls = {"count":0}
⋮----
def fake_cycle(**_kwargs)
⋮----
stop = FakeStopEvent(3)
⋮----
summary = controller.run_controller_daemon(
⋮----
def test_controller_daemon_retries_failures_with_bounded_backoff(monkeypatch)
⋮----
attempts = {"count":0}
recorded = []
⋮----
def flaky_cycle(**_kwargs)
⋮----
def test_bounded_controller_behavior_is_unchanged(monkeypatch)
⋮----
results = controller.run_controller(
⋮----
def test_controller_cli_exposes_daemon_controls()
⋮----
args = _parse_args([
```

## File: test_controller_leader.py
```python
def test_filesystem_controller_leader_lock_is_exclusive_and_releasable(tmp_path)
⋮----
path = tmp_path / "controller.lock"
first = leader.FilesystemControllerLeaderLock(path)
second = leader.FilesystemControllerLeaderLock(path)
⋮----
def test_controller_leader_factory_uses_durable_file_for_sqlite(tmp_path)
⋮----
database = tmp_path / "production.db"
lock = leader.controller_leader_lock(
⋮----
def test_controller_leader_factory_falls_back_to_runtime_state(tmp_path)
⋮----
runtime = tmp_path / "runtime.json"
⋮----
def test_postgres_controller_leader_lock_holds_session_advisory_lock(monkeypatch)
⋮----
calls = []
⋮----
class Result
⋮----
def __init__(self, row)
⋮----
def fetchone(self)
⋮----
class Connection
⋮----
def __init__(self)
⋮----
def execute(self, sql, params)
⋮----
def close(self)
⋮----
connection = Connection()
⋮----
class Backend
⋮----
def __init__(self, dsn)
⋮----
def connect(self)
⋮----
lock = leader.PostgresControllerLeaderLock(
⋮----
def test_postgres_controller_leader_lock_rejects_second_leader(monkeypatch)
⋮----
def execute(self, _sql, _params)
⋮----
def __init__(self, _dsn)
```

## File: test_controller_managed_projects.py
```python
def _cycle_kwargs(tmp_path)
⋮----
def test_controller_defaults_execution_mode_to_managed_after_parity()
⋮----
signature = inspect.signature(run_control_cycle)
⋮----
def test_controller_cli_defaults_to_managed_execution()
⋮----
args = _parse_args([
⋮----
def test_explicit_legacy_mode_remains_supported()
⋮----
def test_controller_cli_accepts_managed_execution_mode()
⋮----
def test_controller_managed_mode_requires_database_path(tmp_path)
⋮----
def test_controller_rejects_unknown_execution_mode(tmp_path)
⋮----
def test_controller_rejects_nonpositive_project_token_budget(tmp_path)
⋮----
class _FakeGitHub
⋮----
def list_repositories(self, _owner)
⋮----
def collect_evidence(self, _repo)
⋮----
action = SimpleNamespace(
assessment = SimpleNamespace(
⋮----
database = tmp_path / "production.sqlite"
backend = open_backend(str(database))
registry = worker_registry_for(backend)
⋮----
kwargs = {
⋮----
result = run_control_cycle(**kwargs)
⋮----
service = ManagedProjectService(
projects = service.list()
⋮----
first = run_control_cycle(**kwargs)
second = run_control_cycle(**kwargs)
⋮----
def test_managed_mode_never_calls_dispatch_handoff(tmp_path, monkeypatch)
⋮----
calls = []
⋮----
def forbidden(*_args, **_kwargs)
⋮----
legacy_calls = []
⋮----
def test_legacy_mode_still_calls_dispatch_handoff(tmp_path, monkeypatch)
⋮----
class _Dispatch
⋮----
def to_dict(self)
⋮----
def fake_dispatch(*_args, **_kwargs)
⋮----
def _project_service(backend)
⋮----
def _with_resource_request(monkeypatch, *, tokens=25)
⋮----
original = controller._handoff_for_action
⋮----
def wrapped(*args, **kwargs)
⋮----
handoff = original(*args, **kwargs)
⋮----
path = tmp_path / "emergency.json"
⋮----
path = tmp_path / "policy.json"
⋮----
policy = tmp_path / "policy.json"
⋮----
path = tmp_path / "rate.json"
store = RateLimitStore(path)
⋮----
decision = store.check_and_record(
⋮----
state = runtime_state_for(backend)
⋮----
budget_path = tmp_path / "budget.json"
rate_path = tmp_path / "rate.json"
⋮----
project_id = first["managed_projects"][0]["project_id"]
⋮----
ledger = BudgetLedger(budget_path)
⋮----
rate = RateLimitStore(rate_path)
⋮----
real_commit = controller.commit_autonomous_admission
calls = {"count":0}
⋮----
def crash_once(*args, **kwargs)
⋮----
projects = _project_service(backend).list()
⋮----
first_project = first["managed_projects"][0]
first_workflow = first_project["current_workflow_id"]
⋮----
backend = open_backend(kwargs["database_path"])
⋮----
first_id = first["managed_projects"][0]["project_id"]
⋮----
same = run_control_cycle(**kwargs)
⋮----
changed = run_control_cycle(**kwargs2)
⋮----
ids = {row["id"] for row in _project_service(backend2).list()}
```

## File: test_cooperative_managed_projects.py
```python
def service(tmp_path)
⋮----
backend = SQLiteBackend(tmp_path / "cooperative.sqlite")
⋮----
def _planner_config(managed, *, goal, instruction=None, budget=1000)
⋮----
tasks = managed._cooperative_workflow_specs(
⋮----
def test_cooperative_workflow_starts_with_bounded_adaptive_planner(tmp_path)
⋮----
managed = service(tmp_path)
planner = _planner_config(
⋮----
config = planner.payload["dynamic_agent_planner"]
fallback = config["fallback_plan"]
⋮----
def test_cooperative_browser_goal_puts_browser_validation_after_review(tmp_path)
⋮----
continuation = planner.payload["dynamic_agent_planner"][
⋮----
browser = continuation[-1]
⋮----
def test_native_mobile_goal_puts_emulator_validation_after_review(tmp_path)
⋮----
planner = _planner_config(managed, goal=goal)
⋮----
mobile = continuation[-1]
⋮----
def test_create_cooperative_project_queues_only_planner_initially(tmp_path)
⋮----
project = managed.create(
⋮----
workflow = managed.workflows.get(project["current_workflow_id"])
⋮----
def test_planner_fallback_expands_code_tests_and_delivery_chain(tmp_path)
⋮----
workflow_id = project["current_workflow_id"]
⋮----
expanded = managed.workflows.record_result(
by_id = {task["task_id"]:task for task in expanded["tasks"]}
⋮----
def test_cooperative_outcome_uses_deepest_stage_and_aggregates_delivery_evidence()
⋮----
workflow = {
⋮----
outcome = _outcome_from_workflow(workflow)
⋮----
def test_cooperative_workflow_rejects_budget_smaller_than_stage_count(tmp_path)
⋮----
def test_retest_preserves_cooperative_dynamic_planner_mode(tmp_path)
⋮----
completed = managed.get(project["project_id"])
⋮----
follow_up = managed.request_verification(
```

## File: test_cooperative_specialist_e2e.py
```python
def build(tmp_path)
⋮----
backend = SQLiteBackend(tmp_path / "cooperative-specialists.sqlite")
queue = SQLiteJobQueue(backend)
workflows = WorkflowEngine(backend, queue)
managed = ManagedProjectService(workflows)
⋮----
def _task(workflow, task_id)
⋮----
@pytest.mark.e2e
def test_cooperative_project_routes_planner_fanout_then_specialists(tmp_path)
⋮----
project = managed.create(
workflow_id = project["current_workflow_id"]
⋮----
workflow = workflows.get(workflow_id)
planner = _task(workflow, "planner")
⋮----
planner_job = queue.claim_next(
⋮----
code_task = _task(workflow, "planner.agent.code")
tests_task = _task(workflow, "planner.agent.tests")
⋮----
code_job = queue.claim_next(
tests_job = queue.claim_next(
⋮----
code_branch = code_job["payload"]["handoff"]["isolation"]["branch"]
tests_branch = tests_job["payload"]["handoff"]["isolation"]["branch"]
⋮----
integration = _task(workflows.get(workflow_id), "integration")
⋮----
integration_job = queue.claim_next(
⋮----
upstream = integration_job["payload"]["handoff"]["upstream_context"]
⋮----
validation = _task(workflows.get(workflow_id), "validation")
⋮----
debug_job = queue.claim_next(
⋮----
review = _task(workflows.get(workflow_id), "review")
⋮----
review_job = queue.claim_next(
⋮----
ui = _task(workflows.get(workflow_id), "ui-validation")
⋮----
browser_job = queue.claim_next(
⋮----
completed = workflows.get(workflow_id)
```

## File: test_dashboard_alerts.py
```python
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
```

## File: test_dashboard_api.py
```python
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
⋮----
project = payload["project"]
launch = payload["launch"]
⋮----
persisted = control.managed_projects.get(project["project_id"])
⋮----
def test_attention_feed_is_viewer_visible_and_worker_forbidden(running_control_plane)
⋮----
project_id = created["project"]["project_id"]
⋮----
request_id = "android-retry-20260925-001"
body = {
⋮----
def test_one_tap_launch_rejects_invalid_request_id(running_control_plane)
⋮----
project = control.managed_projects.create(
project_id = project["project_id"]
⋮----
audit = control.dashboard_store.control_audit_events(limit=10)
⋮----
def test_production_inbox_rejects_invalid_sort_over_http(running_control_plane)
```

## File: test_dashboard_attention.py
```python
class ManagedProjects
⋮----
def __init__(self, rows)
⋮----
def list(self, *, limit=100)
⋮----
def test_attention_prioritizes_failures_reviews_blocked_jobs_and_incidents()
⋮----
managed = [
control = SimpleNamespace(
service = DashboardService(control)
⋮----
payload = service.attention(limit=50)
⋮----
kinds = [item["kind"] for item in payload["items"]]
⋮----
incident = next(item for item in payload["items"] if item["kind"] == "incident")
⋮----
failed = next(item for item in payload["items"] if item["kind"] == "validation_failed")
⋮----
review = next(item for item in payload["items"] if item["kind"] == "project_review")
⋮----
def test_attention_limit_is_bounded_and_completed_items_are_informational()
⋮----
payload = service.attention(limit=2)
⋮----
def test_attention_caps_blocked_job_cards_but_preserves_total_count()
⋮----
blocked = [item for item in payload["items"] if item["kind"] == "blocked_job"]
⋮----
def test_attention_managed_projects_open_unified_productions_surface()
⋮----
payload = service.attention(limit=20)
project_items = [
```

## File: test_dashboard_backup_api.py
```python
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
⋮----
backup_id = "20260925T120000Z-aaaaaaaaaaaa"
⋮----
storage = payload["storage"]
⋮----
stale = backup_dir / ".stale.sqlite.tmp"
⋮----
old = time.time() - 90000
⋮----
prune_rows = [
⋮----
protected = [
⋮----
filesystem = payload["storage"]["filesystem"]
⋮----
encoded = json.dumps(filesystem).lower()
⋮----
now = datetime.now(timezone.utc)
rows = [
⋮----
preview = catalog["storage"]["retention_preview"]
⋮----
fingerprint = preview["candidate_fingerprint"]
⋮----
old_id = rows[-1][0]
```

## File: test_dashboard_backups.py
```python
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
⋮----
backup_id = "20260925T120000Z-aaaaaaaaaaaa"
candidate_id = "20260925T130000Z-bbbbbbbbbbbb"
files = {
⋮----
inventory = backup_storage_inventory(backend)
⋮----
encoded = json.dumps(inventory).lower()
⋮----
backup_dir = tmp_path / "missing-backups"
⋮----
inventory = backup_storage_inventory(_FakePostgres())
⋮----
old_temp = backup_dir / ".old.sqlite.tmp"
fresh_temp = backup_dir / ".fresh.sqlite.tmp"
⋮----
old = time.time() - 90000
⋮----
stale = backup_dir / ".stale.sqlite.tmp"
fresh = backup_dir / ".fresh.sqlite.tmp"
backup = backup_dir / "20260925T120000Z-aaaaaaaaaaaa.sqlite"
candidate = backup_dir / "restore-20260925T130000Z-bbbbbbbbbbbb.sqlite"
receipt = backup_dir / "restore-20260925T130000Z-bbbbbbbbbbbb.activation.json"
unknown = backup_dir / "notes.txt"
⋮----
result = prune_stale_backup_temps(
⋮----
backup_dir = tmp_path / "nested" / "backups"
⋮----
filesystem = inventory["filesystem"]
⋮----
filesystem = backup_storage_inventory(backend)["filesystem"]
⋮----
filesystem = backup_storage_inventory(_FakePostgres())["filesystem"]
⋮----
class Stats
⋮----
f_frsize = 4096
f_bsize = 4096
f_blocks = 1000
f_bfree = 100
f_bavail = 40
⋮----
def fail(_)
⋮----
path_type = type(backup_dir)
original_iterdir = path_type.iterdir
⋮----
def failing_iterdir(path)
⋮----
now = datetime.now(timezone.utc)
samples = [
⋮----
invalid_id = "20260901T120000Z-000000000005"
⋮----
age = backup_storage_inventory(backend)["backup_age"]
⋮----
rows = [
⋮----
invalid_id = "20260717T120000Z-100000000006"
⋮----
protected_id = rows[-1][0]
candidate_id = "20260925T120000Z-200000000001"
rollback_id = "20260925T120000Z-200000000002"
⋮----
preview = backup_storage_inventory(backend)["retention_preview"]
⋮----
protected_old = rows[-1][0]
receipt_candidate = "20260925T120000Z-400000000001"
rollback_id = "20260925T120000Z-400000000002"
⋮----
candidate_id = rows[-2][0]
⋮----
result = prune_expired_verified_backups(
```

## File: test_dashboard_control_api.py
```python
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
```

## File: test_dashboard_control_audit.py
```python
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
def test_release17_schema_is_v16_and_contains_managed_project_tables(tmp_path)
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
```

## File: test_dashboard_control_e2e.py
```python
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
```

## File: test_dashboard_control.py
```python
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
```

## File: test_dashboard_github.py
```python
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
```

## File: test_dashboard_health.py
```python
def test_health_is_healthy_without_operational_problems()
⋮----
result = derive_control_health({
⋮----
def test_queue_without_worker_degrades_health()
⋮----
def test_stale_busy_worker_and_running_execution_are_explained()
⋮----
codes = {item["code"] for item in result["reasons"]}
⋮----
def test_backup_filesystem_pressure_degrades_health_with_severity()
⋮----
warning = derive_control_health({
⋮----
critical = derive_control_health({
```

## File: test_dashboard_incident_signals.py
```python
def test_health_signals_expand_to_targeted_incidents()
⋮----
signals = signals_from_health({
⋮----
keys = {dedupe_key(item) for item in signals}
```

## File: test_dashboard_incidents.py
```python
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
```

## File: test_dashboard_launch_readiness.py
```python
def test_launch_readiness_distinguishes_immediate_execution_from_safe_queue(tmp_path)
⋮----
control = ControlPlane(str(tmp_path / "readiness.sqlite"))
service = control.dashboard
⋮----
queued = service.launch_readiness("dbrckk/example")
⋮----
immediate = service.launch_readiness("dbrckk/example")
⋮----
def test_launch_readiness_does_not_count_paused_or_saturated_workers(tmp_path)
⋮----
control = ControlPlane(str(tmp_path / "readiness-workers.sqlite"))
⋮----
result = service.launch_readiness("dbrckk/example")
⋮----
def test_launch_readiness_validates_repository_shape(tmp_path)
⋮----
control = ControlPlane(str(tmp_path / "readiness-invalid.sqlite"))
```

## File: test_dashboard_launch_ux.py
```python
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
def _post(url, token, payload)
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
⋮----
control = ControlPlane(str(tmp_path / "auto-wake.sqlite"), authorizer=_auth())
⋮----
wakes = []
⋮----
audit = control.dashboard_store.control_audit_events(limit=10)
⋮----
control = ControlPlane(str(tmp_path / "no-auto-wake.sqlite"), authorizer=_auth())
⋮----
control = ControlPlane(str(tmp_path / "wake-saturated.sqlite"), authorizer=_auth())
worker = control.workers.register("worker-a", ["python"], 1)
⋮----
control = ControlPlane(str(tmp_path / "wake-paused.sqlite"), authorizer=_auth())
⋮----
control = ControlPlane(str(tmp_path / "wake-offline.sqlite"), authorizer=_auth())
⋮----
def test_automatic_worker_wake_cooldown_blocks_duplicate_kick(tmp_path)
⋮----
control = ControlPlane(str(tmp_path / "wake-cooldown.sqlite"), authorizer=_auth())
⋮----
control = ControlPlane(str(tmp_path / "wake-dedupe.sqlite"), authorizer=_auth())
⋮----
def test_automatic_worker_wake_cooldown_allows_retry_after_failure(tmp_path)
⋮----
control = ControlPlane(str(tmp_path / "wake-failed-retry.sqlite"), authorizer=_auth())
```

## File: test_dashboard_launch.py
```python
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
⋮----
def test_dashboard_launch_surfaces_automatic_worker_wake_state()
⋮----
launch_start = DASHBOARD_HTML.index("async function launchWorkflow")
launch_end = DASHBOARD_HTML.index("async function refreshDashboard", launch_start)
launch_body = DASHBOARD_HTML[launch_start:launch_end]
```

## File: test_dashboard_maintenance.py
```python
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
```

## File: test_dashboard_mobile_stability.py
```python
def test_dashboard_css_uses_defined_border_token_for_cooperative_stages()
⋮----
def test_dashboard_navigation_matches_eight_destinations_without_overflow_prone_six_column_grid()
⋮----
def test_dashboard_exposes_visible_keyboard_focus_and_reduced_motion_contracts()
⋮----
def test_dashboard_long_content_wraps_instead_of_forcing_horizontal_scroll()
```

## File: test_dashboard_observability_e2e.py
```python
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
```

## File: test_dashboard_playbook_api.py
```python
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
```

## File: test_dashboard_playbooks.py
```python
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
```

## File: test_dashboard_production_inbox_filters_ui.py
```python
def test_production_inbox_exposes_mobile_filter_tabs_and_counts()
⋮----
def test_production_inbox_requests_selected_server_filter()
⋮----
def test_production_inbox_filter_does_not_duplicate_mutation_contracts()
⋮----
def test_production_inbox_exposes_search_sort_and_shareable_url_state()
⋮----
def test_production_inbox_requests_server_search_and_sort()
⋮----
def test_production_inbox_has_shareable_inline_detail_panel()
⋮----
def test_production_inbox_open_stays_in_productions_and_reuses_safe_actions()
⋮----
start = DASHBOARD_HTML.index("function productionInboxActions")
end = DASHBOARD_HTML.index("function updateDashboardUrl", start)
body = DASHBOARD_HTML[start:end]
⋮----
def test_production_inbox_target_restores_detail_even_outside_visible_list()
⋮----
start = DASHBOARD_HTML.index("async function loadProductionInbox")
end = DASHBOARD_HTML.index("async function loadAttention", start)
⋮----
def test_inline_production_detail_supports_custom_follow_up_instruction()
⋮----
def test_custom_follow_up_refreshes_unified_operator_surfaces()
⋮----
start = DASHBOARD_HTML.index("async function submitProductionInstruction")
end = DASHBOARD_HTML.index("function productionInboxActions", start)
```

## File: test_dashboard_production_inbox.py
```python
def _production_fixture(tmp_path)
⋮----
control = ControlPlane(str(tmp_path / "production-inbox.sqlite"))
queued = control.managed_projects.create(
review = control.managed_projects.create(
⋮----
attention = control.managed_projects.create(
cancelled = control.dashboard.cancel_production(
⋮----
done = control.managed_projects.create(
⋮----
def test_production_inbox_aggregates_live_review_attention_and_done(tmp_path)
⋮----
payload = control.dashboard.production_inbox(limit=50)
⋮----
by_id = {item["project_id"]:item for item in payload["items"]}
⋮----
summary = payload["summary"]
⋮----
def test_production_inbox_filters_server_side_without_changing_totals(tmp_path)
⋮----
active = control.dashboard.production_inbox(limit=50, category="active")
⋮----
review_payload = control.dashboard.production_inbox(limit=50, category="review")
⋮----
problems = control.dashboard.production_inbox(limit=50, category="problems")
⋮----
completed = control.dashboard.production_inbox(limit=50, category="completed")
⋮----
def test_production_inbox_rejects_unknown_filter(tmp_path)
⋮----
control = ControlPlane(str(tmp_path / "production-inbox-filter.sqlite"))
⋮----
def test_production_inbox_orders_operator_decisions_before_live_and_done(tmp_path)
⋮----
phases = [row["runtime"]["phase"] for row in payload["items"]]
⋮----
def test_production_inbox_respects_response_limit_after_priority_sort(tmp_path)
⋮----
control = ControlPlane(str(tmp_path / "production-inbox-limit.sqlite"))
⋮----
payload = control.dashboard.production_inbox(limit=2)
⋮----
def test_production_inbox_orders_recent_activity_first_within_same_priority(tmp_path)
⋮----
control = ControlPlane(str(tmp_path / "production-inbox-recency.sqlite"))
older = control.managed_projects.create(
newer = control.managed_projects.create(
⋮----
payload = control.dashboard.production_inbox(limit=50, category="active")
⋮----
def test_production_inbox_search_matches_repository_goal_and_project_id(tmp_path)
⋮----
by_repository = control.dashboard.production_inbox(
⋮----
by_goal = control.dashboard.production_inbox(
⋮----
by_id = control.dashboard.production_inbox(
⋮----
def test_production_inbox_recent_sort_ignores_priority_but_keeps_filter(tmp_path)
⋮----
# Prime reconciliation first so timestamp edits below represent the
# externally visible project activity order rather than status migration.
⋮----
timestamps = {
⋮----
recent = control.dashboard.production_inbox(limit=50, sort="recent")
⋮----
review_only = control.dashboard.production_inbox(
⋮----
def test_production_inbox_rejects_unknown_sort(tmp_path)
⋮----
control = ControlPlane(str(tmp_path / "production-inbox-sort.sqlite"))
```

## File: test_dashboard_production_status.py
```python
def test_production_status_tracks_queue_claim_ack_and_live_telemetry(tmp_path)
⋮----
control = ControlPlane(str(tmp_path / "live-status.sqlite"))
project = control.managed_projects.create(
project_id = project["project_id"]
⋮----
queued = control.dashboard.production_status(project_id)
⋮----
job = control.queue.claim_next("worker-a", capabilities=[])
⋮----
claimed = control.dashboard.production_status(project_id)
⋮----
acked = control.queue.ack(job["key"], "worker-a")
⋮----
running = control.dashboard.production_status(project_id)
⋮----
def test_production_status_validates_and_reports_missing_project(tmp_path)
⋮----
control = ControlPlane(str(tmp_path / "live-status-errors.sqlite"))
⋮----
def test_production_status_reports_cancelling_until_worker_acknowledges(tmp_path)
⋮----
control = ControlPlane(str(tmp_path / "cancel-status.sqlite"))
⋮----
result = control.dashboard.cancel_production(
⋮----
status = control.dashboard.production_status(project_id)
⋮----
cancelled = control.queue.cancel(job["key"], "worker-a")
⋮----
final = control.dashboard.production_status(project_id)
```

## File: test_dashboard_remediation_api.py
```python
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
```

## File: test_dashboard_remediation_history.py
```python
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
def test_sqlite_v14_database_is_migrated_additively_to_v16(tmp_path)
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
```

## File: test_dashboard_remediation_metrics.py
```python
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
```

## File: test_dashboard_retention_prune.py
```python
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
```

## File: test_dashboard_security.py
```python
def test_recursive_redaction_removes_sensitive_values()
⋮----
value = {
redacted = redact_log_value(value)
```

## File: test_dashboard_store_postgres.py
```python
DSN = os.getenv("PRODUCTION_OS_TEST_POSTGRES")
⋮----
pytestmark = pytest.mark.skipif(
⋮----
REQUIRED_EXECUTION_COLUMNS = {
⋮----
def test_postgres_schema_v16_has_managed_project_generation_tables()
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
```

## File: test_dashboard_store.py
```python
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
⋮----
def test_finish_execution_persists_primary_provider_and_aggregates_usage(tmp_path)
⋮----
store = _store(tmp_path)
⋮----
done = store.finish_execution(
⋮----
def test_finish_execution_top_level_usage_overrides_provider_summary(tmp_path)
⋮----
def test_finish_execution_does_not_invent_partial_cost_or_catalog(tmp_path)
```

## File: test_dashboard_ui_v3.py
```python
def test_dashboard_has_primary_views_and_clickable_entities()
⋮----
def test_polling_does_not_reload_or_replace_location()
⋮----
def test_dashboard_has_worker_and_project_detail_tabs()
⋮----
def test_dashboard_renders_native_mobile_validation_evidence()
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
⋮----
def test_backup_overview_renders_storage_inventory_read_only()
⋮----
def test_backup_temp_cleanup_ui_is_guarded_and_stale_only()
⋮----
def test_backup_overview_renders_filesystem_capacity_read_only()
⋮----
def test_backup_overview_renders_verified_backup_age_distribution()
⋮----
def test_backup_overview_renders_retention_preview_read_only()
⋮----
def test_backup_retention_cleanup_ui_requires_preview_fingerprint()
⋮----
def test_one_tap_production_is_primary_and_uses_server_managed_launch()
⋮----
launch_start = DASHBOARD_HTML.index("async function launchWorkflow")
launch_end = DASHBOARD_HTML.index("async function refreshDashboard", launch_start)
launch_body = DASHBOARD_HTML[launch_start:launch_end]
⋮----
def test_managed_technical_creation_options_are_collapsed_by_default()
⋮----
def test_managed_view_can_be_restored_from_navigation_query()
⋮----
def test_attention_center_is_default_mobile_view()
⋮----
def test_attention_center_uses_server_aggregated_feed_and_action_counts()
⋮----
def test_attention_items_navigate_to_existing_operational_views()
⋮----
def test_attention_center_exposes_contextual_server_actions()
⋮----
def test_attention_open_deep_links_to_exact_managed_project_or_job()
⋮----
def test_attention_feed_caps_blocked_job_cards_without_hiding_total()
⋮----
def test_attention_project_cards_accept_inline_follow_up_instruction()
⋮----
def test_completed_attention_items_remain_openable_for_inspection()
⋮----
load_start = DASHBOARD_HTML.index("async function loadAttention")
load_end = DASHBOARD_HTML.index("async function loadManagedProjects", load_start)
attention_body = DASHBOARD_HTML[load_start:load_end]
⋮----
def test_browser_validation_evidence_is_rendered_in_production_outcome()
⋮----
def test_cooperative_multi_agent_progress_is_visible_in_managed_and_production_detail()
⋮----
def test_managed_and_attention_cards_render_normalized_production_outcome()
⋮----
def test_launch_preflight_is_server_backed_and_mobile_visible()
⋮----
def test_last_launched_project_survives_dashboard_reload_on_same_device()
⋮----
def test_dashboard_refresh_and_repository_change_refresh_launch_readiness()
⋮----
def test_last_production_tracker_renders_live_runtime_status()
⋮----
def test_last_production_tracker_keeps_server_outcome_and_project_deep_link()
⋮----
def test_one_tap_launch_persists_request_id_until_successful_response()
⋮----
def test_one_tap_retry_state_does_not_persist_instruction_text()
⋮----
pending_start = DASHBOARD_HTML.index("function pendingLaunchRequest")
pending_end = DASHBOARD_HTML.index("function clearPendingLaunchRequest", pending_start)
pending_body = DASHBOARD_HTML[pending_start:pending_end]
⋮----
def test_last_production_tracker_exposes_guarded_cancel_for_active_phases()
⋮----
def test_last_production_tracker_renders_cancelling_phase_and_cancel_endpoint()
⋮----
def test_last_production_tracker_exposes_recovery_and_completion_actions()
⋮----
def test_last_production_recovery_actions_refresh_server_backed_surfaces()
⋮----
start = DASHBOARD_HTML.index("async function lastProductionManagedAction")
end = DASHBOARD_HTML.index("async function loadLastProduction", start)
body = DASHBOARD_HTML[start:end]
⋮----
def test_dashboard_has_server_backed_multi_production_view()
⋮----
def test_production_inbox_renders_live_runtime_and_server_actions()
⋮----
def test_dashboard_supports_secure_fragment_pairing_without_query_leak()
```

## File: test_dashboard_usage.py
```python
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
```

## File: test_database_maintenance_lock.py
```python
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
```

## File: test_deep_fingerprint_starlist.py
```python
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
```

## File: test_dynamic_agent_fanout.py
```python
def _build(tmp_path)
⋮----
backend = SQLiteBackend(tmp_path / "dynamic-agent.sqlite")
queue = SQLiteJobQueue(backend)
⋮----
def _planner_spec()
⋮----
def test_planner_result_expands_parallel_agents_and_integration(tmp_path)
⋮----
workflow = engine.create(
planner_job = engine.dispatch_ready(workflow["id"], limit=10)[0]
⋮----
expanded = engine.record_result(
⋮----
by_id = {task["task_id"]:task for task in expanded["tasks"]}
⋮----
code = queue.claim_next(
tests = queue.claim_next(
⋮----
progressed = engine.record_result(
⋮----
integration = next(
⋮----
integration_job = queue.claim_next(
⋮----
upstream = integration_job["payload"]["handoff"]["upstream_context"]
⋮----
def test_planner_child_dependencies_preserve_ordered_dag(tmp_path)
⋮----
def test_invalid_planner_plan_is_rejected_before_child_dispatch(tmp_path)
⋮----
current = engine.get(workflow["id"])
⋮----
planner = current["tasks"][0]
⋮----
def test_dynamic_planner_uses_validated_fallback_when_model_plan_missing(tmp_path)
⋮----
fallback = {
planner = _planner_spec()
⋮----
def test_dynamic_planner_rejects_invalid_primary_and_invalid_fallback(tmp_path)
⋮----
def test_dynamic_planner_generates_post_integration_validation_chain(tmp_path)
⋮----
progressed = engine.get(workflow["id"])
⋮----
def test_dynamic_plan_records_model_source_and_fanout_event(tmp_path)
⋮----
children = [
⋮----
events = [
⋮----
def test_dynamic_plan_records_fallback_source(tmp_path)
```

## File: test_emergency_key_revocation.py
```python
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
```

## File: test_execution_feedback_trends.py
```python
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
```

## File: test_execution_optimizer_postgres.py
```python
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
```

## File: test_execution_optimizer.py
```python
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
```

## File: test_executor_worktree.py
```python
def _git(path: Path, *args: str) -> str
⋮----
result = subprocess.run(
⋮----
def _repo(tmp_path: Path) -> Path
⋮----
repo = tmp_path / "repo"
⋮----
def test_prepare_isolated_worktree_creates_attempt_scoped_branch(tmp_path)
⋮----
repo = _repo(tmp_path)
base = _git(repo, "rev-parse", "HEAD")
contract = build_worktree_contract(
⋮----
prepared = prepare_isolated_worktree(
⋮----
path = Path(prepared.worktree_path)
⋮----
def test_prepare_isolated_worktree_reuses_matching_existing_workspace(tmp_path)
⋮----
first = prepare_isolated_worktree(
second = prepare_isolated_worktree(
⋮----
def test_retry_contract_gets_distinct_worktree(tmp_path)
⋮----
first_contract = build_worktree_contract(
retry_contract = build_worktree_contract(
⋮----
retry = prepare_isolated_worktree(
⋮----
def test_remove_isolated_worktree_detaches_and_prunes(tmp_path)
⋮----
listing = _git(repo, "worktree", "list", "--porcelain")
⋮----
def test_prepare_rejects_non_repository_root(tmp_path)
⋮----
folder = tmp_path / "not-repo"
⋮----
contract = {
⋮----
def test_remote_worker_cli_parses_repository_worktree_configuration()
⋮----
args = _parse_args([
⋮----
def test_repository_root_mapping_rejects_ambiguous_values()
⋮----
def test_runner_uses_repository_cache_when_no_explicit_mapping(tmp_path, monkeypatch)
⋮----
class DummyClient
⋮----
worker_id = "worker-test"
⋮----
runner = RemoteWorkerRunner(
⋮----
job = RemoteJob(
⋮----
prepared = runner._prepare_worktree(job)
⋮----
def test_remote_worker_cli_exposes_repository_cache_root()
⋮----
def _commit(repo: Path, message: str) -> str
⋮----
def _current_branch(repo: Path) -> str
⋮----
def test_preintegrate_upstream_commits_applies_clean_independent_changes(tmp_path)
⋮----
base_branch = _current_branch(repo)
⋮----
commit_a = _commit(repo, "agent a")
⋮----
commit_b = _commit(repo, "agent b")
⋮----
result = preintegrate_upstream_commits(
⋮----
target = Path(prepared.worktree_path)
⋮----
def test_preintegrate_conflict_rolls_back_entire_preflight(tmp_path)
⋮----
commit_a = _commit(repo, "agent a conflict")
⋮----
commit_b = _commit(repo, "agent b conflict")
⋮----
def test_preintegrate_missing_commit_leaves_clean_starting_state(tmp_path)
⋮----
missing = "f" * 40
⋮----
def test_preintegrate_dirty_workspace_defers_without_mutation(tmp_path)
⋮----
def test_inspect_worktree_result_reports_clean_committed_evidence(tmp_path)
⋮----
final_sha = _git(target, "rev-parse", "HEAD")
⋮----
evidence = inspect_worktree_result(
⋮----
def test_inspect_worktree_result_reports_uncommitted_changes(tmp_path)
⋮----
def test_prune_integrated_workflow_branches_deletes_only_ancestors(tmp_path)
⋮----
prefix = "production-os/wf-prune"
⋮----
integrated = f"{prefix}/integration"
⋮----
result = prune_integrated_workflow_branches(repo, integrated)
⋮----
branches = set(_git(repo, "branch", "--format=%(refname:short)").splitlines())
⋮----
def test_prune_integrated_workflow_branches_rejects_foreign_branch(tmp_path)
```

## File: test_fairness.py
```python
class Action
⋮----
def __init__(self, repository, task)
⋮----
def test_round_robin_preserves_repo_internal_order()
⋮----
rows=[
result=round_robin_by_repository(rows)
```

## File: test_fanout_learning.py
```python
def _build(tmp_path)
⋮----
backend = SQLiteBackend(tmp_path / "fanout-learning.sqlite")
queue = SQLiteJobQueue(backend)
⋮----
def _history(engine, repository: str, *, max_agents: int, succeeded: bool)
⋮----
workflow = engine.create(
terminal = "succeeded" if succeeded else "failed"
⋮----
def test_fanout_learning_selects_better_observed_bucket(tmp_path)
⋮----
learned = learn_repository_fanout(
⋮----
def test_fanout_learning_requires_multiple_well_sampled_buckets(tmp_path)
⋮----
def test_planning_policy_uses_learned_lower_fanout(tmp_path)
⋮----
policy = planning_policy_for_repository(
⋮----
def test_global_risk_ceiling_caps_learned_high_fanout(tmp_path)
```

## File: test_filesystem_lock.py
```python
@pytest.mark.skipif(os.name != "posix", reason="cross-process flock requires POSIX")
def test_filesystem_lock_blocks_other_processes(tmp_path)
⋮----
lock = tmp_path / "shared.lock"
marker = tmp_path / "acquired.txt"
script = (
⋮----
process = subprocess.Popen([sys.executable, "-c", script])
⋮----
def test_filesystem_lock_creates_parent_directories(tmp_path)
⋮----
lock = tmp_path / "nested" / "locks" / "repo.lock"
```

## File: test_github_automerge.py
```python
class Client(GitHubClient)
⋮----
def __init__(self, token="token")
⋮----
def _request(self, method, path, payload=None)
⋮----
def test_merge_pull_request_is_pinned_to_observed_head_sha()
⋮----
client = Client()
⋮----
result = client.merge_pull_request(
⋮----
def test_merge_pull_request_requires_token()
⋮----
client = Client(token=None)
⋮----
@pytest.mark.parametrize("sha", ["", "abc1234", "g" * 40])
def test_merge_pull_request_rejects_unpinned_or_invalid_sha(sha)
⋮----
def test_merge_pull_request_rejects_unknown_method()
```

## File: test_github_change_review.py
```python
def test_review_changed_paths_allows_ordinary_source_changes()
⋮----
review = review_changed_paths([
⋮----
def test_review_changed_paths_flags_security_runtime_and_schema_surfaces()
⋮----
def test_review_changed_paths_flags_credential_material()
⋮----
def test_review_changed_paths_fails_closed_when_file_list_unavailable()
⋮----
review = review_changed_paths([])
⋮----
def test_review_changed_files_flags_private_key_material_on_added_line()
⋮----
review = review_changed_files([{
⋮----
def test_review_changed_files_flags_dangerous_shell_and_destructive_sql()
⋮----
review = review_changed_files([
⋮----
def test_review_changed_files_flags_tls_verification_disable()
⋮----
def test_review_changed_files_ignores_risky_text_when_removed()
⋮----
def test_review_changed_files_blocks_large_unavailable_text_diff()
⋮----
def test_review_changed_files_allows_unavailable_binary_patch()
```

## File: test_github_client_pr_files.py
```python
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
```

## File: test_github_client_put_file.py
```python
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
```

## File: test_github_webhook.py
```python
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
```

## File: test_github_work_state.py
```python
def state(**kwargs)
⋮----
base = dict(
⋮----
def test_merged_pr_promotes_only_after_post_merge_validation_passes()
⋮----
def test_merged_pr_rolls_back_when_post_merge_ci_fails()
⋮----
def test_merged_pr_waits_while_post_merge_validation_is_running()
⋮----
def test_failed_ci_retries()
⋮----
def test_closed_unmerged_pr_replans()
⋮----
def test_ci_state_does_not_pass_while_any_workflow_is_running()
⋮----
runs = [
⋮----
def test_ci_state_passes_only_when_all_workflows_complete_successfully()
⋮----
def test_external_commit_statuses_fail_closed()
⋮----
def test_external_failed_status_retries()
⋮----
def test_pending_external_status_remains_running()
⋮----
def test_promotion_readiness_requires_open_non_draft_green_pr()
⋮----
def test_missing_required_checks_detects_absent_contexts_across_sources()
⋮----
missing = _missing_required_checks(
⋮----
def test_unknown_branch_protection_check_set_blocks_promotion()
⋮----
def test_promotion_readiness_blocks_when_required_check_is_missing()
⋮----
def test_promotion_readiness_blocks_sensitive_changes()
```

## File: test_governance.py
```python
def test_auto_quarantine_after_failures(tmp_path)
⋮----
runtime=RuntimeState(tmp_path/"runtime.json")
rec=runtime.get("o/a","task")
⋮----
quarantine=QuarantineStore(tmp_path/"quarantine.json")
policies=PolicySet({
actions=apply_governance(runtime,policies,quarantine)
```

## File: test_health_metrics.py
```python
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
```

## File: test_http_security_headers.py
```python
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
```

## File: test_incident_history.py
```python
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
```

## File: test_key_domains.py
```python
def test_distinct_key_domains_are_accepted()
⋮----
result=assert_separate_key_domains(
⋮----
def test_validator_builder_key_reuse_is_rejected()
⋮----
def test_builder_provenance_private_key_reuse_is_rejected()
```

## File: test_key_registry_validation.py
```python
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
```

## File: test_key_rotation.py
```python
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
```

## File: test_learning_control_surface.py
```python
def test_learning_rewards_successful_history()
⋮----
events = [
signals = build_learning_signals(events)
⋮----
def test_control_surface_contains_schedule()
⋮----
html = render_control_surface({
```

## File: test_managed_dynamic_plan_outcome.py
```python
def test_managed_outcome_exposes_dynamic_model_plan_summary()
⋮----
outcome = _outcome_from_workflow({
⋮----
def test_managed_outcome_exposes_fallback_plan_summary()
⋮----
def test_managed_outcome_has_no_dynamic_plan_for_legacy_workflow()
```

## File: test_managed_github_reconciliation.py
```python
class FakeWorkflows
⋮----
backend = object()
⋮----
class FakeGitHub
⋮----
def __init__(self, merge=None, error=None)
⋮----
def state(**overrides)
⋮----
values = {
⋮----
def workflow_with_pr()
⋮----
def test_green_pull_request_is_sha_pinned_merged_then_waits_for_post_merge_ci()
⋮----
github = FakeGitHub()
service = ManagedProjectService(
⋮----
resolution = service._github_resolution_for_succeeded_workflow(
⋮----
def test_pending_pull_request_keeps_project_active()
⋮----
pending = state(
⋮----
target = service._github_target_for_succeeded_workflow(
⋮----
def test_failed_pull_request_moves_project_to_needs_attention()
⋮----
failed = state(
⋮----
def test_sensitive_green_pull_request_requires_review()
⋮----
sensitive = state(
⋮----
def test_automerge_receipt_prevents_duplicate_merge_during_github_staleness(tmp_path)
⋮----
backend = SQLiteBackend(tmp_path / "automerge-idempotent.sqlite")
⋮----
workflow = workflow_with_pr()
⋮----
first = service._github_resolution_for_succeeded_workflow(
second = service._github_resolution_for_succeeded_workflow(
⋮----
def test_automerge_aborts_when_base_sha_changes_during_final_recheck()
⋮----
initial = state()
changed = state(
⋮----
def test_green_pull_request_merge_declined_requires_review()
⋮----
github = FakeGitHub(
⋮----
def test_post_merge_green_resolution_completes_managed_project()
⋮----
merged_green = state(
⋮----
def test_succeeded_workflow_without_pull_request_keeps_legacy_path()
⋮----
workflow = {
⋮----
def test_succeeded_pull_request_without_ci_moves_to_review_instead_of_stalling()
⋮----
no_ci = state(
⋮----
def test_post_merge_failure_resolution_builds_compensating_rollback_plan()
⋮----
merged_failed = state(
⋮----
plan = resolution["rollback_plan"]
⋮----
def test_reconcile_marks_project_done_after_post_merge_green_ci(tmp_path)
⋮----
backend = SQLiteBackend(tmp_path / "automerge-complete.sqlite")
⋮----
project = service.create(
workflow_id = project["current_workflow_id"]
⋮----
completed = service.get(project["project_id"])
⋮----
def test_reconcile_launches_exactly_one_automatic_rollback_generation(tmp_path)
⋮----
backend = SQLiteBackend(tmp_path / "rollback.sqlite")
⋮----
recovered = service.get(project["project_id"])
polled_again = service.get(project["project_id"])
```

## File: test_managed_project_outcome.py
```python
def test_outcome_normalizes_worker_result_evidence()
⋮----
outcome = _outcome_from_workflow({
⋮----
def test_outcome_uses_evidence_fallback_and_keeps_optional_shape_stable()
⋮----
empty = _outcome_from_workflow(None)
⋮----
def test_outcome_accepts_compact_worker_result_fields_without_exposing_paths()
⋮----
def test_terminal_workflow_outcome_is_visible_without_structured_evidence()
⋮----
def test_outcome_preserves_bounded_mobile_validation_evidence()
⋮----
mobile = outcome["mobile_validation"]
⋮----
def test_outcome_preserves_bounded_browser_validation_evidence()
⋮----
browser = outcome["browser_validation"]
```

## File: test_managed_projects_http_v4.py
```python
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
```

## File: test_managed_projects_v4.py
```python
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
⋮----
def test_deterministic_project_id_is_idempotent_and_rejects_parameter_reuse(tmp_path)
⋮----
project_id = "launchrequest0123456789abcdef0123"
⋮----
first = projects.create(
replay = projects.create(
⋮----
project_count = db.execute(
run_count = db.execute(
job_count = db.execute(
⋮----
def test_deterministic_project_id_validation_preserves_default_creation(tmp_path)
⋮----
normal = projects.create(
```

## File: test_mobile_worker_image.py
```python
def test_mobile_worker_image_pins_flutter_android_runtime_and_avd()
⋮----
payload = Path("Dockerfile.mobile-worker").read_text(encoding="utf-8")
⋮----
def test_mobile_worker_image_includes_git_for_repository_materialization()
```

## File: test_model_router.py
```python
def _backend(tmp_path)
⋮----
def _job(key, repository="owner/repo")
⋮----
def _finish(store, key, provider, model, *, status="succeeded", cost=0.0, duration=10)
⋮----
def test_router_prefers_capable_free_candidate_without_history(tmp_path)
⋮----
router = ModelRouter(_backend(tmp_path))
⋮----
route = router.route(
⋮----
def test_router_uses_success_history_between_equally_free_candidates(tmp_path)
⋮----
backend = _backend(tmp_path)
store = DashboardStore(backend)
⋮----
route = ModelRouter(backend).route([
⋮----
ranking = {
⋮----
def test_router_rejects_exhausted_authenticated_provider_quota(tmp_path)
⋮----
def test_router_filters_candidates_without_required_capabilities(tmp_path)
⋮----
def test_workflow_dispatch_injects_model_route_without_changing_capabilities(tmp_path)
⋮----
engine = WorkflowEngine(backend, SQLiteJobQueue(backend))
workflow = engine.create(
⋮----
job = engine.dispatch_ready(workflow["id"], limit=1)[0]
handoff = job["payload"]["handoff"]
⋮----
def test_workflow_without_candidates_keeps_existing_handoff_shape(tmp_path)
⋮----
def test_worker_catalog_is_deduplicated_and_reused_for_one_tap_dispatch(tmp_path)
⋮----
router = ModelRouter(backend)
candidates = [
⋮----
route = job["payload"]["handoff"]["model_route"]
⋮----
def test_worker_catalog_never_blocks_task_when_no_candidate_fits(tmp_path)
⋮----
def test_explicit_model_candidates_override_worker_catalog(tmp_path)
```

## File: test_native_browser_worker_e2e.py
```python
def _auth()
⋮----
def _server(control)
⋮----
server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(control))
thread = threading.Thread(target=server.serve_forever, daemon=True)
⋮----
def _stop(server, thread)
⋮----
def _browser_handoff()
⋮----
control = ControlPlane(
queued = control.queue.enqueue({
calls = []
⋮----
def fake_loop(config, input_stream, output_stream, **kwargs)
⋮----
def external_must_not_start(*_args, **_kwargs)
⋮----
client = RemoteWorkerClient(
runner = RemoteWorkerRunner(
⋮----
outcomes = runner.run(cycles=1, idle_sleep_seconds=0)
⋮----
runtime_root = tmp_path / "runtime"
side_effects = []
durable_completion = threading.Event()
⋮----
def durable_loop(config, input_stream, output_stream, **kwargs)
⋮----
cancelled = kwargs.get("cancelled")
⋮----
def fake_execute(_plan, **execute_kwargs)
⋮----
deadline = time.time() + 2
⋮----
first_outcomes = []
⋮----
first_client = RemoteWorkerClient(
first_runner = RemoteWorkerRunner(
first_thread = threading.Thread(
⋮----
second_client = RemoteWorkerClient(
second_runner = RemoteWorkerRunner(
⋮----
second_outcomes = second_runner.run(
```

## File: test_native_executor.py
```python
def _browser_handoff()
⋮----
def test_select_native_handler_supports_browser_computer_contract()
⋮----
decision = select_native_handler(_browser_request())
⋮----
def test_select_native_handler_rejects_unknown_contracts()
⋮----
decision = select_native_handler({
⋮----
def test_select_native_handler_is_deterministic_when_multiple_contracts_exist()
⋮----
handoff = _browser_request()
⋮----
first = select_native_handler(handoff)
second = select_native_handler(handoff)
⋮----
def test_execute_native_rejects_unsupported_context_without_side_effects()
⋮----
context = NativeExecutionContext(
⋮----
result = execute_native(context)
⋮----
def _browser_request(*, persist_session=True)
⋮----
handoff = _browser_handoff()
⋮----
def test_native_browser_handler_executes_submitted_turns(tmp_path, monkeypatch)
⋮----
seen = {}
⋮----
def fake_loop(config, input_stream, output_stream, **kwargs)
⋮----
def fake_loop(_config, _input, _output, **kwargs)
⋮----
def test_native_browser_handler_rejects_persistent_session_without_runtime()
⋮----
def test_native_browser_handler_rejects_missing_browser_request()
⋮----
result = execute_browser_native(context)
⋮----
def fake_loop(_config, _input, _output, **_kwargs)
⋮----
def test_select_native_handler_rejects_unknown_browser_contract_version()
⋮----
called = []
⋮----
def must_not_run(*_args, **_kwargs)
⋮----
def fail_runtime(*_args, **_kwargs)
⋮----
def test_select_native_handler_accepts_workflow_contract_with_native_request()
⋮----
decision = select_native_handler(handoff)
⋮----
def test_select_native_handler_rejects_contract_only_browser_job()
⋮----
path = Path(kwargs["artifacts_dir"])
```

## File: test_observability.py
```python
def test_observability_payload_contains_all_sections()
⋮----
payload = build_observability_payload(
```

## File: test_p6_hardening.py
```python
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
```

## File: test_persistent_agent_runtime.py
```python
class FakeClient
⋮----
worker_id = "worker-test"
⋮----
def __init__(self, jobs, *, stale=False)
⋮----
def open_session(self, **_kwargs)
⋮----
def heartbeat(self, **kwargs)
⋮----
active = [str(key) for key in kwargs.get("active_job_keys") or []]
⋮----
def claim(self, **_kwargs)
⋮----
def ack(self, key)
⋮----
def complete(self, key, *, result_payload=None, duration_seconds=None)
⋮----
def fail(self, key, reason, *, result_payload=None, duration_seconds=None)
⋮----
def checkpoint_stale(self, key, checkpoint_ref)
⋮----
def test_persistent_runtime_reuses_session_and_marks_resume(tmp_path)
⋮----
runtime = PersistentAgentRuntime(tmp_path / "runtime")
first = runtime.prepare("job/unsafe/../key")
⋮----
checkpoint = tmp_path / "runtime" / runtime._job_dir_name("job/unsafe/../key") / "checkpoint.json"
⋮----
second = runtime.prepare("job/unsafe/../key")
⋮----
def test_remote_runner_passes_durable_runtime_context_to_executor(tmp_path)
⋮----
executor = tmp_path / "executor.py"
⋮----
client = FakeClient([RemoteJob("job-1", {"payload":{"task":"x"}})])
runner = RemoteWorkerRunner(
⋮----
outcomes = runner.run(cycles=1, idle_sleep_seconds=0)
⋮----
result = client.completed[0][1]
⋮----
state = runner.agent_runtime.inspect("job-1")
⋮----
def test_worker_compose_mounts_shared_durable_runtime()
⋮----
compose = open("compose.worker.yaml", encoding="utf-8").read()
⋮----
def test_remote_worker_cli_exposes_runtime_root()
⋮----
args = _parse_args([
⋮----
def test_active_checkpoint_protocol_is_atomic_validated_and_observed(tmp_path)
⋮----
context = runtime.prepare("job-checkpoint")
⋮----
observed = runtime.observe_checkpoint(context.job_key)
⋮----
state = runtime.inspect(context.job_key)
⋮----
def test_checkpoint_with_wrong_session_is_not_resumable(tmp_path)
⋮----
context = runtime.prepare("job-session-bound")
⋮----
def test_stale_job_reports_real_durable_checkpoint_reference(tmp_path)
⋮----
client = FakeClient(
⋮----
seeded = runner.agent_runtime.prepare("job-stale")
⋮----
state = runner.agent_runtime.inspect("job-stale")
⋮----
def test_invalid_checkpoint_does_not_replace_runtime_resume_contract(tmp_path)
⋮----
first = runtime.prepare("job-invalid")
checkpoint = runtime.workspace_for("job-invalid") / "checkpoint.json"
⋮----
second = runtime.prepare("job-invalid")
```

## File: test_policy_budgets.py
```python
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
⋮----
def test_rate_limit_check_does_not_mutate_store(tmp_path)
⋮----
path = tmp_path / "rate.json"
store = RateLimitStore(path)
⋮----
first = store.check("repo:o/a", limit=2, window_seconds=3600)
second = store.check("repo:o/a", limit=2, window_seconds=3600)
⋮----
reloaded = RateLimitStore(path)
⋮----
def test_rate_limit_record_once_is_idempotent(tmp_path)
⋮----
final = RateLimitStore(path)
⋮----
def test_budget_record_once_is_idempotent(tmp_path)
⋮----
path = tmp_path / "budget.json"
ledger = BudgetLedger(path)
⋮----
first = ledger.record_once(
reloaded = BudgetLedger(path)
second = reloaded.record_once(
⋮----
def test_different_project_ids_charge_independently(tmp_path)
⋮----
def test_legacy_rate_limit_check_and_record_still_records_each_call(tmp_path)
⋮----
first = store.check_and_record("repo:o/a", limit=3, window_seconds=3600)
second = store.check_and_record("repo:o/a", limit=3, window_seconds=3600)
```

## File: test_policy_validation.py
```python
def test_valid_policy_payload()
⋮----
result=validate_policy_payload({
⋮----
def test_invalid_policy_payload()
```

## File: test_portfolio_claim_api.py
```python
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
```

## File: test_portfolio_optimizer.py
```python
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
```

## File: test_postgres_backend.py
```python
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
⋮----
def test_postgres_queued_job_can_be_cancelled_without_worker()
⋮----
cancelled=queue.cancel_queued(queued["key"], reason="operator cancel")
⋮----
def test_postgres_learned_skill_storage_round_trip()
⋮----
backend = PostgresBackend(DSN)
⋮----
store = SkillStore(backend)
learned = store.record_success(
⋮----
selected = store.select(
```

## File: test_preemption.py
```python
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
```

## File: test_production_stack_e2e.py
```python
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
```

## File: test_project_memory.py
```python
def _engine(tmp_path)
⋮----
backend = SQLiteBackend(tmp_path / "memory.sqlite")
⋮----
def test_project_memory_records_sanitized_structured_outcome(tmp_path)
⋮----
engine = _engine(tmp_path)
store = ProjectMemoryStore(engine.backend)
⋮----
recorded = store.record_from_result(
⋮----
recalled = store.recall(
⋮----
def test_workflow_result_automatically_creates_managed_project_memory(tmp_path)
⋮----
workflow = engine.create(
⋮----
recalled = engine.project_memory.recall(
⋮----
def test_managed_project_specs_recall_prior_project_memory(tmp_path)
⋮----
managed = ManagedProjectService(engine)
⋮----
task = managed._workflow_spec(
⋮----
context = task.payload["handoff"]["project_memory"]
⋮----
def test_cooperative_planner_receives_memory_as_structured_and_text_context(tmp_path)
⋮----
tasks = managed._cooperative_workflow_specs(
⋮----
planner = tasks[0]
handoff = planner.payload["handoff"]
⋮----
def test_project_memory_deduplicates_identical_repeated_outcomes(tmp_path)
⋮----
kwargs = {
⋮----
first = store.record_from_result(**kwargs)
second = store.record_from_result(**kwargs)
```

## File: test_project_progress.py
```python
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
```

## File: test_provenance_signer.py
```python
def test_release_provenance_can_be_signed_via_signer()
⋮----
signer=PemSigner(private_key)
approval_key=release_approval_key(
release={
attestation={
provenance=create_release_provenance_with_signer(
```

## File: test_queue_audit_checkpoint.py
```python
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
```

## File: test_reconciliation_dispatch.py
```python
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
```

## File: test_regression_bisect.py
```python
def _git(repo: Path, *args: str) -> str
⋮----
result = subprocess.run(
⋮----
def _history(tmp_path: Path)
⋮----
repo = tmp_path / "repo"
⋮----
script = repo / "bisect_test.py"
⋮----
good = _git(repo, "rev-parse", "HEAD")
⋮----
culprit = _git(repo, "rev-parse", "HEAD")
⋮----
bad = _git(repo, "rev-parse", "HEAD")
⋮----
def test_regression_bisect_finds_first_bad_commit_and_resets_repo(tmp_path)
⋮----
original_head = _git(repo, "rev-parse", "HEAD")
⋮----
result = run_regression_bisect(
⋮----
def test_regression_bisect_rejects_dirty_worktree(tmp_path)
⋮----
def test_regression_bisect_rejects_reversed_ancestry(tmp_path)
⋮----
def test_regression_bisect_requires_full_shas(tmp_path)
⋮----
def test_regression_bisect_cli_parses_bounded_runtime_options()
⋮----
args = _parse_args([
```

## File: test_rekor_checkpoint_state_cli.py
```python
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
```

## File: test_rekor_checkpoint_state_concurrency.py
```python
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
```

## File: test_rekor_checkpoint_state_postgres.py
```python
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
```

## File: test_rekor_checkpoint_state.py
```python
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
```

## File: test_rekor_consistency_client.py
```python
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
```

## File: test_rekor_signed_checkpoint_receipt.py
```python
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
```

## File: test_rekor_signed_checkpoint.py
```python
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
```

## File: test_rekor_v1_key_compatibility.py
```python
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
```

## File: test_rekor_witness_quorum_cli.py
```python
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
```

## File: test_rekor_witness_quorum.py
```python
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
```

## File: test_release_ledger.py
```python
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
```

## File: test_release16_operations_e2e.py
```python
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
```

## File: test_release18_managed_projects_e2e.py
```python
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
```

## File: test_release19_restore_staging_e2e.py
```python
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
```

## File: test_release21_offline_restore_e2e.py
```python
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
```

## File: test_release32_one_tap_e2e.py
```python
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
@pytest.mark.e2e
def test_release32_one_tap_launch_worker_completion_survives_restart(tmp_path)
⋮----
database = str(tmp_path / "one-tap-e2e.sqlite")
first = ControlPlane(database, authorizer=_auth())
⋮----
repository = "dbrckk/one-tap-e2e"
instruction = "Implement the requested change, run validation, and report evidence."
⋮----
project = launched["project"]
project_id = project["project_id"]
workflow_id = project["current_workflow_id"]
⋮----
worker = RemoteWorkerClient(
job = worker.claim()
⋮----
handoff = job.payload["payload"]["handoff"]
⋮----
completed = worker.complete(
⋮----
project_after_worker = refreshed["project"]
⋮----
restarted = ControlPlane(database, authorizer=_auth())
restored = restarted.managed_projects.get(project_id)
⋮----
@pytest.mark.e2e
def test_one_tap_auto_enables_cooperative_mode_when_specialist_fleet_exists(tmp_path)
⋮----
control = ControlPlane(
⋮----
workflow = control.workflows.get(
⋮----
tasks = {
⋮----
planner = tasks["planner"]
⋮----
planner_job = control.queue.get(planner["claimed_job_key"])
⋮----
contract = planner_job["payload"]["handoff"]["tool_contracts"][
⋮----
expanded = control.workflows.record_result(
expanded_tasks = {
⋮----
def test_cooperative_fleet_detection_ignores_dead_specialists(tmp_path)
⋮----
worker = control.workers.register(
⋮----
def test_ui_goal_requires_online_browser_specialist_for_cooperative_mode(tmp_path)
⋮----
def test_native_ui_goal_requires_online_mobile_specialist_for_cooperative_mode(tmp_path)
⋮----
def test_non_ui_goal_can_use_any_online_specialist_for_cooperative_mode(tmp_path)
```

## File: test_release33_auto_worker_recovery_e2e.py
```python
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
@pytest.mark.e2e
def test_release33_expired_one_tap_claim_is_recovered_by_next_worker(tmp_path)
⋮----
database = str(tmp_path / "one-tap-recovery.sqlite")
control = ControlPlane(database, authorizer=_auth())
⋮----
repository = "dbrckk/recovery-e2e"
instruction = "Implement and validate the requested production change."
⋮----
project = launched["project"]
project_id = project["project_id"]
workflow_id = project["current_workflow_id"]
⋮----
first_worker = RemoteWorkerClient(
first_claim = first_worker.claim(ack_timeout_seconds=1)
⋮----
job_key = first_claim.key
⋮----
# Simulate a worker disappearing after claim but before ACK.
⋮----
second_worker = RemoteWorkerClient(
recovered_claim = second_worker.claim()
⋮----
completed = second_worker.complete(
⋮----
final = refreshed["project"]
⋮----
queue_job = control.queue.get(job_key)
⋮----
recovered_events = [
```

## File: test_release34_safe_running_recovery_e2e.py
```python
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
@pytest.mark.e2e
def test_release34_running_one_tap_job_recovers_only_after_dual_staleness(tmp_path)
⋮----
database = str(tmp_path / "running-recovery.sqlite")
control = ControlPlane(database, authorizer=_auth())
⋮----
project = launched["project"]
project_id = project["project_id"]
workflow_id = project["current_workflow_id"]
⋮----
worker_one = RemoteWorkerClient(
first_claim = worker_one.claim()
⋮----
job_key = first_claim.key
⋮----
# Stale worker heartbeat alone is insufficient: fresh execution
# telemetry must fence automatic recovery.
⋮----
worker_two = RemoteWorkerClient(
⋮----
# Once both heartbeat and execution telemetry are stale, the next
# healthy worker may safely fence the old owner and resume the job.
⋮----
recovered = worker_two.claim()
⋮----
old_execution = dict(
⋮----
final = refreshed["project"]
⋮----
latest = control.dashboard_store.latest_execution(job_key)
⋮----
recovered_events = [
```

## File: test_release35_control_plane_restart_e2e.py
```python
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
def _stop(server, thread)
⋮----
@pytest.mark.e2e
def test_release35_active_worker_survives_control_plane_restart_without_duplication(tmp_path)
⋮----
database = str(tmp_path / "restart-active.sqlite")
first = ControlPlane(database, authorizer=_auth())
⋮----
project = launched["project"]
project_id = project["project_id"]
workflow_id = project["current_workflow_id"]
⋮----
worker = RemoteWorkerClient(base, "worker-one", "worker-one", [], timeout=5)
claimed = worker.claim()
⋮----
job_key = claimed.key
⋮----
second = ControlPlane(database, authorizer=_auth())
restored_job = second.queue.get(job_key)
restored_execution = second.dashboard_store.latest_execution(job_key)
restored_project = second.managed_projects.get(project_id)
⋮----
reconnected = RemoteWorkerClient(
heartbeat = reconnected.heartbeat(
⋮----
final = second.managed_projects.get(project_id)
⋮----
@pytest.mark.e2e
def test_release35_abandoned_worker_is_recovered_after_restart_with_same_identity(tmp_path)
⋮----
database = str(tmp_path / "restart-abandoned.sqlite")
⋮----
worker_one = RemoteWorkerClient(
claimed = worker_one.claim()
⋮----
worker_two = RemoteWorkerClient(
recovered = worker_two.claim()
⋮----
latest = second.dashboard_store.latest_execution(job_key)
⋮----
first_attempt = dict(
```

## File: test_release36_worker_session_reconciliation_e2e.py
```python
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
def _stop(server, thread)
⋮----
@pytest.mark.e2e
def test_release36_simultaneous_control_and_worker_restart_reconciles_two_projects(tmp_path)
⋮----
database = str(tmp_path / "simultaneous-restart.sqlite")
first = ControlPlane(database, authorizer=_auth())
⋮----
projects = []
⋮----
worker_one = RemoteWorkerClient(
first_claim = worker_one.claim()
⋮----
abandoned_key = first_claim.key
⋮----
first_project_id = projects[0]["project_id"]
second_project_id = projects[1]["project_id"]
first_workflow_id = projects[0]["current_workflow_id"]
second_workflow_id = projects[1]["current_workflow_id"]
⋮----
# Simulate both the Control Plane and worker process restarting. The new
# worker process reports that it has no in-memory active jobs.
second = ControlPlane(database, authorizer=_auth())
⋮----
recovered = reregistered["reconciliation"]["recovered_jobs"]
⋮----
old_execution = second.dashboard_store.latest_execution(abandoned_key)
⋮----
restarted_one = RemoteWorkerClient(
worker_two = RemoteWorkerClient(
⋮----
claim_one = restarted_one.claim()
⋮----
claim_two = worker_two.claim()
⋮----
claimed_keys = {claim_one.key, claim_two.key}
⋮----
queued_rows = db.execute(
expected_keys = {row["key"] for row in queued_rows}
⋮----
final_one = second.managed_projects.get(first_project_id)
final_two = second.managed_projects.get(second_project_id)
⋮----
latest_abandoned = second.dashboard_store.latest_execution(abandoned_key)
⋮----
recovery_events = [
```

## File: test_release41_live_production_tracking_e2e.py
```python
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
@pytest.mark.e2e
def test_release41_live_status_tracks_one_tap_to_review_and_restart(tmp_path)
⋮----
database = str(tmp_path / "release41-live.sqlite")
control = ControlPlane(database, authorizer=_auth())
⋮----
project_id = launched["project"]["project_id"]
workflow_id = launched["project"]["current_workflow_id"]
⋮----
job_key = queued["runtime"]["job_key"]
⋮----
worker = RemoteWorkerClient(base, "worker", "worker-live", [], timeout=5)
claimed = worker.claim()
⋮----
restarted = ControlPlane(database, authorizer=_auth())
restored = restarted.dashboard.production_status(project_id)
```

## File: test_release42_idempotent_launch_e2e.py
```python
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
@pytest.mark.e2e
def test_release42_retry_after_control_plane_restart_returns_same_launch(tmp_path)
⋮----
database = str(tmp_path / "release42-idempotent.sqlite")
request_id = "mobile-retry-20260925-abcdef"
body = {
⋮----
first_control = ControlPlane(database, authorizer=_auth())
⋮----
project_id = first["project"]["project_id"]
workflow_id = first["project"]["current_workflow_id"]
⋮----
# Model an ambiguous network outcome: the first request committed but the
# client retries after both browser/server recovery.
second_control = ControlPlane(database, authorizer=_auth())
⋮----
project_count = db.execute(
workflow_count = db.execute(
job_count = db.execute(
```

## File: test_release43_safe_production_cancel_e2e.py
```python
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
def _stop(server, thread)
⋮----
database = str(tmp_path / "safe-cancel.sqlite")
first = ControlPlane(database, authorizer=_auth())
⋮----
project = launched["project"]
project_id = project["project_id"]
workflow_id = project["current_workflow_id"]
⋮----
worker_one = RemoteWorkerClient(
claimed = worker_one.claim()
⋮----
job_key = claimed.key
⋮----
# The worker disappears before acknowledging cancellation. Persist both
# stale signals so normal abandoned-execution recovery will requeue it.
⋮----
second = ControlPlane(database, authorizer=_auth())
⋮----
worker_two = RemoteWorkerClient(
⋮----
# Claim polling first recovers the abandoned ACKed job, then observes
# the persisted cancel request and finalizes cancellation instead of
# assigning the job to worker two.
⋮----
job = second.queue.get(job_key)
⋮----
final = second.managed_projects.get(project_id)
⋮----
control_state = second.dashboard_control.job_state(job_key)
⋮----
events = second.backend.events_after(0, 2000)
```

## File: test_release44_one_tap_recovery_actions_e2e.py
```python
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
@pytest.mark.e2e
def test_release44_cancel_retest_complete_keeps_same_managed_project(tmp_path)
⋮----
control = ControlPlane(
⋮----
first = launched["project"]
project_id = first["project_id"]
first_workflow = first["current_workflow_id"]
first_job_key = first["current_workflow"]["tasks"][0]["claimed_job_key"]
⋮----
second = retried["project"]
second_workflow = second["current_workflow_id"]
⋮----
worker = RemoteWorkerClient(base, "worker", "worker", [], timeout=5)
job = worker.claim()
```

## File: test_release45_production_inbox_e2e.py
```python
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
def _stop(server, thread)
⋮----
@pytest.mark.e2e
def test_release45_server_inbox_tracks_multiple_productions_across_restart(tmp_path)
⋮----
database = str(tmp_path / "production-inbox-e2e.sqlite")
first = ControlPlane(database, authorizer=_auth())
⋮----
project_ids = []
⋮----
worker = RemoteWorkerClient(base, "worker", "worker", [], timeout=5)
claimed = worker.claim()
⋮----
running = next(
⋮----
second = ControlPlane(database, authorizer=_auth())
⋮----
# A fresh browser/device only needs viewer access. No local last-project
# state is required to reconstruct all current productions.
```

## File: test_release51_one_tap_runner_e2e.py
```python
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
def _stop(server, thread)
⋮----
@pytest.mark.e2e
def test_release51_one_tap_launch_runs_through_real_runner_to_review_required(tmp_path)
⋮----
database = str(tmp_path / "one-tap-runner-success.sqlite")
control = ControlPlane(database, authorizer=_auth())
executor = tmp_path / "success_executor.py"
⋮----
project_id = launched["project"]["project_id"]
workflow_id = launched["project"]["current_workflow_id"]
⋮----
client = RemoteWorkerClient(base, "runner", "runner", [], timeout=5)
runner = RemoteWorkerRunner(
outcomes = runner.run(cycles=1, idle_sleep_seconds=0)
⋮----
outcome = detail["project"]["outcome"]
⋮----
@pytest.mark.e2e
def test_release51_executor_failure_surfaces_as_actionable_production(tmp_path)
⋮----
database = str(tmp_path / "one-tap-runner-failure.sqlite")
⋮----
executor = tmp_path / "failed_executor.py"
⋮----
# Polling cycles are not equivalent to claimed jobs: after a failed
# executor result, workflow reconciliation can requeue the retry just
# after a poll. Allow bounded spare polls while still asserting exactly
# three real attempts below.
outcomes = runner.run(cycles=6, idle_sleep_seconds=0)
⋮----
# Managed Project implementation tasks have max_attempts=3. A worker
# failure is automatically retried with a new job key until that
# budget is exhausted; only then should operator attention be needed.
⋮----
item = next(
```

## File: test_release55_worker_operations.py
```python
def _auth()
⋮----
def _server(control)
⋮----
server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(control))
thread = threading.Thread(target=server.serve_forever, daemon=True)
⋮----
def _stop(server, thread)
⋮----
def _client(base)
⋮----
def test_paused_runner_acknowledges_control_and_does_not_claim(tmp_path)
⋮----
control = ControlPlane(str(tmp_path / "paused.sqlite"), authorizer=_auth())
queued = control.queue.enqueue({
⋮----
executor = tmp_path / "executor.py"
⋮----
runner = RemoteWorkerRunner(
⋮----
state = control.dashboard_control.worker_state("runner-1")
⋮----
def test_draining_runner_finishes_active_job_without_claiming_replacement(tmp_path)
⋮----
control = ControlPlane(str(tmp_path / "draining.sqlite"), authorizer=_auth())
first = control.queue.enqueue({
second = control.queue.enqueue({
marker = tmp_path / "started"
⋮----
outcomes = []
⋮----
runner_thread = threading.Thread(
⋮----
deadline = time.time() + 2
⋮----
def test_resumed_runner_claims_after_pause_acknowledgement(tmp_path)
⋮----
control = ControlPlane(str(tmp_path / "resume.sqlite"), authorizer=_auth())
⋮----
outcomes = runner.run(cycles=2, idle_sleep_seconds=0)
```

## File: test_remote_worker_runner.py
```python
def _server(control)
⋮----
server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(control))
thread = threading.Thread(target=server.serve_forever, daemon=True)
⋮----
def _stop(server, thread)
⋮----
def _auth()
⋮----
def test_worker_session_self_registers_and_reconciles_previous_claim(tmp_path)
⋮----
control = ControlPlane(str(tmp_path / "session.sqlite"), authorizer=_auth())
⋮----
client = RemoteWorkerClient(
session = client.open_session(
⋮----
queued = control.queue.enqueue({
job = client.claim()
⋮----
restarted = RemoteWorkerClient(
reconciled = restarted.open_session(
⋮----
def test_worker_session_rejects_token_identity_mismatch(tmp_path)
⋮----
control = ControlPlane(str(tmp_path / "identity.sqlite"), authorizer=_auth())
⋮----
def test_remote_worker_runner_executes_json_executor_and_completes_job(tmp_path)
⋮----
control = ControlPlane(str(tmp_path / "runner.sqlite"), authorizer=_auth())
⋮----
executor = tmp_path / "executor.py"
⋮----
runner = RemoteWorkerRunner(
⋮----
outcomes = runner.run(cycles=1, idle_sleep_seconds=0)
⋮----
execution = control.dashboard_store.latest_execution(queued["key"])
⋮----
def test_remote_worker_runner_tolerates_transient_active_heartbeat_failure(tmp_path)
⋮----
control = ControlPlane(str(tmp_path / "heartbeat-retry.sqlite"), authorizer=_auth())
⋮----
executor = tmp_path / "slow_success.py"
⋮----
real_heartbeat = runner._heartbeat_active
calls = {"count":0}
⋮----
def flaky_heartbeat(key)
⋮----
def test_remote_worker_runner_fails_job_on_invalid_executor_output(tmp_path)
⋮----
control = ControlPlane(str(tmp_path / "invalid-output.sqlite"), authorizer=_auth())
⋮----
executor = tmp_path / "invalid.py"
⋮----
def test_remote_worker_runner_acknowledges_cancel_and_terminates_executor(tmp_path)
⋮----
control = ControlPlane(str(tmp_path / "cancel.sqlite"), authorizer=_auth())
⋮----
executor = tmp_path / "slow.py"
⋮----
outcomes = []
⋮----
worker_thread = threading.Thread(
⋮----
deadline = time.time() + 5
⋮----
state = control.dashboard_control.job_state(queued["key"])
⋮----
control = ControlPlane(str(tmp_path / "secret-env.sqlite"), authorizer=_auth())
⋮----
executor = tmp_path / "env_check.py"
⋮----
def test_remote_worker_runner_honors_max_concurrency_with_full_active_set(tmp_path)
⋮----
control = ControlPlane(str(tmp_path / "concurrent-runner.sqlite"), authorizer=_auth())
queued = [
markers = tmp_path / "markers"
⋮----
executor = tmp_path / "concurrent_executor.py"
⋮----
deadline = time.time() + 1.0
saw_two_markers = False
saw_two_active = False
⋮----
saw_two_markers = True
⋮----
worker = control.workers.workers.get("runner-1")
⋮----
saw_two_active = True
⋮----
control = ControlPlane(
⋮----
markers = tmp_path / "stop-markers"
⋮----
executor = tmp_path / "stop_executor.py"
⋮----
runner_thread = None
runner = None
⋮----
runner_thread = threading.Thread(
⋮----
deadline = time.time() + 3
⋮----
pid = int(marker.read_text(encoding="utf-8"))
⋮----
# The stopped worker never lies by marking unfinished work failed or
# completed. A fresh session for the same worker is authoritative and
# immediately recovers both abandoned ACKed jobs.
⋮----
session = restarted.open_session(
recovered = session["recovered_jobs"]
⋮----
def test_remote_worker_runner_executes_in_configured_isolated_worktree(tmp_path)
⋮----
repo = tmp_path / "repo"
⋮----
base_sha = subprocess.run(
⋮----
control = ControlPlane(str(tmp_path / "worktree-runner.sqlite"), authorizer=_auth())
⋮----
executor = tmp_path / "worktree_executor.py"
⋮----
result = execution["result_summary"]
⋮----
branch_file = subprocess.run(
⋮----
def test_remote_worker_runner_preintegrates_multi_parent_commits(tmp_path)
⋮----
repo = tmp_path / "integration-repo"
⋮----
base_branch = subprocess.run(
⋮----
commit_a = subprocess.run(
⋮----
commit_b = subprocess.run(
⋮----
executor = tmp_path / "integration_executor.py"
⋮----
preflight = execution["result_summary"]["preflight"]
⋮----
branches = subprocess.run(
⋮----
def test_remote_worker_runner_rejects_success_with_dirty_worktree(tmp_path)
⋮----
repo = tmp_path / "dirty-repo"
⋮----
executor = tmp_path / "dirty_executor.py"
⋮----
def test_remote_worker_run_defaults_executor_mode_to_auto()
⋮----
args = _parse_args([
⋮----
def test_remote_worker_run_allows_auto_without_executor_command()
⋮----
def test_remote_worker_run_rejects_external_mode_without_executor_command()
⋮----
def test_remote_worker_run_accepts_native_without_executor_command()
⋮----
def _native_browser_handoff_for_runner()
⋮----
control = ControlPlane(str(tmp_path / "native-preferred.sqlite"), authorizer=_auth())
⋮----
marker = tmp_path / "external-ran"
executor = tmp_path / "external.py"
⋮----
calls = []
⋮----
def fake_native(context)
⋮----
client = RemoteWorkerClient(base, "worker-secret", "runner-1", [], timeout=5)
⋮----
def test_auto_mode_falls_back_to_external_when_native_is_unsupported(tmp_path)
⋮----
control = ControlPlane(str(tmp_path / "native-fallback.sqlite"), authorizer=_auth())
⋮----
def test_native_mode_rejects_unsupported_job(tmp_path)
⋮----
control = ControlPlane(str(tmp_path / "native-unsupported.sqlite"), authorizer=_auth())
⋮----
def test_auto_mode_without_any_executor_fails_executor_unavailable(tmp_path)
⋮----
control = ControlPlane(str(tmp_path / "executor-unavailable.sqlite"), authorizer=_auth())
⋮----
control = ControlPlane(str(tmp_path / "native-no-fallback.sqlite"), authorizer=_auth())
⋮----
def fail_native(_context)
⋮----
control = ControlPlane(str(tmp_path / "native-heartbeat.sqlite"), authorizer=_auth())
⋮----
def slow_native(_context)
⋮----
def counted(key)
⋮----
control = ControlPlane(str(tmp_path / "native-timeout.sqlite"), authorizer=_auth())
⋮----
seen = {}
⋮----
def slow_native(context)
⋮----
fail_calls = []
real_fail = client.fail
⋮----
def counted_fail(*args, **kwargs)
⋮----
control = ControlPlane(str(tmp_path / "native-cancel.sqlite"), authorizer=_auth())
⋮----
def cancellable_native(context)
⋮----
deadline = time.time() + 0.5
⋮----
deadline = time.time() + 2
⋮----
control = ControlPlane(str(tmp_path / "native-stale.sqlite"), authorizer=_auth())
⋮----
deadline = time.time() + 0.3
⋮----
beats = {"count":0}
⋮----
def stale_after_start(key)
⋮----
snapshot = real_heartbeat(key)
⋮----
checkpoint_calls = []
⋮----
control = ControlPlane(str(tmp_path / "native-shutdown.sqlite"), authorizer=_auth())
⋮----
control = ControlPlane(str(tmp_path / "native-outage.sqlite"), authorizer=_auth())
⋮----
deadline = time.time() + 0.4
⋮----
def unavailable(_key)
⋮----
def _prepared_native_worktree(tmp_path)
⋮----
root = tmp_path / "repo"
worktree = tmp_path / "worktree"
⋮----
control = ControlPlane(str(tmp_path / "native-dirty.sqlite"), authorizer=_auth())
⋮----
prepared = _prepared_native_worktree(tmp_path)
inspections = [
⋮----
control = ControlPlane(str(tmp_path / "native-diverged.sqlite"), authorizer=_auth())
⋮----
control = ControlPlane(str(tmp_path / "native-git-evidence.sqlite"), authorizer=_auth())
⋮----
final_sha = "c" * 40
⋮----
control = ControlPlane(str(tmp_path / "native-failure-path.sqlite"), authorizer=_auth())
⋮----
entered = threading.Event()
release = threading.Event()
⋮----
def slow_to_stop(context)
```

## File: test_remote_worker.py
```python
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
⋮----
def test_worker_heartbeat_catalog_drives_automatic_model_route(tmp_path)
⋮----
control=ControlPlane(str(tmp_path/"catalog.sqlite"),authorizer=auth)
⋮----
capacity={
⋮----
events=[
⋮----
workflow=control.workflows.create(
job=control.workflows.dispatch_ready(workflow["id"],limit=1)[0]
route=job["payload"]["handoff"]["model_route"]
⋮----
def test_worker_heartbeat_rejects_invalid_model_catalog(tmp_path)
⋮----
control=ControlPlane(str(tmp_path/"bad-catalog.sqlite"),authorizer=auth)
```

## File: test_render_start.py
```python
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
```

## File: test_repository_cache.py
```python
def _git(path: Path, *args: str) -> str
⋮----
result = subprocess.run(
⋮----
def _remote_repo(tmp_path: Path) -> tuple[Path, Path]
⋮----
source = tmp_path / "source"
⋮----
remote = tmp_path / "remote.git"
⋮----
def test_repository_cache_clones_fetches_and_updates_remote_refs(tmp_path, monkeypatch)
⋮----
cache = RepositoryCache(tmp_path / "cache")
⋮----
first = cache.ensure("owner/repo")
⋮----
checkout = Path(first.path)
⋮----
first_sha = _git(checkout, "rev-parse", "refs/remotes/origin/master")
⋮----
second = cache.ensure("owner/repo")
second_sha = _git(checkout, "rev-parse", "refs/remotes/origin/master")
⋮----
def test_repository_cache_uses_stable_collision_resistant_path(tmp_path, monkeypatch)
⋮----
def test_repository_cache_rejects_invalid_repository_names(tmp_path, repository)
⋮----
def test_repository_cache_rejects_origin_mismatch(tmp_path, monkeypatch)
```

## File: test_result_cache.py
```python
def test_result_cache_roundtrip(tmp_path)
⋮----
backend=SQLiteBackend(tmp_path/"db.sqlite")
cache=ResultCache(backend)
key=fingerprint(repository="o/a",task="Build",inputs={"commit":"abc"})
⋮----
hit=cache.get(key)
```

## File: test_rollback_plan.py
```python
def test_build_rollback_plan_is_compensating_and_preserves_history()
⋮----
plan = build_rollback_plan(
⋮----
def test_build_rollback_plan_rejects_unpinned_merge_commit()
⋮----
def test_build_rollback_plan_carries_non_blocking_bisect_range()
⋮----
def test_build_rollback_plan_rejects_invalid_known_good_sha()
```

## File: test_runtime_contract.py
```python
ROOT = pathlib.Path(__file__).resolve().parents[1]
⋮----
def test_supported_python_range_matches_ci_contract()
⋮----
payload = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
⋮----
def test_default_runtime_is_pinned_to_ci_python()
```

## File: test_runtime_state.py
```python
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
```

## File: test_scheduler.py
```python
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
```

## File: test_scoring.py
```python
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
```

## File: test_secure_release_e2e.py
```python
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
```

## File: test_self_healing_heartbeat.py
```python
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
```

## File: test_signer_factory.py
```python
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
```

## File: test_signers.py
```python
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
```

## File: test_skill_memory.py
```python
def test_skill_store_records_success_and_retrieves_relevant_skill(tmp_path)
⋮----
backend = SQLiteBackend(tmp_path / "skills.sqlite")
store = SkillStore(backend)
⋮----
learned = store.record_success(
⋮----
selected = store.select(
⋮----
def test_repeated_verified_skill_increases_confidence(tmp_path)
⋮----
result = {
⋮----
first = store.record_success(
second = store.record_success(
⋮----
def test_skill_selection_is_repository_scoped(tmp_path)
⋮----
def test_workflow_injects_learned_skill_into_future_handoff(tmp_path)
⋮----
backend = SQLiteBackend(tmp_path / "workflow.sqlite")
queue = SQLiteJobQueue(backend)
engine = WorkflowEngine(backend, queue)
⋮----
first = engine.create(
⋮----
second = engine.create(
jobs = engine.dispatch_ready(second["id"])
handoff = jobs[0]["payload"]["handoff"]
⋮----
def test_invalid_learned_skill_does_not_corrupt_successful_result(tmp_path)
⋮----
workflow = engine.create(
⋮----
current = engine.record_result(
⋮----
task = current["tasks"][0]
⋮----
def test_learned_skill_rejects_secret_like_material(tmp_path)
⋮----
def test_verified_skill_can_transfer_cross_repository_after_two_validations(tmp_path)
⋮----
backend = SQLiteBackend(tmp_path / "skills-transfer.sqlite")
⋮----
def test_unverified_repetition_does_not_promote_skill_cross_repository(tmp_path)
⋮----
backend = SQLiteBackend(tmp_path / "skills-unverified.sqlite")
⋮----
learned = None
⋮----
def test_cross_repo_transfer_requires_capability_match_when_requested(tmp_path)
⋮----
backend = SQLiteBackend(tmp_path / "skills-capability.sqlite")
⋮----
def test_failed_reuse_penalizes_injected_skill_confidence(tmp_path)
⋮----
backend = SQLiteBackend(tmp_path / "skill-feedback.sqlite")
⋮----
learned = engine.skills.record_success(
⋮----
jobs = engine.dispatch_ready(workflow["id"])
injected = jobs[0]["payload"]["handoff"]["learned_skills"]
⋮----
row = db.execute(
⋮----
def test_successful_reuse_slightly_boosts_skill_confidence(tmp_path)
⋮----
backend = SQLiteBackend(tmp_path / "skill-feedback-success.sqlite")
⋮----
def test_skill_schema_upgrade_columns_exist(tmp_path)
⋮----
backend = SQLiteBackend(tmp_path / "skill-schema.sqlite")
⋮----
columns = {
version = db.execute(
```

## File: test_source_tree.py
```python
def test_candidate_source_filter()
⋮----
def test_priority_prefers_source_dirs()
```

## File: test_specialist_job_preferences.py
```python
def queue(tmp_path)
⋮----
backend = SQLiteBackend(tmp_path / "jobs.sqlite")
⋮----
def test_claim_prefers_specialist_within_same_priority(tmp_path)
⋮----
q = queue(tmp_path)
generic = q.enqueue({
specialist = q.enqueue({
⋮----
claimed = q.claim_next(
⋮----
def test_claim_keeps_higher_priority_ahead_of_specialization(tmp_path)
⋮----
high = q.enqueue({
⋮----
def test_claim_falls_back_to_generic_worker_when_preference_not_available(tmp_path)
⋮----
job = q.enqueue({
⋮----
def test_required_capability_remains_strict(tmp_path)
```

## File: test_speculation_api.py
```python
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
```

## File: test_speculation.py
```python
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
```

## File: test_sqlite_backend.py
```python
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
⋮----
def test_queued_job_can_be_cancelled_atomically_without_worker(tmp_path)
⋮----
backend=SQLiteBackend(tmp_path/"cancel.db")
⋮----
cancelled=queue.cancel_queued(queued["key"], reason="operator cancel")
⋮----
replay=queue.cancel_queued(queued["key"], reason="operator cancel")
```

## File: test_sqlite_migration.py
```python
def test_import_runtime_json(tmp_path)
⋮----
source=tmp_path/"runtime.json"
⋮----
backend=SQLiteBackend(tmp_path/"db.sqlite")
result=import_json_state(backend,runtime_state=str(source))
⋮----
state=SQLiteRuntimeState(backend)
```

## File: test_stragglers.py
```python
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
```

## File: test_supply_chain.py
```python
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
```

## File: test_task_capabilities.py
```python
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
⋮----
def test_preferred_capabilities_preserve_explicit_specialist_routing()
⋮----
preferred = inferred_preferred_capabilities(
⋮----
def test_explicit_specialist_preference_overrides_text_inference()
⋮----
def test_explicit_required_capability_overrides_visual_text_inference_when_authoritative()
⋮----
def test_explicit_required_capabilities_remain_additive_by_default()
```

## File: test_transparency_cli.py
```python
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
```

## File: test_transparency_receipts.py
```python
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
```

## File: test_trust_policy.py
```python
def test_strict_policy_accepts_four_distinct_domains()
⋮----
policy=TrustPolicy.create(
mapping=policy.validate()
⋮----
def test_witness_cannot_reuse_provenance_key()
⋮----
def test_witness_cannot_reuse_builder_key()
```

## File: test_trust_status_summary.py
```python
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
```

## File: test_vault_auth.py
```python
def test_vault_approle_requires_credentials(monkeypatch)
⋮----
def test_vault_kubernetes_requires_role_and_jwt()
⋮----
def test_vault_rejects_unknown_auth_method()
```

## File: test_vault_signer.py
```python
def test_vault_requires_https()
⋮----
def test_vault_requires_credentials()
⋮----
def test_factory_creates_vault_transit_signer()
⋮----
signer=create_signer(
⋮----
def test_factory_rejects_vault_uri_without_key()
```

## File: test_witness.py
```python
def test_signed_transparency_checkpoint_verifies()
⋮----
checkpoint=create_checkpoint(
envelope=sign_checkpoint(
⋮----
def test_checkpoint_root_tampering_is_detected()
⋮----
def test_checkpoint_expected_root_mismatch_fails()
```

## File: test_worker_compose_deployment.py
```python
def test_worker_compose_profile_is_safe_and_deployable()
⋮----
payload = Path("compose.worker.yaml").read_text(encoding="utf-8")
⋮----
def test_worker_compose_exposes_specialist_pool_without_replacing_generic_worker()
⋮----
# Browser worker is present but cannot claim browser validation until a real runtime is provisioned.
⋮----
def test_worker_compose_exposes_kvm_mobile_specialist()
⋮----
def test_worker_compose_persists_repository_cache_and_worktrees()
⋮----
def _service_block(payload: str, service: str) -> str
⋮----
marker = f"  {service}:"
lines = payload.splitlines()
start = lines.index(marker)
end = len(lines)
⋮----
line = lines[index]
⋮----
end = index
⋮----
def test_browser_worker_uses_auto_executor_mode()
⋮----
browser = _service_block(payload, "production-worker-browser")
⋮----
def test_browser_worker_does_not_require_external_executor_command()
⋮----
def test_non_browser_specialists_keep_external_executor_configuration()
⋮----
block = _service_block(payload, service)
```

## File: test_workers.py
```python
def test_selects_least_loaded_capable_worker(tmp_path)
⋮----
registry=WorkerRegistry(tmp_path/"workers.json")
a=registry.register("a",["python","android"],2)
b=registry.register("b",["python"],2)
⋮----
selected=select_worker(registry,["python"])
⋮----
def test_rejects_worker_without_required_capability(tmp_path)
⋮----
def test_cooperative_worker_fleet_accepts_any_online_specialist(tmp_path)
⋮----
registry = WorkerRegistry(tmp_path / "workers.json")
⋮----
def test_cooperative_worker_fleet_rejects_missing_specialist(tmp_path)
⋮----
def test_cooperative_worker_fleet_requires_browser_specialist(tmp_path)
⋮----
def test_cooperative_worker_fleet_requires_mobile_specialist(tmp_path)
⋮----
def test_cooperative_worker_fleet_excludes_dead_workers(tmp_path)
⋮----
worker = registry.register("browser", ["browser-ui-validation"], 1)
⋮----
def test_cooperative_worker_fleet_preserves_full_online_worker_semantics(tmp_path)
```

## File: test_workflow_api.py
```python
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
```

## File: test_workflow_cache.py
```python
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
```

## File: test_workflow_change_impact.py
```python
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
```

## File: test_workflow_engine.py
```python
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
def test_downstream_job_receives_bounded_upstream_context(tmp_path)
⋮----
first=wf.dispatch_ready(created["id"])
⋮----
review=next(
⋮----
job=wf.queue.get(review["claimed_job_key"])
upstream=job["payload"]["handoff"]["upstream_context"]
⋮----
def test_workflow_retry_dispatch_includes_prior_failure_context(tmp_path)
⋮----
second=wf.queue.get(current["claimed_job_key"])
context=second["payload"]["handoff"]["retry_context"]
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
```

## File: test_workflow_postgres.py
```python
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
```

## File: test_workflow_splitting.py
```python
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
```

## File: test_worktree_contract.py
```python
def test_worktree_contract_is_deterministic_and_attempt_scoped()
⋮----
first = build_worktree_contract(
again = build_worktree_contract(
retry = build_worktree_contract(
⋮----
def test_dispatch_ready_injects_unique_worktree_contracts_for_parallel_tasks(tmp_path)
⋮----
backend = SQLiteBackend(tmp_path / "workflow.sqlite")
queue = SQLiteJobQueue(backend)
engine = WorkflowEngine(backend, queue)
workflow = engine.create(
⋮----
jobs = engine.dispatch_ready(workflow["id"], limit=10)
⋮----
by_task = {
code = by_task["code"]["payload"]["handoff"]["isolation"]
tests = by_task["tests"]["payload"]["handoff"]["isolation"]
⋮----
def test_integration_target_contract_is_preserved_in_dispatch(tmp_path)
⋮----
backend = SQLiteBackend(tmp_path / "integration.sqlite")
⋮----
job = engine.dispatch_ready(workflow["id"], limit=1)[0]
isolation = job["payload"]["handoff"]["isolation"]
⋮----
def test_dependent_worktree_bases_from_single_upstream_commit(tmp_path)
⋮----
backend = SQLiteBackend(tmp_path / "upstream-base.sqlite")
⋮----
first = engine.dispatch_ready(workflow["id"], limit=10)
⋮----
claimed_integration = queue.claim_next("integrator", capabilities=[])
⋮----
validation = queue.claim_next("validator", capabilities=[])
⋮----
isolation = validation["payload"]["handoff"]["isolation"]
⋮----
def test_multi_parent_integration_does_not_guess_one_upstream_base(tmp_path)
⋮----
backend = SQLiteBackend(tmp_path / "multi-parent-base.sqlite")
⋮----
claimed_a = queue.claim_next("worker-a", capabilities=[])
claimed_b = queue.claim_next("worker-b", capabilities=[])
⋮----
integration = queue.claim_next("integrator", capabilities=[])
⋮----
isolation = integration["payload"]["handoff"]["isolation"]
```
