# Security Policy

## Supported versions

| Version | Supported |
| --- | --- |
| 1.x | Yes |
| < 1.0 | No |

Production-OS 1.0 is the first stable release line. Security fixes are applied to the current supported 1.x line and `main`.

## Reporting

Do not open a public issue containing credentials, tokens or exploitable secret material.

For ordinary non-secret security hardening observations, a GitHub issue is acceptable. For sensitive reports, use GitHub's private vulnerability reporting feature when available.

## Secrets

Production-OS may use `GITHUB_TOKEN` to increase API limits. Tokens must be supplied through environment variables or a secret manager and must never be committed, persisted in portfolio snapshots, copied into agent workspaces or emitted in task handoffs.

## Trust boundaries

- GitHub metadata and repository content are treated as untrusted input.
- Repository text must never be interpreted as executable instructions by the deterministic scanner.
- Destructive or externally privileged actions require explicit policy and auditable authorization.
- Rekor transparency receipts fail closed when configured trust material or consistency evidence is invalid.
- Independent witness quorum strengthens split-view detection, but witness deployment across genuinely independent trust and network domains remains an operational responsibility.
