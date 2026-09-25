# Release 32 — One-tap production E2E qualification

## Goal

Protect the Release 31 mobile contract with a dedicated end-to-end test that starts from the one-tap launch endpoint.

## Scenario

1. Start a control plane on persistent SQLite storage.
2. Register a remote worker.
3. Launch repository + instruction through POST /v1/dashboard/launch.
4. Verify the server creates a persistent Managed Project with server-owned defaults.
5. Claim, acknowledge and complete the generated job through the remote worker HTTP client.
6. Verify the workflow succeeds and the Managed Project becomes REVIEW_REQUIRED.
7. Stop the HTTP server.
8. Recreate the control plane from the same database.
9. Verify project identity, workflow identity, result usage and review state are restored.

## Completion gate

- dedicated e2e test green
- full non-e2e suite green
- Python 3.11 and 3.12 green
- packaging/docker/CLI smoke green
- final diff review clean
