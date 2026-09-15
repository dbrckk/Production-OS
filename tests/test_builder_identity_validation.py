import pytest

from production_os.builder_identity import (
    BuilderIdentityError,
    BuilderTrustPolicy,
)
from production_os.signing import generate_keypair


def policy(builder):
    _, public_key = generate_keypair()
    return BuilderTrustPolicy(
        builders={"builder-1": builder},
        signing_keys={
            "builder-1": {"public_key": public_key},
        },
    )


def test_builder_identity_rejects_naive_not_before():
    with pytest.raises(BuilderIdentityError, match="timezone-aware"):
        policy({"not_before": "2026-09-15T10:00:00"})


def test_builder_identity_rejects_naive_not_after():
    with pytest.raises(BuilderIdentityError, match="timezone-aware"):
        policy({"not_after": "2026-09-15T11:00:00"})


def test_builder_identity_rejects_invalid_timestamp():
    with pytest.raises(BuilderIdentityError, match="invalid"):
        policy({"not_before": "not-a-timestamp"})


def test_builder_identity_rejects_inverted_validity_window():
    with pytest.raises(
        BuilderIdentityError,
        match="not_before must not be after not_after",
    ):
        policy({
            "not_before": "2026-09-15T12:00:00+00:00",
            "not_after": "2026-09-15T11:00:00+00:00",
        })
