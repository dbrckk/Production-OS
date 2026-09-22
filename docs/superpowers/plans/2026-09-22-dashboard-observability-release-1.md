# Dashboard Observability Release 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship the first production-ready observability dashboard: durable execution telemetry, API/token/cost and commit metrics, project/worker drill-down, deterministic current-production progress, auditable global project progress, history, and a mobile-first UI.

**Architecture:** Production-OS becomes the source of truth for observability. AI Dev Server emits normalized execution evidence; Production-OS persists raw facts and snapshots through a focused dashboard store, derives progress/usage through pure services, and exposes authenticated read APIs consumed by a separate dashboard UI module. Existing workflow, auth, release, transparency, SQLite, PostgreSQL, Render, and GitHub Actions behavior stays intact.

**Tech Stack:** Python 3.11+, stdlib HTTP server, SQLite, PostgreSQL via psycopg, pytest, GitHub REST API, vanilla HTML/CSS/JavaScript, AI Dev Server unittest suite.

**Spec:** `docs/superpowers/specs/2026-09-22-dashboard-observability-control-center-design.md`

## Global Constraints

- Keep Production-OS compatible with Python >=3.11.
- Schema advances from version 8 to version 9 and must remain idempotent in SQLite and PostgreSQL.
- Preserve current workflow creation/dispatch, health endpoints, auth roles, release/transparency behavior, Render deployment, and GitHub Actions worker compatibility.
- Read dashboard endpoints require at least `viewer`; mutation of telemetry by workers requires `worker`.
- Never return or persist raw API keys, authorization headers, worker tokens, operator tokens, or other credential-like values.
- Missing historical telemetry remains unknown; do not fabricate zeros, provider/model identities, quota, price, or commit attribution.
- Production-OS commit attribution requires a correlated SHA emitted by a worker execution.
- GitHub commit totals mean commits reachable from the repository default branch.
- Cost is an estimate only when an exact versioned provider/model price rule exists; otherwise cost is null/unavailable.
- Polling must update components without a full-page reload or scroll reset.
- The first release exposes no enabled pause/resume/cancel/retry/kick controls; those belong to Release 2.
- Do not add a paid external service as a mandatory dependency.

## Review Focus

- Repeated ACK/telemetry/completion delivery must stay idempotent: one execution attempt, cumulative live usage not double-counted, final usage persisted once.
- Old jobs and task results with missing usage/provider/model/commit fields must render as unknown/empty rather than crashing or becoming fake zero-cost data.
- Repository names, worker IDs, pagination cursors, and time windows must be validated before being interpolated into queries or remote paths.
- A GitHub outage must serve cached repository snapshots with freshness/degraded metadata rather than taking down the entire dashboard.
- Background polling must preserve scroll position, selected tab, repository selection, and the unsent production instruction.

---

## File Structure

### Production-OS files created

- `src/production_os/dashboard_store.py` — backend-neutral persistence/query boundary for schema-v9 telemetry and snapshots.
- `src/production_os/dashboard_security.py` — recursive server-side credential redaction for structured logs/metadata.
- `src/production_os/dashboard_usage.py` — normalization, pricing catalog, cost calculation, and usage aggregation.
- `src/production_os/project_progress.py` — deterministic workflow progress and versioned hybrid project progress calculation.
- `src/production_os/dashboard_github.py` — GitHub repository snapshot collection and cache/degraded handling.
- `src/production_os/dashboard_service.py` — read-model aggregation for overview, workers, projects, usage, logs, history, and activity.
- `src/production_os/dashboard_ui.py` — dashboard HTML/CSS/JS, preserving `DASHBOARD_HTML` as an importable compatibility symbol.
- `tests/test_dashboard_store.py`
- `tests/test_dashboard_store_postgres.py`
- `tests/test_dashboard_security.py`
- `tests/test_dashboard_usage.py`
- `tests/test_project_progress.py`
- `tests/test_dashboard_github.py`
- `tests/test_dashboard_api.py`
- `tests/test_dashboard_ui_v3.py`
- `tests/test_dashboard_observability_e2e.py`

### Production-OS files modified

- `src/production_os/sqlite_backend.py:21-309` — schema version and v9 tables/indexes.
- `src/production_os/postgres_backend.py:25-300` — PostgreSQL parity for v9 tables/indexes.
- `src/production_os/control_plane.py:1-84, 84-600, request routing and job ACK/complete/fail handlers` — wire dashboard services, telemetry ingestion, new read routes, and import UI from `dashboard_ui.py`.
- `src/production_os/github_client.py:20-602` — public repository/default-branch facts needed by snapshotter.
- `tests/test_sqlite_backend.py`
- `tests/test_postgres_backend.py`
- `tests/test_control_plane.py`
- `tests/test_dashboard_launch.py`
- `tests/test_workflow_api.py`
- `tests/test_production_stack_e2e.py`

### AI Dev Server files modified

- `studio/github_runner.py:96-220` — enrich usage and result envelope with provider/model and attributable commit SHAs.
- `studio/production_os_worker.py:97-269, 557-810` — telemetry client call and periodic live snapshot publication.
- `tests/test_github_runner_usage.py`
- `tests/test_production_os_result_contract.py`
- `tests/test_production_os_worker.py`
- `tests/test_production_os_worker_runtime.py`

---

### Task 1: Create schema-v9 observability tables with SQLite/PostgreSQL parity

**Files:**
- Modify: `src/production_os/sqlite_backend.py:21-309`
- Modify: `src/production_os/postgres_backend.py:25-300`
- Create: `tests/test_dashboard_store.py`
- Create: `tests/test_dashboard_store_postgres.py`
- Modify: `tests/test_sqlite_backend.py`
- Modify: `tests/test_postgres_backend.py`

**Interfaces:**
- Consumes: existing `SQLiteBackend.connect/transaction` and `PostgresBackend.connect/transaction`.
- Produces: schema version `9` and tables `worker_control_state`, `job_control_state`, `job_executions`, `api_usage_events`, `provider_quota_snapshots`, `worker_log_events`, `project_repository_snapshots`, `project_progress_snapshots`.

- [ ] **Step 1: Write failing SQLite schema tests**

```python
def test_schema_v9_has_dashboard_tables(tmp_path):
    from production_os.sqlite_backend import SQLiteBackend

    backend = SQLiteBackend(tmp_path / "production.db")
    with backend.connect() as db:
        version = db.execute(
            "SELECT value FROM schema_meta WHERE key='schema_version'"
        ).fetchone()["value"]
        names = {
            row["name"]
            for row in db.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }

    assert version == "9"
    assert {
        "worker_control_state",
        "job_control_state",
        "job_executions",
        "api_usage_events",
        "provider_quota_snapshots",
        "worker_log_events",
        "project_repository_snapshots",
        "project_progress_snapshots",
    } <= names


def test_schema_v9_initialization_is_idempotent(tmp_path):
    from production_os.sqlite_backend import SQLiteBackend

    path = tmp_path / "production.db"
    SQLiteBackend(path)
    SQLiteBackend(path)
    with SQLiteBackend(path).connect() as db:
        count = db.execute(
            "SELECT COUNT(*) AS n FROM schema_meta WHERE key='schema_version'"
        ).fetchone()["n"]
    assert count == 1
```

