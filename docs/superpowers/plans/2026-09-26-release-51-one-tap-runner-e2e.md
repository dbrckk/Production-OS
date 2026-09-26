# Release 51 — One-tap to real runner qualification

## Goal

Qualify the exact user-facing One-tap production lifecycle using the real remote worker runner and an actual subprocess executor.

## Success path

1. Launch with POST /v1/dashboard/launch.
2. Preserve project/workflow/generation identity.
3. Open worker session through RemoteWorkerRunner.
4. Claim + ACK the generated job.
5. Execute a JSON subprocess.
6. Complete through the worker API.
7. Reconcile the Managed Project to REVIEW_REQUIRED.
8. Verify outcome evidence in production-status and production inbox.

## Failure path

1. Launch a second One-tap production.
2. Executor returns status=failed, reason=tests_failed.
3. Runner fails the owned job.
4. Managed Project reconciles to NEEDS_ATTENTION.
5. Production inbox exposes it under problems.
6. Attention feed exposes validation_failed with instructions + verify actions.

## Evidence

Success must preserve:
- project id
- workflow id
- generation 1
- validation tests
- changed-file count
- commit SHA evidence

Failure must preserve:
- executor summary
- failed validation state
- actionable project identity

## Completion gate

- dedicated Release 51 E2E success green
- dedicated Release 51 E2E failure green
- Python 3.11 and 3.12 green
- full unit suite green
- all Production E2E green
- distribution/wheel/Docker/CLI smoke green
- final diff/review clean
