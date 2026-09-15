from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .signing import SigningError, verify_payload


REKOR_WITNESS_SCHEMA = "production-os/rekor-witness-observation/v1"
REKOR_WITNESS_REQUEST_SCHEMA = "production-os/rekor-witness-request/v1"


class RekorWitnessQuorumError(RuntimeError):
    pass


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


class RekorWitnessClient:
    def __init__(
        self,
        url: str,
        *,
        timeout_seconds: float = 10.0,
    ) -> None:
        self.url = str(url).strip()
        if not self.url:
            raise ValueError("Rekor witness URL is required")
        self.timeout_seconds = float(timeout_seconds)

    def observe(
        self,
        *,
        log_id: str,
        origin: str,
        tree_size: int,
        root_hash: str,
    ) -> dict[str, Any]:
        payload = {
            "schema_version": REKOR_WITNESS_REQUEST_SCHEMA,
            "log_id": str(log_id).lower(),
            "origin": str(origin),
            "tree_size": int(tree_size),
            "root_hash": str(root_hash).lower(),
        }
        request = Request(
            self.url,
            data=json.dumps(
                payload,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            method="POST",
        )
        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                status = int(response.status)
                raw = response.read()
        except (HTTPError, URLError, TimeoutError) as exc:
            raise RekorWitnessQuorumError(
                f"Rekor witness request failed: {exc}"
            ) from exc
        if status < 200 or status >= 300:
            raise RekorWitnessQuorumError(
                f"Rekor witness returned HTTP {status}"
            )
        try:
            decoded = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise RekorWitnessQuorumError(
                "Rekor witness returned invalid JSON"
            ) from exc
        if not isinstance(decoded, dict):
            raise RekorWitnessQuorumError(
                "Rekor witness response must be an object"
            )
        return decoded


class RekorWitnessObservationStore:
    def __init__(self, backend: Any) -> None:
        self.backend = backend
        self._initialize()

    def _is_postgres(self) -> bool:
        return self.backend.__class__.__name__.startswith("Postgres")

    def _sql(self, statement: str) -> str:
        return statement.replace("?", "%s") if self._is_postgres() else statement

    def _initialize(self) -> None:
        with self.backend.connect() as db:
            db.execute(
                """
                CREATE TABLE IF NOT EXISTS rekor_witness_observations (
                    id TEXT PRIMARY KEY,
                    witness_id TEXT NOT NULL,
                    log_id TEXT NOT NULL,
                    origin TEXT NOT NULL,
                    tree_size BIGINT NOT NULL,
                    root_hash TEXT NOT NULL,
                    verdict TEXT NOT NULL,
                    response_json TEXT NOT NULL,
                    observed_at TEXT NOT NULL
                )
                """
            )
            db.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_rekor_witness_tree
                ON rekor_witness_observations(
                    log_id, origin, tree_size, observed_at
                )
                """
            )

    def record(
        self,
        *,
        response: dict[str, Any],
        verdict: str,
    ) -> dict[str, Any]:
        observation = response.get("observation")
        if not isinstance(observation, dict):
            raise RekorWitnessQuorumError(
                "Rekor witness observation is required"
            )
        witness_id = str(observation.get("witness_id") or "")
        log_id = str(observation.get("log_id") or "").lower()
        origin = str(observation.get("origin") or "")
        root_hash = str(observation.get("root_hash") or "").lower()
        try:
            tree_size = int(observation.get("tree_size"))
        except (TypeError, ValueError) as exc:
            raise RekorWitnessQuorumError(
                "invalid Rekor witness tree size"
            ) from exc
        if not witness_id or not log_id or not origin or tree_size <= 0 or not root_hash:
            raise RekorWitnessQuorumError("invalid Rekor witness observation")
        row = {
            "id": str(uuid.uuid4()),
            "witness_id": witness_id,
            "log_id": log_id,
            "origin": origin,
            "tree_size": tree_size,
            "root_hash": root_hash,
            "verdict": str(verdict),
            "response": response,
            "observed_at": _utcnow(),
        }
        with self.backend.transaction() as db:
            db.execute(
                self._sql(
                    """
                    INSERT INTO rekor_witness_observations(
                        id, witness_id, log_id, origin, tree_size,
                        root_hash, verdict, response_json, observed_at
                    ) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """
                ),
                (
                    row["id"],
                    row["witness_id"],
                    row["log_id"],
                    row["origin"],
                    row["tree_size"],
                    row["root_hash"],
                    row["verdict"],
                    json.dumps(
                        response,
                        sort_keys=True,
                        separators=(",", ":"),
                        ensure_ascii=False,
                    ),
                    row["observed_at"],
                ),
            )
        return row

    def list_for_tree(
        self,
        *,
        log_id: str,
        origin: str,
        tree_size: int,
    ) -> list[dict[str, Any]]:
        with self.backend.connect() as db:
            rows = db.execute(
                self._sql(
                    """
                    SELECT id, witness_id, log_id, origin, tree_size,
                           root_hash, verdict, response_json, observed_at
                    FROM rekor_witness_observations
                    WHERE log_id=? AND origin=? AND tree_size=?
                    ORDER BY observed_at ASC, id ASC
                    """
                ),
                (str(log_id).lower(), str(origin), int(tree_size)),
            ).fetchall()
        return [
            {
                "id": row["id"],
                "witness_id": row["witness_id"],
                "log_id": row["log_id"],
                "origin": row["origin"],
                "tree_size": int(row["tree_size"]),
                "root_hash": row["root_hash"],
                "verdict": row["verdict"],
                "response": json.loads(row["response_json"]),
                "observed_at": row["observed_at"],
            }
            for row in rows
        ]


def _observation_matches_expected(
    observation: dict[str, Any],
    *,
    expected_log_id: str,
    expected_origin: str,
    expected_tree_size: int,
    expected_root_hash: str,
) -> bool:
    try:
        return (
            str(observation.get("log_id") or "").lower()
            == str(expected_log_id).lower()
            and str(observation.get("origin") or "") == str(expected_origin)
            and int(observation.get("tree_size")) == int(expected_tree_size)
            and str(observation.get("root_hash") or "").lower()
            == str(expected_root_hash).lower()
        )
    except (TypeError, ValueError):
        return False


def evaluate_rekor_witness_quorum(
    responses: list[dict[str, Any]],
    *,
    public_keys: dict[str, str],
    threshold: int,
    expected_log_id: str,
    expected_origin: str,
    expected_tree_size: int,
    expected_root_hash: str,
) -> dict[str, Any]:
    required = int(threshold)
    if required <= 0:
        raise RekorWitnessQuorumError("witness threshold must be positive")
    if required > len(public_keys):
        raise RekorWitnessQuorumError(
            "witness threshold exceeds configured witnesses"
        )

    valid_witnesses: list[str] = []
    rejected_witnesses: list[str] = []
    conflicting_witnesses: list[str] = []
    seen: set[str] = set()

    for response in responses:
        if not isinstance(response, dict):
            continue
        observation = response.get("observation")
        signature = response.get("signature")
        if not isinstance(observation, dict) or not isinstance(signature, dict):
            continue
        witness_id = str(observation.get("witness_id") or "")
        if not witness_id or witness_id in seen:
            if witness_id and witness_id not in rejected_witnesses:
                rejected_witnesses.append(witness_id)
            continue
        seen.add(witness_id)
        public_key = public_keys.get(witness_id)
        if public_key is None:
            rejected_witnesses.append(witness_id)
            continue
        if observation.get("schema_version") != REKOR_WITNESS_SCHEMA:
            rejected_witnesses.append(witness_id)
            continue
        try:
            signature_valid = verify_payload(
                public_key,
                observation,
                signature,
            )
        except (SigningError, TypeError, ValueError):
            signature_valid = False
        if not signature_valid:
            rejected_witnesses.append(witness_id)
            continue

        try:
            same_tree_identity = (
                str(observation.get("log_id") or "").lower()
                == str(expected_log_id).lower()
                and str(observation.get("origin") or "") == str(expected_origin)
                and int(observation.get("tree_size")) == int(expected_tree_size)
            )
        except (TypeError, ValueError):
            same_tree_identity = False

        if same_tree_identity and (
            str(observation.get("root_hash") or "").lower()
            != str(expected_root_hash).lower()
        ):
            conflicting_witnesses.append(witness_id)
            continue

        if _observation_matches_expected(
            observation,
            expected_log_id=expected_log_id,
            expected_origin=expected_origin,
            expected_tree_size=expected_tree_size,
            expected_root_hash=expected_root_hash,
        ):
            valid_witnesses.append(witness_id)
        else:
            rejected_witnesses.append(witness_id)

    if conflicting_witnesses:
        return {
            "valid": False,
            "required": required,
            "valid_witnesses": valid_witnesses,
            "rejected_witnesses": rejected_witnesses,
            "conflicting_witnesses": conflicting_witnesses,
            "reason": "conflicting Rekor witness observation",
        }

    valid = len(valid_witnesses) >= required
    return {
        "valid": valid,
        "required": required,
        "valid_witnesses": valid_witnesses,
        "rejected_witnesses": rejected_witnesses,
        "conflicting_witnesses": [],
        "reason": None if valid else "witness quorum not reached",
    }
