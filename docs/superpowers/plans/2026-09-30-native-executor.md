# Native Executor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Let Production OS execute supported browser/computer-use jobs natively inside `remote-worker-run` without requiring an external executor, while preserving external fallback and all existing worker lifecycle safeguards.

**Architecture:** Add a small native-executor selection layer that returns either a supported native handler or `unsupported`. `RemoteWorkerRunner` remains the lifecycle authority and supervises native execution in a `Future` so heartbeats, timeout, cancellation, stale fencing, runtime checkpoints, worktree verification, and completion/failure handling stay unified with the external path. The first native handler reuses the existing bounded browser loop and durable runtime files.

**Tech Stack:** Python 3.11/3.12, `concurrent.futures`, `threading.Event`, existing Production OS browser runtime, Playwright 1.63.0, pytest, Docker Compose.

**Spec:** `docs/superpowers/specs/2026-09-30-native-executor-design.md`

## Global Constraints

- `remote-worker-run` supports `--executor-mode auto|native|external`; default is `auto`.
- Native execution must not bypass worktree preparation, integration preflight, runtime/checkpoint setup, heartbeat, timeout, cancellation, stale-generation fencing, Git-result verification, or control-plane completion/failure.
- External fallback is allowed only before native execution begins.
- Native browser execution reuses `validate_browser_loop_config` and `run_browser_turn_loop`; no second browser runtime.
- No arbitrary browser `evaluate`.
- Browser navigation remains host allowlisted; private-network access remains explicit opt-in.
- A browser job with `persist_session=true` must fail closed if no persistent runtime workspace exists.
- Native handler cancellation is cooperative through a per-job `threading.Event`; no unsafe thread termination.
- Existing external deployments remain compatible.
- Existing CI regression gates remain green: Python 3.11/3.12, unit tests, Production E2E, wheel install, standard Docker smoke, browser-worker smoke, mobile Docker validation, CLI smoke.

## Review Focus

- `auto` mode with a native-capable job and an external command present must execute only the native path, never both; pin this in Task 4.
- A native handler that fails after starting must not fall back externally; pin this in Task 4.
- A persistent browser request without runtime state must fail deterministically instead of silently losing persistence; pin this in Task 3.
- Cancellation/stale/timeout while a native `Future` is running must fence further turns and avoid duplicate completion; pin this in Task 5.
- An unsupported job in `auto` mode with no external command must fail as `executor_unavailable`; pin this in Task 4.

---

### Task 1: Executor Mode Parsing and Startup Validation

**Files:**
- Modify: `src/production_os/cli.py`
- Modify: `src/production_os/remote_worker_runner.py`
- Test: `tests/test_remote_worker_runner.py`
- Test: `tests/test_cli.py` if that file already owns `remote-worker-run` parser tests; otherwise keep parser coverage in `tests/test_remote_worker_runner.py`

**Interfaces:**
- Consumes: existing `run_remote_worker_run(args: argparse.Namespace) -> int`.
- Produces: `executor_mode: Literal["auto", "native", "external"]` semantics passed into `RemoteWorkerRunner`; `executor_command: Sequence[str] | None` may be empty/`None` except in explicit `external` mode.

- [ ] **Step 1: Write failing parser/validation tests**

Add tests named:
- `test_remote_worker_run_defaults_executor_mode_to_auto`
- `test_remote_worker_run_allows_auto_without_executor_command`
- `test_remote_worker_run_rejects_external_mode_without_executor_command`
- `test_remote_worker_run_accepts_native_without_executor_command`

Assertions:
- default mode equals `"auto"`;
- `auto` and `native` accept an empty command;
- `external` without a command raises a deterministic `ValueError` mentioning that an executor command is required.

- [ ] **Step 2: Run the focused tests to verify RED**

Run:
```bash
pytest tests/test_remote_worker_runner.py -k "executor_mode or without_executor_command" -v
```

Expected: FAIL because `--executor-mode` does not exist and the runner currently rejects every empty command.

- [ ] **Step 3: Implement CLI and constructor validation**

In `src/production_os/cli.py`:
- add `--executor-mode` with choices `auto,native,external`, default `auto`;
- make `--executor-command` optional at parse time.

In `RemoteWorkerRunner.__init__(...)`:
- add `executor_mode: str = "auto"`;
- normalize/validate the mode;
- require a non-empty command only for `external`;
- store an empty command for `auto/native` when none is configured.

