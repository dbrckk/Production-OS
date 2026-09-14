from __future__ import annotations

import hashlib
import hmac
import json
from datetime import datetime, timezone
from pathlib import Path

from .atomic_io import atomic_write_json
from .audit_integrity import verify_hash_chain


def create_audit_checkpoint(
    journal_path: str | Path,
    checkpoint_path: str | Path,
    *,
    secret: str,
) -> dict:
    if not secret:
        raise ValueError("secret is required")

    verification = verify_hash_chain(journal_path)
    if not verification.get("valid"):
        raise RuntimeError("cannot checkpoint invalid audit chain")

    payload = {
        "schema_version": "production-os/audit-checkpoint/v1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "journal": str(journal_path),
        "checked": int(verification.get("checked", 0)),
        "head": str(verification.get("head", "0" * 64)),
    }
    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    signature = hmac.new(
        secret.encode("utf-8"),
        canonical,
        hashlib.sha256,
    ).hexdigest()
    output = {**payload, "signature": signature}
    atomic_write_json(checkpoint_path, output)
    return output


def verify_audit_checkpoint(
    checkpoint_path: str | Path,
    *,
    secret: str,
) -> dict:
    payload = json.loads(Path(checkpoint_path).read_text(encoding="utf-8"))
    signature = str(payload.pop("signature", ""))
    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    expected = hmac.new(
        secret.encode("utf-8"),
        canonical,
        hashlib.sha256,
    ).hexdigest()
    return {
        "valid": hmac.compare_digest(signature, expected),
        "head": payload.get("head"),
        "checked": payload.get("checked"),
    }
