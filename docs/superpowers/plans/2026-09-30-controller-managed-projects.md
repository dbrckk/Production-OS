# Controller Managed Projects Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Route approved 24/7 controller actions through idempotent Managed Projects so autonomous daemon work uses the modern planner/parallel-agent/worktree/memory stack without weakening existing governance.

**Architecture:** Extract the safety/economic checks currently embedded in `dispatch_handoff()` into a shared autonomous admission boundary. Add a small `autonomous_projects.py` bridge that derives a stable project id, reuses or creates Managed Projects on the same SQLite backend, and never dual-dispatches. Integrate that bridge into `run_control_cycle()` behind `legacy|managed` execution modes; keep legacy as the migration default until parity tests are green, then switch the default to managed in the final migration task.

**Tech Stack:** Python 3.11/3.12, SQLite backend, existing `ManagedProjectService`, `WorkflowEngine`, `RuntimeState`, `PolicySet`, `BudgetLedger`, `RateLimitStore`, `ApprovalStore`, `QuarantineStore`, pytest.

**Spec:** `docs/superpowers/specs/2026-09-30-controller-managed-projects-design.md`

## Global Constraints

- Target steady-state controller execution default is `managed`.
- Deployment/config default remains `legacy` until safety/economic parity tests are green.
- No `both` execution mode.
- Managed launch failure must never same-cycle fallback to `dispatch_handoff()`.
- `execution_mode=managed` requires `database_path`; file-backed controller deployments remain legacy-only.
- Managed Projects use the same durable backend as the controller.
- New autonomous projects use `requested_by="controller"` and `agent_preference="auto"`.
- Controller-created Managed Projects default to cooperative execution when the online fleet supports it; otherwise use non-cooperative Managed Projects, never legacy fallback.
- Stable project identity excludes timestamps, scan order, scores, lane names, worker ids and process ids.
- Exact successful terminal project + same action fingerprint is skipped, not reopened.
- Budget/rate-limit accounting occurs once per new stable project id, never once per daemon cycle.
- Worker-level rate limiting remains at worker/job execution time, not Managed Project creation.
- Existing controller emergency-stop, policy, quarantine, approval, budget, rate-limit, lease/cooldown/circuit/succeeded semantics must not weaken.
- All existing controller, Managed Project, worker recovery, Python compatibility, E2E, wheel and Docker gates remain green.

## Review Focus

- **Partial project initialization after process crash:** retry with the same stable id must not double-charge budget/rate-limit or create a second workflow; pinned in Tasks 4 and 8.
- **Approval keys after moving admission out of `dispatch_handoff()`:** managed and legacy admission must resolve the same canonical runtime action key; pinned in Task 3.
- **Rate-limit mutation before failed launch:** a failed Managed Project reservation must not consume a reusable admission slot; pinned in Tasks 3 and 4.
- **Terminal project reappearance:** identical successful fingerprint must skip, while changed trigger evidence must create a new project; pinned in Task 4.
- **Worker-capability/backpressure behavior:** cooperative selection must not silently admit work that legacy mode would reject for lack of capable workers; pinned in Tasks 3 and 6.

---

### Task 1: Stable Autonomous Action Fingerprint and Project Identity

**Files:**
- Create: `src/production_os/autonomous_projects.py`
- Create: `tests/test_autonomous_projects.py`

**Interfaces:**
- Produces:
  - `AutonomousProjectRequest` frozen dataclass.
  - `AutonomousProjectLaunch` frozen dataclass.
  - `canonical_action_fingerprint_payload(...) -> dict`
  - `autonomous_action_fingerprint(...) -> str`
  - `autonomous_project_id(*, repository: str, action_fingerprint: str) -> str`
- Stable project id format: `controller-<32 lowercase hex chars>`.
- Fingerprint schema: `production-os/autonomous-action-fingerprint/v1`.

- [ ] **Step 1: Write failing identity tests**

Add:
- `test_autonomous_project_id_is_deterministic`
- `test_action_fingerprint_normalizes_evidence_order`
- `test_action_fingerprint_changes_on_task_change`
- `test_action_fingerprint_changes_on_acceptance_change`
- `test_action_fingerprint_changes_on_trigger_evidence_change`
- `test_action_fingerprint_excludes_score_and_lane_metadata`
- `test_autonomous_project_id_rejects_invalid_repository`

