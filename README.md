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

## Dashboard Control Center Release 2

The dashboard control center separates **desired control intent** from **observed worker state**.

Worker controls:

- `pause`: blocks new claims and lets the current task continue;
- `drain`: blocks new claims and lets active tasks finish before the worker becomes drained;
- `resume`: returns the worker desired state to `active`;
- `cancel-current`: cooperatively cancels one explicitly named active `job_key`;
- `retry`: creates a new workflow attempt with a new job key while preserving prior execution history;
- `kick`: requests an immediate GitHub Actions worker run only when server-side GitHub dispatch credentials are configured.

All dashboard control endpoints require the `operator` role.

Cancellation is job-scoped rather than worker-wide. A cancellation request is not considered acknowledged until the worker reports the matching `cancel_requested` state. Terminal job transitions are exclusive: once cancellation wins, a late completion is rejected; once completion wins, a later cancel-current request is rejected.

Retries preserve lineage. The previous failed or cancelled execution remains immutable, the replacement receives a new idempotency/job key, workflow generation checks still apply, and `max_attempts` cannot be bypassed by repeated control requests.

GitHub Actions kick outcomes are reported honestly:

```text
dispatched
scheduled_fallback
failed
```

`scheduled_fallback` means no immediate dispatch was possible and the existing five-minute scheduled worker poll remains the next wake-up path. It must not be presented as a started worker.

The UI separately presents:

```text
Action demandée
Confirmée par le worker
```

so operator intent is never displayed as runtime acknowledgement before heartbeat evidence exists.

Optional server-side configuration:

```text
PRODUCTION_OS_ACTIONS_REPOSITORY=dbrckk/ai-dev-server
PRODUCTION_OS_ACTIONS_WORKFLOW=production-os-actions-worker.yml
PRODUCTION_OS_ACTIONS_REF=main
```

The GitHub token remains server-side and is never returned to dashboard JavaScript.

## Dashboard Control Center Release 3

Release 3 hardens day-to-day operation of the control center.

### Operator audit

Every operator control action is written to a dedicated durable audit log with:

```text
action
worker_id
optional job_key
requested_by
outcome
optional error_code
requested_at
```

The audit schema intentionally has no columns for bearer tokens, authorization headers, GitHub tokens, or arbitrary secret metadata.

Dashboard viewers can inspect:

```text
GET /v1/dashboard/control-audit?limit=100
```

Worker credentials cannot read dashboard audit history.

### Operational health

The liveness endpoint `/health` only answers whether the HTTP service is alive.

Operational health is separate:

```text
GET /v1/dashboard/health
```

It reports `healthy` or `degraded` with explicit reasons such as:

- queued work with no online worker;
- a busy worker whose heartbeat is stale;
- a running execution whose telemetry is stale.

These diagnostics do not automatically cancel or mutate work.

### Targeted stuck-job recovery

The dashboard exposes a recovery action only for jobs that are still in `claimed` state and whose acknowledgement deadline has expired.

```text
recover-stuck
```

Recovery is job-scoped and requires an explicit `job_key`. A non-expired claim is rejected. The attempt budget is preserved:

- below `max_attempts` → return the job to `queued`;
- at or above `max_attempts` → move the job to `dead-letter`.

The action is audited whether it succeeds or is rejected.

## Dashboard Control Center Release 4

Release 4 adds durable operational incident management on top of Release 3 health diagnostics.

Incidents follow the lifecycle:

```text
open → acknowledged → resolved
```

Health diagnostics are converted into targeted incidents for:

- the global control plane;
- an individual worker;
- an individual job.

Repeated polling does not inflate the occurrence counter when the evidence is unchanged. If an incident clears, it is marked `resolved` rather than deleted. If the same condition later returns, the incident reopens as `open`, increments its occurrence count, and clears the previous acknowledgement.

Dashboard endpoints:

```text
GET  /v1/dashboard/incidents
POST /v1/dashboard/incidents/{incident_id}/acknowledge
```

Viewer and operator roles may read incidents. Acknowledgement requires operator. Worker credentials cannot read dashboard incident history.

Acknowledgement records the operator identity and timestamp. Incident records deliberately avoid arbitrary payload, metadata, authorization headers, or credential fields.

Incident reconciliation is observational only. It does not automatically pause workers, cancel jobs, retry work, or run stuck-job recovery.

## Dashboard Control Center Release 5 — Safe remediation playbooks

Durable incidents can now expose deterministic remediation guidance derived from current server facts.

The dashboard never decides availability on its own. Each playbook suggestion includes:

```text
action
worker_id
job_key
availability
reason
interrupting
```

Availability values are:

```text
available
fallback
unavailable
```

Examples:

- `queue_without_worker` may suggest a GitHub Actions `kick`;
- `stale_busy_workers` may suggest inspection and a targeted `recover-stuck` only for an expired claimed job;
- `stale_running_executions` may suggest inspection and an explicit `cancel-current` only while the named job is still active and owned by the named worker.

Resolved incidents expose no remediation actions.

Playbook generation is read-only and deterministic. It does not mutate the queue, pause workers, cancel jobs, retry work, or recover claims.

Interrupting remediation always requires an explicit operator action and reuses the existing validated control API, including the same confirmation flow used by direct worker controls. Inspection suggestions are navigation-only.

The browser receives no GitHub, worker, or operator credentials from playbook generation.

## Dashboard Control Center Release 6 — Remediation history

Incident-linked remediation actions now have durable lineage in a dedicated remediation ledger.

This ledger is separate from the generic control audit and records only structured fields:

```text
incident_id
action
worker_id
job_key
requested_by
outcome
error_code
requested_at
completed_at
```

No credentials, authorization headers, tokens, arbitrary metadata or free-form request payloads are stored.

When a playbook action is executed from the dashboard, the browser sends the incident id together with the existing worker control request. The server then re-derives the current incident playbook and verifies the exact action, worker target, job target and availability before any control mutation occurs.

If the incident is stale, resolved, the target changed, or the suggested action is no longer available, the server returns a conflict and does not create control or remediation state.

Direct operator controls remain supported without an incident id and continue to use the existing control audit only.

The dashboard Activity view exposes both:

```text
Audit des contrôles
Historique des remédiations
```

so operators can distinguish ordinary control actions from incident-driven remediation.

## Dashboard Control Center Release 7 — Remediation verification