- [ ] **Step 4: Run focused tests to verify GREEN**

Run:
```bash
pytest tests/test_remote_worker_runner.py -k "executor_mode or without_executor_command" -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/production_os/cli.py src/production_os/remote_worker_runner.py tests/test_remote_worker_runner.py
git commit -m "feat(agents): add native executor modes"
```

---

### Task 2: Native Executor Selection Contract

**Files:**
- Create: `src/production_os/native_executor.py`
- Create: `tests/test_native_executor.py`

**Interfaces:**
- Consumes: claimed-job handoff dictionaries and optional runtime context.
- Produces:
  - `NativeExecutionContext` dataclass containing `job_key: str`, `handoff: dict[str, Any]`, `runtime_workspace: str | None`, `cancellation_event: threading.Event`, `artifacts_dir: str | None`;
  - `NativeExecutionDecision` dataclass with `supported: bool`, `handler_name: str | None`, `reason: str | None`;
  - `select_native_handler(handoff: dict[str, Any]) -> NativeExecutionDecision`;
  - `execute_native(context: NativeExecutionContext) -> dict[str, Any]`.

- [ ] **Step 1: Write failing selection tests**

Add tests:
- `test_select_native_handler_supports_browser_computer_contract`
- `test_select_native_handler_rejects_unknown_contracts`
- `test_select_native_handler_is_deterministic_when_multiple_contracts_exist`
- `test_execute_native_rejects_unsupported_context_without_side_effects`

Use a handoff containing `tool_contracts.browser_computer` and assert handler name `"browser_computer"`.

- [ ] **Step 2: Run focused tests to verify RED**

Run:
```bash
pytest tests/test_native_executor.py -v
```

Expected: FAIL because the module/interfaces do not exist.

- [ ] **Step 3: Implement the minimal registry/selection layer**

Create `src/production_os/native_executor.py` with:
- frozen dataclasses for the two interfaces above;
- deterministic selection based only on known `handoff.tool_contracts` keys;
- no shell-command derivation;
- `execute_native` dispatching only to registered native handlers;
- unsupported execution returning/raising a deterministic `native_executor_unsupported` condition suitable for runner normalization.

Do not add generic plugin discovery in this task.

- [ ] **Step 4: Run focused tests to verify GREEN**

Run:
```bash
pytest tests/test_native_executor.py -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/production_os/native_executor.py tests/test_native_executor.py
git commit -m "feat(agents): add native executor selection"
```

---

### Task 3: Native Browser Handler on Existing Browser Loop

**Files:**
- Modify: `src/production_os/native_executor.py`
- Modify: `src/production_os/browser_loop.py` only if a cancellation hook is not already exposed at the required boundary
- Test: `tests/test_native_executor.py`
- Test: `tests/test_browser_loop.py`

**Interfaces:**
- Consumes: `handoff["browser"] = {"config": dict, "turns": list[dict]}`.
- Produces: `execute_browser_native(context: NativeExecutionContext) -> dict[str, Any]` returning the existing executor-style envelope with `status`, optional `reason`, and `result`.
- Uses exact durable runtime filenames:
  - `browser-state.json`
  - `browser-session.json`
  - `browser-checkpoint.json`
  - `browser-artifacts/`

- [ ] **Step 1: Write failing native-browser validation tests**

Add tests:
- `test_native_browser_handler_executes_submitted_turns`
- `test_native_browser_handler_uses_runtime_workspace_paths`
- `test_native_browser_handler_rejects_persistent_session_without_runtime`
- `test_native_browser_handler_rejects_missing_browser_request`
- `test_native_browser_handler_preserves_loop_failure_reason`

Stub `run_browser_turn_loop` for the first four tests so they validate handoff parsing/path construction without launching Chromium.

- [ ] **Step 2: Add a failing cancellation-boundary test to browser loop**

Add `test_browser_loop_stops_before_next_turn_when_cancelled`.

The fake executor sets the cancellation event after the first turn. Assert only the first turn executes and the returned loop summary is terminal without starting turn two.

- [ ] **Step 3: Run focused tests to verify RED**

Run:
```bash
pytest tests/test_native_executor.py tests/test_browser_loop.py -k "native_browser or stops_before_next_turn" -v
```

Expected: FAIL because the browser native handler/cancellation integration does not exist.

- [ ] **Step 4: Implement browser-native execution**

