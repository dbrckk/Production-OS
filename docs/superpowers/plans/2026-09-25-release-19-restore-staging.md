# Production-OS Release 19 — Restore Staging

## Goal

Materialize a verified SQLite backup into an isolated server-side restore candidate without mutating the live database.

## Safety

- operator-only
- exact confirmation phrase required
- accepts only server-issued backup_id
- no client filesystem path
- source backup must pass existing restore verification first
- candidate path is server-generated inside PRODUCTION_OS_BACKUP_DIR
- live database file is never opened for write by staging
- live database bytes must remain unchanged
- PostgreSQL staging remains unsupported and reported truthfully
- no automatic activation or live restore in Release 19

## API

POST /v1/dashboard/backups/{backup_id}/stage-restore

Body:
{
  "confirm": "STAGE_VERIFIED_RESTORE"
}

Response:
- candidate_id
- source_backup_id
- backend_kind
- verified
- integrity
- schema_version
- size_bytes
- sha256
- staged_at
- activation_enabled: false

## Qualification

- valid verified backup stages successfully
- tampered source rejected
- malformed backup id rejected
- candidate stays inside configured server directory
- candidate hash/size/integrity verified
- live DB bytes and durable probe remain unchanged
- viewer forbidden
- wrong confirmation produces zero candidate files
- PostgreSQL unsupported honestly
- full CI + Python 3.11/3.12 green before merge


## Implemented in current branch

- server-only SQLite restore candidate staging
- existing backup verification reused before staging
- SQLite backup API used for isolated candidate materialization
- candidate integrity_check and schema version verification
- candidate SHA-256 and size metadata
- atomic candidate finalization inside configured backup directory
- operator-only stage-restore endpoint with exact confirmation phrase
- distinct control audit action for staging success/failure
- mobile backup card action with explicit non-destructive wording
- viewer/wrong-confirmation/tampered-source protections
- live database invariance tests
- Release 19 restart E2E qualification
- README documentation

## Remaining before Release 19 completion

- final CI qualification on complete head
- final diff/security review
- mark PR ready and merge only after green final head
