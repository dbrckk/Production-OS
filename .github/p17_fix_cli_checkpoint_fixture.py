from pathlib import Path

path = Path("tests/test_transparency_cli.py")
text = path.read_text()
text = text.replace(
    "from cryptography.hazmat.primitives.asymmetric import ec",
    "from cryptography.hazmat.primitives.asymmetric import ec, utils",
    1,
)
old = '''    log_id = hashlib.sha256(log_public.public_bytes(
        serialization.Encoding.DER,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    )).hexdigest()

    proposed = build_rekor_v1_hashedrekord(
'''
new = '''    log_public_der = log_public.public_bytes(
        serialization.Encoding.DER,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    log_id = hashlib.sha256(log_public_der).hexdigest()

    proposed = build_rekor_v1_hashedrekord(
'''
if old not in text:
    raise SystemExit("log key marker not found")
text = text.replace(old, new, 1)
old = '''    canonical = json.dumps(
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
            "rootHash": hashlib.sha256(b"\\x00" + body).hexdigest(),
            "treeSize": 1,
            "hashes": [],
            "checkpoint": "rekor.example\\n1\\nroot\\n\\n— rekor.example signature\\n",
        },
        "signedEntryTimestamp": base64.b64encode(
            set_signature
        ).decode("ascii"),
    }
'''
new = '''    root_hash = hashlib.sha256(b"\\x00" + body).hexdigest()
    note = (
        "rekor.example - 1\\n"
        "1\\n"
        f"{base64.b64encode(bytes.fromhex(root_hash)).decode('ascii')}\\n"
    )
    key_hint = hashlib.sha256(log_public_der).digest()[:4]
    note_digest = hashlib.sha256(note.encode("utf-8")).digest()
    checkpoint_signature = log_private.sign(
        note_digest,
        ec.ECDSA(utils.Prehashed(hashes.SHA256())),
    )
    checkpoint = (
        f"{note}\\n— rekor.example "
        f"{base64.b64encode(key_hint + checkpoint_signature).decode('ascii')}\\n"
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
'''
if old not in text:
    raise SystemExit("checkpoint fixture marker not found")
path.write_text(text.replace(old, new, 1))
