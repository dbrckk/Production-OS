from __future__ import annotations

from pathlib import Path

import pytest

import production_os.controller_leader as leader


def test_filesystem_controller_leader_lock_is_exclusive_and_releasable(tmp_path):
    path = tmp_path / "controller.lock"
    first = leader.FilesystemControllerLeaderLock(path)
    second = leader.FilesystemControllerLeaderLock(path)

    first.acquire()
    try:
        with pytest.raises(
            leader.ControllerLeaderError,
            match="already active",
        ):
            second.acquire()
    finally:
        first.release()

    second.acquire()
    second.release()


def test_controller_leader_factory_uses_durable_file_for_sqlite(tmp_path):
    database = tmp_path / "production.db"
    lock = leader.controller_leader_lock(
        database_path=str(database),
        runtime_state_path=None,
        journal_path=None,
    )

    assert isinstance(lock, leader.FilesystemControllerLeaderLock)
    assert lock.path == Path(str(database) + ".controller.lock").resolve()


def test_controller_leader_factory_falls_back_to_runtime_state(tmp_path):
    runtime = tmp_path / "runtime.json"
    lock = leader.controller_leader_lock(
        database_path=None,
        runtime_state_path=str(runtime),
        journal_path=None,
    )

    assert lock.path == Path(str(runtime) + ".controller.lock").resolve()


def test_postgres_controller_leader_lock_holds_session_advisory_lock(monkeypatch):
    calls = []

    class Result:
        def __init__(self, row):
            self.row = row

        def fetchone(self):
            return self.row

    class Connection:
        def __init__(self):
            self.closed = False

        def execute(self, sql, params):
            calls.append((sql, params))
            if "pg_try_advisory_lock" in sql:
                return Result({"acquired":True})
            return Result({"pg_advisory_unlock":True})

        def close(self):
            self.closed = True

    connection = Connection()

    class Backend:
        def __init__(self, dsn):
            assert dsn == "postgresql://example/test"

        def connect(self):
            return connection

    monkeypatch.setattr(leader, "PostgresBackend", Backend)

    lock = leader.PostgresControllerLeaderLock(
        "postgresql://example/test"
    )
    lock.acquire()

    assert lock._connection is connection
    assert "pg_try_advisory_lock" in calls[0][0]
    assert connection.closed is False

    lock.release()

    assert "pg_advisory_unlock" in calls[-1][0]
    assert connection.closed is True


def test_postgres_controller_leader_lock_rejects_second_leader(monkeypatch):
    class Result:
        def fetchone(self):
            return {"acquired":False}

    class Connection:
        def __init__(self):
            self.closed = False

        def execute(self, _sql, _params):
            return Result()

        def close(self):
            self.closed = True

    connection = Connection()

    class Backend:
        def __init__(self, _dsn):
            pass

        def connect(self):
            return connection

    monkeypatch.setattr(leader, "PostgresBackend", Backend)
    lock = leader.PostgresControllerLeaderLock(
        "postgresql://example/test"
    )

    with pytest.raises(
        leader.ControllerLeaderError,
        match="already active",
    ):
        lock.acquire()

    assert connection.closed is True
