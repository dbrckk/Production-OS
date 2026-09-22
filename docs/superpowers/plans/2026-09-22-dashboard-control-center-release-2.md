# Dashboard Control Center Release 2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the Release-1 observability dashboard into a safe operational control center with durable worker desired state, pause/resume/drain, job-scoped cooperative cancellation, retry, GitHub Actions kick, richer live logs, and operator-facing alerts.

**Architecture:** Control intent is persisted independently from observed runtime state. Production-OS is authoritative for desired worker/job state, while workers acknowledge and enforce that state at safe boundaries; GitHub Actions wake-up uses the existing GitHub workflow-dispatch path when server-side credentials are configured and otherwise reports the five-minute schedule fallback honestly. Dashboard controls call operator-only APIs and display requested vs acknowledged state separately.

**Tech Stack:** Python 3.11+, stdlib HTTP server, SQLite/PostgreSQL schema-v9 tables from Release 1, pytest, GitHub REST workflow dispatch, AI Dev Server Python worker, vanilla HTML/CSS/JavaScript.

**Spec:** `docs/superpowers/specs/2026-09-22-dashboard-observability-control-center-design.md`

## Global Constraints

- Release 2 starts only after Release 1 observability APIs, schema v9, telemetry, and dashboard read views are passing.
- Worker control state uses `worker_control_state`; job cancellation intent uses `job_control_state`.
- Worker-level desired states are exactly `active`, `paused`, and `draining`.
- Job-level desired states are exactly `active` and `cancel_requested`; authoritative terminal outcome stays in `jobs.status`.
- Every control endpoint requires `operator`.
- A requested action is not presented as remotely acknowledged until a worker heartbeat/telemetry/result or GitHub dispatch result proves it.
- Pause does not interrupt the current task; drain stops new claims and lets active tasks finish.
- Cancellation is cooperative for active jobs and immediate only for queued jobs.
- Retry never overwrites the failed execution and remains constrained by workflow generation and max-attempt rules.
- GitHub Actions kick is immediate only when the Production-OS server has a valid server-side GitHub dispatch credential; otherwise return `scheduled_fallback`.
- No worker/operator/API/GitHub token is returned to the browser or persisted in logs.
- Existing workflow-level cancel behavior must remain backward compatible.
- Do not add a required paid service.

## Review Focus

- A worker with `max_concurrency > 1` must cancel only the explicitly targeted job; no worker-wide cancel flag may ambiguously stop sibling work.
- A race between cancel and complete must converge to one valid terminal state without resurrecting or retrying stale work.
- Paused/draining workers that restart must re-read durable desired state before claiming new work.
- Repeated retry requests must not create duplicate active attempts or bypass `max_attempts`.
- Kick must not report success when GitHub dispatch fails, credentials are absent, or only the scheduled five-minute fallback exists.

---

## File Structure

### Production-OS files created

- `src/production_os/dashboard_control.py` — worker/job control state machine and control-service API.
- `src/production_os/dashboard_alerts.py` — bounded alert/anomaly derivation from observability facts.
- `tests/test_dashboard_control.py`
- `tests/test_dashboard_control_api.py`
- `tests/test_dashboard_alerts.py`
- `tests/test_dashboard_control_e2e.py`

### Production-OS files modified

- `src/production_os/dashboard_store.py` — durable control-state CRUD and acknowledgement timestamps.
- `src/production_os/dashboard_service.py` — control availability, requested/acknowledged state, alerts.
- `src/production_os/control_plane.py` — operator-only control routes and claim filtering.
- `src/production_os/github_client.py:198-217` — use existing `dispatch_workflow` from control service.
- `src/production_os/dashboard_ui.py` — control tab, confirmations, state feedback, alert cards.
- `src/production_os/workflow_engine.py:921-1200` — retry/cancel integration without corrupting workflow generation.
- `src/production_os/sqlite_backend.py:1003-1340`
- `src/production_os/postgres_backend.py:1047-1409`
- `tests/test_dashboard_api.py`
- `tests/test_dashboard_ui_v3.py`
- `tests/test_workflow_engine.py`
- `tests/test_workflow_api.py`

### AI Dev Server files modified

- `studio/production_os_worker.py:97-269, 607-810` — read desired state/cancel directives and enforce them before claims and at heartbeat boundaries.
- `tests/test_production_os_worker_runtime.py`
- `.github/workflows/production-os-actions-worker.yml` — retain workflow_dispatch compatibility; no new mandatory secret.

