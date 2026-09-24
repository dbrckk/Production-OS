# Dashboard Control Center Release 8 — Remediation Analytics

## Goal

Summarize observed remediation effectiveness without turning historical metrics into automatic control decisions.

## Principles

- Analytics are read-only.
- Metrics describe observed remediation history only.
- Pending and not_applicable events are never counted as resolved or unresolved effectiveness outcomes.
- Every rate exposes its denominator.
- Small samples are shown as small samples, not extrapolated.
- No ranking, recommendation, retry, cancellation, recovery or worker control is triggered from analytics.
- No LLM is required.

## Metrics

For a selected window (24h / 7d / 30d / all):

- total remediation events
- resolved verification count
- still-active verification count
- pending count
- not-applicable count
- observed resolution rate:
  - denominator = resolved + still_active
  - null when denominator is zero
- median observed resolution detection seconds:
  - verified_at - completed_at for resolved events only
- breakdown by action
- breakdown by incident code

Each breakdown exposes:

- total
- resolved
- still_active
- pending
- not_applicable
- observed_resolution_rate
- effectiveness_denominator

## API / UI

- GET /v1/dashboard/remediation-analytics?window=...
- viewer-readable, worker forbidden through dashboard authorization
- Activity view shows summary and action/incident breakdowns
- current dashboard time-window selector drives analytics
- UI must show sample counts next to rates

## Qualification

- deterministic aggregation tests
- invalid window rejected
- pending/not_applicable excluded from effectiveness denominator
- median derived only from resolved events with timestamps
- viewer access / worker denial
- mobile UI regression
- final CI green before merge


## Implemented in current branch

- deterministic remediation analytics aggregator
- explicit effectiveness denominator semantics
- pending and not_applicable excluded from effectiveness rates
- median resolution-detection duration from resolved events only
- 24h / 7d / 30d / all window filtering
- breakdown by action and incident code
- remediation evidence join from durable incident/remediation data
- viewer-readable remediation analytics API
- worker role remains forbidden by dashboard authorization
- Activity view shows summary, sample size, action and incident breakdowns
- invalid window rejection
- README and API/UI/unit regression coverage

## Remaining before Release 8 completion

- final CI qualification on the complete head
- final diff/security review
- mark PR ready and merge only after green final head
