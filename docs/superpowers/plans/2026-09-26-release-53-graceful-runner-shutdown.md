# Release 53 — Graceful concurrent runner shutdown

## Goal

Stop a concurrent RemoteWorkerRunner safely without orphaning executor subprocesses or corrupting durable job state.

## Runner contract

- expose thread-safe idempotent request_stop()
- stop claiming new work after a stop request
- wake idle polling immediately
- active executors check the stop event at heartbeat cadence
- terminate/kill executor children through the existing bounded termination path
- return abandoned / worker_shutdown outcomes
- never mark unfinished shutdown work completed, failed or cancelled
- converge active_tasks/active_job_keys to zero before return

## Recovery contract

Shutdown leaves unfinished jobs ACKed.

On restart, the same worker opens an authoritative session with its actual active_job_keys. Jobs owned by its previous process but absent from that set are immediately reconciled back to queued state through the existing worker-session recovery contract.

## CLI contract

remote-worker-run installs SIGTERM and SIGINT handlers that only call request_stop(). Previous handlers are restored in finally.

## TDD evidence

RED 1:
- concurrent graceful-stop integration failed because RemoteWorkerRunner had no request_stop method.

RED 2:
- CLI signal contract failed because remote-worker-run installed no SIGTERM/SIGINT handlers.

## Completion gate

- graceful concurrent stop/restart test green
- CLI signal test green
- existing concurrency/cancel/stale/secret tests green
- Python 3.11 and 3.12 green
- full unit suite green
- Production E2E green
- distribution/wheel/Docker/CLI smoke green
- branch current with main
- no unresolved review threads
