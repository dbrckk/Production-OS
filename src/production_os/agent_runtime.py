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
_CHECKPOINT_SCHEMA = "production-os/agent-checkpoint/v1"
_MAX_CHECKPOINT_BYTES = 4 * 1024 * 1024


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(
        json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2),
        encoding="utf-8",
    )
    os.replace(temp, path)


def write_agent_checkpoint(
    path: str | os.PathLike[str],
    *,
    job_key: str,
    session_id: str,
    sequence: int,
    state: dict[str, Any],
    resume_token: str | None = None,
) -> None:
    """Atomically publish a resumable executor checkpoint."""
    key = str(job_key or "").strip()
    session = str(session_id or "").strip()
    if not key:
        raise ValueError("job_key is required")
    if not session:
        raise ValueError("session_id is required")
    if int(sequence) < 1:
        raise ValueError("sequence must be >= 1")
    if not isinstance(state, dict):
        raise ValueError("state must be an object")
    payload = {
        "schema_version": _CHECKPOINT_SCHEMA,
        "job_key": key,
        "session_id": session,
        "sequence": int(sequence),
        "created_at": _utc_now(),
        "state": state,
    }
    if resume_token is not None:
        payload["resume_token"] = str(resume_token)
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        indent=2,
    ).encode("utf-8")
    if len(encoded) > _MAX_CHECKPOINT_BYTES:
        raise ValueError("checkpoint exceeds maximum size")
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    temp = target.with_suffix(target.suffix + ".tmp")
    temp.write_bytes(encoded)
    os.replace(temp, target)


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
            "checkpoint_schema": _CHECKPOINT_SCHEMA,
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
        _write_json_atomic(path, payload)

    def _checkpoint_details(
        self,
        job_key: str,
        *,
        session_id: str | None = None,
    ) -> dict[str, Any]:
        workspace = self.workspace_for(job_key)
        checkpoint_path = workspace / "checkpoint.json"
        try:
            raw = checkpoint_path.read_bytes()
        except OSError:
            return {"valid": False, "reason": "missing"}
        if not raw:
            return {"valid": False, "reason": "empty"}
        if len(raw) > _MAX_CHECKPOINT_BYTES:
            return {"valid": False, "reason": "too_large"}
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            return {"valid": False, "reason": "invalid_json"}
        if not isinstance(payload, dict):
            return {"valid": False, "reason": "invalid_shape"}

        schema = str(payload.get("schema_version") or "")
        sequence = 0
        if schema:
            if schema != _CHECKPOINT_SCHEMA:
                return {"valid": False, "reason": "unsupported_schema"}
            if str(payload.get("job_key") or "") != str(job_key):
                return {"valid": False, "reason": "job_mismatch"}
            if session_id and str(payload.get("session_id") or "") != session_id:
                return {"valid": False, "reason": "session_mismatch"}
            try:
                sequence = int(payload.get("sequence"))
            except (TypeError, ValueError):
                return {"valid": False, "reason": "invalid_sequence"}
            if sequence < 1:
                return {"valid": False, "reason": "invalid_sequence"}
            if not isinstance(payload.get("state"), dict):
                return {"valid": False, "reason": "invalid_state"}
        else:
            # Backwards compatibility with the first persistent-runtime release.
            schema = "legacy-json-object"

        digest = hashlib.sha256(raw).hexdigest()
        return {
            "valid": True,
            "schema_version": schema,
            "sequence": sequence,
            "sha256": digest,
            "size_bytes": len(raw),
            "ref": (
                "runtime-checkpoint://"
                f"{self._job_dir_name(job_key)}/{digest}"
            ),
            "path": str(checkpoint_path),
        }

    def observe_checkpoint(self, job_key: str) -> dict[str, Any]:
        workspace = self.workspace_for(job_key)
        state_path = workspace / "runtime-state.json"
        state = self._read_json(state_path)
        session_id = (
            str(state.get("session_id") or "")
            if state.get("job_key") == str(job_key)
            else ""
        )
        details = self._checkpoint_details(
            job_key,
            session_id=session_id or None,
        )
        previous = dict(state.get("checkpoint") or {})
        changed = False
        if details.get("valid"):
            checkpoint = {
                key: details[key]
                for key in (
                    "schema_version",
                    "sequence",
                    "sha256",
                    "size_bytes",
                    "ref",
                )
            }
            checkpoint["observed_at"] = (
                previous.get("observed_at")
                if previous.get("sha256") == checkpoint["sha256"]
                else _utc_now()
            )
            if previous != checkpoint:
                state["checkpoint"] = checkpoint
                changed = True
            if state.get("checkpoint_available") is not True:
                state["checkpoint_available"] = True
                changed = True
            if "checkpoint_error" in state:
                state.pop("checkpoint_error", None)
                changed = True
        else:
            if state.get("checkpoint_available") is not False:
                state["checkpoint_available"] = False
                changed = True
            reason = str(details.get("reason") or "invalid")
            if reason not in {"missing", "empty"}:
                if state.get("checkpoint_error") != reason:
                    state["checkpoint_error"] = reason
                    changed = True
            elif "checkpoint_error" in state:
                state.pop("checkpoint_error", None)
                changed = True
        if state.get("job_key") == str(job_key) and changed:
            state["updated_at"] = _utc_now()
            self._write_json_atomic(state_path, state)
        return details

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
        checkpoint = self._checkpoint_details(
            key,
            session_id=session_id if same_job else None,
        )
        checkpoint_available = bool(checkpoint.get("valid"))
        resume = bool(
            same_job
            and (
                previous_status in {"running", "interrupted", "abandoned"}
                or checkpoint_available
            )
        )

        payload = {
            "schema_version": _RUNTIME_SCHEMA,
            "job_key": key,
            "session_id": session_id,
            "attempt": attempt,
            "status": "running",
            "resume": resume,
            "checkpoint_available": checkpoint_available,
            "started_at": _utc_now(),
            "updated_at": _utc_now(),
        }
        if checkpoint_available:
            payload["checkpoint"] = {
                name: checkpoint[name]
                for name in (
                    "schema_version",
                    "sequence",
                    "sha256",
                    "size_bytes",
                    "ref",
                )
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
            checkpoint_available=checkpoint_available,
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
        checkpoint = self._checkpoint_details(
            job_key,
            session_id=str(state.get("session_id") or "") or None,
        )
        state["checkpoint_available"] = bool(checkpoint.get("valid"))
        if checkpoint.get("valid"):
            state["checkpoint"] = {
                name: checkpoint[name]
                for name in (
                    "schema_version",
                    "sequence",
                    "sha256",
                    "size_bytes",
                    "ref",
                )
            }
        state["updated_at"] = _utc_now()
        self._write_json_atomic(state_path, state)

    def inspect(self, job_key: str) -> dict[str, Any]:
        workspace = self.workspace_for(job_key)
        return self._read_json(workspace / "runtime-state.json")
