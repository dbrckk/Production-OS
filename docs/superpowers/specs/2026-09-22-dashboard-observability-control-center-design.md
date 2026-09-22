# Production-OS Dashboard Observability & Worker Control Center

Date: 2026-09-22  
Status: Design approved in conversation; implementation not started  
Target repositories: `dbrckk/Production-OS` and `dbrckk/ai-dev-server`

## 1. Purpose

Production-OS currently provides a compact mobile dashboard for launching workflows and checking basic runtime state. The next version must become a reliable operational control center rather than a thin launch surface.

The product must let an operator:

- understand the global state of Production-OS at a glance;
- inspect each worker in detail by clicking its card;
- inspect each project/repository in detail;
- see current workflow progress separately from estimated global project progress;
- understand API/token consumption and estimated cost by provider, model, worker, project, and time window;
- distinguish Production-OS-generated commits from the repository's overall main-branch commit count;
- inspect logs and execution history;
- control workers and jobs safely;
- understand why a project progress estimate has a given score.

The dashboard must remain practical on a smartphone. Heavy data must be fetched on demand, component refreshes must never reload the page or move the user's scroll position, and the backend must be the source of truth for computed metrics.

## 2. Scope

### In scope

1. Durable telemetry and aggregation in Production-OS.
2. Worker drill-down dashboard.
3. Project drill-down dashboard.
4. General overview and activity views.
5. Token/API usage and estimated cost.
6. Production-OS commit attribution and GitHub main-branch commit totals.
7. Deterministic current-workflow progress.
8. Auditable hybrid project-completion estimates with confidence.
9. Worker desired-state controls.
10. Job cancel/retry controls.
11. Structured logs with server-side secret redaction.
12. Historical snapshots for progress and repository state.
13. Mobile-first dashboard redesign.
14. GitHub Actions worker wake-up integration when configured.

### Out of scope for the first implementation

- Grafana, Prometheus, or another mandatory external observability stack.
- WebSockets as a hard dependency.
- Arbitrary shell/terminal control from the dashboard.
- Displaying or retrieving secrets.
- Fabricated provider quotas, balances, prices, or commit counts.
- Treating an AI-generated estimate as an objective fact.

Server-Sent Events or WebSockets may be added later if polling becomes insufficient.

## 3. Architectural decision

Production-OS is the observability source of truth.

Workers publish execution telemetry and structured progress/results to Production-OS. Production-OS persists raw facts, aggregates them into dashboard read models, calculates derived metrics, stores historical snapshots, and exposes authenticated dashboard APIs.

The browser does not calculate authoritative metrics from raw data and does not directly query providers for secrets or quotas.

GitHub remains the source of truth for repository facts such as:

- default branch;
- branch commit history;
- pull requests;
- releases;
- CI status;
- issue counts where applicable.

AI Dev Server remains responsible for producing execution-level evidence such as:

- coding-agent usage;
- provider/model identity when known;
- commit SHAs it creates;
- current stage;
- result envelope;
- optional progress telemetry.

## 4. Existing data that must be reused

The implementation must build on existing Production-OS primitives rather than duplicate them:

- `workers`
- `jobs`
- `claims`
- `workflows`
- `workflow_tasks`
- `execution_history`
- `events`
- workflow task `result_json`
- worker heartbeats and capabilities
- task `estimated_minutes`
- optimizer execution duration history
- AI Dev Server token-usage summaries already returned in Production-OS result envelopes

Existing event and execution history data can be used for best-effort historical backfill, but missing old telemetry must remain explicitly unknown rather than inferred.

## 5. Navigation and information architecture

Primary mobile navigation:

1. **Vue générale**
2. **Projets**
3. **Workers**
4. **Activité**

### Worker detail tabs

- Aperçu
- Tâches
- Logs
- API
- Historique
- Contrôle

### Project detail tabs

- Aperçu
- Avancement
- Commits
- API
- Workflows
- Qualité
- Historique

The current launch experience remains available from the general dashboard and must not become harder to reach.

## 6. Data model

The database schema advances from version 8 to version 9.

SQLite and PostgreSQL implementations must stay behaviorally equivalent.

### 6.1 worker_control_state

Durable operator intent is stored separately from observed worker status.

Fields:

- `worker_id TEXT PRIMARY KEY`
- `desired_state TEXT NOT NULL DEFAULT 'active'`
- `reason TEXT NULL`
- `requested_by TEXT NULL`
- `requested_at TEXT NOT NULL`
- `updated_at TEXT NOT NULL`

Allowed `desired_state` values:

- `active`
- `paused`
- `draining`

Cancellation is job-scoped rather than worker-scoped so workers with concurrency greater than one are never ambiguous.

Observed state remains in `workers.status`.

Example:

- observed state: `busy`
- desired state: `draining`

This means the worker may finish the current job but must not claim another.

### 6.2 job_control_state

Durable job-level operator intent is stored independently from worker control state.

Fields:

- `job_key TEXT PRIMARY KEY`
- `desired_state TEXT NOT NULL DEFAULT 'active'`
- `reason TEXT NULL`
- `requested_by TEXT NULL`
- `requested_at TEXT NOT NULL`
- `acknowledged_at TEXT NULL`
- `updated_at TEXT NOT NULL`

Allowed `desired_state` values:

- `active`
- `cancel_requested`

The authoritative cancellation outcome remains `jobs.status='cancelled'`; the control table records operator intent and acknowledgement, not a second copy of job outcome state.

This prevents a worker-wide cancellation flag from ambiguously targeting one of several concurrent jobs.

### 6.3 job_executions

One row represents one real execution attempt.

Required fields:

- `id TEXT PRIMARY KEY`
- `job_key TEXT NOT NULL`
- `workflow_id TEXT NULL`
- `workflow_task_id TEXT NULL`
- `repository TEXT NOT NULL`
- `worker_id TEXT NOT NULL`
- `attempt INTEGER NOT NULL DEFAULT 1`
- `status TEXT NOT NULL`
- `started_at TEXT NOT NULL`
- `finished_at TEXT NULL`
- `duration_seconds REAL NULL`
- `provider TEXT NULL`
- `model TEXT NULL`
- `api_calls INTEGER NOT NULL DEFAULT 0`
- `input_tokens INTEGER NOT NULL DEFAULT 0`
- `cached_input_tokens INTEGER NOT NULL DEFAULT 0`
- `output_tokens INTEGER NOT NULL DEFAULT 0`
- `reasoning_tokens INTEGER NOT NULL DEFAULT 0`
- `total_tokens INTEGER NOT NULL DEFAULT 0`
- `estimated_cost_usd REAL NULL`
- `pricing_catalog_version TEXT NULL`
- `commit_count INTEGER NOT NULL DEFAULT 0`
- `commit_shas_json TEXT NOT NULL DEFAULT '[]'`
- `retry_of_execution_id TEXT NULL`
- `error_type TEXT NULL`
- `error_message TEXT NULL`
- `current_stage TEXT NULL`
- `progress_percent REAL NULL`
- `live_usage_json TEXT NOT NULL DEFAULT '{}'`
- `last_telemetry_at TEXT NULL`
- `result_summary_json TEXT NOT NULL DEFAULT '{}'`
- `created_at TEXT NOT NULL`

Indexes:

- worker + started_at
- repository + started_at
- workflow + started_at
- job_key + attempt

Execution attempts are append-oriented. A retry creates a new execution row and never mutates the previous failed attempt into a success.

### 6.4 api_usage_events

This table preserves provider/model-level usage detail.

Fields:

- `id TEXT PRIMARY KEY`
- `execution_id TEXT NOT NULL`
- `worker_id TEXT NOT NULL`
- `repository TEXT NOT NULL`
- `provider TEXT NOT NULL`
- `model TEXT NOT NULL`
- `api_calls INTEGER NOT NULL DEFAULT 1`
- `input_tokens INTEGER NOT NULL DEFAULT 0`
- `cached_input_tokens INTEGER NOT NULL DEFAULT 0`
- `output_tokens INTEGER NOT NULL DEFAULT 0`
- `reasoning_tokens INTEGER NOT NULL DEFAULT 0`
- `total_tokens INTEGER NOT NULL DEFAULT 0`
- `estimated_cost_usd REAL NULL`
- `pricing_catalog_version TEXT NULL`
- `occurred_at TEXT NOT NULL`

A worker may submit one aggregate usage event per completed execution in the first release. Finer-grained events may be added later without changing the dashboard contract.

### 6.5 provider_quota_snapshots