---

### Task 1: Implement durable worker/job control state service

**Files:**
- Create: `src/production_os/dashboard_control.py`
- Modify: `src/production_os/dashboard_store.py`
- Create: `tests/test_dashboard_control.py`

**Interfaces:**
- Consumes: schema-v9 `worker_control_state` and `job_control_state`.
- Produces:
  - `DashboardControl(store, queue, workflows, *, github=None, actions_repository=None, actions_workflow=None)`
  - `set_worker_state(worker_id: str, desired_state: str, *, requested_by: str, reason: str | None = None) -> dict`
  - `acknowledge_worker_state(worker_id: str, desired_state: str, *, at: str | None = None) -> dict`
  - `worker_state(worker_id: str) -> dict`
  - `request_job_cancel(job_key: str, *, requested_by: str, reason: str | None = None) -> dict`
  - `acknowledge_job_cancel(job_key: str, *, at: str | None = None) -> dict`
  - `retry_job(job_key: str, *, requested_by: str) -> dict`.

- [ ] **Step 1: Write failing state-machine tests**

```python
def test_missing_worker_control_row_defaults_to_active(store, queue, workflows):
    control = DashboardControl(store, queue, workflows)
    state = control.worker_state("worker-a")
    assert state["desired_state"] == "active"
    assert state["persisted"] is False


def test_pause_and_drain_are_durable(store, queue, workflows):
    control = DashboardControl(store, queue, workflows)
    paused = control.set_worker_state(
        "worker-a", "paused", requested_by="operator:dashboard"
    )
    assert paused["desired_state"] == "paused"

    drained = control.set_worker_state(
        "worker-a", "draining", requested_by="operator:dashboard"
    )
    assert drained["desired_state"] == "draining"
    assert control.worker_state("worker-a")["desired_state"] == "draining"
```

Also test invalid desired state => `ValueError("invalid worker desired state")`.

- [ ] **Step 2: Run tests and verify failure**

```bash
pytest tests/test_dashboard_control.py -q
```

Expected: missing module/class.

- [ ] **Step 3: Add store CRUD**

Implement exact methods in `DashboardStore`:

```python
def get_worker_control(self, worker_id: str) -> dict | None: ...
def set_worker_control(
    self,
    worker_id: str,
    desired_state: str,
    *,
    requested_by: str,
    reason: str | None = None,
    at: str | None = None,
) -> dict: ...

def get_job_control(self, job_key: str) -> dict | None: ...
def set_job_control(
    self,
    job_key: str,
    desired_state: str,
    *,
    requested_by: str,
    reason: str | None = None,
    at: str | None = None,
) -> dict: ...

def acknowledge_worker_control(self, worker_id: str, desired_state: str, *, at: str | None = None) -> dict: ...
def acknowledge_job_control(self, job_key: str, *, at: str | None = None) -> dict: ...
```

Use `INSERT ... ON CONFLICT ... DO UPDATE` with backend placeholder translation already used by `DashboardStore`.

`acknowledge_worker_control` does not add a new schema column: it verifies the supplied state equals the durable `desired_state`, preserves `requested_at`, and advances `updated_at`. `worker_state` exposes `acknowledged_at = updated_at` only when `updated_at != requested_at`; otherwise it returns null. This keeps the approved schema unchanged while distinguishing request time from worker acknowledgement time.

- [ ] **Step 4: Implement control validation**

```python
WORKER_STATES = {"active", "paused", "draining"}
JOB_STATES = {"active", "cancel_requested"}

class DashboardControlError(RuntimeError):
    pass
```

`worker_state` returns a virtual active record when no row exists:

```python
{
    "worker_id": worker_id,
    "desired_state": "active",
    "persisted": False,
    "requested_at": None,
    "acknowledged_at": None,
}
```

- [ ] **Step 5: Run tests**

```bash
pytest tests/test_dashboard_control.py tests/test_dashboard_store.py -q
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add src/production_os/dashboard_control.py src/production_os/dashboard_store.py tests/test_dashboard_control.py
git commit -m "feat(control): persist worker and job desired state"
```

---

### Task 2: Prevent paused/draining workers from claiming new jobs

