# Release 42 — Idempotent One-tap launch

## Goal

Prevent duplicate Managed Projects when a One-tap POST is retried after timeout, response loss or restart.

## Server contract

POST /v1/dashboard/launch accepts optional request_id.

When request_id is supplied:

- validate 8..128 safe characters
- derive deterministic project id from operator identity + request id
- create managed project with ON CONFLICT reservation semantics
- same id + same launch parameters returns existing project
- same id + different parameters returns HTTP 409
- initialization races return conflict instead of duplicate creation

Requests without request_id remain backward compatible.

## Mobile retry contract

Before POST:

- compute a local fingerprint from repository + instruction
- reuse pending request id when the fingerprint matches
- otherwise generate a new request id
- persist only repository, fingerprint and request id
- never persist instruction text

After successful POST:

- remember project id through existing Release 40 tracker
- clear pending launch request

On network/API error:

- keep pending request id so retry is idempotent

## Qualification

- deterministic ManagedProjectService creation unit coverage
- HTTP same-request replay and conflict tests
- UI pending-request contract
- E2E: launch, restart Control Plane, repeat same POST, assert same project/workflow and exactly one job

## Completion gate

- Python 3.11 and 3.12 green
- unit and Production E2E green
- build/wheel/Docker/CLI smoke green
- branch aligned with main
- no unresolved review threads
