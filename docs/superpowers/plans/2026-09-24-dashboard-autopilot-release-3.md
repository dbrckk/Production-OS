# Dashboard Autopilot Queue Release 3

**Goal:** Make Production-OS explain what will run next, why it is ranked there, which worker can take it, and what is blocking execution.

## Release slice 1 — Read-only queue intelligence

- Reuse the durable job queue and `PortfolioOptimizer.rank()`; do not add a second scheduler.
- Add `DashboardService.autopilot_queue(limit)`.
- Add viewer endpoint `GET /v1/dashboard/autopilot?limit=...`.
- For each queued job return:
  - queue position and optimizer score;
  - critical-path flag and descendant count;
  - predicted duration and age;
  - required capabilities;
  - eligible online/active workers with spare capacity;
  - preferred worker when available;
  - explicit wait reason when no worker can take the job.
- Worker desired state is authoritative: paused/draining workers are not eligible for new claims.
- Assigned-worker jobs remain constrained to that worker.
- Unknown/missing capability evidence must not be presented as compatible.

## Release slice 2 — Dashboard view

- Add an `Autopilot` primary view.
- Show NOW-style next jobs, ETA, ranking reason and worker eligibility.
- Mobile-first cards; no polling scroll reset.
- Read-only in the first slice. Existing operator controls remain in worker detail.

## Release slice 3 — Qualification

- SQLite + PostgreSQL-compatible behavior.
- Viewer access; worker token forbidden from dashboard route.
- Tests for paused/draining, capability mismatch, assigned worker, saturated worker, and ranked order.
- Full CI before merge.