Quota data is stored only when a provider exposes it reliably.

Fields:

- `id TEXT PRIMARY KEY`
- `provider TEXT NOT NULL`
- `quota_type TEXT NULL`
- `used_value REAL NULL`
- `limit_value REAL NULL`
- `remaining_value REAL NULL`
- `unit TEXT NULL`
- `source_status TEXT NOT NULL`
- `captured_at TEXT NOT NULL`

If a provider does not expose quota or remaining credit, `source_status` is `unavailable` and numeric values remain null.

### 6.6 worker_log_events

Structured logs exposed to the dashboard.

Fields:

- `id TEXT PRIMARY KEY`
- `worker_id TEXT NOT NULL`
- `repository TEXT NULL`
- `workflow_id TEXT NULL`
- `job_key TEXT NULL`
- `level TEXT NOT NULL`
- `stage TEXT NULL`
- `message TEXT NOT NULL`
- `provider TEXT NULL`
- `model TEXT NULL`
- `metadata_json TEXT NOT NULL DEFAULT '{}'`
- `created_at TEXT NOT NULL`

Levels:

- `debug`
- `info`
- `warning`
- `error`
- `critical`

Secrets are redacted before persistence.

### 6.7 project_repository_snapshots

Periodic repository-level facts.

Fields:

- `id TEXT PRIMARY KEY`
- `repository TEXT NOT NULL`
- `default_branch TEXT NULL`
- `production_os_commits INTEGER NOT NULL DEFAULT 0`
- `github_commits INTEGER NULL`
- `open_issues INTEGER NULL`
- `open_pull_requests INTEGER NULL`
- `ci_status TEXT NULL`
- `latest_commit_sha TEXT NULL`
- `latest_release TEXT NULL`
- `tests_detected INTEGER NULL`
- `tests_passing INTEGER NULL`
- `tests_failing INTEGER NULL`
- `snapshot_json TEXT NOT NULL DEFAULT '{}'`
- `captured_at TEXT NOT NULL`

`github_commits` means unique commits reachable from the repository's default branch at snapshot time. The UI must label this as the main/default-branch commit count rather than implying a sum across every branch.

### 6.8 project_progress_snapshots

Auditable global project progress.

Fields:

- `id TEXT PRIMARY KEY`
- `repository TEXT NOT NULL`
- `current_workflow_id TEXT NULL`
- `production_progress REAL NULL`
- `project_progress REAL NULL`
- `confidence TEXT NOT NULL`
- `code_score REAL NULL`
- `ui_ux_score REAL NULL`
- `assets_score REAL NULL`
- `tests_score REAL NULL`
- `stability_score REAL NULL`
- `release_score REAL NULL`
- `evidence_json TEXT NOT NULL DEFAULT '{}'`
- `remaining_work_json TEXT NOT NULL DEFAULT '[]'`
- `blockers_json TEXT NOT NULL DEFAULT '[]'`
- `calculation_version TEXT NOT NULL`
- `captured_at TEXT NOT NULL`

Allowed confidence values:

- `low`
- `medium`
- `high`

## 7. Telemetry ingestion

### 7.1 Execution lifecycle

When a worker successfully claims and acknowledges a job, Production-OS creates a `job_executions` row with status `running`.

On success:

- close the execution row;
- persist duration;
- persist normalized usage;
- persist commit SHAs;
- persist provider/model where known;
- persist result summary;
- update workflow task state through the existing workflow engine;
- append structured events.

On failure:

- close the execution row with `failed`;
- persist duration, usage available up to failure, and error metadata;
- retain the failed attempt for history;
- append structured events.

### 7.2 AI Dev Server result envelope

The worker result envelope must support normalized telemetry:

```json
{
  "usage": {
    "api_calls": 0,
    "input_tokens": 0,
    "cached_input_tokens": 0,
    "output_tokens": 0,
    "reasoning_tokens": 0,
    "total_tokens": 0,
    "providers": [
      {
        "provider": "nvidia",
        "model": "nvidia/nemotron-3-super-120b-a12b",
        "api_calls": 10,
        "input_tokens": 100000,
        "cached_input_tokens": 20000,
        "output_tokens": 10000,
        "reasoning_tokens": 5000,
        "total_tokens": 110000
      }
    ]
  },
  "commits": {
    "count": 2,
    "shas": ["...", "..."]
  },
  "progress": {
    "stage": "implementation",
    "percent": 64
  }
}
```

