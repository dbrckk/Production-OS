from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


def write_dispatch_receipt(
    directory: str | Path,
    *,
    key: str,
    worker_id: str,
    repository: str,
    task: str,
    status: str = "dispatched",
) -> str:
    path=Path(directory)
    path.mkdir(parents=True,exist_ok=True)
    dest=path/f"{key}.receipt.json"
    payload={
        "schema_version":"production-os/dispatch-receipt/v1",
        "timestamp":datetime.now(timezone.utc).isoformat(),
        "key":key,
        "worker_id":worker_id,
        "repository":repository,
        "task":task,
        "status":status,
    }
    dest.write_text(json.dumps(payload,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    return str(dest)
