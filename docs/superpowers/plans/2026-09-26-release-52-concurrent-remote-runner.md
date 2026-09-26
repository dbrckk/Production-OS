# Release 52 — Concurrent remote worker runner

## Goal

Make RemoteWorkerRunner max_concurrency reflect actual simultaneous executor subprocesses and truthful worker active-job state.

## Contract

- max_concurrency bounds simultaneously executing subprocesses.
- active_tasks equals the size of the authoritative active job set.
- active_job_keys contains every currently executing job.
- each executor keeps independent timeout, stale-generation and cancellation behavior.
- cancellation of one job must not clear unrelated active jobs.
- bounded runs stop claiming after their cycle budget but drain work already launched.
- continuous runs refill freed slots without exceeding max_concurrency.

## Regression

With max_concurrency=2:

1. enqueue two compatible jobs;
2. start one bounded runner cycle;
3. require both executor subprocesses to reach a shared barrier;
4. observe persisted worker active_tasks=2;
5. release both executors;
6. verify two distinct jobs complete;
7. verify worker active_tasks returns to 0.

The test fails against Release 50 because only one executor starts.

## Completion gate

- concurrency regression green after verified RED
- existing runner success/failure/cancel/stale/secret tests green
- Python 3.11 and 3.12 green
- full unit suite green
- Production E2E green
- distribution/wheel/Docker/CLI smoke green
- branch current with main
- no unresolved review threads
