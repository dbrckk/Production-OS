# Dashboard Control Center Release 15 — Restore Readiness

## Goal

Verify that a server-side backup is genuinely restorable before any destructive restore operation is enabled.

## Safety principles

- Release 15 performs no live database restore.
- Only server-issued backup_id values are accepted.
- No client-supplied filesystem path.
- Backup file and manifest paths are derived server-side from PRODUCTION_OS_BACKUP_DIR.
- Exact manifest size and SHA-256 must match current file bytes.
- SQLite integrity_check must equal ok.
- schema_meta must be readable and schema_version reported.
- Backup verification is operator-only.
- Viewer may read catalog verification metadata but cannot trigger verification.
- No database path, backup path, DSN, token, password or secret in API/UI.
- PostgreSQL restore remains unsupported.
- Verification is audit logged.

## API

POST /v1/dashboard/backups/{backup_id}/verify
Body:
{
  "confirm": "VERIFY_BACKUP_FOR_RESTORE"
}

Response:
- backup_id
- backend_kind
- verified
- restorable
- size_bytes
- sha256
- schema_version
- integrity
- checked_at
- restore_enabled: false

## Server behavior

1. Validate backup_id format.
2. Resolve manifest/file only inside configured backup directory.
3. Require safe verified manifest.
4. Recompute file size + SHA-256.
5. Open SQLite backup read-only.
6. PRAGMA integrity_check.
7. Read schema_meta schema_version.
8. Return readiness metadata.
9. Never write to live DB or backup DB.

## UI

Backup card:
- Verify restore readiness button for each verified SQLite backup.
- Explicit browser confirmation.
- Display last verification result.
- Keep restore disabled.

## Qualification

- tampered file rejected
- tampered manifest rejected
- malformed/traversal backup_id rejected
- missing file rejected
- integrity failure rejected
- valid backup reports schema version
- live database remains unchanged
- viewer cannot trigger verification
- operator exact confirmation required
- PostgreSQL remains unsupported
- full CI + Python 3.11/3.12 green before merge


## Implemented in current branch

- strict server-issued backup_id validation
- server-side manifest/file resolution from PRODUCTION_OS_BACKUP_DIR
- exact size and SHA-256 revalidation
- SQLite read-only open
- PRAGMA integrity_check
- schema_meta schema_version verification
- live database remains unchanged during verification
- operator-only verification with exact confirmation
- backup-verify audit trail
- tampered file/manifest, traversal id and missing-file rejection
- mobile restore-readiness verification UI
- no destructive restore action exposed
- README documentation and engine/API/UI regression coverage

## Remaining before Release 15 completion

- final CI qualification on the complete head
- final diff/security review
- mark PR ready and merge only after green final head
