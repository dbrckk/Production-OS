# Release 29 — Guarded verified-backup retention cleanup

## Goal

Allow explicit operator cleanup of verified SQLite backups that are already classified as retention candidates.

## Guardrails

- exact confirmation phrase required
- operator role required
- current candidate count must match
- opaque SHA-256 candidate fingerprint must match
- newest three verified backups are protected
- backups newer than 30 days are protected
- restore source/rollback backups are protected
- invalid-timestamp backups are protected
- clients never submit file paths or backup filenames
- no automatic cleanup

## Audit

Accepted and conflicted cleanup attempts are written to the existing control audit.

## Completion gate

- full CI green
- Python 3.11 and 3.12 green
- final diff/security review clean
