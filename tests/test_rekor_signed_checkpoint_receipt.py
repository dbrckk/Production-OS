import base64
import copy
import hashlib
import json

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, utils

from production_os.transparency_receipts import (
    build_rekor_v1_hashedrekord,
    parse_rekor_v1_receipt,
    verify_rekor_v1_receipt,
)


def _envelope():
    return {
        "checkpoint": {
            "schema_version": "production-os/transparency-witness/v1",
            "root_hash": "a" * 64,
            "entries": 7,
            "created_at": "2026-09-15T17:00:00+00:00",
        },
        "signature": {
            "scheme": "ed25519",
            "key_id": "witness-1",
            "signature": "signed-checkpoint",
        },
    }


def _canonical(value):
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def _leaf_hash(payload: bytes) -> str:
    return hashlib.sha256(b"\x00" + payload).hexdigest()


def _signed_checkpoint(private_key, public_key, root_hash: str) -> str:
    note = (
        "rekor.example - 1\n"
        "1\n"
        f"{base64.b64encode(bytes.fromhex(root_hash)).decode('ascii')}\n"
    )
    der = public_key.public_bytes(
        serialization.Encoding.DER,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    key_hint = hashlib.sha256(der).digest()[:4]
    digest = hashlib.sha256(note.encode("utf-8")).digest()
    signature = private_key.sign(
        digest,
        ec.ECDSA(utils.Prehashed(hashes.SHA256())),
    )
    encoded = base64.b64encode(key_hint + signature).decode("ascii")
    return f"{note}\n— rekor.example {encoded}\n"


def _receipt():
    envelope = _envelope()
    log_private = ec.generate_private_key(ec.SECP256R1())
    log_public = log_private.public_key()
    log_public_pem = log_public.public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode("ascii")
    log_public_der = log_public.public_bytes(
        serialization.Encoding.DER,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    log_id = hashlib.sha256(log_public_der).hexdigest()

    proposed = build_rekor_v1_hashedrekord(
        envelope,
        signature=b"submission-signature",
        public_key_pem="-----BEGIN PUBLIC KEY-----\nsubmission\n-----END PUBLIC KEY-----\n",
    )
    body = _canonical(proposed)
    root_hash = _leaf_hash(body)
    checkpoint = _signed_checkpoint(log_private, log_public, root_hash)
    entry = {
        "logID": log_id,
        "logIndex": 0,
        "integratedTime": 1_789_490_000,
        "body": base64.b64encode(body).decode("ascii"),
    }
    set_signature = log_private.sign(
        _canonical(entry),
        ec.ECDSA(hashes.SHA256()),
    )
    entry["verification"] = {
        "inclusionProof": {
            "logIndex": 0,
            "rootHash": root_hash,
            "treeSize": 1,
            "hashes": [],
            "checkpoint": checkpoint,
        },
        "signedEntryTimestamp": base64.b64encode(set_signature).decode("ascii"),
    }
    receipt = parse_rekor_v1_receipt(
        {"b" * 64: entry},
        envelope=envelope,
    )
    return envelope, receipt, log_public_pem


def test_verified_receipt_rejects_tampered_signed_checkpoint():
    envelope, receipt, log_public_pem = _receipt()
    assert verify_rekor_v1_receipt(
        receipt,
        envelope=envelope,
        log_public_key_pem=log_public_pem,
    ) is True

    tampered = copy.deepcopy(receipt)
    tampered["inclusion_proof"]["checkpoint"] = tampered[
        "inclusion_proof"
    ]["checkpoint"].replace("rekor.example - 1", "evil.example - 1")

    assert verify_rekor_v1_receipt(
        tampered,
        envelope=envelope,
        log_public_key_pem=log_public_pem,
    ) is False
