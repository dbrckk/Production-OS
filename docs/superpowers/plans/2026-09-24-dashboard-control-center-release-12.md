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


## Implemented in current branch

- read-only storage maintenance snapshot engine
- SQLite database size including WAL/SHM without exposing filesystem paths
- PostgreSQL pg_database_size support without exposing DSN
- durable table row counts and valid/invalid timestamp accounting
- configurable retention windows with safe defaults
- exact retention candidate counts from parsed timestamps
- viewer-readable /v1/dashboard/maintenance
- worker role remains forbidden by dashboard authorization
- Overview Storage & retention card with independent degraded mode
- deterministic SQLite/API/UI tests
- PostgreSQL parity contract
- README documentation

## Remaining before Release 12 completion

- final CI qualification on the complete head
- final diff/security review
- mark PR ready and merge only after green final head
