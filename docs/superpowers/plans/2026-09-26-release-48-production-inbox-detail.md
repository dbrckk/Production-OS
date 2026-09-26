# Release 48 — Inline production detail

## Goal

Keep operators inside the mobile Productions inbox when opening one production, while preserving shareable server-backed state.

## UX

- add a focused production detail panel inside the Productions view
- use the existing target URL parameter as the project id
- opening an inbox card writes view=productions&target=<project_id>
- closing the detail clears target but preserves production filter/search/sort
- focused detail loads even when the target is outside the visible filtered list
- provide an explicit advanced Managed Projects link

## Data

Reuse GET /v1/dashboard/production-status?project_id=<id>.

Render:

- repository
- final goal
- phase/message
- generation
- worker/stage
- normalized outcome
- generation history

## Actions

Reuse existing safe action functions and server contracts:

- active -> cancel
- needs_attention -> verify
- review_required -> verify / complete
- done -> open only

No new mutation endpoint.

## Completion gate

- inline detail UI contract tests green
- existing production inbox/navigation tests green
- Python 3.11 and 3.12 green
- full unit suite green
- Production E2E green
- package/wheel/Docker/CLI smoke green
- final diff/review clean
