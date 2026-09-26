# Release 50 — Real remote worker runner

## Goal

Turn remote worker polling into an actual persistent execution path suitable for later production deployment.

## Worker session

Add POST /v1/workers/session.

Worker-role credentials may open only the worker whose id equals the authenticated principal name.

Session opening:

- self-registers capabilities/max concurrency
- accepts authoritative active_job_keys
- immediately reconciles missing persisted claimed/acked jobs
- resets active_tasks to the reported active set

## Executor runner

Add RemoteWorkerRunner and CLI command remote-worker-run.

Executor protocol:

- JSON request on stdin
- JSON result on stdout
- no shell
- success -> existing complete endpoint
- reported/process failure -> existing fail endpoint
- long execution -> periodic heartbeat
- operator cancel -> terminate + acknowledge cancellation
- stale generation -> terminate + stale checkpoint
- timeout -> terminate + fail
- control-plane loss -> terminate locally and leave server recovery to fence the job

## Secret handling

The worker bearer token is sourced from PRODUCTION_OS_WORKER_TOKEN (or --token-env) and removed from the environment passed to the executor process.

## Completion gate

- session self-registration/reconciliation tests
- identity mismatch rejection test
- real subprocess success test
- invalid output failure test
- cooperative cancellation test
- worker-token environment isolation test
- CLI missing-token test
- Python 3.11 / 3.12
- full unit + Production E2E
- build/wheel/Docker/CLI smoke
