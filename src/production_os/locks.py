from __future__ import annotations

import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path


class FileLock:
    def __init__(
        self,
        path: str | Path,
        *,
        timeout_seconds: float = 10.0,
        stale_after_seconds: float = 120.0,
        poll_interval: float = 0.05,
    ):
        self.path = Path(path)
        self.timeout_seconds = timeout_seconds
        self.stale_after_seconds = stale_after_seconds
        self.poll_interval = poll_interval
        self._owned = False

    def acquire(self) -> None:
        deadline = time.monotonic() + self.timeout_seconds
        self.path.parent.mkdir(parents=True, exist_ok=True)

        while True:
            try:
                fd = os.open(
                    self.path,
                    os.O_CREAT | os.O_EXCL | os.O_WRONLY,
                    0o600,
                )
                payload = {
                    "pid": os.getpid(),
                    "created_at": datetime.now(timezone.utc).isoformat(),
                }
                with os.fdopen(fd, "w", encoding="utf-8") as handle:
                    json.dump(payload, handle)
                self._owned = True
                return
            except FileExistsError:
                try:
                    age = time.time() - self.path.stat().st_mtime
                    if age > self.stale_after_seconds:
                        self.path.unlink(missing_ok=True)
                        continue
                except FileNotFoundError:
                    continue

                if time.monotonic() >= deadline:
                    raise TimeoutError(f"lock timeout: {self.path}")
                time.sleep(self.poll_interval)

    def release(self) -> None:
        if self._owned:
            self.path.unlink(missing_ok=True)
            self._owned = False

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.release()
        return False


def sidecar_lock(path: str | Path) -> FileLock:
    target = Path(path)
    return FileLock(target.with_suffix(target.suffix + ".lock"))
