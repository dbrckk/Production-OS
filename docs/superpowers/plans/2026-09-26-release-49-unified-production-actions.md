# Release 49 — Unified production actions

## Goal

Make Productions the primary mobile operator surface for Managed Project follow-up.

## Attention routing

Managed Project items in NEEDS_ATTENTION and REVIEW_REQUIRED use:

view=productions
target=<project_id>

Incident and blocked-job routing remain unchanged.

## Inline follow-up

For NEEDS_ATTENTION and REVIEW_REQUIRED details:

- show an Instruction supplémentaire textarea
- submit through the existing POST /v1/managed-projects/{id}/instructions endpoint
- do not create a new mutation route
- preserve the existing immutable generation semantics
- refresh Productions, Attention and last-production tracker after success

## Existing actions

Keep using existing functions and confirmations for:

- cancel active production
- verify/retest
- mark DONE

Managed Projects remains available from the advanced-view button.

## Completion gate

- attention routing tests green
- inline instruction UI tests green
- existing inbox/detail tests green
- Python 3.11 and 3.12 green
- full unit suite green
- Production E2E green
- package/wheel/Docker/CLI smoke green
- final diff/review clean
