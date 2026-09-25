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
```

## File: test_dashboard_ui_v3.py
```python
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
def test_merged_pr_promotes()
⋮----
def test_failed_ci_retries()
⋮----
def test_closed_unmerged_pr_replans()
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

## File: test_source_tree.py
```python
def test_candidate_source_filter()
⋮----
def test_priority_prefers_source_dirs()
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
