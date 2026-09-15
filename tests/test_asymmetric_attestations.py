from production_os.asymmetric_attestations import (
    create_release_provenance,
    create_validation_attestation,
    verify_release_provenance,
    verify_validation_attestation,
)
from production_os.attestations import release_approval_key
from production_os.signing import generate_keypair


def validation():
    return {
        "status":"passed",
        "promotion_allowed":True,
        "blocking_failures":[],
    }


def test_public_key_validation_attestation():
    private_key,public_key=generate_keypair()
    attestation=create_validation_attestation(
        validator_id="validator-1",
        private_key_pem=private_key,
        workflow_id="wf-1",
        artifact_id="artifact-1",
        artifact_sha256="a"*64,
        source_revision="sha-1",
        workflow_generation=7,
        validation=validation(),
    )

    verified=verify_validation_attestation(
        attestation,
        trusted_public_keys={"validator-1":public_key},
        workflow_id="wf-1",
        artifact_id="artifact-1",
        artifact_sha256="a"*64,
        source_revision="sha-1",
        workflow_generation=7,
        validation=validation(),
    )

    assert verified["verified"] is True
    assert verified["signature"]["algorithm"]=="ed25519"
    assert verified["signature"]["key_id"].startswith("sha256:")


def test_release_provenance_is_offline_publicly_verifiable():
    validator_private,validator_public=generate_keypair()
    release_private,release_public=generate_keypair()
    attestation=create_validation_attestation(
        validator_id="validator-1",
        private_key_pem=validator_private,
        workflow_id="wf-1",
        artifact_id="artifact-1",
        artifact_sha256="a"*64,
        source_revision="sha-1",
        workflow_generation=1,
        validation=validation(),
    )
    approval_key=release_approval_key(
        workflow_id="wf-1",
        artifact_id="artifact-1",
        artifact_sha256="a"*64,
        source_revision="sha-1",
        workflow_generation=1,
    )
    release={
        "id":"release-1",
        "workflow_id":"wf-1",
        "artifact_id":"artifact-1",
        "repository":"o/a",
        "source_revision":"sha-1",
        "workflow_generation":1,
        "metadata":{
            "artifact_sha256":"a"*64,
            "approval":{
                "approval_key":approval_key,
                "approved_by":"operator-1",
                "role":"operator",
            },
        },
        "created_at":"2026-09-15T05:00:00+00:00",
    }
    provenance=create_release_provenance(
        private_key_pem=release_private,
        release=release,
        attestation=attestation,
    )

    assert verify_release_provenance(
        provenance,
        public_key_pem=release_public,
    ) is True

    provenance["artifact_sha256"]="b"*64
    assert verify_release_provenance(
        provenance,
        public_key_pem=release_public,
    ) is False

    assert validator_public