Incident-linked remediation history now distinguishes the control result from whether the incident was actually cleared.

Verification states are:

```text
pending
still_active
resolved
not_applicable
```

Semantics:

- `pending`: the remediation request completed but has not yet been checked against refreshed incident state;
- `still_active`: the related incident remains open or acknowledged after a verification refresh;
- `resolved`: the related incident is durably resolved;
- `not_applicable`: the remediation action itself failed, so effectiveness verification does not apply.

Verification is observational only. It never triggers another kick, retry, cancellation, recovery, pause, resume or drain action.

The verification engine runs from current durable incident state. A resolved verification is terminal and does not regress if the same incident later reopens as a new occurrence.

To avoid write amplification from dashboard polling, repeated checks that would keep the same verification state do not rewrite the remediation ledger or increment the verification counter.

Existing schema v12 databases are migrated additively to schema v13 with:

```text
verification_state
verification_checks
verified_at
```

The Activity view shows control outcome and remediation verification separately.

## Dashboard Control Center Release 8 — Remediation analytics

The dashboard can summarize observed remediation effectiveness without turning historical metrics into automatic control decisions.

Analytics support the existing dashboard windows:

```text
24h
7d
30d
all
```

The summary exposes:

```text
total
resolved
still_active
pending
not_applicable
effectiveness_denominator
observed_resolution_rate
median_resolution_detection_seconds
```

The observed resolution rate uses only remediation events with a verification state of `resolved` or `still_active`:

```text
resolved / (resolved + still_active)
```

Pending and not-applicable events are excluded from that denominator.

The median resolution-detection duration is calculated only from resolved events with valid `completed_at` and `verified_at` timestamps.

Breakdowns are available by control action and by incident code. Every rate is displayed with its observed sample size. A zero-size effectiveness sample produces no rate rather than an inferred value.

These analytics are read-only. They never rank playbooks, launch controls, or change worker, job, workflow, incident, or remediation state beyond the existing incident refresh needed to read current verification facts.

## Dashboard Control Center Release 9 — Remediation recurrence

Resolved remediation events are now monitored for incident recurrence.

When a remediation verification becomes `resolved`, Production-OS stores the incident's current `occurrence_count` and starts a read-only recurrence watch.

If the same durable incident later reopens and its `occurrence_count` becomes greater than the stored resolution snapshot, the remediation event is marked:

```text
recurrence_state = recurred
```

The recurrence lifecycle is:

```text
not_evaluated -> watching -> recurred
```

`recurred` is terminal for that remediation event. Pending, still-active and not-applicable remediations do not enter recurrence tracking.

Recurrence is observational only. It never triggers retry, cancellation, recovery, pause, drain, kick or any other control action.

Remediation analytics expose recurrence with explicit denominators:

```text
watching_recurrence
recurred
recurrence_denominator
observed_recurrence_rate
```

The dashboard Activity view presents recurrence separately from control outcome and remediation verification.

## Dashboard Control Center Release 10 — Remediation durability

Remediation analytics now measure observed durability after a verified resolution.

For remediations that later recur, Production-OS derives:

```text
median_time_to_recurrence_seconds
min_time_to_recurrence_seconds
max_time_to_recurrence_seconds
```

For resolved remediations that remain under recurrence watch, Production-OS exposes:

```text
median_watching_age_seconds
```

These metrics are descriptive only. They never trigger retry, cancel, recovery, pause, drain, kick or any other control action.

Invalid or chronologically inconsistent timestamps are ignored instead of being converted into misleading durations.

## Dashboard Control Center Release 11 — Simplified launch UX

The default operator workflow is intentionally minimal:

```text
select repository
enter instruction
launch production
```

Opening the Production-OS service root redirects to `/dashboard`. Machine health checks remain available at `/health` and `/healthz`.

Repository discovery is performed by Production-OS on the server through `GitHubClient`. The browser no longer calls GitHub's repository API directly.

When a server-side GitHub token is available, Production-OS lists repositories accessible to that credential for the configured owner. If not, it falls back to the owner's public repositories. If GitHub itself is unavailable, the picker degrades to repositories already observed locally by Production-OS.

No additional operator credential, token field or launch parameter is introduced.

## Dashboard Control Center Release 12 — Storage maintenance visibility

Production-OS exposes a read-only storage maintenance snapshot at:

```text
GET /v1/dashboard/maintenance
```

It reports:

- backend kind (SQLite or PostgreSQL);
- measurable database size in bytes;
- row counts for durable operational tables;
- oldest/newest valid timestamps;
- invalid timestamp counts;
- configured retention days and cutoffs;
- rows currently older than each retention window;
- total retention candidates;
- a maintenance status: `healthy`, `attention`, or `unknown`.

Default retention windows are currently diagnostic only:

```text
worker logs                  30 days
API usage                    90 days
job executions               90 days
control audit               180 days
remediation history         180 days
repository/progress snapshots 90 days
generic event stream         90 days
```

Release 12 performs no deletion, VACUUM, backup mutation or restore action. It deliberately establishes visibility before destructive maintenance is introduced. Timestamp scans are streamed row by row so large history tables do not need to be loaded fully into memory. The resulting maintenance snapshot is cached server-side for five minutes (30 seconds after an unknown/error state), so normal dashboard polling does not repeatedly rescan large tables.

The dashboard never exposes the SQLite path, PostgreSQL DSN, credentials or tokens. If maintenance diagnostics fail, the rest of the Overview remains available and the storage card degrades to `unknown`.

## Dashboard Control Center Release 13 — Safe retention cleanup

Expired historical data can now be pruned explicitly by an operator from the Storage & retention card.

The cleanup endpoint is:

```text
POST /v1/dashboard/maintenance/prune
```

and requires both:

```text
confirm = PRUNE_EXPIRED_HISTORY
expected_candidate_rows = <fresh prunable count observed by the operator>
```

The server recomputes every eligible row inside the cleanup transaction. If the current prunable count differs from the operator's expected count, cleanup returns a conflict and deletes nothing.

Prunable history includes expired:

- API usage events;
- worker log events;
- terminal job executions (`succeeded`, `failed`, `cancelled`);
- control audit events;
- repository/progress snapshots;
- generic event-stream entries.

Protected data includes:

