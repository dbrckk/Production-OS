# Release 55 — Worker operations

## Goal

Close the worker-control loop so deployed remote runners visibly acknowledge operator pause, resume, and drain requests while continuing to report authoritative runtime load.

## Existing foundation

Production OS already persists worker desired state (`active`, `paused`, `draining`), exposes operator controls, blocks new claims for paused/draining workers, reports heartbeat load, and marks stale workers dead. Release 55 must build on those contracts rather than introduce a second control system.

## Required behavior

- `RemoteWorkerRunner` reads `control.worker.desired_state` from heartbeat responses.
- A runner acknowledges the observed state on its next heartbeat by sending `control_state`.
- `paused` prevents new claims while leaving active executors untouched.
- `draining` prevents new claims and lets already-active executors finish normally.
- `active` resumes normal claiming.
- Control acknowledgement is durable through the existing dashboard-control store.
- Runner shutdown remains independent: process shutdown still abandons active work for restart recovery rather than pretending it is a drain.
- Worker heartbeat/load remains authoritative and `dead` detection remains based on heartbeat age.

## Safety and compatibility

- No new mutation endpoint.
- No new worker credential scope.
- Worker identity checks remain unchanged.
- Existing `/v1/dashboard/workers/<id>/control` remains the operator mutation surface.
- Existing `/v1/workers/heartbeat` remains the worker acknowledgement surface.
- Existing `/v1/jobs/claim` remains the admission gate.
- Python 3.11 and 3.12 compatibility is required.

## Verification

Tests must prove pause, drain, resume, acknowledgement durability, active-job completion during drain, and that a paused/draining runner does not claim queued work. Full CI, Production E2E, package, wheel, Docker, and CLI smoke tests must remain green.