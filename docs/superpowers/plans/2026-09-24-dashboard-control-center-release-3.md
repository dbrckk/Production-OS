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