- running/non-terminal executions;
- incident records;
- remediation history;
- workflows and workflow tasks;
- jobs and workers;
- worker/job desired control state;
- release/trust history;
- invalid timestamps and rows newer than their retention cutoff.

Cleanup is never automatic. It is not triggered by alerts, health checks, analytics or dashboard polling. The UI requires an explicit browser confirmation, and every accepted/conflicted cleanup request is recorded in the control audit.

Release 13 does not run `VACUUM` in the request path and does not mutate backup/restore state.

## Dashboard Control Center Release 14 — Backup readiness

Production-OS can create verified server-side SQLite backups before any restore capability is enabled.

SQLite backup creation uses the online SQLite backup API, then performs:

```text
online backup
-> PRAGMA integrity_check
-> SHA-256 + size
-> atomic rename
-> safe manifest
```

The backup directory is configured only on the server through:

```text
PRODUCTION_OS_BACKUP_DIR
```

No filesystem path, database path, DSN, token, password, or secret is returned by the dashboard API or stored in the backup manifest.

Backup creation is operator-only and requires the exact confirmation phrase:

```text
CREATE_VERIFIED_BACKUP
```

Viewer access is limited to backup readiness and verified catalog metadata.

PostgreSQL backup creation is intentionally not claimed in Release 14. The dashboard reports it as unsupported until qualified external `pg_dump` tooling is explicitly integrated.

Restore remains disabled.

## Dashboard Control Center Release 15 — Restore readiness

Production-OS can verify that a server-created SQLite backup is genuinely restorable without modifying the live database.

Restore-readiness verification accepts only the server-issued `backup_id`; clients never provide filesystem paths. The server derives the backup and manifest locations from `PRODUCTION_OS_BACKUP_DIR`, then verifies:

```text
manifest identity
-> exact file size
-> SHA-256
-> read-only SQLite open
-> PRAGMA integrity_check
-> schema_meta schema_version
```

Verification is operator-only and requires the exact confirmation:

```text
VERIFY_BACKUP_FOR_RESTORE
```

The operation is audit logged. It does not write to the live database or the backup database.

Restore remains disabled in Release 15. PostgreSQL restore verification remains unsupported until qualified `pg_dump` / `pg_restore` tooling is integrated.

No database path, backup path, DSN, token, password or secret is returned by the API or rendered in the dashboard.

## Release 19 — Safe restore staging

Verified SQLite backups can be materialized into an isolated restore candidate without mutating the live database.

The operator action:

```text
POST /v1/dashboard/backups/{backup_id}/stage-restore
confirm = STAGE_VERIFIED_RESTORE
```

performs:

1. Existing backup manifest, size, SHA-256 and SQLite integrity verification.
2. SQLite backup-copy into a server-generated temporary candidate.
3. Candidate `PRAGMA integrity_check`.
4. Candidate schema version read.
5. Candidate SHA-256 and size calculation.
6. Atomic rename inside `PRODUCTION_OS_BACKUP_DIR`.

The browser never provides or receives filesystem paths.

The returned candidate metadata includes:

```text
candidate_id
source_backup_id
backend_kind
verified
integrity
schema_version
size_bytes
sha256
staged_at
activation_enabled = false
```

Restore staging is deliberately non-destructive. It never swaps or overwrites the active Production-OS database. Live activation remains disabled and must be designed as a separate maintenance-mode operation.

## Release 20 — Exclusive SQLite maintenance lock

The long-running control-plane server now owns an exclusive operating-system lock for the lifetime of a SQLite database process.

The lock is based on POSIX `flock(LOCK_EX | LOCK_NB)`, not file age. This means:

- a second control-plane process fails fast while the first process holds the lock;
- the kernel automatically releases ownership if the process exits or crashes;
- the metadata file may remain on disk without blocking future acquisition;
- no time-based stale-lock deletion can accidentally evict a healthy server.

The lock file is derived server-side from the SQLite database path and contains only diagnostic metadata such as PID, timestamp and purpose. It is never returned through the HTTP API.

PostgreSQL is unchanged because database-level maintenance coordination must use PostgreSQL-native mechanisms rather than a local filesystem lock.

This lock is a prerequisite for any future destructive SQLite restore activation. Release 20 itself performs no restore and no live database replacement.

## Release 21 — Offline SQLite restore activation

A staged SQLite restore candidate can be activated only through the CLI while the live control plane is offline.

Example:

```bash
production-os restore-activate \
  --database /path/to/production.sqlite \
  --candidate-id <candidate-id> \
  --confirm ACTIVATE_STAGED_RESTORE
```

Activation safety sequence:

1. Revalidate the staged candidate manifest, SHA-256, size, integrity and schema.
2. Acquire the exclusive Release 20 SQLite maintenance lock.
3. Revalidate the candidate after the lock is held.
4. Create a verified rollback backup of the current live database.
5. Copy the candidate to a temporary file beside the live database.
6. Verify the temporary candidate.
7. Remove only the target database WAL/SHM sidecars.
8. Atomically replace the live SQLite file.
9. Verify integrity and schema on the restored live database.
10. If post-replacement verification fails, atomically restore the verified rollback backup.

There is intentionally no HTTP endpoint for restore activation. If the control plane is still running, the CLI fails because it cannot acquire the exclusive database lock.

PostgreSQL restore activation remains unsupported.

## Release 22 — One-shot restore activation

Successful staged SQLite restore candidates are now one-shot.

After the restored live database passes integrity and schema verification:

- the candidate manifest is atomically marked `activation_state=activated`;
- `activated_at` and the verified rollback backup id are persisted;
- a separate activation receipt is written with only structured safe metadata;
- any later attempt to activate the same candidate is rejected before database mutation.

If activation fails and the previous live database is restored successfully, the candidate remains staged and may be retried.

Activation receipts contain only:

```text
candidate_id
source_backup_id
rollback_backup_id
activated_at
schema_version
sha256
```

No credentials, paths, DSNs, authorization headers or arbitrary request payloads are stored.

## Release 23 — Restore activation history

The existing backups dashboard now exposes successful offline restore activations as read-only history.

History is derived only from Release 22 activation receipts and contains:

```text
candidate_id
source_backup_id
rollback_backup_id
activated_at
schema_version
sha256
```

Malformed receipts are ignored. No paths, DSNs, credentials, tokens or arbitrary payloads are exposed.

This is visibility only. Restore activation remains unavailable over HTTP and continues to require the offline CLI path, exact confirmation and exclusive maintenance lock.

