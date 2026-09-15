from production_os.supply_chain import (
    PREDICATE_TYPE,
    STATEMENT_TYPE,
    create_slsa_statement,
    sign_slsa_statement,
    statement_digest,
    verify_signed_slsa_statement,
)
from production_os.signing import generate_keypair


def release():
    return {
        "id":"release-1",
        "workflow_id":"wf-1",
        "artifact_id":"artifact-1",
        "repository":"owner/repo",
        "source_revision":"abc123",
        "workflow_generation":4,
        "created_at":"2026-09-15T08:00:00+00:00",
        "metadata":{
            "artifact_name":"app.aab",
            "artifact_sha256":"a"*64,
        },
    }


def provenance():
    return {
        "schema_version":"production-os/release-provenance/v2",
        "approval_key":"approval-1",
        "validator_id":"validator-1",
        "signature":{
            "algorithm":"ed25519",
            "key_id":"sha256:key",
            "signature":"signature",
        },
    }


def test_slsa_statement_contains_subject_and_material():
    statement=create_slsa_statement(
        release=release(),
        provenance=provenance(),
    )
    assert statement["_type"]==STATEMENT_TYPE
    assert statement["predicateType"]==PREDICATE_TYPE
    assert statement["subject"][0]["name"]=="app.aab"
    assert statement["subject"][0]["digest"]["sha256"]=="a"*64
    dependency=statement["predicate"]["buildDefinition"][
        "resolvedDependencies"
    ][0]
    assert dependency["digest"]["gitCommit"]=="abc123"


def test_signed_slsa_statement_is_offline_verifiable():
    private_key,public_key=generate_keypair()
    statement=create_slsa_statement(
        release=release(),
        provenance=provenance(),
    )
    envelope=sign_slsa_statement(
        statement=statement,
        private_key_pem=private_key,
    )
    assert verify_signed_slsa_statement(
        envelope,
        public_key_pem=public_key,
        expected_sha256="a"*64,
    ) is True
    assert len(statement_digest(statement))==64


def test_slsa_tampering_is_detected():
    private_key,public_key=generate_keypair()
    statement=create_slsa_statement(
        release=release(),
        provenance=provenance(),
    )
    envelope=sign_slsa_statement(
        statement=statement,
        private_key_pem=private_key,
    )
    envelope["statement"]["subject"][0]["digest"]["sha256"]="b"*64
    assert verify_signed_slsa_statement(
        envelope,
        public_key_pem=public_key,
        expected_sha256="b"*64,
    ) is False
