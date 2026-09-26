# Release 47 — Navigable production inbox

## Goal

Make the persistent production inbox fast to navigate on mobile and preserve its state across reloads/shareable URLs.

## Server contract

Extend GET /v1/dashboard/productions with:

- filter=all|active|review|problems|completed
- q=<case-insensitive search>
- sort=priority|recent

Search matches repository, final goal, project id and outcome summary.

Global production totals remain independent of filter/search. The response adds summary.matching, search and sort.

Priority remains:

problems -> review -> active -> completed

Recent sort orders by updated_at descending regardless of category priority.

## UI

- search field
- priority/recent selector
- active filter styling
- URL persistence:
  - production_filter
  - production_q
  - production_sort
- restore these values on page load
- preserve existing target deep-link semantics
- scroll focused production cards into view when the target is visible

## Safety

- read-only endpoint semantics unchanged
- viewer access unchanged
- worker access remains forbidden
- existing cancel/retest/DONE controls are reused unchanged
- no browser-local authority is introduced

## Completion gate

- service search/sort tests green
- HTTP query propagation tests green
- mobile URL-state tests green
- Python 3.11 and 3.12 green
- full unit suite green
- Production E2E green
- package/wheel/Docker/CLI smoke green
- final diff/review clean