- [ ] **Step 2: Run SQLite tests and verify they fail on schema 8**

Run:

```bash
pytest tests/test_dashboard_store.py tests/test_sqlite_backend.py -q
```

Expected: failure showing schema version `8` or missing v9 tables.

- [ ] **Step 3: Add exact v9 tables and indexes to SQLite**

Set:

```python
class SQLiteBackend:
    SCHEMA_VERSION = 9
```

Add the tables from the approved spec, including these indexes:

```sql
CREATE UNIQUE INDEX IF NOT EXISTS idx_job_executions_job_attempt
ON job_executions(job_key, attempt);

CREATE INDEX IF NOT EXISTS idx_job_executions_worker_started
ON job_executions(worker_id, started_at DESC);

CREATE INDEX IF NOT EXISTS idx_job_executions_repo_started
ON job_executions(repository, started_at DESC);

CREATE INDEX IF NOT EXISTS idx_api_usage_worker_time
ON api_usage_events(worker_id, occurred_at DESC);

CREATE INDEX IF NOT EXISTS idx_api_usage_repo_time
ON api_usage_events(repository, occurred_at DESC);

CREATE INDEX IF NOT EXISTS idx_worker_logs_worker_time
ON worker_log_events(worker_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_project_repo_snapshots_repo_time
ON project_repository_snapshots(repository, captured_at DESC);

CREATE INDEX IF NOT EXISTS idx_project_progress_repo_time
ON project_progress_snapshots(repository, captured_at DESC);
```

The `job_executions` definition must include live fields:

```sql
current_stage TEXT,
progress_percent REAL,
live_usage_json TEXT NOT NULL DEFAULT '{}',
last_telemetry_at TEXT
```

- [ ] **Step 4: Mirror schema exactly in PostgreSQL and write parity tests**

Use PostgreSQL-compatible `BIGSERIAL` only where the existing backend already does; all new dashboard IDs remain application-supplied `TEXT` so SQLite/PostgreSQL result shapes match.

Add a parity test that compares required column names from both backends:

```python
REQUIRED_EXECUTION_COLUMNS = {
    "id", "job_key", "workflow_id", "workflow_task_id", "repository",
    "worker_id", "attempt", "status", "started_at", "finished_at",
    "duration_seconds", "provider", "model", "api_calls",
    "input_tokens", "cached_input_tokens", "output_tokens",
    "reasoning_tokens", "total_tokens", "estimated_cost_usd",
    "pricing_catalog_version", "commit_count", "commit_shas_json",
    "retry_of_execution_id", "error_type", "error_message",
    "current_stage", "progress_percent", "live_usage_json",
    "last_telemetry_at", "result_summary_json", "created_at",
}
```

- [ ] **Step 5: Run backend tests**

Run:

```bash
pytest tests/test_dashboard_store.py tests/test_sqlite_backend.py -q
pytest tests/test_dashboard_store_postgres.py tests/test_postgres_backend.py -q
```

Expected: SQLite tests PASS. PostgreSQL tests PASS when the existing PostgreSQL test DSN is available; otherwise the repository's established skip behavior is preserved.

- [ ] **Step 6: Commit**

```bash
git add src/production_os/sqlite_backend.py src/production_os/postgres_backend.py tests/test_dashboard_store.py tests/test_dashboard_store_postgres.py tests/test_sqlite_backend.py tests/test_postgres_backend.py
git commit -m "feat(observability): add schema v9 telemetry tables"
```

---

### Task 2: Implement the dashboard persistence boundary and idempotent execution lifecycle

**Files:**
- Create: `src/production_os/dashboard_store.py`
- Modify: `tests/test_dashboard_store.py`
- Modify: `tests/test_dashboard_store_postgres.py`
- Create: `src/production_os/dashboard_security.py`
- Create: `tests/test_dashboard_security.py`

**Interfaces:**
- Consumes: schema-v9 tables from Task 1.
- Produces:
  - `redact_log_value(value: object) -> object`
  - `DashboardStore(backend)`
  - `start_execution(job: dict, worker_id: str, *, started_at: str | None = None) -> dict`
  - `update_live_execution(job_key: str, worker_id: str, telemetry: dict, *, at: str | None = None) -> dict`
  - `finish_execution(job_key: str, worker_id: str, *, status: str, duration_seconds: float | None, result: dict | None, error_type: str | None = None, error_message: str | None = None, finished_at: str | None = None) -> dict`
  - snapshot/log/query methods used by later tasks.

- [ ] **Step 1: Write failing lifecycle tests**

```python
def test_start_execution_is_idempotent_for_same_delivery_attempt(backend):
    store = DashboardStore(backend)
    job = {
        "key": "job-1",
        "repository": "dbrckk/example",
        "task": "ship",
        "delivery_attempt": 2,
        "payload": {"workflow_id": "wf-1", "workflow_task_id": "build"},
    }

    first = store.start_execution(job, "worker-a", started_at="2026-09-22T10:00:00+00:00")
    second = store.start_execution(job, "worker-a", started_at="2026-09-22T10:00:10+00:00")

    assert first["id"] == second["id"]
    assert first["attempt"] == 2
    assert store.execution_count("job-1") == 1


def test_live_usage_replaces_cumulative_snapshot_instead_of_summing(backend):
    store = DashboardStore(backend)
    store.start_execution(sample_job(), "worker-a")
    store.update_live_execution(
        "job-1", "worker-a",
        {"progress": 30, "usage": {"total_tokens": 100}},
    )
    row = store.update_live_execution(
        "job-1", "worker-a",
        {"progress": 45, "usage": {"total_tokens": 130}},
    )

    assert row["progress_percent"] == 45
    assert row["live_usage"]["total_tokens"] == 130
```

Also add tests for:
- recursive log redaction removes authorization/token/api-key/password values before persistence;
- wrong worker cannot update a claimed execution;
- progress `101` is rejected;
- progress does not move backward;
- missing usage remains `{}`, not invented zeros;
- finishing the same execution twice is idempotent;
- duplicate commit SHAs are deduplicated.

- [ ] **Step 2: Run tests and verify failures**

```bash
pytest tests/test_dashboard_store.py -q
```

Expected: import/function failures because `DashboardStore` does not exist.

- [ ] **Step 3: Implement backend-neutral SQL helpers and execution IDs**

