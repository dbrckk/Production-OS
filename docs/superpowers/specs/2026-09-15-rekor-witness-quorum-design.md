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

- `REKOR_WITNESS_REQUEST_SCHEMA = "production-os/rekor-witness-request/v1"`;
- `REKOR_WITNESS_ATTESTATION_SCHEMA = "production-os/rekor-witness-attestation/v1"`;
- canonical checkpoint-claim/request builders;
- attestation parsing and structural validation;
- Ed25519 signature verification using existing canonical-signature primitives;
- trusted witness registry parsing;
- duplicate detection;
- quorum evaluation;
- explicit split-view detection;
- `RekorWitnessClient` for HTTPS witness requests;
- `RekorWitnessQuorum` for deterministic evaluation of a set of witness results.

This module does not own Rekor RFC6962 verification or local checkpoint-state persistence.

### 2. `rekor_checkpoint_state.py`

Retains responsibility for one-installation continuity:

- bootstrap;
- rollback rejection;
- same-size root equality;
- RFC6962 growth verification;
- compare-and-swap state advancement.

`RekorCheckpointMonitor` is split into two explicit phases:

- `prepare_verified_receipt(receipt)` validates the candidate against current persisted state, fetches/verifies an RFC6962 consistency proof when required, and returns an immutable transition description without mutating trusted state;
- `commit_prepared_transition(transition)` performs the existing bootstrap/CAS write and rechecks concurrency invariants before state advancement.

`observe_verified_receipt(receipt)` remains as a backward-compatible wrapper that calls prepare then commit when quorum is not used.

This separation is mandatory so quorum failure cannot advance trusted state.

### 3. `witness.py`

Keeps the existing generic Production OS checkpoint publication path unchanged. Rekor witness quorum is a separate protocol because it signs Rekor tree identity rather than the local Production OS transparency checkpoint envelope.

### 4. CLI orchestration

`transparency-checkpoint` gains optional quorum configuration:

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

The quorum must be between `1` and the number of configured distinct witnesses. A production example is 2-of-3; Production OS does not hard-code 2-of-3 as a universal policy.

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

The command processing order is fail-closed:

1. build and sign the local Production OS transparency checkpoint;
2. publish it to Rekor;
3. verify the Rekor receipt, SET, signed tree checkpoint, inclusion proof, and pinned log identity;
4. call `prepare_verified_receipt()` to validate local history continuity without mutation;
5. if quorum is configured, request attestations from every configured witness;
6. authenticate and classify all returned attestations;
7. reject any trusted contradictory same-size root observation;
8. require at least the configured number of distinct matching trusted witnesses;
9. persist authenticated witness observations append-only;
10. call `commit_prepared_transition()` to advance local Rekor checkpoint state atomically;
11. write `--receipt-output` and emit the final command result.

If the final local-state commit loses a compare-and-swap race, the command re-reads state. It succeeds only when the committed state is exactly the candidate tree or when the candidate can still be proven consistent from the newly committed state and a new final CAS succeeds. Otherwise it fails closed.

## Persistence

Add an append-only table named `rekor_witness_observations` on SQLite and PostgreSQL with these logical columns:

- `id` database-native primary key;
- `log_id` text, required;
- `origin` text, required;
- `tree_id` text, nullable;
- `tree_size` bigint, required;
- `root_hash` text, required;
- `witness_id` text, required;
- `witness_key_id` text, required;
- `issued_at` text, required;
- `attestation_json` text, required;
- `observed_at` text, required.

A unique constraint on `(log_id, origin, tree_size, root_hash, witness_id, witness_key_id)` prevents duplicate counting/persistence for the same attestation identity while still allowing a contradictory root from the same trusted witness to remain preserved as evidence.

Historical conflicting valid attestations are never overwritten or deleted by normal quorum processing.

The latest local Rekor checkpoint state remains in `rekor_checkpoint_state`; witness history is evidence, not the source of local state truth.

Witness observations are persisted only after cryptographic authentication. Invalid, unauthenticated network payloads are represented only in transient CLI status and are not stored as trusted evidence.

## Failure semantics

When quorum is not configured, behavior is identical to the current `main` branch through the backward-compatible `observe_verified_receipt()` wrapper.

When quorum is configured:

- individual witness network failure does not immediately abort if quorum can still be reached;
- final insufficient quorum fails the command;
- signature or identity mismatch makes that response unusable;
- a valid contradictory trusted witness observation triggers a split-view error immediately;
- malformed responses never count;
- duplicate witness IDs never count twice;
- witness failure never causes fallback to uncorroborated acceptance;
- receipt output is not written on quorum failure;
- trusted checkpoint state is not advanced on quorum failure.

## Concurrency

Two Production OS processes may observe the same or different newer Rekor checkpoints concurrently.

The existing compare-and-swap update remains the final authority for local state advancement. Quorum collection happens before the final state commit. A stale process never overwrites a newer state merely because it independently obtained quorum.

After a CAS conflict, the slower process re-reads current state and must either:

- accept the already-committed identical candidate tree;
- prove the candidate is still a valid append-only advance from current state and retry one bounded CAS;
- or fail on conflict, rollback, or split-view.

There is no unbounded retry loop.

## Configuration validation

Fail command configuration for:

- empty witness registry;
- duplicate witness IDs;
- non-HTTPS URLs;
- invalid public keys;
- expected key ID mismatch;
- quorum <= 0;
- quorum greater than configured witness count;
- witness IDs outside `[A-Za-z0-9._-]{1,128}`.

Plain HTTP is supported only through an explicit Python constructor option used by tests/development; no CLI flag enables insecure witness transport.

Default attestation freshness is 10 minutes with a maximum accepted future skew of 60 seconds. These values are constructor-level policy parameters for tests/embedding in this phase and are not additional CLI flags.

Bearer tokens are read from environment variables and are never persisted in attestation history.

## Observability

CLI result adds a `rekor_witness_quorum` section containing only non-secret evidence:

- required quorum;
- configured witness count;
- valid matching witness IDs;
- invalid/unavailable witness IDs and non-sensitive reason category;
- tree identity;
- status (`disabled`, `satisfied`, `failed`, `split-view`).

No token, private key, PEM body, or raw secret is logged.

## Tests

Test-first implementation covers at minimum:

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
- bounded CAS retry after a concurrent compatible advancement;
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

Update the README transparency milestone status after implementation passes CI.

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
