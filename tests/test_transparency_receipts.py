import base64
import hashlib
import json

import pytest
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, utils

from production_os.signing import generate_keypair
from production_os.transparency_receipts import (
    RECEIPT_SCHEMA,
    RekorV1Publisher,
    TransparencyReceiptError,
    build_rekor_v1_hashedrekord,
    checkpoint_digest,
    parse_rekor_v1_receipt,
    verify_inclusion_proof,
    verify_rekor_signed_entry_timestamp,
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


def _leaf_hash(payload: bytes) -> str:
    return hashlib.sha256(b"\x00" + payload).hexdigest()


def _rekor_signing_private_pem() -> str:
    private_key = ec.generate_private_key(ec.SECP256R1())
    return private_key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    ).decode("ascii")




def test_checkpoint_digest_is_deterministic():
    envelope = _envelope()
    reordered = {
        "signature": envelope["signature"],
        "checkpoint": envelope["checkpoint"],
    }

    assert checkpoint_digest(envelope) == checkpoint_digest(reordered)
    assert len(checkpoint_digest(envelope)) == 64


def test_build_rekor_v1_hashedrekord_binds_checkpoint_digest():
    envelope = _envelope()
    proposed = build_rekor_v1_hashedrekord(
        envelope,
        signature=b"detached-signature",
        public_key_pem="-----BEGIN PUBLIC KEY-----\nkey\n-----END PUBLIC KEY-----\n",
    )

    assert proposed["kind"] == "hashedrekord"
    assert proposed["apiVersion"] == "0.0.1"
    assert proposed["spec"]["data"]["hash"] == {
        "algorithm": "sha256",
        "value": checkpoint_digest(envelope),
    }
    assert base64.b64decode(
        proposed["spec"]["signature"]["content"]
    ) == b"detached-signature"


def test_verify_inclusion_proof_accepts_single_leaf():
    leaf = b'{"entry":"checkpoint"}'
    assert verify_inclusion_proof(
        leaf_body=leaf,
        log_index=0,
        tree_size=1,
        hashes=[],
        root_hash=_leaf_hash(leaf),
    ) is True


def test_verify_inclusion_proof_detects_tampered_leaf():
    leaf = b'{"entry":"checkpoint"}'
    assert verify_inclusion_proof(
        leaf_body=leaf + b"tampered",
        log_index=0,
        tree_size=1,
        hashes=[],
        root_hash=_leaf_hash(leaf),
    ) is False


def test_verify_inclusion_proof_accepts_two_leaf_tree():
    left = b"left"
    right = b"right"
    left_hash = hashlib.sha256(b"\x00" + left).digest()
    right_hash = hashlib.sha256(b"\x00" + right).digest()
    root = hashlib.sha256(
        b"\x01" + left_hash + right_hash
    ).hexdigest()

    assert verify_inclusion_proof(
        leaf_body=left,
        log_index=0,
        tree_size=2,
        hashes=[right_hash.hex()],
        root_hash=root,
    ) is True
    assert verify_inclusion_proof(
        leaf_body=right,
        log_index=1,
        tree_size=2,
        hashes=[left_hash.hex()],
        root_hash=root,
    ) is True


