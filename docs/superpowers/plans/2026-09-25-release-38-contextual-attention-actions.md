# Release 38 — Contextual attention actions

## Goal

Turn the attention-first mobile dashboard into an operational command surface while preserving existing safety and authorization contracts.

## Server feed

Attention items may expose contextual action metadata:

- REVIEW_REQUIRED managed project:
  - verify
  - complete
- NEEDS_ATTENTION / failed managed validation:
  - verify
- open incident:
  - acknowledge
- incident playbook:
  - available/fallback remediation suggestions only

Viewer access can read action metadata, but all mutations continue to require operator credentials.

## Deep links

Attention navigation carries a target id in the dashboard query.

Managed Projects and Autopilot:

- highlight the exact target card
- scroll the target into view
- preserve the target across URL navigation

## Noise control

Blocked jobs remain fully counted in summary metrics, but only the first eight individual blocked-job cards are rendered in the attention feed.

## Safety

- MARK_PROJECT_DONE exact confirmation remains required
- incident remediation reuses existing server-side playbook availability checks
- worker-control audit and remediation events remain unchanged
- no arbitrary endpoint or action is accepted from browser metadata
- viewer cannot execute proposed actions

## Completion gate

- contextual action aggregation tests green
- blocked-job cap/total tests green
- API authorization regression green
- UI action/deep-link contracts green
- full non-E2E suite green
- Production E2E green
- Python 3.11 and 3.12 green
- packaging/Docker/CLI smoke green
- final diff/review clean
