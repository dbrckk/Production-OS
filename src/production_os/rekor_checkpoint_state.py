from __future__ import annotations

import base64
import hashlib
import json
import re
from datetime import datetime, timezone
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


_HEX_64 = re.compile(r"^[0-9a-fA-F]{64}$")
_TREE_ID = re.compile(r" - ([0-9]+)$")


class RekorCheckpointStateError(RuntimeError):
    pass


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def _hash_children(left: bytes, right: bytes) -> bytes:
    return hashlib.sha256(b"\x01" + left + right).digest()


def _decode_hash(value: str) -> bytes:
    text = str(value).lower()
    if not _HEX_64.fullmatch(text):
        raise ValueError("invalid SHA-256 hash")
    return bytes.fromhex(text)


def parse_checkpoint_identity(checkpoint: str) -> dict[str, Any]:
    """Extract the authenticated tree identity from a Rekor signed note.

    This function deliberately does not verify the note signature. Callers use
    it only after receipt verification has authenticated the checkpoint.
    """
    if not isinstance(checkpoint, str) or not checkpoint:
        raise RekorCheckpointStateError("invalid Rekor checkpoint")
    split = checkpoint.rfind("\n\n")
    note = checkpoint if split < 0 else checkpoint[: split + 1]
    lines = note.splitlines()
    if len(lines) < 3 or not lines[0]:
        raise RekorCheckpointStateError("invalid Rekor checkpoint")
    try:
        tree_size = int(lines[1])
        root = base64.b64decode(lines[2], validate=True)
    except (TypeError, ValueError) as exc:
        raise RekorCheckpointStateError("invalid Rekor checkpoint") from exc
    if tree_size <= 0 or len(root) != 32:
        raise RekorCheckpointStateError("invalid Rekor checkpoint")
    origin = lines[0]
    match = _TREE_ID.search(origin)
    return {
        "origin": origin,
        "tree_id": match.group(1) if match else None,
        "tree_size": tree_size,
        "root_hash": root.hex(),
    }


def verify_consistency_proof(
    *,
    previous_tree_size: int,
    previous_root_hash: str,
    tree_size: int,
    root_hash: str,
    hashes: list[str],
) -> bool:
    """Verify an RFC6962 append-only Merkle-tree consistency proof."""
    try:
        first = int(previous_tree_size)
        second = int(tree_size)
        first_root = _decode_hash(previous_root_hash)
        second_root = _decode_hash(root_hash)
        path = [_decode_hash(item) for item in hashes]
    except (TypeError, ValueError):
        return False

    if first <= 0 or second <= 0 or first > second:
        return False
    if first == second:
        return first_root == second_root and not path

    fn = first - 1
    sn = second - 1
    while fn & 1:
        fn >>= 1
        sn >>= 1

    if fn == 0:
        first_hash = first_root
        second_hash = first_root
    else:
        if not path:
            return False
        first_hash = path[0]
        second_hash = path[0]
        path = path[1:]

    for sibling in path:
        if sn == 0:
            return False
        if (fn & 1) or fn == sn:
            first_hash = _hash_children(sibling, first_hash)
            second_hash = _hash_children(sibling, second_hash)
            while fn != 0 and fn & 1 == 0:
                fn >>= 1
                sn >>= 1
        else:
            second_hash = _hash_children(second_hash, sibling)
        fn >>= 1
        sn >>= 1

    return (
        sn == 0
        and first_hash == first_root
        and second_hash == second_root
    )


