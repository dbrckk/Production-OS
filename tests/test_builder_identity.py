from production_os.builder_identity import BuilderTrustPolicy
from production_os.signing import generate_keypair, key_id, load_public_key
from production_os.supply_chain import (
    create_slsa_statement,
    sign_slsa_statement,
    verify_trusted_slsa_statement,
)


def release(repository="owner/repo"):
    return {
        "id":"release-1",
        "workflow_id":"wf-1",
        "artifact_id":"artifact-1",
        "repository":repository,
        "source_revision":"abc123",
        "workflow_generation":1,
        "created_at":"2026-09-15T10:00:00+00:00",
        "metadata":{
            "artifact_sha256":"a"*64,
        },
    }


def provenance():
    return {
        "schema_version":"production-os/release-provenance/v2",
        "approval_key":"approval-1",
        "validator_id":"validator-1",
        "signature":{"key_id":"sha256:x"},
    }


def policy(public_key):
    return BuilderTrustPolicy(
        builders={
            "https://builder.example/prod":{
                "key_owner":"prod-builder",
                "allowed_repositories":["owner/repo"],
            }
        },
        signing_keys={
            "prod-builder":{"public_key":public_key}
        },
    )


def test_trusted_builder_can_sign_authorized_repository():
    private_key,public_key=generate_keypair()
    statement=create_slsa_statement(
        release=release(),
        provenance=provenance(),
        builder_id="https://builder.example/prod",
    )
    envelope=sign_slsa_statement(
        statement=statement,
        private_key_pem=private_key,
    )
    assert verify_trusted_slsa_statement(
        envelope,
        builder_policy=policy(public_key),
        expected_repository="owner/repo",
        expected_sha256="a"*64,
    ) is True


def test_builder_is_rejected_for_other_repository():
    private_key,public_key=generate_keypair()
    statement=create_slsa_statement(
        release=release("other/repo"),
        provenance=provenance(),
        builder_id="https://builder.example/prod",
    )
    envelope=sign_slsa_statement(
        statement=statement,
        private_key_pem=private_key,
    )
    assert verify_trusted_slsa_statement(
        envelope,
        builder_policy=policy(public_key),
        expected_repository="other/repo",
        expected_sha256="a"*64,
    ) is False