Fields may be absent when the underlying provider or runner cannot supply them. Absence remains unknown, not zero, unless the producer explicitly reports zero.

### 7.3 Live worker telemetry

Workers need an intermediate telemetry path so the dashboard can show current stage, task progress, and known API usage before a job completes.

Endpoint:

`POST /v1/jobs/{job_key}/telemetry`

Authentication: `worker`.

The request must include the worker identity and may include:

- current stage;
- progress percentage 0–100;
- cumulative known usage totals;
- cumulative provider/model usage breakdown;
- structured log entries;
- optional current result/evidence summary.

Production-OS validates that the job is currently claimed by that worker before accepting telemetry.

The server updates only the active `job_executions` row's live fields:

- `current_stage`
- `progress_percent`
- `live_usage_json`
- `last_telemetry_at`

Progress is clamped to 0–100 and must not move backwards for the same execution unless the worker explicitly starts a new stage that declares its own nested progress. Dashboard task progress therefore remains stable instead of oscillating because of malformed worker updates.

Live usage payloads are cumulative for the current execution. The server replaces the latest live snapshot rather than summing repeated heartbeats, preventing double counting. Provider/model `api_usage_events` are finalized from the correlated completion/failure envelope, where possible.

Structured log entries supplied through telemetry are redacted server-side before insertion into `worker_log_events`.

This endpoint is observability-only: malformed optional telemetry must not invalidate an otherwise valid heartbeat or completion path.

### 7.4 Cost calculation

Token counts are raw facts. Cost is derived.

Production-OS maintains a versioned pricing catalog keyed by provider/model and validity period.

An execution stores:

- the calculated estimated cost;
- the pricing catalog version used.

If no trustworthy price exists, `estimated_cost_usd` remains null and the UI shows cost unavailable.

Historical raw token usage must never be rewritten because of a later pricing change.

## 8. Commit attribution

Two commit metrics are displayed.

### Production-OS commits

A commit counts as Production-OS-generated only when its SHA is emitted by a correlated worker execution and persisted in `job_executions.commit_shas_json`.

Duplicate SHAs are counted once in aggregated project totals.

### GitHub default-branch commits

This count comes from GitHub and represents commits reachable from the repository's default branch.

The UI shows both values independently:

- Production-OS commits
- Default-branch commits

Time windows supported:

- 24h
- 7d
- 30d
- all available history

Historical windows may be limited by provider/API availability and must expose that limitation in metadata.

## 9. Progress models

### 9.1 Current production progress

Current-workflow progress is deterministic.

Primary formula:

```
production_progress =
  sum(weight of terminal-successful work) /
  sum(weight of all executable work) * 100
```

Default task weight is `estimated_minutes`.

Virtual barrier tasks with zero estimated minutes do not distort the score.

States:

- succeeded: contributes full weight;
- skipped because change-impact analysis proves no execution is required: contributes full weight;
- pending/ready/running: contributes zero completed weight;
- failed/blocked/cancelled: does not count as complete.

The API may additionally expose counts and ETA, but the percentage remains based on durable workflow state.

### 9.2 Global project progress

Global progress is an estimate and is always presented as such.

Default dimensions and weights for visual/game-style repositories:

- Code / functionality: 25%
- UI / UX: 15%
- Assets: 15%
- Tests / CI: 15%
- Stability: 15%
- Release readiness: 15%

Production-OS selects a versioned progress profile appropriate to the repository type. Dimensions that are genuinely not applicable are marked `not_applicable` and their weights are redistributed across applicable dimensions. A backend/service project is therefore not penalized for lacking game assets or UI screens. Unknown evidence and not-applicable dimensions are distinct states.

Each applicable dimension contains:

- score 0–100;
- evidence items;
- evidence freshness;
- confidence.

Evidence may include:

- completed vs remaining workflows/tasks;
- CI state;
- tests detected/passing/failing;
- release state;
- issues, roadmap entries, and explicit remaining-work markers;
- assets expected/generated/rejected;
- visual-quality evidence;
- recurring failures;
- blockers;
- build/package readiness;
- recent project analysis from Production-OS.

The global score is the weighted mean of available dimension scores.

