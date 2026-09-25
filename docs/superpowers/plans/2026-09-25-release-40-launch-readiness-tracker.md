# Release 40 — Launch readiness + persistent last-production tracker

## Goal

Make One-tap launch status truthful before and after submission.

## Server preflight

GET /v1/dashboard/launch-readiness?repository=owner/name

Return:

- repository
- known_repository
- repository_source
- can_launch
- execution = immediate | queued
- available_workers
- online_workers
- queued_jobs
- message
- generated_at

The preflight is advisory. No available worker must not reject launch because the Managed Project is persisted first.

## Mobile tracker

- remember only the last launched project_id in localStorage
- reload the project from GET /v1/managed-projects/{id}
- render real Managed Project state + normalized Release 39 outcome
- survive page/browser reload on the same device
- deep-link into the exact Managed Project
- refresh readiness when repository changes and during normal polling

## Security / semantics

- readiness is viewer-readable
- workers remain forbidden from dashboard endpoints
- no credentials or result payloads are persisted in browser storage
- server remains authoritative for production status
- launch endpoint behavior remains unchanged

## Completion gate

- readiness service tests green
- API authorization contract green
- UI persistence/preflight tests green
- full non-E2E suite green
- Production E2E green
- Python 3.11 and 3.12 green
- packaging/Docker/CLI smoke green
- final diff review clean
