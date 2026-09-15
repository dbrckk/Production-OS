from __future__ import annotations

import hashlib
import json
from typing import Any


LOG_SCHEMA = "production-os/transparency-entry/v1"
GENESIS_HASH = "0" * 64


class TransparencyError(ValueError):
    pass


def _canonical(payload: dict[str, Any]) -> bytes:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def entry_hash(payload: dict[str, Any]) -> str:
    return hashlib.sha256(_canonical(payload)).hexdigest()


def create_entry(
    *,
    sequence: int,
    release_id: str,
    release_provenance_sha256: str,
    slsa_statement_sha256: str | None,
    previous_hash: str | None,
    created_at: str,
) -> dict[str, Any]:
    if sequence < 1:
        raise TransparencyError("sequence must be positive")
    previous = previous_hash or GENESIS_HASH
    if len(previous) != 64:
        raise TransparencyError("invalid previous transparency hash")
    payload = {
        "schema_version":LOG_SCHEMA,
        "sequence":sequence,
        "release_id":release_id,
        "release_provenance_sha256":release_provenance_sha256,
        "slsa_statement_sha256":slsa_statement_sha256,
        "previous_hash":previous,
        "created_at":created_at,
    }
    return {**payload, "entry_hash":entry_hash(payload)}


def verify_entry(
    entry: dict[str, Any],
    *,
    expected_previous_hash: str | None = None,
) -> bool:
    payload = dict(entry)
    supplied = str(payload.pop("entry_hash", ""))
    if payload.get("schema_version") != LOG_SCHEMA:
        return False
    if expected_previous_hash is not None and payload.get(
        "previous_hash"
    ) != expected_previous_hash:
        return False
    return supplied == entry_hash(payload)


def verify_chain(entries: list[dict[str, Any]]) -> dict[str, Any]:
    previous = GENESIS_HASH
    expected_sequence = 1
    for item in entries:
        if item.get("sequence") != expected_sequence:
            return {
                "valid":False,
                "reason":"transparency sequence gap",
                "sequence":expected_sequence,
            }
        if not verify_entry(
            item,
            expected_previous_hash=previous,
        ):
            return {
                "valid":False,
                "reason":"invalid transparency chain entry",
                "sequence":expected_sequence,
            }
        previous = item["entry_hash"]
        expected_sequence += 1
    return {
        "valid":True,
        "entries":len(entries),
        "root_hash":previous,
    }
