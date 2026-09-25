# Release 30 — Backup filesystem capacity incidents

## Goal

Integrate configured SQLite backup filesystem pressure into operational health and durable incident tracking.

## Signals

- warning below 10% available -> medium severity
- critical below 5% available -> high severity
- incident code: backup_filesystem_capacity
- target: backup-storage / primary

## Safety

Observational only. No cleanup or control action is triggered automatically from capacity incidents.

## Completion gate

- full CI green
- Python 3.11 and 3.12 green
- incident lifecycle regression coverage
- final diff/security review clean
