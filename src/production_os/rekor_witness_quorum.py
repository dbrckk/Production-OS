from __future__ import annotations

from typing import Any

from .signing import SigningError, verify_payload


REKOR_WITNESS_SCHEMA = "production-os/rekor-witness-observation/v1"


class RekorWitnessQuorumError(RuntimeError):
    pass


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