**Files:**
- Modify: `src/production_os/control_plane.py: worker heartbeat and claim routes`
- Modify: `src/production_os/dashboard_service.py`
- Modify: `studio/production_os_worker.py:607-810` in `dbrckk/ai-dev-server`
- Modify: `tests/test_dashboard_control.py`
- Modify: `tests/test_portfolio_claim_api.py`
- Modify: `tests/test_production_os_worker_runtime.py` in `dbrckk/ai-dev-server`

**Interfaces:**
- Consumes: `DashboardControl.worker_state`.
- Produces: heartbeat control envelope, worker acknowledgement via optional `control_state`, and claim behavior that returns no job for paused/draining workers.

- [ ] **Step 1: Write failing claim-gating tests**

```python
def test_paused_worker_cannot_claim_but_can_heartbeat(...):
    pause_worker("worker-a")
    status, payload = claim("worker-a")
    assert status == 204

    status, heartbeat = heartbeat_worker("worker-a", active_job_keys=[])
    assert status == 200
    assert heartbeat["worker"]["status"] == "online"


def test_draining_worker_finishes_current_job_but_claims_no_second_job(...):
    first = claim_and_ack("worker-a")
    set_worker_state("worker-a", "draining")
    enqueue_second_job()

    assert heartbeat_worker("worker-a", [first["key"]])[0] == 200
    assert claim("worker-a")[0] == 204
```

- [ ] **Step 2: Run tests and verify failure**

```bash
pytest tests/test_dashboard_control.py tests/test_portfolio_claim_api.py -q
```

- [ ] **Step 3: Return desired state from heartbeat and record explicit worker acknowledgement**

Heartbeat response includes:

```python
"control": {
    "worker": control.dashboard_control.worker_state(worker_id),
    "jobs": {...},
}
```

Heartbeat request accepts optional `control_state`. When it exactly matches the current durable desired state, call:

```python
control.dashboard_store.acknowledge_worker_control(
    worker_id,
    control_state,
)
```

A mismatched/stale state is ignored for acknowledgement and the current desired state is returned again.

In AI Dev Server, `run_once` performs a pre-claim heartbeat. If the response requests `paused` or `draining`, it immediately sends one acknowledgement heartbeat with `control_state` set to that value, then returns without calling `claim`. This lets ephemeral GitHub Actions workers acknowledge a pause/drain even when they do no work.

- [ ] **Step 4: Gate before optimizer/queue claim**

In the worker claim route:

```python
desired = control.dashboard_control.worker_state(worker_id)
if desired["desired_state"] in {"paused", "draining"}:
    self._send(HTTPStatus.NO_CONTENT, {})
    return
```

Do this before ranking candidates so paused workers do not consume optimizer work or modify queue state.

- [ ] **Step 5: Surface desired/observed state together**

`DashboardService.worker_detail` returns:

```python
{
    "status": worker.status,
    "desired_state": desired["desired_state"],
    "control_requested_at": desired.get("requested_at"),
    "control_reason": desired.get("reason"),
}
```

If draining and active tasks == 0, derive display state `drained` without rewriting `workers.status`.

- [ ] **Step 6: Run tests**

Production-OS:

```bash
pytest tests/test_dashboard_control.py tests/test_portfolio_claim_api.py tests/test_dashboard_api.py -q
```

AI Dev Server:

```bash
python -m unittest tests.test_production_os_worker_runtime -v
```

Expected: PASS.

- [ ] **Step 7: Commit**

Production-OS:

```bash
git add src/production_os/control_plane.py src/production_os/dashboard_service.py tests/test_dashboard_control.py tests/test_portfolio_claim_api.py tests/test_dashboard_api.py
git commit -m "feat(control): honor pause and drain during claims"
```

AI Dev Server:

```bash
git add studio/production_os_worker.py tests/test_production_os_worker_runtime.py
git commit -m "feat(production-os): honor worker desired state"
```

---

### Task 3: Expose operator-only worker control API with requested-vs-acknowledged semantics

**Files:**
- Modify: `src/production_os/control_plane.py`
- Create: `tests/test_dashboard_control_api.py`

**Interfaces:**
- Consumes: `DashboardControl`.
- Produces: `POST /v1/dashboard/workers/{worker_id}/control` for `pause|resume|drain|cancel-current|kick`.

- [ ] **Step 1: Write failing authorization and response tests**

