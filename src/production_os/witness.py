from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .signing import sign_payload, verify_payload


WITNESS_SCHEMA = "production-os/transparency-witness/v1"


class WitnessError(RuntimeError):
    pass


def create_checkpoint(
    *,
    root_hash: str,
    entries: int,
    created_at: str | None = None,
) -> dict[str, Any]:
    if len(str(root_hash)) != 64:
        raise WitnessError("invalid transparency root hash")
    return {
        "schema_version":WITNESS_SCHEMA,
        "root_hash":str(root_hash),
        "entries":int(entries),
        "created_at":created_at
        or datetime.now(timezone.utc).isoformat(),
    }


def sign_checkpoint(
    checkpoint: dict[str, Any],
    *,
    private_key_pem: str,
) -> dict[str, Any]:
    return {
        "checkpoint":checkpoint,
        "signature":sign_payload(
            private_key_pem,
            checkpoint,
        ),
    }


def verify_checkpoint(
    envelope: dict[str, Any],
    *,
    public_key_pem: str,
    expected_root_hash: str | None = None,
) -> bool:
    checkpoint = envelope.get("checkpoint")
    signature = envelope.get("signature")
    if not isinstance(checkpoint, dict) or not isinstance(
        signature, dict
    ):
        return False
    if checkpoint.get("schema_version") != WITNESS_SCHEMA:
        return False
    if (
        expected_root_hash is not None
        and checkpoint.get("root_hash") != expected_root_hash
    ):
        return False
    return verify_payload(
        public_key_pem,
        checkpoint,
        signature,
    )


def publish_checkpoint(
    *,
    url: str,
    envelope: dict[str, Any],
    bearer_token: str | None = None,
    timeout_seconds: float = 10.0,
) -> dict[str, Any]:
    body = json.dumps(
        envelope,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    headers = {
        "Content-Type":"application/json",
        "Accept":"application/json",
    }
    if bearer_token:
        headers["Authorization"] = f"Bearer {bearer_token}"
    request = Request(
        url,
        data=body,
        headers=headers,
        method="POST",
    )
    try:
        with urlopen(
            request,
            timeout=timeout_seconds,
        ) as response:
            raw = response.read()
            status = int(response.status)
    except (HTTPError, URLError, TimeoutError) as exc:
        raise WitnessError(
            f"witness publication failed: {exc}"
        ) from exc
    if status < 200 or status >= 300:
        raise WitnessError(
            f"witness returned HTTP {status}"
        )
    if not raw:
        return {"status":status}
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise WitnessError(
            "witness returned invalid JSON"
        ) from exc
    if not isinstance(payload, dict):
        raise WitnessError(
            "witness response must be an object"
        )
    return {"status":status, "response":payload}
