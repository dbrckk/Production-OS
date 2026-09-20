import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from production_os.cli import _parse_args, run_asset_forge_batch


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


def test_transparency_checkpoint_parser_accepts_rekor_publication_options():
    args = _parse_args([
        "transparency-checkpoint",
        "--database", "state.sqlite",
        "--private-key", "witness.pem",
        "--rekor-url", "https://rekor.example",
        "--rekor-private-key", "rekor.pem",
        "--rekor-log-public-key", "rekor-log.pem",
        "--receipt-output", "receipt.json",
    ])

    assert args.command == "transparency-checkpoint"
    assert args.rekor_url == "https://rekor.example"
    assert args.rekor_private_key == "rekor.pem"
    assert args.rekor_log_public_key == "rekor-log.pem"
    assert args.receipt_output == "receipt.json"


def test_transparency_checkpoint_verify_parser_accepts_rekor_receipt():
    args = _parse_args([
        "transparency-checkpoint-verify",
        "--checkpoint", "checkpoint.json",
        "--public-key", "witness.pub.pem",
        "--receipt", "receipt.json",
        "--rekor-log-public-key", "rekor-log.pem",
        "--rekor-log-id", "a" * 64,
    ])

    assert args.command == "transparency-checkpoint-verify"
    assert args.receipt == "receipt.json"
    assert args.rekor_log_public_key == "rekor-log.pem"
    assert args.rekor_log_id == "a" * 64


def test_asset_forge_batch_parser_accepts_result_file():
    args = _parse_args([
        "asset-forge-batch",
        "--spec", "batch.json",
        "--target-worktree", "repo",
        "--result-file", "receipt.json",
    ])
    assert args.command == "asset-forge-batch"
    assert args.result_file == "receipt.json"


def test_asset_forge_batch_writes_visual_quality_failure_receipt():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        spec = root / "batch.json"
        receipt = root / "receipt.json"
        spec.write_text(json.dumps({"items": [{"request": {}, "target_path": "a.png"}]}))

        args = _parse_args([
            "asset-forge-batch",
            "--spec", str(spec),
            "--target-worktree", str(root / "repo"),
            "--result-file", str(receipt),
        ])
        with patch(
            "production_os.cli.execute_asset_forge_batch",
            side_effect=RuntimeError("visual consistency score 0.200 is below required 0.550"),
        ):
            rc = run_asset_forge_batch(args)

        assert rc == 1
        payload = json.loads(receipt.read_text())
        assert payload["success"] is False
        assert payload["error_code"] == "visual_quality_failed"
        assert payload["error_type"] == "RuntimeError"


def test_asset_forge_batch_writes_success_receipt():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        spec = root / "batch.json"
        receipt = root / "receipt.json"
        spec.write_text(json.dumps({"items": [{"request": {}, "target_path": "a.png"}]}))

        args = _parse_args([
            "asset-forge-batch",
            "--spec", str(spec),
            "--target-worktree", str(root / "repo"),
            "--result-file", str(receipt),
        ])
        expected = {
            "schema_version": "production-os/asset-forge-batch/v1",
            "success": True,
            "quality_summary": {
                "checked": 1,
                "regenerated": 1,
                "minimum_score": 0.81,
            },
        }
        with patch("production_os.cli.execute_asset_forge_batch", return_value=expected):
            rc = run_asset_forge_batch(args)

        assert rc == 0
        assert json.loads(receipt.read_text()) == expected