```python
def test_worker_control_requires_operator(...):
    status, _ = post(
        "/v1/dashboard/workers/worker-a/control",
        viewer_token,
        {"action": "pause"},
    )
    assert status == 403


def test_pause_returns_requested_state_not_fake_remote_ack(...):
    status, payload = post(
        "/v1/dashboard/workers/worker-a/control",
        operator_token,
        {"action": "pause"},
    )
    assert status == 202
    assert payload["accepted"] is True
    assert payload["desired_state"] == "paused"
    assert payload["acknowledged"] is False
```

Add invalid action => 400.

- [ ] **Step 2: Run tests and verify failure**

```bash
pytest tests/test_dashboard_control_api.py -q
```

- [ ] **Step 3: Implement pause/resume/drain route**

Map:

```python
WORKER_ACTION_STATE = {
    "pause": "paused",
    "resume": "active",
    "drain": "draining",
}
```

Use `HTTPStatus.ACCEPTED` because this records desired state, not remote completion.

- [ ] **Step 4: Make `cancel-current` require an explicit job key**

Request:

```json
{
  "action": "cancel-current",
  "job_key": "job-abc123"
}
```

Validate:
1. job exists;
2. `claimed_by == worker_id`;
3. job is active/claimed/acked;
4. then call `request_job_cancel`.

If a worker has multiple active jobs and `job_key` is absent, return 400; never pick the first one.

- [ ] **Step 5: Run API tests**

```bash
pytest tests/test_dashboard_control_api.py tests/test_control_plane.py -q
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add src/production_os/control_plane.py tests/test_dashboard_control_api.py
git commit -m "feat(control): add operator worker control API"
```

---

### Task 4: Implement cooperative active-job cancellation end to end

**Files:**
- Modify: `src/production_os/control_plane.py`
- Modify: `src/production_os/dashboard_control.py`
- Modify: `src/production_os/dashboard_store.py`
- Modify: `src/production_os/sqlite_backend.py:1239-1298`
- Modify: `src/production_os/postgres_backend.py:1300-1364`
- Modify: `studio/production_os_worker.py` in `dbrckk/ai-dev-server`
- Modify: `tests/test_dashboard_control.py`
- Modify: `tests/test_dashboard_control_api.py`
- Modify: `tests/test_production_os_worker_runtime.py`

**Interfaces:**
- Consumes: job-scoped `cancel_requested`.
- Produces:
  - worker control directives included in heartbeat/telemetry responses;
  - safe cancellation acknowledgement;
  - job terminal status `cancelled` only after acknowledgement/reconciliation.

- [ ] **Step 1: Write failing multi-job cancellation tests**

```python
def test_cancel_request_targets_only_named_job(...):
    job_a = active_job("worker-a", "job-a")
    job_b = active_job("worker-a", "job-b")

    request_cancel("job-a")

    assert control.get_job_control("job-a")["desired_state"] == "cancel_requested"
    assert control.get_job_control("job-b") is None
```

Worker test:

```python
def test_worker_stops_only_when_current_job_has_cancel_directive():
    fake = _FakeClient(sample_job())
    fake.heartbeat_response = {
        "control": {
            "jobs": {"job-abc123": {"desired_state": "cancel_requested"}}
        }
    }
    result = run_once(..., client=fake, run_project=cooperative_runner)
    assert result["status"] == "cancelled"
    assert any(call[0] == "cancelled" for call in fake.calls)
```

- [ ] **Step 2: Run tests and verify failure**

```bash
pytest tests/test_dashboard_control.py tests/test_dashboard_control_api.py -q
python -m unittest tests.test_production_os_worker_runtime -v
```

- [ ] **Step 3: Return control directives from heartbeat**

Heartbeat response adds:

```python
"control": {
    "worker": {
        "desired_state": control.dashboard_control.worker_state(worker_id)["desired_state"]
    },
    "jobs": {
        key: control.dashboard_control.job_state(key)
        for key in active_job_keys
    },
}
```

Only active keys declared by that worker are returned.

- [ ] **Step 4: Add worker-side cancellation signal**

In AI Dev Server introduce:

```python
class JobCancellationRequested(RuntimeError):
    pass
```

The heartbeat thread sets a `threading.Event` when the active job directive is `cancel_requested`.

Pass a cancellation callback to the execution wrapper where possible:

```python
def cancelled() -> bool:
    return cancel_event.is_set()
```

At safe boundaries already controlled by `run_once`:
- before starting `run_project`;
- after each heartbeat;
- before completion submission.

If the underlying long-running runner cannot be interrupted inside a single external subprocess, do not kill it unsafely; mark cancellation as pending until the next safe boundary.

