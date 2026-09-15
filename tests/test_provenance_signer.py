from production_os.asymmetric_attestations import (
    create_release_provenance_with_signer,
    verify_release_provenance,
)
from production_os.attestations import release_approval_key
from production_os.signers import PemSigner
from production_os.signing import generate_keypair


def test_release_provenance_can_be_signed_via_signer():
    private_key,public_key=generate_keypair()
    signer=PemSigner(private_key)
    approval_key=release_approval_key(
        workflow_id="wf-1",
        artifact_id="artifact-1",
        artifact_sha256="a"*64,
        source_revision="abc",
        workflow_generation=2,
    )
    release={
        "id":"release-1",
        "workflow_id":"wf-1",
        "artifact_id":"artifact-1",
        "repository":"owner/repo",
        "source_revision":"abc",
        "workflow_generation":2,
        "created_at":"2026-09-15T11:00:00+00:00",
        "metadata":{
            "artifact_sha256":"a"*64,
            "approval":{
                "approval_key":approval_key,
                "approved_by":"operator",
                "role":"release-manager",
            },
        },
    }
    attestation={
        "validator_id":"validator-1",
        "signature":{
            "key_id":"sha256:validator",
            "signature":"signed-validation",
        },
    }
    provenance=create_release_provenance_with_signer(
        signer=signer,
        release=release,
        attestation=attestation,
    )
    assert provenance["signature"]["key_id"]==signer.key_id
    assert verify_release_provenance(
        provenance,
        public_key_pem=public_key,
    ) is True
