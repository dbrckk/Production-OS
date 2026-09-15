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
- [ ] external transparency-log anchoring

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
- [ ] dual-sign migration from P15 HMAC to P16 Ed25519
- [ ] key validity windows and revocation metadata
- [ ] SLSA/in-toto compatible statement envelope
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
