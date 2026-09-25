# Release 35 — Control-plane restart reconciliation

## Goal

Prove that restarting the Control Plane during an active One-tap production neither duplicates nor loses execution state.

## Scenario A — active worker reconnects

1. Launch a One-tap Managed Project.
2. Worker A claims, ACKs and emits telemetry.
3. Stop the Control Plane.
4. Recreate it from the same database.
5. Verify job=acked, execution=running, project=ACTIVE, same workflow.
6. Worker A reconnects, heartbeats and emits telemetry.
7. Worker A completes.
8. Verify only one execution attempt exists and project becomes REVIEW_REQUIRED.

## Scenario B — worker stays abandoned

1. Launch and ACK a One-tap job.
2. Persist stale worker heartbeat + stale execution telemetry.
3. Restart the Control Plane.
4. Verify persisted state is still ACKed before recovery.
5. Worker B requests work.
6. Existing Release 34 dual-staleness recovery fences Worker A.
7. Worker B reclaims the same job and completes.
8. Verify attempt 1=worker_abandoned, attempt 2=succeeded.
9. Verify project/workflow/generation identities are unchanged.

## Completion gate

- both restart E2Es green
- full non-e2e suite green
- Python 3.11 and 3.12 green
- packaging/Docker/CLI smoke green
- final diff review clean
