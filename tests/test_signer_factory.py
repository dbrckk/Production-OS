import pytest

from production_os.signer_factory import (
    RemoteHttpSigner,
    SignerConfigurationError,
    create_signer,
)
from production_os.signers import PemSigner
from production_os.signing import generate_keypair


def test_factory_creates_pem_signer():
    private_key,_=generate_keypair()
    signer=create_signer("pem:",pem_value=private_key)
    assert isinstance(signer,PemSigner)


def test_remote_signer_requires_key_id():
    with pytest.raises(SignerConfigurationError,match="key_id"):
        RemoteHttpSigner(
            endpoint="https://signer.example/sign",
            signing_key_id="",
        )


def test_factory_rejects_unknown_scheme():
    with pytest.raises(
        SignerConfigurationError,
        match="unsupported signer URI",
    ):
        create_signer("kms://key-1")


def test_remote_signer_exposes_configured_public_identity():
    signer=create_signer(
        "remote+https://signer.example/sign",
        key_id="sha256:abc",
    )
    assert isinstance(signer,RemoteHttpSigner)
    assert signer.key_id=="sha256:abc"