Start `dashboard_store.py` with:

```python
from __future__ import annotations

import json
from datetime import datetime, timezone


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _is_postgres(backend) -> bool:
    return backend.__class__.__name__ == "PostgresBackend"


def _sql(backend, statement: str) -> str:
    return statement.replace("?", "%s") if _is_postgres(backend) else statement


def _execute(db, backend, statement: str, params: tuple = ()):
    return db.execute(_sql(backend, statement), params)


def execution_id(job_key: str, attempt: int) -> str:
    return f"{job_key}:{max(1, int(attempt))}"


class DashboardStore:
    def __init__(self, backend):
        self.backend = backend
```

`start_execution` uses `job["delivery_attempt"] or 1` and an `INSERT` statement with `ON CONFLICT(id) DO NOTHING`, then reads back the row. This makes repeated ACK delivery safe.

Add `dashboard_security.py` with recursive redaction before any log serialization:

```python
_SENSITIVE_KEYS = {"authorization", "token", "api_key", "apikey", "secret", "password", "cookie"}

def redact_log_value(value: object) -> object:
    if isinstance(value, dict):
        return {
            str(key): ("[REDACTED]" if str(key).lower() in _SENSITIVE_KEYS else redact_log_value(child))
            for key, child in value.items()
        }
    if isinstance(value, list):
        return [redact_log_value(child) for child in value]
    if isinstance(value, str):
        return _scrub_secret_patterns(value)
    return value
```

`DashboardStore.append_logs` must call `redact_log_value` before writing `message` or `metadata_json`.

- [ ] **Step 4: Implement live and final execution writes**

Normalize live payload without summing repeated snapshots:

```python
def _bounded_progress(value):
    if value is None:
        return None
    value = float(value)
    if value < 0 or value > 100:
        raise ValueError("progress must be between 0 and 100")
    return value
```

`update_live_execution` must:
1. load the currently running execution for `job_key`;
2. require `worker_id` equality;
3. reject backward progress for the same stage;
4. replace `live_usage_json` with the new cumulative snapshot;
5. set `last_telemetry_at`.

`finish_execution` must:
1. load the running execution;
2. require matching worker;
3. update terminal status only if not already terminal;
4. copy normalized final usage and commit fields from `result`;
5. insert provider/model rows once into `api_usage_events` using deterministic IDs `{execution_id}:{index}`;
6. keep unknown provider/model/cost null.

- [ ] **Step 5: Add query and snapshot primitives needed by later services**

Implement these exact method contracts:

- `latest_execution(self, job_key: str) -> dict | None`
- `executions_for_worker(self, worker_id: str, *, limit: int = 100) -> list[dict]`
- `executions_for_repository(self, repository: str, *, limit: int = 100) -> list[dict]`
- `usage_events(self, *, worker_id: str | None = None, repository: str | None = None, since: str | None = None) -> list[dict]`
- `append_logs(self, worker_id: str, rows: list[dict]) -> list[dict]`
- `logs_for_worker(self, worker_id: str, *, after: str | None = None, limit: int = 100) -> list[dict]`
- `save_repository_snapshot(self, snapshot: dict) -> dict`
- `latest_repository_snapshot(self, repository: str) -> dict | None`
- `save_progress_snapshot(self, snapshot: dict) -> dict`
- `latest_progress_snapshot(self, repository: str) -> dict | None`
- `progress_history(self, repository: str, *, limit: int = 100) -> list[dict]`

Each query must use parameter binding through `_execute`. Snapshot inserts use application-generated IDs and JSON serialization with sorted keys. `logs_for_worker` uses the stored log ID as an opaque cursor and orders by `created_at DESC, id DESC`.

Clamp log `limit` to 1–500 and reject invalid cursors rather than interpolating them into SQL.

- [ ] **Step 6: Run SQLite and PostgreSQL store tests**

```bash
pytest tests/test_dashboard_store.py tests/test_dashboard_store_postgres.py -q
```

Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add src/production_os/dashboard_store.py src/production_os/dashboard_security.py tests/test_dashboard_store.py tests/test_dashboard_store_postgres.py tests/test_dashboard_security.py
git commit -m "feat(observability): persist execution telemetry"
```

---

### Task 3: Wire execution lifecycle and live telemetry into the Production-OS control plane

**Files:**
- Modify: `src/production_os/control_plane.py:20-84 and job ACK/complete/fail POST routes`
- Modify: `tests/test_control_plane.py`
- Modify: `tests/test_workflow_api.py`
- Create: `tests/test_dashboard_api.py`

**Interfaces:**
- Consumes: `DashboardStore` from Task 2.
- Produces: worker-authenticated `POST /v1/jobs/{job_key}/telemetry`, plus automatic execution start/finalization on ACK/complete/fail.

- [ ] **Step 1: Write failing telemetry API tests**

```python
def test_worker_can_publish_owned_job_telemetry(running_control_plane):
    base, operator, worker = running_control_plane
    job = enqueue_and_claim(base, operator, worker)

    status, payload = api(
        base,
        f"/v1/jobs/{job['key']}/telemetry",
        worker,
        {
            "worker_id": "worker-a",
            "stage": "implementation",
            "progress": 42,
            "usage": {"total_tokens": 1234},
            "logs": [{"level": "info", "message": "Round 2 complete"}],
        },
    )

    assert status == 200
    assert payload["execution"]["progress_percent"] == 42


def test_other_worker_cannot_publish_telemetry_for_claimed_job(
    running_control_plane_two_workers,
):
    base, operator, worker_a, worker_b = running_control_plane_two_workers
    job = enqueue_and_claim(base, operator, worker_a)
    status, _ = api(
        base,
        f"/v1/jobs/{job['key']}/telemetry",
        worker_b,
        {
            "worker_id": "worker-b",
            "stage": "implementation",
            "progress": 10,
        },
    )
    assert status == 409
```

Add auth tests:
- viewer token => 403;
- no token => 401;
- malformed progress => 400;
- telemetry failure does not alter job status.

- [ ] **Step 2: Run tests and verify failure**

```bash
pytest tests/test_dashboard_api.py tests/test_workflow_api.py -q
```

Expected: 404 or missing route.

- [ ] **Step 3: Instantiate the store in `ControlPlane`**

Add:

```python
from .dashboard_store import DashboardStore