## Release 24 — Backup storage inventory

The backups dashboard now measures backup and restore storage growth without deleting anything.

For configured SQLite backup storage it exposes aggregate counts and bytes for:

```text
verified backups
staged restore candidates
activation receipts
temporary files
unknown files
```

Only aggregate metrics are returned. Individual file names and server paths are not exposed.

This release is read-only: there is no cleanup action, retention mutation or restore behavior change.

## Release 25 — Safe backup temp cleanup

Operators can now remove only stale temporary files from configured SQLite backup storage.

A file is eligible only when it is already classified as temporary and is at least 24 hours old. Cleanup requires:

- operator authorization;
- the exact confirmation phrase `PRUNE_STALE_BACKUP_TEMPS`;
- the expected stale-candidate count, rechecked immediately before deletion.

Verified backups, rollback backups, restore candidates, activation receipts, unknown files and fresh temporary files are never deleted by this operation.

The response contains only aggregate deleted counts/bytes and the refreshed storage inventory. File names and server paths remain hidden.

## Release 26 — Backup filesystem capacity

The backups dashboard now reports the capacity of the filesystem that stores SQLite backup artifacts.

It exposes total, free, available and used bytes, plus used/available percentages. When the configured backup directory does not exist yet, Production-OS measures the nearest existing parent without creating the directory.

Capacity status is informational only:

```text
ok       available >= 10%
warning  available < 10%
critical available < 5%
unknown  measurement unavailable
```

No automatic cleanup, backup, restore or control action is triggered from this status. Server paths remain hidden.


## Release 27 — Verified backup age observability

The backups dashboard now reports the age distribution of verified SQLite backup manifests without deleting or reclassifying any backup.

The read-only summary includes:

```text
verified_count
valid_timestamp_count
invalid_timestamp_count
newest_created_at
oldest_created_at
under_24h
one_to_seven_days
seven_to_thirty_days
over_thirty_days
```

Only manifests already marked `verified=true` participate in the age summary. Invalid timestamps are counted explicitly instead of being coerced into an age bucket.

This release is observational only. It introduces no retention policy, no automatic deletion, no cleanup of verified backups, and no path exposure. The age distribution is intended to provide evidence for a later guarded retention design.


## Release 28 — Backup retention preview

Production-OS now computes a read-only preview of which verified SQLite backups could become eligible for a future retention cleanup.

The preview currently uses conservative defaults:

```text
retention_days = 30
min_keep_latest = 3
```

A verified backup is never considered a retention candidate when it is:

- among the newest three verified backups;
- referenced as a source or rollback backup by restore activation history;
- newer than the retention threshold;
- associated with an invalid creation timestamp.

The dashboard exposes only aggregate counts and bytes:

```text
candidate_count
candidate_bytes
protected_count
protected_reasons
```

No backup identifiers, file names or server paths are exposed through this preview.

This release is strictly observational. It does not delete or archive backups, change restore behavior, or enable automatic retention. Any future destructive retention action must be implemented separately with explicit operator confirmation and fresh-state race protection.


## Release 29 — Guarded verified-backup retention cleanup

Operators can now explicitly remove only verified SQLite backups that are currently classified as retention candidates.

The cleanup endpoint is:

```text
POST /v1/dashboard/backups/prune-expired
```

It requires all of:

```text
confirm = PRUNE_EXPIRED_VERIFIED_BACKUPS
expected_candidate_count
expected_candidate_fingerprint
```

The fingerprint is an opaque SHA-256 digest of the current candidate set. Production-OS recomputes the retention state immediately before deletion and rejects the request if either the candidate count or fingerprint changed.

Backups remain protected when they are:

- among the newest three verified backups;
- newer than 30 days;
- referenced by restore activation history as a source or rollback backup;
- associated with an invalid creation timestamp.

Only the server-derived `<backup_id>.sqlite` and `<backup_id>.json` artifacts for the current candidate set can be removed. Clients never provide file names or paths.

Every accepted or conflicted cleanup request is recorded in the control audit. Cleanup is never triggered automatically by capacity warnings, dashboard polling, health checks or retention previews.


## Release 30 — Backup filesystem capacity incidents

Backup filesystem pressure now participates in operational health and durable incident reconciliation.

When configured SQLite backup storage reports:

```text
available < 10%  -> warning / medium incident
available < 5%   -> critical / high incident
```

Production-OS emits the durable incident code:

```text
backup_filesystem_capacity
```

The incident targets the backup-storage surface and is automatically resolved when filesystem capacity returns to `ok`.

This remains observational only. Capacity incidents never trigger retention cleanup, temp cleanup, backup creation, restore staging, restore activation, pause, retry, cancellation or any other control action automatically.


## Release 31 — One-tap Production

The mobile dashboard now treats production launch as the primary action.

The main path is intentionally reduced to:

```text
Repository
Instruction
Lancer la production
```

The browser no longer constructs a raw workflow or chooses execution parameters. It sends only the repository and instruction to:

```text
POST /v1/dashboard/launch
```

The control plane then creates a persistent Managed Project with server-owned defaults:

```text
token_budget = 30000
agent_preference = auto
```

The managed project is persisted before dispatch and remains available if the browser closes or refreshes. If no worker is currently online, the production remains queued instead of being lost.

Advanced token-budget and agent controls remain available in the Managed Projects view but are collapsed by default. The primary mobile surface exposes no per-run technical tuning.

The one-tap endpoint requires the operator role. Viewer and worker credentials cannot launch production.


## Release 32 — One-tap production E2E qualification

The primary mobile launch path is now covered by a dedicated end-to-end qualification test.

The test proves the complete server-side lifecycle:

```text
POST /v1/dashboard/launch
        ↓
persistent Managed Project
        ↓
workflow + queued job
        ↓
remote worker claim / ack / complete
        ↓
workflow succeeded
        ↓
Managed Project REVIEW_REQUIRED
        ↓
control-plane restart
        ↓
same project/workflow/result restored
```

The qualification verifies that repository, instruction, final goal, server-owned execution defaults, worker result usage, workflow identity, generation history and review state survive a control-plane restart.

This specifically protects the mobile promise introduced in Release 31: closing or reloading the dashboard does not own the execution lifetime and cannot discard the production.


## Release 33 — Automatic expired-claim recovery