- [ ] **Step 5: Add explicit queue cancellation primitives and cancelled endpoint/client action**

Add queue methods with SQLite/PostgreSQL parity:

```python
def cancel(self, key: str, worker_id: str) -> dict:
    return self._transition(
        key, worker_id, {"claimed", "acked"},
        "cancelled", "job-cancelled", completed=True,
    )

def cancel_queued(self, key: str) -> dict:
    # transactionally require status == "queued", set terminal cancelled,
    # completed_at/updated_at = now, and append `job-cancelled` event.
    ...
```

`cancel_queued` must not accept a worker ID and must fail if the job has already been claimed. Replace the comment-body implementation above with the backend's existing transaction/placeholder style; the test must assert the SQL transition and emitted event.

Then add the worker acknowledgement route:

Production-OS:

```text
POST /v1/jobs/cancelled
```

Worker payload:

```json
{
  "key": "job-abc123",
  "worker_id": "worker-a",
  "duration_seconds": 12.5,
  "reason": "operator cancellation"
}
```

Route requires `worker`, validates claim ownership and pending job control, calls `queue.cancel(key, worker_id)`, acknowledges control, records execution terminal state `cancelled`, and correlates the workflow task.

Dashboard job action `cancel` calls `queue.cancel_queued(key)` immediately only when current status is `queued`; for `claimed`/`acked` it creates `cancel_requested` and waits for the worker acknowledgement path.

AI Dev Server adds `ProductionOSClient.cancelled(payload)`.

- [ ] **Step 6: Resolve cancel-vs-complete race transactionally**

If completion wins first, a later cancellation acknowledgement returns 409 and must not rewrite success.

If cancellation wins first, a later completion returns 409 and must not resurrect the job.

Pin both orders in tests.

- [ ] **Step 7: Run tests**

```bash
pytest tests/test_dashboard_control.py tests/test_dashboard_control_api.py tests/test_workflow_api.py -q
python -m unittest tests.test_production_os_worker_runtime -v
```

Expected: PASS.

- [ ] **Step 8: Commit in both repositories**

Production-OS:

```bash
git add src/production_os/control_plane.py src/production_os/dashboard_control.py src/production_os/dashboard_store.py src/production_os/sqlite_backend.py src/production_os/postgres_backend.py tests/test_dashboard_control.py tests/test_dashboard_control_api.py tests/test_workflow_api.py
git commit -m "feat(control): add cooperative job cancellation"
```

AI Dev Server:

```bash
git add studio/production_os_worker.py tests/test_production_os_worker_runtime.py
git commit -m "feat(production-os): honor job cancellation directives"
```

---

### Task 5: Implement safe retry lineage without bypassing workflow attempt limits

**Files:**
- Modify: `src/production_os/dashboard_control.py`
- Modify: `src/production_os/workflow_engine.py:1080-1200`
- Modify: `src/production_os/control_plane.py`
- Modify: `tests/test_dashboard_control.py`
- Modify: `tests/test_dashboard_control_api.py`
- Modify: `tests/test_workflow_engine.py`

**Interfaces:**
- Consumes: terminal failed/cancelled job and workflow task metadata.
- Produces: `POST /v1/dashboard/jobs/{job_key}/control {"action":"retry"}`.

- [ ] **Step 1: Write failing retry tests**

```python
def test_retry_creates_new_attempt_and_preserves_failed_execution(...):
    failed = failed_job_for_task("wf-1", "build", delivery_attempt=1)
    status, payload = retry_job(failed["key"])

    assert status == 202
    assert payload["retry_of"] == failed["key"]
    assert payload["job"]["delivery_attempt"] == 2
    assert execution_history(failed["key"])[0]["status"] == "failed"


def test_repeated_retry_request_is_idempotent_while_retry_active(...):
    first = retry_job("job-1")
    second = retry_job("job-1")
    assert first["job"]["key"] == second["job"]["key"]
```

Add tests for:
- succeeded job cannot retry;
- stale workflow generation cannot retry;
- max attempts reached => 409;
- blocked workflow dependencies remain respected.

- [ ] **Step 2: Run tests and verify failure**

```bash
pytest tests/test_dashboard_control.py tests/test_workflow_engine.py -q
```

- [ ] **Step 3: Add workflow retry primitive**

Add exact interface:

```python
def retry_task_job(
    self,
    workflow_id: str,
    task_id: str,
    *,
    failed_job_key: str,
) -> dict:
    ...
```

