# Production-OS Release 16 — Operations E2E Qualification

## Goal

Qualify the full current Production-OS operator path end-to-end before introducing destructive restore.

## Scenario

On an isolated temporary SQLite database:

1. Start authenticated control plane.
2. Create a workflow/job from an operator launch.
3. Register worker and exercise pause/resume/drain.
4. Claim/ack a job.
5. Create an incident and execute a server-validated remediation path.
6. Persist control/remediation audit.
7. Create a verified SQLite backup.
8. Verify restore readiness for that backup.
9. Confirm live database remains unchanged.
10. Restart control plane and verify durable state remains readable.

## Safety

- test-only temporary database and backup directory
- no external network dependency
- no production restore
- no secrets in fixtures
- no paid dependency
- deterministic assertions

## Qualification

- full scenario green on Python 3.11/3.12
- existing suite remains green
- no changes to production control semantics unless a real defect is found
