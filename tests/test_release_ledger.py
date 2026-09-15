import pytest

from production_os.attestations import create_validation_attestation
from production_os.asymmetric_attestations import (
    create_validation_attestation as create_validation_attestation_v2,
)
from production_os.signing import generate_keypair
from production_os.dual_sign import create_dual_attestation
from production_os.release_ledger import ReleaseLedger
from production_os.sqlite_backend import SQLiteBackend, SQLiteJobQueue
from production_os.workflow_engine import WorkflowEngine, WorkflowTaskSpec


def setup_release(tmp_path):
    backend=SQLiteBackend(tmp_path/"db.sqlite")
    workflows=WorkflowEngine(backend,SQLiteJobQueue(backend))
    releases=ReleaseLedger(
        backend,
        workflows,
        trusted_validation_secrets={"validator-1":"validator-secret"},
        provenance_secret="provenance-secret",
    )

    workflow=workflows.create(
        name="release",
        repository="o/a",
        metadata={
            "github_pr_number":12,
            "github_pr_head_sha":"sha-1",
            "github_pr_generation":1,
        },
        tasks=[WorkflowTaskSpec("build","Build",{})],
    )
    workflows.dispatch_ready(workflow["id"])
    workflows.record_result(
        workflow["id"],
        "build",
        succeeded=True,
        result={"ok":True},
    )
    artifact=workflows.add_artifact(
        workflow["id"],
        name="app.aab",
        uri="artifact://app.aab",
        sha256="aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        metadata={
            "source_revision":"sha-1",
            "workflow_generation":1,
        },
    )
    return backend,workflows,releases,workflow,artifact


def passed_validation():
    return {
        "status":"passed",
        "promotion_allowed":True,
        "blocking_failures":[],
    }


def approval():
    return {
        "approved":True,
        "approved_by":"operator-1",
        "role":"operator",
    }


def signed_attestation(workflow, artifact, validation=None):
    validation=validation or passed_validation()
    return create_validation_attestation(
        validator_id="validator-1",
        secret="validator-secret",
        workflow_id=workflow["id"],
        artifact_id=artifact["id"],
        artifact_sha256=artifact["sha256"],
        source_revision=artifact["metadata"].get("source_revision"),
        workflow_generation=artifact["metadata"].get(
            "workflow_generation"
        ),
        validation=validation,
    )


def test_promote_creates_immutable_release_record(tmp_path):
    _,_,releases,workflow,artifact=setup_release(tmp_path)

    release=releases.promote(
        workflow_id=workflow["id"],
        artifact_id=artifact["id"],
        validation=passed_validation(),
        attestation=signed_attestation(workflow, artifact),
        approval=approval(),
        metadata={"channel":"internal"},
    )

    assert release["status"]=="promoted"
    assert release["artifact_id"]==artifact["id"]
    assert release["source_revision"]=="sha-1"
    assert release["workflow_generation"]==1
    assert release["validation"]["status"]=="passed"
    assert release["metadata"]["artifact_sha256"]=="aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"


def test_promotion_rejects_failed_validation(tmp_path):
    _,_,releases,workflow,artifact=setup_release(tmp_path)

    with pytest.raises(RuntimeError,match="validation must be passed"):
        releases.promote(
            workflow_id=workflow["id"],
            artifact_id=artifact["id"],
            validation={
                "status":"failed",
                "promotion_allowed":False,
                "blocking_failures":["tests"],
            },
            attestation={},
            approval=approval(),
        )


def test_promotion_rejects_duplicate_artifact(tmp_path):
    _,_,releases,workflow,artifact=setup_release(tmp_path)
    releases.promote(
        workflow_id=workflow["id"],
        artifact_id=artifact["id"],
        validation=passed_validation(),
        attestation=signed_attestation(workflow, artifact),
        approval=approval(),
    )

    with pytest.raises(RuntimeError,match="already promoted"):
        releases.promote(
            workflow_id=workflow["id"],
            artifact_id=artifact["id"],
            validation=passed_validation(),
            attestation=signed_attestation(workflow, artifact),
            approval=approval(),
        )


def test_promotion_rejects_superseded_workflow(tmp_path):
    _,workflows,releases,workflow,artifact=setup_release(tmp_path)
    generation,_=workflows.ensure_pr_generation(
        "o/a",
        12,
        "sha-2",
    )
    assert generation is not None

    with pytest.raises(RuntimeError,match="superseded"):
        releases.promote(
            workflow_id=workflow["id"],
            artifact_id=artifact["id"],
            validation=passed_validation(),
            attestation={},
            approval=approval(),
        )


