# Security Policy

## Supported versions

Production-OS is pre-1.0. Security fixes are applied to the current `main` branch.

## Reporting

Do not open a public issue containing credentials, tokens or exploitable secret material.

For ordinary non-secret security hardening observations, a GitHub issue is acceptable. For sensitive reports, use GitHub's private vulnerability reporting feature when available.

## Secrets

Production-OS may use `GITHUB_TOKEN` to increase API limits. Tokens must be supplied through environment variables or a secret manager and must never be committed, persisted in portfolio snapshots, copied into agent workspaces or emitted in task handoffs.

## Trust boundaries

- GitHub metadata and repository content are treated as untrusted input.
- Repository text must never be interpreted as executable instructions by the deterministic scanner.
- Destructive repository actions are outside the V0 scanner.
- Future autonomous mutation must require explicit policy and auditable authorization.
