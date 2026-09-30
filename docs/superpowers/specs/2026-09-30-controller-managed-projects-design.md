# Controller to Managed Projects Design

Date: 2026-09-30

## Status

Proposed architecture for routing autonomous controller actions through the modern Managed Projects execution stack instead of dispatching legacy handoffs directly.

## Problem

Production OS now has two execution paths.

The modern path is:

- Managed Projects;
- WorkflowEngine;
- dynamic planning;
- parallel child agents;
- isolated Git worktrees;
- integration;
- validation and review;
- browser/mobile specialist stages;
- learned-skill reuse;
- durable project memory;
- native browser execution;
- persistent runtime/checkpoint handling.

The controller daemon, however, still uses the older direct path:

`run_control_cycle() -> dispatch_handoff()`

That means 24/7 autonomous portfolio execution bypasses the system's strongest orchestration features.

The controller already solves the right portfolio-level problems:

- repository scanning;
- scoring and action ranking;
- scheduling into NOW/PARALLEL/NEXT/PAUSE/IGNORE;
- capacity allocation;
- governance;
- policy enforcement;
- budgets;
- approvals;
- quarantine;
- emergency stop;
- lease renewal;
- worker/dead-job recovery;
- GitHub reconciliation;
- observability;
- self-healing.

The missing boundary is execution ownership. The controller decides what should run, but still executes through a legacy handoff instead of delegating to Managed Projects.

## Goal

Make Managed Projects the default execution engine for autonomous controller actions while preserving the controller as the portfolio-level scheduler and policy authority.

Target flow:

```
controller daemon
    -> scan / score / schedule
    -> governance / budget / policy gates
    -> autonomous managed-project bridge
    -> ManagedProjectService
    -> WorkflowEngine
    -> planner / parallel agents / worktrees
    -> integration / validation / review / specialists
    -> skill learning / project memory
    -> durable result
```

## Non-goals

This phase does not:

- replace repository scoring or scheduling;
- move governance decisions into ManagedProjectService;
- duplicate dispatch through both legacy and managed paths;
- redesign worker execution;
- replace the controller daemon;
- remove `dispatch_handoff()` from the codebase;
- change the Managed Projects API contract for interactive users;
- add a new database or event bus.

## Architectural Boundary

The controller remains responsible for:

- what work is eligible;
- when work may start;
- portfolio capacity;
- risk/policy/budget approval;
- emergency stop;
- autonomous scheduling;
- recovery orchestration;
- global observability.

ManagedProjectService becomes responsible for:

- how an approved action is decomposed;
- planner execution;
- agent fan-out;
- capability routing;
- isolated worktrees;
- integration;
- validation/review;
- specialist browser/mobile stages;
- project memory;
- learned-skill injection and feedback;
- workflow-level retries.

This separation avoids duplicating orchestration logic.

## Execution Modes

Add a controller execution mode:

```
PRODUCTION_OS_CONTROLLER_EXECUTION_MODE=managed|legacy
```

Default: `managed`.

Semantics:

- `managed`: controller actions create or reuse Managed Projects.
- `legacy`: preserve existing `dispatch_handoff()` behavior.
- no `both` mode.

A dual-dispatch mode is explicitly prohibited because it can create duplicate branches, commits, PRs, side effects, token spend and worker contention.

The CLI should expose the same setting:

```
production-os controller --execution-mode managed
```

Environment remains the deployment default; explicit CLI input wins.

## Autonomous Managed Project Bridge

Add a small controller-side boundary module:

`src/production_os/autonomous_projects.py`

Its purpose is to translate one already-approved controller action into an idempotent Managed Project launch.

It must not contain scheduling, scoring or worker logic.

Proposed interface:

```python
@dataclass(frozen=True, slots=True)
class AutonomousProjectRequest:
    repository: str
    task: str
    rationale: str
    acceptance_criteria: tuple[str, ...]
    priority: float
    token_budget: int
    agent_preference: str
    cooperative: bool
    action_fingerprint: str

@dataclass(frozen=True, slots=True)
class AutonomousProjectLaunch:
    project_id: str
    created: bool
    project: dict

def autonomous_project_id(
    *,
    repository: str,
    action_fingerprint: str,
) -> str: ...

def launch_autonomous_project(
    service: ManagedProjectService,
    request: AutonomousProjectRequest,
) -> AutonomousProjectLaunch: ...
```

