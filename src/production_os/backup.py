from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def create_backup(paths: list[str], destination_dir: str) -> dict:
    destination = Path(destination_dir)
    destination.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    root = destination / stamp
    root.mkdir(parents=True, exist_ok=False)

    files = []
    for raw in paths:
        source = Path(raw)
        if not source.exists() or not source.is_file():
            continue
        target = root / source.name
        shutil.copy2(source, target)
        files.append({
            "source": str(source),
            "backup": str(target),
            "sha256": _sha256(target),
        })

    manifest = {
        "schema_version": "production-os/backup/v1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "files": files,
    }
    (root / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return manifest
