import pytest

from production_os.key_registry import (
    KeyRegistryError,
    TrustedKeyRegistry,
)
from production_os.signing import generate_keypair


def entry(public_key, **extra):
    return {"public_key": public_key, **extra}


def test_registry_rejects_inverted_key_validity_window():
    _, public_key = generate_keypair()
    with pytest.raises(
        KeyRegistryError,
        match="not_before must not be after not_after",
    ):
        TrustedKeyRegistry({
            "validator": entry(
                public_key,
                not_before="2026-09-15T12:00:00+00:00",
                not_after="2026-09-15T11:00:00+00:00",
            )
        })


def test_registry_rejects_revocation_before_activation():
    _, public_key = generate_keypair()
    with pytest.raises(
        KeyRegistryError,
        match="revoked_at must not be before not_before",
    ):
        TrustedKeyRegistry({
            "validator": entry(
                public_key,
                not_before="2026-09-15T12:00:00+00:00",
                revoked_at="2026-09-15T11:00:00+00:00",
            )
        })


def test_registry_rejects_duplicate_key_for_same_owner():
    _, public_key = generate_keypair()
    with pytest.raises(
        KeyRegistryError,
        match="duplicate signing key for owner",
    ):
        TrustedKeyRegistry({
            "validator": [
                entry(public_key),
                entry(public_key),
            ]
        })


def test_same_public_key_can_be_explicitly_trusted_by_different_owners():
    _, public_key = generate_keypair()
    registry = TrustedKeyRegistry({
        "validator-a": entry(public_key),
        "validator-b": entry(public_key),
    })

    assert len(registry.by_owner["validator-a"]) == 1
    assert len(registry.by_owner["validator-b"]) == 1
