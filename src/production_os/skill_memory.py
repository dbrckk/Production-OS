from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


SKILL_SCHEMA = "production-os/learned-skill/v1"
_TERM = re.compile(r"[a-z0-9][a-z0-9._-]{1,63}")
_SECRET_PATTERNS = (
    re.compile(r"(?i)\bbearer\s+[a-z0-9._~+/-]{12,}"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{16,}\b"),
    re.compile(r"(?i)\b(password|passwd|secret|token)\s*[=:]\s*\S{8,}"),
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _is_postgres(backend) -> bool:
    return backend.__class__.__name__.startswith("Postgres")


def _sql(backend, statement: str) -> str:
    return statement.replace("?", "%s") if _is_postgres(backend) else statement


def _execute(db, backend, statement: str, params: tuple = ()):
    return db.execute(_sql(backend, statement), params)


def _terms(value: str) -> tuple[str, ...]:
    rows = []
    for term in _TERM.findall(str(value or "").lower()):
        if len(term) < 3 or term in rows:
            continue
        rows.append(term)
    return tuple(rows[:32])


@dataclass(frozen=True, slots=True)
class LearnedSkill:
    skill_id: str
    repository: str
    title: str
    trigger_terms: tuple[str, ...]
    capabilities: tuple[str, ...]
    procedure: tuple[str, ...]
    successes: int
    verified_successes: int
    uses: int
    failed_uses: int
    confidence: float
    source_task: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version":SKILL_SCHEMA,
            "skill_id":self.skill_id,
            "repository":self.repository,
            "title":self.title,
            "trigger_terms":list(self.trigger_terms),
            "capabilities":list(self.capabilities),
            "procedure":list(self.procedure),
            "successes":self.successes,
            "verified_successes":self.verified_successes,
            "uses":self.uses,
            "failed_uses":self.failed_uses,
            "confidence":self.confidence,
            "source_task":self.source_task,
        }


class SkillStore:
    def __init__(self, backend):
        self.backend = backend

    @staticmethod
    def _validated_skill(
        repository: str,
        task: str,
        capabilities: list[str],
        payload: dict[str, Any],
    ) -> tuple[str, str, tuple[str, ...], tuple[str, ...], tuple[str, ...]]:
        if str(payload.get("schema_version") or "") != SKILL_SCHEMA:
            raise ValueError("unsupported learned skill schema")
        title = str(payload.get("title") or "").strip()
        if not title or len(title) > 160:
            raise ValueError("learned skill title is invalid")

        raw_procedure = payload.get("procedure")
        if not isinstance(raw_procedure, list) or not raw_procedure:
            raise ValueError("learned skill procedure is required")
        procedure = tuple(
            str(step or "").strip()
            for step in raw_procedure
            if str(step or "").strip()
        )
        if not procedure or len(procedure) > 12:
            raise ValueError("learned skill procedure must contain 1-12 steps")
        if any(len(step) > 1200 for step in procedure):
            raise ValueError("learned skill procedure step is too long")
        secret_scan = "\n".join((title, *procedure))
        if any(pattern.search(secret_scan) for pattern in _SECRET_PATTERNS):
            raise ValueError("learned skill must not contain credentials or secrets")

        raw_terms = payload.get("trigger_terms")
        if raw_terms is None:
            trigger_terms = _terms(task)
        elif isinstance(raw_terms, list):
            trigger_terms = tuple(dict.fromkeys(
                term
                for value in raw_terms
                for term in _terms(str(value))
            ))[:32]
        else:
            raise ValueError("learned skill trigger_terms must be a list")
        if not trigger_terms:
            raise ValueError("learned skill requires trigger terms")

        normalized_capabilities = tuple(sorted(set(
            str(value or "").strip().lower()
            for value in capabilities
            if str(value or "").strip()
        )))[:12]
        canonical = json.dumps({
            "repository":repository,
            "title":title.lower(),
            "trigger_terms":trigger_terms,
            "capabilities":normalized_capabilities,
            "procedure":procedure,
        }, ensure_ascii=False, sort_keys=True)
        skill_id = hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:32]
        return skill_id, title, trigger_terms, normalized_capabilities, procedure

    @staticmethod
    def _from_row(row) -> LearnedSkill:
        return LearnedSkill(
            skill_id=str(row["skill_id"]),
            repository=str(row["repository"]),
            title=str(row["title"]),
            trigger_terms=tuple(json.loads(row["trigger_terms_json"])),
            capabilities=tuple(json.loads(row["capabilities_json"])),
            procedure=tuple(json.loads(row["procedure_json"])),
            successes=int(row["successes"]),
            verified_successes=int(row["verified_successes"]),
            uses=int(row["uses"]),
            failed_uses=int(row["failed_uses"]),
            confidence=float(row["confidence"]),
            source_task=str(row["source_task"]),
        )

    def record_success(
        self,
        *,
        repository: str,
        task: str,
        capabilities: list[str],
        result: dict[str, Any],
    ) -> LearnedSkill | None:
        payload = result.get("learned_skill")
        if not isinstance(payload, dict):
            return None
        skill_id, title, terms, caps, procedure = self._validated_skill(
            str(repository),
            str(task),
            capabilities,
            payload,
        )
        validation = result.get("validation")
        verified = (
            isinstance(validation, dict)
            and str(validation.get("status") or "").lower()
            in {"passed", "pass", "success", "green"}
        )
        now = _now()
        with self.backend.transaction() as db:
            row = _execute(
                db,
                self.backend,
                """SELECT successes,verified_successes,uses,failed_uses,confidence
                   FROM learned_skills WHERE skill_id=?""",
                (skill_id,),
            ).fetchone()
            if row is None:
                successes = 1
                verified_successes = 1 if verified else 0
                uses = 0
                failed_uses = 0
                confidence = 0.8 if verified else 0.6
                _execute(
                    db,
                    self.backend,
                    """INSERT INTO learned_skills(
                        skill_id,repository,title,trigger_terms_json,
                        capabilities_json,procedure_json,successes,
                        verified_successes,uses,failed_uses,confidence,
                        source_task,created_at,updated_at,last_failure_at
                    ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,NULL)""",
                    (
                        skill_id, str(repository), title,
                        json.dumps(list(terms)),
                        json.dumps(list(caps)),
                        json.dumps(list(procedure), ensure_ascii=False),
                        successes, verified_successes, uses, failed_uses,
                        confidence, str(task), now, now,
                    ),
                )
            else:
                successes = int(row["successes"]) + 1
                verified_successes = (
                    int(row["verified_successes"]) + (1 if verified else 0)
                )
                uses = int(row["uses"])
                failed_uses = int(row["failed_uses"])
                previous_confidence = float(row["confidence"])
                if verified:
                    target = (
                        0.72
                        + min(verified_successes, 6) * 0.04
                        + min(successes, 8) * 0.01
                    )
                    confidence = min(
                        0.98,
                        round(max(previous_confidence + 0.04, target), 3),
                    )
                else:
                    target = 0.58 + min(successes, 8) * 0.02
                    confidence = min(
                        0.75,
                        round(max(previous_confidence, target), 3),
                    )
                _execute(
                    db,
                    self.backend,
                    """UPDATE learned_skills
                       SET successes=?,verified_successes=?,
                           confidence=?,updated_at=?
                       WHERE skill_id=?""",
                    (
                        successes, verified_successes,
                        confidence, now, skill_id,
                    ),
                )
        return LearnedSkill(
            skill_id=skill_id,
            repository=str(repository),
            title=title,
            trigger_terms=terms,
            capabilities=caps,
            procedure=procedure,
            successes=successes,
            verified_successes=verified_successes,
            uses=uses,
            failed_uses=failed_uses,
            confidence=confidence,
            source_task=str(task),
        )

    def record_use_outcome(
        self,
        skill_ids: list[str] | tuple[str, ...],
        *,
        succeeded: bool,
    ) -> None:
        ids = list(dict.fromkeys(
            str(value or "").strip()
            for value in skill_ids
            if str(value or "").strip()
        ))[:10]
        if not ids:
            return
        now = _now()
        with self.backend.transaction() as db:
            for skill_id in ids:
                row = _execute(
                    db,
                    self.backend,
                    """SELECT confidence,failed_uses,last_failure_at
                       FROM learned_skills WHERE skill_id=?""",
                    (skill_id,),
                ).fetchone()
                if row is None:
                    continue
                confidence = float(row["confidence"])
                failed_uses = int(row["failed_uses"])
                if succeeded:
                    confidence = min(0.98, round(confidence + 0.015, 3))
                    last_failure_at = row["last_failure_at"]
                else:
                    failed_uses += 1
                    confidence = max(0.2, round(confidence - 0.12, 3))
                    last_failure_at = now
                _execute(
                    db,
                    self.backend,
                    """UPDATE learned_skills
                       SET failed_uses=?,confidence=?,last_failure_at=?,
                           updated_at=?
                       WHERE skill_id=?""",
                    (
                        failed_uses, confidence, last_failure_at,
                        now, skill_id,
                    ),
                )
                self.backend.append_event(
                    db,
                    "skill-reuse-outcome",
                    {
                        "skill_id":skill_id,
                        "succeeded":bool(succeeded),
                        "confidence":confidence,
                        "failed_uses":failed_uses,
                    },
                )

    def select(
        self,
        *,
        repository: str,
        task: str,
        capabilities: list[str],
        limit: int = 3,
        min_confidence: float = 0.55,
    ) -> list[LearnedSkill]:
        query_repository = str(repository)
        query_terms = set(_terms(task))
        query_caps = {
            str(value or "").strip().lower()
            for value in capabilities
            if str(value or "").strip()
        }
        with self.backend.connect() as db:
            rows = _execute(
                db,
                self.backend,
                """SELECT * FROM learned_skills
                   WHERE confidence>=?
                   ORDER BY confidence DESC,verified_successes DESC,
                            successes DESC,updated_at DESC
                   LIMIT 300""",
                (float(min_confidence),),
            ).fetchall()

        scored: list[tuple[float, LearnedSkill]] = []
        for row in rows:
            terms = tuple(json.loads(row["trigger_terms_json"]))
            caps = tuple(json.loads(row["capabilities_json"]))
            term_overlap = len(query_terms.intersection(terms))
            cap_overlap = len(query_caps.intersection(caps))
            same_repo = str(row["repository"]) == query_repository

            if same_repo:
                if query_terms and term_overlap == 0 and query_caps and cap_overlap == 0:
                    continue
            else:
                if int(row["verified_successes"]) < 2:
                    continue
                if float(row["confidence"]) < 0.84:
                    continue
                if term_overlap < 2:
                    continue
                if query_caps and cap_overlap == 0:
                    continue
                if int(row["failed_uses"]) > int(row["verified_successes"]):
                    continue

            score = (
                float(row["confidence"]) * 10.0
                + term_overlap * 2.5
                + cap_overlap * 3.0
                + min(int(row["verified_successes"]), 8) * 0.45
                + min(int(row["successes"]), 8) * 0.15
                + (2.0 if same_repo else -1.5)
                - min(int(row["failed_uses"]), 5) * 1.2
            )
            scored.append((score, self._from_row(row)))

        selected = [
            skill
            for _score, skill in sorted(
                scored,
                key=lambda item:(-item[0], item[1].skill_id),
            )[:max(0, min(int(limit), 5))]
        ]
        if selected:
            now = _now()
            with self.backend.transaction() as db:
                for skill in selected:
                    _execute(
                        db,
                        self.backend,
                        """UPDATE learned_skills
                           SET uses=uses+1,updated_at=?
                           WHERE skill_id=?""",
                        (now, skill.skill_id),
                    )
        return selected
