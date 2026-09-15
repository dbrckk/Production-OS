# Rekor witness quorum hardening design

Date: 2026-09-15
Status: approved design, implementation pending
Scope: P17 external transparency hardening

## Context

Production OS already verifies Rekor v1 receipts cryptographically, authenticates Rekor signed tree checkpoints with a pinned Rekor log public key, persists the latest authenticated checkpoint in SQLite/PostgreSQL, rejects rollback and same-size root conflicts, and verifies RFC6962 consistency proofs before advancing local trust state.

That protects one Production OS installation across time, but it does not detect a malicious or compromised transparency service serving mutually consistent yet different histories to different Production OS installations. The remaining gap is cross-observer split-view detection.

## Goal

Add an optional quorum of independent cryptographic witnesses for authenticated Rekor checkpoints. When enabled, Production OS must require enough distinct trusted witnesses to sign the same Rekor tree identity before accepting the new checkpoint as externally corroborated.

The feature must preserve current behavior when no quorum is configured and become fail-closed once quorum enforcement is enabled.

## Non-goals

This phase does not implement peer discovery, gossip routing, a public witness directory, Byzantine consensus, blockchain anchoring, Rekor v2, or automatic witness infrastructure deployment. It also does not change the existing Rekor receipt format.

## Security properties

A quorum observation is bound to the exact tuple:

- Rekor provider: `rekor-v1`
- Rekor `log_id`
- signed-note `origin`
- optional Rekor `tree_id`
- `tree_size`
- `root_hash`

Each accepted witness attestation must additionally bind:

- witness ID
- attestation schema version
- issued timestamp
- Ed25519 signing key ID

Production OS must reject:

- unknown witnesses;
- unknown or mismatched signing keys;
- malformed signatures;
- stale/future-dated attestations outside configured skew/freshness limits;
- duplicate attestations from the same witness;
- attestations for another log/origin/tree size/root;
- mixed roots for the same `(log_id, origin, tree_size)`;
- insufficient distinct valid witnesses;
- responses that cannot be authenticated.

A contradictory valid attestation from a trusted witness for the same `(log_id, origin, tree_size)` is a split-view signal and must fail closed even if another root independently reaches quorum.

## Architecture

### 1. `rekor_witness_quorum.py`

New isolated module responsible for witness-specific logic.

It defines:

- `REKOR_WITNESS_ATTESTATION_SCHEMA = "production-os/rekor-witness-attestation/v1"`;
- a canonical checkpoint-claim builder;
- attestation parsing and structural validation;
- Ed25519 signature verification using existing canonical-signature primitives;
- trusted witness registry parsing;
- duplicate detection;
- quorum evaluation;
- explicit split-view detection;
- a provider-neutral HTTP witness client interface used by the CLI orchestration layer.

This module must not own Rekor RFC6962 verification or local checkpoint persistence.

### 2. `rekor_checkpoint_state.py`

Retains responsibility for one-installation continuity:

- bootstrap;
- rollback rejection;
- same-size root equality;
- RFC6962 growth verification;
- compare-and-swap state advancement.

It exposes the authenticated checkpoint identity to the quorum layer but does not absorb witness policy.

### 3. `witness.py`

Keeps the existing generic Production OS checkpoint publication path unchanged. Rekor witness quorum is a separate protocol because it signs Rekor tree identity rather than the local Production OS transparency checkpoint envelope.

### 4. CLI orchestration

`transparency-checkpoint` gains optional quorum configuration.

Recommended configuration surface:

- `--rekor-witness-config <json>`
- `--rekor-witness-quorum <int>`

The JSON configuration maps each witness ID to:

- HTTPS endpoint;
- Ed25519 public key;
- optional expected key ID;
- optional bearer-token environment variable;
- optional timeout.

Example:

```json
{
  "witnesses": {
    "witness-a": {
      "url": "https://witness-a.example/v1/rekor/checkpoint",
      "public_key": "-----BEGIN PUBLIC KEY-----\n...\n-----END PUBLIC KEY-----"
    },
    "witness-b": {
      "url": "https://witness-b.example/v1/rekor/checkpoint",
      "public_key": "-----BEGIN PUBLIC KEY-----\n...\n-----END PUBLIC KEY-----"
    },
    "witness-c": {
      "url": "https://witness-c.example/v1/rekor/checkpoint",
      "public_key": "-----BEGIN PUBLIC KEY-----\n...\n-----END PUBLIC KEY-----"
    }
  }
}
```

A quorum is enabled only when both a witness configuration and positive quorum are supplied. Supplying only one is a configuration error.

The quorum must be between `1` and the number of configured distinct witnesses. A production example is 2-of-3; Production OS must not hard-code 2-of-3 as a universal policy.

## Witness request/response protocol

Production OS sends the exact authenticated Rekor checkpoint claim as canonical JSON:

```json
{
  "schema_version": "production-os/rekor-witness-request/v1",
  "provider": "rekor-v1",
  "log_id": "...",
  "origin": "...",
  "tree_id": "...",
  "tree_size": 123,
  "root_hash": "...",
  "checkpoint": "..."
}
```

The witness responds with:

```json
{
  "schema_version": "production-os/rekor-witness-attestation/v1",
  "witness_id": "witness-a",
  "claim": {
    "provider": "rekor-v1",
    "log_id": "...",
    "origin": "...",
    "tree_id": "...",
    "tree_size": 123,
    "root_hash": "..."
  },
  "issued_at": "2026-09-15T18:00:00+00:00",
  "signature": {
    "algorithm": "ed25519",
    "key_id": "sha256:...",
    "signature": "..."
  }
}
```

The signed payload is the complete attestation object without its `signature` field, using the repository's existing canonical JSON signing format.

The witness endpoint may persist the complete signed Rekor checkpoint independently before returning the attestation. Production OS does not trust that persistence claim; it trusts only the configured witness identity and signature.

## Processing order

The command processing order is deliberately fail-closed:

1. build and sign the local Production OS transparency checkpoint;
2. publish it to Rekor;
3. verify the Rekor receipt, SET, signed tree checkpoint, inclusion proof, and pinned log identity;
4. compare the authenticated Rekor tree against the locally persisted Rekor checkpoint state and verify RFC6962 consistency if it grew;
5. if quorum is configured, request attestations from all configured witnesses;
6. authenticate every returned attestation that is usable;
7. reject any trusted contradictory same-size root observation;
8. require at least the configured number of distinct matching trusted witnesses;
9. persist the witness observation history;
10. advance the local Rekor checkpoint state;
11. write `--receipt-output` and emit the final command result.

To preserve the current compare-and-swap safety model, implementation may need to split `RekorCheckpointMonitor.observe_verified_receipt()` into a non-mutating validation/planning phase and a final atomic commit phase. The important invariant is that quorum failure must not advance the trusted checkpoint or persist the new receipt output.

## Persistence

Add an append-only witness observation table for SQLite and PostgreSQL. Suggested logical fields:

- `log_id`
- `origin`
- `tree_id`
- `tree_size`
- `root_hash`
- `witness_id`
- `witness_key_id`
- `issued_at`
- `attestation_json`
- `observed_at`

Uniqueness must prevent one witness from counting twice for the same tree identity.

Historical conflicting valid attestations must remain queryable for audit and incident analysis; they must not be overwritten by later observations.

The latest local Rekor checkpoint state remains in `rekor_checkpoint_state`; witness history is evidence, not the source of local state truth.

## Failure semantics

When quorum is not configured, behavior is identical to the current `main` branch.

When quorum is configured:

- individual witness network failure does not immediately abort if quorum can still be reached;
- final insufficient quorum fails the command;
- signature or identity mismatch makes that response unusable and auditable;
- a valid contradictory trusted witness observation triggers a split-view error immediately;
- malformed responses never count;
- duplicate witness IDs never count twice;
- witness failure never causes fallback to uncorroborated acceptance;
- receipt output is not written on quorum failure;
- trusted checkpoint state is not advanced on quorum failure.

## Concurrency

Two Production OS processes may observe the same or different newer Rekor checkpoints concurrently.

The existing compare-and-swap update remains the final authority for local state advancement. Quorum collection happens before the final state commit. If another process advances state first, the slower process must re-read state and either:

- accept the already-committed same tree;
- prove consistency from the newly committed state before retrying advancement;
- or fail on a conflict/rollback/split-view.

A stale process must never overwrite a newer state merely because it independently obtained quorum.

## Configuration validation

Fail startup/command parsing for:

- empty witness registry;
- duplicate witness IDs;
- non-HTTPS URLs except an explicit test/development escape hatch in Python-only configuration;
- invalid public keys;
- expected key ID mismatch;
- quorum <= 0;
- quorum greater than configured witness count;
- witness IDs that do not match a conservative identifier pattern.

Bearer tokens are read from environment variables and are never persisted in attestation history.

## Observability

CLI result adds a `rekor_witness_quorum` section containing only non-secret evidence:

- required quorum;
- configured witness count;
- valid matching witness IDs;
- invalid/unavailable witness IDs and non-sensitive reason category;
- tree identity;
- status (`disabled`, `satisfied`, `failed`, `split-view`).

No token, private key, or raw secret may be logged.

## Tests

Test-first implementation must cover at minimum:

- quorum disabled preserves current behavior;
- 2-of-3 success;
- 3-of-3 success;
- insufficient quorum;
- one offline witness with quorum still reached;
- unknown witness;
- duplicate witness response;
- invalid signature;
- wrong key ID;
- wrong log ID;
- wrong origin;
- wrong tree ID;
- wrong tree size;
- wrong root hash;
- stale attestation;
- excessive future timestamp;
- same-size contradictory trusted root causes split-view failure;
- contradictory witness blocks acceptance even if another root reaches numeric quorum;
- witness history persistence on SQLite;
- witness history persistence on PostgreSQL;
- no trusted-state advancement on quorum failure;
- no receipt-output write on quorum failure;
- successful state advancement after quorum;
- concurrent state advancement race;
- CLI configuration validation;
- HTTPS enforcement;
- bearer-token redaction/no persistence;
- full existing test suite regression.

## Documentation

Update `docs/transparency-rekor.md` with:

- the cross-observer threat model;
- witness config format;
- quorum examples;
- exact fail-closed behavior;
- operational guidance for independent administrative domains;
- warning that three endpoints controlled by one operator are not three independent trust domains.

Update the README P16/P17 transparency status after implementation passes CI.

## Acceptance criteria

The feature is complete only when all of the following are true:

1. Existing no-quorum Rekor behavior remains backward compatible.
2. Configured quorum requires N distinct valid trusted witness signatures over the exact authenticated Rekor tree identity.
3. A valid trusted contradictory root for the same tree size is detected as split-view.
4. Quorum failure cannot advance local Rekor trust state.
5. Quorum failure cannot write the new receipt output.
6. Witness evidence is append-only and supported on SQLite and PostgreSQL.
7. Concurrent observers cannot overwrite newer state.
8. CLI output exposes useful non-secret quorum evidence.
9. Documentation describes deployment and independence requirements.
10. Compile, complete test suite, PostgreSQL-backed coverage, and CLI smoke test pass in CI.

## Follow-on hardening after this phase

Once signed witness quorum is complete, the remaining transparency work is optional higher-order hardening rather than a prerequisite for the core quorum design:

- active gossip exchange between witness services;
- automated witness discovery/rotation;
- witness health/SLO monitoring;
- Rekor v2 adapter when its deployment/API target is appropriate;
- long-term external archival of witness evidence;
- independent interoperability tests against real deployed witness implementations.
