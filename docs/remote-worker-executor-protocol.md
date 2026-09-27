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


## Git worktree isolation

Cooperative multi-agent workflow jobs may include:

```json
{
  "handoff": {
    "isolation": {
      "schema_version": "production-os/git-worktree-isolation/v1",
      "mode": "git-worktree",
      "repository": "owner/repo",
      "workflow_id": "workflow-id",
      "task_id": "implementation-code",
      "attempt": 1,
      "branch": "production-os/workflow-id/implementation-code-a1-...",
      "workspace_key": "implementation-code-...",
      "base_ref": "HEAD",
      "integration_target": false,
      "requirements": {
        "exclusive_workspace": true,
        "no_shared_working_tree_writes": true,
        "commit_changes_before_success": true,
        "report_commit_shas": true
      }
    }
  }
}
```

An executor that receives this contract must create or reuse an isolated Git worktree for exactly that job attempt. It must not write into another active agent's working tree. Successful mutation tasks must commit their changes and return the resulting commit SHAs.

Parallel implementation tasks deliberately receive distinct branch and workspace identities. Their integration task depends on both tasks and receives both results through `upstream_context`, including reported commit SHAs. The integration executor is responsible for combining those commits conservatively in its own isolated integration worktree before validation and review continue.

A retry receives a new attempt-scoped branch/workspace identity. This prevents an interrupted attempt from silently sharing an uncommitted working tree with its retry.


## Automatic worker-managed worktrees

A remote worker can execute the isolation contract itself instead of delegating
worktree setup to the external executor.

Configure one or more mounted repositories and a worktree parent:

```bash
production-os remote-worker-run \
  --url http://control-plane:8080 \
  --worker-id worker-one \
  --executor-command "python /worker/executor.py" \
  --repository-root owner/repo=/srv/repos/repo \
  --worktree-root /srv/worktrees
```

When the claimed job contains a `git-worktree` isolation contract for a
configured repository, Production OS:

1. validates that the configured path is exactly the Git top-level directory;
2. resolves the requested base ref to a concrete commit;
3. creates or safely reuses the attempt-scoped worktree;
4. starts the external executor with that worktree as its current directory;
5. adds `executor_workspace` to the JSON request;
6. exposes `PRODUCTION_OS_REPOSITORY_ROOT`, `PRODUCTION_OS_WORKTREE`,
   `PRODUCTION_OS_WORKTREE_BRANCH`, and `PRODUCTION_OS_WORKTREE_BASE`.

Repository mappings are explicit by design. The worker never guesses a local
path and never receives Git credentials from this mechanism. If no mapping is
configured, the existing external-executor contract remains valid and the
executor may implement isolation itself.


## Automatic repository cache

For one-tap repository selection, workers can materialize the selected GitHub
repository automatically instead of requiring an `--repository-root` mapping.

Set:

```bash
--repository-cache-root /var/lib/production-os/repositories
--worktree-root /var/lib/production-os/worktrees
```

or the equivalent environment variables:

- `PRODUCTION_OS_REPOSITORY_CACHE_DIR`
- `PRODUCTION_OS_WORKTREE_DIR`

For a validated `owner/repo` handoff, the cache clones
`https://github.com/owner/repo.git` with no checkout, verifies the cached
`origin` on reuse, fetches/prunes current remote branches, and then supplies
that local checkout to the worktree runtime. Concurrent materialization of the
same repository is serialized inside the worker process.

No GitHub credential is copied into the executor request. Private-repository
authentication remains the responsibility of the worker's normal Git
credential configuration. Explicit `--repository-root` mappings take
precedence over the automatic cache.