Assert exact schema inclusion, sorted evidence/criteria normalization, and `controller-[0-9a-f]{32}`.

- [ ] **Step 2: Run focused tests for RED**

Run:
```bash
pytest tests/test_autonomous_projects.py -v
```

Expected: FAIL because the module/interfaces do not exist.

- [ ] **Step 3: Implement canonical serialization and identity helpers**

Use sorted-key JSON and SHA-256. Canonical payload fields are:
- `schema_version`
- `repository`
- `task`
- `acceptance_criteria`
- `trigger_evidence`
- `risk_class`

Do not include timestamps, priority score or scheduler lane.

- [ ] **Step 4: Run focused tests for GREEN**

Run:
```bash
pytest tests/test_autonomous_projects.py -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/production_os/autonomous_projects.py tests/test_autonomous_projects.py
git commit -m "feat(controller): add stable autonomous project identity"
```

---

### Task 2: Read-Only Rate-Limit Check and Idempotent Admission Accounting

**Files:**
- Modify: `src/production_os/rate_limit.py`
- Modify: `src/production_os/budgets.py`
- Test: `tests/test_policy_budgets.py`
- Test: `tests/test_autonomous_projects.py`

**Interfaces:**
- Produces:
  - `RateLimitStore.check(key: str, *, limit: int, window_seconds: int) -> RateLimitDecision`
  - `RateLimitStore.record_once(key: str, idempotency_key: str, *, window_seconds: int) -> None`
  - `BudgetLedger.record_once(repository: str, delta: dict[str, float], *, idempotency_key: str) -> dict[str, float]`
- Existing `check_and_record()` remains backward compatible for legacy callers.

- [ ] **Step 1: Write failing accounting tests**

Add tests:
- `test_rate_limit_check_does_not_mutate_store`
- `test_rate_limit_record_once_is_idempotent`
- `test_budget_record_once_is_idempotent`
- `test_different_project_ids_charge_independently`

Persist and reload stores between repeated calls to prove durability.

- [ ] **Step 2: Run focused tests for RED**

Run:
```bash
pytest tests/test_policy_budgets.py tests/test_autonomous_projects.py -k "record_once or does_not_mutate" -v
```

Expected: FAIL because read-only/idempotent APIs do not exist.

- [ ] **Step 3: Implement durable idempotency markers**

Extend store schemas backward-compatibly:
- rate-limit store keeps an `idempotency` map/set keyed by project id;
- budget ledger keeps a `recorded_idempotency_keys` collection.

`record_once` must survive process restart and never apply the delta twice.

- [ ] **Step 4: Keep legacy `check_and_record` behavior unchanged**

Add one regression assertion that two allowed calls still create two legacy events.

- [ ] **Step 5: Run focused tests for GREEN**

Run:
```bash
pytest tests/test_policy_budgets.py tests/test_autonomous_projects.py -v
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add src/production_os/rate_limit.py src/production_os/budgets.py tests/test_policy_budgets.py tests/test_autonomous_projects.py
git commit -m "feat(controller): add idempotent autonomous accounting"
```

---

### Task 3: Extract Shared Autonomous Admission Gate

**Files:**
- Create: `src/production_os/autonomous_admission.py`
- Modify: `src/production_os/dispatch.py`
- Reuse: `src/production_os/runtime_state.py::task_key(repository, task)`
- Test: `tests/test_reconciliation_dispatch.py`
- Create: `tests/test_autonomous_admission.py`

**Interfaces:**
- Produces:
  - `AutonomousAdmissionRequest` frozen dataclass containing handoff, repository, task, required capabilities and rate-limit settings.
  - `AutonomousAdmissionDecision` frozen dataclass containing normalized handoff, risk class, constraints, resource request, runtime action key from `task_key(repository, task)`, and selected worker metadata.
  - `evaluate_autonomous_admission(...) -> AutonomousAdmissionDecision`
  - `commit_autonomous_admission(...) -> None`
