import pytest

from production_os.vault_auth import VaultAuthError
from production_os.signer_factory import (
    SignerConfigurationError,
    create_signer,
)


def test_vault_approle_requires_credentials(monkeypatch):
    with pytest.raises(VaultAuthError,match="required"):
        create_signer(
            "vault+https://vault.example/keys/builder",
            key_id="sha256:abc",
            vault_auth_method="approle",
        )


def test_vault_kubernetes_requires_role_and_jwt():
    with pytest.raises(VaultAuthError,match="required"):
        create_signer(
            "vault+https://vault.example/keys/builder",
            key_id="sha256:abc",
            vault_auth_method="kubernetes",
        )


def test_vault_rejects_unknown_auth_method():
    with pytest.raises(
        SignerConfigurationError,
        match="unsupported Vault auth method",
    ):
        create_signer(
            "vault+https://vault.example/keys/builder",
            key_id="sha256:abc",
            vault_auth_method="password",
        )
