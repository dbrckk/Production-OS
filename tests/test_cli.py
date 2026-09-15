import pytest

from production_os.cli import _parse_args


def test_control_plane_builder_trust_options_are_registered():
    args = _parse_args([
        "control-plane",
        "--database", "state.sqlite",
        "--auth-config", "auth.json",
        "--builder-id", "https://builder.example/prod",
        "--builder-private-key-env", "BUILDER_PRIVATE_KEY",
        "--builder-signer-uri", "https://signer.example/sign",
        "--builder-signer-key-id", "builder-key",
        "--builder-signer-token-env", "BUILDER_TOKEN",
        "--trusted-builders-env", "TRUSTED_BUILDERS",
        "--trusted-builder-keys-env", "TRUSTED_BUILDER_KEYS",
        "--require-trusted-builder",
    ])

    assert args.command == "control-plane"
    assert args.builder_id == "https://builder.example/prod"
    assert args.builder_private_key_env == "BUILDER_PRIVATE_KEY"
    assert args.builder_signer_uri == "https://signer.example/sign"
    assert args.builder_signer_key_id == "builder-key"
    assert args.builder_signer_token_env == "BUILDER_TOKEN"
    assert args.trusted_builders_env == "TRUSTED_BUILDERS"
    assert args.trusted_builder_keys_env == "TRUSTED_BUILDER_KEYS"
    assert args.require_trusted_builder is True


def test_builder_trust_options_are_scoped_to_control_plane():
    with pytest.raises(SystemExit) as exc:
        _parse_args([
            "scan",
            "--owner", "dbrckk",
            "--builder-id", "https://builder.example/prod",
        ])

    assert exc.value.code == 2


def test_trust_status_parser_accepts_incident_filters():
    args = _parse_args([
        "trust-status",
        "--database", "state.sqlite",
        "--validator-id", "validator-prod",
        "--builder-id", "https://builder.example/prod",
        "--key-id", "sha256:abc",
    ])

    assert args.command == "trust-status"
    assert args.database == "state.sqlite"
    assert args.validator_id == "validator-prod"
    assert args.builder_id == "https://builder.example/prod"
    assert args.key_id == "sha256:abc"


def test_trust_status_requires_database():
    with pytest.raises(SystemExit) as exc:
        _parse_args(["trust-status"])

    assert exc.value.code == 2
