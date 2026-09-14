import pytest

from production_os.attestations import (
    AttestationError,
    create_release_provenance,
    create_validation_attestation,
    verify_release_provenance,
    verify_validation_attestation,
)


def validation():
    return {
        "status":"passed",
        "promotion_allowed":True,
        "blocking_failures":[],
    }


def test_validation_attestation_verifies_exact_bindings():
    attestation=create_validation_attestation(
        validator_id="validator-1",
        secret="secret",
        workflow_id="wf-1",
        artifact_id="artifact-1",
        artifact_sha256="a"*64,
        source_revision="sha-1",
        workflow_generation=3,
        validation=validation(),
        issued_at="2026-09-14T20:00:00+00:00",
    )

    verified=verify_validation_attestation(
        attestation,
        trusted_secrets={"validator-1":"secret"},
        workflow_id="wf-1",
        artifact_id="artifact-1",
        artifact_sha256="a"*64,
        source_revision="sha-1",
        workflow_generation=3,
        validation=validation(),
    )

    assert verified["verified"] is True


def test_validation_attestation_rejects_binding_change():
    attestation=create_validation_attestation(
        validator_id="validator-1",
        secret="secret",
        workflow_id="wf-1",
        artifact_id="artifact-1",
        artifact_sha256="a"*64,
        source_revision="sha-1",
        workflow_generation=3,
        validation=validation(),
    )

    with pytest.raises(AttestationError,match="artifact_sha256"):
        verify_validation_attestation(
            attestation,
            trusted_secrets={"validator-1":"secret"},
            workflow_id="wf-1",
            artifact_id="artifact-1",
            artifact_sha256="b"*64,
            source_revision="sha-1",
            workflow_generation=3,
            validation=validation(),
        )


def test_validation_attestation_rejects_untrusted_validator():
    attestation=create_validation_attestation(
        validator_id="validator-2",
        secret="secret",
        workflow_id="wf-1",
        artifact_id="artifact-1",
        artifact_sha256="a"*64,
        source_revision=None,
        workflow_generation=None,
        validation=validation(),
    )

    with pytest.raises(AttestationError,match="untrusted"):
        verify_validation_attestation(
            attestation,
            trusted_secrets={"validator-1":"other"},
            workflow_id="wf-1",
            artifact_id="artifact-1",
            artifact_sha256="a"*64,
            source_revision=None,
            workflow_generation=None,
            validation=validation(),
        )


def test_release_provenance_detects_tampering():
    attestation=create_validation_attestation(
        validator_id="validator-1",
        secret="validator-secret",
        workflow_id="wf-1",
        artifact_id="artifact-1",
        artifact_sha256="a"*64,
        source_revision="sha-1",
        workflow_generation=1,
        validation=validation(),
    )
    release={
        "id":"release-1",
        "workflow_id":"wf-1",
        "artifact_id":"artifact-1",
        "repository":"o/a",
        "source_revision":"sha-1",
        "workflow_generation":1,
        "metadata":{"artifact_sha256":"a"*64},
        "created_at":"2026-09-14T20:00:00+00:00",
    }
    provenance=create_release_provenance(
        secret="provenance-secret",
        release=release,
        attestation=attestation,
    )

    assert verify_release_provenance(
        provenance,
        secret="provenance-secret",
    ) is True

    provenance["artifact_sha256"]="b"*64
    assert verify_release_provenance(
        provenance,
        secret="provenance-secret",
    ) is False
