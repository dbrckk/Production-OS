# Production-OS Release 22 — Restore Replay Protection

## Goal

Make successful staged SQLite restore activation one-shot and durably auditable.

## Safety

- CLI only; no HTTP activation endpoint.
- Successful activation marks the candidate manifest as activated.
- Activated candidates cannot be activated again.
- Candidate replay is rejected before acquiring mutation state.
- Failed activation followed by successful rollback leaves the candidate reusable.
- A durable activation receipt records candidate id, source backup id, rollback backup id, activated_at, schema version and SHA-256.
- Receipts contain no credentials or arbitrary payloads.
- Candidate manifest update happens only after restored database verification succeeds.
- Receipt write and candidate manifest finalization use atomic replace.
- Existing offline lock, exact confirmation, integrity/schema checks and rollback behavior remain unchanged.

## Qualification

- first activation succeeds
- second activation of same candidate is rejected
- failed activation + rollback does not consume candidate
- activation receipt is created and contains only structured safe fields
- tampered activated manifest remains rejected
- no HTTP activation route
- full CI + Python 3.11/3.12 green before merge
