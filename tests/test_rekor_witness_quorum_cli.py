import argparse
import base64
import hashlib

import pytest

from production_os import cli
from production_os.signing import generate_keypair
from production_os.sqlite_backend import SQLiteBackend


def _receipt() -> dict:
    root_hash = hashlib.sha256(b"rekor-root").hexdigest()
    root_b64 = base64.b64encode(bytes.fromhex(root_hash)).decode("ascii")
    checkpoint = (
        "rekor.example - 42\n"
        "1\n"
        f"{root_b64}\n"
        "\n"
        "— rekor.example already-verified\n"
    )
    return {
        "provider": "rekor-v1",
        "log_id": "a" * 64,
        "inclusion_proof": {
            "treeSize": 1,
            "rootHash": root_hash,
            "checkpoint": checkpoint,
        },
    }


def test_checkpoint_parser_accepts_rekor_witness_config():
    args = cli._parse_args(
        [
            "transparency-checkpoint",
            "--database",
            "state.sqlite",
            "--private-key",
            "witness.pem",
            "--rekor-url",
            "https://rekor.example",
            "--rekor-private-key",
            "rekor.pem",
            "--rekor-log-public-key",
            "rekor-log.pem",
            "--rekor-witness-config",
            "witnesses.json",
        ]
    )

    assert args.rekor_witness_config == "witnesses.json"


def test_checkpoint_publication_fails_closed_before_receipt_output_on_bad_quorum(
    tmp_path, monkeypatch
):
    database = tmp_path / "state.db"
    backend = SQLiteBackend(database)

    class Ledger:
        def __init__(self):
            self.backend = backend

        def verify_transparency(self):
            return {
                "valid": True,
                "root_hash": "b" * 64,
                "entries": 1,
            }

    monkeypatch.setattr(cli, "_release_ledger", lambda _: Ledger())

    class FakePublisher:
        @classmethod
        def from_private_key(cls, *args, **kwargs):
            return cls()

        def publish(self, envelope):
            return _receipt()

    monkeypatch.setattr(cli, "RekorV1Publisher", FakePublisher)
    monkeypatch.setattr(
        cli,
        "load_rekor_witness_config",
        lambda path: {
            "threshold": 2,
            "witnesses": [
                {"id": "w1", "url": "https://w1", "public_key": "key1"},
                {"id": "w2", "url": "https://w2", "public_key": "key2"},
            ],
        },
    )
    observed = {}

    def fake_collect(config, **kwargs):
        observed.update(kwargs)
        return {
            "valid": False,
            "required": 2,
            "valid_witnesses": ["w1"],
            "rejected_witnesses": ["w2"],
            "conflicting_witnesses": [],
            "errors": {},
            "reason": "witness quorum not reached",
        }

    monkeypatch.setattr(cli, "collect_rekor_witness_quorum", fake_collect)

    witness_private, _ = generate_keypair()
    witness_key = tmp_path / "witness.pem"
    witness_key.write_text(witness_private, encoding="ascii")
    rekor_key = tmp_path / "rekor.pem"
    rekor_key.write_text("submission-key", encoding="ascii")
    log_key = tmp_path / "rekor-log.pem"
    log_key.write_text("log-key", encoding="ascii")
    receipt_output = tmp_path / "receipt.json"

    args = argparse.Namespace(
        database=str(database),
        private_key=str(witness_key),
        witness_signer_uri=None,
        witness_signer_key_id=None,
        witness_signer_token_env=None,
        output=None,
        publish_url=None,
        bearer_token_env=None,
        rekor_url="https://rekor.example",
        rekor_private_key=str(rekor_key),
        rekor_log_public_key=str(log_key),
        rekor_witness_config="witnesses.json",
        receipt_output=str(receipt_output),
    )

    with pytest.raises(RuntimeError, match="witness quorum not reached"):
        cli.run_transparency_checkpoint(args)

    assert observed["log_id"] == "a" * 64
    assert observed["origin"] == "rekor.example - 42"
    assert observed["tree_size"] == 1
    assert observed["store"].backend is backend
    assert not receipt_output.exists()
