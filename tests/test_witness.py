from production_os.signing import generate_keypair
from production_os.witness import (
    WITNESS_SCHEMA,
    create_checkpoint,
    sign_checkpoint,
    verify_checkpoint,
)


def test_signed_transparency_checkpoint_verifies():
    private_key,public_key=generate_keypair()
    checkpoint=create_checkpoint(
        root_hash="a"*64,
        entries=42,
        created_at="2026-09-15T09:00:00+00:00",
    )
    envelope=sign_checkpoint(
        checkpoint,
        private_key_pem=private_key,
    )
    assert checkpoint["schema_version"]==WITNESS_SCHEMA
    assert verify_checkpoint(
        envelope,
        public_key_pem=public_key,
        expected_root_hash="a"*64,
    ) is True


def test_checkpoint_root_tampering_is_detected():
    private_key,public_key=generate_keypair()
    envelope=sign_checkpoint(
        create_checkpoint(
            root_hash="a"*64,
            entries=1,
        ),
        private_key_pem=private_key,
    )
    envelope["checkpoint"]["root_hash"]="b"*64
    assert verify_checkpoint(
        envelope,
        public_key_pem=public_key,
    ) is False


def test_checkpoint_expected_root_mismatch_fails():
    private_key,public_key=generate_keypair()
    envelope=sign_checkpoint(
        create_checkpoint(
            root_hash="a"*64,
            entries=1,
        ),
        private_key_pem=private_key,
    )
    assert verify_checkpoint(
        envelope,
        public_key_pem=public_key,
        expected_root_hash="b"*64,
    ) is False
