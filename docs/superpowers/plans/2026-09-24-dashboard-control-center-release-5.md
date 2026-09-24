# Dashboard Control Center Release 5 — Safe Remediation Playbooks

## Goal

Turn durable incidents into deterministic remediation guidance without introducing destructive autonomous actions.

## Principles

- An incident may expose one or more remediation suggestions.
- Suggestions are derived only from current server facts.
- Destructive or interrupting remediation always requires an explicit operator action.
- No LLM is required for playbook selection.
- No credentials or secrets are returned to the browser.
- Suggested actions must reuse existing validated control APIs.
- A suggestion must explain why it is available or unavailable.

## Initial playbooks

### queue_without_worker
- Suggest `kick` for the GitHub Actions worker.
- Availability is truthful:
  - immediate dispatch configured;
  - scheduled fallback only;
  - unavailable/failed is never shown as started.

### stale_busy_workers
- Suggest worker inspection.
- Suggest `recover-stuck` only when the server reports an expired claimed job.
- Never recover an acked/running job automatically.

### stale_running_executions
- Suggest inspection and optional explicit `cancel-current` only when the job is still active and belongs to the named worker.
- Never auto-cancel.

## Qualification

- deterministic playbook derivation tests
- role/security tests
- no direct queue mutations from suggestion generation
- mobile UI regression
- final CI green before merge
