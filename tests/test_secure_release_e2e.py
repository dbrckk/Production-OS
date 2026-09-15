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


def test_secure_release_rejects_attestation_replay_across_workflows(tmp_path):
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

    first = workflows.create(
        name="first",
        repository="dbrckk/example",
        tasks=[WorkflowTaskSpec("build", "Build", {})],
    )
    workflows.dispatch_ready(first["id"])
    workflows.record_result(first["id"], "build", succeeded=True)
    first_artifact = workflows.add_artifact(
        first["id"], name="release.bin", uri="artifact://first", sha256="f" * 64
    )
    validation = {
        "status": "passed",
        "promotion_allowed": True,
        "blocking_failures": [],
    }
    replayed = create_validation_attestation(
        validator_id="validator-prod",
        private_key_pem=validator_private,
        workflow_id=first["id"],
        artifact_id=first_artifact["id"],
        artifact_sha256=first_artifact["sha256"],
        source_revision=None,
        workflow_generation=None,
        validation=validation,
    )

    second = workflows.create(
        name="second",
        repository="dbrckk/example",
        tasks=[WorkflowTaskSpec("build", "Build", {})],
    )
    workflows.dispatch_ready(second["id"])
    workflows.record_result(second["id"], "build", succeeded=True)
    second_artifact = workflows.add_artifact(
        second["id"], name="release.bin", uri="artifact://second", sha256="f" * 64
    )

    import pytest
    with pytest.raises(RuntimeError, match="binding mismatch"):
        releases.promote(
            workflow_id=second["id"],
            artifact_id=second_artifact["id"],
            validation=validation,
            attestation=replayed,
            approval={
                "approved": True,
                "approved_by": "release-operator",
                "role": "operator",
            },
        )


def test_secure_release_verification_detects_provenance_tampering(tmp_path):
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
        name="provenance-tamper",
        repository="dbrckk/example",
        tasks=[WorkflowTaskSpec("build", "Build", {})],
    )
    workflows.dispatch_ready(workflow["id"])
    workflows.record_result(workflow["id"], "build", succeeded=True)
    artifact = workflows.add_artifact(
        workflow["id"], name="release.bin", uri="artifact://release", sha256="1" * 64
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
        source_revision=None,
        workflow_generation=None,
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

    with backend.transaction() as db:
        row = db.execute(
            "SELECT metadata_json FROM releases WHERE id=?",
            (release["id"],),
        ).fetchone()
        import json
        metadata = json.loads(row["metadata_json"])
        metadata["provenance"]["repository"] = "attacker/repository"
        db.execute(
            "UPDATE releases SET metadata_json=? WHERE id=?",
            (json.dumps(metadata), release["id"]),
        )

    verification = releases.verify(release["id"])
    assert verification["valid"] is False
    assert "provenance" in verification["reason"].lower()


def test_release_becomes_untrusted_after_validator_key_compromise(tmp_path):
    backend = SQLiteBackend(tmp_path / "production-os.sqlite")
    workflows = WorkflowEngine(backend, SQLiteJobQueue(backend))
    validator_private, validator_public = generate_keypair()
    provenance_private, provenance_public = generate_keypair()
    workflow = workflows.create(
        name="validator-compromise",
        repository="dbrckk/example",
        tasks=[WorkflowTaskSpec("build", "Build", {})],
    )
    workflows.dispatch_ready(workflow["id"])
    workflows.record_result(workflow["id"], "build", succeeded=True)
    artifact = workflows.add_artifact(
        workflow["id"], name="release.bin", uri="artifact://release", sha256="2" * 64
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
        source_revision=None,
        workflow_generation=None,
        validation=validation,
    )
    initial = ReleaseLedger(
        backend,
        workflows,
        trusted_validation_public_keys={"validator-prod": validator_public},
        provenance_private_key=provenance_private,
        provenance_public_key=provenance_public,
        validation_signature_policy="ed25519-only",
    )
    release = initial.promote(
        workflow_id=workflow["id"],
        artifact_id=artifact["id"],
        validation=validation,
        attestation=attestation,
        approval={"approved": True, "approved_by": "operator", "role": "operator"},
    )
    assert initial.verify(release["id"])["valid"] is True

    compromised = ReleaseLedger(
        backend,
        workflows,
        trusted_validation_public_keys={
            "validator-prod": {
                "public_key": validator_public,
                "compromised": True,
            }
        },
        provenance_private_key=provenance_private,
        provenance_public_key=provenance_public,
        validation_signature_policy="ed25519-only",
    )
    verification = compromised.verify(release["id"])
    assert verification["valid"] is False
    assert "compromised" in verification["reason"].lower()


def test_release_becomes_untrusted_after_builder_key_compromise(tmp_path):
    backend = SQLiteBackend(tmp_path / "production-os.sqlite")
    workflows = WorkflowEngine(backend, SQLiteJobQueue(backend))
    validator_private, validator_public = generate_keypair()
    provenance_private, provenance_public = generate_keypair()
    builder_private, builder_public = generate_keypair()
    builder_id = "https://builder.example/prod"
    repository = "dbrckk/example"
    workflow = workflows.create(
        name="builder-compromise",
        repository=repository,
        tasks=[WorkflowTaskSpec("build", "Build", {})],
    )
    workflows.dispatch_ready(workflow["id"])
    workflows.record_result(workflow["id"], "build", succeeded=True)
    artifact = workflows.add_artifact(
        workflow["id"], name="release.bin", uri="artifact://release", sha256="3" * 64
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
        source_revision=None,
        workflow_generation=None,
        validation=validation,
    )
    builders = {
        builder_id: {
            "key_owner": "production-builder",
            "allowed_repositories": [repository],
        }
    }
    initial = ReleaseLedger(
        backend,
        workflows,
        trusted_validation_public_keys={"validator-prod": validator_public},
        provenance_private_key=provenance_private,
        provenance_public_key=provenance_public,
        builder_id=builder_id,
        builder_private_key=builder_private,
        trusted_builders=builders,
        trusted_builder_keys={"production-builder": {"public_key": builder_public}},
        require_trusted_builder=True,
        validation_signature_policy="ed25519-only",
    )
    release = initial.promote(
        workflow_id=workflow["id"],
        artifact_id=artifact["id"],
        validation=validation,
        attestation=attestation,
        approval={"approved": True, "approved_by": "operator", "role": "operator"},
    )
    assert initial.verify(release["id"])["valid"] is True

    compromised = ReleaseLedger(
        backend,
        workflows,
        trusted_validation_public_keys={"validator-prod": validator_public},
        provenance_private_key=provenance_private,
        provenance_public_key=provenance_public,
        builder_id=builder_id,
        trusted_builders=builders,
        trusted_builder_keys={
            "production-builder": {
                "public_key": builder_public,
                "compromised": True,
            }
        },
        require_trusted_builder=True,
        validation_signature_policy="ed25519-only",
    )
    verification = compromised.verify(release["id"])
    assert verification["valid"] is False
    assert "slsa" in verification["reason"].lower()
