from __future__ import annotations

from contextlib import contextmanager
import json
import os

import pytest

from production_os.api_auth import TokenAuthorizer
from production_os.control_plane import serve_control_plane
from production_os.database_maintenance_lock import (
    DatabaseInUseError,
    SQLiteDatabaseProcessLock,
    database_server_lock,
)


def test_sqlite_database_lock_blocks_second_live_owner(tmp_path):
    database = tmp_path / "production.sqlite"
    first = SQLiteDatabaseProcessLock(str(database))
    second = SQLiteDatabaseProcessLock(str(database))
    first.acquire()
    try:
        metadata = json.loads(
            (tmp_path / "production.sqlite.maintenance.lock").read_text()
        )
        assert metadata["pid"] == os.getpid()
        assert metadata["purpose"] == "production-os-control-plane"
        with pytest.raises(DatabaseInUseError, match="already locked"):
            second.acquire()
    finally:
        first.release()


def test_sqlite_database_lock_can_be_reacquired_after_release(tmp_path):
    database = tmp_path / "production.sqlite"
    first = SQLiteDatabaseProcessLock(str(database))
    first.acquire()
    first.release()

    second = SQLiteDatabaseProcessLock(str(database))
    second.acquire()
    try:
        assert second._fd is not None
    finally:
        second.release()


def test_lock_file_persistence_does_not_mean_database_is_locked(tmp_path):
    database = tmp_path / "production.sqlite"
    path = tmp_path / "production.sqlite.maintenance.lock"
    path.write_text(
        json.dumps({
            "pid":99999999,
            "created_at":"2000-01-01T00:00:00+00:00",
            "purpose":"stale-metadata",
        })
    )

    lock = SQLiteDatabaseProcessLock(str(database))
    lock.acquire()
    try:
        metadata = json.loads(path.read_text())
        assert metadata["pid"] == os.getpid()
        assert metadata["purpose"] == "production-os-control-plane"
    finally:
        lock.release()


def test_postgres_database_server_lock_is_noop():
    with database_server_lock(
        "postgresql://user:password@localhost/db"
    ):
        pass


def test_serve_control_plane_holds_lock_for_server_lifetime(
    tmp_path,
    monkeypatch,
):
    events = []

    @contextmanager
    def fake_lock(database):
        events.append(("lock-enter", database))
        try:
            yield
        finally:
            events.append(("lock-exit", database))

    class FakeServer:
        def __init__(self, address, handler):
            events.append(("server-init", address))
            self.handler = handler

        def serve_forever(self):
            events.append(("serve", None))

        def server_close(self):
            events.append(("server-close", None))

    monkeypatch.setattr(
        "production_os.control_plane.database_server_lock",
        fake_lock,
    )
    monkeypatch.setattr(
        "production_os.control_plane.ThreadingHTTPServer",
        FakeServer,
    )
    monkeypatch.setattr(
        "production_os.control_plane.TokenAuthorizer.load",
        lambda path: TokenAuthorizer([]),
    )

    database = str(tmp_path / "production.sqlite")
    serve_control_plane(
        database,
        str(tmp_path / "auth.json"),
        host="127.0.0.1",
        port=0,
    )

    assert events[0] == ("lock-enter", database)
    assert events[1][0] == "server-init"
    assert events[2] == ("serve", None)
    assert events[3] == ("server-close", None)
    assert events[4] == ("lock-exit", database)
