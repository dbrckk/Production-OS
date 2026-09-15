from datetime import datetime, timedelta, timezone

import pytest

from production_os.asymmetric_attestations import (
    AsymmetricAttestationError,
    create_validation_attestation,
    verify_validation_attestation,
)
from production_os.signing import generate_keypair, key_id, load_public_key


def validation():
    return {
        "status": "passed",
        "promotion_allowed": True,
        "blocking_failures": [],
    }


def make_attestation(private_key, *, issued_at):
    return create_validation_attestation(
        validator_id="validator-prod",
        private_key_pem=private_key,
        workflow_id="workflow-1",
        artifact_id="artifact-1",
        artifact_sha256="a" * 64,
        source_revision="revision-1",
        workflow_generation=1,
        validation=validation(),
        issued_at=issued_at,
    )


def verify(attestation, registry):
    return verify_validation_attestation(
        attestation,
        trusted_public_keys=registry,
        workflow_id="workflow-1",
        artifact_id="artifact-1",
        artifact_sha256="a" * 64,
        source_revision="revision-1",
        workflow_generation=1,
        validation=validation(),
        max_age_seconds=3600,
    )


def test_validator_key_rotation_accepts_old_and_new_keys_in_their_windows():
    old_private, old_public = generate_keypair()
    new_private, new_public = generate_keypair()
    now = datetime.now(timezone.utc)
    rotation = now - timedelta(minutes=20)

    registry = {
        "validator-prod": [
            {
                "public_key": old_public,
                "not_after": rotation.isoformat(),
            },
            {
                "public_key": new_public,
                "not_before": rotation.isoformat(),
            },
        ]
    }

    old_attestation = make_attestation(
        old_private,
        issued_at=(rotation - timedelta(minutes=5)).isoformat(),
    )
    new_attestation = make_attestation(
        new_private,
        issued_at=(rotation + timedelta(minutes=5)).isoformat(),
    )

    assert verify(old_attestation, registry)["verified"] is True
    assert verify(new_attestation, registry)["verified"] is True


def test_validator_key_rotation_rejects_old_key_after_cutover():
    old_private, old_public = generate_keypair()
    _, new_public = generate_keypair()
    now = datetime.now(timezone.utc)
    rotation = now - timedelta(minutes=20)

    registry = {
        "validator-prod": [
            {
                "public_key": old_public,
                "not_after": rotation.isoformat(),
            },
            {
                "public_key": new_public,
                "not_before": rotation.isoformat(),
            },
        ]
    }
    attestation = make_attestation(
        old_private,
        issued_at=(rotation + timedelta(minutes=5)).isoformat(),
    )

    with pytest.raises(AsymmetricAttestationError, match="expired"):
        verify(attestation, registry)


def test_revoked_validator_key_is_rejected_at_and_after_revocation():
    private_key, public_key = generate_keypair()
    now = datetime.now(timezone.utc)
    revoked_at = now - timedelta(minutes=20)
    attestation = make_attestation(
        private_key,
        issued_at=(revoked_at + timedelta(minutes=5)).isoformat(),
    )
    registry = {
        "validator-prod": {
            "public_key": public_key,
            "revoked_at": revoked_at.isoformat(),
        }
    }

    with pytest.raises(AsymmetricAttestationError, match="revoked"):
        verify(attestation, registry)


def test_registry_rejects_key_id_that_does_not_match_public_key():
    private_key, public_key = generate_keypair()
    attestation = make_attestation(
        private_key,
        issued_at=datetime.now(timezone.utc).isoformat(),
    )
    registry = {
        "validator-prod": {
            "public_key": public_key,
            "key_id": "sha256:" + "0" * 64,
        }
    }

    with pytest.raises(
        AsymmetricAttestationError,
        match="key_id does not match public key",
    ):
        verify(attestation, registry)


def test_generated_signature_key_id_matches_registry_identity():
    private_key, public_key = generate_keypair()
    attestation = make_attestation(
        private_key,
        issued_at=datetime.now(timezone.utc).isoformat(),
    )

    assert attestation["signature"]["key_id"] == key_id(
        load_public_key(public_key)
    )
