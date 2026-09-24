# Production-OS Release 17 — Managed Projects

## Goal

Track long-running repository goals across multiple immutable workflow generations until explicit human validation.

## Lifecycle

ACTIVE
-> REVIEW_REQUIRED
-> ACTIVE (new instruction/retest)
-> REVIEW_REQUIRED
-> DONE

Terminal workflow failure/cancellation maps to NEEDS_ATTENTION.

## Principles

- Never mutate a completed workflow to add work.
- Every follow-up instruction creates a new workflow generation.
- Prior workflows remain immutable and auditable.
- One current workflow per managed project.
- Follow-up instruction/retest allowed only from REVIEW_REQUIRED or NEEDS_ATTENTION.
- Mark-done requires operator role and exact confirmation.
- Viewer can inspect project state and generation history.
- No paid dependency.

## Schema v15

managed_projects:
- id
- repository
- final_goal
- status
- current_workflow_id
- generation
- created_by
- created_at
- updated_at
- reviewed_at
- completed_at

managed_project_runs:
- id
- project_id
- generation
- kind: initial | instruction | retest
- instruction
- workflow_id
- requested_by
- created_at

SQLite/PostgreSQL parity required.

## API

GET /v1/dashboard/managed-projects
GET /v1/dashboard/managed-projects/{id}

POST /v1/dashboard/managed-projects
{
  repository,
  final_goal
}

POST /v1/dashboard/managed-projects/{id}/instruction
{
  instruction
}

POST /v1/dashboard/managed-projects/{id}/retest

POST /v1/dashboard/managed-projects/{id}/complete
{
  confirm: "MARK_PROJECT_DONE"
}

## Workflow generation

Each generation creates a normal WorkflowEngine workflow with metadata:
- managed_project_id
- managed_project_generation
- managed_project_kind

The single task handoff contains repository, task, final_goal, agent_preference=codex and token_budget=30000.

## Qualification

- restart persistence
- immutable prior workflow generations
- succeeded workflow -> REVIEW_REQUIRED
- failed/cancelled -> NEEDS_ATTENTION
- follow-up instruction creates generation+1
- retest creates generation+1
- concurrent active generation rejected
- mark done operator-only + exact confirmation
- viewer read / worker denied
- SQLite/PostgreSQL parity
- mobile UI regression
- full CI + Python 3.11/3.12 green


## Implemented in current branch

- schema v15 SQLite/PostgreSQL managed_projects + managed_project_runs
- immutable workflow generation model
- ACTIVE / REVIEW_REQUIRED / NEEDS_ATTENTION / DONE lifecycle
- workflow success -> REVIEW_REQUIRED reconciliation
- workflow failure/cancel -> NEEDS_ATTENTION reconciliation
- additional instruction creates generation+1
- retest creates generation+1 with original final goal
- prior workflows remain immutable/auditable
- concurrent/early follow-up rejected
- repository owner/name validation
- restart persistence
- viewer read / worker denied / operator mutation API
- exact MARK_PROJECT_DONE confirmation
- mobile Projects UI for create/instruction/retest/complete
- SQLite/PostgreSQL schema parity and migration coverage
- lifecycle/API/UI regression tests
- README documentation

## Remaining before Release 17 completion

- final CI qualification on complete head
- final diff/security review
- mark PR ready and merge only after green final head
