# Dashboard Control Center Release 12 — Storage Maintenance

## Goal

Expose durable storage health and retention pressure before introducing any destructive cleanup.

## Principles

- Read-only in Release 12.
- No row deletion, VACUUM, backup mutation or restore action.
- SQLite and PostgreSQL parity.
- No database path, DSN, token, credential or secret returned to the browser.
- Counts and retention candidates come from durable server data only.
- Retention windows are explicit and configurable.

## Default retention windows

- worker logs: 30 days
- API usage events: 90 days
- execution history: 90 days
- control audit: 180 days
- remediation history: 180 days
- repository/progress snapshots: 90 days
- generic event stream: 90 days

Incidents are not considered independently pruneable while remediation history references them.

## API / UI

GET /v1/dashboard/maintenance

Returns:
- backend kind
- database size bytes when measurable
- table row counts
- oldest/newest timestamps where applicable
- configured retention days
- candidate row count older than cutoff
- total candidate rows
- maintenance status: healthy | attention | unknown

Dashboard Overview renders a compact Storage maintenance card.

## Qualification

- SQLite deterministic tests
- PostgreSQL size/count parity contract
- no secrets or filesystem path exposed
- invalid/missing timestamps do not invent candidate counts
- viewer-readable, worker forbidden through dashboard authorization
- full CI + Python 3.11/3.12 green before merge