Worker claim recovery is now part of the normal worker pull path.

Before selecting the next queued job, `POST /v1/jobs/claim` first requeues expired, unacknowledged claims that are still below the delivery-attempt limit. This allows another healthy worker to continue the same persistent workflow without requiring an operator to press `recover-stuck`.

Safety remains bounded:

- only jobs still in `claimed` state are automatically recovered;
- the claim deadline must have expired;
- acknowledged/running jobs are not silently duplicated;
- delivery attempts continue to increment;
- jobs reaching the configured attempt ceiling move to dead-letter instead of looping forever;
- the original Managed Project and workflow identity are preserved.

A dedicated E2E test starts from the One-tap launch endpoint, lets one worker claim and disappear before ACK, then proves a second worker automatically reclaims the same job, completes it, and advances the same generation-1 Managed Project to `REVIEW_REQUIRED`.


## Release 34 — Safe recovery after ACK

Production-OS now has a guarded recovery path for jobs whose worker disappears after ACK and during execution.

Automatic recovery requires two independent stale signals:

- the owning worker heartbeat is older than the busy-worker timeout;
- the running execution telemetry is older than the running-execution timeout.

Only when both are stale is the old worker fenced and the same job returned to the queue. The previous execution attempt is closed as `worker_abandoned`, while the Managed Project, workflow and generation remain unchanged.

This avoids recovering a job merely because a worker is slow or temporarily delayed while still reporting fresh execution telemetry.

A dedicated One-tap E2E test proves both sides of the contract:

1. stale worker heartbeat + fresh telemetry does **not** recover the job;
2. stale heartbeat + stale execution telemetry allows a second worker to reclaim the same job and complete the same generation safely.


## Release 35 — Control-plane restart reconciliation

The One-tap execution path is now qualified across a real control-plane restart.

Two end-to-end scenarios are covered:

1. **Active worker reconnects after restart**
   - the ACKed job, running execution, Managed Project and workflow remain persisted;
   - the worker reconnects, resumes heartbeat/telemetry, and completes the same attempt;
   - no duplicate execution is created.

2. **Worker is abandoned across restart**
   - the persisted job remains ACKed after the server comes back;
   - if both worker heartbeat and execution telemetry are stale, a healthy worker safely reclaims the same job;
   - the old attempt is recorded as `worker_abandoned`;
   - project id, workflow id and generation remain unchanged.

This verifies that restarting the Control Plane itself does not own or reset the production lifecycle.


## Release 36 — Worker session reconciliation

Production-OS now supports explicit worker-session reconciliation after a worker process restart.

`POST /v1/workers/register` accepts an optional `active_job_keys` list. When supplied, the list is treated as the authoritative set of jobs still held by the restarted worker process.

For that explicit reconciliation path:

- persisted `claimed` or `acked` jobs owned by the worker but absent from `active_job_keys` are fenced and recovered;
- ACKed executions that disappeared with the old worker process are closed as `worker_restarted`;
- the worker's persisted `active_tasks` count is reset to the number of reported active jobs;
- retained active jobs are not duplicated;
- recovered jobs preserve their job key, Managed Project, workflow and generation;
- delivery attempts remain monotonic and still respect the dead-letter ceiling.

The field is optional for backwards compatibility. Existing registration calls that do not report `active_job_keys` retain their previous behavior.

A dedicated E2E test covers simultaneous Control Plane + worker restart with two One-tap projects. The restarted worker reports an empty active set, its lost ACKed job is immediately recovered, and two workers then finish both projects without creating new workflows.


## Release 37 — “À faire maintenant”

The mobile dashboard now opens on an attention-first operational view instead of a broad status overview.

The server exposes a single aggregated feed:

```text
GET /v1/dashboard/attention
```

It prioritizes:

- active operational incidents;
- Managed Projects in `NEEDS_ATTENTION`;
- failed managed workflow validation / CI state;
- Managed Projects in `REVIEW_REQUIRED`;
- queued jobs blocked by missing workers, capabilities, controls or capacity;
- recently completed Managed Projects as informational context.

The response includes a compact summary with counts for actions required, incidents, projects to review, projects needing attention, blocked jobs and recently completed projects.

The mobile UI renders this as the default `À faire` view. Each actionable card links back into the existing Managed Projects, Autopilot or Overview surfaces rather than duplicating control logic.

The One-tap launch card remains above navigation, so the two primary mobile actions are now:

```text
Launch a production
or
Handle what needs attention
```


## Release 38 — Contextual attention actions

The `À faire maintenant` surface is now actionable without forcing the operator through intermediate screens.

Attention items can expose state-safe contextual actions:

- `REVIEW_REQUIRED` Managed Projects: **Retest** or **Mark DONE**;
- `NEEDS_ATTENTION` / failed validation Managed Projects: **Retest**;
- open incidents: **Acknowledge**;
- incidents with an available remediation playbook: the same guarded worker control action already exposed by the incident view.

The feed remains read-only for viewer credentials. Mutation endpoints still require the operator role, so action metadata does not widen authorization.

Opening an attention item now deep-links to the exact Managed Project or Autopilot job through a persisted `target` navigation parameter. The matching card is highlighted and scrolled into view.

To keep the mobile surface usable during queue pressure, the feed shows at most eight individual blocked-job cards while preserving the real blocked-job and action-required totals in the summary.

All contextual mutations reuse existing server contracts and confirmations. In particular, marking a project complete still requires the exact `MARK_PROJECT_DONE` confirmation, and incident remediation still uses the server-backed playbook validation/audit path.

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
- [x] internal append-only transparency hash-chain anchoring
- [x] signed external transparency checkpoints
- [x] generic HTTP witness publication
- [ ] provider-specific transparency service integration

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
- [x] strict dual-sign migration from P15 HMAC to P16 Ed25519
- [x] key validity windows and revocation metadata
- [x] SLSA/in-toto compatible statement envelope
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

### Key rotation and revocation

The Ed25519 validator trust registry supports multiple simultaneous keys per validator.

Example:

    {
      "validator-1": [
        {
          "public_key": "<old PEM>",
          "not_after": "2026-10-01T00:00:00+00:00"
        },
        {
          "public_key": "<new PEM>",
          "not_before": "2026-09-15T00:00:00+00:00"
        }
      ]
    }

Each key is addressed by the SHA-256 key ID already embedded in the Ed25519 signature envelope.

