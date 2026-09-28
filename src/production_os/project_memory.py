from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from typing import Any


MEMORY_SCHEMA = "production-os/project-memory/v1"
_TERM = re.compile(r"[a-z0-9][a-z0-9._/-]{2,63}")
_SHA = re.compile(r"^[0-9a-f]{7,64}$", re.I)
_SECRET_PATTERNS = (
    re.compile(r"(?i)\bbearer\s+[a-z0-9._~+/-]{12,}"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{16,}\b"),
    re.compile(r"(?i)\b(password|passwd|secret|token|api[_-]?key)\s*[=:]\s*\S{8,}"),
)


def _is_postgres(backend) -> bool:
    return backend.__class__.__name__.startswith("Postgres")


def _sql(backend, statement: str) -> str:
    return statement.replace("?", "%s") if _is_postgres(backend) else statement


def _execute(db, backend, statement: str, params: tuple = ()):
    return db.execute(_sql(backend, statement), params)


def _terms(value: str) -> set[str]:
    return {
        term
        for term in _TERM.findall(str(value or "").lower())
        if len(term) >= 3
    }


def _clean_text(value: Any, *, limit: int) -> str:
    text = " ".join(str(value or "").split()).strip()
    if not text:
        return ""
    if any(pattern.search(text) for pattern in _SECRET_PATTERNS):
        return ""
    return text[:limit]


def _clean_list(value: Any, *, items: int, item_limit: int) -> list[str]:
    if not isinstance(value, list):
        return []
    rows: list[str] = []
    for raw in value:
        text = _clean_text(raw, limit=item_limit)
        if text and text not in rows:
            rows.append(text)
        if len(rows) >= items:
            break
    return rows


@dataclass(frozen=True, slots=True)
class ProjectMemory:
    event_id: int
    repository: str
    project_id: str
    generation: int
    workflow_id: str
    task_id: str
    kind: str
    summary: str
    validation_status: str
    commit_shas: tuple[str, ...]
    changed_files: tuple[str, ...]
    decisions: tuple[str, ...]
    constraints: tuple[str, ...]
    facts: tuple[str, ...]
    risks: tuple[str, ...]
    next_steps: tuple[str, ...]
    created_at: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version":MEMORY_SCHEMA,
            "event_id":self.event_id,
            "repository":self.repository,
            "project_id":self.project_id,
            "generation":self.generation,
            "workflow_id":self.workflow_id,
            "task_id":self.task_id,
            "kind":self.kind,
            "summary":self.summary,
            "validation_status":self.validation_status,
            "commit_shas":list(self.commit_shas),
            "changed_files":list(self.changed_files),
            "decisions":list(self.decisions),
            "constraints":list(self.constraints),
            "facts":list(self.facts),
            "risks":list(self.risks),
            "next_steps":list(self.next_steps),
            "created_at":self.created_at,
        }


