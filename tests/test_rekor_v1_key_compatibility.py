import pytest
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec

from production_os.signing import generate_keypair
from production_os.transparency_receipts import (
    RekorV1Publisher,
    TransparencyReceiptError,
)


def _ec_private_pem():
    private_key = ec.generate_private_key(ec.SECP256R1())
    return private_key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    ).decode("ascii")


def test_rekor_v1_hashedrekord_accepts_ecdsa_pkix_signing_key():
    private_pem = _ec_private_pem()
    publisher = RekorV1Publisher.from_private_key(
        "https://rekor.example",
        private_key_pem=private_pem,
    )

    public_key = serialization.load_pem_public_key(
        publisher.public_key_pem.encode("ascii")
    )
    signature = publisher.signer(b"checkpoint")
    public_key.verify(
        signature,
        b"checkpoint",
        ec.ECDSA(hashes.SHA256()),
    )


def test_rekor_v1_hashedrekord_rejects_ed25519_key():
    private_pem, _ = generate_keypair()

    with pytest.raises(
        TransparencyReceiptError,
        match="hashedrekord requires a PKIX ECDSA or RSA signing key",
    ):
        RekorV1Publisher.from_private_key(
            "https://rekor.example",
            private_key_pem=private_pem,
        )