A dimension with insufficient evidence is marked unknown rather than silently assigned a neutral score. The overall confidence decreases as evidence coverage/freshness decreases.

The dashboard must show:

- score;
- confidence;
- component scores;
- evidence summary;
- remaining work;
- blockers;
- calculation version;
- progress profile/version;
- snapshot time.

Clicking a progress score must explain why the score exists.

### 9.3 Confidence

Initial policy:

- high: broad, recent, mutually consistent evidence across most dimensions;
- medium: partial but meaningful objective evidence;
- low: sparse, stale, or conflicting evidence.

The exact thresholds belong in implementation code and tests, versioned under `calculation_version`.

## 10. Worker control semantics

Worker control is based on durable desired state.

### pause

- sets desired state to `paused`;
- does not interrupt the active task;
- worker finishes current work but must not claim another job.

### drain

- sets desired state to `draining`;
- worker immediately stops claiming new work;
- worker finishes active jobs;
- while active jobs remain, observed state may be `busy` with desired state `draining`;
- once active jobs reach zero, the worker reports `drained` while continuing heartbeat/reconciliation;
- intended for graceful maintenance or shutdown preparation.

### resume

- sets desired state to `active`;
- worker may claim work again.

### cancel-current

- creates or updates `job_control_state` for the explicitly selected active job with `cancel_requested`;
- the worker observes the job-scoped request at heartbeat/checkpoint boundaries;
- it stops cleanly at the next supported safe interruption point;
- the job becomes cancelled only after Production-OS receives or reconciles the cancellation outcome;
- if a worker has multiple active jobs, the API requires the target `job_key` and never guesses which one to cancel.

No UI action may pretend a remote process was killed when no acknowledgement exists.

### kick

For persistent workers, kick may be a no-op or a wake signal appropriate to that worker type.

For the GitHub Actions ephemeral worker:

- when a GitHub dispatch credential/integration is configured, Production-OS dispatches the worker workflow and returns the dispatch result;
- otherwise the API returns a clear deferred result such as `scheduled_fallback`, with the known periodic polling interval.

The UI must never claim immediate wake-up when only the five-minute schedule is available.

## 11. Job control semantics

### cancel

Allowed for queued jobs and cooperatively cancellable active jobs.

Queued jobs can be cancelled immediately in Production-OS.

Active jobs require a cancellation request and worker acknowledgement/checkpoint semantics.

### retry

Retry creates a new execution attempt connected through `retry_of_execution_id`.

It does not delete or overwrite the previous failure.

Retries remain constrained by workflow generation, max attempts, and current job/workflow validity rules.

## 12. Dashboard API contract

All dashboard read endpoints require at least `viewer`.

All mutations require `operator`.

### 12.1 General overview

`GET /v1/dashboard/overview?window=7d`

Returns:

- worker counts by state;
- production/workflow counts by state;
- API usage totals;
- estimated cost;
- Production-OS commit count;
- default-branch commit count;
- success rate;
- execution time;
- active project summaries.

### 12.2 Worker list

`GET /v1/dashboard/workers`

Each worker summary includes:

- worker ID;
- observed status;
- desired state;
- heartbeat time;
- capabilities;
- current repository/workflow/job/stage/progress;
- today's usage;
- basic performance statistics.

### 12.3 Worker detail

`GET /v1/dashboard/workers/{worker_id}`

Returns:

- identity/state/capabilities;
- current execution;
- elapsed time;
- provider/model;
- current known usage;
- historical performance;
- recent projects;
- control availability.

### 12.4 Worker logs

`GET /v1/dashboard/workers/{worker_id}/logs?limit=100&after=<cursor>`

Cursor-based pagination is required.

### 12.5 Worker usage

`GET /v1/dashboard/workers/{worker_id}/usage?window=30d`

Returns:

- totals;
- provider/model breakdown;
- timeline;
- optional quota snapshots.

### 12.6 Worker control

`POST /v1/dashboard/workers/{worker_id}/control`

Body:

```json
{"action":"pause"}
```

Allowed actions:

- pause
- resume
- drain
- cancel-current
- kick

Response distinguishes request acceptance from remote acknowledgement.

### 12.7 Job control

`POST /v1/dashboard/jobs/{job_key}/control`

Allowed actions:

- cancel
- retry

### 12.8 Project list

