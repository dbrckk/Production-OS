# Release 40 — Review guidance

## Goal

Translate Managed Project lifecycle and production outcome evidence into a clear next step for mobile review without automatically approving or mutating projects.

## Server contract

ManagedProjectService.get adds review_guidance:

- action_required
- state
- headline
- detail
- primary_action
- available_actions
- evidence_level
- evidence_count
- evidence flags
- validation_passed (true / false / null)

## Evidence quality

Six observable categories are counted:

1. result summary
2. validation status
3. test evidence
4. commit evidence
5. artifact or changed-file evidence
6. pull request evidence

Levels:

- none: 0
- minimal: 1–2
- partial: 3–4
- rich: 5–6

## Lifecycle guidance

- ACTIVE: production in progress, no operator action
- NEEDS_ATTENTION: correction/retest guidance
- REVIEW_REQUIRED: evidence review and explicit human decision
- DONE: no action required

A passed validation never marks the project DONE automatically.

## UX

Managed Projects and Attention render:

- Prochaine étape
- explanatory detail
- evidence quality and count

Existing contextual actions remain the only mutation paths.

## Completion gate

- guidance state tests green
- no false validation pass for missing evidence
- One-tap restart E2E guidance persistence green
- Attention propagation tests green
- mobile UI rendering tests green
- full 3.11/3.12 CI green
- Production E2E green
- packaging/Docker/CLI smoke green
- branch aligned with main
- review clean
