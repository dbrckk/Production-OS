# Release 41 — Live production tracking

## Goal

Expose the real execution phase of the last One-tap Managed Project on mobile.

## Server

GET /v1/dashboard/production-status?project_id=<id>

Returns the authoritative Managed Project plus runtime fields:

- phase
- message
- workflow/task/job status
- job key
- worker id
- delivery attempt
- execution stage
- telemetry progress
- last telemetry timestamp
- observed queue position

## Mobile

- poll the remembered last project every 5 seconds
- show queued / claimed / running / review / attention / done
- show worker, attempt, stage and queue position when available
- show a progress bar when telemetry includes progress
- reuse normalized production outcome once terminal
- keep exact Managed Project deep link

## Qualification

E2E: One-tap launch -> queued -> worker claim -> ACK -> telemetry at 67% -> completion -> REVIEW_REQUIRED -> Control Plane restart -> same status and normalized result restored.

## Completion gate

- service phase tests green
- API auth test green
- UI tracker contract green
- dedicated E2E green
- full suite + Python 3.11/3.12 green
- wheel/Docker/CLI smoke green
