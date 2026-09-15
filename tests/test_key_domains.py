import pytest

from production_os.key_domains import (
    KeyDomainError,
    assert_separate_key_domains,
)
from production_os.signing import generate_keypair


def test_distinct_key_domains_are_accepted():
    validator_private,validator_public=generate_keypair()
    builder_private,builder_public=generate_keypair()
    provenance_private,_=generate_keypair()
    result=assert_separate_key_domains(
        validator_keys={
            "validator":{"public_key":validator_public}
        },
        builder_keys={
            "builder":{"public_key":builder_public}
        },
        builder_private_key=builder_private,
        provenance_private_key=provenance_private,
    )
    assert set(result.values())=={
        "validator","builder","provenance"
    }
    assert validator_private


def test_validator_builder_key_reuse_is_rejected():
    _,public_key=generate_keypair()
    with pytest.raises(KeyDomainError,match="reused across"):
        assert_separate_key_domains(
            validator_keys={
                "validator":{"public_key":public_key}
            },
            builder_keys={
                "builder":{"public_key":public_key}
            },
        )


def test_builder_provenance_private_key_reuse_is_rejected():
    private_key,public_key=generate_keypair()
    with pytest.raises(KeyDomainError,match="reused across"):
        assert_separate_key_domains(
            builder_keys={
                "builder":{"public_key":public_key}
            },
            builder_private_key=private_key,
            provenance_private_key=private_key,
        )