Inside one backend transaction:
1. load workflow/task;
2. validate current generation;
3. require task terminal failure/cancel state;
4. check `attempts < max_attempts`;
5. move task to `ready`;
6. clear `claimed_job_key` but preserve prior `result_json` in execution history/event evidence;
7. call normal `dispatch_ready(..., limit=1)` after transaction.

Do not construct a job that bypasses the workflow engine.

- [ ] **Step 4: Implement dashboard retry control**

`DashboardControl.retry_job` resolves `workflow_id` and `workflow_task_id` from the failed job payload, calls the workflow primitive, then records an event:

```python
{
    "type": "job-retry-requested",
    "retry_of": old_key,
    "new_job_key": new_job["key"],
    "requested_by": requested_by,
}
```

- [ ] **Step 5: Add operator API route**

```text
POST /v1/dashboard/jobs/{job_key}/control
```

Body:

```json
{"action":"retry"}
```

`cancel` is also accepted and routes to queued-immediate or active-cooperative cancellation as appropriate.

- [ ] **Step 6: Run tests**

```bash
pytest tests/test_dashboard_control.py tests/test_dashboard_control_api.py tests/test_workflow_engine.py tests/test_workflow_api.py -q
```

Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add src/production_os/dashboard_control.py src/production_os/workflow_engine.py src/production_os/control_plane.py tests/test_dashboard_control.py tests/test_dashboard_control_api.py tests/test_workflow_engine.py
git commit -m "feat(control): add traceable job retry"
```

---

### Task 6: Add honest GitHub Actions worker kick with scheduled fallback

**Files:**
- Modify: `src/production_os/dashboard_control.py`
- Modify: `src/production_os/control_plane.py`
- Modify: `tests/test_dashboard_control.py`
- Modify: `tests/test_dashboard_control_api.py`
- Verify: `dbrckk/ai-dev-server/.github/workflows/production-os-actions-worker.yml`
- Verify: `dbrckk/ai-dev-server/tests/test_production_os_actions_worker_workflow.py`

**Interfaces:**
- Consumes: existing `GitHubClient.dispatch_workflow(full_name, workflow, ref, inputs=None)`.
- Produces: kick result states `dispatched`, `scheduled_fallback`, or `failed`.

- [ ] **Step 1: Write failing configured/fallback tests**

```python
def test_kick_dispatches_actions_worker_when_configured(...):
    github = FakeGitHub()
    control = DashboardControl(
        store, queue, workflows,
        github=github,
        actions_repository="dbrckk/ai-dev-server",
        actions_workflow="production-os-actions-worker.yml",
    )
    result = control.kick_worker("github-actions-worker")
    assert result["status"] == "dispatched"
    assert github.calls == [(
        "dbrckk/ai-dev-server",
        "production-os-actions-worker.yml",
        "main",
    )]


def test_kick_reports_scheduled_fallback_without_dispatch_credentials(...):
    control = DashboardControl(store, queue, workflows)
    result = control.kick_worker("github-actions-worker")
    assert result == {
        "status": "scheduled_fallback",
        "poll_interval_seconds": 300,
    }
```

- [ ] **Step 2: Run tests and verify failure**

```bash
pytest tests/test_dashboard_control.py -q
```

- [ ] **Step 3: Configure server-side dispatch explicitly**

Read optional environment/config values at control-plane construction:

```text
PRODUCTION_OS_ACTIONS_REPOSITORY=dbrckk/ai-dev-server
PRODUCTION_OS_ACTIONS_WORKFLOW=production-os-actions-worker.yml
PRODUCTION_OS_ACTIONS_REF=main
```

Use the existing server-side GitHub token source only if already configured for `GitHubClient`. Do not expose it to dashboard JavaScript.

- [ ] **Step 4: Implement dispatch/fallback result**

On GitHub exception:

```python
return {
    "status": "failed",
    "error": "github_dispatch_failed",
}
```

Do not silently downgrade an attempted-but-failed immediate dispatch to `dispatched`.

If no dispatch client/config exists, return scheduled fallback with 300 seconds.

- [ ] **Step 5: Verify AI Dev Server workflow still supports both triggers**

```bash
python -m unittest tests.test_production_os_actions_worker_workflow -v
```

The workflow must retain:
- `workflow_dispatch`;
- `schedule: */5 * * * *`;
- single-flight concurrency;
- `--once`.

- [ ] **Step 6: Run Production-OS tests**

```bash
pytest tests/test_dashboard_control.py tests/test_dashboard_control_api.py -q
```

Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add src/production_os/dashboard_control.py src/production_os/control_plane.py tests/test_dashboard_control.py tests/test_dashboard_control_api.py
git commit -m "feat(control): dispatch actions worker on kick"
```

