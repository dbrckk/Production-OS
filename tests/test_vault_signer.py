import pytest

from production_os.signer_factory import create_signer
from production_os.vault_signer import (
    VaultSignerError,
    VaultTransitSigner,
)


def test_vault_requires_https():
    with pytest.raises(VaultSignerError,match="HTTPS"):
        VaultTransitSigner(
            address="http://vault.example",
            transit_key="builder",
            signing_key_id="sha256:abc",
            token="token",
        )


def test_vault_requires_credentials():
    with pytest.raises(VaultSignerError,match="required"):
        VaultTransitSigner(
            address="https://vault.example",
            transit_key="builder",
            signing_key_id="sha256:abc",
            token="",
        )


def test_factory_creates_vault_transit_signer():
    signer=create_signer(
        "vault+https://vault.example/keys/builder",
        key_id="sha256:abc",
        vault_token="token",
    )
    assert isinstance(signer,VaultTransitSigner)
    assert signer.key_id=="sha256:abc"
    assert signer.transit_key=="builder"


def test_factory_rejects_vault_uri_without_key():
    with pytest.raises(Exception):
        create_signer(
            "vault+https://vault.example/transit",
            key_id="sha256:abc",
            vault_token="token",
        )
