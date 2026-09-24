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


## Implemented in current branch

- schema v13 SQLite/PostgreSQL verification columns
- additive migration for existing v12 remediation ledgers
- remediation verification lifecycle: pending / still_active / resolved / not_applicable
- failed remediation -> not_applicable
- incident refresh drives observational verification only
- resolved verification is terminal
- repeated still-active polling is idempotent and does not amplify writes
- remediation history refreshes against current incident state
- Activity view separates control outcome from verification state
- SQLite migration, lifecycle, terminal-state and polling-idempotence tests
- PostgreSQL schema parity contract
- README documentation and UI/API regression coverage

## Remaining before Release 7 completion

- final CI qualification on the complete head
- final diff/security review
- mark PR ready and merge only after green final head
