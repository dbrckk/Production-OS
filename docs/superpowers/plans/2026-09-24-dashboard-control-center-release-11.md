# Dashboard Control Center Release 11 — Launch UX hardening

## Goal

Make the existing smartphone launch flow truly minimal and server-backed: open Production-OS at the root URL, select a repository, enter one instruction, launch.

## Scope

- GET / redirects to /dashboard.
- Keep /health and /healthz as machine health endpoints.
- Add viewer-readable /v1/dashboard/repositories.
- Repository discovery happens server-side through GitHubClient.
- When a GitHub token is present, discover accessible repositories and filter to the configured owner.
- Without a token, fall back to public owner repositories.
- Browser no longer calls api.github.com directly.
- Existing launchWorkflow remains repo + instruction and uses the existing workflow/dispatch APIs.
- No new operator token or setup field.

## Qualification

- root redirect contract
- health endpoints unchanged
- viewer can read repo list; worker forbidden by dashboard authorization
- archived repos excluded
- repository list sorted deterministically
- browser contains no direct api.github.com repository fetch
- launch flow unchanged
- mobile UI tests and full CI green before merge


## Implemented in current branch

- root URL redirects to /dashboard
- /health and /healthz remain JSON health endpoints
- server-backed /v1/dashboard/repositories
- GitHub token-aware accessible repository discovery with public fallback
- archived repositories excluded
- deterministic repository sorting
- browser no longer calls GitHub repository API directly
- GitHub outage degrades to locally observed repositories
- existing repo + instruction launch workflow preserved
- API/UI/redirect regression coverage
- README documentation

## Remaining before Release 11 completion

- final CI qualification
- final diff review
- mark PR ready and merge after green head
