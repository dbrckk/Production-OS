# Changelog

All notable changes to Production-OS are documented in this file.

## [1.0.0] - 2026-09-15

First stable release of Production-OS.

### Core control plane

- portfolio discovery, maturity scoring, classification, prioritization, scheduling and resource allocation;
- persistent runtime state with leases, retries, circuit breakers, cooldowns and idempotency guards;
- authenticated HTTP control plane and capability-aware remote workers;
- durable SQLite and PostgreSQL backends;
- workflow DAG execution, artifacts, execution feedback, incident history and release promotion/rollback.

### Supply-chain and trust

- signed validation attestations and release provenance;
- trusted-builder enforcement and SLSA provenance verification;
- append-only local transparency log;
- Rekor v1 publication and offline receipt verification;
- signed Rekor tree checkpoint validation and RFC6962 inclusion/consistency proofs;
- persistent checkpoint rollback/split-view protection;
- optional independent Ed25519 witness quorum with fail-closed conflict detection.

### Operations

- Docker and Docker Compose deployment paths;
- authenticated dashboard/control-plane endpoints;
- PostgreSQL production path;
- health, metrics and structured observability outputs;
- production-stack E2E qualification covering PostgreSQL, HTTP control plane, remote worker, workflow execution, artifact registration, attestation, release promotion and transparency verification.

### Release qualification

The canonical CI gate compiles the package, runs the complete non-E2E test suite, runs the production-stack E2E scenario against PostgreSQL, builds Python distribution artifacts, installs and smoke-tests the wheel in an isolated virtual environment, builds and smoke-tests the Docker image, and verifies the installed CLI.

### Operational note

Independent Rekor witnesses should be operated across genuinely independent trust and network domains for stronger ecosystem-wide split-view resistance. This is a deployment property rather than a missing receipt-format feature.
