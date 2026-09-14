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
- [ ] optional PostgreSQL backend
- [ ] TLS termination / reverse-proxy reference config