- Consumes existing:
  - `RuntimeState`
  - `WorkerRegistry`
  - `PolicySet`
  - `RateLimitStore`
  - `ApprovalStore`
  - `BudgetLedger`
  - `QuarantineStore`

- [ ] **Step 1: Write RED parity tests before extraction**

Pin existing dispatch behavior for:
- emergency stop;
- disabled/max-risk policy;
- quarantine;
- repository budget;
- portfolio budget;
- required human approval;
- repository rate limit;
- no capable worker/backpressure;
- runtime leased;
- runtime cooldown;
- runtime circuit-open/succeeded.

Also add:
- `test_managed_admission_uses_same_runtime_key_as_legacy_dispatch`
- `test_managed_admission_rate_limit_check_is_read_only_until_commit`

- [ ] **Step 2: Run parity tests to establish current behavior**

Run:
```bash
pytest tests/test_reconciliation_dispatch.py tests/test_autonomous_admission.py -v
```

Expected: existing legacy cases PASS; new shared-gate tests FAIL.

- [ ] **Step 3: Extract admission without behavior change**

Move pre-queue validation/normalization from `dispatch_handoff()` into `evaluate_autonomous_admission()`.

`dispatch_handoff()` must call the shared gate and then preserve its existing:
- lease acquisition;
- worker active-task increment;
- queue write;
- receipt write;
- exception rollback.

- [ ] **Step 4: Separate accounting commit**

Legacy `dispatch_handoff()` calls `commit_autonomous_admission(...)` after successful queue reservation, preserving current repository/portfolio budget accounting and repository rate-limit semantics.

Worker-scoped rate limiting remains inside the legacy worker-selection/dispatch path because Managed Project creation does not yet select the worker that will eventually claim each WorkflowEngine job.

Managed callers later use `commit_autonomous_admission(..., idempotency_key=project_id)` only for controller-level repository/portfolio accounting.

- [ ] **Step 5: Run parity tests for GREEN**

Run:
```bash
pytest tests/test_reconciliation_dispatch.py tests/test_autonomous_admission.py tests/test_policy_budgets.py -v
```

Expected: PASS with no legacy behavior regression.

- [ ] **Step 6: Commit**

```bash
git add src/production_os/autonomous_admission.py src/production_os/dispatch.py tests/test_reconciliation_dispatch.py tests/test_autonomous_admission.py tests/test_policy_budgets.py
git commit -m "refactor(controller): share autonomous admission gate"
```

---

### Task 4: Managed Project Launch Bridge and Idempotent Reuse

**Files:**
- Modify: `src/production_os/autonomous_projects.py`
- Test: `tests/test_autonomous_projects.py`

**Interfaces:**
- Produces:
  - `launch_autonomous_project(service: ManagedProjectService, request: AutonomousProjectRequest) -> AutonomousProjectLaunch`
  - `autonomous_project_status(service, project_id) -> dict | None`
- Uses exact creation call:
```python
service.create(
    repository=request.repository,
    final_goal=request.task,
    token_budget=request.token_budget,
    agent_preference="auto",
    requested_by="controller",
    project_id=stable_project_id,
    cooperative=request.cooperative,
)
```

- [ ] **Step 1: Write failing bridge tests**

Add:
- `test_launch_creates_managed_project_once`
- `test_repeated_identical_launch_reuses_existing_project`
- `test_reuse_does_not_create_second_workflow`
- `test_successful_terminal_identical_project_is_skipped`
- `test_changed_trigger_evidence_creates_new_project`
- `test_partial_initialization_retry_uses_same_project_id`

Use real SQLite backend + `WorkflowEngine` + `ManagedProjectService`, not mocks, for idempotency tests.

- [ ] **Step 2: Run RED**

Run:
```bash
pytest tests/test_autonomous_projects.py -v
```

Expected: new launch tests FAIL.

- [ ] **Step 3: Implement launch/reuse semantics**

Rules:
- derive stable id before service call;
- existing active/review/attention project -> return `created=False`;
- existing successful `DONE` -> return skipped/reused result, no reopen;
- new fingerprint -> new project id;
- do not catch initialization errors and create a different id.

