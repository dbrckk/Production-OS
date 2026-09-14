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
- [ ] GitHub issue/PR state ingestion
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