class RekorV1ConsistencyClient:
    """Fetch Rekor v1 Merkle consistency proofs."""

    def __init__(
        self,
        base_url: str,
        *,
        timeout_seconds: float = 10.0,
    ) -> None:
        url = str(base_url).rstrip("/")
        if not url:
            raise ValueError("Rekor base URL is required")
        entries_suffix = "/api/v1/log/entries"
        log_suffix = "/api/v1/log"
        if url.endswith(entries_suffix):
            url = url[: -len("/entries")]
        elif not url.endswith(log_suffix):
            url += log_suffix
        self.proof_endpoint = url + "/proof"
        self.timeout_seconds = float(timeout_seconds)

    def fetch(
        self,
        *,
        first_size: int,
        last_size: int,
        tree_id: str | None = None,
    ) -> dict[str, Any]:
        params = {
            "firstSize": int(first_size),
            "lastSize": int(last_size),
        }
        if tree_id is not None:
            params["treeID"] = str(tree_id)
        request = Request(
            self.proof_endpoint + "?" + urlencode(params),
            headers={"Accept": "application/json"},
            method="GET",
        )
        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                status = int(response.status)
                raw = response.read()
        except (HTTPError, URLError, TimeoutError) as exc:
            raise RekorCheckpointStateError(
                f"Rekor consistency proof request failed: {exc}"
            ) from exc
        if status < 200 or status >= 300:
            raise RekorCheckpointStateError(
                f"Rekor consistency proof returned HTTP {status}"
            )
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise RekorCheckpointStateError(
                "Rekor consistency proof returned invalid JSON"
            ) from exc
        if not isinstance(payload, dict):
            raise RekorCheckpointStateError(
                "Rekor consistency proof must be an object"
            )
        root_hash = str(payload.get("rootHash") or "").lower()
        hashes = payload.get("hashes")
        if (
            not _HEX_64.fullmatch(root_hash)
            or not isinstance(hashes, list)
            or any(not _HEX_64.fullmatch(str(item)) for item in hashes)
        ):
            raise RekorCheckpointStateError(
                "invalid Rekor consistency proof response"
            )
        return {
            "rootHash": root_hash,
            "hashes": [str(item).lower() for item in hashes],
        }


class RekorCheckpointStateStore:
    """Persist one latest authenticated checkpoint per Rekor log/origin."""

    def __init__(self, backend: Any) -> None:
        self.backend = backend
        self._initialize()

    def _initialize(self) -> None:
        with self.backend.connect() as db:
            db.execute(
                """
                CREATE TABLE IF NOT EXISTS rekor_checkpoint_state (
                    log_id TEXT NOT NULL,
                    origin TEXT NOT NULL,
                    tree_id TEXT,
                    tree_size INTEGER NOT NULL,
                    root_hash TEXT NOT NULL,
                    checkpoint TEXT NOT NULL,
                    observed_at TEXT NOT NULL,
                    PRIMARY KEY(log_id, origin)
                )
                """
            )

    def get(self, log_id: str, origin: str) -> dict[str, Any] | None:
        with self.backend.connect() as db:
            row = db.execute(
                """
                SELECT log_id, origin, tree_id, tree_size, root_hash,
                       checkpoint, observed_at
                FROM rekor_checkpoint_state
                WHERE log_id=? AND origin=?
                """,
                (str(log_id).lower(), str(origin)),
            ).fetchone()
        if row is None:
            return None
        return {
            "log_id": row["log_id"],
            "origin": row["origin"],
            "tree_id": row["tree_id"],
            "tree_size": int(row["tree_size"]),
            "root_hash": row["root_hash"],
            "checkpoint": row["checkpoint"],
            "observed_at": row["observed_at"],
        }

    def put(
        self,
        *,
        log_id: str,
        origin: str,
        tree_size: int,
        root_hash: str,
        checkpoint: str,
        tree_id: str | None = None,
    ) -> dict[str, Any]:
        log_id_value = str(log_id).lower()
        root_hash_value = str(root_hash).lower()
        if not _HEX_64.fullmatch(log_id_value):
            raise RekorCheckpointStateError("invalid Rekor log ID")
        if not _HEX_64.fullmatch(root_hash_value):
            raise RekorCheckpointStateError("invalid Rekor root hash")
        if int(tree_size) <= 0:
            raise RekorCheckpointStateError("invalid Rekor tree size")
        observed_at = _utcnow()
        with self.backend.transaction() as db:
            db.execute(
                """
                INSERT INTO rekor_checkpoint_state(
                    log_id, origin, tree_id, tree_size, root_hash,
                    checkpoint, observed_at
                )
                VALUES(?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(log_id, origin) DO UPDATE SET
                    tree_id=excluded.tree_id,
                    tree_size=excluded.tree_size,
                    root_hash=excluded.root_hash,
                    checkpoint=excluded.checkpoint,
                    observed_at=excluded.observed_at
                """,
                (
                    log_id_value,
                    str(origin),
                    tree_id,
                    int(tree_size),
                    root_hash_value,
                    str(checkpoint),
                    observed_at,
                ),
            )
        stored = self.get(log_id_value, str(origin))
        if stored is None:
            raise RekorCheckpointStateError("failed to persist Rekor checkpoint")
        return stored


