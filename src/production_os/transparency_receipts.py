from __future__ import annotations

import base64
import hashlib
import json
import re
from typing import Any, Callable, Protocol
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, ed25519, padding, rsa


RECEIPT_SCHEMA = "production-os/transparency-receipt/v1"
_HEX_64 = re.compile(r"^[0-9a-fA-F]{64}$")
_ENTRY_UUID = re.compile(r"^(?:[0-9a-fA-F]{64}|[0-9a-fA-F]{80})$")


class TransparencyReceiptError(RuntimeError):
    pass


class TransparencyPublisher(Protocol):
    def publish(self, envelope: dict[str, Any]) -> dict[str, Any]: ...


def _canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def checkpoint_digest(envelope: dict[str, Any]) -> str:
    return hashlib.sha256(_canonical_json_bytes(envelope)).hexdigest()


def build_rekor_v1_hashedrekord(
    envelope: dict[str, Any],
    *,
    signature: bytes,
    public_key_pem: str,
) -> dict[str, Any]:
    if not isinstance(signature, bytes) or not signature:
        raise TransparencyReceiptError("detached signature is required")
    if not str(public_key_pem).strip():
        raise TransparencyReceiptError("public key is required")
    return {
        "apiVersion": "0.0.1",
        "kind": "hashedrekord",
        "spec": {
            "data": {
                "hash": {
                    "algorithm": "sha256",
                    "value": checkpoint_digest(envelope),
                }
            },
            "signature": {
                "content": base64.b64encode(signature).decode("ascii"),
                "publicKey": {
                    "content": base64.b64encode(
                        public_key_pem.encode("ascii")
                    ).decode("ascii")
                },
            },
        },
    }


def _hash_leaf(body: bytes) -> bytes:
    return hashlib.sha256(b"\x00" + body).digest()


def _hash_children(left: bytes, right: bytes) -> bytes:
    return hashlib.sha256(b"\x01" + left + right).digest()


def verify_inclusion_proof(
    *,
    leaf_body: bytes,
    log_index: int,
    tree_size: int,
    hashes: list[str],
    root_hash: str,
) -> bool:
    try:
        index = int(log_index)
        size = int(tree_size)
    except (TypeError, ValueError):
        return False
    if index < 0 or size <= 0 or index >= size:
        return False
    if not _HEX_64.fullmatch(str(root_hash)):
        return False
    try:
        path = [bytes.fromhex(str(item)) for item in hashes]
    except ValueError:
        return False
    if any(len(item) != 32 for item in path):
        return False

    fn = index
    sn = size - 1
    current = _hash_leaf(leaf_body)

    for sibling in path:
        if sn == 0:
            return False
        if fn == sn or fn & 1:
            current = _hash_children(sibling, current)
            while fn != 0 and fn & 1 == 0:
                fn >>= 1
                sn >>= 1
        else:
            current = _hash_children(current, sibling)
        fn >>= 1
        sn >>= 1

    return sn == 0 and current.hex() == str(root_hash).lower()


def _decode_entry_body(encoded: str) -> tuple[bytes, dict[str, Any]]:
    try:
        raw = base64.b64decode(encoded, validate=True)
        body = json.loads(raw)
    except (ValueError, json.JSONDecodeError) as exc:
        raise TransparencyReceiptError(
            "invalid Rekor entry body"
        ) from exc
    if not isinstance(body, dict):
        raise TransparencyReceiptError("Rekor entry body must be an object")
    return raw, body


def _entry_checkpoint_digest(body: dict[str, Any]) -> str:
    try:
        if body.get("kind") == "hashedrekord":
            value = body["spec"]["data"]["hash"]["value"]
        else:
            value = body["HashedRekordObj"]["data"]["hash"]["value"]
    except (KeyError, TypeError) as exc:
        raise TransparencyReceiptError(
            "Rekor entry is not a hashedrekord"
        ) from exc
    value = str(value).lower()
    if not _HEX_64.fullmatch(value):
        raise TransparencyReceiptError("invalid Rekor checkpoint digest")
    return value