In `native_executor.py`:
- validate `handoff.browser.config` with `validate_browser_loop_config`;
- serialize the submitted finite turn list to an in-memory JSONL input stream;
- call `run_browser_turn_loop` with the runtime-derived storage/session/checkpoint/artifact paths;
- require runtime workspace when config requests `persist_session=true`;
- normalize browser-loop output into the worker executor result envelope.

If needed in `browser_loop.py`, add a `cancelled: Callable[[], bool] | None = None` or equivalent event check that is evaluated before each turn and before each new plan starts.

- [ ] **Step 5: Run focused tests to verify GREEN**

Run:
```bash
pytest tests/test_native_executor.py tests/test_browser_loop.py -k "native_browser or stops_before_next_turn" -v
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add src/production_os/native_executor.py src/production_os/browser_loop.py tests/test_native_executor.py tests/test_browser_loop.py
git commit -m "feat(browser): add native browser executor"
```

---

### Task 4: Runner Native/External Path Selection

**Files:**
- Modify: `src/production_os/remote_worker_runner.py`
- Test: `tests/test_remote_worker_runner.py`

**Interfaces:**
- Consumes:
  - `select_native_handler(handoff) -> NativeExecutionDecision`;
  - `execute_native(context) -> dict[str, Any]`.
- Produces: one execution-path choice per claimed job before side effects begin:
  - native;
  - external;
  - unavailable.

- [ ] **Step 1: Write failing path-selection tests**

Add:
- `test_auto_mode_prefers_native_browser_over_external_executor`
- `test_auto_mode_falls_back_to_external_when_native_is_unsupported`
- `test_native_mode_rejects_unsupported_job`
- `test_auto_mode_without_any_executor_fails_executor_unavailable`
- `test_native_runtime_failure_never_falls_back_external`

Use fakes/mocks to count calls to `execute_native` and `subprocess.Popen`. The last test must assert external call count remains zero after native execution has begun and failed.

- [ ] **Step 2: Run focused tests to verify RED**

Run:
```bash
pytest tests/test_remote_worker_runner.py -k "auto_mode or native_mode or executor_unavailable or never_falls_back" -v
```

Expected: FAIL because every job currently takes the subprocess path.

- [ ] **Step 3: Implement pre-execution path selection**

In `RemoteWorkerRunner`:
- add a small internal method `_select_execution_path(job: RemoteJob) -> str` returning `"native"`, `"external"`, or `"unavailable"`;
- select before launching any native handler or subprocess;
- in `auto`, prefer native support;
- only choose external fallback when native is unsupported and a command exists;
- map unsupported `native` mode to `native_executor_unsupported`;
- map no available executor to `executor_unavailable`;
- never change path after native execution starts.

Do not yet add asynchronous native supervision; call the native interface directly only in tests that finish immediately. Task 5 replaces that direct call with supervised execution.

- [ ] **Step 4: Run focused tests to verify GREEN**

Run:
```bash
pytest tests/test_remote_worker_runner.py -k "auto_mode or native_mode or executor_unavailable or never_falls_back" -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/production_os/remote_worker_runner.py tests/test_remote_worker_runner.py
git commit -m "feat(agents): route jobs to native execution"
```

---

### Task 5: Supervised Native Future, Heartbeats, Fencing and Cancellation

**Files:**
- Modify: `src/production_os/remote_worker_runner.py`
- Test: `tests/test_remote_worker_runner.py`

**Interfaces:**
- Consumes: `execute_native(context)`.
- Produces: `_run_native_supervised(...) -> dict[str, Any]` or equivalent internal helper that:
  - runs native execution in a `Future`;
  - accepts a per-job `threading.Event`;
  - keeps the existing heartbeat cadence;
  - enforces the existing executor timeout;
  - observes stale-generation and cancel state;
  - returns one normalized terminal payload.

- [ ] **Step 1: Write failing supervision tests**

Add:
- `test_native_execution_heartbeats_while_future_is_running`
- `test_native_execution_timeout_sets_cancel_event_and_fails_once`
- `test_native_execution_cancel_request_sets_event_and_does_not_complete`
- `test_native_execution_stale_generation_sets_event_and_checkpoints_stale`
- `test_native_execution_worker_shutdown_sets_event_and_abandons`
- `test_native_execution_control_plane_outage_abandons_after_existing_failure_threshold`

Use a blocking fake native handler that waits on the provided event.

- [ ] **Step 2: Run focused tests to verify RED**

