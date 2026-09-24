# Dashboard Control Center Release 10 — Remediation Durability

## Goal

Measure how long observed remediation resolutions remain durable before recurrence, without turning durability metrics into automatic control decisions.

## Principles

- Read-only analytics only.
- No control action is triggered from durability metrics.
- Durability is measured only for remediation events whose verification reached resolved.
- Time-to-recurrence = recurred_at - verified_at.
- Watching resolutions expose observed age, not a claimed final durability.
- Every rate/count exposes its sample size.
- No LLM or paid dependency required.

## Metrics

For 24h / 7d / 30d / all:
- resolved remediation events
- currently watching recurrence
- recurred
- recurrence denominator
- observed recurrence rate
- median time-to-recurrence seconds
- minimum / maximum observed time-to-recurrence seconds
- resolved-without-recurrence age median for currently watching events

Breakdowns by action and incident code keep the same explicit denominators.

## API / UI

- Extend existing remediation analytics response.
- No new control endpoint.
- Activity view displays recurrence timing separately from resolution timing.
- Mobile-safe display.

## Qualification

- deterministic timing tests
- negative/invalid timestamps ignored
- unresolved/not_applicable excluded
- window semantics preserved
- no control mutation
- full CI + Python 3.11/3.12 green before merge


## Implemented in current branch

- deterministic time-to-recurrence metrics
- median/min/max recurrence delay for valid recurred events
- observed age median for resolved events still under recurrence watch
- invalid or negative timestamp durations ignored
- existing window semantics and explicit recurrence denominators preserved
- Activity view durability display
- unit/UI regression coverage
- README documentation

## Remaining before Release 10 completion

- final CI qualification on the complete head
- final diff/security review
- mark PR ready and merge only after green final head
