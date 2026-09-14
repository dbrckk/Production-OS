from __future__ import annotations

import hashlib
import hmac
import json
from datetime import datetime, timedelta, timezone
from typing import Any


ATTESTATION_SCHEMA = "production-os/validation-attestation/v1"
PROVENANCE_SCHEMA = "production-os/release-provenance/v1"


class AttestationError(ValueError):
    pass


def _canonical(payload: dict[str, Any]) -> bytes:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def _sign(secret: str, payload: dict[str, Any]) -> str:
    if not secret:
        raise AttestationError("signing secret is required")
    return hmac.new(
        secret.encode("utf-8"),
        _canonical(payload),
        hashlib.sha256,
    ).hexdigest()


def create_validation_attestation(
    *,
    validator_id: str,
    secret: str,
    workflow_id: str,
    artifact_id: str,
    artifact_sha256: str,
    source_revision: str | None,
    workflow_generation: int | None,
    validation: dict[str, Any],
    issued_at: str | None = None,
) -> dict[str, Any]:
    payload = {
        "schema_version":ATTESTATION_SCHEMA,
        "validator_id":str(validator_id),
        "issued_at":issued_at
        or datetime.now(timezone.utc).isoformat(),
        "workflow_id":str(workflow_id),
        "artifact_id":str(artifact_id),
        "artifact_sha256":str(artifact_sha256),
        "source_revision":source_revision,
        "workflow_generation":workflow_generation,
        "validation":validation,
    }
    return {
        **payload,
        "signature":_sign(secret, payload),
    }


def verify_validation_attestation(
    attestation: dict[str, Any],
    *,
    trusted_secrets: dict[str, str],
    workflow_id: str,
    artifact_id: str,
    artifact_sha256: str,
    source_revision: str | None,
    workflow_generation: int | None,
    validation: dict[str, Any],
    max_age_seconds: int = 3600,
    future_skew_seconds: int = 300,
) -> dict[str, Any]:
    payload = dict(attestation)
    signature = str(payload.pop("signature", ""))
    if payload.get("schema_version") != ATTESTATION_SCHEMA:
        raise AttestationError("unsupported validation attestation schema")

    validator_id = str(payload.get("validator_id") or "")
    secret = trusted_secrets.get(validator_id)
    if not validator_id or not secret:
        raise AttestationError("untrusted validation attestation producer")

    issued_raw = str(payload.get("issued_at") or "")
    try:
        issued_at = datetime.fromisoformat(
            issued_raw.replace("Z", "+00:00")
        )
    except ValueError as exc:
        raise AttestationError(
            "invalid validation attestation issued_at"
        ) from exc
    if issued_at.tzinfo is None:
        raise AttestationError(
            "validation attestation issued_at must be timezone-aware"
        )
    now = datetime.now(timezone.utc)
    if issued_at > now + timedelta(seconds=future_skew_seconds):
        raise AttestationError(
            "validation attestation issued_at is in the future"
        )
    if (
        max_age_seconds >= 0
        and now - issued_at > timedelta(seconds=max_age_seconds)
    ):
        raise AttestationError("validation attestation expired")

    expected_bindings = {
        "workflow_id":str(workflow_id),
        "artifact_id":str(artifact_id),
        "artifact_sha256":str(artifact_sha256),
        "source_revision":source_revision,
        "workflow_generation":workflow_generation,
        "validation":validation,
    }
    for key, expected in expected_bindings.items():
        if payload.get(key) != expected:
            raise AttestationError(
                f"validation attestation binding mismatch: {key}"
            )

    expected = _sign(secret, payload)
    if not hmac.compare_digest(signature, expected):
        raise AttestationError("invalid validation attestation signature")

    return {
        **payload,
        "signature":signature,
        "verified":True,
    }


def create_release_provenance(
    *,
    secret: str,
    release: dict[str, Any],
    attestation: dict[str, Any],
) -> dict[str, Any]:
    payload = {
        "schema_version":PROVENANCE_SCHEMA,
        "release_id":release["id"],
        "workflow_id":release["workflow_id"],
        "artifact_id":release["artifact_id"],
        "repository":release["repository"],
        "artifact_sha256":release["metadata"]["artifact_sha256"],
        "source_revision":release.get("source_revision"),
        "workflow_generation":release.get("workflow_generation"),
        "validator_id":attestation["validator_id"],
        "validation_attestation_signature":attestation["signature"],
        "created_at":release["created_at"],
    }
    return {
        **payload,
        "signature":_sign(secret, payload),
    }


def verify_release_provenance(
    provenance: dict[str, Any],
    *,
    secret: str,
) -> bool:
    payload = dict(provenance)
    signature = str(payload.pop("signature", ""))
    if payload.get("schema_version") != PROVENANCE_SCHEMA:
        return False
    return hmac.compare_digest(
        signature,
        _sign(secret, payload),
    )
