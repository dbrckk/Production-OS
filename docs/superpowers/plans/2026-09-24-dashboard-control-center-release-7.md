# Dashboard Control Center Release 7 — Remediation Verification

## Goal

Verify whether incident-linked remediation actually clears the incident, without triggering any additional autonomous action.

## Principles

- Verification is observational only.
- A remediation action never causes a follow-up control automatically.
- Failed control outcomes are marked not_applicable for verification.
- Accepted remediation starts pending.
- If the incident is still active on a later health refresh, verification becomes still_active.
- If the incident later resolves, verification becomes resolved.
- Verification state is derived from current durable incident state, not from browser assumptions.
- No credentials, tokens or arbitrary payloads are stored.

## Schema v13

Extend dashboard_remediation_events with:

- verification_state: pending | still_active | resolved | not_applicable
- verification_checks
- verified_at

SQLite/PostgreSQL parity required.

## Server behavior

- completed failed remediation -> not_applicable
- accepted/dispatched/fallback remediation -> pending
- each incident refresh verifies completed remediation events:
  - related incident resolved -> resolved
  - related incident still open/acknowledged -> still_active
- resolved is terminal and never regresses
- verification does not mutate jobs, workers, workflows or incident status

## API / UI

- remediation history exposes verification state/check count/time
- Activity view displays verification separately from control outcome
- incident filtering remains supported
- direct controls without incident_id remain unaffected

## Qualification

- restart persistence
- failed remediation not_applicable
- active incident -> still_active
- resolved incident -> resolved
- resolved verification never regresses after incident reopen
- SQLite/PostgreSQL schema parity
- Python 3.11/3.12 and full CI green before merge