def test_release_rollback_is_append_only(tmp_path):
    _,_,releases,workflow,artifact=setup_release(tmp_path)
    promoted=releases.promote(
        workflow_id=workflow["id"],
        artifact_id=artifact["id"],
        validation=passed_validation(),
        attestation=signed_attestation(workflow,artifact),
        approval=approval(),
    )

    rollback=releases.rollback(
        promoted["id"],
        reason="regression detected",
        metadata={"ticket":"INC-1"},
    )

    assert rollback["status"]=="rollback"
    assert rollback["rollback_of"]==promoted["id"]
    assert rollback["validation"]["reason"]=="regression detected"
    assert releases.get(promoted["id"])["status"]=="promoted"

    with pytest.raises(RuntimeError,match="already rolled back"):
        releases.rollback(
            promoted["id"],
            reason="duplicate",
        )


def test_promotion_requires_artifact_sha256(tmp_path):
    backend=SQLiteBackend(tmp_path/"db.sqlite")
    workflows=WorkflowEngine(backend,SQLiteJobQueue(backend))
    releases=ReleaseLedger(
        backend,
        workflows,
        trusted_validation_secrets={"validator-1":"validator-secret"},
        provenance_secret="provenance-secret",
    )
    workflow=workflows.create(
        name="release",
        repository="o/a",
        tasks=[WorkflowTaskSpec("build","Build",{})],
    )
    workflows.dispatch_ready(workflow["id"])
    workflows.record_result(
        workflow["id"],
        "build",
        succeeded=True,
    )
    artifact=workflows.add_artifact(
        workflow["id"],
        name="unsigned.bin",
        uri="artifact://unsigned.bin",
    )

    with pytest.raises(RuntimeError,match="sha256 is required"):
        releases.promote(
            workflow_id=workflow["id"],
            artifact_id=artifact["id"],
            validation=passed_validation(),
            attestation={},
            approval=approval(),
        )


def test_promotion_rejects_invalid_attestation_signature(tmp_path):
    _,_,releases,workflow,artifact=setup_release(tmp_path)
    attestation=signed_attestation(workflow,artifact)
    attestation["signature"]="0"*64

    with pytest.raises(RuntimeError,match="invalid validation attestation signature"):
        releases.promote(
            workflow_id=workflow["id"],
            artifact_id=artifact["id"],
            validation=passed_validation(),
            attestation=attestation,
            approval=approval(),
        )


def test_promoted_release_contains_signed_provenance(tmp_path):
    _,_,releases,workflow,artifact=setup_release(tmp_path)
    release=releases.promote(
        workflow_id=workflow["id"],
        artifact_id=artifact["id"],
        validation=passed_validation(),
        attestation=signed_attestation(workflow,artifact),
        approval=approval(),
    )

    assert release["metadata"]["validation_attestation"]["verified"] is True
    assert release["metadata"]["provenance"]["validator_id"]=="validator-1"
    assert len(release["metadata"]["provenance"]["signature"])==64


def test_release_verification_checks_full_chain(tmp_path):
    _,_,releases,workflow,artifact=setup_release(tmp_path)
    release=releases.promote(
        workflow_id=workflow["id"],
        artifact_id=artifact["id"],
        validation=passed_validation(),
        attestation=signed_attestation(workflow,artifact),
        approval=approval(),
    )

    verification=releases.verify(release["id"])

    assert verification["valid"] is True
    assert verification["validator_id"]=="validator-1"
    assert verification["artifact_sha256"]==artifact["sha256"]


def test_promotion_requires_operator_approval(tmp_path):
    _,_,releases,workflow,artifact=setup_release(tmp_path)

    with pytest.raises(RuntimeError,match="release approval is required"):
        releases.promote(
            workflow_id=workflow["id"],
            artifact_id=artifact["id"],
            validation=passed_validation(),
            attestation=signed_attestation(workflow,artifact),
            approval={},
        )