`GET /v1/dashboard/projects`

Each entry includes:

- repository;
- status;
- current production progress;
- global project progress;
- confidence;
- active worker;
- commit metrics;
- usage;
- last activity.

### 12.9 Project detail

Repository paths contain owner and repository as separate URL segments:

`GET /v1/dashboard/projects/{owner}/{repository}`

Returns:

- project status;
- current production;
- global progress;
- commits;
- usage;
- latest workflow/build/release signals.

### 12.10 Progress explanation

`GET /v1/dashboard/projects/{owner}/{repository}/progress`

Returns:

- score;
- confidence;
- dimension scores;
- evidence;
- remaining work;
- blockers;
- calculation version;
- captured_at.

### 12.11 Project commits

`GET /v1/dashboard/projects/{owner}/{repository}/commits?window=30d`

Returns both commit categories and recent commit details.

### 12.12 Project usage

`GET /v1/dashboard/projects/{owner}/{repository}/usage?window=30d`

Same aggregation model as worker usage.

### 12.13 Project workflows and history

- `GET /v1/dashboard/projects/{owner}/{repository}/workflows`
- `GET /v1/dashboard/projects/{owner}/{repository}/history`

History exposes progress snapshots and major project events.

### 12.14 Activity

`GET /v1/dashboard/activity?repository=&worker_id=&type=&after=&limit=100`

Returns normalized activity entries sourced primarily from the existing event ledger plus telemetry events.

## 13. Refresh behavior

No full-page refresh is allowed during normal dashboard polling.

Recommended initial intervals:

- active worker/current task: 5s
- active logs: 5s
- current workflow progress: 5–10s
- overview: 15s
- API usage: 30s
- GitHub repository facts: 2–5 min
- global project progress: event-driven plus periodic snapshot

Updating a component must preserve:

- scroll position;
- selected tab;
- open detail view;
- user-entered workflow instruction;
- selected repository.

## 14. Mobile UI behavior

The dashboard remains dark, compact, and card-based.

Requirements:

- large tap targets;
- sticky primary navigation;
- status pills with both color and text;
- readable progress bars;
- no horizontal overflow on common Android viewport widths;
- skeleton/loading placeholders;
- lazy loading for detail tabs;
- bounded log rendering;
- critical actions separated from normal navigation;
- confirmation for destructive/interrupting actions;
- disabled actions explain why they are unavailable.

Worker cards and project cards are clickable as whole cards, while nested action buttons remain independently accessible.

## 15. Security

1. Secrets, tokens, authorization headers, API keys, and credential-like values are redacted server-side before log persistence.
2. Dashboard APIs never return raw credentials.
3. Read endpoints require `viewer`.
4. Control endpoints require `operator`.
5. Existing token-role hierarchy remains authoritative.
6. Mutation endpoints validate allowed state transitions.
7. GitHub dispatch credentials remain server-side only.
8. Pricing and quota connectors must fail closed on authentication or malformed responses.
9. Log metadata receives size limits and field allow/deny sanitization.
10. User-provided repository names and cursor parameters are validated.

## 16. Migration and backward compatibility

Schema migration 8 -> 9 must be idempotent for both SQLite and PostgreSQL.

Existing deployments must retain:

- workflow/job history;
- releases and transparency data;
- current dashboard launch capability;
- existing auth tokens and role behavior.

Workers without a `worker_control_state` row are interpreted as desired state `active` until an operator changes that state. This makes the migration compatible with existing workers without requiring an eager row for every historical worker.

Backfill strategy:

- use `execution_history` for historical durations/success/worker association;
- use `events` for historical lifecycle facts;
- use workflow task results for historical token summaries where present;
- do not invent provider/model/commit attribution for old runs when missing.

The UI must represent partial historical data explicitly.

## 17. Failure handling

### Worker offline

The detail page remains accessible using last-known data and displays freshness.

### GitHub unavailable

Production-OS returns cached repository snapshots with:

- freshness timestamp;
- degraded/stale marker.

### Provider pricing unavailable

Token counts still display. Cost is null/unavailable.

### Quota unavailable

Quota is shown as unavailable, not zero.

### Telemetry malformed

Reject invalid telemetry fields without corrupting workflow completion. Core job completion remains possible when optional observability data is malformed, but a telemetry-validation event is recorded.

