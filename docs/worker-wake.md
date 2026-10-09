# Worker wake and ephemeral GitHub Actions runners

Production-OS dispatches jobs to registered workers. A persistent worker may
claim the next queued job without a new launch; a GitHub Actions runner cannot.
The Actions workflow in `dbrckk/ai-dev-server` executes a bounded job and exits,
but the server's worker registry can retain its last `online` heartbeat until the
dead-worker timeout. The wake decision must not treat that stale heartbeat as
proof that a runner process is still polling.

## Wake policy

With queued work, only **active, online, compatible, persistent workers with
free concurrency slots** suppress a new wake. Short-lived workers still
participate in normal claims and heartbeats; they are just excluded from the
persistent-capacity check. Fleet-wide operator pause/drain continues to block
automatic wake. Wake requests retain the existing durable cooldown.

The default short-lived worker ID is `github-actions-worker`, matching the
Actions workflow's `PRODUCTION_OS_WORKER_ID`. Override it on the **control
plane** when deployments use different one-shot IDs:

```bash
PRODUCTION_OS_EPHEMERAL_WORKER_IDS=github-actions-worker,actions-custom
```

An explicitly empty value disables the default classification. Persistent
workers must not be included in this list. A new dispatch may occur while an
Actions runner is already active, but the Actions workflow's single-flight
concurrency group prevents simultaneous worker jobs.

## Immediate wake prerequisites

Set these on the **Production-OS server** (for example, its Render service):

```text
GITHUB_TOKEN=<GitHub credential with Actions: write on dbrckk/ai-dev-server>
PRODUCTION_OS_ACTIONS_REPOSITORY=dbrckk/ai-dev-server
PRODUCTION_OS_ACTIONS_WORKFLOW=production-os-actions-worker.yml
PRODUCTION_OS_ACTIONS_REF=main
```

Configure the GitHub credential as a secret, never in source code. On
`dbrckk/ai-dev-server`, the workflow still requires its configured
`PRODUCTION_OS_WORKER_TOKEN` and Studio provider credentials. The server's
worker-token identity must match the Actions worker ID.

Without a valid dispatch credential and workflow configuration,
`worker_wake_mode()` reports `scheduled_fallback` rather than immediate
dispatch. GitHub scheduled workflows are best-effort and may run late;
`scheduled_fallback` is **not** evidence that a runner has started.

## Verification

1. Check the server's `/readyz` response.
2. Queue a bounded, authorized canary through the existing
   `production-os-worker-canary.yml` workflow.
3. Verify that the worker run reports a compatible queued job, performs one
   execution, and reports `completed`.
4. Verify the canary receives `succeeded` rather than only `launched`.
5. Run `pytest -q tests/test_worker_wake.py tests/test_control_plane.py
   tests/test_dashboard_control.py` for the wake and operator-control
   regressions.

Never treat GitHub Actions run `success` by itself as proof of executed work:
a runner can exit successfully after probing an empty queue.
