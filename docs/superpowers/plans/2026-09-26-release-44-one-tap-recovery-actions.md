# Release 44 — One-tap recovery and completion actions

## Goal

Complete the mobile Managed Project lifecycle from the persistent last-production tracker.

## UI

For NEEDS_ATTENTION:
- show Relancer / retester
- call the existing verification endpoint
- refresh last production, Managed Projects, Attention and launch readiness

For REVIEW_REQUIRED:
- show Retester
- show Valider DONE
- keep the exact MARK_PROJECT_DONE confirmation contract

## Safety

- no new mutation endpoint
- operator-only server authorization remains unchanged
- immutable workflow generations remain the retry boundary
- DONE still requires explicit confirmation
- same Managed Project id survives cancellation, recovery and completion

## E2E

1. Launch generation 1.
2. Cancel it while queued.
3. Verify project becomes NEEDS_ATTENTION.
4. Retest the same project.
5. Verify generation 2 uses a new workflow.
6. Worker executes generation 2 successfully.
7. Verify REVIEW_REQUIRED and normalized validation evidence.
8. Mark DONE.
9. Verify final production status is done with the generation-2 workflow.

## Completion gate

- UI contract tests green
- dedicated E2E green
- full non-E2E suite green
- Python 3.11 and 3.12 green
- packaging, wheel, Docker and CLI smoke green
- final diff review clean
