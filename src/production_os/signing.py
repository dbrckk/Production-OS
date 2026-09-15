from __future__ import annotations

import base64
import hashlib
import json
from typing import Any

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)


SIGNATURE_ALGORITHM = "ed25519"


class SigningError(ValueError):
    pass


def canonical_bytes(payload: dict[str, Any]) -> bytes:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def key_id(public_key: Ed25519PublicKey) -> str:
    raw = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def generate_keypair() -> tuple[str, str]:
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode("ascii")
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode("ascii")
    return private_pem, public_pem


def load_private_key(value: str) -> Ed25519PrivateKey:
    try:
        key = serialization.load_pem_private_key(
            value.encode("ascii"),
            password=None,
        )
    except (TypeError, ValueError) as exc:
        raise SigningError("invalid Ed25519 private key") from exc
    if not isinstance(key, Ed25519PrivateKey):
        raise SigningError("private key is not Ed25519")
    return key


def load_public_key(value: str) -> Ed25519PublicKey:
    try:
        key = serialization.load_pem_public_key(
            value.encode("ascii")
        )
    except (TypeError, ValueError) as exc:
        raise SigningError("invalid Ed25519 public key") from exc
    if not isinstance(key, Ed25519PublicKey):
        raise SigningError("public key is not Ed25519")
    return key


def sign_payload(
    private_key_pem: str,
    payload: dict[str, Any],
) -> dict[str, str]:
    private_key = load_private_key(private_key_pem)
    public_key = private_key.public_key()
    signature = private_key.sign(canonical_bytes(payload))
    return {
        "algorithm":SIGNATURE_ALGORITHM,
        "key_id":key_id(public_key),
        "signature":base64.b64encode(signature).decode("ascii"),
    }


def verify_payload(
    public_key_pem: str,
    payload: dict[str, Any],
    signature: dict[str, Any],
) -> bool:
    if signature.get("algorithm") != SIGNATURE_ALGORITHM:
        return False
    public_key = load_public_key(public_key_pem)
    if signature.get("key_id") != key_id(public_key):
        return False
    try:
        raw = base64.b64decode(
            str(signature.get("signature") or ""),
            validate=True,
        )
        public_key.verify(raw, canonical_bytes(payload))
    except (InvalidSignature, ValueError):
        return False
    return True
