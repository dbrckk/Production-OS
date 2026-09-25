from __future__ import annotations

from contextlib import nullcontext
from datetime import datetime, timezone
import json
import os
from pathlib import Path

from .storage import is_postgres

try:
    import fcntl
except ImportError:  # pragma: no cover - Production-OS servers run on POSIX.
    fcntl = None


class DatabaseInUseError(RuntimeError):
    pass


class SQLiteDatabaseProcessLock:
    def __init__(self, database: str):
        self.database = str(database)
        self.path = Path(self.database + ".maintenance.lock")
        self._fd: int | None = None

    def acquire(self) -> None:
        if fcntl is None:
            raise DatabaseInUseError(
                "exclusive SQLite maintenance lock requires POSIX flock"
            )
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(
            self.path,
            os.O_CREAT | os.O_RDWR,
            0o600,
        )
        try:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as exc:
                owner = self._read_metadata(fd)
                suffix = (
                    f" (pid {owner.get('pid')})"
                    if isinstance(owner, dict) and owner.get("pid")
                    else ""
                )
                raise DatabaseInUseError(
                    "SQLite database is already locked by a live "
                    f"Production-OS process{suffix}"
                ) from exc

            payload = {
                "pid":os.getpid(),
                "created_at":datetime.now(timezone.utc).isoformat(),
                "purpose":"production-os-control-plane",
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

    @staticmethod
    def _read_metadata(fd: int) -> dict:
        try:
            os.lseek(fd, 0, os.SEEK_SET)
            raw = os.read(fd, 4096)
            payload = json.loads(raw.decode("utf-8")) if raw else {}
            return payload if isinstance(payload, dict) else {}
        except Exception:
            return {}

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


def database_server_lock(database: str):
    if is_postgres(str(database)):
        return nullcontext()
    return SQLiteDatabaseProcessLock(str(database))