def test_release_ledger_promotes_ed25519_attestation(tmp_path):
    backend,workflows,_,workflow,artifact=setup_release(tmp_path)
    validator_private,validator_public=generate_keypair()
    release_private,release_public=generate_keypair()
    releases=ReleaseLedger(
        backend,
        workflows,
        trusted_validation_public_keys={
            "validator-v2":validator_public
        },
        provenance_private_key=release_private,
        provenance_public_key=release_public,
    )
    attestation=create_validation_attestation_v2(
        validator_id="validator-v2",
        private_key_pem=validator_private,
        workflow_id=workflow["id"],
        artifact_id=artifact["id"],
        artifact_sha256=artifact["sha256"],
        source_revision=artifact["metadata"]["source_revision"],
        workflow_generation=artifact["metadata"][
            "workflow_generation"
        ],
        validation=passed_validation(),
    )

    release=releases.promote(
        workflow_id=workflow["id"],
        artifact_id=artifact["id"],
        validation=passed_validation(),
        attestation=attestation,
        approval=approval(),
    )

    assert release["metadata"]["provenance"][
        "schema_version"
    ]=="production-os/release-provenance/v2"
    verification=releases.verify(release["id"])
    assert verification["valid"] is True
    assert verification["signature_scheme"]=="ed25519"
    assert verification["validator_id"]=="validator-v2"
    assert release["metadata"]["slsa_provenance"]["statement"][
        "_type"
    ]=="https://in-toto.io/Statement/v1"
    assert release["metadata"]["slsa_provenance"]["statement"][
        "predicateType"
    ]=="https://slsa.dev/provenance/v1"
    assert len(release["metadata"]["slsa_statement_sha256"])==64


def test_release_is_anchored_in_transparency_chain(tmp_path):
    _,_,releases,workflow,artifact=setup_release(tmp_path)
    release=releases.promote(
        workflow_id=workflow["id"],
        artifact_id=artifact["id"],
        validation=passed_validation(),
        attestation=signed_attestation(workflow,artifact),
        approval=approval(),
    )

    chain=releases.verify_transparency()
    verification=releases.verify(release["id"])

    assert chain["valid"] is True
    assert chain["entries"]==1
    assert verification["valid"] is True
    assert verification["transparency_sequence"]==1
    assert len(verification["transparency_entry_hash"])==64
    assert verification["transparency_root_hash"]==chain["root_hash"]


def test_release_ledger_promotes_strict_dual_sign_bundle(tmp_path):
    backend,workflows,_,workflow,artifact=setup_release(tmp_path)
    validator_private,validator_public=generate_keypair()
    release_private,release_public=generate_keypair()
    releases=ReleaseLedger(
        backend,
        workflows,
        trusted_validation_secrets={
            "validator-1":"validation-secret"
        },
        trusted_validation_public_keys={
            "validator-1":validator_public
        },
        provenance_private_key=release_private,
        provenance_public_key=release_public,
    )
    attestation=create_dual_attestation(
        validator_id="validator-1",
        hmac_secret="validation-secret",
        private_key_pem=validator_private,
        workflow_id=workflow["id"],
        artifact_id=artifact["id"],
        artifact_sha256=artifact["sha256"],
        source_revision=artifact["metadata"]["source_revision"],
        workflow_generation=artifact["metadata"][
            "workflow_generation"
        ],
        validation=passed_validation(),
    )
    release=releases.promote(
        workflow_id=workflow["id"],
        artifact_id=artifact["id"],
        validation=passed_validation(),
        attestation=attestation,
        approval=approval(),
    )
    verification=releases.verify(release["id"])
    assert verification["valid"] is True
    assert verification["signature_scheme"]==(
        "hmac-sha256+ed25519"
    )
    assert release["metadata"]["validation_attestation"][
        "schema_version"
    ]=="production-os/validation-attestation-bundle/v1"


def test_ed25519_only_policy_rejects_legacy_hmac(tmp_path):
    backend,workflows,_,workflow,artifact=setup_release(tmp_path)
    releases=ReleaseLedger(
        backend,
        workflows,
        trusted_validation_secrets={
            "validator-1":"validation-secret"
        },
        provenance_secret="provenance-secret",
        validation_signature_policy="ed25519-only",
    )
    import pytest
    with pytest.raises(
        RuntimeError,
        match="requires Ed25519-only",
    ):
        releases.promote(
            workflow_id=workflow["id"],
            artifact_id=artifact["id"],
            validation=passed_validation(),
            attestation=signed_attestation(workflow,artifact),
            approval=approval(),
        )


