# Release 43 — Safe production cancellation

## Goal

Let the operator stop the current One-tap production directly from the persistent mobile tracker without losing the Managed Project or allowing a cancelled job to be revived by crash recovery.

## Contract

POST /v1/managed-projects/{project_id}/cancel

Required exact confirmation:

CANCEL_ACTIVE_PRODUCTION

Operator role only.

## State semantics

Queued:
- atomically transition queued job to cancelled server-side
- acknowledge persisted cancel control
- mark workflow task cancelled
- Managed Project reconciles to NEEDS_ATTENTION

Claimed / ACKed / running:
- persist cancel_requested
- tracker reports cancelling
- worker acknowledges cancellation through existing heartbeat control protocol
- task/workflow become cancelled
- Managed Project reconciles to NEEDS_ATTENTION

Replay:
- already-cancelled workflow returns cancelled idempotently

## Crash safety

If a worker disappears after cancel_requested:
1. abandoned execution recovery may return the job to queued
2. worker claim polling checks persisted job control before placement
3. queued cancel is finalized atomically
4. replacement worker receives no cancelled job

## Storage parity

Add cancel_queued to SQLiteJobQueue and PostgresJobQueue with equivalent transactional semantics.

## Mobile

The last-production tracker exposes a guarded Annuler la production action for preparing/queued/claimed/running phases and a disabled Annulation en cours state while cooperative cancellation is pending.

## Completion gate

- SQLite queued cancel test
- PostgreSQL parity test when integration DB is available
- API role + exact-confirmation + idempotency tests
- production-status cancelling test
- crash/restart/recovery E2E proving zero re-execution
- UI contract tests
- full CI, Python 3.11/3.12, packaging/Docker/CLI smoke green
