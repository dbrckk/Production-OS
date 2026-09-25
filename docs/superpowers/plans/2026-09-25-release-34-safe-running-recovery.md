# Release 34 — Safe recovery after ACK

## Goal

Recover a One-tap production when a worker disappears after ACK, without creating duplicate execution while the old worker may still be alive.

## Recovery gate

An ACKed job is recoverable only when both conditions are true:

- owning worker heartbeat is stale beyond STALE_BUSY_WORKER_SECONDS
- latest running execution telemetry is stale beyond STALE_RUNNING_EXECUTION_SECONDS

## Recovery action

- fence the old worker by atomically changing the job from acked to queued
- clear claim ownership
- record a job-recovered event
- close the old execution attempt as failed with error_type=worker_abandoned
- keep job key, workflow id, Managed Project id and generation unchanged

## E2E scenario

1. Launch through /v1/dashboard/launch.
2. Worker A claims and ACKs the job.
3. Worker A sends fresh telemetry.
4. Expire only Worker A heartbeat.
5. Worker B requests work and must receive no job.
6. Expire execution telemetry too.
7. Worker B requests work and reclaims the same job key.
8. Worker B completes successfully.
9. Verify attempt 1 is worker_abandoned and attempt 2 succeeded.
10. Verify the same Managed Project reaches REVIEW_REQUIRED.

## Completion gate

- dedicated E2E green
- full non-e2e suite green
- Python 3.11 and 3.12 green
- packaging/Docker/CLI smoke green
- final diff review clean
