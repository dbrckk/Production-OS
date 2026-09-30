# Native Executor Design

Date: 2026-09-30

## Status

Proposed design for replacing the current mandatory external worker executor with a Production OS native executor, while preserving external-executor compatibility as a fallback during migration.

## Problem

Production OS already owns most of the execution control plane:

- repository materialization and refresh;
- per-attempt Git worktree isolation;
- persistent per-job runtime state and checkpoints;
- worker liveness, cancellation and stale-generation fencing;
- dynamic multi-agent planning and DAG expansion;
- integration preflight and Git-result verification;
- browser/computer-use plan validation;
- resumable browser sessions and action checkpoints;
- bounded multi-turn browser execution.

However, `remote-worker-run` still requires an `--executor-command`. The worker launches that external process for every job and delegates task execution to it.

This creates a mismatch between the desired UX and the current architecture. The target UX is:

1. select a repository;
2. provide an instruction;
3. let Production OS choose and execute the required capabilities.

The browser worker is the clearest case: the worker image already contains Chromium, Playwright, the browser runtime, durable browser loop state, and the `browser_computer` contract, but cannot execute that contract without an external executor process.

## Goals

The native executor must:

1. execute Production OS-native tool contracts without requiring an external executor;
2. initially support browser/computer-use jobs end to end;
3. preserve the existing worker request/result schemas;
4. preserve worktree, runtime, heartbeat, cancellation, stale-generation, timeout and Git-verification behavior;
5. allow unsupported jobs to fall back to the existing external executor;
6. let the browser specialist worker run useful jobs with no `PRODUCTION_OS_WORKER_EXECUTOR_COMMAND`;
7. keep execution bounded, auditable and recoverable after process or worker restart;
8. avoid introducing a second scheduling or job-state system.

## Non-goals

This phase does not attempt to:

- replace every external coding/model executor;
- embed a general-purpose LLM provider implementation directly into the worker;
- remove the external executor protocol;
- change the control-plane job API;
- make arbitrary browser JavaScript evaluation available;
- bypass existing capability routing, policy, worktree or runtime safeguards.

## Architecture

### 1. Executor mode

`remote-worker-run` gains:

```
--executor-mode auto|native|external
```

Default: `auto`.

Behavior:

- `native`: only Production OS-native execution is allowed. Unsupported jobs fail with a deterministic `native_executor_unsupported` reason.
- `external`: preserve the current behavior and require `--executor-command`.
- `auto`: prefer native execution when a compatible native handler exists; otherwise fall back to `--executor-command` when configured.

In `auto` mode, absence of `--executor-command` is valid as long as a claimed job has a native handler.

### 2. Native executor boundary

Add a dedicated module:

`src/production_os/native_executor.py`

It owns only task execution selection and native handler invocation.

It does not own:

- claiming or acknowledging jobs;
- heartbeats;
- process cancellation;
- timeout accounting;
- worktree creation;
- repository cache management;
- runtime/checkpoint lifecycle;
- job completion/failure writes.

Those remain in `RemoteWorkerRunner`.

The native executor accepts a structured context produced by the runner and returns the same logical result envelope expected from external executors:

```json
{
  "status": "succeeded",
  "result": {
    "summary": "...",
    "validation": {}
  }
}
```

or:

```json
{
  "status": "failed",
  "reason": "native_executor_...",
  "result": {
    "summary": "..."
  }
}
```

### 3. Native handler registry

The native executor exposes a small registry keyed by tool contract / capability.

Initial handler:

`browser_computer`

Future handlers may include other Production OS-native tools, but no generic registry framework beyond what is needed for deterministic lookup should be added in this phase.

Selection order:

1. inspect `handoff.tool_contracts`;
2. check for a supported native contract;
3. validate that required capability/runtime prerequisites are present;
4. invoke the matching handler;
5. otherwise return `unsupported` to the runner so `auto` can fall back externally.

The handler lookup must be deterministic and must not infer arbitrary shell commands from model-authored input.

### 4. Browser native handler

The browser handler uses the existing browser runtime rather than creating another browser implementation.

It must use:

- `validate_browser_loop_config`;
- `run_browser_turn_loop`;
- existing browser-plan validation;
- existing storage/session/checkpoint paths;
- existing runtime workspace.

The native browser input contract is a handoff field containing a bounded browser loop request.

Proposed field:

```json
{
  "handoff": {
    "browser": {
      "config": {
        "schema_version": "production-os/browser-computer-loop/v1",
        "allowed_hosts": ["example.com"],
        "persist_session": true,
        "allow_private_network": false,
        "max_turns": 32
      },
      "turns": [
        {
          "schema_version": "production-os/browser-computer-turn/v1",
          "turn_id": "observe-1",
          "actions": [
            {"action": "navigate", "url": "https://example.com"},
            {"action": "snapshot", "name": "page"}
          ]
        }
      ]
    }
  }
}
```

The first native phase supports a finite submitted turn list. Interactive model-driven generation of additional turns remains the responsibility of a higher-level agent/executor until a native planner/model loop is added.

This deliberately separates:

- browser execution, which Production OS can already perform safely;
- browser reasoning/model generation, which may still come from the external agent layer.

### 5. Runtime paths

The runner already creates `PersistentAgentRuntime` context. The browser handler derives durable files from that runtime workspace:

- `browser-state.json`
- `browser-session.json`
- `browser-checkpoint.json`
- `browser-artifacts/`

The handler must not invent paths outside the runtime workspace when a runtime context is available.

If no persistent runtime exists for a browser job requesting `persist_session=true`, native execution must fail closed rather than silently downgrade persistence.

### 6. Runner integration

`RemoteWorkerRunner` remains the single job lifecycle authority.

The execution sequence becomes:

1. prepare runtime context;
2. ACK job;
3. register active heartbeat;
4. fence stale jobs;
5. prepare worktree and integration preflight;
6. build common executor context;
7. select execution path:
   - native handler;
   - external child process;
8. apply the same timeout/cancellation/stale-generation lifecycle;
9. normalize result;
10. perform authoritative Git verification for managed worktrees;
11. complete/fail job through the control plane;
12. perform successful worktree cleanup.

The native path must not bypass Git result verification.

### 7. Cancellation and timeout model

External execution is currently cancellable because the runner owns a child process.

Native execution must therefore run in a cancellable execution unit rather than block the polling thread indefinitely.

Required implementation:

- start the native handler in a dedicated `Future` owned by the job execution path;
- keep the runner thread in a bounded supervision loop using the existing heartbeat interval;
- on each supervision tick, observe runtime checkpoints, heartbeat the control plane, enforce timeout, inspect stale-generation state, and inspect cancellation state;
- pass a per-job `threading.Event` cancellation signal into the native handler;
- browser execution checks that event before every turn and before starting each new browser plan;
- action-level execution remains bounded by existing browser action timeouts;
- if cancellation, stale-generation fencing, worker shutdown, or timeout occurs, set the cancellation event and stop accepting new native work.

The runner must not call job completion/failure until the native future has reached a terminal state or the cooperative cancellation grace period has expired.

This phase does not attempt unsafe Python thread termination. Native handlers must cooperate with cancellation at defined safe boundaries. If a handler does not stop within the bounded grace period, the job is abandoned/fenced rather than re-executed through the external fallback.

### 8. External fallback

In `auto` mode:

- if native handler selection returns `supported`, execute natively;
- if selection returns `unsupported` and an external command exists, use the existing external path;
- if no handler and no external command exist, fail deterministically with `executor_unavailable`.

A native handler runtime failure must not silently fall back to an external executor. That could duplicate side effects. Fallback occurs only before native execution begins.

### 9. CLI and Compose

`remote-worker-run` changes:

- `--executor-mode auto|native|external`, default `auto`;
- `--executor-command` becomes optional at argument-parse time;
- startup validation requires it only when mode is `external`;
- `auto` without external command is allowed.

Browser worker Compose changes:

- set `--executor-mode auto`;
- do not require `PRODUCTION_OS_WORKER_EXECUTOR_COMMAND` for browser-native jobs;
- retain the variable so operators can provide an external fallback.

