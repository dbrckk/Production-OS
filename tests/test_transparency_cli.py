import argparse
import base64
import hashlib
import json

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, utils

from production_os import cli
from production_os.signing import generate_keypair
from production_os.transparency_receipts import (
    RECEIPT_SCHEMA,
    build_rekor_v1_hashedrekord,
    parse_rekor_v1_receipt,
)
from production_os.witness import create_checkpoint, sign_checkpoint


def _signed_rekor_receipt(envelope):
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
        signature=b"detached-signature",
        public_key_pem="-----BEGIN PUBLIC KEY-----\nkey\n-----END PUBLIC KEY-----\n",
    )
    body = json.dumps(
        proposed,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    entry = {
        "logID": log_id,
        "logIndex": 0,
        "integratedTime": 1_789_490_000,
        "body": base64.b64encode(body).decode("ascii"),
    }
    root_hash = hashlib.sha256(b"\x00" + body).hexdigest()
    note = (
        "rekor.example - 1\n"
        "1\n"
        f"{base64.b64encode(bytes.fromhex(root_hash)).decode('ascii')}\n"
    )
    key_hint = hashlib.sha256(log_public_der).digest()[:4]
    note_digest = hashlib.sha256(note.encode("utf-8")).digest()
    checkpoint_signature = log_private.sign(
        note_digest,
        ec.ECDSA(utils.Prehashed(hashes.SHA256())),
    )
    checkpoint = (
        f"{note}\n— rekor.example "
        f"{base64.b64encode(key_hint + checkpoint_signature).decode('ascii')}\n"
    )
    canonical = json.dumps(
        entry,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    set_signature = log_private.sign(
        canonical,
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
        "signedEntryTimestamp": base64.b64encode(
            set_signature
        ).decode("ascii"),
    }
    receipt = parse_rekor_v1_receipt(
        {"b" * 64: entry},
        envelope=envelope,
    )
    return receipt, log_public_pem, log_id


def test_checkpoint_verify_combines_witness_and_rekor_receipt(tmp_path, capsys):
    witness_private, witness_public = generate_keypair()
    envelope = sign_checkpoint(
        create_checkpoint(
            root_hash="a" * 64,
            entries=1,
            created_at="2026-09-15T17:00:00+00:00",
        ),
        private_key_pem=witness_private,
    )
    receipt, log_public_pem, log_id = _signed_rekor_receipt(envelope)

    checkpoint_path = tmp_path / "checkpoint.json"
    witness_key_path = tmp_path / "witness.pub.pem"
    receipt_path = tmp_path / "receipt.json"
    log_key_path = tmp_path / "rekor-log.pem"
    checkpoint_path.write_text(json.dumps(envelope), encoding="utf-8")
    witness_key_path.write_text(witness_public, encoding="ascii")
    receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
    log_key_path.write_text(log_public_pem, encoding="ascii")

    args = argparse.Namespace(
        checkpoint=str(checkpoint_path),
        public_key=str(witness_key_path),
        root_hash="a" * 64,
        receipt=str(receipt_path),
        rekor_log_public_key=str(log_key_path),
        rekor_log_id=log_id,
    )
    exit_code = cli.run_transparency_checkpoint_verify(args)
    result = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert result["valid"] is True
    assert result["checkpoint_valid"] is True
    assert result["receipt_valid"] is True


def test_checkpoint_verify_fails_closed_on_tampered_rekor_receipt(
    tmp_path, capsys
):
    witness_private, witness_public = generate_keypair()
    envelope = sign_checkpoint(
        create_checkpoint(
            root_hash="a" * 64,
            entries=1,
            created_at="2026-09-15T17:00:00+00:00",
        ),
        private_key_pem=witness_private,
    )
    receipt, log_public_pem, log_id = _signed_rekor_receipt(envelope)
    receipt["integrated_time"] += 1

    checkpoint_path = tmp_path / "checkpoint.json"
    witness_key_path = tmp_path / "witness.pub.pem"
    receipt_path = tmp_path / "receipt.json"
    log_key_path = tmp_path / "rekor-log.pem"
    checkpoint_path.write_text(json.dumps(envelope), encoding="utf-8")
    witness_key_path.write_text(witness_public, encoding="ascii")
    receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
    log_key_path.write_text(log_public_pem, encoding="ascii")

    args = argparse.Namespace(
        checkpoint=str(checkpoint_path),
        public_key=str(witness_key_path),
        root_hash="a" * 64,
        receipt=str(receipt_path),
        rekor_log_public_key=str(log_key_path),
        rekor_log_id=log_id,
    )
    exit_code = cli.run_transparency_checkpoint_verify(args)
    result = json.loads(capsys.readouterr().out)

    assert exit_code == 9
    assert result["valid"] is False
    assert result["checkpoint_valid"] is True
    assert result["receipt_valid"] is False


def test_checkpoint_publication_writes_rekor_receipt(tmp_path, monkeypatch, capsys):
    witness_private, _ = generate_keypair()
    rekor_private, _ = generate_keypair()
    witness_key_path = tmp_path / "witness.pem"
    rekor_key_path = tmp_path / "rekor.pem"
    log_key_path = tmp_path / "rekor-log.pem"
    receipt_path = tmp_path / "receipt.json"
    witness_key_path.write_text(witness_private, encoding="ascii")
    rekor_key_path.write_text(rekor_private, encoding="ascii")
    log_key_path.write_text("log-public-key", encoding="ascii")

    class Ledger:
        def verify_transparency(self):
            return {
                "valid": True,
                "root_hash": "a" * 64,
                "entries": 3,
            }

    observed = {}

    class FakePublisher:
        @classmethod
        def from_private_key(
            cls,
            base_url,
            *,
            private_key_pem,
            log_public_key_pem,
            **kwargs,
        ):
            observed["base_url"] = base_url
            observed["private_key_pem"] = private_key_pem
            observed["log_public_key_pem"] = log_public_key_pem
            return cls()

        def publish(self, envelope):
            observed["envelope"] = envelope
            return {
                "schema_version": RECEIPT_SCHEMA,
                "provider": "rekor-v1",
                "checkpoint_sha256": "c" * 64,
                "entry_uuid": "b" * 64,
                "log_id": "a" * 64,
                "log_index": 4,
                "integrated_time": 1_789_490_000,
                "proof_verified": True,
            }

    monkeypatch.setattr(cli, "_release_ledger", lambda database: Ledger())
    monkeypatch.setattr(cli, "RekorV1Publisher", FakePublisher, raising=False)

    args = argparse.Namespace(
        database="state.sqlite",
        private_key=str(witness_key_path),
        witness_signer_uri=None,
        witness_signer_key_id=None,
        witness_signer_token_env=None,
        output=None,
        publish_url=None,
        bearer_token_env=None,
        rekor_url="https://rekor.example",
        rekor_private_key=str(rekor_key_path),
        rekor_log_public_key=str(log_key_path),
        receipt_output=str(receipt_path),
    )
    exit_code = cli.run_transparency_checkpoint(args)
    result = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert observed["base_url"] == "https://rekor.example"
    assert observed["private_key_pem"] == rekor_private
    assert observed["log_public_key_pem"] == "log-public-key"
    assert result["rekor_receipt"]["proof_verified"] is True
    assert json.loads(receipt_path.read_text())["provider"] == "rekor-v1"