### Dashboard aggregation failure

The API should return partial sections with explicit errors where practical instead of turning every non-critical metric failure into a total dashboard outage.

## 18. Testing strategy

### Database

Tests for SQLite and PostgreSQL:

- schema v9 creation;
- idempotent initialization;
- execution append semantics;
- retry lineage;
- indexes/queries;
- snapshot persistence;
- worker desired-state persistence.

### Telemetry

Tests for:

- live telemetry ownership validation;
- cumulative live usage without double counting;
- monotonic active-execution progress;
- normalized token aggregation;
- unknown vs explicit zero;
- provider/model breakdown;
- commit SHA deduplication;
- pricing catalog versioning;
- secret redaction;
- malformed telemetry handling.

### Progress

Tests for:

- weighted task progress;
- skipped impacted tasks;
- zero-minute virtual barriers;
- failed/blocked/cancelled tasks;
- unknown project dimensions;
- confidence calculation;
- evidence freshness;
- score bounds 0–100;
- calculation-version stability.

### Controls

Tests for:

- pause;
- drain;
- resume;
- job-scoped cooperative cancellation on workers with one and multiple active jobs;
- queued cancellation;
- retry lineage;
- max-attempt enforcement;
- kick configured;
- kick fallback when dispatch is unavailable;
- operator-only authorization.

### API

Contract tests for every dashboard endpoint, including:

- role enforcement;
- pagination;
- time windows;
- missing worker/project;
- partial/stale data;
- schema version fields.

### Frontend

Tests for:

- worker card -> detail navigation;
- project card -> detail navigation;
- tab state;
- no scroll reset on polling;
- no full-page refresh;
- mobile layout;
- destructive-action confirmation;
- unavailable-action explanation;
- progress explanation;
- partial-data rendering.

### End-to-end

At least one production-stack E2E scenario must:

1. create a workflow;
2. register a worker;
3. claim/ack a job;
4. submit telemetry;
5. complete the job;
6. verify worker detail;
7. verify project detail;
8. verify usage;
9. verify progress;
10. verify commit attribution;
11. verify activity history.

## 19. Delivery sequence

### Release 1: observability

- schema v9;
- execution/usage/log/project snapshot persistence;
- dashboard aggregation service;
- overview;
- worker list/detail;
- project list/detail;
- current production progress;
- global project progress;
- usage and commit metrics;
- basic history;
- mobile UI redesign.

### Release 2: control center

- worker desired-state enforcement;
- pause/resume/drain;
- cooperative cancellation;
- retry;
- GitHub Actions kick integration;
- richer live logs;
- alerts and anomaly indicators;
- deeper historical analysis.

Release 1 must not expose controls that are visually enabled but not operational.

## 20. Acceptance criteria

The design is complete when implementation can demonstrate all of the following:

1. Clicking a worker opens a dedicated dashboard with useful operational information.
2. The worker page exposes current work, capabilities, health, usage, history, logs, and performance.
3. The project page shows current production progress and separate global project progress.
4. Global progress includes confidence, component breakdown, evidence, remaining work, and blockers.
5. API usage can be grouped by project, worker, provider/model, and time window.
6. Estimated cost is shown only when a trustworthy pricing rule exists.
7. Provider quota is shown only when the provider exposes it reliably.
8. Production-OS commits and default-branch commits are displayed separately.
9. Polling does not reload the page or reset mobile scroll position.
10. Historical progress snapshots can show project evolution over time.
11. Secrets never appear in dashboard logs or API responses.
12. Worker/job controls are role-protected and accurately distinguish requested from acknowledged state.
13. The GitHub Actions worker can be kicked immediately only when a dispatch integration is configured; otherwise the UI reports the scheduled fallback.
14. Existing workflow creation/dispatch remains functional throughout the migration.
15. SQLite and PostgreSQL behavior remains covered by equivalent tests.

## 21. Implementation constraints

- Follow the existing Production-OS auth model.
- Prefer focused modules over growing `control_plane.py` into a larger monolith.
- Keep dashboard aggregation isolated behind explicit interfaces.
- Preserve current public health endpoints.
- Do not add paid infrastructure as a mandatory dependency.
- Keep Render deployment compatibility.
- Keep GitHub Actions worker compatibility.
- Preserve existing release/transparency trust guarantees.
