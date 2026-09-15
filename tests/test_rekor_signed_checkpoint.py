import base64
import hashlib

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, utils

from production_os.transparency_receipts import verify_rekor_signed_checkpoint


def _log_keypair():
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
    key_hint = hashlib.sha256(public_der).digest()[:4]
    return private_key, public_pem, key_hint


def _signed_checkpoint(
    private_key,
    key_hint: bytes,
    *,
    root_hash: str,
    tree_size: int = 1,
    origin: str = "rekor.example - 1",
) -> str:
    note = (
        f"{origin}\n"
        f"{tree_size}\n"
        f"{base64.b64encode(bytes.fromhex(root_hash)).decode('ascii')}\n"
    )
    digest = hashlib.sha256(note.encode("utf-8")).digest()
    signature = private_key.sign(
        digest,
        ec.ECDSA(utils.Prehashed(hashes.SHA256())),
    )
    encoded = base64.b64encode(key_hint + signature).decode("ascii")
    return f"{note}\n— rekor.example {encoded}\n"


def test_verify_rekor_signed_checkpoint_authenticates_root_and_tree_size():
    private_key, public_pem, key_hint = _log_keypair()
    root_hash = hashlib.sha256(b"root").hexdigest()
    checkpoint = _signed_checkpoint(
        private_key,
        key_hint,
        root_hash=root_hash,
        tree_size=17,
    )

    assert verify_rekor_signed_checkpoint(
        checkpoint,
        public_key_pem=public_pem,
        expected_tree_size=17,
        expected_root_hash=root_hash,
    ) is True
