# Release 45 — Server-backed production inbox

## Goal

Show all current/recent Managed Project productions from persistent server state, independent of the browser-local last-project tracker.

## Server

GET /v1/dashboard/productions?limit=50

The feed is built from Managed Projects plus production_status for each visible project.

Visible states:
- ACTIVE
- REVIEW_REQUIRED
- NEEDS_ATTENTION
- up to five recent DONE projects

Summary counts:
- active
- preparing
- queued
- claimed
- running
- cancelling
- review_required
- needs_attention
- done

Each item includes:
- project id / repository / final goal
- generation / managed status
- runtime phase and live execution fields
- normalized outcome evidence

## Mobile

Add a Productions primary view with five-second polling.

Each card reuses the existing safe actions:
- active -> cancel
- cancelling -> disabled cancellation state
- needs_attention -> relaunch/retest
- review_required -> retest / DONE
- all -> open exact Managed Project

## Cross-device guarantee

No localStorage project id is required for this view. A new browser/device can reconstruct the feed from viewer-authorized server state.

## E2E

1. Launch two One-tap projects.
2. Verify both are queued in the inbox.
3. Start one project and publish live telemetry.
4. Verify inbox reports one running + one queued.
5. Restart the Control Plane.
6. Query from a viewer session with no local browser state.
7. Verify both project ids, phases, stage and progress are restored.

## Completion gate

- aggregation tests
- viewer/worker authorization test
- UI contract tests
- restart E2E
- Python 3.11 / 3.12
- full unit + Production E2E
- package/wheel/Docker/CLI smoke
- clean diff and review threads
