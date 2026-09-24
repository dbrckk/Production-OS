# Dashboard Control Center Release 9 — Remediation Recurrence

## Goal

Observe whether an incident that was resolved after a remediation later reappears, without using recurrence as an automatic control signal.

## Principles

- Recurrence tracking is observational only.
- No retry, cancel, recover, pause, drain or kick is triggered from recurrence.
- A remediation can be recurrence-tracked only after verification_state=resolved.
- The incident occurrence_count is snapshotted when resolution is verified.
- A later higher occurrence_count marks that remediation as recurred.
- Recurred is terminal for that remediation event.
- Rates always expose their denominator.
- No credentials, tokens or arbitrary payloads are stored.

## Schema v14

Extend dashboard_remediation_events with:

- resolved_occurrence_count INTEGER
- recurrence_state TEXT NOT NULL DEFAULT 'not_evaluated'
  - not_evaluated
  - watching
  - recurred
- recurred_at TEXT

SQLite/PostgreSQL additive migration parity required.

## Server behavior

- when verification transitions to resolved:
  - snapshot current incident occurrence_count
  - set recurrence_state=watching
- later incident refresh:
  - if occurrence_count > resolved_occurrence_count -> recurred
  - otherwise keep watching without write amplification
- recurred never regresses
- not_applicable / still_active / pending do not enter recurrence tracking

## Analytics / UI

- remediation history exposes recurrence state and recurred_at
- remediation analytics exposes:
  - watching count
  - recurred count
  - recurrence denominator = watching + recurred
  - observed recurrence rate or null when denominator=0
- Activity view displays recurrence separately from verification/outcome

## Qualification

- v13 -> v14 SQLite migration
- PostgreSQL parity
- snapshot occurrence count at resolution
- reopened incident -> recurred
- unchanged incident does not amplify writes
- recurred is terminal
- pending/not_applicable excluded
- direct controls unaffected
- full CI and Python 3.11/3.12 green before merge