class ProjectMemoryStore:
    def __init__(self, backend):
        self.backend = backend

    @staticmethod
    def _payload(
        *,
        project_id: str,
        generation: int,
        workflow_id: str,
        task_id: str,
        kind: str,
        result: dict[str, Any],
    ) -> dict[str, Any] | None:
        summary = _clean_text(result.get("summary"), limit=1200)
        validation = result.get("validation")
        validation_status = ""
        if isinstance(validation, dict):
            validation_status = _clean_text(
                validation.get("status"),
                limit=80,
            )

        commit_shas = [
            str(value).lower()
            for value in (result.get("commit_shas") or [])
            if _SHA.fullmatch(str(value or "").strip())
        ][:8]
        changed_files = _clean_list(
            result.get("changed_files"),
            items=30,
            item_limit=300,
        )

        explicit = result.get("project_memory")
        explicit = explicit if isinstance(explicit, dict) else {}
        decisions = _clean_list(
            explicit.get("decisions"),
            items=8,
            item_limit=500,
        )
        constraints = _clean_list(
            explicit.get("constraints"),
            items=8,
            item_limit=500,
        )
        facts = _clean_list(
            explicit.get("facts"),
            items=10,
            item_limit=500,
        )
        risks = _clean_list(
            explicit.get("risks"),
            items=8,
            item_limit=500,
        )
        next_steps = _clean_list(
            explicit.get("next_steps"),
            items=8,
            item_limit=500,
        )

        if not any((
            summary,
            validation_status,
            commit_shas,
            changed_files,
            decisions,
            constraints,
            facts,
            risks,
            next_steps,
        )):
            return None

        payload = {
            "schema_version":MEMORY_SCHEMA,
            "project_id":str(project_id),
            "generation":max(1, int(generation)),
            "workflow_id":str(workflow_id),
            "task_id":str(task_id),
            "kind":_clean_text(kind, limit=80) or "execution",
            "summary":summary,
            "validation_status":validation_status,
            "commit_shas":commit_shas,
            "changed_files":changed_files,
            "decisions":decisions,
            "constraints":constraints,
            "facts":facts,
            "risks":risks,
            "next_steps":next_steps,
        }
        canonical = json.dumps(
            {
                key:payload[key]
                for key in (
                    "project_id",
                    "task_id",
                    "kind",
                    "summary",
                    "validation_status",
                    "commit_shas",
                    "changed_files",
                    "decisions",
                    "constraints",
                    "facts",
                    "risks",
                    "next_steps",
                )
            },
            ensure_ascii=False,
            sort_keys=True,
        )
        payload["memory_fingerprint"] = hashlib.sha256(
            canonical.encode("utf-8")
        ).hexdigest()
        return payload

    def record_from_result(
        self,
        *,
        repository: str,
        project_id: str,
        generation: int,
        workflow_id: str,
        task_id: str,
        kind: str,
        result: dict[str, Any],
    ) -> dict[str, Any] | None:
        payload = self._payload(
            project_id=project_id,
            generation=generation,
            workflow_id=workflow_id,
            task_id=task_id,
            kind=kind,
            result=dict(result or {}),
        )
        if payload is None:
            return None

        with self.backend.connect() as db:
            recent = _execute(
                db,
                self.backend,
                """
                SELECT id,payload_json FROM events
                WHERE event_type='project-memory'
                  AND repository=? AND task_key=?
                ORDER BY id DESC
                LIMIT 100
                """,
                (str(repository), str(project_id)),
            ).fetchall()
        fingerprint = str(payload["memory_fingerprint"])
        for row in recent:
            try:
                existing = json.loads(row["payload_json"])
            except (TypeError, ValueError, json.JSONDecodeError):
                continue
            if (
                isinstance(existing, dict)
                and existing.get("memory_fingerprint") == fingerprint
            ):
                return {
                    "event_id":int(row["id"]),
                    "deduplicated":True,
                    **existing,
                }

        with self.backend.transaction() as db:
            event_id = self.backend.append_event(
                db,
                "project-memory",
                payload,
                repository=str(repository),
                task_key_value=str(project_id),
            )
        return {
            "event_id":event_id,
            "deduplicated":False,
            **payload,
        }

    @staticmethod
    def _from_row(row) -> ProjectMemory | None:
        try:
            payload = json.loads(row["payload_json"])
        except (TypeError, ValueError, json.JSONDecodeError):
            return None
        if not isinstance(payload, dict):
            return None
        if payload.get("schema_version") != MEMORY_SCHEMA:
            return None
        return ProjectMemory(
            event_id=int(row["id"]),
            repository=str(row["repository"] or ""),
            project_id=str(payload.get("project_id") or ""),
            generation=int(payload.get("generation") or 1),
            workflow_id=str(payload.get("workflow_id") or ""),
            task_id=str(payload.get("task_id") or ""),
            kind=str(payload.get("kind") or ""),
            summary=str(payload.get("summary") or ""),
            validation_status=str(payload.get("validation_status") or ""),
            commit_shas=tuple(payload.get("commit_shas") or ()),
            changed_files=tuple(payload.get("changed_files") or ()),
            decisions=tuple(payload.get("decisions") or ()),
            constraints=tuple(payload.get("constraints") or ()),
            facts=tuple(payload.get("facts") or ()),
            risks=tuple(payload.get("risks") or ()),
            next_steps=tuple(payload.get("next_steps") or ()),
            created_at=str(row["created_at"] or ""),
        )

    def recall(
        self,
        *,
        repository: str,
        project_id: str | None,
        query: str,
        limit: int = 6,
    ) -> list[ProjectMemory]:
        bounded = max(1, min(int(limit), 12))
        with self.backend.connect() as db:
            rows = _execute(
                db,
                self.backend,
                """
                SELECT id,repository,payload_json,created_at
                FROM events
                WHERE event_type='project-memory' AND repository=?
                ORDER BY id DESC
                LIMIT 250
                """,
                (str(repository),),
            ).fetchall()

        query_terms = _terms(query)
        scored: list[tuple[float, ProjectMemory]] = []
        seen_fingerprints: set[str] = set()
        for rank, row in enumerate(rows):
            try:
                raw_payload = json.loads(row["payload_json"])
            except (TypeError, ValueError, json.JSONDecodeError):
                raw_payload = {}
            fingerprint = str(
                raw_payload.get("memory_fingerprint") or ""
            )
            if fingerprint and fingerprint in seen_fingerprints:
                continue
            if fingerprint:
                seen_fingerprints.add(fingerprint)
            memory = self._from_row(row)
            if memory is None:
                continue
            same_project = bool(
                project_id
                and memory.project_id == str(project_id)
            )
            searchable = " ".join((
                memory.summary,
                " ".join(memory.changed_files),
                " ".join(memory.decisions),
                " ".join(memory.constraints),
                " ".join(memory.facts),
                " ".join(memory.risks),
                " ".join(memory.next_steps),
            ))
            overlap = len(query_terms.intersection(_terms(searchable)))
            if not same_project and query_terms and overlap == 0:
                continue
            score = (
                (12.0 if same_project else 0.0)
                + overlap * 2.5
                + (1.5 if memory.validation_status.lower() in {
                    "passed", "pass", "success", "green"
                } else 0.0)
                + max(0.0, 2.0 - rank * 0.02)
            )
            scored.append((score, memory))

        return [
            memory
            for _score, memory in sorted(
                scored,
                key=lambda item:(-item[0], -item[1].event_id),
            )[:bounded]
        ]

    def context(
        self,
        *,
        repository: str,
        project_id: str | None,
        query: str,
        limit: int = 6,
    ) -> dict[str, Any]:
        memories = self.recall(
            repository=repository,
            project_id=project_id,
            query=query,
            limit=limit,
        )
        items = []
        for memory in memories:
            item = {
                "generation":memory.generation,
                "task_id":memory.task_id,
                "kind":memory.kind,
            }
            for key, value in (
                ("summary", memory.summary),
                ("validation_status", memory.validation_status),
            ):
                if value:
                    item[key] = value
            for key, value in (
                ("commit_shas", memory.commit_shas),
                ("changed_files", memory.changed_files),
                ("decisions", memory.decisions),
                ("constraints", memory.constraints),
                ("facts", memory.facts),
                ("risks", memory.risks),
                ("next_steps", memory.next_steps),
            ):
                if value:
                    item[key] = list(value)
            items.append(item)
        return {
            "schema_version":"production-os/project-memory-context/v1",
            "repository":str(repository),
            "project_id":str(project_id or ""),
            "items":items,
        }

    @staticmethod
    def context_text(context: dict[str, Any], *, max_chars: int = 5000) -> str:
        items = context.get("items")
        if not isinstance(items, list) or not items:
            return "No durable project memory is available yet."
        lines = ["Relevant durable project memory:"]
        for item in items:
            if not isinstance(item, dict):
                continue
            prefix = (
                f"- generation {item.get('generation')}, "
                f"task {item.get('task_id')}:"
            )
            details = []
            if item.get("summary"):
                details.append(str(item["summary"]))
            for label in ("decisions", "constraints", "facts", "risks", "next_steps"):
                values = item.get(label)
                if isinstance(values, list) and values:
                    details.append(
                        f"{label}=" + "; ".join(str(v) for v in values[:4])
                    )
            line = prefix + " " + " | ".join(details)
            lines.append(line[:1400])
            if sum(len(value) + 1 for value in lines) >= max_chars:
                break
        return "\n".join(lines)[:max_chars]