# In ControlPlane.__init__, immediately after self.backend is created:
self.dashboard_store = DashboardStore(self.backend)
```

- [ ] **Step 4: Start/finalize executions at existing lifecycle boundaries**

Immediately after successful job ACK:

```python
acked = control.queue.ack(key, worker_id)
control.dashboard_store.start_execution(acked, worker_id)
```

Before/after existing workflow result correlation in completion/failure routes, call:

```python
control.dashboard_store.finish_execution(
    key,
    worker_id,
    status="succeeded",
    duration_seconds=duration_seconds,
    result=dict(body.get("result") or {}),
)
```

and failure equivalent with `status="failed"`, `error_message=reason`.

Keep current optimizer recording and workflow result recording unchanged.

- [ ] **Step 5: Add the live telemetry route**

In POST routing, parse path segments and require `worker`:

```python
if (
    len(parts) == 4
    and parts[:2] == ["v1", "jobs"]
    and parts[3] == "telemetry"
):
    principal = self._require("worker")
    if principal is None:
        return
    key = parts[2]
    worker_id = str(body.get("worker_id") or "")
    job = control.queue.get(key)
    if job.get("claimed_by") != worker_id:
        self._send(HTTPStatus.CONFLICT, {"error": "job claim owner mismatch"})
        return
    execution = control.dashboard_store.update_live_execution(
        key, worker_id, body
    )
    self._send(HTTPStatus.OK, {"execution": execution})
    return
```

Logs in `body["logs"]` go through `DashboardStore.append_logs`, whose Task-2 contract redacts credential-like values before persistence.

- [ ] **Step 6: Verify current control-plane behavior still passes**

```bash
pytest tests/test_control_plane.py tests/test_workflow_api.py tests/test_dashboard_api.py -q
```

Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add src/production_os/control_plane.py tests/test_control_plane.py tests/test_workflow_api.py tests/test_dashboard_api.py
git commit -m "feat(observability): ingest live worker telemetry"
```

---

### Task 4: Enrich AI Dev Server results and publish live telemetry

**Files:**
- Modify: `studio/agents/orchestrator.py:56-157` in `dbrckk/ai-dev-server`
- Modify: `studio/github_runner.py:96-220` in `dbrckk/ai-dev-server`
- Modify: `studio/production_os_worker.py:97-269, 557-810`
- Modify: `tests/test_agent_router.py`
- Modify: `tests/test_github_runner_usage.py`
- Modify: `tests/test_production_os_result_contract.py`
- Modify: `tests/test_production_os_worker.py`
- Modify: `tests/test_production_os_worker_runtime.py`

**Interfaces:**
- Consumes: Production-OS telemetry endpoint from Task 3.
- Produces:
  - normalized `usage.providers`;
  - `commits.count` and `commits.shas`;
  - `ProductionOSClient.telemetry(key, payload)`;
  - bounded periodic live telemetry during a job.

- [ ] **Step 1: Write failing usage/result-contract tests**

Extend the usage test with provider/model identity carried by an attempt:

```python
attempt = {
    "agent": "codex",
    "provider": "nvidia",
    "model": "nvidia/nemotron-3-super-120b-a12b",
    "usage": {
        "input_tokens": 100,
        "output_tokens": 20,
        "total_tokens": 120,
    },
}
```

Expected aggregate:

```python
assert usage["providers"] == [{
    "provider": "nvidia",
    "model": "nvidia/nemotron-3-super-120b-a12b",
    "api_calls": 1,
    "input_tokens": 100,
    "cached_input_tokens": 0,
    "output_tokens": 20,
    "reasoning_tokens": 0,
    "total_tokens": 120,
}]
```

Add a result contract assertion:

```python
assert envelope["commits"]["shas"] == ["a" * 40]
assert envelope["commits"]["count"] == 1
```

- [ ] **Step 2: Run focused AI Dev Server tests**

```bash
python -m unittest tests.test_github_runner_usage tests.test_production_os_result_contract tests.test_production_os_worker -v
```

Expected: failures for missing `providers` and `commits`.

- [ ] **Step 3: Attach provider/model identity only when runtime evidence knows it, then aggregate without breaking totals**

In `studio/agents/orchestrator.py`, extend the existing `_run_evidence` after its current base evidence dictionary is created. Add only explicit identity that the runtime configuration actually knows:

```python
if run.agent == "opencode":
    model = str(
        os.environ.get("STUDIO_CODE_MODEL")
        or os.environ.get("STUDIO_MODEL")
        or ""
    ).strip()
    base = str(os.environ.get("STUDIO_API_BASE") or "").strip()
    if model and base:
        evidence["provider"] = "studio"
        evidence["model"] = model
```

Leave provider/model absent for `codex-chatgpt` and `omniroute-free` unless their execution evidence later exposes the resolved model explicitly.

Keep the existing top-level counters and add `providers`:

```python
totals = {
    "input_tokens": 0,
    "cached_input_tokens": 0,
    "output_tokens": 0,
    "reasoning_tokens": 0,
    "total_tokens": 0,
    "runs": 0,
    "agents": {},
    "providers": [],
}
```

Aggregate by `(provider, model)` only when both strings are explicitly present. Existing attempts lacking these fields continue to contribute to totals but not to a fabricated provider bucket.

- [ ] **Step 4: Emit attributable commit SHAs from known result evidence**

Add a pure helper:

```python
_COMMIT_KEYS = (
    "commit_sha",
    "candidate_commit_sha",
    "candidate_merge_commit_sha",
    "registry_promotion_commit_sha",
    "merge_commit_sha",
)

def collect_commit_shas(summary: dict) -> list[str]:
    found: set[str] = set()
    def visit(value):
        if isinstance(value, dict):
            for key, child in value.items():
                if key in _COMMIT_KEYS and isinstance(child, str):
                    sha = child.strip().lower()
                    if len(sha) == 40 and all(c in "0123456789abcdef" for c in sha):
                        found.add(sha)
                else:
                    visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)
    visit(summary)
    return sorted(found)
```

Then `write_production_os_result` adds:

```python
commits = collect_commit_shas(summary)
envelope["commits"] = {"count": len(commits), "shas": commits}
```

Do not count branch baselines or arbitrary SHA-looking strings that are not under explicit commit keys.

- [ ] **Step 5: Add `ProductionOSClient.telemetry`**

```python
def telemetry(self, key: str, payload: dict) -> dict | None:
    return self._post(
        f"/v1/jobs/{urllib.parse.quote(str(key), safe='')}/telemetry",
        payload,
        token=self.worker_token,
    )
```

- [ ] **Step 6: Publish bounded live snapshots from the heartbeat thread**

The heartbeat loop sends telemetry after a successful heartbeat. Use a helper that reads only known small status files and never sends full stdout/stderr:

```python
def live_telemetry_snapshot(project_out: Path) -> dict:
    status = read_status(project_out)
    percent = status.get("progress_percent")
    return {
        "stage": status.get("next_stage") or status.get("status"),
        "progress": percent if isinstance(percent, (int, float)) else None,
        "usage": status.get("usage") if isinstance(status.get("usage"), dict) else {},
        "logs": [],
    }
```

Call:

