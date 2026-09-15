import base64
import hashlib

import pytest

from production_os.rekor_checkpoint_state import (
    RekorCheckpointStateError,
    RekorCheckpointStateStore,
    RekorCheckpointMonitor,
    verify_consistency_proof,
)
from production_os.sqlite_backend import SQLiteBackend


def _leaf(payload: bytes) -> bytes:
    return hashlib.sha256(b"\x00" + payload).digest()


def _node(left: bytes, right: bytes) -> bytes:
    return hashlib.sha256(b"\x01" + left + right).digest()


def _checkpoint(root_hash: str, tree_size: int, tree_id: int = 42) -> str:
    root_b64 = base64.b64encode(bytes.fromhex(root_hash)).decode("ascii")
    return (
        f"rekor.example - {tree_id}\n"
        f"{tree_size}\n"
        f"{root_b64}\n"
        "\n"
        "— rekor.example ignored-signature\n"
    )


def _receipt(root_hash: str, tree_size: int, *, log_id: str = "a" * 64) -> dict:
    return {
        "provider": "rekor-v1",
        "log_id": log_id,
        "inclusion_proof": {
            "treeSize": tree_size,
            "rootHash": root_hash,
            "checkpoint": _checkpoint(root_hash, tree_size),
        },
    }


def test_verify_consistency_proof_accepts_one_to_two_leaf_growth():
    first = _leaf(b"first")
    second = _leaf(b"second")
    new_root = _node(first, second)

    assert verify_consistency_proof(
        previous_tree_size=1,
        previous_root_hash=first.hex(),
        tree_size=2,
        root_hash=new_root.hex(),
        hashes=[second.hex()],
    ) is True


def test_monitor_bootstraps_and_persists_first_verified_checkpoint(tmp_path):
    backend = SQLiteBackend(tmp_path / "state.db")
    store = RekorCheckpointStateStore(backend)

    monitor = RekorCheckpointMonitor(
        store,
        proof_fetcher=lambda **_: pytest.fail("bootstrap must not request consistency proof"),
    )
    root = _leaf(b"first").hex()

    result = monitor.observe_verified_receipt(_receipt(root, 1))
    persisted = store.get("a" * 64, "rekor.example - 42")

    assert result["status"] == "bootstrapped"
    assert persisted is not None
    assert persisted["tree_size"] == 1
    assert persisted["root_hash"] == root


def test_monitor_advances_only_with_valid_consistency_proof(tmp_path):
    backend = SQLiteBackend(tmp_path / "state.db")
    store = RekorCheckpointStateStore(backend)
    first = _leaf(b"first")
    second = _leaf(b"second")
    new_root = _node(first, second)

    bootstrap = RekorCheckpointMonitor(
        store,
        proof_fetcher=lambda **_: pytest.fail("bootstrap must not fetch proof"),
    )
    bootstrap.observe_verified_receipt(_receipt(first.hex(), 1))

    observed = {}

    def proof_fetcher(**kwargs):
        observed.update(kwargs)
        return {"rootHash": new_root.hex(), "hashes": [second.hex()]}

    monitor = RekorCheckpointMonitor(store, proof_fetcher=proof_fetcher)
    result = monitor.observe_verified_receipt(_receipt(new_root.hex(), 2))
    persisted = store.get("a" * 64, "rekor.example - 42")

    assert result["status"] == "advanced"
    assert observed == {
        "first_size": 1,
        "last_size": 2,
        "tree_id": "42",
    }
    assert persisted is not None
    assert persisted["tree_size"] == 2
    assert persisted["root_hash"] == new_root.hex()


def test_monitor_rejects_split_view_without_overwriting_state(tmp_path):
    backend = SQLiteBackend(tmp_path / "state.db")
    store = RekorCheckpointStateStore(backend)
    original_root = _leaf(b"first").hex()

    monitor = RekorCheckpointMonitor(
        store,
        proof_fetcher=lambda **_: pytest.fail("same-size split view must not fetch proof"),
    )
    monitor.observe_verified_receipt(_receipt(original_root, 1))

    with pytest.raises(RekorCheckpointStateError, match="split-view"):
        monitor.observe_verified_receipt(_receipt(_leaf(b"evil").hex(), 1))

    persisted = store.get("a" * 64, "rekor.example - 42")
    assert persisted is not None
    assert persisted["tree_size"] == 1
    assert persisted["root_hash"] == original_root


def test_monitor_rejects_invalid_growth_proof_without_overwriting_state(tmp_path):
    backend = SQLiteBackend(tmp_path / "state.db")
    store = RekorCheckpointStateStore(backend)
    first = _leaf(b"first")
    second = _leaf(b"second")
    new_root = _node(first, second)

    RekorCheckpointMonitor(
        store,
        proof_fetcher=lambda **_: pytest.fail("bootstrap must not fetch proof"),
    ).observe_verified_receipt(_receipt(first.hex(), 1))

    monitor = RekorCheckpointMonitor(
        store,
        proof_fetcher=lambda **_: {
            "rootHash": new_root.hex(),
            "hashes": [_leaf(b"wrong").hex()],
        },
    )
    with pytest.raises(RekorCheckpointStateError, match="consistency proof"):
        monitor.observe_verified_receipt(_receipt(new_root.hex(), 2))

    persisted = store.get("a" * 64, "rekor.example - 42")
    assert persisted is not None
    assert persisted["tree_size"] == 1
    assert persisted["root_hash"] == first.hex()


def test_monitor_rejects_tree_rollback(tmp_path):
    backend = SQLiteBackend(tmp_path / "state.db")
    store = RekorCheckpointStateStore(backend)
    first = _leaf(b"first")
    second = _leaf(b"second")
    new_root = _node(first, second)

    store.put(
        log_id="a" * 64,
        origin="rekor.example - 42",
        tree_size=2,
        root_hash=new_root.hex(),
        checkpoint=_checkpoint(new_root.hex(), 2),
    )
    monitor = RekorCheckpointMonitor(
        store,
        proof_fetcher=lambda **_: pytest.fail("rollback must not fetch proof"),
    )

    with pytest.raises(RekorCheckpointStateError, match="rollback"):
        monitor.observe_verified_receipt(_receipt(first.hex(), 1))
