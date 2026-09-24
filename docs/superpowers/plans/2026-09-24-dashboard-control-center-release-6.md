# Dashboard Control Center Release 6 — Remediation History

## Goal

Make incident remediation actions durably traceable from recommendation to operator request and final control outcome.

## Principles

- Remediation history is separate from the generic control audit.
- Every incident-linked remediation records incident_id, action, target, actor, outcome and timestamps.
- The server re-validates the current incident playbook before accepting an incident-linked remediation.
- A browser cannot attach an arbitrary incident_id to an unrelated control action.
- No secrets, credentials, request headers or tokens are persisted.
- Existing direct operator controls remain supported without an incident_id.
- Playbook generation remains read-only and deterministic.

## Slice 1 — durable remediation ledger

- Schema v12 SQLite/PostgreSQL parity.
- New dashboard_remediation_events table.
- Append/update/list store APIs.
- Restart persistence tests.

## Slice 2 — server-verified incident linkage

- Worker control endpoint accepts optional incident_id.
- If incident_id is supplied, current playbook must contain the exact action + worker_id + job_key as available/fallback.
- Invalid/stale linkage returns conflict and performs no control mutation.
- Record requested, accepted/dispatched/fallback/failed outcome.
- Preserve the existing control_audit_events entry.

## Slice 3 — history API and dashboard

- Viewer-readable remediation history.
- Worker role forbidden by existing dashboard authorization.
- Show incident, action, target, actor, outcome, timestamp.
- Incident playbook buttons send incident_id automatically.
- Mobile-safe rendering and regression coverage.

## Qualification

- SQLite/PostgreSQL parity.
- Direct controls still work without incident_id.
- Invalid incident/action linkage cannot mutate control state.
- Restart persistence.
- No secrets in ledger payloads.
- Python 3.11/3.12 and full CI green before merge.


## Implemented in current branch

- schema v12 SQLite/PostgreSQL remediation ledger
- durable append/update/list remediation store APIs
- restart persistence and secret-shape tests
- optional incident_id on existing worker control requests
- server re-validation of exact playbook action + worker + job + availability
- stale/forged incident remediation rejected before audit/control mutation
- remediation outcome finalized alongside control audit outcome
- viewer-readable remediation history API
- worker role remains forbidden from dashboard history
- incident-filtered history queries
- dashboard playbook buttons transmit incident_id
- Activity view renders remediation lineage
- direct controls remain backward compatible without incident_id
- README documentation and UI/API regression coverage

## Remaining before Release 6 completion

- final CI qualification on the complete head
- final diff/security review
- mark PR ready and merge only after green final head
