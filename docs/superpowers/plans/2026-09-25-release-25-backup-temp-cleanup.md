# Production-OS Release 25 — Safe Backup Temp Cleanup

## Goal

Allow operators to remove only stale temporary files from configured SQLite backup storage.

## Safety

- Only files already classified as temporary may be deleted.
- Verified backups are never deleted.
- Restore candidates are never deleted.
- Activation receipts are never deleted.
- Unknown files are never deleted.
- Rollback backups are protected like any verified backup.
- Minimum stale age: 24 hours.
- Exact confirmation phrase required: PRUNE_STALE_BACKUP_TEMPS.
- Request must include expected_candidate_count; mismatch aborts with zero deletion.
- Server paths and file names are never returned.
- PostgreSQL cleanup unsupported.
- Operation is audited through existing control audit.
- No restore activation behavior change.

## API/UI

POST /v1/dashboard/backups/prune-temp
{
  "confirm":"PRUNE_STALE_BACKUP_TEMPS",
  "expected_candidate_count":N
}

Response contains only aggregate counts/bytes.

Dashboard shows cleanup button only when stale temp count > 0.

## Qualification

- stale temp files removed
- fresh temp files protected
- backups/candidates/receipts/unknown files protected
- wrong confirmation = zero deletion
- count mismatch = zero deletion
- viewer forbidden / operator required
- audit success/failure
- no paths exposed
- full CI + Python 3.11/3.12 green before merge