Run:
```bash
pytest tests/test_remote_worker_runner.py -k "native_execution_" -v
```

Expected: FAIL because native execution has no supervision loop.

- [ ] **Step 3: Implement supervised native execution**

Implement a runner helper around a `concurrent.futures.Future` completed by one dedicated daemon `threading.Thread` per native job:
- create the `Future` before starting the thread;
- the thread calls `execute_native(context)` and sets the future result/exception exactly once;
- the runner waits at most `heartbeat_interval_seconds` per supervision tick;
- on each tick call existing checkpoint/heartbeat/control inspection;
- set the cancellation event on timeout, cancellation, stale state, shutdown, or control-plane abandonment;
- use a bounded cancellation grace period before returning abandoned/fenced state;
- never join an uncooperative native thread indefinitely;
- do not start the external fallback.

Do not use a short-lived `ThreadPoolExecutor` context manager for this helper: its shutdown semantics may wait for a running handler and defeat the bounded cancellation requirement.

Reuse existing deterministic reasons where applicable; use `native_executor_failed` only for native handler failures that are not a more specific validation/runtime reason.

- [ ] **Step 4: Run focused tests to verify GREEN**

Run:
```bash
pytest tests/test_remote_worker_runner.py -k "native_execution_" -v
```

Expected: PASS.

- [ ] **Step 5: Run the complete runner suite**

Run:
```bash
pytest tests/test_remote_worker_runner.py -v
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add src/production_os/remote_worker_runner.py tests/test_remote_worker_runner.py
git commit -m "feat(agents): supervise native executor lifecycle"
```

---

### Task 6: Preserve Git Verification and Completion Semantics for Native Jobs

**Files:**
- Modify: `src/production_os/remote_worker_runner.py`
- Test: `tests/test_remote_worker_runner.py`

**Interfaces:**
- Consumes: normalized native/external executor payloads.
- Produces: a single shared post-execution result path for:
  - worktree cleanliness/history verification;
  - authoritative `commit_shas` and `changed_files`;
  - control-plane complete/fail;
  - worktree cleanup and integrated branch pruning.

- [ ] **Step 1: Write failing parity tests**

Add:
- `test_native_success_still_rejects_dirty_managed_worktree`
- `test_native_success_still_rejects_diverged_history`
- `test_native_success_reports_git_derived_commit_evidence`
- `test_native_failure_uses_existing_control_plane_failure_path`

Use the existing temporary-Git helpers from `tests/test_remote_worker_runner.py`.

- [ ] **Step 2: Run focused tests to verify RED**

Run:
```bash
pytest tests/test_remote_worker_runner.py -k "native_success or native_failure_uses_existing" -v
```

Expected: at least one FAIL if native and external result processing remain duplicated.

- [ ] **Step 3: Refactor only enough to share post-execution handling**

Extract internal helpers as needed, for example:
- `_verify_executor_git_result(...)`;
- `_finalize_executor_payload(...)`.

Both native and external paths must feed the same finalization code. Do not change the control-plane API.

- [ ] **Step 4: Run focused and full runner tests**

Run:
```bash
pytest tests/test_remote_worker_runner.py -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/production_os/remote_worker_runner.py tests/test_remote_worker_runner.py
git commit -m "refactor(agents): unify executor result verification"
```

---

### Task 7: Browser Worker Compose Without Mandatory External Executor

**Files:**
- Modify: `compose.worker.yaml`
- Modify: `docs/remote-worker-executor-protocol.md`
- Test: `tests/test_worker_compose_deployment.py`
- Test: `tests/test_browser_worker_image.py` if image-level assertions belong there

**Interfaces:**
- Consumes: Task 1 executor-mode CLI.
- Produces: browser specialist service configured in `auto` mode without requiring a non-empty external executor command.

- [ ] **Step 1: Write failing Compose tests**

Add:
- `test_browser_worker_uses_auto_executor_mode`
- `test_browser_worker_does_not_require_external_executor_command`
- `test_non_browser_specialists_keep_external_executor_configuration`

Assert the browser service includes:
```yaml
--executor-mode
auto
```

and does not require `--executor-command` when the environment variable is empty. Code/debug/review remain explicitly compatible with the external command path.

- [ ] **Step 2: Run focused tests to verify RED**

Run:
```bash
pytest tests/test_worker_compose_deployment.py -k "browser_worker" -v
```

Expected: FAIL against current Compose.

- [ ] **Step 3: Update Compose and protocol documentation**

