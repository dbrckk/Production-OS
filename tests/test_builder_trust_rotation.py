from datetime import datetime, timedelta, timezone

from production_os.builder_identity import BuilderTrustPolicy
from production_os.signing import generate_keypair
from production_os.supply_chain import (
    create_slsa_statement,
    sign_slsa_statement,
    verify_trusted_slsa_statement,
)


def release(repository, created_at):
    return {
        "id": "release-1",
        "workflow_id": "workflow-1",
        "artifact_id": "artifact-1",
        "repository": repository,
        "source_revision": "revision-1",
        "workflow_generation": 1,
        "created_at": created_at,
        "metadata": {
            "artifact_sha256": "a" * 64,
            "artifact_name": "release.bin",
        },
    }


def provenance():
    return {
        "schema_version": "production-os/release-provenance/v2",
        "signature": {"key_id": "provenance-key"},
        "approval_key": "approval-1",
        "validator_id": "validator-prod",
    }


def envelope(private_key, repository, signed_at, builder_id):
    item = release(repository, signed_at)
    statement = create_slsa_statement(
        release=item,
        provenance=provenance(),
        builder_id=builder_id,
    )
    return sign_slsa_statement(
        statement=statement,
        private_key_pem=private_key,
    )


def test_builder_key_rotation_accepts_each_key_only_in_its_window():
    old_private, old_public = generate_keypair()
    new_private, new_public = generate_keypair()
    now = datetime.now(timezone.utc)
    rotation = now - timedelta(minutes=20)
    builder_id = "https://builder.example/prod"
    repository = "dbrckk/example"
    policy = BuilderTrustPolicy(
        builders={
            builder_id: {
                "key_owner": "production-builder",
                "allowed_repositories": [repository],
            },
        },
        signing_keys={
            "production-builder": [
                {
                    "public_key": old_public,
                    "not_after": rotation.isoformat(),
                },
                {
                    "public_key": new_public,
                    "not_before": rotation.isoformat(),
                },
            ],
        },
    )

    old = envelope(
        old_private,
        repository,
        (rotation - timedelta(minutes=5)).isoformat(),
        builder_id,
    )
    new = envelope(
        new_private,
        repository,
        (rotation + timedelta(minutes=5)).isoformat(),
        builder_id,
    )
    stale = envelope(
        old_private,
        repository,
        (rotation + timedelta(minutes=5)).isoformat(),
        builder_id,
    )

    assert verify_trusted_slsa_statement(
        old,
        builder_policy=policy,
        expected_repository=repository,
        expected_sha256="a" * 64,
    )
    assert verify_trusted_slsa_statement(
        new,
        builder_policy=policy,
        expected_repository=repository,
        expected_sha256="a" * 64,
    )
    assert not verify_trusted_slsa_statement(
        stale,
        builder_policy=policy,
        expected_repository=repository,
        expected_sha256="a" * 64,
    )


def test_revoked_builder_key_cannot_validate_new_slsa_statement():
    private_key, public_key = generate_keypair()
    now = datetime.now(timezone.utc)
    revoked_at = now - timedelta(minutes=10)
    builder_id = "https://builder.example/prod"
    repository = "dbrckk/example"
    policy = BuilderTrustPolicy(
        builders={
            builder_id: {
                "key_owner": "production-builder",
                "allowed_repositories": [repository],
            },
        },
        signing_keys={
            "production-builder": {
                "public_key": public_key,
                "revoked_at": revoked_at.isoformat(),
            },
        },
    )
    signed = envelope(
        private_key,
        repository,
        (revoked_at + timedelta(minutes=1)).isoformat(),
        builder_id,
    )

    assert not verify_trusted_slsa_statement(
        signed,
        builder_policy=policy,
        expected_repository=repository,
        expected_sha256="a" * 64,
    )


def test_builder_cannot_cross_repository_trust_boundary():
    private_key, public_key = generate_keypair()
    now = datetime.now(timezone.utc).isoformat()
    builder_id = "https://builder.example/prod"
    policy = BuilderTrustPolicy(
        builders={
            builder_id: {
                "key_owner": "production-builder",
                "allowed_repositories": ["dbrckk/allowed"],
            },
        },
        signing_keys={
            "production-builder": {"public_key": public_key},
        },
    )
    signed = envelope(
        private_key,
        "dbrckk/forbidden",
        now,
        builder_id,
    )

    assert not verify_trusted_slsa_statement(
        signed,
        builder_policy=policy,
        expected_repository="dbrckk/forbidden",
        expected_sha256="a" * 64,
    )