def _rekor_log_id(public_key: Any) -> str:
    der = public_key.public_bytes(
        serialization.Encoding.DER,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return hashlib.sha256(der).hexdigest()


def verify_rekor_signed_entry_timestamp(
    entry: dict[str, Any],
    *,
    public_key_pem: str,
) -> bool:
    """Authenticate Rekor's SET and bind it to the configured log key."""
    try:
        verification = entry.get("verification")
        if not isinstance(verification, dict):
            return False
        encoded = verification.get("signedEntryTimestamp")
        if not isinstance(encoded, str) or not encoded:
            return False
        signature = base64.b64decode(encoded, validate=True)
        public_key = serialization.load_pem_public_key(
            public_key_pem.encode("ascii")
        )
        if str(entry.get("logID") or "").lower() != _rekor_log_id(
            public_key
        ):
            return False
        payload = {
            key: value
            for key, value in entry.items()
            if key != "verification"
        }
        canonical = _canonical_json_bytes(payload)
        if isinstance(public_key, ec.EllipticCurvePublicKey):
            public_key.verify(
                signature,
                canonical,
                ec.ECDSA(hashes.SHA256()),
            )
        elif isinstance(public_key, ed25519.Ed25519PublicKey):
            public_key.verify(signature, canonical)
        elif isinstance(public_key, rsa.RSAPublicKey):
            public_key.verify(
                signature,
                canonical,
                padding.PKCS1v15(),
                hashes.SHA256(),
            )
        else:
            return False
        return True
    except (
        InvalidSignature,
        TypeError,
        ValueError,
        UnicodeEncodeError,
    ):
        return False


def parse_rekor_v1_receipt(
    response: dict[str, Any],
    *,
    envelope: dict[str, Any],
) -> dict[str, Any]:
    if not isinstance(response, dict) or len(response) != 1:
        raise TransparencyReceiptError(
            "Rekor response must contain exactly one entry"
        )
    entry_uuid, entry = next(iter(response.items()))
    if not _ENTRY_UUID.fullmatch(str(entry_uuid)):
        raise TransparencyReceiptError("invalid Rekor entry UUID")
    if not isinstance(entry, dict):
        raise TransparencyReceiptError("invalid Rekor entry")

    log_id = str(entry.get("logID") or "")
    if not _HEX_64.fullmatch(log_id):
        raise TransparencyReceiptError("invalid Rekor log ID")
    try:
        log_index = int(entry["logIndex"])
        integrated_time = int(entry["integratedTime"])
    except (KeyError, TypeError, ValueError) as exc:
        raise TransparencyReceiptError("invalid Rekor entry metadata") from exc
    if log_index < 0 or integrated_time < 0:
        raise TransparencyReceiptError("invalid Rekor entry metadata")

    body_encoded = entry.get("body")
    if not isinstance(body_encoded, str) or not body_encoded:
        raise TransparencyReceiptError("Rekor entry body is required")
    body_raw, body = _decode_entry_body(body_encoded)
    expected_digest = checkpoint_digest(envelope)
    if _entry_checkpoint_digest(body) != expected_digest:
        raise TransparencyReceiptError("checkpoint digest mismatch")

    verification = entry.get("verification")
    if not isinstance(verification, dict):
        raise TransparencyReceiptError("Rekor verification is required")
    proof = verification.get("inclusionProof")
    if not isinstance(proof, dict):
        raise TransparencyReceiptError("Rekor inclusion proof is required")
    try:
        proof_index = int(proof["logIndex"])
        tree_size = int(proof["treeSize"])
    except (KeyError, TypeError, ValueError) as exc:
        raise TransparencyReceiptError("invalid Rekor inclusion proof") from exc
    hashes = proof.get("hashes")
    root_hash = str(proof.get("rootHash") or "")
    checkpoint = proof.get("checkpoint")
    if proof_index != log_index:
        raise TransparencyReceiptError("Rekor proof index mismatch")
    if not isinstance(hashes, list) or not isinstance(checkpoint, str) or not checkpoint:
        raise TransparencyReceiptError("invalid Rekor inclusion proof")
    if not verify_inclusion_proof(
        leaf_body=body_raw,
        log_index=proof_index,
        tree_size=tree_size,
        hashes=[str(item) for item in hashes],
        root_hash=root_hash,
    ):
        raise TransparencyReceiptError("invalid Rekor inclusion proof")

    signed_entry_timestamp = verification.get("signedEntryTimestamp")
    if not isinstance(signed_entry_timestamp, str) or not signed_entry_timestamp:
        raise TransparencyReceiptError(
            "Rekor signed entry timestamp is required"
        )

    return {
        "schema_version": RECEIPT_SCHEMA,
        "provider": "rekor-v1",
        "checkpoint_sha256": expected_digest,
        "entry_uuid": str(entry_uuid).lower(),
        "log_id": log_id.lower(),
        "log_index": log_index,
        "integrated_time": integrated_time,
        "entry_body": body_encoded,
        "inclusion_proof": dict(proof),
        "signed_entry_timestamp": signed_entry_timestamp,
        "proof_verified": True,
    }


def verify_rekor_v1_receipt(
    receipt: dict[str, Any],
    *,
    envelope: dict[str, Any],
    expected_log_id: str | None = None,
    log_public_key_pem: str | None = None,
) -> bool:
    try:
        if receipt.get("schema_version") != RECEIPT_SCHEMA:
            return False
        if receipt.get("provider") != "rekor-v1":
            return False
        if receipt.get("checkpoint_sha256") != checkpoint_digest(envelope):
            return False
        log_id = str(receipt.get("log_id") or "")
        if not _HEX_64.fullmatch(log_id):
            return False
        if expected_log_id is not None and log_id.lower() != str(
            expected_log_id
        ).lower():
            return False
        if not _ENTRY_UUID.fullmatch(str(receipt.get("entry_uuid") or "")):
            return False

        body_encoded = receipt.get("entry_body")
        if not isinstance(body_encoded, str) or not body_encoded:
            return False
        body_raw, body = _decode_entry_body(body_encoded)
        if _entry_checkpoint_digest(body) != checkpoint_digest(envelope):
            return False

        proof = receipt.get("inclusion_proof")
        if not isinstance(proof, dict):
            return False
        if int(proof.get("logIndex", -1)) != int(
            receipt.get("log_index", -2)
        ):
            return False
        hashes = proof.get("hashes")
        if not isinstance(hashes, list):
            return False
        proof_valid = verify_inclusion_proof(
            leaf_body=body_raw,
            log_index=int(proof["logIndex"]),
            tree_size=int(proof["treeSize"]),
            hashes=[str(item) for item in hashes],
            root_hash=str(proof["rootHash"]),
        )
        if not proof_valid:
            return False

        if log_public_key_pem is not None:
            set_entry = {
                "logID": log_id,
                "logIndex": int(receipt["log_index"]),
                "integratedTime": int(receipt["integrated_time"]),
                "body": body_encoded,
                "verification": {
                    "signedEntryTimestamp": str(
                        receipt.get("signed_entry_timestamp") or ""
                    )
                },
            }
            if not verify_rekor_signed_entry_timestamp(
                set_entry,
                public_key_pem=log_public_key_pem,
            ):
                return False
        return True
    except (
        KeyError,
        TypeError,
        ValueError,
        TransparencyReceiptError,
    ):
        return False


def _private_key_signer(private_key: Any) -> Callable[[bytes], bytes]:
    if isinstance(private_key, ed25519.Ed25519PrivateKey):
        return private_key.sign
    if isinstance(private_key, ec.EllipticCurvePrivateKey):
        return lambda payload: private_key.sign(
            payload,
            ec.ECDSA(hashes.SHA256()),
        )
    if isinstance(private_key, rsa.RSAPrivateKey):
        return lambda payload: private_key.sign(
            payload,
            padding.PKCS1v15(),
            hashes.SHA256(),
        )
    raise TransparencyReceiptError("unsupported Rekor signing key type")


class RekorV1Publisher:
    """Publish a checkpoint envelope through Rekor's stable v1 API.

    The supplied signer must produce a detached signature compatible with
    Rekor hashedrekord verification for the supplied public key.
    """

    def __init__(
        self,
        base_url: str,
        *,
        signer: Callable[[bytes], bytes],
        public_key_pem: str,
        timeout_seconds: float = 10.0,
        log_public_key_pem: str | None = None,
    ) -> None:
        url = str(base_url).rstrip("/")
        if not url:
            raise ValueError("Rekor base URL is required")
        self.endpoint = (
            url
            if url.endswith("/api/v1/log/entries")
            else url + "/api/v1/log/entries"
        )
        self.signer = signer
        self.public_key_pem = public_key_pem
        self.timeout_seconds = float(timeout_seconds)
        self.log_public_key_pem = log_public_key_pem

    @classmethod
    def from_private_key(
        cls,
        base_url: str,
        *,
        private_key_pem: str,
        timeout_seconds: float = 10.0,
        log_public_key_pem: str | None = None,
    ) -> "RekorV1Publisher":
        try:
            private_key = serialization.load_pem_private_key(
                private_key_pem.encode("ascii"),
                password=None,
            )
        except (TypeError, ValueError, UnicodeEncodeError) as exc:
            raise TransparencyReceiptError(
                "invalid Rekor signing private key"
            ) from exc
        signer = _private_key_signer(private_key)
        public_key_pem = private_key.public_key().public_bytes(
            serialization.Encoding.PEM,
            serialization.PublicFormat.SubjectPublicKeyInfo,
        ).decode("ascii")
        return cls(
            base_url,
            signer=signer,
            public_key_pem=public_key_pem,
            timeout_seconds=timeout_seconds,
            log_public_key_pem=log_public_key_pem,
        )

    def publish(self, envelope: dict[str, Any]) -> dict[str, Any]:
        payload = _canonical_json_bytes(envelope)
        signature = self.signer(payload)
        proposed = build_rekor_v1_hashedrekord(
            envelope,
            signature=signature,
            public_key_pem=self.public_key_pem,
        )
        request = Request(
            self.endpoint,
            data=_canonical_json_bytes(proposed),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            method="POST",
        )
        try:
            with urlopen(
                request,
                timeout=self.timeout_seconds,
            ) as response:
                status = int(response.status)
                raw = response.read()
        except (HTTPError, URLError, TimeoutError) as exc:
            raise TransparencyReceiptError(
                f"Rekor publication failed: {exc}"
            ) from exc
        if status < 200 or status >= 300:
            raise TransparencyReceiptError(
                f"Rekor returned HTTP {status}"
            )
        try:
            decoded = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise TransparencyReceiptError(
                "Rekor returned invalid JSON"
            ) from exc
        receipt = parse_rekor_v1_receipt(
            decoded,
            envelope=envelope,
        )
        if self.log_public_key_pem is not None and not verify_rekor_v1_receipt(
            receipt,
            envelope=envelope,
            log_public_key_pem=self.log_public_key_pem,
        ):
            raise TransparencyReceiptError(
                "invalid Rekor signed entry timestamp"
            )
        return receipt
