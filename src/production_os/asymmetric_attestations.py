from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from .attestations import release_approval_key
from .signing import SigningError, sign_payload, verify_payload


ATTESTATION_SCHEMA = "production-os/validation-attestation/v2"
PROVENANCE_SCHEMA = "production-os/release-provenance/v2"


class AsymmetricAttestationError(ValueError):
    pass


def create_validation_attestation(
    *,
    validator_id: str,
    private_key_pem: str,
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
        "signature":sign_payload(private_key_pem, payload),
    }


def verify_validation_attestation(
    attestation: dict[str, Any],
    *,
    trusted_public_keys: dict[str, str],
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
    signature = dict(payload.pop("signature", {}) or {})
    if payload.get("schema_version") != ATTESTATION_SCHEMA:
        raise AsymmetricAttestationError(
            "unsupported asymmetric validation attestation schema"
        )
    validator_id = str(payload.get("validator_id") or "")
    public_key = trusted_public_keys.get(validator_id)
    if not validator_id or not public_key:
        raise AsymmetricAttestationError(
            "untrusted validation attestation producer"
        )

    issued_raw = str(payload.get("issued_at") or "")
    try:
        issued_at = datetime.fromisoformat(
            issued_raw.replace("Z", "+00:00")
        )
    except ValueError as exc:
        raise AsymmetricAttestationError(
            "invalid validation attestation issued_at"
        ) from exc
    if issued_at.tzinfo is None:
        raise AsymmetricAttestationError(
            "validation attestation issued_at must be timezone-aware"
        )
    now = datetime.now(timezone.utc)
    if issued_at > now + timedelta(seconds=future_skew_seconds):
        raise AsymmetricAttestationError(
            "validation attestation issued_at is in the future"
        )
    if (
        max_age_seconds >= 0
        and now - issued_at > timedelta(seconds=max_age_seconds)
    ):
        raise AsymmetricAttestationError(
            "validation attestation expired"
        )

    expected = {
        "workflow_id":str(workflow_id),
        "artifact_id":str(artifact_id),
        "artifact_sha256":str(artifact_sha256),
        "source_revision":source_revision,
        "workflow_generation":workflow_generation,
        "validation":validation,
    }
    for key, value in expected.items():
        if payload.get(key) != value:
            raise AsymmetricAttestationError(
                f"validation attestation binding mismatch: {key}"
            )
    try:
        valid = verify_payload(public_key, payload, signature)
    except SigningError as exc:
        raise AsymmetricAttestationError(str(exc)) from exc
    if not valid:
        raise AsymmetricAttestationError(
            "invalid validation attestation signature"
        )
    return {
        **payload,
        "signature":signature,
        "verified":True,
    }


def create_release_provenance(
    *,
    private_key_pem: str,
    release: dict[str, Any],
    attestation: dict[str, Any],
) -> dict[str, Any]:
    approval = release["metadata"]["approval"]
    expected_key = release_approval_key(
        workflow_id=release["workflow_id"],
        artifact_id=release["artifact_id"],
        artifact_sha256=release["metadata"]["artifact_sha256"],
        source_revision=release.get("source_revision"),
        workflow_generation=release.get("workflow_generation"),
    )
    if approval["approval_key"] != expected_key:
        raise AsymmetricAttestationError(
            "release approval binding mismatch"
        )
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
        "validation_attestation_key_id":
            attestation["signature"]["key_id"],
        "validation_attestation_signature":
            attestation["signature"]["signature"],
        "approval_key":approval["approval_key"],
        "approved_by":approval["approved_by"],
        "approval_role":approval["role"],
        "created_at":release["created_at"],
    }
    return {
        **payload,
        "signature":sign_payload(private_key_pem, payload),
    }


def verify_release_provenance(
    provenance: dict[str, Any],
    *,
    public_key_pem: str,
) -> bool:
    payload = dict(provenance)
    signature = dict(payload.pop("signature", {}) or {})
    if payload.get("schema_version") != PROVENANCE_SCHEMA:
        return False
    try:
        return verify_payload(public_key_pem, payload, signature)
    except SigningError:
        return False
