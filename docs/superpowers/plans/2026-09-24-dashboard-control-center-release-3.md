# Dashboard Control Center Release 3 — Operational Reliability

## Goal

Harden Production-OS for day-to-day operation after Release 2 by making control actions auditable, failures diagnosable, and recovery explicit.

## Release 3 — Slice 1: durable operator control audit

### Requirements

- Every operator control action is recorded durably.
- Audit records contain:
  - action
  - worker_id
  - optional job_key
  - requested_by
  - requested_at
  - outcome
  - optional error_code
- Never persist bearer tokens, GitHub tokens, request headers, or raw credentials.
- A failed action must also be auditable.
- Audit writes must not silently convert a failed action into success.
- Viewer/operator dashboard reads may inspect audit history; worker role may not.
- Audit history is bounded and ordered newest-first.
- SQLite and PostgreSQL remain behaviorally equivalent.

### Planned files

- Modify: src/production_os/sqlite_backend.py
- Modify: src/production_os/postgres_backend.py
- Modify: src/production_os/dashboard_store.py
- Modify: src/production_os/control_plane.py
- Modify: src/production_os/dashboard_service.py
- Modify: src/production_os/dashboard_ui.py
- Add: tests/test_dashboard_control_audit.py

## Later slices

- control-plane health / degraded-state diagnostics
- safe recovery actions for stuck jobs
- alert acknowledgement / incident history
- release qualification and mobile polish


## Implemented in current branch

- durable SQLite/PostgreSQL control audit table
- operator control audit for success/fallback/failure outcomes
- viewer-readable / worker-forbidden control audit API
- Activity UI control-audit panel
- deterministic operational health derivation
- dashboard health endpoint and overview rendering
- targeted expired-claim recovery in SQLite/PostgreSQL
- audited `recover-stuck` operator action
- worker detail exposes only truly recoverable expired claims
- UI recovery button is shown only for server-confirmed recoverable jobs

## Remaining before Release 3 completion

- complete CI qualification on both Python compatibility jobs and full test suite
- add README operational notes for audit/health/recovery
- add restart/E2E qualification covering audit persistence and recover-stuck
- final security review for audit payloads and role boundaries
- final UI/mobile regression check