Optional policy fields:

    key_id
    not_before
    not_after
    revoked_at

If key_id is supplied in configuration, it must exactly match the public key fingerprint.

Verification resolves the exact signing key from:

    validator_id + signature.key_id

and evaluates the key policy at the attestation's signed issued_at timestamp.

This permits overlap during planned rotation while preventing an expired or revoked key from signing new accepted validation evidence.

Legacy shorthand remains valid:

    {
      "validator-1": "<PEM public key>"
    }

The registry therefore supports staged migration without invalidating existing configuration.

### SLSA / in-toto provenance

Every Ed25519-promoted release now carries a signed supply-chain statement using:

    _type = https://in-toto.io/Statement/v1
    predicateType = https://slsa.dev/provenance/v1

The statement subject binds the released artifact name and SHA-256 digest.

The build definition records:

    repository
    workflow_id
    workflow_generation
    source revision as a resolved dependency

Run details bind the Production-OS builder and the immutable release provenance through byproducts containing:

    release_id
    provenance schema
    provenance signing key ID
    approval key
    validator ID

The statement is independently signed with the release Ed25519 private key and its canonical SHA-256 digest is stored beside the release.

Release verification checks both:

    Production-OS release provenance signature
    SLSA/in-toto statement signature + artifact digest

Offline verification:

    production-os slsa-verify \
      --statement signed-slsa.json \
      --public-key release-public.pem \
      --artifact-sha256 <64-char-sha256>

This does not require access to the Production-OS database or control plane.

### Append-only transparency log

Every promoted release is now atomically appended to the Production-OS transparency log in the same database transaction as release creation.

Each entry contains:

    sequence
    release_id
    release_provenance_sha256
    slsa_statement_sha256
    previous_hash
    created_at
    entry_hash

The first entry is linked to a 64-zero genesis hash. Every later entry commits to the previous entry hash.

This provides deletion, insertion, reordering and mutation detection for the local release history.

Release verification now checks:

    cryptographic validation attestation
    release provenance
    SLSA statement
    transparency-chain integrity
    release inclusion
    release provenance digest

The verification result includes:

    transparency_sequence
    transparency_entry_hash
    transparency_root_hash

Audit endpoint:

    GET /v1/transparency

It returns the ordered append-only entries and current chain verification/root hash.

The internal chain is intentionally separate from the remaining external anchoring milestone. A database administrator who can rewrite the complete database could still replace the entire local history and recompute the chain. The next stage therefore publishes periodic roots to an independent external transparency service or immutable witness.

### External transparency witness

Production-OS can now export the current append-only transparency root as an independently signed checkpoint.

Create a checkpoint:

    production-os transparency-checkpoint \
      --database artifacts/production.db \
      --private-key witness-private.pem \
      --output checkpoint.json

The signed checkpoint commits to:

    schema version
    transparency root hash
    number of entries
    checkpoint timestamp

It is signed with Ed25519 and can be archived outside the Production-OS database.

Offline verification:

    production-os transparency-checkpoint-verify \
      --checkpoint checkpoint.json \
      --public-key witness-public.pem \
      --root-hash <expected-root>

A checkpoint may also be published to an independent HTTP witness:

    production-os transparency-checkpoint \
      --database artifacts/production.db \
      --private-key witness-private.pem \
      --publish-url https://witness.example/checkpoints \
      --bearer-token-env WITNESS_TOKEN

The HTTP body is the complete signed checkpoint envelope.

This closes the local-only trust gap when the receiving witness stores checkpoints independently. A later full database rewrite can then be detected by comparing its recomputed root against a previously published checkpoint.

The generic witness protocol deliberately avoids coupling Production-OS to one provider. Provider-specific Rekor or equivalent transparency integrations remain a separate milestone.

### Dual-sign migration

Production-OS now supports a strict migration bundle containing both legacy HMAC-SHA256 and Ed25519 validation attestations for the same validation decision.

Schema:

    production-os/validation-attestation-bundle/v1

A dual-sign bundle is accepted only when both signatures independently verify against their configured trust stores.

The two attestations must bind the same:

    validator identity
    workflow
    artifact
    artifact SHA-256
    source revision
    workflow generation
    validation result

The ReleaseLedger uses the verified Ed25519 attestation as the canonical input for v2 release provenance and SLSA generation, while retaining the complete dual-sign bundle in immutable release metadata.

Post-release verification repeats both validation checks and reports:

    signature_scheme = hmac-sha256+ed25519

This provides an explicit migration period where existing P15 HMAC validators and P16 public-key infrastructure must agree before a release can be promoted.

Once all validators and auditors have migrated, deployments can stop producing dual-sign bundles and use pure v2 Ed25519 attestations without changing the release provenance format.

### Cryptographic migration policy

Deployments can now explicitly control which validation signature generation is accepted:

    PRODUCTION_OS_VALIDATION_SIGNATURE_POLICY=compatible
    PRODUCTION_OS_VALIDATION_SIGNATURE_POLICY=dual-required
    PRODUCTION_OS_VALIDATION_SIGNATURE_POLICY=ed25519-only

Modes:

    compatible
        Accept legacy HMAC, strict dual-sign, and pure Ed25519.

    dual-required
        Reject legacy HMAC and pure Ed25519.
        Both HMAC and Ed25519 must independently verify.

    ed25519-only
        Reject HMAC and dual-sign bundles.
        Only validation-attestation/v2 is accepted.

Recommended staged migration:

    Stage 1  compatible
    Stage 2  dual-required
    Stage 3  ed25519-only

This turns HMAC retirement into an enforceable deployment policy rather than an operational convention. Historical releases remain verifiable with the cryptographic material required by their original signature scheme.

### Trusted builder identities

SLSA verification can now enforce builder identity independently from the artifact and release signature.

A builder trust policy binds:

    builder ID
    signing key owner
    signing key ID
    repository allowlist
    builder validity window
    signing-key validity / revocation policy

Example policy:

    builders = {
      "https://builder.example/prod": {
        "key_owner": "prod-builder",
        "allowed_repositories": ["owner/repo"]
      }
    }

    signing_keys = {
      "prod-builder": {
        "public_key": "<PEM>",
        "not_before": "2026-09-01T00:00:00+00:00",
        "not_after": "2027-09-01T00:00:00+00:00"
      }
    }

