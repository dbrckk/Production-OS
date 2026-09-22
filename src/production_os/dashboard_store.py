from __future__ import annotations

import json
import re
import uuid
from datetime import datetime, timezone

from .dashboard_security import redact_log_value


_TERMINAL_EXECUTION_STATES = {"succeeded", "failed", "cancelled"}
_LOG_LEVELS = {"debug", "info", "warning", "error", "critical"}
_COMMIT_SHA = re.compile(r"^[0-9a-f]{40}$")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _is_postgres(backend) -> bool:
    return backend.__class__.__name__ == "PostgresBackend"


def _sql(backend, statement: str) -> str:
    return statement.replace("?", "%s") if _is_postgres(backend) else statement


def _execute(db, backend, statement: str, params: tuple = ()):
    return db.execute(_sql(backend, statement), params)


def _json(value, default):
    if value in (None, ""):
        return default
    if isinstance(value, (dict, list)):
        return value
    try:
        parsed = json.loads(value)
    except (TypeError, ValueError, json.JSONDecodeError):
        return default
    return parsed


def _dump(value) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _non_negative_int(value) -> int:
    if isinstance(value, bool):
        return 0
    try:
        return max(0, int(value))
    except (TypeError, ValueError):
        return 0


def _optional_float(value):
    if value is None or isinstance(value, bool):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _bounded_progress(value):
    if value is None:
        return None
    value = float(value)
    if value < 0 or value > 100:
        raise ValueError("progress must be between 0 and 100")
    return value


def execution_id(job_key: str, attempt: int) -> str:
    return f"{job_key}:{max(1, int(attempt))}"


def _dedupe_commit_shas(result: dict) -> list[str]:
    commits = result.get("commits")
    if not isinstance(commits, dict):
        return []
    raw = commits.get("shas")
    if not isinstance(raw, list):
        return []
    found: list[str] = []
    seen: set[str] = set()
    for value in raw:
        sha = str(value or "").strip().lower()
        if not _COMMIT_SHA.fullmatch(sha) or sha in seen:
            continue
        seen.add(sha)
        found.append(sha)
    return found


def _normalize_provider_row(value: object) -> dict | None:
    if not isinstance(value, dict):
        return None
    provider = str(value.get("provider") or "").strip()
    model = str(value.get("model") or "").strip()
    if not provider or not model:
        return None
    return {
        "provider": provider,
        "model": model,
        "api_calls": _non_negative_int(value.get("api_calls", 1)),
        "input_tokens": _non_negative_int(value.get("input_tokens")),
        "cached_input_tokens": _non_negative_int(
            value.get("cached_input_tokens")
        ),
        "output_tokens": _non_negative_int(value.get("output_tokens")),
        "reasoning_tokens": _non_negative_int(
            value.get("reasoning_tokens")
        ),
        "total_tokens": _non_negative_int(value.get("total_tokens")),
        "estimated_cost_usd": _optional_float(
            value.get("estimated_cost_usd")
        ),
        "pricing_catalog_version": (
            str(value.get("pricing_catalog_version"))
            if value.get("pricing_catalog_version") is not None
            else None
        ),
    }


def _normalize_usage(result: dict) -> tuple[dict, list[dict]]:
    raw = result.get("usage")
    usage = dict(raw) if isinstance(raw, dict) else {}
    providers = []
    provider_rows = usage.get("providers")
    if isinstance(provider_rows, list):
        for value in provider_rows:
            row = _normalize_provider_row(value)
            if row is not None:
                providers.append(row)

    def counter(name: str) -> int:
        if name in usage:
            return _non_negative_int(usage.get(name))
        return sum(_non_negative_int(row.get(name)) for row in providers)

    normalized = {
        "api_calls": counter("api_calls"),
        "input_tokens": counter("input_tokens"),
        "cached_input_tokens": counter("cached_input_tokens"),
        "output_tokens": counter("output_tokens"),
        "reasoning_tokens": counter("reasoning_tokens"),
        "total_tokens": counter("total_tokens"),
    }
    costs = [row["estimated_cost_usd"] for row in providers]
    normalized["estimated_cost_usd"] = (
        sum(costs)
        if providers
        and all(value is not None for value in costs)
        else _optional_float(usage.get("estimated_cost_usd"))
    )
    versions = {
        row["pricing_catalog_version"]
        for row in providers
        if row["pricing_catalog_version"]
    }
    normalized["pricing_catalog_version"] = (
        next(iter(versions)) if len(versions) == 1 else None
    )
    return normalized, providers


