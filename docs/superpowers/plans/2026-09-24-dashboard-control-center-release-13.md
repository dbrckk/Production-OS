# Dashboard Control Center Release 13 — Safe Retention Cleanup

## Goal

Allow operators to prune expired historical data safely, using the read-only retention diagnostics introduced in Release 12.

## Safety principles

- Operator-only.
- No automatic cleanup.
- No cleanup from analytics, alerts, incidents or health polling.
- Exact confirmation phrase required.
- Fresh retention snapshot recomputed immediately before deletion.
- Client must provide expected prunable candidate count; mismatch returns conflict and deletes nothing.
- Only rows with valid parsed timestamps older than the configured cutoff are eligible.
- Invalid timestamps are never deleted.
- Active/running executions are never deleted.
- Incidents and remediation history are protected in Release 13.
- Worker/job/workflow/control desired-state tables are never touched.
- No VACUUM in the request path.
- Every cleanup is recorded in the generic control audit.

## Prunable tables

Deletion order:
1. api_usage_events
2. worker_log_events
3. terminal job_executions
4. control_audit_events (excluding the current cleanup audit row)
5. project_repository_snapshots
6. project_progress_snapshots
7. generic events

Protected:
- dashboard_incidents
- dashboard_remediation_events
- workflows / workflow_tasks
- jobs
- workers / worker_control_state / job_control_state
- releases / trust history

## API

POST /v1/dashboard/maintenance/prune

Body:
{
  "confirm": "PRUNE_EXPIRED_HISTORY",
  "expected_candidate_rows": <int>
}

Response includes:
- deleted_rows total
- per-table deleted counts
- protected_candidate_rows
- maintenance snapshot after cleanup

Conflict if expected count no longer matches the fresh prunable count.

## UI

Storage card exposes:
- prunable candidate rows
- protected candidate rows
- operator button only when prunable > 0
- explicit browser confirmation before POST
- result receipt after cleanup

## Qualification

- dry safety: wrong phrase / viewer / stale expected count => zero deletion
- invalid timestamps survive
- recent rows survive
- running executions survive
- terminal old executions can be pruned
- protected incident/remediation rows survive
- SQLite/PostgreSQL parity
- audit row created
- full CI + Python 3.11/3.12 green before merge
