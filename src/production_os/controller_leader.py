from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from .postgres_backend import PostgresBackend
from .storage import is_postgres

try:
    import fcntl
except ImportError:  # pragma: no cover - production server images are POSIX.
    fcntl = None


class ControllerLeaderError(RuntimeError):
    pass


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class FilesystemControllerLeaderLock:
    def __init__(self, path: str | os.PathLike[str]):
        self.path = Path(path).expanduser().resolve()
        self._fd: int | None = None

    def acquire(self) -> None:
        if fcntl is None:
            raise ControllerLeaderError(
                "controller leader lock requires POSIX flock"
            )
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(self.path, os.O_CREAT | os.O_RDWR, 0o600)
        try:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as exc:
                raise ControllerLeaderError(
                    "another Production-OS controller daemon is already active"
                ) from exc

            payload = {
                "pid":os.getpid(),
                "purpose":"production-os-controller-daemon",
                "acquired_at":_utc_now(),
            }
            encoded = json.dumps(
                payload,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
            os.ftruncate(fd, 0)
            os.lseek(fd, 0, os.SEEK_SET)
            os.write(fd, encoded)
            os.fsync(fd)
            self._fd = fd
        except Exception:
            os.close(fd)
            raise

    def release(self) -> None:
        fd = self._fd
        if fd is None:
            return
        self._fd = None
        try:
            if fcntl is not None:
                fcntl.flock(fd, fcntl.LOCK_UN)
        finally:
            os.close(fd)

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.release()
        return False


class PostgresControllerLeaderLock:
    _LOCK_KEY = int.from_bytes(
        hashlib.sha256(
            b"production-os/controller-daemon/v1"
        ).digest()[:8],
        "big",
        signed=True,
    )

    def __init__(self, dsn: str):
        self.dsn = str(dsn)
        self._connection = None

    def acquire(self) -> None:
        backend = PostgresBackend(self.dsn)
        connection = backend.connect()
        try:
            row = connection.execute(
                "SELECT pg_try_advisory_lock(%s) AS acquired",
                (self._LOCK_KEY,),
            ).fetchone()
            acquired = bool(
                row.get("acquired")
                if isinstance(row, dict)
                else row[0]
            )
            if not acquired:
                raise ControllerLeaderError(
                    "another Production-OS controller daemon is already active"
                )
            self._connection = connection
        except Exception:
            connection.close()
            raise

    def release(self) -> None:
        connection = self._connection
        if connection is None:
            return
        self._connection = None
        try:
            connection.execute(
                "SELECT pg_advisory_unlock(%s)",
                (self._LOCK_KEY,),
            )
        finally:
            connection.close()

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.release()
        return False


def controller_leader_lock(
    *,
    database_path: str | None,
    runtime_state_path: str | None,
    journal_path: str | None,
):
    if database_path and is_postgres(str(database_path)):
        return PostgresControllerLeaderLock(str(database_path))

    anchor = (
        str(database_path or "").strip()
        or str(runtime_state_path or "").strip()
        or str(journal_path or "").strip()
    )
    if not anchor:
        raise ControllerLeaderError(
            "controller daemon requires a durable state path for leader locking"
        )
    return FilesystemControllerLeaderLock(anchor + ".controller.lock")
