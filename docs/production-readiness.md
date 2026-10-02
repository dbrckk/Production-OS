# Production readiness

Production-OS 1.0 is qualified as a stable release when the canonical CI workflow is green on the exact release commit.

## Release gate

The release commit must pass all of the following on GitHub Actions:

1. install the development and PostgreSQL dependency sets;
2. compile every module under `src`;
3. pass the complete non-E2E pytest suite on Python 3.11 and Python 3.12;
4. pass the production-stack E2E test against PostgreSQL 16 on Python 3.12;
5. build both Python wheel and source distribution artifacts;
6. install the wheel into an isolated virtual environment and run the installed CLI;
7. build the production Docker image and run the image CLI smoke test;
8. run the editable-install CLI smoke test.

The E2E test uses an isolated PostgreSQL database and exercises a real HTTP control plane, authenticated operator and worker identities, remote claim/ack/complete, a dependency-ordered workflow, artifact registration, validation attestation, release promotion, release verification, transparency verification and final control-plane statistics.

## Supported runtime paths

- Python 3.11 and 3.12, both covered by the compatibility gate
- Python 3.12 in the production container and production-stack E2E gate
- SQLite for local/single-node durable state
- PostgreSQL for distributed/production state
- Docker / Docker Compose deployment

## Security and trust expectations

Production-OS treats repository content and GitHub metadata as untrusted input and keeps privileged/destructive behavior behind explicit policy and auditable authorization.

Supply-chain controls include signed validation attestations, provenance verification, trusted-builder enforcement, local transparency, Rekor v1 receipts, signed tree checkpoints, RFC6962 inclusion and consistency verification, rollback protection and optional independent witness quorum.

Rekor witness independence is an operational requirement: deployments that rely on quorum for split-view resistance should place witnesses in genuinely independent administrative and network domains.

## Stable-release policy

The supported stable line is 1.x. Changes that break documented CLI, persistence, receipt or API contracts require a new major version. Security and correctness fixes may ship in compatible 1.x releases after passing the same canonical qualification gate.

A release must not be declared stable from a branch-only result. The exact merged release commit on `main` must be green before a tag or GitHub Release is created.


## Generated-context head qualification

Repository-standards may advance `main` after an application merge by committing regenerated `.ai/**` context. Those generated-only commits are part of the branch history, so Production-OS treats the resulting commit as the new release candidate rather than relying on the CI result of its parent.

The repository-standards workflow therefore compares the post-generation `main` head with the triggering commit. If generated context advanced the branch, it explicitly dispatches the canonical `ci.yml` workflow against the new head. A generated-only commit must not be considered release-qualified until that exact-head CI succeeds.

Generated unified AI-context commits are marked `[skip render]`. They stage only `.ai/**`, so this prevents redundant Render rebuilds without suppressing deployment of application, workflow, configuration, or documentation changes that can affect the production artifact.
