import hashlib
import os

import pytest

from production_os.postgres_backend import PostgresBackend
from production_os.rekor_checkpoint_state import RekorCheckpointStateStore


DSN = os.getenv("PRODUCTION_OS_TEST_POSTGRES")

pytestmark = pytest.mark.skipif(
    not DSN,
    reason="PRODUCTION_OS_TEST_POSTGRES not configured",
)


def test_rekor_checkpoint_state_round_trips_on_postgres():
    backend = PostgresBackend(DSN)
    store = RekorCheckpointStateStore(backend)
    log_id = hashlib.sha256(b"rekor-checkpoint-state-postgres").hexdigest()
    origin = "rekor.example - 4242"
    root_hash = hashlib.sha256(b"root").hexdigest()

    with backend.connect() as db:
        db.execute(
            "DELETE FROM rekor_checkpoint_state WHERE log_id=%s AND origin=%s",
            (log_id, origin),
        )

    stored = store.put(
        log_id=log_id,
        origin=origin,
        tree_id="4242",
        tree_size=3_000_000_000,
        root_hash=root_hash,
        checkpoint="signed-checkpoint",
    )
    loaded = store.get(log_id, origin)

    assert stored["tree_size"] == 3_000_000_000
    assert loaded is not None
    assert loaded["tree_size"] == 3_000_000_000
    assert loaded["root_hash"] == root_hash