The bridge should be deterministic and small enough to unit test independently.

## Stable Idempotency

The controller daemon runs repeatedly. A controller action must therefore map to a stable project identity.

The project id must derive from:

- repository;
- canonical task/action identity;
- acceptance criteria or other material action inputs;
- action generation/fingerprint.

It must not derive from:

- current timestamp;
- scan order;
- worker id;
- controller process id.

Recommended representation:

```
controller-<sha256(canonical-action)[:32]>
```

The canonical fingerprint input should use stable JSON with sorted keys.

Two identical autonomous actions across controller cycles must produce the same `project_id`.

A materially changed action must produce a new identity.

Examples of material change:

- different task;
- different acceptance criteria;
- different repository;
- changed risk-relevant execution intent.

Non-material metadata such as scheduling score drift should not create a new project.

## Project Creation

For a new approved autonomous action, the bridge calls:

```python
ManagedProjectService.create(
    repository=request.repository,
    final_goal=request.task,
    token_budget=request.token_budget,
    agent_preference=request.agent_preference,
    requested_by="controller",
    project_id=stable_project_id,
    cooperative=request.cooperative,
)
```

The existing ManagedProjectService idempotency remains authoritative.

The bridge must not pre-insert Managed Project rows itself.

## Cooperative Mode

Controller-created Managed Projects should default to:

`cooperative=True`

when the required worker fleet can support cooperative execution.

If specialist/cooperative capacity is unavailable, the launch policy must be explicit.

Recommended policy:

1. use cooperative mode when an eligible cooperative fleet exists;
2. otherwise use non-cooperative Managed Project mode;
3. do not fall back to legacy dispatch merely because cooperative workers are absent.

Legacy mode is selected only through controller execution mode, not dynamically after a managed launch attempt.

This prevents the same action from switching execution systems mid-flight.

## Token Budget

The legacy controller currently uses schedule/allocation concepts rather than a Managed Project token budget.

The managed bridge therefore needs a deterministic token-budget policy.

Add controller configuration:

```
PRODUCTION_OS_CONTROLLER_PROJECT_TOKEN_BUDGET
```

and CLI option:

```
--project-token-budget
```

Default should be conservative and bounded.

Recommended default:

`12000`

This budget applies per new autonomous Managed Project, not per controller cycle.

Reusing an existing project must not allocate a second initial budget.

Future adaptive budget policy is out of scope.

## Agent Preference

Controller-created Managed Projects use:

`agent_preference="auto"`

in this phase.

The model router/planning policy remains responsible for lower-level choice.

No controller-specific model selection is introduced.

## Governance and Policy Ordering

The controller's existing governance path remains before project creation.

Managed execution is reached only after existing checks such as:

- emergency stop;
- policy;
- approval;
- budget;
- quarantine;
- rate limiting;
- branch-protection/risk checks where applicable.

The bridge must never weaken or bypass those gates.

Where a legacy gate currently exists only inside `dispatch_handoff()`, that gate must be explicitly preserved before enabling managed mode.

This requirement is a hard migration gate: managed mode cannot become default until parity is proven for all pre-dispatch safety checks.

## Legacy Dispatch Safety-Parity Audit

Before changing the default, implementation must inventory every safety/economic check performed by `dispatch_handoff()`.

For each check, classify it as:

- already enforced before the call in `run_control_cycle()`;
- enforced by ManagedProjectService/WorkflowEngine;
- needs to be moved or duplicated into a controller pre-launch gate.

The implementation must include a regression test for any migrated gate.

No safety check may disappear just because the execution backend changes.

## Existing Project Reuse

When the stable project id already exists:

- do not create a duplicate project;
- return the existing project;
- do not create a second initial workflow;
- do not reset project memory;
- do not reset learned-skill state;
- do not charge a new initial project budget.

