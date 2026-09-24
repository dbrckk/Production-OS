from __future__ import annotations

import json
from datetime import datetime, timezone
from uuid import uuid4

from .dashboard_security import redact_log_value


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _is_postgres(backend) -> bool:
    return backend.__class__.__name__ == "PostgresBackend"


def _sql(backend, statement: str) -> str:
    return statement.replace("?", "%s") if _is_postgres(backend) else statement


def _execute(db, backend, statement: str, params: tuple = ()):
    if _is_postgres(backend):
        cursor = db.cursor()
        cursor.execute(_sql(backend, statement), params)
        return cursor
    return db.execute(statement, params)


def execution_id(job_key: str, attempt: int) -> str:
    return f"{job_key}:{max(1, int(attempt))}"


def _bounded_progress(value):
    if value is None:
        return None
    value = float(value)
    if value < 0 or value > 100:
        raise ValueError("progress must be between 0 and 100")
    return value


def _valid_commit_shas(values) -> list[str]:
    shas = []
    seen = set()
    for value in values or []:
        if not isinstance(value, str):
            continue
        sha = value.strip().lower()
        if len(sha) != 40 or any(ch not in "0123456789abcdef" for ch in sha) or sha in seen:
            continue
        seen.add(sha)
        shas.append(sha)
    return shas


def _decode(row) -> dict | None:
    if row is None:
        return None
    value = dict(row)
    for key, target in (
        ("live_usage_json", "live_usage"),
        ("commit_shas_json", "commit_shas"),
        ("result_summary_json", "result_summary"),
        ("metadata_json", "metadata"),
        ("snapshot_json", "snapshot"),
        ("evidence_json", "evidence"),
        ("remaining_work_json", "remaining_work"),
        ("blockers_json", "blockers"),
    ):
        if key in value:
            try:
                value[target] = json.loads(value[key] or ("[]" if target in {"commit_shas", "remaining_work", "blockers"} else "{}"))
            except (TypeError, json.JSONDecodeError):
                value[target] = None
    if "project_progress" in value:
        evidence = value.get("evidence") or {}
        value["profile"] = evidence.get("profile") or "generic"
    return value


