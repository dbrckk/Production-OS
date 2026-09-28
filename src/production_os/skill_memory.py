from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


SKILL_SCHEMA = "production-os/learned-skill/v1"
_TERM = re.compile(r"[a-z0-9][a-z0-9._-]{1,63}")


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
    uses: int
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
            "uses":self.uses,
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
                "SELECT successes,uses FROM learned_skills WHERE skill_id=?",
                (skill_id,),
            ).fetchone()
            if row is None:
                successes = 1
                uses = 0
                confidence = 0.8 if verified else 0.6
                _execute(
                    db,
                    self.backend,
                    """INSERT INTO learned_skills(
                        skill_id,repository,title,trigger_terms_json,
                        capabilities_json,procedure_json,successes,uses,
                        confidence,source_task,created_at,updated_at
                    ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (
                        skill_id, str(repository), title,
                        json.dumps(list(terms)),
                        json.dumps(list(caps)),
                        json.dumps(list(procedure), ensure_ascii=False),
                        successes, uses, confidence, str(task), now, now,
                    ),
                )
            else:
                successes = int(row["successes"]) + 1
                uses = int(row["uses"])
                confidence = min(
                    0.98,
                    round(0.6 + min(successes, 8) * 0.045 + (0.08 if verified else 0), 3),
                )
                _execute(
                    db,
                    self.backend,
                    """UPDATE learned_skills
                       SET successes=?,confidence=?,updated_at=?
                       WHERE skill_id=?""",
                    (successes, confidence, now, skill_id),
                )
        return LearnedSkill(
            skill_id=skill_id,
            repository=str(repository),
            title=title,
            trigger_terms=terms,
            capabilities=caps,
            procedure=procedure,
            successes=successes,
            uses=uses,
            confidence=confidence,
            source_task=str(task),
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
                   WHERE repository=? AND confidence>=?
                   ORDER BY confidence DESC,successes DESC,updated_at DESC
                   LIMIT 100""",
                (str(repository), float(min_confidence)),
            ).fetchall()

        scored: list[tuple[float, LearnedSkill]] = []
        for row in rows:
            terms = tuple(json.loads(row["trigger_terms_json"]))
            caps = tuple(json.loads(row["capabilities_json"]))
            procedure = tuple(json.loads(row["procedure_json"]))
            term_overlap = len(query_terms.intersection(terms))
            cap_overlap = len(query_caps.intersection(caps))
            if query_terms and term_overlap == 0 and query_caps and cap_overlap == 0:
                continue
            score = (
                float(row["confidence"]) * 10.0
                + term_overlap * 2.5
                + cap_overlap * 3.0
                + min(int(row["successes"]), 8) * 0.3
            )
            scored.append((
                score,
                LearnedSkill(
                    skill_id=str(row["skill_id"]),
                    repository=str(row["repository"]),
                    title=str(row["title"]),
                    trigger_terms=terms,
                    capabilities=caps,
                    procedure=procedure,
                    successes=int(row["successes"]),
                    uses=int(row["uses"]),
                    confidence=float(row["confidence"]),
                    source_task=str(row["source_task"]),
                ),
            ))
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