```python
snapshot = live_telemetry_snapshot(project_out)
snapshot["worker_id"] = worker_id
client.telemetry(key, snapshot)
```

Telemetry exceptions are recorded in the existing heartbeat error list and do not abort the coding run.

- [ ] **Step 7: Verify AI Dev Server tests**

```bash
python -m unittest tests.test_github_runner_usage tests.test_production_os_result_contract tests.test_production_os_worker tests.test_production_os_worker_runtime -v
```

Expected: PASS.

- [ ] **Step 8: Commit in `dbrckk/ai-dev-server`**

```bash
git add studio/github_runner.py studio/production_os_worker.py tests/test_github_runner_usage.py tests/test_production_os_result_contract.py tests/test_production_os_worker.py tests/test_production_os_worker_runtime.py
git commit -m "feat(production-os): publish observability telemetry"
```

---

### Task 5: Add versioned pricing and usage aggregation

**Files:**
- Create: `src/production_os/dashboard_usage.py`
- Modify: `src/production_os/dashboard_store.py`
- Create: `tests/test_dashboard_usage.py`
- Modify: `tests/test_dashboard_store.py`

**Interfaces:**
- Consumes: raw usage/result fields from Tasks 2–4.
- Produces:
  - `PricingCatalog.from_mapping(payload: dict) -> PricingCatalog`
  - `PricingCatalog.estimate(provider: str, model: str, usage: dict, at: str) -> tuple[float | None, str | None]`
  - `aggregate_usage(rows: list[dict], *, window: str) -> dict`

- [ ] **Step 1: Write failing pricing/aggregation tests**

```python
def test_pricing_returns_unknown_for_unlisted_model():
    catalog = PricingCatalog.from_mapping({
        "version": "2026-09-22",
        "rules": [],
    })
    cost, version = catalog.estimate(
        "unknown", "model-x", {"input_tokens": 1000}, "2026-09-22T00:00:00Z"
    )
    assert cost is None
    assert version is None


def test_usage_aggregation_does_not_mix_live_snapshot_with_final_events():
    rows = [{
        "provider": "studio",
        "model": "model-a",
        "api_calls": 1,
        "input_tokens": 700,
        "cached_input_tokens": 0,
        "output_tokens": 200,
        "reasoning_tokens": 0,
        "total_tokens": 900,
        "estimated_cost_usd": None,
        "occurred_at": "2026-09-22T10:00:00+00:00",
    }]
    result = aggregate_usage(rows, window="24h")
    assert result["totals"]["total_tokens"] == 900
```

Also pin explicit zero vs unknown: missing token/cost fields remain unavailable metadata; a producer-reported zero remains zero.

- [ ] **Step 2: Run tests and verify failure**

```bash
pytest tests/test_dashboard_usage.py -q
```

Expected: missing module.

- [ ] **Step 3: Implement versioned catalog**

Use exact rule shape:

```python
{
    "version": "2026-09-22",
    "rules": [{
        "provider": "nvidia",
        "model": "example-model",
        "valid_from": "2026-09-01T00:00:00+00:00",
        "valid_to": None,
        "input_per_million_usd": 1.0,
        "cached_input_per_million_usd": 0.2,
        "output_per_million_usd": 2.0,
        "reasoning_per_million_usd": 2.0,
    }],
}
```

Only an exact provider/model match valid at execution time produces cost.

- [ ] **Step 4: Implement usage aggregation**

Supported windows:

```python
WINDOW_SECONDS = {
    "24h": 24 * 60 * 60,
    "7d": 7 * 24 * 60 * 60,
    "30d": 30 * 24 * 60 * 60,
    "all": None,
}
```

Reject any other value with `ValueError("invalid window")`.

Return totals, provider/model breakdown, and daily timeline. Use final `api_usage_events`; do not sum `live_usage_json` into historical totals.

- [ ] **Step 5: Run tests**

```bash
pytest tests/test_dashboard_usage.py tests/test_dashboard_store.py -q
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add src/production_os/dashboard_usage.py src/production_os/dashboard_store.py tests/test_dashboard_usage.py tests/test_dashboard_store.py
git commit -m "feat(observability): aggregate safe API usage"
```

---

### Task 6: Collect cached GitHub repository snapshots and reliable default-branch commit counts

**Files:**
- Modify: `src/production_os/github_client.py:20-602`
- Create: `src/production_os/dashboard_github.py`
- Create: `tests/test_dashboard_github.py`
- Modify: `tests/test_github_client_pr_files.py`

**Interfaces:**
- Consumes: existing `GitHubClient`, `DashboardStore`.
- Produces:
  - `GitHubClient.repository(full_name: str) -> dict`
  - `GitHubClient.default_branch_commit_count(full_name: str, branch: str) -> int`
  - `GitHubClient.open_pull_request_count(full_name: str) -> int`
  - `GitHubClient.latest_release(full_name: str) -> dict | None`
  - `RepositorySnapshotter.refresh(repository: str) -> dict`
  - `RepositorySnapshotter.get(repository: str, *, max_age_seconds: int = 300) -> dict`

- [ ] **Step 1: Write failing client/snapshot tests**

Use a fake GitHub transport whose `/commits?sha=main&per_page=1` response has:

```http
Link: <https://api.github.com/repos/dbrckk/example/commits?sha=main&per_page=1&page=214>; rel="last"
```

Assert:

```python
assert client.default_branch_commit_count("dbrckk/example", "main") == 214
```

Also test one-commit/no-Link response => `1`, empty response => `0`.

Snapshot failure test:

```python
def test_snapshotter_returns_cached_snapshot_as_degraded_on_github_failure(
    tmp_path,
):
    backend = SQLiteBackend(tmp_path / "production.db")
    store = DashboardStore(backend)
    github = FakeGitHub(
        repository={
            "default_branch": "main",
            "sha": "a" * 40,
            "commit_count": 7,
        }
    )
    snapshotter = RepositorySnapshotter(github, store)
    cached = snapshotter.refresh("dbrckk/example")
    github.fail = True
    result = snapshotter.get("dbrckk/example", max_age_seconds=0)
    assert result["degraded"] is True
    assert result["latest_commit_sha"] == cached["latest_commit_sha"]
    assert result["captured_at"] == cached["captured_at"]
```

- [ ] **Step 2: Run tests and verify failure**

```bash
pytest tests/test_dashboard_github.py tests/test_github_client_pr_files.py -q
```

- [ ] **Step 3: Add a header-preserving request helper without breaking `_get`**

Implement:

```python
def _request_json_with_headers(
    self,
    method: str,
    path: str,
) -> tuple[Any, dict[str, str]]:
    request = urllib.request.Request(
        f"{self.API}{path}",
        method=method.upper(),
        headers={
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "Production-OS/1.0",
            **(
                {"Authorization": f"Bearer {self.token}"}
                if self.token
                else {}
            ),
        },
    )
    try:
        with urllib.request.urlopen(
            request,
            timeout=self.timeout,
        ) as response:
            body = response.read()
            payload = json.loads(body.decode("utf-8")) if body else None
            headers = {str(k): str(v) for k, v in response.headers.items()}
            return payload, headers
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise GitHubAPIError(
            f"GitHub API {exc.code}: {body}"
        ) from exc
    except urllib.error.URLError as exc:
        raise GitHubAPIError(
            f"GitHub API unavailable: {exc}"
        ) from exc
```

Keep existing `_get` and `_request` return contracts unchanged by having them discard headers.

Parse the final page number from the RFC-style Link header; do not count pages by downloading the full history.

- [ ] **Step 4: Implement `RepositorySnapshotter`**

Validate repository format with:

```python
_REPOSITORY = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
```

Refresh stores:
- default branch;
- default-branch commit count;
- open PR count;
- latest commit SHA;
- latest release;
- latest known CI status when available;
- issue/test facts only when reliable, otherwise null;
- `captured_at`.

On remote failure, return the most recent stored snapshot with `degraded=True` and `fresh=False`. If no cache exists, raise a typed `RepositorySnapshotUnavailable`.

- [ ] **Step 5: Run tests**

```bash
pytest tests/test_dashboard_github.py tests/test_github_client_pr_files.py -q
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add src/production_os/github_client.py src/production_os/dashboard_github.py tests/test_dashboard_github.py tests/test_github_client_pr_files.py
git commit -m "feat(observability): snapshot GitHub project state"
```

---

### Task 7: Implement deterministic workflow progress and auditable hybrid project progress

**Files:**
- Create: `src/production_os/project_progress.py`
- Create: `tests/test_project_progress.py`
- Modify: `src/production_os/dashboard_store.py`

**Interfaces:**
- Consumes: workflow dicts from `WorkflowEngine.get`, repository snapshot, recent execution/events/visual evidence.
- Produces:
  - `workflow_progress(workflow: dict) -> dict`
  - `build_project_evidence(*, workflow: dict | None, repository_snapshot: dict | None, executions: list[dict], events: list[dict], visual_quality: dict | None) -> dict`
  - `ProjectProgressEngine.calculate(repository: str, evidence: dict, *, captured_at: str | None = None) -> dict`
  - persisted `project_progress_snapshots`.

- [ ] **Step 1: Write failing workflow-progress tests**

```python
def test_workflow_progress_is_weighted_by_estimated_minutes():
    workflow = {
        "tasks": [
            {"status": "succeeded", "estimated_minutes": 10},
            {"status": "running", "estimated_minutes": 30},
        ]
    }
    result = workflow_progress(workflow)
    assert result["percent"] == 25.0
    assert result["completed_weight"] == 10.0
    assert result["total_weight"] == 40.0


def test_zero_minute_virtual_barrier_does_not_distort_progress():
    workflow = {
        "tasks": [
            {"status": "succeeded", "estimated_minutes": 10},
            {"status": "pending", "estimated_minutes": 0},
        ]
    }
    assert workflow_progress(workflow)["percent"] == 100.0
```

Add tests for:
- impact-skipped terminal tasks count complete;
- failed/blocked/cancelled do not count complete;
- no executable weight => `percent=None`, not 100.

- [ ] **Step 2: Write failing project-profile/confidence tests**

```python
def test_backend_profile_marks_ui_and_assets_not_applicable():
    engine = ProjectProgressEngine()
    result = engine.calculate(
        "dbrckk/api",
        {
            "profile": "backend",
            "dimensions": {
                "code": {"score": 80, "evidence": 4, "fresh": True},
                "tests": {"score": 70, "evidence": 3, "fresh": True},
                "stability": {"score": 90, "evidence": 3, "fresh": True},
                "release": {"score": 50, "evidence": 2, "fresh": True},
            },
        },
    )
    assert result["components"]["ui_ux"]["status"] == "not_applicable"
    assert result["components"]["assets"]["status"] == "not_applicable"
    assert 0 <= result["score"] <= 100
```

- [ ] **Step 3: Run tests and verify failure**

```bash
pytest tests/test_project_progress.py -q
```

- [ ] **Step 4: Implement pure progress functions**

Use fixed profiles:

```python
PROFILES = {
    "visual_app": {
        "code": 0.25, "ui_ux": 0.15, "assets": 0.15,
        "tests": 0.15, "stability": 0.15, "release": 0.15,
    },
    "backend": {
        "code": 0.35, "tests": 0.25, "stability": 0.20, "release": 0.20,
    },
    "generic": {
        "code": 0.35, "ui_ux": 0.10, "assets": 0.10,
        "tests": 0.15, "stability": 0.15, "release": 0.15,
    },
}
CALCULATION_VERSION = "project-progress/v1"
```

Unknown dimensions are excluded from the numeric mean but reduce confidence. Not-applicable dimensions neither contribute nor reduce confidence.

Initial confidence thresholds:
- high: >= 0.80 evidence coverage and no stale critical dimension;
- medium: >= 0.50;
- low: below 0.50.

Expose the threshold values in code constants and pin them in tests.

- [ ] **Step 5: Build auditable evidence from real project facts**

Implement `build_project_evidence` so it maps only observed facts into the six dimensions. Example rules:

```python
def build_project_evidence(*, workflow, repository_snapshot, executions, events, visual_quality):
    evidence = {"dimensions": {}, "remaining_work": [], "blockers": []}
    if workflow:
        evidence["workflow"] = workflow_progress(workflow)
    if repository_snapshot:
        evidence["repository"] = {
            "ci_status": repository_snapshot.get("ci_status"),
            "latest_release": repository_snapshot.get("latest_release"),
            "tests_detected": repository_snapshot.get("tests_detected"),
            "tests_passing": repository_snapshot.get("tests_passing"),
            "tests_failing": repository_snapshot.get("tests_failing"),
        }
    if visual_quality:
        evidence["visual_quality"] = visual_quality
    evidence["execution_summary"] = _execution_summary(executions)
    evidence["recent_events"] = _relevant_progress_events(events)
    return evidence
```

A missing fact stays absent; this builder must never manufacture a score. `ProjectProgressEngine.calculate` converts the available evidence into dimension scores/confidence using versioned rules.

- [ ] **Step 6: Persist progress snapshots through `DashboardStore`**

The saved payload must contain:
- current workflow ID;
- deterministic production progress;
- global score;
- confidence;
- six component scores/nulls;
- evidence;
- remaining work;
- blockers;
- calculation version;
- selected profile.

- [ ] **Step 7: Run tests**

```bash
pytest tests/test_project_progress.py tests/test_dashboard_store.py -q
```

Expected: PASS.