def test_dual_required_policy_rejects_pure_ed25519(tmp_path):
    backend,workflows,_,workflow,artifact=setup_release(tmp_path)
    validator_private,validator_public=generate_keypair()
    release_private,release_public=generate_keypair()
    releases=ReleaseLedger(
        backend,
        workflows,
        trusted_validation_public_keys={
            "validator-v2":validator_public
        },
        provenance_private_key=release_private,
        provenance_public_key=release_public,
        validation_signature_policy="dual-required",
    )
    attestation=create_validation_attestation_v2(
        validator_id="validator-v2",
        private_key_pem=validator_private,
        workflow_id=workflow["id"],
        artifact_id=artifact["id"],
        artifact_sha256=artifact["sha256"],
        source_revision=artifact["metadata"]["source_revision"],
        workflow_generation=artifact["metadata"][
            "workflow_generation"
        ],
        validation=passed_validation(),
    )
    import pytest
    with pytest.raises(
        RuntimeError,
        match="requires dual-sign",
    ):
        releases.promote(
            workflow_id=workflow["id"],
            artifact_id=artifact["id"],
            validation=passed_validation(),
            attestation=attestation,
            approval=approval(),
        )


def test_release_verify_enforces_trusted_builder_repository(tmp_path):
    backend,workflows,_,workflow,artifact=setup_release(tmp_path)
    validator_private,validator_public=generate_keypair()
    release_private,release_public=generate_keypair()
    builder_private,builder_public=generate_keypair()
    builder_id="https://builder.example/prod"
    releases=ReleaseLedger(
        backend,
        workflows,
        trusted_validation_public_keys={
            "validator-v2":validator_public
        },
        provenance_private_key=release_private,
        provenance_public_key=release_public,
        builder_id=builder_id,
        builder_private_key=builder_private,
        trusted_builders={
            builder_id:{
                "key_owner":"release-builder",
                "allowed_repositories":[workflow["repository"]],
            }
        },
        trusted_builder_keys={
            "release-builder":{"public_key":builder_public}
        },
        require_trusted_builder=True,
    )
    attestation=create_validation_attestation_v2(
        validator_id="validator-v2",
        private_key_pem=validator_private,
        workflow_id=workflow["id"],
        artifact_id=artifact["id"],
        artifact_sha256=artifact["sha256"],
        source_revision=artifact["metadata"]["source_revision"],
        workflow_generation=artifact["metadata"][
            "workflow_generation"
        ],
        validation=passed_validation(),
    )
    release=releases.promote(
        workflow_id=workflow["id"],
        artifact_id=artifact["id"],
        validation=passed_validation(),
        attestation=attestation,
        approval=approval(),
    )
    verification=releases.verify(release["id"])
    assert verification["valid"] is True


def test_release_verify_rejects_untrusted_builder_repository(tmp_path):
    backend,workflows,_,workflow,artifact=setup_release(tmp_path)
    validator_private,validator_public=generate_keypair()
    release_private,release_public=generate_keypair()
    builder_private,builder_public=generate_keypair()
    builder_id="https://builder.example/prod"
    releases=ReleaseLedger(
        backend,
        workflows,
        trusted_validation_public_keys={
            "validator-v2":validator_public
        },
        provenance_private_key=release_private,
        provenance_public_key=release_public,
        builder_id=builder_id,
        builder_private_key=builder_private,
        trusted_builders={
            builder_id:{
                "key_owner":"release-builder",
                "allowed_repositories":["other/repo"],
            }
        },
        trusted_builder_keys={
            "release-builder":{"public_key":builder_public}
        },
        require_trusted_builder=True,
    )
    attestation=create_validation_attestation_v2(
        validator_id="validator-v2",
        private_key_pem=validator_private,
        workflow_id=workflow["id"],
        artifact_id=artifact["id"],
        artifact_sha256=artifact["sha256"],
        source_revision=artifact["metadata"]["source_revision"],
        workflow_generation=artifact["metadata"][
            "workflow_generation"
        ],
        validation=passed_validation(),
    )
    release=releases.promote(
        workflow_id=workflow["id"],
        artifact_id=artifact["id"],
        validation=passed_validation(),
        attestation=attestation,
        approval=approval(),
    )
    verification=releases.verify(release["id"])
    assert verification["valid"] is False
    assert "untrusted SLSA" in verification["reason"]


def test_trusted_builder_requires_dedicated_signing_key(tmp_path):
    backend,workflows,_,_,_=setup_release(tmp_path)
    provenance_private,provenance_public=generate_keypair()
    _,builder_public=generate_keypair()
    releases=ReleaseLedger(
        backend,
        workflows,
        provenance_private_key=provenance_private,
        provenance_public_key=provenance_public,
        builder_id="https://builder.example/prod",
        trusted_builders={
            "https://builder.example/prod":{
                "key_owner":"builder"
            }
        },
        trusted_builder_keys={
            "builder":{"public_key":builder_public}
        },
        require_trusted_builder=True,
    )
    assert releases.builder_private_key is None