---

### Task 7: Add alerts and anomaly indicators from existing observability facts

**Files:**
- Create: `src/production_os/dashboard_alerts.py`
- Modify: `src/production_os/dashboard_service.py`
- Create: `tests/test_dashboard_alerts.py`

**Interfaces:**
- Consumes: Release-1 overview/execution/usage/workflow facts.
- Produces: `derive_alerts(snapshot: dict) -> list[dict]`.

- [ ] **Step 1: Write failing deterministic alert tests**

```python
def test_offline_worker_with_queued_work_is_high_alert():
    alerts = derive_alerts({
        "workers": {"online": 0, "offline": 1},
        "productions": {"queued": 3, "running": 0},
        "performance": {"recent_failures": 0},
        "usage": {"cost_delta_ratio": None},
    })
    assert alerts[0]["code"] == "queue_without_worker"
    assert alerts[0]["severity"] == "high"
```

Also test:
- three or more consecutive failures => high;
- usage/cost > 2x rolling baseline when baseline exists => medium;
- stale telemetry on a reported busy worker => medium;
- no baseline => no fake cost anomaly.

- [ ] **Step 2: Run tests and verify failure**

```bash
pytest tests/test_dashboard_alerts.py -q
```

- [ ] **Step 3: Implement bounded, explainable rules**

Use constants:

```python
CONSECUTIVE_FAILURE_THRESHOLD = 3
COST_SPIKE_RATIO = 2.0
BUSY_TELEMETRY_STALE_SECONDS = 180
```

Each alert returns:

```python
{
    "code": "...",
    "severity": "info|medium|high",
    "title": "...",
    "message": "...",
    "evidence": {...},
}
```

No ML/anomaly service is introduced in Release 2.

- [ ] **Step 4: Include alerts in overview and worker/project details where relevant**

Do not make alert derivation failure fatal to the dashboard; return `alerts=[]` plus a section error if necessary.

- [ ] **Step 5: Run tests**

```bash
pytest tests/test_dashboard_alerts.py tests/test_dashboard_api.py -q
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add src/production_os/dashboard_alerts.py src/production_os/dashboard_service.py tests/test_dashboard_alerts.py tests/test_dashboard_api.py
git commit -m "feat(dashboard): add operational alerts"
```

---

### Task 8: Build the worker Control tab and actionable dashboard feedback

**Files:**
- Modify: `src/production_os/dashboard_ui.py`
- Modify: `tests/test_dashboard_ui_v3.py`

**Interfaces:**
- Consumes: control APIs from Tasks 3–6.
- Produces: operator control UI with explicit confirmation and requested/acknowledged state.

- [ ] **Step 1: Write failing UI contract tests**

```python
def test_worker_control_tab_has_safe_actions():
    html = DASHBOARD_HTML
    for action in ("pause", "resume", "drain", "kick"):
        assert f'data-control-action="{action}"' in html
    assert 'data-control-action="cancel-current"' in html
    assert "confirmControlAction" in html


def test_ui_distinguishes_requested_from_acknowledged():
    assert "Action demandée" in DASHBOARD_HTML
    assert "Confirmée par le worker" in DASHBOARD_HTML
```

- [ ] **Step 2: Run tests and verify failure**

```bash
pytest tests/test_dashboard_ui_v3.py -q
```

- [ ] **Step 3: Implement action drawer**

Non-destructive actions:
- pause;
- resume;
- drain;
- kick.

Interrupting actions:
- cancel current job;
- retry failed job.

Use a modal/drawer confirmation for cancel/retry. The selected `job_key` is displayed before submit.

- [ ] **Step 4: Implement API state feedback**

After submit:

```javascript
async function runWorkerControl(workerId, action, jobKey=null) {
  const body = {action};
  if (jobKey) body.job_key = jobKey;
  const result = await api(
    "/v1/dashboard/workers/" + encodeURIComponent(workerId) + "/control",
    {method: "POST", body: JSON.stringify(body)}
  );
  renderControlReceipt(result);
  await loadWorkerDetail(workerId);
}
```

