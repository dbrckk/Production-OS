# Dashboard Control Center Release 4 — Incident Management

## Goal

Turn Release 3 operational health signals into durable, reviewable incident records without introducing destructive autonomous remediation.

## Slice 1 — durable incidents

- Persist incidents derived from operational health / alerts.
- Stable deduplication key per incident code + affected target.
- Track first_seen_at, last_seen_at, occurrence_count, status.
- Status values: open, acknowledged, resolved.
- Never persist credentials or raw request headers.

## Slice 2 — acknowledgement

- Operator-only acknowledge action with actor and timestamp.
- Viewer may read incidents.
- Worker role may not read dashboard incidents.
- Repeated diagnostics update an existing open/acknowledged incident instead of creating duplicates.

## Slice 3 — safe resolution

- When evidence clears, mark incident resolved; do not delete history.
- No automatic pause/cancel/retry/recover from an incident.
- Dashboard shows open, acknowledged, and recently resolved incidents.

## Qualification

- SQLite/PostgreSQL parity.
- Restart persistence.
- Dedupe tests.
- Role/security tests.
- Mobile dashboard regression.
