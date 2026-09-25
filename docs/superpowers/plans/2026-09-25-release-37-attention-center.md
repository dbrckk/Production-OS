# Release 37 — À faire maintenant

## Goal

Make the mobile dashboard operationally actionable by default.

## Server

GET /v1/dashboard/attention aggregates and prioritizes:

- active incidents
- Managed Projects NEEDS_ATTENTION
- failed current managed workflows (CI / validation)
- Managed Projects REVIEW_REQUIRED
- blocked queued jobs from Autopilot
- recently completed Managed Projects

The response includes compact counts plus a ranked item feed.

## UI

- add an À faire navigation item
- make it the default dashboard view
- keep the One-tap launch card above navigation
- render action counts and prioritized cards
- route actions into existing Managed, Autopilot or Overview views
- preserve existing polling and scroll behavior

## Safety

- viewer role can read the feed
- worker role remains blocked from dashboard endpoints
- no new mutation path is introduced
- existing control confirmation semantics remain unchanged

## Completion gate

- service aggregation tests green
- API authorization test green
- mobile UI contract tests green
- full non-E2E suite green
- Production E2E green
- Python 3.11 and 3.12 green
- packaging/Docker/CLI smoke green
- final diff review clean
