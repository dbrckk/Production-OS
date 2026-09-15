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
- an optional explicit `--rekor-log-id` pin matches the receipt.

The existing generic `--publish-url` witness mechanism remains available and can be used together with Rekor publication.

## Publish a checkpoint

Provide a witness signing key, a dedicated key used to submit the `hashedrekord`, and a trusted Rekor log public key:

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

For an additional identity pin, supply the expected 64-character Rekor log ID:

```bash
production-os transparency-checkpoint-verify \
  --checkpoint checkpoint.json \
  --public-key witness.pub.pem \
  --receipt receipt.json \
  --rekor-log-public-key rekor-log.pub.pem \
  --rekor-log-id <expected-log-id>
```

The command exits with status `0` only when both the Production OS checkpoint signature and the Rekor receipt are valid. A receipt mismatch, altered entry, invalid Merkle path, wrong log identity, or invalid SET returns verification failure.

## Versioning

This adapter is explicitly named `rekor-v1`. Rekor v1 remains the stable public API while Rekor v2 evolves separately, so the provider-specific protocol is kept behind the `TransparencyPublisher` abstraction. A future Rekor v2 publisher can be added without changing the Production OS receipt consumer contract.

## Remaining hardening

The receipt validates entry inclusion and the Rekor SET against a pinned log key. Production OS currently stores the checkpoint text delivered with the inclusion proof but does not yet independently verify the signed tree checkpoint/note or require a quorum of independent witnesses. Those are the next steps for stronger split-view resistance.