class DashboardStore:
    def __init__(self, backend):
        self.backend = backend

    def _fetchone(self, db, statement, params=()):
        cur = _execute(db, self.backend, statement, tuple(params))
        return _decode(cur.fetchone())

    def _fetchall(self, db, statement, params=()):
        cur = _execute(db, self.backend, statement, tuple(params))
        return [_decode(row) for row in cur.fetchall()]

    def start_execution(self, job: dict, worker_id: str, *, started_at: str | None = None) -> dict:
        attempt = max(1, int(job.get("delivery_attempt") or 1))
        ident = execution_id(job["key"], attempt)
        payload = job.get("payload") or {}
        at = started_at or _now()
        with self.backend.transaction() as db:
            _execute(db, self.backend, """INSERT INTO job_executions(
                    id, job_key, workflow_id, workflow_task_id, repository, worker_id,
                    attempt, status, started_at, created_at
                ) VALUES(?,?,?,?,?,?,?,?,?,?) ON CONFLICT(id) DO NOTHING""",
                (ident, job["key"], payload.get("workflow_id"), payload.get("workflow_task_id"), job["repository"], worker_id, attempt, "running", at, at))
            row = self._fetchone(db, "SELECT * FROM job_executions WHERE id=?", (ident,))
        return row

    def execution_count(self, job_key: str) -> int:
        with self.backend.connect() as db:
            cur = _execute(db, self.backend, "SELECT COUNT(*) AS n FROM job_executions WHERE job_key=?", (job_key,))
            row = cur.fetchone()
        return int(row["n"])

    def latest_execution(self, job_key: str) -> dict | None:
        with self.backend.connect() as db:
            return self._fetchone(db, "SELECT * FROM job_executions WHERE job_key=? ORDER BY attempt DESC LIMIT 1", (job_key,))

    def update_live_execution(self, job_key: str, worker_id: str, telemetry: dict, *, at: str | None = None) -> dict:
        progress = _bounded_progress(telemetry.get("progress")); usage = telemetry.get("usage")
        with self.backend.transaction() as db:
            row = self._fetchone(db, "SELECT * FROM job_executions WHERE job_key=? ORDER BY attempt DESC LIMIT 1", (job_key,))
            if row is None or row["status"] != "running": raise KeyError("running execution not found")
            if row["worker_id"] != worker_id: raise PermissionError("execution belongs to another worker")
            old = row.get("progress_percent"); stage = telemetry.get("stage", row.get("current_stage"))
            if progress is not None and old is not None and progress < float(old) and stage == row.get("current_stage"):
                raise ValueError("progress must not move backward within a stage")
            live_usage = usage if usage is not None else (row.get("live_usage") or {})
            _execute(db, self.backend, "UPDATE job_executions SET current_stage=?, progress_percent=?, live_usage_json=?, last_telemetry_at=? WHERE id=?",
                     (stage, progress if progress is not None else old, json.dumps(live_usage, sort_keys=True), at or _now(), row["id"]))
            return self._fetchone(db, "SELECT * FROM job_executions WHERE id=?", (row["id"],))

    def finish_execution(self, job_key: str, worker_id: str, *, status: str, duration_seconds: float | None, result: dict | None,
                         error_type: str | None = None, error_message: str | None = None, finished_at: str | None = None) -> dict:
        result = result or {}; usage = result.get("usage") or {}; commits = result.get("commits") or {}; shas = _valid_commit_shas(commits.get("shas"))
        with self.backend.transaction() as db:
            row = self._fetchone(db, "SELECT * FROM job_executions WHERE job_key=? ORDER BY attempt DESC LIMIT 1", (job_key,))
            if row is None: raise KeyError("execution not found")
            if row["worker_id"] != worker_id: raise PermissionError("execution belongs to another worker")
            if row["status"] != "running": return row
            _execute(db, self.backend, """UPDATE job_executions SET status=?, finished_at=?, duration_seconds=?, api_calls=?, input_tokens=?, cached_input_tokens=?, output_tokens=?, reasoning_tokens=?, total_tokens=?, commit_count=?, commit_shas_json=?, error_type=?, error_message=?, result_summary_json=? WHERE id=?""",
                     (status, finished_at or _now(), duration_seconds, int(usage.get("api_calls") or 0), int(usage.get("input_tokens") or 0), int(usage.get("cached_input_tokens") or 0), int(usage.get("output_tokens") or 0), int(usage.get("reasoning_tokens") or 0), int(usage.get("total_tokens") or 0), len(shas), json.dumps(shas), error_type, error_message, json.dumps(result, sort_keys=True), row["id"]))
            for index, item in enumerate(usage.get("providers") or []):
                _execute(db, self.backend, """INSERT INTO api_usage_events(id, execution_id, worker_id, repository, provider, model, api_calls, input_tokens, cached_input_tokens, output_tokens, reasoning_tokens, total_tokens, estimated_cost_usd, pricing_catalog_version, occurred_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(id) DO NOTHING""",
                         (f"{row['id']}:{index}", row["id"], worker_id, row["repository"], item.get("provider"), item.get("model"), int(item.get("api_calls") or 0), int(item.get("input_tokens") or 0), int(item.get("cached_input_tokens") or 0), int(item.get("output_tokens") or 0), int(item.get("reasoning_tokens") or 0), int(item.get("total_tokens") or 0), item.get("estimated_cost_usd"), item.get("pricing_catalog_version"), finished_at or _now()))
            return self._fetchone(db, "SELECT * FROM job_executions WHERE id=?", (row["id"],))

    def upsert_dashboard_incident(
        self,
        *,
        code: str,
        severity: str,
        title: str,
        message: str,
        target_type: str,
        target_id: str,
        at: str | None = None,
    ) -> dict:
        timestamp = at or _now()
        dedupe_key = f"{code}:{target_type}:{target_id}"
        ident = uuid4().hex
        with self.backend.transaction() as db:
            _execute(
                db,
                self.backend,
                """INSERT INTO dashboard_incidents(
                    id, dedupe_key, code, severity, title, message,
                    target_type, target_id, status, occurrence_count,
                    first_seen_at, last_seen_at
                ) VALUES(?,?,?,?,?,?,?,?,'open',1,?,?)
                ON CONFLICT(dedupe_key) DO UPDATE SET
                    severity=excluded.severity,
                    title=excluded.title,
                    message=excluded.message,
                    occurrence_count=CASE
                        WHEN dashboard_incidents.message<>excluded.message
                          OR dashboard_incidents.status='resolved'
                        THEN dashboard_incidents.occurrence_count+1
                        ELSE dashboard_incidents.occurrence_count
                    END,
                    last_seen_at=excluded.last_seen_at,
                    status=CASE
                        WHEN dashboard_incidents.status='resolved'
                        THEN 'open'
                        ELSE dashboard_incidents.status
                    END,
                    acknowledged_by=CASE
                        WHEN dashboard_incidents.status='resolved'
                        THEN NULL
                        ELSE dashboard_incidents.acknowledged_by
                    END,
                    acknowledged_at=CASE
                        WHEN dashboard_incidents.status='resolved'
                        THEN NULL
                        ELSE dashboard_incidents.acknowledged_at
                    END,
                    resolved_at=NULL""",
                (
                    ident,
                    dedupe_key,
                    code,
                    severity,
                    title,
                    message,
                    target_type,
                    target_id,
                    timestamp,
                    timestamp,
                ),
            )
            return self._fetchone(
                db,
                "SELECT * FROM dashboard_incidents WHERE dedupe_key=?",
                (dedupe_key,),
            )

    def dashboard_incidents(
        self,
        *,
        limit: int = 100,
        status: str | None = None,
    ) -> list[dict]:
        bounded = max(1, min(500, int(limit)))
        with self.backend.connect() as db:
            if status is None:
                return self._fetchall(
                    db,
                    """SELECT * FROM dashboard_incidents
                       ORDER BY last_seen_at DESC, id DESC
                       LIMIT ?""",
                    (bounded,),
                )
            return self._fetchall(
                db,
                """SELECT * FROM dashboard_incidents
                   WHERE status=?
                   ORDER BY last_seen_at DESC, id DESC
                   LIMIT ?""",
                (status, bounded),
            )

    def resolve_dashboard_incidents_except(
        self,
        active_dedupe_keys: set[str],
        *,
        at: str | None = None,
    ) -> list[dict]:
        timestamp = at or _now()
        with self.backend.transaction() as db:
            rows = self._fetchall(
                db,
                """SELECT * FROM dashboard_incidents
                   WHERE status IN ('open','acknowledged')""",
            )
            resolved = []
            for row in rows:
                if row["dedupe_key"] in active_dedupe_keys:
                    continue
                _execute(
                    db,
                    self.backend,
                    """UPDATE dashboard_incidents
                       SET status='resolved', resolved_at=?
                       WHERE id=?""",
                    (timestamp, row["id"]),
                )
                resolved.append(
                    self._fetchone(
                        db,
                        "SELECT * FROM dashboard_incidents WHERE id=?",
                        (row["id"],),
                    )
                )
            return resolved

    def acknowledge_dashboard_incident(
        self,
        incident_id: str,
        *,
        acknowledged_by: str,
        at: str | None = None,
    ) -> dict:
        timestamp = at or _now()
        with self.backend.transaction() as db:
            row = self._fetchone(
                db,
                "SELECT * FROM dashboard_incidents WHERE id=?",
                (incident_id,),
            )
            if row is None:
                raise KeyError(incident_id)
            if row["status"] == "resolved":
                raise RuntimeError("resolved incident cannot be acknowledged")
            _execute(
                db,
                self.backend,
                """UPDATE dashboard_incidents
                   SET status='acknowledged',
                       acknowledged_by=?,
                       acknowledged_at=?
                   WHERE id=?""",
                (acknowledged_by, timestamp, incident_id),
            )
            return self._fetchone(
                db,
                "SELECT * FROM dashboard_incidents WHERE id=?",
                (incident_id,),
            )

    def append_control_audit(
        self,
        *,
        action: str,
        worker_id: str,
        requested_by: str,
        outcome: str,
        job_key: str | None = None,
        error_code: str | None = None,
        at: str | None = None,
    ) -> dict:
        ident = uuid4().hex
        timestamp = at or _now()
        with self.backend.transaction() as db:
            _execute(
                db,
                self.backend,
                """INSERT INTO control_audit_events(
                    id, action, worker_id, job_key, requested_by,
                    outcome, error_code, requested_at
                ) VALUES(?,?,?,?,?,?,?,?)""",
                (
                    ident,
                    action,
                    worker_id,
                    job_key,
                    requested_by,
                    outcome,
                    error_code,
                    timestamp,
                ),
            )
            return self._fetchone(
                db,
                "SELECT * FROM control_audit_events WHERE id=?",
                (ident,),
            )

    def update_control_audit(
        self,
        event_id: str,
        *,
        outcome: str,
        error_code: str | None = None,
    ) -> dict:
        with self.backend.transaction() as db:
            _execute(
                db,
                self.backend,
                """UPDATE control_audit_events
                   SET outcome=?, error_code=?
                   WHERE id=?""",
                (outcome, error_code, event_id),
            )
            row = self._fetchone(
                db,
                "SELECT * FROM control_audit_events WHERE id=?",
                (event_id,),
            )
            if row is None:
                raise KeyError(event_id)
            return row

    def control_audit_events(self, *, limit: int = 100) -> list[dict]:
        bounded = max(1, min(500, int(limit)))
        with self.backend.connect() as db:
            return self._fetchall(
                db,
                """SELECT * FROM control_audit_events
                   ORDER BY requested_at DESC, id DESC
                   LIMIT ?""",
                (bounded,),
            )

    def get_worker_control(self, worker_id: str) -> dict | None:
        with self.backend.connect() as db:
            return self._fetchone(
                db,
                "SELECT * FROM worker_control_state WHERE worker_id=?",
                (worker_id,),
            )

    def set_worker_control(
        self,
        worker_id: str,
        desired_state: str,
        *,
        requested_by: str,
        reason: str | None = None,
        at: str | None = None,
    ) -> dict:
        timestamp = at or _now()
        with self.backend.transaction() as db:
            _execute(
                db,
                self.backend,
                """INSERT INTO worker_control_state(
                    worker_id, desired_state, reason, requested_by, requested_at, updated_at
                ) VALUES(?,?,?,?,?,?)
                ON CONFLICT(worker_id) DO UPDATE SET
                    desired_state=excluded.desired_state,
                    reason=excluded.reason,
                    requested_by=excluded.requested_by,
                    requested_at=excluded.requested_at,
                    updated_at=excluded.updated_at""",
                (worker_id, desired_state, reason, requested_by, timestamp, timestamp),
            )
            return self._fetchone(
                db,
                "SELECT * FROM worker_control_state WHERE worker_id=?",
                (worker_id,),
            )

    def acknowledge_worker_control(
        self,
        worker_id: str,
        desired_state: str,
        *,
        at: str | None = None,
    ) -> dict:
        timestamp = at or _now()
        with self.backend.transaction() as db:
            row = self._fetchone(
                db,
                "SELECT * FROM worker_control_state WHERE worker_id=?",
                (worker_id,),
            )
            if row is None:
                raise KeyError("worker control state not found")
            if row.get("desired_state") != desired_state:
                raise ValueError("stale worker desired state")
            _execute(
                db,
                self.backend,
                "UPDATE worker_control_state SET updated_at=? WHERE worker_id=?",
                (timestamp, worker_id),
            )
            return self._fetchone(
                db,
                "SELECT * FROM worker_control_state WHERE worker_id=?",
                (worker_id,),
            )

    def get_job_control(self, job_key: str) -> dict | None:
        with self.backend.connect() as db:
            return self._fetchone(
                db,
                "SELECT * FROM job_control_state WHERE job_key=?",
                (job_key,),
            )

    def set_job_control(
        self,
        job_key: str,
        desired_state: str,
        *,
        requested_by: str,
        reason: str | None = None,
        at: str | None = None,
    ) -> dict:
        timestamp = at or _now()
        with self.backend.transaction() as db:
            _execute(
                db,
                self.backend,
                """INSERT INTO job_control_state(
                    job_key, desired_state, reason, requested_by, requested_at,
                    acknowledged_at, updated_at
                ) VALUES(?,?,?,?,?,NULL,?)
                ON CONFLICT(job_key) DO UPDATE SET
                    desired_state=excluded.desired_state,
                    reason=excluded.reason,
                    requested_by=excluded.requested_by,
                    requested_at=excluded.requested_at,
                    acknowledged_at=NULL,
                    updated_at=excluded.updated_at""",
                (job_key, desired_state, reason, requested_by, timestamp, timestamp),
            )
            return self._fetchone(
                db,
                "SELECT * FROM job_control_state WHERE job_key=?",
                (job_key,),
            )

    def acknowledge_job_control(
        self,
        job_key: str,
        *,
        at: str | None = None,
    ) -> dict:
        timestamp = at or _now()
        with self.backend.transaction() as db:
            row = self._fetchone(
                db,
                "SELECT * FROM job_control_state WHERE job_key=?",
                (job_key,),
            )
            if row is None:
                raise KeyError("job control state not found")
            _execute(
                db,
                self.backend,
                """UPDATE job_control_state
                   SET acknowledged_at=?, updated_at=?
                   WHERE job_key=?""",
                (timestamp, timestamp, job_key),
            )
            return self._fetchone(
                db,
                "SELECT * FROM job_control_state WHERE job_key=?",
                (job_key,),
            )

    def executions_for_worker(self, worker_id: str, *, limit: int = 100) -> list[dict]:
        with self.backend.connect() as db: return self._fetchall(db, "SELECT * FROM job_executions WHERE worker_id=? ORDER BY started_at DESC LIMIT ?", (worker_id, max(1,min(limit,500))))

    def executions_for_repository(self, repository: str, *, limit: int = 100) -> list[dict]:
        with self.backend.connect() as db: return self._fetchall(db, "SELECT * FROM job_executions WHERE repository=? ORDER BY started_at DESC LIMIT ?", (repository, max(1,min(limit,500))))

    def usage_events(self, *, worker_id=None, repository=None, since=None) -> list[dict]:
        clauses, params = [], []
        for column, value in (("worker_id", worker_id), ("repository", repository)):
            if value is not None: clauses.append(f"{column}=?"); params.append(value)
        if since is not None: clauses.append("occurred_at>=?"); params.append(since)
        where = (" WHERE " + " AND ".join(clauses)) if clauses else ""
        with self.backend.connect() as db: return self._fetchall(db, "SELECT * FROM api_usage_events" + where + " ORDER BY occurred_at DESC", params)

    def append_logs(self, worker_id: str, rows: list[dict]) -> list[dict]:
        saved=[]
        with self.backend.transaction() as db:
            for source in rows:
                row=redact_log_value(source); ident=str(row.get("id") or uuid4()); created=row.get("created_at") or _now()
                _execute(db,self.backend,"""INSERT INTO worker_log_events(id,worker_id,repository,workflow_id,job_key,level,stage,message,provider,model,metadata_json,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(id) DO NOTHING""",
                         (ident,worker_id,row.get("repository"),row.get("workflow_id"),row.get("job_key"),row.get("level") or "info",row.get("stage"),str(row.get("message") or ""),row.get("provider"),row.get("model"),json.dumps(row.get("metadata") or {},sort_keys=True),created))
                saved.append(self._fetchone(db,"SELECT * FROM worker_log_events WHERE id=?",(ident,)))
        return saved

    def logs_for_worker(self, worker_id: str, *, after: str | None = None, limit: int = 100) -> list[dict]:
        limit=max(1,min(int(limit),500))
        with self.backend.connect() as db:
            if after is None: return self._fetchall(db,"SELECT * FROM worker_log_events WHERE worker_id=? ORDER BY created_at DESC, id DESC LIMIT ?",(worker_id,limit))
            cursor=self._fetchone(db,"SELECT * FROM worker_log_events WHERE id=? AND worker_id=?",(after,worker_id))
            if cursor is None: raise ValueError("invalid log cursor")
            return self._fetchall(db,"""SELECT * FROM worker_log_events WHERE worker_id=? AND (created_at < ? OR (created_at = ? AND id < ?)) ORDER BY created_at DESC, id DESC LIMIT ?""",(worker_id,cursor["created_at"],cursor["created_at"],after,limit))

    def _save_snapshot(self, table: str, snapshot: dict, json_fields: tuple[str, ...]) -> dict:
        allowed={
            "project_repository_snapshots":("id","repository","default_branch","production_os_commits","github_commits","open_issues","open_pull_requests","ci_status","latest_commit_sha","latest_release","tests_detected","tests_passing","tests_failing","snapshot_json","captured_at"),
            "project_progress_snapshots":("id","repository","current_workflow_id","production_progress","project_progress","confidence","code_score","ui_ux_score","assets_score","tests_score","stability_score","release_score","evidence_json","remaining_work_json","blockers_json","calculation_version","captured_at"),
            "provider_quota_snapshots":("id","provider","quota_type","used_value","limit_value","remaining_value","unit","source_status","captured_at"),
        }[table]
        values=dict(snapshot)
        for field in json_fields: values[field]=json.dumps(values.get(field) or ([] if field in {"remaining_work_json","blockers_json"} else {}),sort_keys=True)
        cols=[x for x in allowed if x in values]
        with self.backend.transaction() as db:
            _execute(db,self.backend,f"INSERT INTO {table}({','.join(cols)}) VALUES({','.join('?' for _ in cols)}) ON CONFLICT(id) DO NOTHING",tuple(values[x] for x in cols))
            return self._fetchone(db,f"SELECT * FROM {table} WHERE id=?",(values["id"],))

    def save_repository_snapshot(self, snapshot: dict) -> dict: return self._save_snapshot("project_repository_snapshots",snapshot,("snapshot_json",))
    def latest_repository_snapshot(self, repository: str) -> dict | None:
        with self.backend.connect() as db: return self._fetchone(db,"SELECT * FROM project_repository_snapshots WHERE repository=? ORDER BY captured_at DESC, id DESC LIMIT 1",(repository,))
    def save_progress_snapshot(self, snapshot: dict) -> dict: return self._save_snapshot("project_progress_snapshots",snapshot,("evidence_json","remaining_work_json","blockers_json"))
    def latest_progress_snapshot(self, repository: str) -> dict | None:
        with self.backend.connect() as db: return self._fetchone(db,"SELECT * FROM project_progress_snapshots WHERE repository=? ORDER BY captured_at DESC, id DESC LIMIT 1",(repository,))
    def progress_history(self, repository: str, *, limit: int = 100) -> list[dict]:
        with self.backend.connect() as db: return self._fetchall(db,"SELECT * FROM project_progress_snapshots WHERE repository=? ORDER BY captured_at DESC, id DESC LIMIT ?",(repository,max(1,min(limit,500))))
    def save_provider_quota_snapshot(self, snapshot: dict) -> dict: return self._save_snapshot("provider_quota_snapshots",snapshot,())
    def latest_provider_quota_snapshots(self) -> list[dict]:
        with self.backend.connect() as db: return self._fetchall(db,"""SELECT q.* FROM provider_quota_snapshots q JOIN (SELECT provider, MAX(captured_at) captured_at FROM provider_quota_snapshots GROUP BY provider) latest ON latest.provider=q.provider AND latest.captured_at=q.captured_at ORDER BY q.provider""")