For `scheduled_fallback`, show:
`Réveil automatique prévu ≤ 5 min`.

For `dispatched`, show:
`Réveil GitHub Actions demandé`.

Never display either as `Worker démarré` until heartbeat evidence appears.

- [ ] **Step 5: Preserve mobile state while controls refresh**

Control completion may refresh the worker card/detail only. It must not reset:
- scroll;
- active tab;
- selected worker;
- launch form.

- [ ] **Step 6: Run UI tests**

```bash
pytest tests/test_dashboard_ui_v3.py tests/test_dashboard_launch.py -q
```

Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add src/production_os/dashboard_ui.py tests/test_dashboard_ui_v3.py
git commit -m "feat(dashboard): add worker control center"
```

---

### Task 9: Qualify the complete control center with race, restart, and E2E tests

**Files:**
- Create: `tests/test_dashboard_control_e2e.py`
- Modify: `tests/test_production_stack_e2e.py`
- Modify: `tests/test_dashboard_control.py`
- Modify: `tests/test_dashboard_control_api.py`
- Modify: `tests/test_dashboard_ui_v3.py`
- Modify: `README.md`

**Interfaces:**
- Consumes: all Release-2 features.
- Produces: a release gate proving safe control semantics end to end.

- [ ] **Step 1: Add restart persistence test**

```python
def test_paused_state_survives_control_plane_restart(tmp_path):
    first = ControlPlane(str(tmp_path / "production.db"), ...)
    first.dashboard_control.set_worker_state(
        "worker-a", "paused", requested_by="operator:dashboard"
    )

    second = ControlPlane(str(tmp_path / "production.db"), ...)
    assert second.dashboard_control.worker_state("worker-a")["desired_state"] == "paused"
```

- [ ] **Step 2: Add cancellation race tests**

Pin both orderings:
1. completion commits first, cancel acknowledgement => 409;
2. cancellation commits first, completion => 409.

Assert one terminal execution row and one terminal job state.

- [ ] **Step 3: Add retry race/idempotency tests**

Two identical retry requests against one failed job produce exactly one new active job.

A retry against stale workflow generation returns conflict and creates nothing.

- [ ] **Step 4: Add full E2E flow**

The E2E must:
1. launch workflow;
2. register worker;
3. pause and verify claim blocked;
4. resume and claim;
5. drain and verify current job remains valid while second claim blocked;
6. resume;
7. request cancellation for named job;
8. worker observes directive and acknowledges cancellation;
9. retry cancelled/failed work if allowed;
10. complete retry;
11. verify execution lineage and activity;
12. kick GitHub Actions fake configured client and verify dispatch result;
13. verify dashboard API/UI states.

- [ ] **Step 5: Update README**

Document:
- pause vs drain;
- active-job cooperative cancellation;
- retry lineage;
- immediate kick vs scheduled fallback;
- operator-role requirement;
- requested vs acknowledged UI semantics.

- [ ] **Step 6: Run complete Production-OS suite**

```bash
pytest tests/test_dashboard_control.py tests/test_dashboard_control_api.py tests/test_dashboard_control_e2e.py tests/test_dashboard_alerts.py tests/test_dashboard_ui_v3.py -q
pytest -q
```

Expected: all available tests PASS.

- [ ] **Step 7: Run AI Dev Server worker/control tests**

```bash
python -m unittest tests.test_production_os_worker_runtime tests.test_production_os_actions_worker_workflow -v
```

Expected: PASS.

- [ ] **Step 8: Commit final qualification**

```bash
git add tests/test_dashboard_control_e2e.py tests/test_production_stack_e2e.py tests/test_dashboard_control.py tests/test_dashboard_control_api.py tests/test_dashboard_ui_v3.py README.md
git commit -m "test(control): qualify dashboard control center"
```

---

## Release-2 Completion Gate

Before declaring the control center complete, fresh evidence must show:

```bash
pytest -q
```

passes for Production-OS, the focused AI Dev Server worker/Actions tests pass, and CI is green in both repositories for affected workflows.

Do not claim completion if:

- a paused or draining worker can still claim new work;
- cancel-current can target the wrong job;
- a cancellation/completion race can produce two terminal truths;
- retry can bypass max attempts or stale generation checks;
- kick claims immediate success without successful workflow dispatch;
- a control action is presented as acknowledged before runtime evidence exists;
- secrets appear in control/activity/log payloads.