The controller journal records a reuse event rather than a new launch event.

## Terminal Projects and Repeated Actions

A completed Managed Project may correspond to an action that appears again in a later scan.

The controller must distinguish:

1. same action, already completed and still satisfied;
2. same action identity but new evidence indicates regression/reappearance;
3. materially changed action.

In this phase:

- exact same fingerprint + terminal successful project -> do not relaunch;
- materially changed fingerprint -> new Managed Project;
- regression/reappearance must change the action fingerprint using stable trigger evidence so it can launch a new project.

The controller must not blindly reopen completed projects.

## Action Fingerprint

The fingerprint payload should include stable, sanitized fields:

```json
{
  "repository": "owner/repo",
  "task": "...",
  "acceptance_criteria": ["..."],
  "trigger_evidence": ["..."],
  "risk_class": "...",
  "schema_version": "production-os/autonomous-action-fingerprint/v1"
}
```

Evidence ordering must be normalized.

Volatile timestamps, scores and lane names are excluded.

## Controller Integration

In `run_control_cycle()`, keep all existing scan/schedule/governance logic.

Replace only the final execution branch.

Pseudo-flow:

```python
if execution_mode == "legacy":
    dispatch_handoff(...)

elif execution_mode == "managed":
    request = build_autonomous_project_request(...)
    project = bridge.launch(...)
    record managed launch/reuse
```

The controller should instantiate ManagedProjectService using the same durable backend when `database_path` is configured.

Recommended construction:

```python
queue = job_queue_for(backend)
workflows = WorkflowEngine(backend, queue)
managed_projects = ManagedProjectService(workflows)
```

Do not instantiate a separate SQLite database.

## File-backed Legacy Controller Mode

The existing controller can run without `database_path` using JSON/file state.

Managed Projects require the structured backend.

Therefore:

- `execution_mode=managed` requires `database_path`;
- if managed mode is requested without a database, fail startup/cycle validation with a clear configuration error;
- `legacy` remains available for file-backed deployments.

Do not silently switch to legacy mode when managed mode is misconfigured.

## Worker Fleet Detection

The controller needs a simple cooperative decision.

Reuse the same principle as `ControlPlane.cooperative_worker_fleet_available()`, but avoid creating a full ControlPlane instance inside the controller.

Add a shared helper in an appropriate worker/capability module so both ControlPlane and controller can use one implementation.

The helper should answer whether the online fleet supports:

- general cooperative execution;
- browser specialist requirement;
- mobile specialist requirement.

This avoids duplicated capability logic.

## Result and Progress Ownership

The controller does not poll each Managed Project to completion inside the same control cycle.

A control cycle launches/reuses projects and returns.

Workers and WorkflowEngine progress them asynchronously.

Later controller cycles may inspect project status for observability and scheduling decisions.

This keeps controller cycles bounded and avoids blocking the daemon on long tasks.

## Capacity Semantics

The existing scheduler's NOW/PARALLEL capacity remains the admission decision.

A managed project counts as admitted when launched or reused as active.

The controller must avoid filling future cycles with duplicate admitted actions.

Stable idempotency handles duplicate launch attempts, but scheduler accounting should also identify active Managed Projects to avoid misleading resource allocation.

Initial implementation may annotate the cycle result with managed project statuses without rewriting the scheduler algorithm.

## Journal and Observability

Add controller journal events:

- `managed-project-created`;
- `managed-project-reused`;
- `managed-project-skipped-terminal`;
- `managed-project-launch-error`.

Each event includes:

- repository;
- task;
- project_id;
- action_fingerprint;
- project status where available.

Do not log raw secrets or full sensitive handoff payloads.

The control-cycle response gains:

```json
{
  "managed_projects": [...]
}
```

Legacy mode retains:

```json
{
  "dispatches": [...]
}
```

For compatibility, both keys may exist, but only one execution mechanism is populated per cycle.

## Failure Semantics

Managed launch failure must not trigger legacy fallback in the same cycle.

Reasons:

