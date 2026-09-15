from __future__ import annotations

from typing import Any

from .asymmetric_attestations import (
    create_validation_attestation as create_v2,
    verify_validation_attestation as verify_v2,
)
from .attestations import (
    AttestationError,
    create_validation_attestation as create_v1,
    verify_validation_attestation as verify_v1,
)


DUAL_SCHEMA = "production-os/validation-attestation-bundle/v1"


class DualSignError(ValueError):
    pass


def create_dual_attestation(
    *,
    validator_id: str,
    hmac_secret: str,
    private_key_pem: str,
    workflow_id: str,
    artifact_id: str,
    artifact_sha256: str,
    source_revision: str | None,
    workflow_generation: int | None,
    validation: dict[str, Any],
    issued_at: str | None = None,
) -> dict[str, Any]:
    common = dict(
        validator_id=validator_id,
        workflow_id=workflow_id,
        artifact_id=artifact_id,
        artifact_sha256=artifact_sha256,
        source_revision=source_revision,
        workflow_generation=workflow_generation,
        validation=validation,
        issued_at=issued_at,
    )
    return {
        "schema_version":DUAL_SCHEMA,
        "validator_id":validator_id,
        "hmac":create_v1(
            secret=hmac_secret,
            **common,
        ),
        "ed25519":create_v2(
            private_key_pem=private_key_pem,
            **common,
        ),
    }


def verify_dual_attestation(
    bundle: dict[str, Any],
    *,
    trusted_secrets: dict[str, str],
    trusted_public_keys: dict[str, Any],
    workflow_id: str,
    artifact_id: str,
    artifact_sha256: str,
    source_revision: str | None,
    workflow_generation: int | None,
    validation: dict[str, Any],
    max_age_seconds: int = 3600,
) -> dict[str, Any]:
    if bundle.get("schema_version") != DUAL_SCHEMA:
        raise DualSignError("unsupported dual-sign schema")
    hmac = dict(bundle.get("hmac") or {})
    ed25519 = dict(bundle.get("ed25519") or {})
    if not hmac or not ed25519:
        raise DualSignError(
            "dual-sign bundle requires HMAC and Ed25519 attestations"
        )
    kwargs = dict(
        workflow_id=workflow_id,
        artifact_id=artifact_id,
        artifact_sha256=artifact_sha256,
        source_revision=source_revision,
        workflow_generation=workflow_generation,
        validation=validation,
        max_age_seconds=max_age_seconds,
    )
    try:
        verified_hmac = verify_v1(
            hmac,
            trusted_secrets=trusted_secrets,
            **kwargs,
        )
        verified_ed25519 = verify_v2(
            ed25519,
            trusted_public_keys=trusted_public_keys,
            **kwargs,
        )
    except (AttestationError, ValueError) as exc:
        raise DualSignError(str(exc)) from exc
    if verified_hmac["validator_id"] != (
        verified_ed25519["validator_id"]
    ):
        raise DualSignError("dual-sign validator identity mismatch")
    if bundle.get("validator_id") != verified_hmac["validator_id"]:
        raise DualSignError("dual-sign bundle identity mismatch")
    return {
        "schema_version":DUAL_SCHEMA,
        "validator_id":verified_hmac["validator_id"],
        "hmac":verified_hmac,
        "ed25519":verified_ed25519,
        "verified":True,
    }
