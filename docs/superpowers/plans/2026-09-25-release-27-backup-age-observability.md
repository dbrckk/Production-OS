# Release 27 — Verified backup age observability

## Goal

Add read-only age visibility for verified SQLite backups so operators can understand backup accumulation before any retention/deletion policy is designed.

## Scope

- aggregate verified backup age distribution
- valid/invalid timestamp counts
- oldest/newest verified backup timestamp
- age buckets: <24h, 1–7d, 7–30d, >30d
- mobile dashboard rendering
- no backup deletion
- no automatic retention
- no path exposure
- regression coverage

## Safety

This release is observational only. It does not delete, archive, compact, activate, restore or otherwise mutate verified backup artifacts.

## Completion gate

- full CI green
- Python 3.11 and 3.12 green
- final diff/security review clean
