# Release 28 — Backup retention preview

## Goal

Expose a conservative, read-only preview of verified SQLite backups that could be eligible for a future retention cleanup.

## Policy preview

- retention threshold: 30 days
- always keep the newest 3 verified backups
- protect backups referenced by restore activation history
- protect invalid-timestamp backups
- aggregate counts/bytes only
- no candidate identifiers or server paths

## Safety

Release 28 performs no deletion, archive, compaction, restore activation or automatic retention.

## Completion gate

- full CI green
- Python 3.11 and 3.12 green
- final diff/security review clean