Trusted SLSA verification resolves the public key from the builder identity and signature key ID, then checks repository authorization before accepting the statement.

This prevents a cryptographically valid builder key from being reused to attest an unauthorized repository.

Signed SLSA envelopes now also carry the statement signing timestamp, allowing builder/key validity policy to be evaluated at signing time.

### Production builder enforcement

Trusted builder identity can now be made mandatory in the ReleaseLedger and control plane.

Configuration:

    PRODUCTION_OS_BUILDER_ID=https://builder.example/prod
    PRODUCTION_OS_TRUSTED_BUILDERS=<JSON>
    PRODUCTION_OS_TRUSTED_BUILDER_KEYS=<JSON>
    PRODUCTION_OS_REQUIRE_TRUSTED_BUILDER=true

When enforcement is enabled, release verification fails unless the SLSA statement:

    has a trusted builder ID
    is signed by a key assigned to that builder
    uses a currently valid/non-revoked key
    targets a repository authorized for that builder
    retains a valid artifact SHA-256 binding

The builder ID used during SLSA statement creation is configurable rather than hard-coded.

Recommended production configuration combines:

    PRODUCTION_OS_VALIDATION_SIGNATURE_POLICY=ed25519-only
    PRODUCTION_OS_REQUIRE_TRUSTED_BUILDER=true

This makes public-key validator identity and repository-scoped builder identity mandatory for newly verified production releases.

### Builder / provenance key separation

Production deployments can now use distinct Ed25519 keys for two separate trust domains:

    PRODUCTION_OS_RELEASE_PROVENANCE_PRIVATE_KEY
        signs the immutable Production-OS release provenance

    PRODUCTION_OS_BUILDER_PRIVATE_KEY
        signs the SLSA/in-toto builder statement

When trusted builder enforcement is enabled, a dedicated builder private key is mandatory. Production-OS no longer falls back to the release provenance key for SLSA signing in that mode.

Recommended production topology:

    validator key
        validation identity only

    builder key
        SLSA build identity only

    release provenance key
        ReleaseLedger provenance only

    witness key
        external transparency checkpoint only

This reduces cross-domain key reuse and limits the blast radius of a compromised signing credential.

Legacy/non-strict deployments retain the previous provenance-key fallback for compatibility.

### Key-purpose invariant

Strict trusted-builder deployments now enforce key-purpose separation by fingerprint.

Production-OS computes the Ed25519 key ID for configured validator, builder and release-provenance credentials and rejects startup/configuration when the same key appears in multiple trust domains.

Rejected examples:

    validator key == builder key
    builder key == release provenance key
    validator key == release provenance key

The comparison uses the public-key SHA-256 fingerprint, so re-encoding the same underlying private/public key does not bypass the invariant.

This converts key separation from a deployment recommendation into an enforced cryptographic property whenever trusted builder enforcement is enabled.

### Unified trust policy

Cryptographic domain separation is now centralized in TrustPolicy.

The policy covers four independent signing authorities:

    validator
    builder
    release provenance
    transparency witness

With strict key domains enabled, the same Ed25519 fingerprint cannot appear in more than one authority.

    PRODUCTION_OS_STRICT_KEY_DOMAINS=true

Witness checkpoint creation validates this policy before signing, preventing a witness credential from reusing a configured builder, validator or release-provenance key.

ReleaseLedger uses the same centralized policy for validator/builder/provenance separation.

This removes duplicated domain-separation logic and establishes one reusable trust-policy boundary for future KMS/HSM and external transparency integrations.

### Pluggable signing boundary

Production-OS now has a Signer interface for operations that require private-key signatures.

Current backend:

    PemSigner
        local Ed25519 PEM compatibility backend

Signer exposes only:

    key_id
    sign(payload)

SLSA builder statements and transparency witness checkpoints can now be signed through this interface instead of requiring direct access to PEM key material.

Strict trusted-builder ReleaseLedger operation uses the Signer boundary for builder signing. Existing PEM configuration is automatically wrapped in PemSigner, preserving deployment compatibility.

This creates the integration boundary required for future:

    cloud KMS
    HSM
    Vault Transit
    PKCS#11
    remote signing services

Those backends can implement Signer without exposing private key bytes to ReleaseLedger or SLSA code.

The local PEM backend remains appropriate for development and migration, while production can progressively move signing authority outside the Production-OS process.

### Signer-backed release provenance

Release provenance v2 signing now supports the same Signer boundary as SLSA builder and witness signing.

The strict cryptographic path is therefore:

    builder statement -> Signer
    release provenance -> Signer
    transparency checkpoint -> Signer

ReleaseLedger accepts a provenance_signer and no longer requires direct private-key access for v2 provenance creation when a signer is supplied.

TrustPolicy can evaluate signer key IDs directly, so domain separation remains enforceable even when the underlying private key is held by a remote KMS/HSM implementation and no PEM material exists in the Production-OS process.

PEM configuration remains supported through automatic PemSigner wrapping.

This completes the core abstraction needed to move builder and release-provenance private keys out of process. Witness already exposes the same signing boundary; the remaining deployment work is adding concrete remote signer providers and configuration/factory support.

### Remote signer factory

Production-OS now includes a fail-closed Signer factory.

Supported signer URIs:

    pem:
        local compatibility backend

    remote+https://host/path
        generic remote Ed25519 signing service

Remote signing requests contain only:

    key_id
    canonical payload object

The configured private key never needs to enter the Production-OS process.

Remote signer responses must contain:

    algorithm = ed25519
    matching key_id
    signature

Algorithm mismatch, key-ID mismatch, malformed JSON, network errors and timeouts fail closed.

Builder configuration:

    PRODUCTION_OS_BUILDER_SIGNER_URI=remote+https://signer.example/sign
    PRODUCTION_OS_BUILDER_SIGNER_KEY_ID=sha256:<fingerprint>
    PRODUCTION_OS_BUILDER_SIGNER_TOKEN=<secret>

The existing PRODUCTION_OS_BUILDER_PRIVATE_KEY remains available for the local PemSigner migration path.

The generic remote backend is intentionally provider-neutral. Future KMS, Vault Transit and PKCS#11 adapters can be registered behind the same factory without changing ReleaseLedger.

### Out-of-process signing for all release authorities

The SignerFactory path now covers builder, release-provenance and transparency-witness signing.