In `compose.worker.yaml`:
- configure browser worker `--executor-mode auto`;
- keep the existing `--executor-command ${PRODUCTION_OS_WORKER_EXECUTOR_COMMAND:-}` pair as the optional fallback;
- rely on Task 1 startup validation to treat the empty-string command as “no external executor configured” in `auto` mode.

In `docs/remote-worker-executor-protocol.md`, document:
- native/auto/external modes;
- native browser request shape;
- fallback rule;
- no fallback after native execution begins;
- deterministic failure reasons.

- [ ] **Step 4: Run focused tests to verify GREEN**

Run:
```bash
pytest tests/test_worker_compose_deployment.py tests/test_browser_worker_image.py -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add compose.worker.yaml docs/remote-worker-executor-protocol.md tests/test_worker_compose_deployment.py tests/test_browser_worker_image.py
git commit -m "feat(browser): enable executorless native browser worker"
```

---

### Task 8: Native Browser Worker End-to-End Recovery Test

**Files:**
- Create or modify: `tests/test_native_browser_worker_e2e.py`
- Modify production files only if the test exposes a concrete integration bug

**Interfaces:**
- Consumes: full stack from Tasks 1-7.
- Produces: executable proof that a browser-specialist worker can complete a native browser job with no external executor command.

- [ ] **Step 1: Write failing E2E test for executorless browser completion**

The test must:
1. start/use the existing test control plane;
2. queue a job whose handoff contains `tool_contracts.browser_computer` and a finite `handoff.browser` request;
3. construct `RemoteWorkerRunner(..., executor_mode="auto", executor_command=[])`;
4. use a mocked `run_browser_turn_loop` boundary for this runner-level E2E so the test proves dispatch/lifecycle selection without requiring Chromium;
5. run one worker cycle;
6. assert job completion and no external subprocess invocation.

Add a separate browser-image smoke assertion in Task 7 to retain real Chromium/Playwright provisioning coverage.

Name: `test_native_browser_worker_completes_without_external_executor`.

- [ ] **Step 2: Add recovery/fencing E2E test**

Name: `test_native_browser_worker_reuses_durable_runtime_without_replaying_completed_side_effect`.

Use the existing browser-loop durable manifest/checkpoint behavior to prove that a completed non-replayable turn is not executed twice after a simulated interruption.

- [ ] **Step 3: Run E2E tests to verify RED/GREEN as appropriate**

Run:
```bash
pytest tests/test_native_browser_worker_e2e.py -v
```

Expected after Tasks 1-7: PASS. If it fails, fix only the exposed integration defect with a regression assertion before changing production code.

- [ ] **Step 4: Run all targeted native/browser/runner suites**

Run:
```bash
pytest tests/test_native_executor.py tests/test_browser_loop.py tests/test_browser_computer.py tests/test_remote_worker_runner.py tests/test_worker_compose_deployment.py tests/test_native_browser_worker_e2e.py -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add tests/test_native_browser_worker_e2e.py
git commit -m "test(browser): prove native worker end to end"
```

---

### Task 9: Full Regression Verification and Delivery

**Files:**
- No production changes unless a regression is proven by the verification commands.
- Update: PR description/review notes only.

**Interfaces:**
- Consumes: completed implementation branch.
- Produces: CI-ready branch with documented TDD evidence and no unresolved review findings.

- [ ] **Step 1: Run full local test suite**

Run:
```bash
pytest -q
```

Expected: all tests pass.

- [ ] **Step 2: Run compile/package checks used by CI**

Run the repository's existing compile/build commands from `.github/workflows` rather than inventing alternatives.

Expected: PASS.

- [ ] **Step 3: Push and verify CI**

Required green gates:
- `test`;
- `python-compat (3.11)`;
- `python-compat (3.12)`;
- Production E2E;
- wheel install;
- Docker image smoke;
- browser worker smoke;
- mobile worker Dockerfile validation;
- CLI smoke.

- [ ] **Step 4: Request fresh code review**

Request review only after the final CI head is green. Resolve every technically valid blocking finding with a regression test.

- [ ] **Step 5: Merge with exact head SHA**

Use squash merge with `expected_head_sha` equal to the reviewed green commit.

- [ ] **Step 6: Verify post-merge main**

Confirm:
- PR state is merged;
- `main` contains the squash commit;
- any automatic context-refresh commit does not hide a failed merge;
- the native browser worker path remains covered by CI.
