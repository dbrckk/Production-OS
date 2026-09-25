# Production-OS Release 23 — Restore Activation History

## Goal

Expose successful offline restore activations as read-only operational history in the existing backups dashboard surface.

## Safety

- Read-only visibility only.
- No HTTP activation endpoint.
- Activation continues to require the offline CLI path and Release 20 exclusive lock.
- History is derived only from Release 22 activation receipt files.
- Receipt parsing whitelists safe structured fields.
- Malformed receipts are ignored, not surfaced as trusted history.
- PostgreSQL remains unsupported for restore activation and returns no activation history.
- No credentials, paths, DSNs or arbitrary payloads are exposed.

## API/UI

- /v1/dashboard/backups adds activations[]
- each activation contains:
  - candidate_id
  - source_backup_id
  - rollback_backup_id
  - activated_at
  - schema_version
  - sha256
- newest activations first
- mobile overview renders recent activation history

## Qualification

- valid receipts listed newest-first
- malformed/tampered shape ignored
- unconfigured directory returns empty history
- Postgres returns empty history
- no HTTP activation route added
- full CI + Python 3.11/3.12 green before merge


## Implemented in current branch

- strict safe activation receipt parser
- viewer-readable activations[] in existing backups API
- malformed receipts ignored
- PostgreSQL/unconfigured history remains empty
- mobile backup card renders recent restore activations
- no HTTP activation route added
- unit/API/UI regression coverage
- README documentation

## Remaining before Release 23 completion

- final CI qualification on complete head
- final diff/security review
- mark PR ready and merge only after green final head
