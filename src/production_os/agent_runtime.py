from __future__ import annotations

import hashlib
import json
import os
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


_RUNTIME_SCHEMA = "production-os/persistent-agent-runtime/v1"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


@dataclass(frozen=True, slots=True)
class AgentRuntimeContext:
    job_key: str
    session_id: str
    workspace: str
    state_path: str
    checkpoint_path: str
    attempt: int
    resume: bool
    checkpoint_available: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": _RUNTIME_SCHEMA,
            "job_key": self.job_key,
            "session_id": self.session_id,
            "workspace": self.workspace,
            "state_path": self.state_path,
            "checkpoint_path": self.checkpoint_path,
            "attempt": self.attempt,
            "resume": self.resume,
            "checkpoint_available": self.checkpoint_available,
        }


class PersistentAgentRuntime:
    """Durable per-job runtime metadata and workspace.

    The control plane remains authoritative for queue ownership. This store only
    preserves executor-local context needed to resume useful work after a worker
    restart. Job keys are hashed before being used as paths.
    """

    def __init__(self, root: str | os.PathLike[str]):
        self.root = Path(root).expanduser().resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _job_dir_name(job_key: str) -> str:
        key = str(job_key or "").strip()
        if not key:
            raise ValueError("job_key is required")
        return hashlib.sha256(key.encode("utf-8")).hexdigest()[:24]

    def workspace_for(self, job_key: str) -> Path:
        path = self.root / self._job_dir_name(job_key)
        path.mkdir(parents=True, exist_ok=True)
        return path

    @staticmethod
    def _read_json(path: Path) -> dict[str, Any]:
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (FileNotFoundError, OSError, json.JSONDecodeError):
            return {}
        return value if isinstance(value, dict) else {}

    @staticmethod
    def _write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        temp = path.with_suffix(path.suffix + ".tmp")
        temp.write_text(
            json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2),
            encoding="utf-8",
        )
        os.replace(temp, path)

    def prepare(self, job_key: str) -> AgentRuntimeContext:
        key = str(job_key).strip()
        workspace = self.workspace_for(key)
        state_path = workspace / "runtime-state.json"
        checkpoint_path = workspace / "checkpoint.json"
        previous = self._read_json(state_path)

        same_job = previous.get("job_key") == key
        previous_status = str(previous.get("status") or "")
        attempt = int(previous.get("attempt") or 0) + 1 if same_job else 1
        session_id = (
            str(previous.get("session_id") or "")
            if same_job
            else ""
        ) or uuid.uuid4().hex
        resume = bool(
            same_job
            and (
                previous_status in {"running", "interrupted", "abandoned"}
                or checkpoint_path.is_file()
            )
        )

        payload = {
            "schema_version": _RUNTIME_SCHEMA,
            "job_key": key,
            "session_id": session_id,
            "attempt": attempt,
            "status": "running",
            "resume": resume,
            "checkpoint_available": checkpoint_path.is_file(),
            "started_at": _utc_now(),
            "updated_at": _utc_now(),
        }
        self._write_json_atomic(state_path, payload)
        return AgentRuntimeContext(
            job_key=key,
            session_id=session_id,
            workspace=str(workspace),
            state_path=str(state_path),
            checkpoint_path=str(checkpoint_path),
            attempt=attempt,
            resume=resume,
            checkpoint_available=checkpoint_path.is_file(),
        )

    def mark_outcome(self, job_key: str, outcome: dict[str, Any]) -> None:
        workspace = self.workspace_for(job_key)
        state_path = workspace / "runtime-state.json"
        state = self._read_json(state_path)
        if state.get("job_key") != str(job_key):
            return
        status = str(outcome.get("status") or "unknown")
        state["status"] = (
            "interrupted"
            if status == "abandoned"
            else status
        )
        state["last_outcome"] = {
            "status": status,
            **(
                {"reason": str(outcome.get("reason"))[:512]}
                if outcome.get("reason")
                else {}
            ),
        }
        state["checkpoint_available"] = (workspace / "checkpoint.json").is_file()
        state["updated_at"] = _utc_now()
        self._write_json_atomic(state_path, state)

    def inspect(self, job_key: str) -> dict[str, Any]:
        workspace = self.workspace_for(job_key)
        return self._read_json(workspace / "runtime-state.json")