- [ ] **Step 4: Prove no duplicate initial workflow/jobs**

Assert first and second launch have the same `current_workflow_id` and task count.

- [ ] **Step 5: Run GREEN**

Run:
```bash
pytest tests/test_autonomous_projects.py -v
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add src/production_os/autonomous_projects.py tests/test_autonomous_projects.py
git commit -m "feat(controller): launch idempotent managed projects"
```

---

### Task 5: Shared Cooperative Fleet Capability Helper

**Files:**
- Modify: `src/production_os/workers.py`
- Modify: `src/production_os/control_plane.py`
- Test: `tests/test_workers.py`
- Test: `tests/test_cooperative_managed_projects.py`

**Interfaces:**
- Produces:
  - `cooperative_worker_fleet_available(registry: WorkerRegistry, *, needs_browser: bool = False, needs_mobile: bool = False) -> bool`
- Both ControlPlane and controller use the same helper.

- [ ] **Step 1: Write RED capability tests**

Cover the exact current `ControlPlane.cooperative_worker_fleet_available(final_goal)` semantics:
- non-specialist goal returns true when any online worker exposes one of `code-implementation`, `test-debug`, `code-review`, `browser-ui-validation`, or `mobile-ui-validation`;
- browser-required goal returns true only with an online `browser-ui-validation` worker;
- mobile-required goal returns true only with an online `mobile-ui-validation` worker;
- dead workers are excluded;
- keep current behavior for full-but-online workers unless a separate existing test already treats capacity as unavailable.

This task is an extraction, not a stricter fleet-policy redesign.

- [ ] **Step 2: Run RED**

Run:
```bash
pytest tests/test_workers.py tests/test_cooperative_managed_projects.py -k "cooperative_worker_fleet" -v
```

Expected: FAIL until helper is extracted.

- [ ] **Step 3: Extract shared helper and delegate existing ControlPlane method**

Do not duplicate capability lists in controller and control plane.

- [ ] **Step 4: Run GREEN**

Run:
```bash
pytest tests/test_workers.py tests/test_cooperative_managed_projects.py -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/production_os/workers.py src/production_os/control_plane.py tests/test_workers.py tests/test_cooperative_managed_projects.py
git commit -m "refactor(workers): share cooperative fleet detection"
```

---

### Task 6: Controller Execution Mode, Configuration and Managed Service Wiring

**Files:**
- Modify: `src/production_os/controller.py`
- Modify: `src/production_os/cli.py`
- Test: `tests/test_controller_daemon.py`
- Create: `tests/test_controller_managed_projects.py`

**Interfaces:**
- Extend `run_control_cycle(...)` with:
  - `execution_mode: str = "legacy"`
  - `project_token_budget: int = 12000`
- CLI:
  - `--execution-mode legacy|managed`
  - `--project-token-budget 12000`
- Environment:
  - `PRODUCTION_OS_CONTROLLER_EXECUTION_MODE`
  - `PRODUCTION_OS_CONTROLLER_PROJECT_TOKEN_BUDGET`

- [ ] **Step 1: Write failing config tests**

Add:
- `test_controller_defaults_execution_mode_to_legacy_during_migration`
- `test_controller_cli_accepts_managed_execution_mode`
- `test_controller_managed_mode_requires_database_path`
- `test_controller_rejects_unknown_execution_mode`
- `test_controller_rejects_nonpositive_project_token_budget`

- [ ] **Step 2: Run RED**

Run:
```bash
pytest tests/test_controller_daemon.py tests/test_controller_managed_projects.py -k "execution_mode or project_token_budget" -v
```

Expected: FAIL.

- [ ] **Step 3: Implement validation and service construction**

When `execution_mode=="managed"`:
- require `database_path`;
- reuse `backend` created at cycle start;
- build `WorkflowEngine(backend, durable_queue)`;
- build `ManagedProjectService(workflows)`.

Do not instantiate another database.

- [ ] **Step 4: Keep legacy path unchanged**

No controller action routing changes yet; Task 7 performs the switch.

- [ ] **Step 5: Run GREEN**

