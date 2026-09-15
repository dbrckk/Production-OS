import argparse
import base64
import hashlib
import json

from production_os import cli
from production_os.rekor_checkpoint_state import RekorCheckpointStateStore
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


def test_checkpoint_publication_persists_verified_rekor_state(
    tmp_path, monkeypatch, capsys
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

    receipt = _receipt()

    class FakePublisher:
        timeout_seconds = 10.0

        @classmethod
        def from_private_key(cls, *args, **kwargs):
            return cls()

        def publish(self, envelope):
            return receipt

    monkeypatch.setattr(cli, "RekorV1Publisher", FakePublisher)

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
        receipt_output=str(receipt_output),
    )

    assert cli.run_transparency_checkpoint(args) == 0
    result = json.loads(capsys.readouterr().out)

    assert result["rekor_checkpoint_state"]["status"] == "bootstrapped"
    stored = RekorCheckpointStateStore(backend).get(
        "a" * 64,
        "rekor.example - 42",
    )
    assert stored is not None
    assert stored["tree_size"] == 1
    assert receipt_output.exists()
