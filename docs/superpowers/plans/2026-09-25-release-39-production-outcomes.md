# Release 39 — Production outcome summaries

## Goal

Make Managed Project review states explain what the worker actually delivered.

## Outcome contract

ManagedProjectService.get exposes a stable outcome object for the current workflow:

- available
- workflow_status
- summary
- validation_status
- validation_tests
- commit_shas
- artifact_count
- artifact_names
- changed_file_count
- pull_request {number,state}
- completed_at

## Compatibility

The normalizer accepts current and common worker result shapes:

- summary or message
- validation.status / validation.tests
- validation_status / tests
- commit_shas, commits or commit_sha
- pull_request or pr_number / pull_request_number
- changed_files only as an aggregate count
- nested evidence equivalents

No existing worker is required to adopt a new schema.

## UX

Managed Project and Attention cards render:

- delivered result summary
- workflow/validation status
- tests
- shortened commit SHAs
- artifact count
- changed-file count
- PR number/state

Terminal workflow status is still visible when no structured result evidence exists.

## Persistence

Release 32 One-tap E2E is extended to verify summary and validation evidence remain available after a Control Plane restart.

## Completion gate

- outcome normalization tests green
- compact/legacy format compatibility green
- no changed-file paths exposed
- Attention outcome preference tests green
- mobile UI contract tests green
- One-tap restart E2E green
- full Python 3.11/3.12 CI green
- packaging/Docker/CLI smoke green
- branch aligned with main
- final review clean
