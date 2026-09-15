from datetime import datetime, timedelta, timezone

import pytest

from production_os.key_registry import KeyRegistryError, TrustedKeyRegistry
from production_os.signing import generate_keypair, key_id, load_public_key


def test_compromised_key_is_rejected_even_for_precompromise_signature():
    _, public_key = generate_keypair()
    registry = TrustedKeyRegistry({
        "validator": {
            "public_key": public_key,
            "compromised": True,
        }
    })
    kid = key_id(load_public_key(public_key))
    historical = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()

    with pytest.raises(KeyRegistryError, match="compromised"):
        registry.resolve(
            "validator",
            kid,
            signed_at=historical,
        )


def test_normal_revocation_preserves_pre_revocation_history():
    _, public_key = generate_keypair()
    now = datetime.now(timezone.utc)
    revoked_at = now - timedelta(days=1)
    registry = TrustedKeyRegistry({
        "validator": {
            "public_key": public_key,
            "revoked_at": revoked_at.isoformat(),
        }
    })
    kid = key_id(load_public_key(public_key))

    resolved = registry.resolve(
        "validator",
        kid,
        signed_at=(revoked_at - timedelta(days=1)).isoformat(),
    )
    assert resolved == public_key

    with pytest.raises(KeyRegistryError, match="revoked"):
        registry.resolve(
            "validator",
            kid,
            signed_at=(revoked_at + timedelta(seconds=1)).isoformat(),
        )


def test_compromise_semantics_apply_to_builder_key_registry():
    _, public_key = generate_keypair()
    registry = TrustedKeyRegistry({
        "production-builder": {
            "public_key": public_key,
            "compromised": True,
        }
    })
    kid = key_id(load_public_key(public_key))

    with pytest.raises(KeyRegistryError, match="compromised"):
        registry.resolve(
            "production-builder",
            kid,
            signed_at=datetime.now(timezone.utc).isoformat(),
        )
