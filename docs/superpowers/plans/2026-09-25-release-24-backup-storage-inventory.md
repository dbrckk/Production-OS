# Production-OS Release 24 — Backup Storage Inventory

## Goal

Measure backup/restore storage growth safely before introducing any cleanup action.

## Principles

- Read-only inventory only.
- No file deletion.
- No retention action.
- No restore activation changes.
- No paths exposed to the browser.
- Malformed/unrecognized files are counted as unknown, not trusted.
- PostgreSQL reports unsupported backup storage inventory truthfully.

## Metrics

For configured SQLite backup storage:
- total_size_bytes
- backup_count
- backup_bytes
- restore_candidate_count
- restore_candidate_bytes
- activation_receipt_count
- activation_receipt_bytes
- temp_file_count
- temp_file_bytes
- unknown_file_count
- unknown_file_bytes

## API/UI

- Existing /v1/dashboard/backups adds storage{}
- Mobile backup card renders size and counts
- No cleanup button in this release

## Qualification

- deterministic file classification
- no server paths in response
- missing directory returns zero inventory
- malformed files counted unknown
- Postgres returns unsupported/empty inventory
- no deletion or mutation
- full CI + Python 3.11/3.12 green before merge