- [ ] **Step 8: Commit**

```bash
git add src/production_os/project_progress.py src/production_os/dashboard_store.py tests/test_project_progress.py
git commit -m "feat(observability): calculate auditable project progress"
```

---

### Task 8: Build dashboard read models and authenticated API endpoints

**Files:**
- Create: `src/production_os/dashboard_service.py`
- Modify: `src/production_os/control_plane.py`
- Modify: `tests/test_dashboard_api.py`

**Interfaces:**
- Consumes: `DashboardStore`, `RepositorySnapshotter`, `ProjectProgressEngine`, existing workers/workflows/events.
- Produces:
  - `DashboardService.overview(window: str) -> dict`
  - `workers() -> dict`
  - `worker_detail(worker_id: str) -> dict`
  - `worker_logs(worker_id: str, after: str | None, limit: int) -> dict`
  - `worker_usage(worker_id: str, window: str) -> dict`
  - `projects() -> dict`
  - `project_detail(repository: str) -> dict`
  - `project_progress(repository: str) -> dict`
  - `project_commits(repository: str, window: str) -> dict`
  - `project_usage(repository: str, window: str) -> dict`
  - `project_workflows(repository: str) -> dict`
  - `project_history(repository: str) -> dict`
  - `activity(*, repository: str | None = None, worker_id: str | None = None, event_type: str | None = None, after: int = 0, limit: int = 100) -> dict`.

- [ ] **Step 1: Write API contract tests before service code**

Pin these routes:

```text
GET /v1/dashboard/overview?window=7d
GET /v1/dashboard/workers
GET /v1/dashboard/workers/{worker_id}
GET /v1/dashboard/workers/{worker_id}/logs
GET /v1/dashboard/workers/{worker_id}/usage?window=30d
GET /v1/dashboard/projects
GET /v1/dashboard/projects/{owner}/{repository}
GET /v1/dashboard/projects/{owner}/{repository}/progress
GET /v1/dashboard/projects/{owner}/{repository}/commits?window=30d
GET /v1/dashboard/projects/{owner}/{repository}/usage?window=30d
GET /v1/dashboard/projects/{owner}/{repository}/workflows
GET /v1/dashboard/projects/{owner}/{repository}/history
GET /v1/dashboard/activity?limit=100
```

Test:
- viewer succeeds;
- worker-only token without viewer privilege fails according to current role hierarchy;
- missing auth => 401;
- unknown worker/project => 404;
- `window=2h` => 400;
- `limit=999999` is clamped;
- stale GitHub data returns `degraded: true`, not 500.

- [ ] **Step 2: Run contract tests and verify failure**

```bash
pytest tests/test_dashboard_api.py -q
```

- [ ] **Step 3: Implement `DashboardService` with partial-section degradation**

Return a stable envelope:

```python
{
    "schema_version": "production-os/dashboard-overview/v1",
    "generated_at": "2026-09-22T12:00:00+00:00",
    "workers": {"total": 1, "online": 1, "busy": 0, "paused": 0, "offline": 0},
    "productions": {"running": 0, "queued": 0, "succeeded": 0, "failed": 0},
    "usage": {"api_calls": 0, "tokens": 0, "estimated_cost_usd": None},
    "commits": {"production_os": 0, "github_default_branch": 0},
    "performance": {"success_rate": None, "execution_seconds": 0.0},
    "projects": [],
    "errors": [],
}
```

If GitHub refresh fails but stored snapshots exist, include the cached data plus a section-level warning in `errors`. A GitHub error must not erase worker/workflow/API usage sections.

- [ ] **Step 4: Add URL parsing helpers and GET routes to control plane**

Validate project path segments separately:

```python
def _repository_from_dashboard_path(parts: list[str]) -> str:
    owner, repo = parts[3], parts[4]
    repository = f"{owner}/{repo}"
    if not _REPOSITORY.fullmatch(repository):
        raise ValueError("invalid repository")
    return repository
```

Every dashboard read branch calls `self._require("viewer")` before service access.

- [ ] **Step 5: Run API and legacy route suites**

```bash
pytest tests/test_dashboard_api.py tests/test_control_plane.py tests/test_workflow_api.py tests/test_http_security_headers.py -q
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add src/production_os/dashboard_service.py src/production_os/control_plane.py tests/test_dashboard_api.py
git commit -m "feat(dashboard): expose observability read APIs"
```

---

### Task 9: Move dashboard UI out of the control-plane monolith and ship the mobile V3 views

**Files:**
- Create: `src/production_os/dashboard_ui.py`
- Modify: `src/production_os/control_plane.py:84-600`
- Create: `tests/test_dashboard_ui_v3.py`
- Modify: `tests/test_dashboard_launch.py`
- Modify: `tests/test_http_security_headers.py`

**Interfaces:**
- Consumes: dashboard read APIs from Task 8 and existing workflow launch endpoints.
- Produces: `DASHBOARD_HTML` in `dashboard_ui.py`, imported/re-exported by `control_plane.py` for compatibility.

- [ ] **Step 1: Write failing structural UI tests**

```python
from production_os.dashboard_ui import DASHBOARD_HTML

def test_dashboard_has_primary_views_and_clickable_entities():
    for label in ("Vue générale", "Projets", "Workers", "Activité"):
        assert label in DASHBOARD_HTML
    assert 'data-view="overview"' in DASHBOARD_HTML
    assert 'data-view="projects"' in DASHBOARD_HTML
    assert 'data-view="workers"' in DASHBOARD_HTML
    assert 'data-view="activity"' in DASHBOARD_HTML


def test_polling_does_not_reload_or_replace_location():
    assert "location.reload(" not in DASHBOARD_HTML
    assert "window.location =" not in DASHBOARD_HTML
    assert "history.replaceState" in DASHBOARD_HTML
```

Also assert:
- worker detail tabs;
- project detail tabs;
- launch form still has repository + instruction + primary launch button;
- no enabled control-center buttons from Release 2;
- viewport meta and mobile breakpoint;
- no horizontal overflow rule;
- `aria-live` for state changes.

- [ ] **Step 2: Run UI tests and verify failure**

```bash
pytest tests/test_dashboard_ui_v3.py tests/test_dashboard_launch.py -q
```

- [ ] **Step 3: Extract dashboard module without changing route behavior**

At the top of `control_plane.py`:

```python
from .dashboard_ui import DASHBOARD_HTML
```

Delete the in-file 500+ line HTML constant only after compatibility tests import successfully.

- [ ] **Step 4: Implement V3 app state and navigation**

Use one in-memory state object:

```javascript
const appState = {
  view: "overview",
  workerId: null,
  repository: null,
  tab: null,
  polling: new Map(),
};
```

Navigation updates URL query state without reload:

```javascript
function navigate(next) {
  Object.assign(appState, next);
  const params = new URLSearchParams();
  if (appState.view) params.set("view", appState.view);
  if (appState.workerId) params.set("worker", appState.workerId);
  if (appState.repository) params.set("repo", appState.repository);
  if (appState.tab) params.set("tab", appState.tab);
  history.replaceState(null, "", "/dashboard?" + params.toString());
  renderActiveView();
}
```

- [ ] **Step 5: Implement component-level polling that preserves scroll/form state**

Do not replace the top-level `.shell`. Update only named containers with keyed render functions.

Use:

```javascript
function schedulePoll(key, intervalMs, fn) {
  if (appState.polling.has(key)) clearInterval(appState.polling.get(key));
  const id = setInterval(async () => {
    const y = window.scrollY;
    await fn();
    if (Math.abs(window.scrollY - y) > 1) window.scrollTo({top: y, behavior: "instant"});
  }, intervalMs);
  appState.polling.set(key, id);
}
```

The render functions must not touch `#repository` or `#instruction` unless the user explicitly changes launch state.

- [ ] **Step 6: Implement the four views and detail tabs**

Overview must render:
- workers online/busy/offline;
- running/queued productions;
- 24h/7d/30d selector;
- tokens/API calls/cost if known;
- Production-OS commits and default-branch commits;
- top active projects;
- recent activity.

Worker cards open:
`Aperçu | Tâches | Logs | API | Historique`.

Project cards open:
`Aperçu | Avancement | Commits | API | Workflows | Qualité | Historique`.

Progress must display:
- `Production actuelle`;
- `Projet estimé`;
- confidence badge;
- component breakdown;
- explanation/evidence/remaining work.

- [ ] **Step 7: Run UI + security tests**

```bash
pytest tests/test_dashboard_ui_v3.py tests/test_dashboard_launch.py tests/test_http_security_headers.py -q
```

Expected: PASS.

- [ ] **Step 8: Commit**

```bash
git add src/production_os/dashboard_ui.py src/production_os/control_plane.py tests/test_dashboard_ui_v3.py tests/test_dashboard_launch.py tests/test_http_security_headers.py
git commit -m "feat(dashboard): add mobile observability workspace"
```

---

### Task 10: Add historical backfill, end-to-end coverage, and release verification

**Files:**
- Modify: `src/production_os/dashboard_store.py`
- Modify: `src/production_os/dashboard_service.py`
- Create: `tests/test_dashboard_observability_e2e.py`
- Modify: `tests/test_production_stack_e2e.py`
- Modify: `README.md`

**Interfaces:**
- Consumes: all Release-1 modules.
- Produces: best-effort historical visibility and a release gate proving the dashboard from workflow creation through completion.

- [ ] **Step 1: Write a failing E2E scenario**

The test must perform:

```python
workflow = create_workflow(
    repository="dbrckk/example",
    task_id="build",
    estimated_minutes=30,
)
register_worker("worker-a", capabilities=["python"])
job = claim_and_ack(worker_id="worker-a")
post_telemetry(job["key"], {
    "worker_id": "worker-a",
    "stage": "implementation",
    "progress": 60,
    "usage": {"total_tokens": 500},
})
complete_job(job["key"], result={
    "usage": {
        "total_tokens": 900,
        "providers": [{
            "provider": "test-provider",
            "model": "test-model",
            "api_calls": 1,
            "input_tokens": 700,
            "cached_input_tokens": 0,
            "output_tokens": 200,
            "reasoning_tokens": 0,
            "total_tokens": 900,
        }],
    },
    "commits": {"count": 1, "shas": ["a" * 40]},
})
```

Then assert:
- worker detail includes the execution;
- project detail includes the workflow;
- usage totals equal 900, not 1400;
- Production-OS commit count is 1;
- progress endpoint returns deterministic production progress and a versioned global estimate;
- activity contains completion;
- no secret-like value appears in logs.

- [ ] **Step 2: Run E2E and verify failure**

```bash
pytest tests/test_dashboard_observability_e2e.py -q
```

- [ ] **Step 3: Implement best-effort historical backfill query behavior**

Do not mutate old records eagerly. In `DashboardService`, if v9 executions are absent for an older period:
- use `execution_history` only for duration/success/worker metrics;
- use existing `events` for lifecycle activity;
- use task `result_json.usage` when present;
- label `history_coverage="partial"`;
- never derive Production-OS commit attribution from unrelated repository SHAs.

- [ ] **Step 4: Update README operational documentation**

Document:
- new dashboard route remains `/dashboard`;
- pairing/auth behavior;
- new view names;
- meaning of the two progress percentages;
- estimated-cost caveat;
- commit-count distinction;
- live telemetry endpoint is worker-only;
- Release 1 controls are read-only.

- [ ] **Step 5: Run focused and full Production-OS verification**

```bash
pytest tests/test_dashboard_store.py tests/test_dashboard_usage.py tests/test_project_progress.py tests/test_dashboard_github.py tests/test_dashboard_api.py tests/test_dashboard_ui_v3.py tests/test_dashboard_observability_e2e.py -q
pytest -q
```

Expected: all available tests PASS.

- [ ] **Step 6: Run AI Dev Server verification**

From `dbrckk/ai-dev-server`:

```bash
python -m unittest tests.test_github_runner_usage tests.test_production_os_result_contract tests.test_production_os_worker tests.test_production_os_worker_runtime -v
```

Expected: PASS.

- [ ] **Step 7: Verify Render/GitHub Actions compatibility before merge**

Production-OS:
- CI workflow green.
- Existing Render start test still green: `pytest tests/test_render_start.py -q`.

AI Dev Server:
- `tests/test_production_os_actions_worker_workflow.py` green.
- No new required secret added for Release 1.

Run:

```bash
pytest tests/test_render_start.py tests/test_production_stack_e2e.py -q
python -m unittest tests.test_production_os_actions_worker_workflow -v
```

- [ ] **Step 8: Commit docs/E2E**

```bash
git add src/production_os/dashboard_store.py src/production_os/dashboard_service.py tests/test_dashboard_observability_e2e.py tests/test_production_stack_e2e.py README.md
git commit -m "test(observability): qualify dashboard release one"
```

---

## Release-1 Completion Gate

Before declaring Release 1 complete:

```bash
pytest -q
```

must pass in Production-OS, the focused AI Dev Server worker/result suites must pass, and fresh CI evidence must show no regression in production-stack qualification.

The release is not complete if any of these remain true:

- default-branch commit totals are fabricated or silently partial without metadata;
- usage can double-count live and final telemetry;
- project estimates lack confidence/evidence;
- a dashboard poll resets scroll or launch-form state;
- a credential-like value can reach persisted logs;
- SQLite and PostgreSQL schema/query behavior diverge.
