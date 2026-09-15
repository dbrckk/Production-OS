from pathlib import Path

source = Path("src/production_os/transparency_receipts.py")
text = source.read_text()
old = '''            if not verify_rekor_signed_entry_timestamp(
                set_entry,
                public_key_pem=log_public_key_pem,
            ):
                return False
        return True
'''
new = '''            if not verify_rekor_signed_entry_timestamp(
                set_entry,
                public_key_pem=log_public_key_pem,
            ):
                return False
            checkpoint = proof.get("checkpoint")
            if not isinstance(checkpoint, str) or not verify_rekor_signed_checkpoint(
                checkpoint,
                public_key_pem=log_public_key_pem,
                expected_tree_size=int(proof["treeSize"]),
                expected_root_hash=str(proof["rootHash"]),
            ):
                return False
        return True
'''
if old not in text:
    raise SystemExit("receipt verification marker not found")
source.write_text(text.replace(old, new, 1))

tests = Path("tests/test_transparency_receipts.py")
text = tests.read_text()
text = text.replace(
    "from cryptography.hazmat.primitives.asymmetric import ec",
    "from cryptography.hazmat.primitives.asymmetric import ec, utils",
    1,
)
old = '''    response = _rekor_response(envelope, log_id=log_id)
    entry = response["b" * 64]
    signed_payload = {
'''
new = '''    response = _rekor_response(envelope, log_id=log_id)
    entry = response["b" * 64]
    proof = entry["verification"]["inclusionProof"]
    note = (
        "rekor.example - 1\\n"
        f"{proof['treeSize']}\\n"
        f"{base64.b64encode(bytes.fromhex(proof['rootHash'])).decode('ascii')}\\n"
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
        f"{note}\\n— rekor.example {checkpoint_encoded}\\n"
    )
    signed_payload = {
'''
if old not in text:
    raise SystemExit("signed response fixture marker not found")
tests.write_text(text.replace(old, new, 1))
