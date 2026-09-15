# External transparency receipts with Rekor v1

Production OS can anchor a signed local transparency checkpoint in a Rekor v1 log and persist a receipt that can be verified later without trusting the original HTTP response.

## Security model

The Rekor integration binds the complete signed Production OS checkpoint envelope to a `hashedrekord` entry using SHA-256. A successful receipt records the Rekor entry UUID, log ID, log index, integrated time, encoded log entry, RFC6962 inclusion proof, tree checkpoint text, and signed entry timestamp (SET).

Receipt verification is fail-closed when a trusted Rekor log public key is supplied. Production OS checks all of the following:

- the stored checkpoint digest matches the exact checkpoint envelope being verified;
- the Rekor entry is a `hashedrekord` carrying that digest;
- the RFC6962 Merkle inclusion path resolves to the advertised root hash;
- the receipt log index matches the inclusion proof index;
- the Rekor `logID` matches SHA-256 of the pinned log public key SubjectPublicKeyInfo DER;
- the Rekor signed entry timestamp authenticates the immutable log entry metadata;
- the Rekor signed tree checkpoint authenticates the proof tree size and root hash with the same pinned log key;
- the current signed tree is consistent with the last authenticated tree state stored by Production OS;
- when an independent witness quorum is configured, enough pinned witnesses sign the exact same Rekor log identity, note origin, tree size, and root hash;
- an optional explicit `--rekor-log-id` pin matches the receipt.

The existing generic `--publish-url` witness mechanism remains available and can be used together with Rekor publication.

## Publish a checkpoint

Provide a witness signing key, a dedicated PKIX-compatible ECDSA or RSA private key used to submit the `hashedrekord`, and a trusted Rekor log public key. Rekor v1 `hashedrekord` does not support Ed25519 submission signatures because only the artifact digest, not the original message, is sent to Rekor; Production OS rejects Ed25519 for this path instead of allowing a request Rekor cannot verify.

```bash
production-os transparency-checkpoint \
  --database state.sqlite \
  --private-key witness.pem \
  --output checkpoint.json \
  --rekor-url https://rekor.sigstore.dev \
  --rekor-private-key rekor-submit.pem \
  --rekor-log-public-key rekor-log.pub.pem \
  --receipt-output receipt.json
```

`--rekor-log-public-key` is intentionally required when publishing through the CLI. The key should be obtained and pinned through a trusted channel rather than learned from the publication response itself. This prevents a forged endpoint from returning a self-consistent Merkle proof under an attacker-controlled identity.

The command prints the signed checkpoint envelope, the verified Rekor receipt, and the checkpoint-state result. `--output` stores the checkpoint envelope; `--receipt-output` stores the Rekor receipt separately.

## Persistent checkpoint consistency

When Rekor publication succeeds, Production OS stores the latest authenticated Rekor tree checkpoint in the database selected by `--database`. The checkpoint state is keyed by Rekor log identity and signed-note origin, and works with both SQLite and PostgreSQL backends.

The state transition is fail-closed:

- the first authenticated tree is inserted as the bootstrap state;
- observing the same tree size again requires exactly the same root hash;
- observing a smaller tree size is rejected as a rollback;
- observing a larger tree size triggers a Rekor v1 `/api/v1/log/proof` request and RFC6962 consistency verification from the stored tree to the new tree;
- a mismatched root or invalid consistency path is rejected;
- database updates use conditional writes so a slow observer cannot overwrite a newer checkpoint written concurrently.

Checkpoint-state validation happens before `--receipt-output` is written. Therefore a split view, rollback, invalid consistency proof, or concurrent stale write prevents the new receipt from becoming persisted output.

## Independent witness quorum

Local consistency can prove that one Production OS installation is being shown an append-only history, but it cannot by itself detect a log that presents different append-only histories to different observers. `--rekor-witness-config` adds an optional quorum of independently operated witnesses.

Example `witnesses.json`:

```json
{
  "threshold": 2,
  "witnesses": [
    {
      "id": "witness-eu-1",
      "url": "https://w1.example/observe",
      "public_key_path": "keys/w1.pub.pem"
    },
    {
      "id": "witness-us-1",
      "url": "https://w2.example/observe",
      "public_key_path": "keys/w2.pub.pem"
    },
    {
      "id": "witness-ap-1",
      "url": "https://w3.example/observe",
      "public_key_path": "keys/w3.pub.pem"
    }
  ]
}
```

Public-key paths are resolved relative to the configuration file. An inline `public_key` value is also accepted. Witness IDs must be unique, and the threshold must be between one and the number of configured witnesses.

Enable the quorum when publishing:

```bash
production-os transparency-checkpoint \
  --database state.sqlite \
  --private-key witness.pem \
  --rekor-url https://rekor.sigstore.dev \
  --rekor-private-key rekor-submit.pem \
  --rekor-log-public-key rekor-log.pub.pem \
  --rekor-witness-config witnesses.json \
  --receipt-output receipt.json
```

For each configured endpoint, Production OS sends a `production-os/rekor-witness-request/v1` JSON request containing the Rekor log ID, signed-note origin, tree size, and root hash. A compatible endpoint returns an Ed25519-signed `production-os/rekor-witness-observation/v1` object carrying the same fields plus its configured witness ID.

The client verifies each response against the public key pinned for that witness ID. Unreachable endpoints, malformed responses, unknown identities, duplicate identities, and invalid signatures do not count toward the threshold. A cryptographically valid observation for the same log, origin, and tree size but a different root is treated as a split-view conflict and fails closed even if the numerical threshold would otherwise be satisfied.

When quorum mode is enabled, quorum validation runs before the local Rekor checkpoint state is advanced and before `--receipt-output` is written. A failed quorum therefore cannot poison the trusted local checkpoint state or persist a newly accepted receipt. Received signed observations and their verdicts are stored in `rekor_witness_observations` for audit.

## Verify offline

```bash
production-os transparency-checkpoint-verify \
  --checkpoint checkpoint.json \
  --public-key witness.pub.pem \
  --receipt receipt.json \
  --rekor-log-public-key rekor-log.pub.pem
```

The offline CLI invokes the same signed-tree-checkpoint verification as the receipt API, so a pinned Rekor log key authenticates both the SET and the tree state carried by the inclusion proof.

For an additional identity pin, supply the expected 64-character Rekor log ID:

```bash
production-os transparency-checkpoint-verify \
  --checkpoint checkpoint.json \
  --public-key witness.pub.pem \
  --receipt receipt.json \
  --rekor-log-public-key rekor-log.pub.pem \
  --rekor-log-id <expected-log-id>
```

The command exits with status `0` only when both the Production OS checkpoint signature and the Rekor receipt are valid. A receipt mismatch, altered entry, invalid Merkle path, wrong log identity, invalid SET, or invalid signed tree checkpoint returns verification failure.

## Signed tree checkpoints

Production OS parses the Rekor signed-note format and verifies the tree checkpoint using the pinned Rekor log public key. It validates the four-byte public-key hint derived from SubjectPublicKeyInfo, authenticates ECDSA, RSA, or Ed25519 note signatures, and requires the signed tree size and root hash to match the RFC6962 inclusion proof exactly.

Receipt parsing remains independent of trust configuration, but receipt verification requires this signed checkpoint whenever `log_public_key_pem` is supplied. This means a valid SET plus a mathematically valid inclusion proof is no longer enough if the signed tree state has been altered.

## Versioning

This adapter is explicitly named `rekor-v1`. Rekor v1 remains the stable public API while Rekor v2 evolves separately, so the provider-specific protocol is kept behind the `TransparencyPublisher` abstraction. A future Rekor v2 publisher can be added without changing the Production OS receipt consumer contract.

## Remaining hardening

Production OS now authenticates each Rekor tree, verifies append-only consistency across local observations, and can require an independent signed quorum before accepting a newly published tree. Further hardening is operational rather than required for the receipt format: deploy witnesses across genuinely independent trust and network domains, monitor witness availability and disagreement, and add gossip between witness operators where stronger ecosystem-wide split-view detection is required.
