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

The command prints the signed checkpoint envelope and the verified Rekor receipt. `--output` stores the checkpoint envelope; `--receipt-output` stores the Rekor receipt separately.

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

The remaining split-view hardening is checkpoint consistency checking across observations and/or a quorum of independent witnesses. Those mechanisms can build on the now-authenticated signed tree checkpoints without changing the receipt format.