class RekorCheckpointMonitor:
    def __init__(
        self,
        store: RekorCheckpointStateStore,
        *,
        proof_fetcher: Callable[..., dict[str, Any]],
    ) -> None:
        self.store = store
        self.proof_fetcher = proof_fetcher

    def observe_verified_receipt(self, receipt: dict[str, Any]) -> dict[str, Any]:
        if receipt.get("provider") != "rekor-v1":
            raise RekorCheckpointStateError("unsupported transparency provider")
        log_id = str(receipt.get("log_id") or "").lower()
        if not _HEX_64.fullmatch(log_id):
            raise RekorCheckpointStateError("invalid Rekor log ID")
        proof = receipt.get("inclusion_proof")
        if not isinstance(proof, dict):
            raise RekorCheckpointStateError("Rekor inclusion proof is required")
        checkpoint = proof.get("checkpoint")
        identity = parse_checkpoint_identity(checkpoint)
        try:
            proof_size = int(proof["treeSize"])
            proof_root = str(proof["rootHash"]).lower()
        except (KeyError, TypeError, ValueError) as exc:
            raise RekorCheckpointStateError("invalid Rekor inclusion proof") from exc
        if (
            identity["tree_size"] != proof_size
            or identity["root_hash"] != proof_root
        ):
            raise RekorCheckpointStateError(
                "Rekor checkpoint does not match inclusion proof"
            )

        origin = str(identity["origin"])
        previous = self.store.get(log_id, origin)
        if previous is None:
            current = self.store.put(
                log_id=log_id,
                origin=origin,
                tree_id=identity["tree_id"],
                tree_size=proof_size,
                root_hash=proof_root,
                checkpoint=str(checkpoint),
            )
            return {"status": "bootstrapped", "checkpoint": current}

        previous_size = int(previous["tree_size"])
        previous_root = str(previous["root_hash"]).lower()
        if proof_size < previous_size:
            raise RekorCheckpointStateError("Rekor tree rollback detected")
        if proof_size == previous_size:
            if proof_root != previous_root:
                raise RekorCheckpointStateError("Rekor split-view detected")
            return {"status": "unchanged", "checkpoint": previous}

        consistency = self.proof_fetcher(
            first_size=previous_size,
            last_size=proof_size,
            tree_id=identity["tree_id"],
        )
        if not isinstance(consistency, dict):
            raise RekorCheckpointStateError("invalid Rekor consistency proof")
        hashes = consistency.get("hashes")
        response_root = str(consistency.get("rootHash") or "").lower()
        if (
            response_root != proof_root
            or not isinstance(hashes, list)
            or not verify_consistency_proof(
                previous_tree_size=previous_size,
                previous_root_hash=previous_root,
                tree_size=proof_size,
                root_hash=proof_root,
                hashes=[str(item) for item in hashes],
            )
        ):
            raise RekorCheckpointStateError("invalid Rekor consistency proof")

        current = self.store.put(
            log_id=log_id,
            origin=origin,
            tree_id=identity["tree_id"],
            tree_size=proof_size,
            root_hash=proof_root,
            checkpoint=str(checkpoint),
        )
        return {"status": "advanced", "checkpoint": current}
