from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
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


def load_rekor_witness_config(path: str | Path) -> dict[str, Any]:
    config_path = Path(path)
    try:
        payload = json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RekorWitnessQuorumError(
            f"invalid Rekor witness configuration: {exc}"
        ) from exc
    if not isinstance(payload, dict):
        raise RekorWitnessQuorumError(
            "Rekor witness configuration must be an object"
        )
    try:
        threshold = int(payload.get("threshold"))
    except (TypeError, ValueError) as exc:
        raise RekorWitnessQuorumError(
            "invalid Rekor witness threshold"
        ) from exc
    raw_witnesses = payload.get("witnesses")
    if threshold <= 0 or not isinstance(raw_witnesses, list) or not raw_witnesses:
        raise RekorWitnessQuorumError("invalid Rekor witness configuration")

    witnesses: list[dict[str, str]] = []
    seen_ids: set[str] = set()
    for item in raw_witnesses:
        if not isinstance(item, dict):
            raise RekorWitnessQuorumError("invalid Rekor witness configuration")
        witness_id = str(item.get("id") or "").strip()
        url = str(item.get("url") or "").strip()
        if not witness_id or witness_id in seen_ids or not url:
            raise RekorWitnessQuorumError("invalid Rekor witness configuration")
        seen_ids.add(witness_id)
        inline_key = item.get("public_key")
        key_path_value = item.get("public_key_path")
        if inline_key is not None:
            public_key = str(inline_key)
        elif key_path_value:
            key_path = Path(str(key_path_value))
            if not key_path.is_absolute():
                key_path = config_path.parent / key_path
            try:
                public_key = key_path.read_text(encoding="ascii")
            except (OSError, UnicodeError) as exc:
                raise RekorWitnessQuorumError(
                    f"cannot read Rekor witness public key for {witness_id}: {exc}"
                ) from exc
        else:
            raise RekorWitnessQuorumError(
                f"Rekor witness public key is required for {witness_id}"
            )
        if not public_key.strip():
            raise RekorWitnessQuorumError(
                f"Rekor witness public key is required for {witness_id}"
            )
        witnesses.append(
            {
                "id": witness_id,
                "url": url,
                "public_key": public_key,
            }
        )

    if threshold > len(witnesses):
        raise RekorWitnessQuorumError(
            "witness threshold exceeds configured witnesses"
        )
    return {"threshold": threshold, "witnesses": witnesses}


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


def collect_rekor_witness_quorum(
    config: dict[str, Any],
    *,
    log_id: str,
    origin: str,
    tree_size: int,
    root_hash: str,
    store: RekorWitnessObservationStore | None = None,
) -> dict[str, Any]:
    raw_witnesses = config.get("witnesses")
    if not isinstance(raw_witnesses, list) or not raw_witnesses:
        raise RekorWitnessQuorumError("invalid Rekor witness configuration")
    try:
        threshold = int(config.get("threshold"))
    except (TypeError, ValueError) as exc:
        raise RekorWitnessQuorumError("invalid Rekor witness threshold") from exc

    public_keys: dict[str, str] = {}
    responses: list[dict[str, Any]] = []
    responses_by_id: dict[str, dict[str, Any]] = {}
    errors: dict[str, str] = {}

    for item in raw_witnesses:
        if not isinstance(item, dict):
            raise RekorWitnessQuorumError("invalid Rekor witness configuration")
        witness_id = str(item.get("id") or "").strip()
        url = str(item.get("url") or "").strip()
        public_key = str(item.get("public_key") or "")
        if not witness_id or not url or not public_key:
            raise RekorWitnessQuorumError("invalid Rekor witness configuration")
        if witness_id in public_keys:
            raise RekorWitnessQuorumError("duplicate Rekor witness ID")
        public_keys[witness_id] = public_key
        try:
            response = RekorWitnessClient(url).observe(
                log_id=log_id,
                origin=origin,
                tree_size=tree_size,
                root_hash=root_hash,
            )
        except RekorWitnessQuorumError as exc:
            errors[witness_id] = str(exc)
            continue
        observation = response.get("observation")
        returned_id = (
            str(observation.get("witness_id") or "")
            if isinstance(observation, dict)
            else ""
        )
        if returned_id != witness_id:
            errors[witness_id] = "Rekor witness identity mismatch"
            continue
        responses.append(response)
        responses_by_id[witness_id] = response

    result = evaluate_rekor_witness_quorum(
        responses,
        public_keys=public_keys,
        threshold=threshold,
        expected_log_id=log_id,
        expected_origin=origin,
        expected_tree_size=tree_size,
        expected_root_hash=root_hash,
    )
    result["errors"] = errors

    if store is not None:
        valid_ids = set(result["valid_witnesses"])
        rejected_ids = set(result["rejected_witnesses"])
        conflicting_ids = set(result["conflicting_witnesses"])
        for witness_id, response in responses_by_id.items():
            if witness_id in valid_ids:
                verdict = "valid"
            elif witness_id in conflicting_ids:
                verdict = "conflicting"
            elif witness_id in rejected_ids:
                verdict = "rejected"
            else:
                verdict = "rejected"
            store.record(response=response, verdict=verdict)

    return result
