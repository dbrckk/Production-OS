# Release 36 — Worker session reconciliation

## Goal

Recover safely when the Control Plane and a worker process both restart, including multiple queued One-tap projects.

## Registration contract

POST /v1/workers/register keeps its existing behavior unless active_job_keys is supplied.

When active_job_keys is supplied:

- treat it as the new worker process's authoritative in-memory active set
- preserve matching claimed/acked jobs
- recover claimed/acked jobs owned by the same worker but missing from that set
- close missing ACKed execution attempts as worker_restarted
- reset active_tasks to the number of reported active jobs
- preserve job/project/workflow/generation identity
- keep delivery_attempt monotonic and respect dead-letter limits

## E2E scenario

1. Register Worker A.
2. Launch two One-tap Managed Projects.
3. Worker A claims + ACKs one project and emits telemetry.
4. Crash Control Plane and Worker A.
5. Restart Control Plane from the same database.
6. Re-register Worker A with active_job_keys=[].
7. Verify the old ACKed job is fenced and requeued immediately.
8. Register Worker B.
9. Worker A and Worker B each claim one of the two queued jobs.
10. Complete both.
11. Verify both original Managed Projects reach REVIEW_REQUIRED with their original workflow ids and generation 1.
12. Verify the abandoned job has attempt 1=worker_restarted and attempt 2=succeeded.

## Completion gate

- dedicated simultaneous-restart E2E green
- full non-E2E suite green
- Python 3.11 and 3.12 green
- packaging/Docker/CLI smoke green
- final diff review clean
