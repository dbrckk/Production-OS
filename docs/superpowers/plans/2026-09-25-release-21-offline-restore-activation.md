# Production-OS Release 21 — Offline Restore Activation

## Goal

Activate a previously staged and verified SQLite restore candidate only while the live control plane is offline and the exclusive Release 20 database lock can be acquired.

## Safety

- CLI only; no HTTP activation endpoint.
- SQLite only.
- Exact confirmation phrase required.
- Candidate id is server-issued; no arbitrary source path.
- Candidate manifest, SHA-256, size, integrity and schema are revalidated before activation.
- Current live database is snapshotted to a verified rollback backup before replacement.
- Exclusive database maintenance lock must be acquired; if the live control plane is running activation fails.
- Candidate schema version must equal the current Production-OS schema version.
- Replacement uses a temporary file and atomic os.replace.
- SQLite WAL/SHM sidecars are removed only after the exclusive lock is acquired and before reopening the restored database.
- Restored live database receives PRAGMA integrity_check and schema verification before success is reported.
- On post-replace verification failure, rollback backup is restored automatically.
- PostgreSQL activation remains unsupported.

## CLI

production-os restore-activate \
  --database /path/to/production.sqlite \
  --candidate-id <server-issued-id> \
  --confirm ACTIVATE_STAGED_RESTORE

## Qualification

- live control-plane lock blocks activation
- wrong confirmation makes zero changes
- malformed candidate id rejected
- tampered candidate rejected
- schema mismatch rejected
- rollback backup created before replacement
- successful activation replaces durable content
- post-replace failure rolls back live database
- WAL/SHM cleanup is bounded to the target database sidecars
- PostgreSQL rejected truthfully
- no HTTP activation route
- Python 3.11/3.12 + full CI green before merge
