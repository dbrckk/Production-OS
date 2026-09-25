# Production-OS Release 26 — Backup Filesystem Capacity

## Goal

Surface backup-filesystem capacity before backup/restore operations fail because the target filesystem is nearly full.

## Principles

- Read-only observation only.
- No automatic deletion.
- No automatic restore or backup mutation.
- No server path exposure.
- Capacity is measured on the configured SQLite backup directory, or its nearest existing parent when the directory has not been created yet.
- PostgreSQL backup storage capacity remains unsupported here.
- Status thresholds are informational only:
  - ok: available ratio >= 10%
  - warning: available ratio < 10%
  - critical: available ratio < 5%
- Unknown filesystem measurements stay unknown; never synthesize zero capacity.

## Metrics

storage.filesystem:
- status
- total_bytes
- free_bytes
- available_bytes
- used_bytes
- used_percent
- available_percent

## API/UI

- Existing /v1/dashboard/backups storage{} includes filesystem{}
- Mobile backup card renders available space and capacity state
- No cleanup or automated action is triggered from the state

## Qualification

- deterministic statvfs conversion
- missing configured directory uses nearest existing parent
- unconfigured/Postgres => unavailable capacity
- filesystem errors => unknown/degraded, not zero
- no paths returned
- full CI + Python 3.11/3.12 green before merge
