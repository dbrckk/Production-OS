# Dashboard Control Center Release 14 — Backup Readiness

## Goal

Create and verify consistent server-side backups before any restore capability is introduced.

## Safety principles

- No client-supplied filesystem path.
- Backup directory is server-only: PRODUCTION_OS_BACKUP_DIR.
- Operator-only backup creation.
- Viewer-readable readiness/catalog metadata.
- No database path, DSN, token, password or secret in API/UI/manifest.
- SQLite backup uses the online sqlite backup API, not a raw file copy.
- Backup is written to a temporary file, integrity-checked, hashed, then atomically renamed.
- Restore is not enabled in Release 14.
- PostgreSQL support is reported truthfully; no fake backup success.
- Backup creation is audit logged.

## SQLite backup

POST /v1/dashboard/backups/create
Body:
{
  "confirm": "CREATE_VERIFIED_BACKUP"
}

Server:
1. Validate configured backup directory.
2. Create backup into server-generated temp name.
3. Run PRAGMA integrity_check on backup.
4. Compute SHA-256 and size.
5. Atomically rename to final server-generated backup id.
6. Persist sidecar manifest with safe metadata only.
7. Return backup id / size / sha256 / created_at / verified.

No source DB path is returned.

## Backup catalog

GET /v1/dashboard/backups

Returns:
- backend_kind
- status: ready | unconfigured | unsupported | degraded
- restore_enabled: false
- backup directory configured: boolean
- safe catalog of verified backup manifests

## PostgreSQL

Release 14 exposes readiness only:
- backend_kind=postgres
- create_supported=false
- status indicates external backup tooling required
- no claim that a backup has been created

A later release may add pg_dump/pg_restore after explicit qualification.

## UI

Overview Storage card gains:
- Backup status
- Last verified backup
- Create verified backup button only when create_supported=true
- Explicit browser confirmation
- no path display

## Qualification

- online SQLite backup contains committed durable data
- integrity_check must equal ok
- hash/size deterministic for file bytes
- manifest contains no path/DSN/secrets
- missing backup directory => no write
- viewer cannot create backup
- operator exact confirmation required
- PostgreSQL reports unsupported creation honestly
- full CI + Python 3.11/3.12 green before merge