def _rekor_response(envelope, *, digest=None, log_id=None):
    proposed = build_rekor_v1_hashedrekord(
        envelope,
        signature=b"signature",
        public_key_pem="-----BEGIN PUBLIC KEY-----\nkey\n-----END PUBLIC KEY-----\n",
    )
    if digest is not None:
        proposed["spec"]["data"]["hash"]["value"] = digest
    body = json.dumps(
        proposed,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return {
        "b" * 64: {
            "logID": log_id or "a" * 64,
            "logIndex": 0,
            "integratedTime": 1_789_490_000,
            "body": base64.b64encode(body).decode("ascii"),
            "verification": {
                "inclusionProof": {
                    "logIndex": 0,
                    "rootHash": _leaf_hash(body),
                    "treeSize": 1,
                    "hashes": [],
                    "checkpoint": "rekor.example\n1\nroot\n\n— rekor.example signature\n",
                },
                "signedEntryTimestamp": base64.b64encode(
                    b"set"
                ).decode("ascii"),
            },
        }
    }


def _signed_rekor_response(envelope):
    private_key = ec.generate_private_key(ec.SECP256R1())
    public_key = private_key.public_key()
    public_pem = public_key.public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode("ascii")
    public_der = public_key.public_bytes(
        serialization.Encoding.DER,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    log_id = hashlib.sha256(public_der).hexdigest()
    response = _rekor_response(envelope, log_id=log_id)
    entry = response["b" * 64]
    proof = entry["verification"]["inclusionProof"]
    note = (
        "rekor.example - 1\n"
        f"{proof['treeSize']}\n"
        f"{base64.b64encode(bytes.fromhex(proof['rootHash'])).decode('ascii')}\n"
    )
    key_hint = hashlib.sha256(public_der).digest()[:4]
    checkpoint_digest = hashlib.sha256(note.encode("utf-8")).digest()
    checkpoint_signature = private_key.sign(
        checkpoint_digest,
        ec.ECDSA(utils.Prehashed(hashes.SHA256())),
    )
    checkpoint_encoded = base64.b64encode(
        key_hint + checkpoint_signature
    ).decode("ascii")
    proof["checkpoint"] = (
        f"{note}\n— rekor.example {checkpoint_encoded}\n"
    )
    signed_payload = {
        key: value
        for key, value in entry.items()
        if key != "verification"
    }
    canonical = json.dumps(
        signed_payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    signature = private_key.sign(
        canonical,
        ec.ECDSA(hashes.SHA256()),
    )
    entry["verification"]["signedEntryTimestamp"] = (
        base64.b64encode(signature).decode("ascii")
    )
    return response, public_pem, log_id


def test_parse_rekor_v1_receipt_requires_bound_inclusion_proof():
    envelope = _envelope()
    receipt = parse_rekor_v1_receipt(
        _rekor_response(envelope),
        envelope=envelope,
    )

    assert receipt["schema_version"] == RECEIPT_SCHEMA
    assert receipt["provider"] == "rekor-v1"
    assert receipt["checkpoint_sha256"] == checkpoint_digest(envelope)
    assert receipt["entry_uuid"] == "b" * 64
    assert receipt["log_id"] == "a" * 64
    assert receipt["log_index"] == 0
    assert receipt["proof_verified"] is True


def test_parse_rekor_v1_receipt_rejects_wrong_checkpoint_digest():
    with pytest.raises(
        TransparencyReceiptError,
        match="checkpoint digest mismatch",
    ):
        parse_rekor_v1_receipt(
            _rekor_response(_envelope(), digest="0" * 64),
            envelope=_envelope(),
        )


def test_verify_rekor_signed_entry_timestamp_binds_log_identity_and_entry():
    response, public_pem, _ = _signed_rekor_response(_envelope())
    entry = response["b" * 64]

    assert verify_rekor_signed_entry_timestamp(
        entry,
        public_key_pem=public_pem,
    ) is True

    entry["logIndex"] = 1
    assert verify_rekor_signed_entry_timestamp(
        entry,
        public_key_pem=public_pem,
    ) is False


def test_verify_rekor_v1_receipt_rejects_wrong_log_id_or_envelope():
    envelope = _envelope()
    receipt = parse_rekor_v1_receipt(
        _rekor_response(envelope),
        envelope=envelope,
    )

    assert verify_rekor_v1_receipt(
        receipt,
        envelope=envelope,
        expected_log_id="a" * 64,
    ) is True
    assert verify_rekor_v1_receipt(
        receipt,
        envelope=envelope,
        expected_log_id="c" * 64,
    ) is False

    tampered = _envelope()
    tampered["checkpoint"]["entries"] = 8
    assert verify_rekor_v1_receipt(
        receipt,
        envelope=tampered,
        expected_log_id="a" * 64,
    ) is False


def test_verify_rekor_v1_receipt_can_authenticate_rekor_set():
    envelope = _envelope()
    response, public_pem, log_id = _signed_rekor_response(envelope)
    receipt = parse_rekor_v1_receipt(
        response,
        envelope=envelope,
    )

    assert verify_rekor_v1_receipt(
        receipt,
        envelope=envelope,
        expected_log_id=log_id,
        log_public_key_pem=public_pem,
    ) is True

    receipt["integrated_time"] += 1
    assert verify_rekor_v1_receipt(
        receipt,
        envelope=envelope,
        expected_log_id=log_id,
        log_public_key_pem=public_pem,
    ) is False


def test_rekor_v1_publisher_posts_hashedrekord_and_returns_receipt(monkeypatch):
    envelope = _envelope()
    observed = {}

    class Response:
        status = 201

        def __init__(self, payload):
            self._payload = payload

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self):
            return json.dumps(self._payload).encode("utf-8")

    def fake_urlopen(request, timeout):
        observed["url"] = request.full_url
        observed["timeout"] = timeout
        proposed = json.loads(request.data)
        observed["proposed"] = proposed
        body = json.dumps(
            proposed,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        payload = {
            "b" * 64: {
                "logID": "a" * 64,
                "logIndex": 0,
                "integratedTime": 1_789_490_000,
                "body": base64.b64encode(body).decode("ascii"),
                "verification": {
                    "inclusionProof": {
                        "logIndex": 0,
                        "rootHash": _leaf_hash(body),
                        "treeSize": 1,
                        "hashes": [],
                        "checkpoint": "checkpoint",
                    },
                    "signedEntryTimestamp": base64.b64encode(
                        b"set"
                    ).decode("ascii"),
                },
            }
        }
        return Response(payload)

    monkeypatch.setattr(
        "production_os.transparency_receipts.urlopen",
        fake_urlopen,
    )
    publisher = RekorV1Publisher(
        "https://rekor.example",
        signer=lambda payload: b"signed:" + hashlib.sha256(payload).digest(),
        public_key_pem="-----BEGIN PUBLIC KEY-----\nkey\n-----END PUBLIC KEY-----\n",
    )

    receipt = publisher.publish(envelope)

    assert observed["url"] == "https://rekor.example/api/v1/log/entries"
    assert observed["proposed"]["kind"] == "hashedrekord"
    assert receipt["proof_verified"] is True


def test_rekor_v1_publisher_from_private_key_derives_signing_identity():
    private_pem = _rekor_signing_private_pem()
    publisher = RekorV1Publisher.from_private_key(
        "https://rekor.example",
        private_key_pem=private_pem,
    )

    signature = publisher.signer(b"checkpoint")
    public_key = serialization.load_pem_public_key(
        publisher.public_key_pem.encode("ascii")
    )
    public_key.verify(
        signature,
        b"checkpoint",
        ec.ECDSA(hashes.SHA256()),
    )


def test_rekor_v1_publisher_with_log_key_fails_closed_on_bad_set(monkeypatch):
    envelope = _envelope()
    log_private = ec.generate_private_key(ec.SECP256R1())
    log_public = log_private.public_key()
    log_public_pem = log_public.public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode("ascii")
    log_id = hashlib.sha256(log_public.public_bytes(
        serialization.Encoding.DER,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    )).hexdigest()
    private_pem = _rekor_signing_private_pem()

    class Response:
        status = 201
        def __enter__(self):
            return self
        def __exit__(self, *args):
            return False
        def read(self):
            proposed = json.loads(self.request.data)
            body = json.dumps(
                proposed,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
            payload = {
                "b" * 64: {
                    "logID": log_id,
                    "logIndex": 0,
                    "integratedTime": 1_789_490_000,
                    "body": base64.b64encode(body).decode("ascii"),
                    "verification": {
                        "inclusionProof": {
                            "logIndex": 0,
                            "rootHash": _leaf_hash(body),
                            "treeSize": 1,
                            "hashes": [],
                            "checkpoint": "checkpoint",
                        },
                        "signedEntryTimestamp": base64.b64encode(
                            b"forged"
                        ).decode("ascii"),
                    },
                }
            }
            return json.dumps(payload).encode("utf-8")

    def fake_urlopen(request, timeout):
        response = Response()
        response.request = request
        return response

    monkeypatch.setattr(
        "production_os.transparency_receipts.urlopen",
        fake_urlopen,
    )
    publisher = RekorV1Publisher.from_private_key(
        "https://rekor.example",
        private_key_pem=private_pem,
        log_public_key_pem=log_public_pem,
    )

    with pytest.raises(
        TransparencyReceiptError,
        match="signed entry timestamp",
    ):
        publisher.publish(envelope)
