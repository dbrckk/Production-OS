import pytest

from production_os.key_domains import KeyDomainError
from production_os.signing import generate_keypair
from production_os.trust_policy import TrustPolicy


def test_strict_policy_accepts_four_distinct_domains():
    validator_private,validator_public=generate_keypair()
    builder_private,builder_public=generate_keypair()
    provenance_private,_=generate_keypair()
    witness_private,_=generate_keypair()
    policy=TrustPolicy.create(
        validator_keys={
            "validator":{"public_key":validator_public}
        },
        builder_keys={
            "builder":{"public_key":builder_public}
        },
        builder_private_key=builder_private,
        provenance_private_key=provenance_private,
        witness_private_key=witness_private,
        strict_key_domains=True,
    )
    mapping=policy.validate()
    assert set(mapping.values())=={
        "validator","builder","provenance","witness"
    }
    assert validator_private


def test_witness_cannot_reuse_provenance_key():
    private_key,_=generate_keypair()
    with pytest.raises(KeyDomainError,match="reused across"):
        TrustPolicy.create(
            provenance_private_key=private_key,
            witness_private_key=private_key,
            strict_key_domains=True,
        )


def test_witness_cannot_reuse_builder_key():
    private_key,public_key=generate_keypair()
    with pytest.raises(KeyDomainError,match="reused across"):
        TrustPolicy.create(
            builder_keys={
                "builder":{"public_key":public_key}
            },
            witness_private_key=private_key,
            strict_key_domains=True,
        )