Builder:

    PRODUCTION_OS_BUILDER_SIGNER_URI=remote+https://signer.example/builder
    PRODUCTION_OS_BUILDER_SIGNER_KEY_ID=sha256:<builder>
    PRODUCTION_OS_BUILDER_SIGNER_TOKEN=<secret>

Release provenance:

    PRODUCTION_OS_PROVENANCE_SIGNER_URI=remote+https://signer.example/provenance
    PRODUCTION_OS_PROVENANCE_SIGNER_KEY_ID=sha256:<provenance>
    PRODUCTION_OS_PROVENANCE_SIGNER_TOKEN=<secret>

Witness CLI:

    production-os transparency-checkpoint \
      --database artifacts/production.db \
      --witness-signer-uri remote+https://signer.example/witness \
      --witness-signer-key-id sha256:<witness> \
      --witness-signer-token-env WITNESS_SIGNER_TOKEN

A local --private-key remains supported for witness migration and is wrapped as a PemSigner.

With remote signers configured, the Production-OS control plane no longer needs the builder or release-provenance private key material. Witness checkpoint signing can likewise be performed without loading its private key.

TrustPolicy continues to enforce domain separation from Signer.key_id values.

### Remote signer transport hardening

RemoteHttpSigner now defaults to HTTPS-only operation and fails configuration when a plain HTTP endpoint is supplied.

Transport controls include:

    system or custom CA validation
    optional client certificate + private key for mTLS
    bounded request timeout
    bounded retries
    exponential retry backoff
    circuit breaker after repeated failed signing operations
    automatic circuit reset window

Default retry policy:

    retries = 2
    backoff = 0.25 seconds
    circuit failure threshold = 3
    circuit reset = 30 seconds

All terminal failures remain fail-closed: Production-OS does not create a substitute signature or silently fall back to a local signing key.

Plain HTTP can only be enabled explicitly through the Python signer configuration and is intended for isolated development environments.

Remote response validation still requires Ed25519, the exact configured key ID, and a non-empty signature.

### Vault Transit signer

Production-OS now has a native HashiCorp Vault Transit signing backend behind the existing Signer interface.

Signer URI:

    vault+https://vault.example/keys/<transit-key>

Required configuration:

    key_id
    Vault token

Optional controls:

    Vault namespace
    custom Transit mount
    custom CA
    mTLS client certificate/key
    request timeout

The signer canonicalizes the Production-OS payload, base64-encodes it, and asks Vault Transit to sign with Ed25519. Production-OS never receives the Transit private key.

The returned Vault signature is validated structurally and normalized to the common Signer response while preserving the original provider signature for audit metadata.

Example factory configuration:

    create_signer(
        "vault+https://vault.example/keys/production-builder",
        key_id="sha256:<public-key-fingerprint>",
        vault_token="<token>",
    )

The same backend can be supplied as builder_signer, provenance_signer or witness_signer, while TrustPolicy continues to enforce distinct key IDs between those domains.

### Dynamic Vault authentication

Vault-backed signers no longer require a long-lived static Vault token.

SignerFactory supports three Vault authentication modes:

    token
        existing compatibility mode

    approle
        exchanges role_id + secret_id for a Vault client token

    kubernetes
        exchanges a Kubernetes service-account JWT + Vault role
        for a Vault client token

Both dynamic flows use Vault's HTTPS auth endpoints and fail closed when credentials are missing, the auth method is unknown, Vault is unavailable, or no client token is returned.

Relevant factory options:

    vault_auth_method
    vault_role_id
    vault_secret_id
    vault_kubernetes_role
    vault_kubernetes_jwt
    vault_auth_mount
    vault_namespace

The resulting short-lived Vault token is passed only to VaultTransitSigner and is not exposed through the common Signer interface.

Recommended Kubernetes deployment:

    Pod service account
          ↓
    Kubernetes JWT
          ↓
    Vault Kubernetes auth
          ↓
    short-lived Vault token
          ↓
    Transit Ed25519 signing

This removes the need to provision a permanent Vault token into the Production-OS container.


## Trust incident response

Production-OS can re-evaluate promoted releases against the current validator
and builder trust policy. This is intended for key compromise, emergency
revocation, and supply-chain incident response.

Inspect the current blast radius:

```bash
production-os trust-status --database production.db --key-id sha256:...
```

Generate a machine-readable report without mutating audit history:

```bash
production-os incident-report --database production.db --key-id sha256:...
```

Persist a deduplicated snapshot in the immutable incident ledger:

```bash
production-os incident-snapshot --database production.db --key-id sha256:...
```

`incident-snapshot` exits with 0 for a healthy scope, 2 when a new active
incident state was recorded, and 3 when the active state was already recorded.

The authenticated control plane exposes the same incident surfaces:

```text
GET  /v1/trust-status
GET  /v1/incident-report
GET  /v1/incident-history
GET  /v1/incident-history/verify
POST /v1/incident-snapshot
```

Read endpoints require an authenticated viewer. The snapshot endpoint mutates
the append-only audit ledger and therefore requires the `operator` role.

Incident history entries are SHA-256 hash chained. Rewriting a persisted report
or breaking the previous-hash chain causes verification to fail. Unchanged
snapshots are deduplicated while genuine blast-radius changes append a new
entry.


## Dashboard observability — Release 1

The authenticated workspace remains available at `/dashboard`. Pair the browser
with a viewer or operator credential to read observability data; worker-only
credentials cannot read dashboard routes. The workspace provides **Vue générale**,
**Projets**, **Workers**, and **Activité**, while the existing repository +
instruction launch form remains available.

Project pages distinguish **Production actuelle** from **Projet estimé**. The
first is deterministic workflow progress weighted by task estimates. The second
is a versioned evidence-based estimate and is always accompanied by confidence
and evidence coverage; unavailable evidence stays unknown rather than being
invented.

API cost is an estimate only when an exact provider/model price is known for the
execution date. Token totals remain useful when cost cannot be calculated.
Production-OS-attributed commits are reported separately from total commits on
the repository default branch; the latter comes from GitHub snapshots and may be
marked degraded when cached data is used.

Workers publish live execution telemetry through
`POST /v1/jobs/{job_key}/telemetry`; this endpoint requires the owning worker
credential. Release 1 dashboard observability is read-only: pause, drain,
cancellation, retry and kick controls belong to Release 2.
