import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from production_os.cli import _parse_args, run_asset_forge_batch, run_restore_activate
from production_os.dashboard_backups import create_verified_sqlite_backup, stage_verified_sqlite_restore
from production_os.database_maintenance_lock import SQLiteDatabaseProcessLock
from production_os.sqlite_backend import SQLiteBackend


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


def test_restore_activate_parser_requires_explicit_activation_fields():
    args = _parse_args([
        "restore-activate",
        "--database", "state.sqlite",
        "--candidate-id", "20260925T120000Z-abcdef123456",
        "--confirm", "ACTIVATE_STAGED_RESTORE",
    ])
    assert args.command == "restore-activate"
    assert args.database == "state.sqlite"
    assert args.candidate_id == "20260925T120000Z-abcdef123456"
    assert args.confirm == "ACTIVATE_STAGED_RESTORE"


def test_restore_activate_cli_refuses_live_database_lock(
    tmp_path,
    monkeypatch,
    capsys,
):
    backup_dir = tmp_path / "backups"
    monkeypatch.setenv("PRODUCTION_OS_BACKUP_DIR", str(backup_dir))
    database = tmp_path / "production.sqlite"
    backend = SQLiteBackend(database)
    backup = create_verified_sqlite_backup(backend)
    staged = stage_verified_sqlite_restore(backend, backup["backup_id"])
    args = _parse_args([
        "restore-activate",
        "--database", str(database),
        "--candidate-id", staged["candidate_id"],
        "--confirm", "ACTIVATE_STAGED_RESTORE",
    ])

    lock = SQLiteDatabaseProcessLock(str(database))
    lock.acquire()
    try:
        rc = run_restore_activate(args)
    finally:
        lock.release()

    assert rc == 9
    payload = json.loads(capsys.readouterr().err)
    assert payload["activated"] is False
    assert "already locked" in payload["error"]

def test_remote_worker_run_requires_token_from_environment(monkeypatch, capsys):
    from production_os.cli import main

    monkeypatch.delenv("PRODUCTION_OS_WORKER_TOKEN", raising=False)
    try:
        main([
            "remote-worker-run",
            "--url", "http://127.0.0.1:8787",
            "--worker-id", "runner-1",
            "--executor-command", "python executor.py",
            "--cycles", "1",
        ])
    except ValueError as exc:
        assert str(exc) == "PRODUCTION_OS_WORKER_TOKEN is required"
    else:
        raise AssertionError("runner must not accept a missing worker token")

def test_auth_config_init_hashes_environment_tokens(tmp_path, monkeypatch):
    import json
    import stat
    from production_os.api_auth import token_digest
    from production_os.cli import main

    output = tmp_path / "auth.json"
    monkeypatch.setenv("PRODUCTION_OS_OPERATOR_TOKEN", "operator-secret")
    monkeypatch.setenv("PRODUCTION_OS_WORKER_TOKEN", "worker-secret")

    assert main([
        "auth-config-init",
        "--output", str(output),
        "--worker-id", "worker-one",
    ]) == 0

    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload == {
        "tokens":[
            {
                "name":"operator",
                "role":"operator",
                "sha256":token_digest("operator-secret"),
            },
            {
                "name":"worker-one",
                "role":"worker",
                "sha256":token_digest("worker-secret"),
            },
        ]
    }
    raw = output.read_text(encoding="utf-8")
    assert "operator-secret" not in raw
    assert "worker-secret" not in raw
    assert stat.S_IMODE(output.stat().st_mode) == 0o600


def test_auth_config_init_refuses_implicit_overwrite(tmp_path, monkeypatch):
    from production_os.cli import main

    output = tmp_path / "auth.json"
    output.write_text('{"sentinel":true}\n', encoding="utf-8")
    monkeypatch.setenv("PRODUCTION_OS_OPERATOR_TOKEN", "operator-secret")
    monkeypatch.setenv("PRODUCTION_OS_WORKER_TOKEN", "worker-secret")

    try:
        main([
            "auth-config-init",
            "--output", str(output),
            "--worker-id", "worker-one",
        ])
    except FileExistsError as exc:
        assert "auth config already exists" in str(exc)
    else:
        raise AssertionError("auth bootstrap must not overwrite implicitly")

    assert output.read_text(encoding="utf-8") == '{"sentinel":true}\n'