- duplicate side effects;
- inconsistent policy accounting;
- ambiguity over execution ownership.

Instead:

1. record `managed-project-launch-error`;
2. increment the controller dispatch-failure metric;
3. allow the next daemon cycle to retry the same stable project identity if safe.

Idempotency handles partial initialization cases using existing ManagedProjectService behavior.

## Emergency Stop

Emergency stop remains checked before managed project creation.

When emergency stop becomes active after a project is already launched, existing queue/worker/control-plane cancellation mechanisms remain responsible for active work.

This phase does not add a new Managed Project-wide kill switch.

## Budget and Rate-Limit Accounting

Controller-level budget/rate-limit gates must remain effective in managed mode.

The implementation must explicitly decide where accounting occurs:

- admission charge before Managed Project creation;
- or equivalent Managed Project-aware ledger entry.

It must not charge again every daemon cycle when the same project is reused.

A stable project id should be used as the idempotency key for controller-side admission accounting where supported.

## Migration Strategy

Phase 1:
- add bridge;
- add `managed|legacy` configuration;
- keep deployment default as legacy while parity tests run.

Phase 2:
- prove policy/budget/rate-limit parity;
- add controller-managed E2E coverage;
- switch code/config default to managed.

Phase 3:
- observe production behavior;
- keep legacy mode available as explicit rollback.

The repository-level design target is managed-by-default, but implementation should make the default switch only in the commit where parity tests are green.

## Security Boundaries

The bridge must:

- accept only controller-produced actions;
- validate repository format;
- canonicalize fingerprint content;
- never include secrets in project ids or journal events;
- preserve governance before launch;
- never invoke both execution systems;
- never silently downgrade managed mode to legacy;
- reuse the same durable backend;
- rely on ManagedProjectService for project-row idempotency.

## Testing Strategy

### Unit tests

Add tests for:

- deterministic project id;
- fingerprint stable under evidence ordering;
- fingerprint changes on material action changes;
- bridge creates Managed Project once;
- repeated identical launch reuses project;
- completed identical project is skipped;
- managed mode requires database backend;
- legacy mode preserves existing behavior;
- managed launch failure never invokes legacy dispatch.

### Safety parity tests

Inventory `dispatch_handoff()` and prove managed admission preserves:

- emergency stop;
- rate limits;
- approvals;
- policy;
- budgets;
- quarantine;
- required risk/branch-protection logic.

Each parity check should fail RED before migration if not already applied before dispatch.

### Controller integration tests

Prove:

1. schedule NOW/PARALLEL action creates Managed Project;
2. second cycle does not duplicate project/workflow;
3. cooperative worker fleet selects cooperative Managed Project;
4. unavailable cooperative fleet still uses non-cooperative managed execution;
5. browser/mobile actions preserve specialist requirements;
6. launch failure records journal/metrics but does not legacy-dispatch;
7. legacy execution mode still calls `dispatch_handoff()`.

### Daemon recovery test

Run multiple daemon cycles against one durable database:

- cycle 1 launches managed project;
- controller process is recreated;
- cycle 2 sees the same action;
- same project id is reused;
- no duplicate initial workflow/jobs are created.

### Full regression

All existing gates must remain green:

- controller daemon tests;
- managed-project tests;
- dynamic agent tests;
- worker recovery tests;
- Python 3.11/3.12;
- Production E2E;
- wheel install;
- Docker/controller smoke tests;
- browser/mobile worker smoke checks.

## Acceptance Criteria

The design is complete when:

- autonomous controller actions default to Managed Projects after safety parity is proven;
- repeated daemon cycles cannot duplicate the same autonomous action;
- Managed Projects use the same durable database as the controller;
- cooperative planning/parallel agents/worktrees are available to autonomous controller work;
- project memory and learned skills participate naturally through WorkflowEngine;
- legacy mode remains explicit and functional;
- no cycle can invoke managed and legacy execution for the same action;
- managed launch errors never cause same-cycle legacy fallback;
- existing governance/budget/rate-limit safety is preserved;
- daemon restart does not duplicate active work;
- all relevant CI and E2E tests pass.
