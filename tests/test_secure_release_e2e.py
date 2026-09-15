from production_os.asymmetric_attestations import (
    create_validation_attestation,
)
from production_os.release_ledger import ReleaseLedger
from production_os.signing import generate_keypair
from production_os.sqlite_backend import SQLiteBackend, SQLiteJobQueue
from production_os.workflow_engine import WorkflowEngine, WorkflowTaskSpec


def test_secure_release_pipeline_end_to_end(tmp_path):
    backend = SQLiteBackend(tmp_path / "production-os.sqlite")
    queue = SQLiteJobQueue(backend)
    workflows = WorkflowEngine(backend, queue)

    validator_private, validator_public = generate_keypair()
    provenance_private, provenance_public = generate_keypair()
    builder_private, builder_public = generate_keypair()

    builder_id = "https://builder.example/production"
    repository = "dbrckk/example"

    releases = ReleaseLedger(
        backend,
        workflows,
        trusted_validation_public_keys={
            "validator-prod": validator_public,
        },
        provenance_private_key=provenance_private,
        provenance_public_key=provenance_public,
        builder_id=builder_id,
        builder_private_key=builder_private,
        trusted_builders={
            builder_id: {
                "key_owner": "production-builder",
                "allowed_repositories": [repository],
            },
        },
        trusted_builder_keys={
            "production-builder": {
                "public_key": builder_public,
            },
        },
        require_trusted_builder=True,
        validation_signature_policy="ed25519-only",
    )

    workflow = workflows.create(
        name="secure-release",
        repository=repository,
        metadata={
            "github_pr_number": 42,
            "github_pr_head_sha": "revision-42",
            "github_pr_generation": 1,
        },
        tasks=[
            WorkflowTaskSpec(
                "build",
                "Build release artifact",
                {"required_capabilities": ["python"]},
            ),
        ],
    )
    workflows.dispatch_ready(workflow["id"])
    workflows.record_result(
        workflow["id"],
        "build",
        succeeded=True,
        result={"tests": "passed"},
    )

    artifact = workflows.add_artifact(
        workflow["id"],
        name="release.bin",
        uri="artifact://release.bin",
        sha256="b" * 64,
        metadata={
            "source_revision": "revision-42",
            "workflow_generation": 1,
        },
    )

    validation = {
        "status": "passed",
        "promotion_allowed": True,
        "blocking_failures": [],
    }
    attestation = create_validation_attestation(
        validator_id="validator-prod",
        private_key_pem=validator_private,
        workflow_id=workflow["id"],
        artifact_id=artifact["id"],
        artifact_sha256=artifact["sha256"],
        source_revision="revision-42",
        workflow_generation=1,
        validation=validation,
    )

    release = releases.promote(
        workflow_id=workflow["id"],
        artifact_id=artifact["id"],
        validation=validation,
        attestation=attestation,
        approval={
            "approved": True,
            "approved_by": "release-operator",
            "role": "operator",
        },
    )

    verification = releases.verify(release["id"])
    transparency = releases.verify_transparency()

    assert release["status"] == "promoted"
    assert verification["valid"] is True
    assert verification["signature_scheme"] == "ed25519"
    assert verification["validator_id"] == "validator-prod"
    assert verification["artifact_sha256"] == artifact["sha256"]
    assert transparency["valid"] is True
    assert transparency["entries"] == 1

    metadata = release["metadata"]
    assert metadata["validation_attestation"]["verified"] is True
    assert metadata["provenance"]["schema_version"] == (
        "production-os/release-provenance/v2"
    )
    assert metadata["slsa_provenance"]["statement"]["predicateType"] == (
        "https://slsa.dev/provenance/v1"
    )
    assert len(metadata["slsa_statement_sha256"]) == 64


def test_secure_release_rejects_attestation_bound_to_other_artifact(tmp_path):
    backend = SQLiteBackend(tmp_path / "production-os.sqlite")
    workflows = WorkflowEngine(backend, SQLiteJobQueue(backend))
    validator_private, validator_public = generate_keypair()
    provenance_private, provenance_public = generate_keypair()

    releases = ReleaseLedger(
        backend,
        workflows,
        trusted_validation_public_keys={"validator-prod": validator_public},
        provenance_private_key=provenance_private,
        provenance_public_key=provenance_public,
        validation_signature_policy="ed25519-only",
    )
    workflow = workflows.create(
        name="tamper-test",
        repository="dbrckk/example",
        tasks=[WorkflowTaskSpec("build", "Build", {})],
    )
    workflows.dispatch_ready(workflow["id"])
    workflows.record_result(workflow["id"], "build", succeeded=True)
    artifact = workflows.add_artifact(
        workflow["id"],
        name="release.bin",
        uri="artifact://release.bin",
        sha256="c" * 64,
    )
    validation = {
        "status": "passed",
        "promotion_allowed": True,
        "blocking_failures": [],
    }
    attestation = create_validation_attestation(
        validator_id="validator-prod",
        private_key_pem=validator_private,
        workflow_id=workflow["id"],
        artifact_id="attacker-substituted-artifact",
        artifact_sha256=artifact["sha256"],
        source_revision=None,
        workflow_generation=None,
        validation=validation,
    )

    import pytest
    with pytest.raises(RuntimeError, match="binding mismatch: artifact_id"):
        releases.promote(
            workflow_id=workflow["id"],
            artifact_id=artifact["id"],
            validation=validation,
            attestation=attestation,
            approval={
                "approved": True,
                "approved_by": "release-operator",
                "role": "operator",
            },
        )


def test_secure_release_rejects_tampered_artifact_digest(tmp_path):
    backend = SQLiteBackend(tmp_path / "production-os.sqlite")
    workflows = WorkflowEngine(backend, SQLiteJobQueue(backend))
    validator_private, validator_public = generate_keypair()
    provenance_private, provenance_public = generate_keypair()

    releases = ReleaseLedger(
        backend,
        workflows,
        trusted_validation_public_keys={"validator-prod": validator_public},
        provenance_private_key=provenance_private,
        provenance_public_key=provenance_public,
        validation_signature_policy="ed25519-only",
    )
    workflow = workflows.create(
        name="digest-test",
        repository="dbrckk/example",
        tasks=[WorkflowTaskSpec("build", "Build", {})],
    )
    workflows.dispatch_ready(workflow["id"])
    workflows.record_result(workflow["id"], "build", succeeded=True)
    artifact = workflows.add_artifact(
        workflow["id"],
        name="release.bin",
        uri="artifact://release.bin",
        sha256="d" * 64,
    )
    validation = {
        "status": "passed",
        "promotion_allowed": True,
        "blocking_failures": [],
    }
    attestation = create_validation_attestation(
        validator_id="validator-prod",
        private_key_pem=validator_private,
        workflow_id=workflow["id"],
        artifact_id=artifact["id"],
        artifact_sha256="e" * 64,
        source_revision=None,
        workflow_generation=None,
        validation=validation,
    )

    import pytest
    with pytest.raises(RuntimeError, match="binding mismatch: artifact_sha256"):
        releases.promote(
            workflow_id=workflow["id"],
            artifact_id=artifact["id"],
            validation=validation,
            attestation=attestation,
            approval={
                "approved": True,
                "approved_by": "release-operator",
                "role": "operator",
            },
        )
