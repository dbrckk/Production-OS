import base64
import hashlib

import pytest

from production_os.rekor_checkpoint_state import (
    RekorCheckpointMonitor,
    RekorCheckpointStateError,
    RekorCheckpointStateStore,
)
from production_os.sqlite_backend import SQLiteBackend


def _leaf(payload: bytes) -> bytes:
    return hashlib.sha256(b"\x00" + payload).digest()


def _node(left: bytes, right: bytes) -> bytes:
    return hashlib.sha256(b"\x01" + left + right).digest()


def _checkpoint(root_hash: str, tree_size: int) -> str:
    root_b64 = base64.b64encode(bytes.fromhex(root_hash)).decode("ascii")
    return (
        "rekor.example - 42\n"
        f"{tree_size}\n"
        f"{root_b64}\n"
        "\n"
        "— rekor.example already-verified\n"
    )


def _receipt(root_hash: str, tree_size: int) -> dict:
    return {
        "provider": "rekor-v1",
        "log_id": "a" * 64,
        "inclusion_proof": {
            "treeSize": tree_size,
            "rootHash": root_hash,
            "checkpoint": _checkpoint(root_hash, tree_size),
        },
    }


def test_slow_observer_cannot_overwrite_newer_checkpoint_state(tmp_path):
    backend = SQLiteBackend(tmp_path / "state.db")
    store = RekorCheckpointStateStore(backend)
    first = _leaf(b"first")
    second = _leaf(b"second")
    third = _leaf(b"third")
    size_two_root = _node(first, second)
    size_three_root = _node(size_two_root, third)

    RekorCheckpointMonitor(
        store,
        proof_fetcher=lambda **_: pytest.fail("bootstrap must not fetch proof"),
    ).observe_verified_receipt(_receipt(first.hex(), 1))

    def proof_fetcher(**_):
        store.put(
            log_id="a" * 64,
            origin="rekor.example - 42",
            tree_id="42",
            tree_size=3,
            root_hash=size_three_root.hex(),
            checkpoint=_checkpoint(size_three_root.hex(), 3),
        )
        return {
            "rootHash": size_two_root.hex(),
            "hashes": [second.hex()],
        }

    monitor = RekorCheckpointMonitor(store, proof_fetcher=proof_fetcher)
    with pytest.raises(RekorCheckpointStateError, match="concurrent"):
        monitor.observe_verified_receipt(_receipt(size_two_root.hex(), 2))

    persisted = store.get("a" * 64, "rekor.example - 42")
    assert persisted is not None
    assert persisted["tree_size"] == 3
    assert persisted["root_hash"] == size_three_root.hex()


def test_concurrent_first_observation_cannot_replace_bootstrap_state(tmp_path):
    backend = SQLiteBackend(tmp_path / "state.db")
    trusted_root = _leaf(b"trusted").hex()
    competing_root = _leaf(b"competing").hex()

    class RacingStore(RekorCheckpointStateStore):
        raced = False

        def get(self, log_id, origin):
            current = super().get(log_id, origin)
            if not self.raced and current is None:
                self.raced = True
                super().put(
                    log_id=log_id,
                    origin=origin,
                    tree_id="42",
                    tree_size=1,
                    root_hash=competing_root,
                    checkpoint=_checkpoint(competing_root, 1),
                )
            return current

    store = RacingStore(backend)
    monitor = RekorCheckpointMonitor(
        store,
        proof_fetcher=lambda **_: pytest.fail("bootstrap must not fetch proof"),
    )

    with pytest.raises(RekorCheckpointStateError, match="concurrent"):
        monitor.observe_verified_receipt(_receipt(trusted_root, 1))

    persisted = RekorCheckpointStateStore(backend).get(
        "a" * 64,
        "rekor.example - 42",
    )
    assert persisted is not None
    assert persisted["root_hash"] == competing_root
