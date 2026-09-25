# Release 33 — Automatic expired-claim recovery

## Goal

Allow the worker pool to recover a One-tap production automatically when a worker disappears after claiming a job but before acknowledging it.

## Runtime change

POST /v1/jobs/claim now calls the queue's expired-claim recovery before selecting a candidate.

Recovery remains fail-safe:

- only status=claimed jobs are eligible
- ACK deadline must be expired
- acknowledged/running jobs are never auto-requeued
- delivery attempts remain monotonic
- attempt ceiling sends the job to dead-letter
- workflow and Managed Project identity are preserved

## E2E scenario

1. Launch through POST /v1/dashboard/launch.
2. Worker A claims the generated job.
3. Simulate Worker A disappearing before ACK by expiring its claim.
4. Worker B requests work.
5. The claim path automatically requeues the expired job.
6. Worker B claims the same job key, ACKs, and completes it.
7. Verify the same Managed Project and workflow generation reaches REVIEW_REQUIRED.
8. Verify exactly one job-recovered event and delivery_attempt=2.

## Completion gate

- dedicated E2E recovery test green
- full non-e2e suite green
- Python 3.11 and 3.12 green
- packaging/Docker/CLI smoke green
- final diff review clean
