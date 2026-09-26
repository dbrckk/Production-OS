# Release 55 Worker Operations Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make deployed remote runners acknowledge and obey persistent pause/resume/drain state end-to-end.

**Architecture:** Reuse DashboardControl as the sole desired-state store and `/v1/workers/heartbeat` as the acknowledgement channel. Add a small runner-side control-state machine that consumes heartbeat control state, echoes acknowledgement on subsequent heartbeats, and suppresses claims whenever the desired state is not active.

**Tech Stack:** Python 3.11/3.12, stdlib HTTP/threading/concurrent futures, pytest.

**Spec:** `docs/superpowers/specs/2026-09-26-release-55-worker-operations.md`

## Global Constraints

- No new mutation endpoint or credential scope.
- Preserve existing worker identity checks and shutdown semantics.
- Pause/drain never terminate active executors.
- Existing server claim admission remains authoritative.

## Review Focus

- Control request arriving while the runner has active concurrent jobs: jobs finish, no replacement claim occurs.
- Resume after pause/drain: acknowledgement becomes durable and claiming resumes.
- Heartbeat failure during state transition: runner must not invent an acknowledgement.
- Process shutdown while draining: shutdown semantics win and active work is recoverable.
- Stale/dead detection: operator desired state must not overwrite heartbeat-derived liveness.

---

### Task 1: Runner control-state acknowledgement

**Files:**
- Modify: `src/production_os/remote_worker_runner.py`
- Test: `tests/test_remote_worker_runner.py`

**Interfaces:**
- Consumes: `RemoteWorkerClient.heartbeat(..., control_state=...) -> dict`
- Produces: runner-observed desired state and acknowledgement through the existing heartbeat protocol.

- [ ] Add failing tests proving pause/drain are observed and acknowledged without terminating active executors.
- [ ] Run the focused tests and verify RED.
- [ ] Implement runner control-state tracking and heartbeat acknowledgement.
- [ ] Run focused tests and verify GREEN.
- [ ] Commit.

### Task 2: Admission behavior across pause/drain/resume

**Files:**
- Modify: `src/production_os/remote_worker_runner.py`
- Test: `tests/test_remote_worker_runner.py`
- Test: `tests/test_remote_worker.py`

**Interfaces:**
- Consumes: Task 1 observed desired state.
- Produces: claim loop that claims only in `active` state.

- [ ] Add failing integration tests: paused runner leaves queued work untouched; draining runner completes active work without replacement; resumed runner claims again.
- [ ] Run focused tests and verify RED.
- [ ] Gate runner claims on observed desired state while retaining server-side admission as defense in depth.
- [ ] Run focused tests and verify GREEN.
- [ ] Commit.

### Task 3: Operational contract and full qualification

**Files:**
- Modify: `README.md`
- Modify: `.ai/project-state.md` if present and appropriate.

**Interfaces:**
- Consumes: completed runner behavior.
- Produces: documented Release 55 operator semantics.

- [ ] Document pause/resume/drain acknowledgement and liveness separation.
- [ ] Run worker/control/dashboard focused suites.
- [ ] Run full test suite and compile checks.
- [ ] Push branch and require Python 3.11/3.12, Production E2E, package/wheel/Docker/CLI smoke checks green.
- [ ] Review final diff for duplicate control systems, credential changes, or shutdown regressions.