General/code/debug/review workers retain external behavior during this phase.

## Data flow

### Native browser job

```
Managed Project / Planner
        |
        v
WorkflowEngine
  injects browser_computer contract
        |
        v
Control Plane queue
        |
        v
Browser RemoteWorkerRunner
  runtime + worktree + heartbeat
        |
        v
NativeExecutor.select()
        |
        v
BrowserNativeHandler
        |
        v
run_browser_turn_loop()
        |
        v
normalized result
        |
        v
RemoteWorkerRunner
  Git verification + complete/fail
        |
        v
WorkflowEngine result propagation
```

### Unsupported job in auto mode

```
NativeExecutor.select() -> unsupported
        |
        +--> external executor configured -> existing subprocess path
        |
        +--> no external executor -> executor_unavailable
```

## Error model

Add deterministic reasons where needed:

- `native_executor_unsupported`
- `native_executor_invalid_request`
- `native_executor_runtime_unavailable`
- `native_executor_failed`
- `executor_unavailable`

Existing reasons remain unchanged for external execution.

Validation failures are separated from runtime failures. Browser schema/host/safety validation failure must not be reported as a generic process failure.

Native browser execution must preserve the existing rule that uncertain side effects are not replayed without positive recovery proof.

## Security boundaries

The native executor must preserve these rules:

- no shell execution derived from handoff content;
- no worker bearer token exposed to task code;
- no arbitrary browser `evaluate`;
- browser navigation remains host allowlisted;
- private-network navigation remains opt-in;
- durable browser paths remain within the runtime workspace;
- repository writes remain inside the assigned worktree;
- control-plane state remains authoritative;
- external fallback is selected only before native side effects begin.

## Backward compatibility

Existing deployments using:

```
remote-worker-run --executor-command ...
```

must continue to work.

Explicit `--executor-mode external` provides old behavior.

The worker executor request schema remains supported and unchanged for external executors.

Jobs without a native contract are unchanged when an external executor is configured.

## Testing strategy

### Unit tests

Add tests for:

- mode parsing and startup validation;
- native-handler selection;
- unsupported native jobs;
- auto fallback selection;
- no fallback after native execution begins;
- browser request validation;
- runtime path derivation;
- persistent browser jobs rejecting missing runtime state;
- cancellation checks between turns.

### Runner integration tests

Prove:

1. browser job + native mode does not start an external subprocess;
2. browser job + auto mode prefers native execution;
3. unsupported job + auto mode starts the external executor when configured;
4. unsupported job + auto mode + no command fails deterministically;
5. native result still passes through worktree Git verification;
6. native failure still reaches the existing control-plane failure path.

### Browser end-to-end test

Use a local deterministic test page and browser worker image:

1. queue a browser-computer job;
2. let the browser worker claim it with no external executor command;
3. execute navigate/snapshot or another bounded non-destructive interaction;
4. produce a normal job result;
5. restart/retry with durable runtime state and verify safe recovery semantics.

### Regression gates

The existing full suite must remain green, including:

- Python 3.11 and 3.12 compatibility;
- Production E2E;
- wheel install;
- standard Docker smoke;
- browser worker smoke;
- mobile Docker validation;
- CLI smoke.

## Delivery sequence

1. Add executor-mode parsing and validation without changing runtime behavior.
2. Add native executor selection API and tests.
3. Add browser-native handler using existing browser loop.
4. Integrate native path into `RemoteWorkerRunner`.
5. Add cancellation/heartbeat coverage for native execution.
6. Update browser worker Compose for executor-less native browser jobs.
7. Add end-to-end browser worker test.
8. Keep external fallback enabled by default in `auto` mode.

## Acceptance criteria

This design is complete when all of the following are true:

- a browser-specialist worker can start with no external executor command;
- a queued browser-computer job can complete through Production OS-native browser execution;
- repository/runtime/worktree safeguards remain active;
- browser persistence and recovery use the existing durable runtime;
- unsupported jobs still use the existing external executor in `auto` mode;
- no runtime failure can trigger a second execution path for the same job;
- existing external deployments remain compatible;
- all existing and new CI checks pass.