Run:
```bash
pytest tests/test_controller_daemon.py tests/test_controller_managed_projects.py -v
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add src/production_os/controller.py src/production_os/cli.py tests/test_controller_daemon.py tests/test_controller_managed_projects.py
git commit -m "feat(controller): add managed execution mode"
```

---

### Task 7: Route Approved Controller Actions to Managed Projects

**Files:**
- Modify: `src/production_os/controller.py`
- Modify: `src/production_os/autonomous_projects.py`
- Test: `tests/test_controller_managed_projects.py`
- Test: `tests/test_controller_asset_capabilities.py`

**Interfaces:**
- Consumes Tasks 1-6.
- Produces cycle response:
  - `managed_projects: list[dict]`
  - existing `dispatches: list[dict]`
- Only one list is populated for execution work in a cycle.

- [ ] **Step 1: Write RED integration tests**

Add:
- `test_managed_mode_now_action_creates_managed_project`
- `test_managed_mode_parallel_action_creates_managed_project`
- `test_second_cycle_reuses_same_project_without_duplicate_workflow`
- `test_managed_mode_never_calls_dispatch_handoff`
- `test_managed_launch_failure_never_falls_back_to_legacy`
- `test_legacy_mode_still_calls_dispatch_handoff`
- `test_managed_cycle_response_contains_managed_projects_and_empty_dispatches`

Use a deterministic fake GitHub client/assessment setup already used by controller tests.

- [ ] **Step 2: Run RED**

Run:
```bash
pytest tests/test_controller_managed_projects.py -v
```

Expected: FAIL because controller still always calls `dispatch_handoff()`.

- [ ] **Step 3: Build AutonomousProjectRequest from approved action**

Map:
- repository;
- task;
- rationale;
- acceptance criteria;
- trigger evidence;
- priority;
- risk class;
- configured token budget;
- `agent_preference="auto"`;
- cooperative decision from shared fleet helper.

- [ ] **Step 4: Apply shared admission before new project creation**

Order:
1. derive stable id;
2. check whether project already exists;
3. if existing, reuse/skip with no accounting;
4. if new, evaluate shared admission;
5. create Managed Project;
6. commit idempotent accounting;
7. journal created/reused/skipped/error.

- [ ] **Step 5: Preserve legacy branch exactly**

`execution_mode=="legacy"` continues to call `dispatch_handoff()`.

No same-cycle cross-fallback.

- [ ] **Step 6: Run GREEN**

