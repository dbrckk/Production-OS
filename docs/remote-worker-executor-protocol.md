# Remote worker executor protocol

## Request

Production-OS starts the configured executor directly, without a shell, and writes one UTF-8 JSON object to stdin.

Schema:

`production-os/worker-executor-request/v1`

Fields:

- `job.key`: durable Production-OS job key.
- `job.payload`: the complete claimed job representation returned by the Control Plane.
- Managed Project jobs expose their handoff at `job.payload.payload.handoff`.

The runner does not inject the worker bearer token into the child environment.

## Success response

The executor must write a single JSON object to stdout:

```json
{
  "status": "succeeded",
  "result": {
    "summary": "human-readable result",
    "usage": {
      "total_tokens": 1234,
      "runs": 1,
      "agents": {"auto": 1}
    },
    "validation": {
      "status": "passed",
      "tests": ["unit", "integration"]
    }
  }
}
```

`result` must be a JSON object. Its shape is intentionally compatible with the existing job completion and Managed Project outcome pipeline.

## Failure response

```json
{
  "status": "failed",
  "reason": "tests_failed",
  "result": {
    "summary": "Tests did not pass",
    "validation": {"status": "failed"}
  }
}
```

The runner records the failure through the existing job/workflow failure path.

## Process failures

Production-OS generates deterministic reasons:

- `executor_timeout`
- `executor_invalid_output`
- `executor_exit_<code>`
- `control_plane_unavailable` (execution is abandoned locally so server recovery can fence/requeue it)
- `stale` (the process is terminated and a stale-generation checkpoint event is recorded)

## Cancellation

While the executor is running, the runner heartbeats the current job. If the Control Plane reports `cancel_requested`, the child process is terminated and the cancellation is acknowledged through the existing worker heartbeat contract.

## Session identity

`POST /v1/workers/session` allows a worker-role token to create/reconcile only the worker whose id equals that token entry's `name`.

Recommended auth entry:

```json
{
  "name": "worker-one",
  "role": "worker",
  "sha256": "<sha256 of bearer token>"
}
```

This lets a restarted runner reconcile its own abandoned work without possessing an operator token.
