from __future__ import annotations

import os
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

try:
    import fcntl
except ImportError:  # pragma: no cover - non-POSIX fallback
    fcntl = None


_guard = threading.Lock()
_thread_locks: dict[str, threading.Lock] = {}


def _thread_lock(path: Path) -> threading.Lock:
    key = str(path)
    with _guard:
        return _thread_locks.setdefault(key, threading.Lock())


@contextmanager
def filesystem_lock(path: str | os.PathLike[str]) -> Iterator[None]:
    """Serialize a critical section across threads and POSIX processes."""
    target = Path(path).expanduser().resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    local = _thread_lock(target)
    with local:
        handle = target.open("a+", encoding="utf-8")
        try:
            if fcntl is not None:
                fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
            yield
        finally:
            if fcntl is not None:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
            handle.close()