Run:
```bash
pytest tests/test_controller_managed_projects.py tests/test_controller_asset_capabilities.py -v
```

Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add src/production_os/controller.py src/production_os/autonomous_projects.py tests/test_controller_managed_projects.py tests/test_controller_asset_capabilities.py
git commit -m "feat(controller): route autonomous work through managed projects"
```

---

### Task 8: Safety, Accounting and Restart Parity E2E

**Files:**
- Modify: `tests/test_controller_managed_projects.py`
- Create: `tests/test_controller_managed_recovery_e2e.py`

**Interfaces:**
- No new production API unless a failing parity test proves one is needed.

- [ ] **Step 1: Add safety-parity matrix tests**

For managed mode prove each block occurs before project creation:
- emergency stop;
- policy disabled/max-risk;
- quarantine;
- repository budget;
- portfolio budget;
- approval required using the same `task_key(repository, task)` as legacy dispatch;
- repository rate limit;
- runtime lease/cooldown/circuit/succeeded;
- no capable worker/backpressure where required.

Do not assert worker-scoped rate-limit charging at project creation; it remains a worker/job execution concern.

For each case assert:
- zero new Managed Project rows;
- zero new workflows;
- zero legacy dispatches;
- journal/metrics record the skip/failure.

- [ ] **Step 2: Add accounting idempotency tests**

Prove:
- successful new project charges once;
- second daemon cycle reuses without second charge;
- failed creation does not double-charge retry;
- controller restart + same project id does not charge again.

- [ ] **Step 3: Add daemon restart E2E**

`test_controller_restart_reuses_active_managed_project`:
1. cycle 1 creates project in SQLite;
2. discard/recreate controller-side objects;
3. cycle 2 sees same action;
4. same project id and workflow id returned;
5. no duplicate initial queue jobs.

- [ ] **Step 4: Add terminal/reappearance E2E**

Prove:
- same successful terminal fingerprint -> skipped;
- changed trigger evidence -> new project id.

- [ ] **Step 5: Run parity/recovery suite**

Run:
```bash
pytest tests/test_controller_managed_projects.py tests/test_controller_managed_recovery_e2e.py tests/test_reconciliation_dispatch.py tests/test_policy_budgets.py -v
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add tests/test_controller_managed_projects.py tests/test_controller_managed_recovery_e2e.py
git commit -m "test(controller): prove managed execution safety parity"
```

---

### Task 9: Switch Default to Managed and Update Deployment/Docs

**Files:**
- Modify: `src/production_os/controller.py`
- Modify: `src/production_os/cli.py`
- Modify: `compose.yaml`
- Modify: `README.md`
- Modify: relevant controller operations documentation
- Test: `tests/test_controller_daemon.py`
- Test: `tests/test_controller_daemon_deployment.py`

**Interfaces:**
- After this task:
  - default `execution_mode="managed"`;
  - deployment default `PRODUCTION_OS_CONTROLLER_EXECUTION_MODE=managed`;
  - explicit `legacy` remains available.

- [ ] **Step 1: Write RED default-switch tests**

Add:
- `test_controller_defaults_execution_mode_to_managed_after_parity`
- `test_controller_deployment_defaults_to_managed_execution`
- `test_explicit_legacy_mode_remains_supported`

- [ ] **Step 2: Run RED**

Run:
```bash
pytest tests/test_controller_daemon.py tests/test_controller_daemon_deployment.py -k "execution_mode or legacy_mode" -v
```

Expected: FAIL while migration default is still legacy.

- [ ] **Step 3: Switch code and deployment default**

Change only after Task 8 parity suite is green.

Update docs with:
- managed default;
- required SQLite `database_path`;
- rollback command/env for `legacy`;
- project token budget configuration;
- no dual-dispatch semantics.

- [ ] **Step 4: Run GREEN**

Run:
```bash
pytest tests/test_controller_daemon.py tests/test_controller_daemon_deployment.py tests/test_controller_managed_projects.py -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/production_os/controller.py src/production_os/cli.py README.md tests/test_controller_daemon.py tests/test_controller_daemon_deployment.py
git commit -m "feat(controller): make managed projects autonomous default"
```

---

### Task 10: Full Regression, Review and Merge

**Files:**
- No production change unless a failing verification exposes a concrete defect.
- Update PR description/review notes.

**Interfaces:**
- Produces a reviewed, green branch and verified post-merge `main`.

- [ ] **Step 1: Run focused controller/managed suites**

Run:
```bash
pytest   tests/test_autonomous_projects.py   tests/test_autonomous_admission.py   tests/test_controller_daemon.py   tests/test_controller_daemon_deployment.py   tests/test_controller_managed_projects.py   tests/test_controller_managed_recovery_e2e.py   tests/test_cooperative_managed_projects.py   tests/test_reconciliation_dispatch.py   tests/test_policy_budgets.py   tests/test_workers.py -v
```

Expected: PASS.

- [ ] **Step 2: Run full suite**

Run:
```bash
pytest -q
```

Expected: all tests pass.

- [ ] **Step 3: Verify CI gates on pushed head**

Required:
- unit tests;
- Python 3.11;
- Python 3.12;
- Production E2E;
- wheel install;
- controller/standard Docker smoke;
- browser/mobile worker validation;
- CLI smoke.

- [ ] **Step 4: Request fresh code review**

Ask reviewer to focus on:
- admission parity;
- duplicate accounting;
- crash/restart idempotency;
- no same-cycle legacy fallback;
- default-switch safety.

Resolve each valid blocking issue with a RED regression test first.

- [ ] **Step 5: Merge with exact reviewed SHA**

Squash merge using `expected_head_sha`.

- [ ] **Step 6: Verify post-merge main**

Confirm:
- PR is merged;
- `main` contains squash commit;
- controller deployment default is managed;
- explicit legacy rollback remains functional;
- post-merge CI/context refresh did not hide a failed merge.
