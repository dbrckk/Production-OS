from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

import pytest

from production_os.filesystem_lock import filesystem_lock


@pytest.mark.skipif(os.name != "posix", reason="cross-process flock requires POSIX")
def test_filesystem_lock_blocks_other_processes(tmp_path):
    lock = tmp_path / "shared.lock"
    marker = tmp_path / "acquired.txt"
    script = (
        "from pathlib import Path\n"
        "from production_os.filesystem_lock import filesystem_lock\n"
        f"lock = Path({str(lock)!r})\n"
        f"marker = Path({str(marker)!r})\n"
        "with filesystem_lock(lock):\n"
        "    marker.write_text('acquired', encoding='utf-8')\n"
    )

    with filesystem_lock(lock):
        process = subprocess.Popen([sys.executable, "-c", script])
        time.sleep(0.25)
        assert marker.exists() is False

    process.wait(timeout=5)

    assert process.returncode == 0
    assert marker.read_text(encoding="utf-8") == "acquired"


def test_filesystem_lock_creates_parent_directories(tmp_path):
    lock = tmp_path / "nested" / "locks" / "repo.lock"

    with filesystem_lock(lock):
        assert lock.is_file()