class DashboardStore:
    def __init__(self, backend):
        self.backend = backend

    @staticmethod
    def _execution_dict(row) -> dict:
        value = dict(row)
        value["live_usage"] = _json(value.pop("live_usage_json", None), {})
        value["commit_shas"] = _json(
            value.pop("commit_shas_json", None),
            [],
        )
        value["result_summary"] = _json(
            value.pop("result_summary_json", None),
            {},
        )
        return value

    @staticmethod
    def _usage_dict(row) -> dict:
        return dict(row)

    @staticmethod
    def _log_dict(row) -> dict:
        value = dict(row)
        value["metadata"] = _json(value.pop("metadata_json", None), {})
        return value

    @staticmethod
    def _repository_snapshot_dict(row) -> dict:
        value = dict(row)
        value["snapshot"] = _json(value.pop("snapshot_json", None), {})
        return value

    @staticmethod
    def _progress_snapshot_dict(row) -> dict:
        value = dict(row)
        value["evidence"] = _json(value.pop("evidence_json", None), {})
        value["remaining_work"] = _json(
            value.pop("remaining_work_json", None),
            [],
        )
        value["blockers"] = _json(value.pop("blockers_json", None), [])
        return value

    def start_execution(
        self,
        job: dict,
        worker_id: str,
        *,
        started_at: str | None = None,
    ) -> dict:
        key = str(job.get("key") or "").strip()
        repository = str(job.get("repository") or "").strip()
        worker_id = str(worker_id or "").strip()
        if not key or not repository or not worker_id:
            raise ValueError("job key, repository, and worker_id are required")
        attempt = max(1, int(job.get("delivery_attempt") or 1))
        identifier = execution_id(key, attempt)
        payload = job.get("payload")
        payload = payload if isinstance(payload, dict) else {}
        started = started_at or _now()
        with self.backend.transaction() as db:
            _execute(
                db,
                self.backend,
                """
                INSERT INTO job_executions(
                    id, job_key, workflow_id, workflow_task_id,
                    repository, worker_id, attempt, status,
                    started_at, created_at
                )
                VALUES(?, ?, ?, ?, ?, ?, ?, 'running', ?, ?)
                ON CONFLICT(id) DO NOTHING
                """,
                (
                    identifier,
                    key,
                    payload.get("workflow_id"),
                    payload.get("workflow_task_id"),
                    repository,
                    worker_id,
                    attempt,
                    started,
                    started,
                ),
            )
            row = _execute(
                db,
                self.backend,
                "SELECT * FROM job_executions WHERE id=?",
                (identifier,),
            ).fetchone()
        return self._execution_dict(row)

    def execution_count(self, job_key: str) -> int:
        with self.backend.connect() as db:
            row = _execute(
                db,
                self.backend,
                "SELECT COUNT(*) AS count FROM job_executions WHERE job_key=?",
                (str(job_key),),
            ).fetchone()
        return int(row["count"])

    def latest_execution(self, job_key: str) -> dict | None:
        with self.backend.connect() as db:
            row = _execute(
                db,
                self.backend,
                """
                SELECT * FROM job_executions
                WHERE job_key=?
                ORDER BY attempt DESC, started_at DESC
                LIMIT 1
                """,
                (str(job_key),),
            ).fetchone()
        return self._execution_dict(row) if row is not None else None

    def _running_execution(self, db, job_key: str):
        return _execute(
            db,
            self.backend,
            """
            SELECT * FROM job_executions
            WHERE job_key=? AND status='running'
            ORDER BY attempt DESC, started_at DESC
            LIMIT 1
            """,
            (str(job_key),),
        ).fetchone()

    def update_live_execution(
        self,
        job_key: str,
        worker_id: str,
        telemetry: dict,
        *,
        at: str | None = None,
    ) -> dict:
        telemetry = telemetry if isinstance(telemetry, dict) else {}
        stage_value = telemetry.get("stage")
        stage = str(stage_value).strip() if stage_value is not None else None
        progress = _bounded_progress(telemetry.get("progress"))
        when = at or _now()
        with self.backend.transaction() as db:
            row = self._running_execution(db, job_key)
            if row is None:
                raise RuntimeError("running execution not found")
            if str(row["worker_id"]) != str(worker_id):
                raise RuntimeError("worker mismatch")
            old_stage = row["current_stage"]
            old_progress = row["progress_percent"]
            if (
                progress is not None
                and old_progress is not None
                and (stage or old_stage) == old_stage
                and progress < float(old_progress)
            ):
                raise ValueError("progress cannot move backward")
            existing_usage = _json(row["live_usage_json"], {})
            usage = telemetry.get("usage")
            live_usage = (
                dict(usage)
                if isinstance(usage, dict)
                else existing_usage
            )
            _execute(
                db,
                self.backend,
                """
                UPDATE job_executions
                SET current_stage=?,
                    progress_percent=?,
                    live_usage_json=?,
                    last_telemetry_at=?
                WHERE id=?
                """,
                (
                    stage if stage is not None else old_stage,
                    progress if progress is not None else old_progress,
                    _dump(live_usage),
                    when,
                    row["id"],
                ),
            )
            updated = _execute(
                db,
                self.backend,
                "SELECT * FROM job_executions WHERE id=?",
                (row["id"],),
            ).fetchone()
        return self._execution_dict(updated)

    def finish_execution(
        self,
        job_key: str,
        worker_id: str,
        *,
        status: str,
        duration_seconds: float | None,
        result: dict | None,
        error_type: str | None = None,
        error_message: str | None = None,
        finished_at: str | None = None,
    ) -> dict:
        status = str(status or "").strip()
        if status not in _TERMINAL_EXECUTION_STATES:
            raise ValueError("invalid terminal execution status")
        result = dict(result) if isinstance(result, dict) else {}
        when = finished_at or _now()
        with self.backend.transaction() as db:
            row = _execute(
                db,
                self.backend,
                """
                SELECT * FROM job_executions
                WHERE job_key=?
                ORDER BY attempt DESC, started_at DESC
                LIMIT 1
                """,
                (str(job_key),),
            ).fetchone()
            if row is None:
                raise RuntimeError("execution not found")
            if str(row["worker_id"]) != str(worker_id):
                raise RuntimeError("worker mismatch")
            if str(row["status"]) != "running":
                return self._execution_dict(row)

            usage, provider_rows = _normalize_usage(result)
            commit_shas = _dedupe_commit_shas(result)
            provider = (
                provider_rows[0]["provider"]
                if len(provider_rows) == 1
                else None
            )
            model = (
                provider_rows[0]["model"]
                if len(provider_rows) == 1
                else None
            )
            summary = redact_log_value(result)
            _execute(
                db,
                self.backend,
                """
                UPDATE job_executions
                SET status=?,
                    finished_at=?,
                    duration_seconds=?,
                    provider=?,
                    model=?,
                    api_calls=?,
                    input_tokens=?,
                    cached_input_tokens=?,
                    output_tokens=?,
                    reasoning_tokens=?,
                    total_tokens=?,
                    estimated_cost_usd=?,
                    pricing_catalog_version=?,
                    commit_count=?,
                    commit_shas_json=?,
                    error_type=?,
                    error_message=?,
                    result_summary_json=?
                WHERE id=? AND status='running'
                """,
                (
                    status,
                    when,
                    _optional_float(duration_seconds),
                    provider,
                    model,
                    usage["api_calls"],
                    usage["input_tokens"],
                    usage["cached_input_tokens"],
                    usage["output_tokens"],
                    usage["reasoning_tokens"],
                    usage["total_tokens"],
                    usage["estimated_cost_usd"],
                    usage["pricing_catalog_version"],
                    len(commit_shas),
                    _dump(commit_shas),
                    str(error_type) if error_type else None,
                    str(error_message) if error_message else None,
                    _dump(summary),
                    row["id"],
                ),
            )
            for index, provider_row in enumerate(provider_rows):
                event_id = f"{row['id']}:{index}"
                _execute(
                    db,
                    self.backend,
                    """
                    INSERT INTO api_usage_events(
                        id, execution_id, worker_id, repository,
                        provider, model, api_calls, input_tokens,
                        cached_input_tokens, output_tokens,
                        reasoning_tokens, total_tokens,
                        estimated_cost_usd, pricing_catalog_version,
                        occurred_at
                    )
                    VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(id) DO NOTHING
                    """,
                    (
                        event_id,
                        row["id"],
                        row["worker_id"],
                        row["repository"],
                        provider_row["provider"],
                        provider_row["model"],
                        provider_row["api_calls"],
                        provider_row["input_tokens"],
                        provider_row["cached_input_tokens"],
                        provider_row["output_tokens"],
                        provider_row["reasoning_tokens"],
                        provider_row["total_tokens"],
                        provider_row["estimated_cost_usd"],
                        provider_row["pricing_catalog_version"],
                        when,
                    ),
                )
            updated = _execute(
                db,
                self.backend,
                "SELECT * FROM job_executions WHERE id=?",
                (row["id"],),
            ).fetchone()
        return self._execution_dict(updated)

    def executions_for_worker(
        self,
        worker_id: str,
        *,
        limit: int = 100,
    ) -> list[dict]:
        limit = max(1, min(500, int(limit)))
        with self.backend.connect() as db:
            rows = _execute(
                db,
                self.backend,
                """
                SELECT * FROM job_executions
                WHERE worker_id=?
                ORDER BY started_at DESC, id DESC
                LIMIT ?
                """,
                (str(worker_id), limit),
            ).fetchall()
        return [self._execution_dict(row) for row in rows]

    def executions_for_repository(
        self,
        repository: str,
        *,
        limit: int = 100,
    ) -> list[dict]:
        limit = max(1, min(500, int(limit)))
        with self.backend.connect() as db:
            rows = _execute(
                db,
                self.backend,
                """
                SELECT * FROM job_executions
                WHERE repository=?
                ORDER BY started_at DESC, id DESC
                LIMIT ?
                """,
                (str(repository), limit),
            ).fetchall()
        return [self._execution_dict(row) for row in rows]

    def usage_events(
        self,
        *,
        worker_id: str | None = None,
        repository: str | None = None,
        since: str | None = None,
    ) -> list[dict]:
        clauses: list[str] = []
        params: list[object] = []
        if worker_id is not None:
            clauses.append("worker_id=?")
            params.append(str(worker_id))
        if repository is not None:
            clauses.append("repository=?")
            params.append(str(repository))
        if since is not None:
            clauses.append("occurred_at>=?")
            params.append(str(since))
        where = f" WHERE {' AND '.join(clauses)}" if clauses else ""
        with self.backend.connect() as db:
            rows = _execute(
                db,
                self.backend,
                (
                    "SELECT * FROM api_usage_events"
                    + where
                    + " ORDER BY occurred_at DESC, id DESC"
                ),
                tuple(params),
            ).fetchall()
        return [self._usage_dict(row) for row in rows]

    def append_logs(
        self,
        worker_id: str,
        rows: list[dict],
    ) -> list[dict]:
        inserted: list[dict] = []
        worker_id = str(worker_id)
        with self.backend.transaction() as db:
            for raw in rows:
                if not isinstance(raw, dict):
                    continue
                redacted = redact_log_value(raw)
                level = str(redacted.get("level") or "info").lower()
                if level not in _LOG_LEVELS:
                    level = "info"
                identifier = str(
                    redacted.get("id") or uuid.uuid4().hex
                )
                created_at = str(redacted.get("created_at") or _now())
                metadata = redacted.get("metadata")
                metadata = metadata if isinstance(metadata, dict) else {}
                message = str(redacted.get("message") or "")
                _execute(
                    db,
                    self.backend,
                    """
                    INSERT INTO worker_log_events(
                        id, worker_id, repository, workflow_id,
                        job_key, level, stage, message, provider,
                        model, metadata_json, created_at
                    )
                    VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(id) DO NOTHING
                    """,
                    (
                        identifier,
                        worker_id,
                        redacted.get("repository"),
                        redacted.get("workflow_id"),
                        redacted.get("job_key"),
                        level,
                        redacted.get("stage"),
                        message,
                        redacted.get("provider"),
                        redacted.get("model"),
                        _dump(metadata),
                        created_at,
                    ),
                )
                row = _execute(
                    db,
                    self.backend,
                    "SELECT * FROM worker_log_events WHERE id=?",
                    (identifier,),
                ).fetchone()
                if row is not None:
                    inserted.append(self._log_dict(row))
        return inserted

    def logs_for_worker(
        self,
        worker_id: str,
        *,
        after: str | None = None,
        limit: int = 100,
    ) -> list[dict]:
        limit = max(1, min(500, int(limit)))
        params: list[object] = [str(worker_id)]
        cursor_clause = ""
        with self.backend.connect() as db:
            if after is not None:
                cursor = _execute(
                    db,
                    self.backend,
                    """
                    SELECT id, created_at FROM worker_log_events
                    WHERE worker_id=? AND id=?
                    """,
                    (str(worker_id), str(after)),
                ).fetchone()
                if cursor is None:
                    raise ValueError("invalid log cursor")
                cursor_clause = (
                    " AND (created_at < ? OR "
                    "(created_at = ? AND id < ?))"
                )
                params.extend(
                    [
                        cursor["created_at"],
                        cursor["created_at"],
                        cursor["id"],
                    ]
                )
            params.append(limit)
            rows = _execute(
                db,
                self.backend,
                (
                    "SELECT * FROM worker_log_events "
                    "WHERE worker_id=?"
                    + cursor_clause
                    + " ORDER BY created_at DESC, id DESC LIMIT ?"
                ),
                tuple(params),
            ).fetchall()
        return [self._log_dict(row) for row in rows]

    def save_repository_snapshot(self, snapshot: dict) -> dict:
        snapshot = dict(snapshot)
        identifier = str(snapshot.get("id") or uuid.uuid4().hex)
        captured_at = str(snapshot.get("captured_at") or _now())
        raw_snapshot = snapshot.get("snapshot")
        raw_snapshot = raw_snapshot if isinstance(raw_snapshot, dict) else {}
        with self.backend.transaction() as db:
            _execute(
                db,
                self.backend,
                """
                INSERT INTO project_repository_snapshots(
                    id, repository, default_branch,
                    production_os_commits, github_commits,
                    open_issues, open_pull_requests, ci_status,
                    latest_commit_sha, latest_release,
                    tests_detected, tests_passing, tests_failing,
                    snapshot_json, captured_at
                )
                VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO NOTHING
                """,
                (
                    identifier,
                    str(snapshot["repository"]),
                    snapshot.get("default_branch"),
                    _non_negative_int(
                        snapshot.get("production_os_commits")
                    ),
                    snapshot.get("github_commits"),
                    snapshot.get("open_issues"),
                    snapshot.get("open_pull_requests"),
                    snapshot.get("ci_status"),
                    snapshot.get("latest_commit_sha"),
                    snapshot.get("latest_release"),
                    snapshot.get("tests_detected"),
                    snapshot.get("tests_passing"),
                    snapshot.get("tests_failing"),
                    _dump(raw_snapshot),
                    captured_at,
                ),
            )
            row = _execute(
                db,
                self.backend,
                "SELECT * FROM project_repository_snapshots WHERE id=?",
                (identifier,),
            ).fetchone()
        return self._repository_snapshot_dict(row)

    def latest_repository_snapshot(
        self,
        repository: str,
    ) -> dict | None:
        with self.backend.connect() as db:
            row = _execute(
                db,
                self.backend,
                """
                SELECT * FROM project_repository_snapshots
                WHERE repository=?
                ORDER BY captured_at DESC, id DESC
                LIMIT 1
                """,
                (str(repository),),
            ).fetchone()
        return (
            self._repository_snapshot_dict(row)
            if row is not None
            else None
        )

    def save_progress_snapshot(self, snapshot: dict) -> dict:
        snapshot = dict(snapshot)
        identifier = str(snapshot.get("id") or uuid.uuid4().hex)
        captured_at = str(snapshot.get("captured_at") or _now())
        with self.backend.transaction() as db:
            _execute(
                db,
                self.backend,
                """
                INSERT INTO project_progress_snapshots(
                    id, repository, current_workflow_id,
                    production_progress, project_progress, confidence,
                    code_score, ui_ux_score, assets_score, tests_score,
                    stability_score, release_score, evidence_json,
                    remaining_work_json, blockers_json,
                    calculation_version, captured_at
                )
                VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO NOTHING
                """,
                (
                    identifier,
                    str(snapshot["repository"]),
                    snapshot.get("current_workflow_id"),
                    snapshot.get("production_progress"),
                    snapshot.get("project_progress"),
                    str(snapshot.get("confidence") or "low"),
                    snapshot.get("code_score"),
                    snapshot.get("ui_ux_score"),
                    snapshot.get("assets_score"),
                    snapshot.get("tests_score"),
                    snapshot.get("stability_score"),
                    snapshot.get("release_score"),
                    _dump(snapshot.get("evidence") or {}),
                    _dump(snapshot.get("remaining_work") or []),
                    _dump(snapshot.get("blockers") or []),
                    str(snapshot["calculation_version"]),
                    captured_at,
                ),
            )
            row = _execute(
                db,
                self.backend,
                "SELECT * FROM project_progress_snapshots WHERE id=?",
                (identifier,),
            ).fetchone()
        return self._progress_snapshot_dict(row)

    def latest_progress_snapshot(
        self,
        repository: str,
    ) -> dict | None:
        history = self.progress_history(repository, limit=1)
        return history[0] if history else None

    def progress_history(
        self,
        repository: str,
        *,
        limit: int = 100,
    ) -> list[dict]:
        limit = max(1, min(500, int(limit)))
        with self.backend.connect() as db:
            rows = _execute(
                db,
                self.backend,
                """
                SELECT * FROM project_progress_snapshots
                WHERE repository=?
                ORDER BY captured_at DESC, id DESC
                LIMIT ?
                """,
                (str(repository), limit),
            ).fetchall()
        return [self._progress_snapshot_dict(row) for row in rows]

    def save_provider_quota_snapshot(self, snapshot: dict) -> dict:
        snapshot = dict(snapshot)
        identifier = str(snapshot.get("id") or uuid.uuid4().hex)
        captured_at = str(snapshot.get("captured_at") or _now())
        with self.backend.transaction() as db:
            _execute(
                db,
                self.backend,
                """
                INSERT INTO provider_quota_snapshots(
                    id, provider, quota_type, used_value,
                    limit_value, remaining_value, unit,
                    source_status, captured_at
                )
                VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO NOTHING
                """,
                (
                    identifier,
                    str(snapshot["provider"]),
                    snapshot.get("quota_type"),
                    snapshot.get("used_value"),
                    snapshot.get("limit_value"),
                    snapshot.get("remaining_value"),
                    snapshot.get("unit"),
                    str(snapshot.get("source_status") or "unavailable"),
                    captured_at,
                ),
            )
            row = _execute(
                db,
                self.backend,
                "SELECT * FROM provider_quota_snapshots WHERE id=?",
                (identifier,),
            ).fetchone()
        return dict(row)

    def latest_provider_quota_snapshots(self) -> list[dict]:
        with self.backend.connect() as db:
            rows = _execute(
                db,
                self.backend,
                """
                SELECT q.*
                FROM provider_quota_snapshots q
                WHERE NOT EXISTS (
                    SELECT 1
                    FROM provider_quota_snapshots newer
                    WHERE newer.provider=q.provider
                      AND (
                        newer.captured_at > q.captured_at
                        OR (
                            newer.captured_at = q.captured_at
                            AND newer.id > q.id
                        )
                      )
                )
                ORDER BY q.provider ASC
                """,
            ).fetchall()
        return [dict(row) for row in rows]
