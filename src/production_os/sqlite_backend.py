from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from dataclasses import asdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterator

from .claims import ClaimRecord
from .runtime_state import RuntimeRecord, task_key
from .workers import Worker


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


class SQLiteBackend:
    SCHEMA_VERSION = 15

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.initialize()

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(
            self.path,
            timeout=30,
            isolation_level=None,
        )
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys=ON")
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("PRAGMA synchronous=NORMAL")
        connection.execute("PRAGMA busy_timeout=30000")
        return connection

    @contextmanager
    def transaction(self, *, immediate: bool = True) -> Iterator[sqlite3.Connection]:
        connection = self.connect()
        try:
            connection.execute("BEGIN IMMEDIATE" if immediate else "BEGIN")
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def initialize(self) -> None:
        with self.connect() as db:
            db.executescript(
                """
                CREATE TABLE IF NOT EXISTS schema_meta (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS runtime_records (
                    key TEXT PRIMARY KEY,
                    repository TEXT NOT NULL,
                    task TEXT NOT NULL,
                    status TEXT NOT NULL,
                    attempts INTEGER NOT NULL DEFAULT 0,
                    consecutive_failures INTEGER NOT NULL DEFAULT 0,
                    lease_owner TEXT,
                    lease_expires_at TEXT,
                    cooldown_until TEXT,
                    last_decision TEXT,
                    updated_at TEXT,
                    priority REAL NOT NULL DEFAULT 0,
                    interruptible INTEGER NOT NULL DEFAULT 0,
                    preempt_requested INTEGER NOT NULL DEFAULT 0,
                    checkpoint_ref TEXT,
                    started_at TEXT
                );

                CREATE UNIQUE INDEX IF NOT EXISTS idx_runtime_repo_task
                ON runtime_records(repository, task);

                CREATE TABLE IF NOT EXISTS workers (
                    worker_id TEXT PRIMARY KEY,
                    capabilities_json TEXT NOT NULL,
                    max_concurrency INTEGER NOT NULL,
                    active_tasks INTEGER NOT NULL DEFAULT 0,
                    status TEXT NOT NULL DEFAULT 'online',
                    last_heartbeat TEXT
                );

                CREATE TABLE IF NOT EXISTS claims (
                    key TEXT PRIMARY KEY,
                    worker_id TEXT NOT NULL,
                    repository TEXT NOT NULL,
                    task TEXT NOT NULL,
                    status TEXT NOT NULL,
                    claimed_at TEXT NOT NULL,
                    ack_deadline TEXT NOT NULL,
                    completed_at TEXT
                );

                CREATE TABLE IF NOT EXISTS jobs (
                    key TEXT PRIMARY KEY,
                    repository TEXT NOT NULL,
                    task TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    priority REAL NOT NULL DEFAULT 0,
                    status TEXT NOT NULL DEFAULT 'queued',
                    assigned_worker TEXT,
                    claimed_by TEXT,
                    claimed_at TEXT,
                    ack_deadline TEXT,
                    completed_at TEXT,
                    delivery_attempt INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_jobs_status_priority
                ON jobs(status, priority DESC, created_at ASC);

                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    repository TEXT,
                    task_key TEXT,
                    payload_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS webhook_deliveries (
                    delivery_id TEXT PRIMARY KEY,
                    event_name TEXT NOT NULL,
                    repository TEXT,
                    received_at TEXT NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_events_id
                ON events(id);

                CREATE TABLE IF NOT EXISTS workflows (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    repository TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pending',
                    metadata_json TEXT NOT NULL DEFAULT '{}',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS workflow_tasks (
                    workflow_id TEXT NOT NULL,
                    task_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pending',
                    priority REAL NOT NULL DEFAULT 0,
                    dependencies_json TEXT NOT NULL DEFAULT '[]',
                    claimed_job_key TEXT,
                    result_json TEXT,
                    attempts INTEGER NOT NULL DEFAULT 0,
                    max_attempts INTEGER NOT NULL DEFAULT 1,
                    estimated_minutes REAL NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    PRIMARY KEY(workflow_id, task_id),
                    FOREIGN KEY(workflow_id) REFERENCES workflows(id)
                        ON DELETE CASCADE
                );

                CREATE INDEX IF NOT EXISTS idx_workflow_tasks_status
                ON workflow_tasks(workflow_id, status, priority DESC);

                CREATE TABLE IF NOT EXISTS artifacts (
                    id TEXT PRIMARY KEY,
                    workflow_id TEXT NOT NULL,
                    task_id TEXT,
                    name TEXT NOT NULL,
                    uri TEXT NOT NULL,
                    sha256 TEXT,
                    metadata_json TEXT NOT NULL DEFAULT '{}',
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(workflow_id) REFERENCES workflows(id)
                        ON DELETE CASCADE
                );

                CREATE INDEX IF NOT EXISTS idx_artifacts_workflow
                ON artifacts(workflow_id, task_id);

                CREATE TABLE IF NOT EXISTS releases (
                    id TEXT PRIMARY KEY,
                    workflow_id TEXT NOT NULL,
                    artifact_id TEXT NOT NULL,
                    repository TEXT NOT NULL,
                    source_revision TEXT,
                    workflow_generation INTEGER,
                    validation_json TEXT NOT NULL,
                    metadata_json TEXT NOT NULL DEFAULT '{}',
                    status TEXT NOT NULL,
                    rollback_of TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(workflow_id) REFERENCES workflows(id)
                        ON DELETE RESTRICT,
                    FOREIGN KEY(artifact_id) REFERENCES artifacts(id)
                        ON DELETE RESTRICT,
                    FOREIGN KEY(rollback_of) REFERENCES releases(id)
                        ON DELETE RESTRICT
                );

                CREATE UNIQUE INDEX IF NOT EXISTS idx_release_promoted_artifact
                ON releases(artifact_id)
                WHERE status='promoted';

                CREATE INDEX IF NOT EXISTS idx_releases_workflow
                ON releases(workflow_id, created_at);

                CREATE TABLE IF NOT EXISTS transparency_log (
                    sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                    release_id TEXT NOT NULL UNIQUE,
                    entry_json TEXT NOT NULL,
                    entry_hash TEXT NOT NULL UNIQUE,
                    previous_hash TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(release_id) REFERENCES releases(id)
                        ON DELETE RESTRICT
                );

                CREATE INDEX IF NOT EXISTS idx_transparency_release
                ON transparency_log(release_id);

                CREATE UNIQUE INDEX IF NOT EXISTS idx_release_single_rollback
                ON releases(rollback_of)
                WHERE rollback_of IS NOT NULL;

                CREATE TABLE IF NOT EXISTS trust_incident_reports (
                    sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                    incident_id TEXT NOT NULL,
                    report_json TEXT NOT NULL,
                    report_hash TEXT NOT NULL UNIQUE,
                    previous_hash TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_trust_incident_id
                ON trust_incident_reports(incident_id, sequence);

                CREATE TABLE IF NOT EXISTS execution_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    repository TEXT NOT NULL,
                    task TEXT NOT NULL,
                    worker_id TEXT NOT NULL,
                    duration_seconds REAL NOT NULL,
                    succeeded INTEGER NOT NULL,
                    capabilities_json TEXT NOT NULL DEFAULT '[]',
                    created_at TEXT NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_execution_history_task
                ON execution_history(repository, task, created_at DESC);

                CREATE INDEX IF NOT EXISTS idx_execution_history_worker
                ON execution_history(worker_id, created_at DESC);

                CREATE TABLE IF NOT EXISTS result_cache (
                    fingerprint TEXT PRIMARY KEY,
                    repository TEXT NOT NULL,
                    task TEXT NOT NULL,
                    result_json TEXT NOT NULL,
                    artifact_json TEXT NOT NULL DEFAULT '[]',
                    created_at TEXT NOT NULL,
                    last_used_at TEXT NOT NULL,
                    hits INTEGER NOT NULL DEFAULT 0
                );

                CREATE INDEX IF NOT EXISTS idx_result_cache_repo_task
                ON result_cache(repository, task, last_used_at DESC);

                CREATE TABLE IF NOT EXISTS speculation_groups (
                    group_id TEXT PRIMARY KEY,
                    canonical_job_key TEXT NOT NULL,
                    winner_job_key TEXT,
                    created_at TEXT NOT NULL,
                    resolved_at TEXT
                );

                CREATE TABLE IF NOT EXISTS speculation_members (
                    group_id TEXT NOT NULL,
                    job_key TEXT NOT NULL,
                    worker_id TEXT,
                    created_at TEXT NOT NULL,
                    PRIMARY KEY(group_id, job_key),
                    FOREIGN KEY(group_id) REFERENCES speculation_groups(group_id)
                        ON DELETE CASCADE
                );

                CREATE INDEX IF NOT EXISTS idx_speculation_members_job
                ON speculation_members(job_key);

                CREATE TABLE IF NOT EXISTS worker_control_state (
                    worker_id TEXT PRIMARY KEY, desired_state TEXT NOT NULL DEFAULT 'active',
                    reason TEXT, requested_by TEXT, requested_at TEXT NOT NULL, updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS job_control_state (
                    job_key TEXT PRIMARY KEY, desired_state TEXT NOT NULL DEFAULT 'active',
                    reason TEXT, requested_by TEXT, requested_at TEXT NOT NULL,
                    acknowledged_at TEXT, updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS control_audit_events (
                    id TEXT PRIMARY KEY,
                    action TEXT NOT NULL,
                    worker_id TEXT NOT NULL,
                    job_key TEXT,
                    requested_by TEXT NOT NULL,
                    outcome TEXT NOT NULL,
                    error_code TEXT,
                    requested_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_control_audit_requested_at
                ON control_audit_events(requested_at DESC);
                CREATE TABLE IF NOT EXISTS dashboard_incidents (
                    id TEXT PRIMARY KEY,
                    dedupe_key TEXT NOT NULL UNIQUE,
                    code TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    title TEXT NOT NULL,
                    message TEXT NOT NULL,
                    target_type TEXT NOT NULL,
                    target_id TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'open',
                    occurrence_count INTEGER NOT NULL DEFAULT 1,
                    first_seen_at TEXT NOT NULL,
                    last_seen_at TEXT NOT NULL,
                    acknowledged_by TEXT,
                    acknowledged_at TEXT,
                    resolved_at TEXT
                );
                CREATE INDEX IF NOT EXISTS idx_dashboard_incidents_status_time
                ON dashboard_incidents(status, last_seen_at DESC);
                CREATE TABLE IF NOT EXISTS dashboard_remediation_events (
                    id TEXT PRIMARY KEY,
                    incident_id TEXT NOT NULL,
                    action TEXT NOT NULL,
                    worker_id TEXT,
                    job_key TEXT,
                    requested_by TEXT NOT NULL,
                    outcome TEXT NOT NULL,
                    error_code TEXT,
                    requested_at TEXT NOT NULL,
                    completed_at TEXT,
                    verification_state TEXT NOT NULL DEFAULT 'pending',
                    verification_checks INTEGER NOT NULL DEFAULT 0,
                    verified_at TEXT,
                    resolved_occurrence_count INTEGER,
                    recurrence_state TEXT NOT NULL DEFAULT 'not_evaluated',
                    recurred_at TEXT,
                    FOREIGN KEY(incident_id) REFERENCES dashboard_incidents(id)
                        ON DELETE RESTRICT
                );
                CREATE INDEX IF NOT EXISTS idx_dashboard_remediation_incident_time
                ON dashboard_remediation_events(incident_id, requested_at DESC);
                CREATE INDEX IF NOT EXISTS idx_dashboard_remediation_requested_at
                ON dashboard_remediation_events(requested_at DESC);
                CREATE TABLE IF NOT EXISTS job_executions (
                    id TEXT PRIMARY KEY, job_key TEXT NOT NULL, workflow_id TEXT,
                    workflow_task_id TEXT, repository TEXT NOT NULL, worker_id TEXT NOT NULL,
                    attempt INTEGER NOT NULL DEFAULT 1, status TEXT NOT NULL, started_at TEXT NOT NULL,
                    finished_at TEXT, duration_seconds REAL, provider TEXT, model TEXT,
                    api_calls INTEGER NOT NULL DEFAULT 0, input_tokens INTEGER NOT NULL DEFAULT 0,
                    cached_input_tokens INTEGER NOT NULL DEFAULT 0, output_tokens INTEGER NOT NULL DEFAULT 0,
                    reasoning_tokens INTEGER NOT NULL DEFAULT 0, total_tokens INTEGER NOT NULL DEFAULT 0,
                    estimated_cost_usd REAL, pricing_catalog_version TEXT,
                    commit_count INTEGER NOT NULL DEFAULT 0, commit_shas_json TEXT NOT NULL DEFAULT '[]',
                    retry_of_execution_id TEXT, error_type TEXT, error_message TEXT,
                    current_stage TEXT, progress_percent REAL, live_usage_json TEXT NOT NULL DEFAULT '{}',
                    last_telemetry_at TEXT, result_summary_json TEXT NOT NULL DEFAULT '{}', created_at TEXT NOT NULL
                );
                CREATE UNIQUE INDEX IF NOT EXISTS idx_job_executions_job_attempt ON job_executions(job_key, attempt);
                CREATE INDEX IF NOT EXISTS idx_job_executions_worker_started ON job_executions(worker_id, started_at DESC);
                CREATE INDEX IF NOT EXISTS idx_job_executions_repo_started ON job_executions(repository, started_at DESC);
                CREATE INDEX IF NOT EXISTS idx_job_executions_workflow_started ON job_executions(workflow_id, started_at DESC);
                CREATE TABLE IF NOT EXISTS api_usage_events (
                    id TEXT PRIMARY KEY, execution_id TEXT NOT NULL, worker_id TEXT NOT NULL,
                    repository TEXT NOT NULL, provider TEXT, model TEXT,
                    api_calls INTEGER NOT NULL DEFAULT 1, input_tokens INTEGER NOT NULL DEFAULT 0,
                    cached_input_tokens INTEGER NOT NULL DEFAULT 0, output_tokens INTEGER NOT NULL DEFAULT 0,
                    reasoning_tokens INTEGER NOT NULL DEFAULT 0, total_tokens INTEGER NOT NULL DEFAULT 0,
                    estimated_cost_usd REAL, pricing_catalog_version TEXT, occurred_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_api_usage_worker_time ON api_usage_events(worker_id, occurred_at DESC);
                CREATE INDEX IF NOT EXISTS idx_api_usage_repo_time ON api_usage_events(repository, occurred_at DESC);
                CREATE TABLE IF NOT EXISTS provider_quota_snapshots (
                    id TEXT PRIMARY KEY, provider TEXT NOT NULL, quota_type TEXT, used_value REAL,
                    limit_value REAL, remaining_value REAL, unit TEXT, source_status TEXT NOT NULL, captured_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS worker_log_events (
                    id TEXT PRIMARY KEY, worker_id TEXT NOT NULL, repository TEXT, workflow_id TEXT,
                    job_key TEXT, level TEXT NOT NULL, stage TEXT, message TEXT NOT NULL, provider TEXT,
                    model TEXT, metadata_json TEXT NOT NULL DEFAULT '{}', created_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_worker_logs_worker_time ON worker_log_events(worker_id, created_at DESC);
                CREATE TABLE IF NOT EXISTS project_repository_snapshots (
                    id TEXT PRIMARY KEY, repository TEXT NOT NULL, default_branch TEXT,
                    production_os_commits INTEGER NOT NULL DEFAULT 0, github_commits INTEGER,
                    open_issues INTEGER, open_pull_requests INTEGER, ci_status TEXT, latest_commit_sha TEXT,
                    latest_release TEXT, tests_detected INTEGER, tests_passing INTEGER, tests_failing INTEGER,
                    snapshot_json TEXT NOT NULL DEFAULT '{}', captured_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_project_repo_snapshots_repo_time ON project_repository_snapshots(repository, captured_at DESC);
                CREATE TABLE IF NOT EXISTS project_progress_snapshots (
                    id TEXT PRIMARY KEY, repository TEXT NOT NULL, current_workflow_id TEXT,
                    production_progress REAL, project_progress REAL, confidence TEXT NOT NULL,
                    code_score REAL, ui_ux_score REAL, assets_score REAL, tests_score REAL,
                    stability_score REAL, release_score REAL, evidence_json TEXT NOT NULL DEFAULT '{}',
                    remaining_work_json TEXT NOT NULL DEFAULT '[]', blockers_json TEXT NOT NULL DEFAULT '[]',
                    calculation_version TEXT NOT NULL, captured_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_project_progress_repo_time ON project_progress_snapshots(repository, captured_at DESC);
                CREATE TABLE IF NOT EXISTS managed_projects (
                    id TEXT PRIMARY KEY,
                    repository TEXT NOT NULL,
                    final_goal TEXT NOT NULL,
                    token_budget INTEGER NOT NULL,
                    agent_preference TEXT NOT NULL,
                    status TEXT NOT NULL,
                    current_workflow_id TEXT,
                    generation INTEGER NOT NULL DEFAULT 1,
                    created_by TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    reviewed_at TEXT,
                    completed_at TEXT,
                    completed_by TEXT,
                    FOREIGN KEY(current_workflow_id) REFERENCES workflows(id)
                        ON DELETE RESTRICT
                );
                CREATE INDEX IF NOT EXISTS idx_managed_projects_status_time
                ON managed_projects(status, updated_at DESC);
                CREATE INDEX IF NOT EXISTS idx_managed_projects_repository
                ON managed_projects(repository, updated_at DESC);
                CREATE TABLE IF NOT EXISTS managed_project_runs (
                    id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    generation INTEGER NOT NULL,
                    kind TEXT NOT NULL,
                    instruction TEXT NOT NULL,
                    workflow_id TEXT NOT NULL,
                    requested_by TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(project_id) REFERENCES managed_projects(id)
                        ON DELETE CASCADE,
                    FOREIGN KEY(workflow_id) REFERENCES workflows(id)
                        ON DELETE RESTRICT,
                    UNIQUE(project_id, generation)
                );
                CREATE INDEX IF NOT EXISTS idx_managed_project_runs_project
                ON managed_project_runs(project_id, generation DESC);
                """
            )
            managed_columns = {
                row["name"]
                for row in db.execute(
                    "PRAGMA table_info(managed_projects)"
                ).fetchall()
            }
            if "token_budget" not in managed_columns:
                db.execute(
                    """ALTER TABLE managed_projects
                       ADD COLUMN token_budget INTEGER NOT NULL
                       DEFAULT 30000"""
                )
            if "agent_preference" not in managed_columns:
                db.execute(
                    """ALTER TABLE managed_projects
                       ADD COLUMN agent_preference TEXT NOT NULL
                       DEFAULT 'auto'"""
                )
            if "completed_by" not in managed_columns:
                db.execute(
                    """ALTER TABLE managed_projects
                       ADD COLUMN completed_by TEXT"""
                )

            remediation_columns = {
                row["name"]
                for row in db.execute(
                    "PRAGMA table_info(dashboard_remediation_events)"
                ).fetchall()
            }
            if "verification_state" not in remediation_columns:
                db.execute(
                    """ALTER TABLE dashboard_remediation_events
                       ADD COLUMN verification_state TEXT NOT NULL
                       DEFAULT 'pending'"""
                )
            if "verification_checks" not in remediation_columns:
                db.execute(
                    """ALTER TABLE dashboard_remediation_events
                       ADD COLUMN verification_checks INTEGER NOT NULL
                       DEFAULT 0"""
                )
            if "verified_at" not in remediation_columns:
                db.execute(
                    """ALTER TABLE dashboard_remediation_events
                       ADD COLUMN verified_at TEXT"""
                )
            if "resolved_occurrence_count" not in remediation_columns:
                db.execute(
                    """ALTER TABLE dashboard_remediation_events
                       ADD COLUMN resolved_occurrence_count INTEGER"""
                )
            if "recurrence_state" not in remediation_columns:
                db.execute(
                    """ALTER TABLE dashboard_remediation_events
                       ADD COLUMN recurrence_state TEXT NOT NULL
                       DEFAULT 'not_evaluated'"""
                )
            if "recurred_at" not in remediation_columns:
                db.execute(
                    """ALTER TABLE dashboard_remediation_events
                       ADD COLUMN recurred_at TEXT"""
                )

            db.execute(
                """
                INSERT INTO schema_meta(key, value)
                VALUES('schema_version', ?)
                ON CONFLICT(key) DO UPDATE SET value=excluded.value
                """,
                (str(self.SCHEMA_VERSION),),
            )

    def append_event(
        self,
        db: sqlite3.Connection,
        event_type: str,
        payload: dict,
        *,
        repository: str | None = None,
        task_key_value: str | None = None,
    ) -> int:
        cursor = db.execute(
            """
            INSERT INTO events(event_type, repository, task_key, payload_json, created_at)
            VALUES(?, ?, ?, ?, ?)
            """,
            (
                event_type,
                repository,
                task_key_value,
                json.dumps(payload, ensure_ascii=False, sort_keys=True),
                _utcnow(),
            ),
        )
        return int(cursor.lastrowid)

    def events_after(self, event_id: int = 0, limit: int = 100) -> list[dict]:
        with self.connect() as db:
            rows = db.execute(
                """
                SELECT id, event_type, repository, task_key, payload_json, created_at
                FROM events
                WHERE id > ?
                ORDER BY id ASC
                LIMIT ?
                """,
                (max(0, event_id), max(1, min(limit, 1000))),
            ).fetchall()
        return [
            {
                "id": row["id"],
                "event_type": row["event_type"],
                "repository": row["repository"],
                "task_key": row["task_key"],
                "payload": json.loads(row["payload_json"]),
                "created_at": row["created_at"],
            }
            for row in rows
        ]


class SQLiteRuntimeState:
    def __init__(self, backend: SQLiteBackend):
        self.backend = backend
        self.records: dict[str, RuntimeRecord] = {}
        self.load()

    @staticmethod
    def _row(row: sqlite3.Row) -> RuntimeRecord:
        return RuntimeRecord(
            key=row["key"],
            repository=row["repository"],
            task=row["task"],
            status=row["status"],
            attempts=row["attempts"],
            consecutive_failures=row["consecutive_failures"],
            lease_owner=row["lease_owner"],
            lease_expires_at=row["lease_expires_at"],
            cooldown_until=row["cooldown_until"],
            last_decision=row["last_decision"],
            updated_at=row["updated_at"],
            priority=row["priority"],
            interruptible=bool(row["interruptible"]),
            preempt_requested=bool(row["preempt_requested"]),
            checkpoint_ref=row["checkpoint_ref"],
            started_at=row["started_at"],
        )

    def load(self) -> None:
        with self.backend.connect() as db:
            rows = db.execute("SELECT * FROM runtime_records").fetchall()
        self.records = {row["key"]: self._row(row) for row in rows}

    def save(self) -> None:
        with self.backend.transaction() as db:
            for record in self.records.values():
                db.execute(
                    """
                    INSERT INTO runtime_records(
                        key, repository, task, status, attempts,
                        consecutive_failures, lease_owner, lease_expires_at,
                        cooldown_until, last_decision, updated_at, priority,
                        interruptible, preempt_requested, checkpoint_ref,
                        started_at
                    )
                    VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                    ON CONFLICT(key) DO UPDATE SET
                        repository=excluded.repository,
                        task=excluded.task,
                        status=excluded.status,
                        attempts=excluded.attempts,
                        consecutive_failures=excluded.consecutive_failures,
                        lease_owner=excluded.lease_owner,
                        lease_expires_at=excluded.lease_expires_at,
                        cooldown_until=excluded.cooldown_until,
                        last_decision=excluded.last_decision,
                        updated_at=excluded.updated_at,
                        priority=excluded.priority,
                        interruptible=excluded.interruptible,
                        preempt_requested=excluded.preempt_requested,
                        checkpoint_ref=excluded.checkpoint_ref,
                        started_at=excluded.started_at
                    """,
                    (
                        record.key,
                        record.repository,
                        record.task,
                        record.status,
                        record.attempts,
                        record.consecutive_failures,
                        record.lease_owner,
                        record.lease_expires_at,
                        record.cooldown_until,
                        record.last_decision,
                        record.updated_at,
                        record.priority,
                        int(record.interruptible),
                        int(record.preempt_requested),
                        record.checkpoint_ref,
                        record.started_at,
                    ),
                )

    def get(self, repository: str, task: str) -> RuntimeRecord:
        key = task_key(repository, task)
        with self.backend.transaction() as db:
            row = db.execute(
                "SELECT * FROM runtime_records WHERE key=?",
                (key,),
            ).fetchone()
            if row is None:
                db.execute(
                    """
                    INSERT INTO runtime_records(key, repository, task, status)
                    VALUES(?, ?, ?, 'idle')
                    """,
                    (key, repository, task),
                )
                row = db.execute(
                    "SELECT * FROM runtime_records WHERE key=?",
                    (key,),
                ).fetchone()
        record = self._row(row)
        self.records[key] = record
        return record

    @staticmethod
    def _parse(ts: str | None) -> datetime | None:
        if not ts:
            return None
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))

    def is_leased(self, record: RuntimeRecord, now: datetime | None = None) -> bool:
        now = now or datetime.now(timezone.utc)
        expires = self._parse(record.lease_expires_at)
        return bool(expires and expires > now and record.lease_owner)

    def in_cooldown(self, record: RuntimeRecord, now: datetime | None = None) -> bool:
        now = now or datetime.now(timezone.utc)
        until = self._parse(record.cooldown_until)
        return bool(until and until > now)

    def acquire_lease(
        self,
        repository: str,
        task: str,
        owner: str,
        minutes: int = 30,
        *,
        priority: float = 0.0,
        interruptible: bool = False,
    ) -> RuntimeRecord:
        key = task_key(repository, task)
        now = datetime.now(timezone.utc)
        expires = (now + timedelta(minutes=minutes)).isoformat()
        with self.backend.transaction() as db:
            row = db.execute(
                "SELECT * FROM runtime_records WHERE key=?",
                (key,),
            ).fetchone()
            if row is None:
                db.execute(
                    """
                    INSERT INTO runtime_records(key, repository, task, status)
                    VALUES(?, ?, ?, 'idle')
                    """,
                    (key, repository, task),
                )
                row = db.execute(
                    "SELECT * FROM runtime_records WHERE key=?",
                    (key,),
                ).fetchone()
            current = self._row(row)
            if self.is_leased(current, now):
                raise RuntimeError("task already leased")
            db.execute(
                """
                UPDATE runtime_records
                SET lease_owner=?, lease_expires_at=?, status='running',
                    started_at=?, priority=?, interruptible=?,
                    preempt_requested=0, updated_at=?
                WHERE key=?
                """,
                (
                    owner,
                    expires,
                    now.isoformat(),
                    float(priority),
                    int(interruptible),
                    now.isoformat(),
                    key,
                ),
            )
            self.backend.append_event(
                db,
                "lease-acquired",
                {"owner": owner, "lease_expires_at": expires},
                repository=repository,
                task_key_value=key,
            )
            row = db.execute(
                "SELECT * FROM runtime_records WHERE key=?",
                (key,),
            ).fetchone()
        record = self._row(row)
        self.records[key] = record
        return record

    def heartbeat_lease(
        self,
        repository: str,
        task: str,
        owner: str,
        minutes: int = 30,
    ) -> RuntimeRecord:
        key = task_key(repository, task)
        now = datetime.now(timezone.utc)
        with self.backend.transaction() as db:
            row = db.execute(
                "SELECT * FROM runtime_records WHERE key=?",
                (key,),
            ).fetchone()
            if row is None:
                raise RuntimeError("task has no active lease")
            current = self._row(row)
            if not self.is_leased(current, now):
                raise RuntimeError("task has no active lease")
            if current.lease_owner != owner:
                raise RuntimeError("lease owner mismatch")
            expires = (now + timedelta(minutes=minutes)).isoformat()
            db.execute(
                """
                UPDATE runtime_records
                SET lease_expires_at=?, updated_at=?
                WHERE key=?
                """,
                (expires, now.isoformat(), key),
            )
            row = db.execute(
                "SELECT * FROM runtime_records WHERE key=?",
                (key,),
            ).fetchone()
        record = self._row(row)
        self.records[key] = record
        return record

    def release_lease(self, repository: str, task: str) -> RuntimeRecord:
        key = task_key(repository, task)
        now = _utcnow()
        with self.backend.transaction() as db:
            row = db.execute(
                "SELECT status FROM runtime_records WHERE key=?",
                (key,),
            ).fetchone()
            if row is None:
                raise KeyError(key)
            status = "idle" if row["status"] in {"running", "preempt-requested"} else row["status"]
            db.execute(
                """
                UPDATE runtime_records
                SET lease_owner=NULL, lease_expires_at=NULL, status=?, updated_at=?
                WHERE key=?
                """,
                (status, now, key),
            )
            self.backend.append_event(
                db,
                "lease-released",
                {},
                repository=repository,
                task_key_value=key,
            )
            row = db.execute(
                "SELECT * FROM runtime_records WHERE key=?",
                (key,),
            ).fetchone()
        record = self._row(row)
        self.records[key] = record
        return record

    def record_outcome(
        self,
        repository: str,
        task: str,
        decision: str,
        *,
        retry_budget: int = 3,
        cooldown_minutes: int = 60,
        circuit_breaker_failures: int = 3,
    ) -> RuntimeRecord:
        current = self.get(repository, task)
        now = datetime.now(timezone.utc)
        attempts = current.attempts + 1
        failures = current.consecutive_failures
        status = "idle"
        cooldown = current.cooldown_until
        if decision == "promote":
            status = "succeeded"
            failures = 0
            cooldown = None
        elif decision in {"rollback", "retry"}:
            failures += 1
            status = "failed"
            if attempts >= retry_budget or failures >= circuit_breaker_failures:
                status = "circuit-open"
                cooldown = (now + timedelta(minutes=cooldown_minutes)).isoformat()
        elif decision == "replan":
            status = "replan"
            cooldown = (
                now + timedelta(minutes=max(10, cooldown_minutes // 2))
            ).isoformat()

        with self.backend.transaction() as db:
            db.execute(
                """
                UPDATE runtime_records
                SET attempts=?, consecutive_failures=?, lease_owner=NULL,
                    lease_expires_at=NULL, last_decision=?, status=?,
                    cooldown_until=?, updated_at=?
                WHERE key=?
                """,
                (
                    attempts,
                    failures,
                    decision,
                    status,
                    cooldown,
                    now.isoformat(),
                    current.key,
                ),
            )
            self.backend.append_event(
                db,
                "task-outcome",
                {"decision": decision, "status": status},
                repository=repository,
                task_key_value=current.key,
            )
            row = db.execute(
                "SELECT * FROM runtime_records WHERE key=?",
                (current.key,),
            ).fetchone()
        record = self._row(row)
        self.records[current.key] = record
        return record


class SQLiteWorkerRegistry:
    def __init__(self, backend: SQLiteBackend):
        self.backend = backend
        self.workers: dict[str, Worker] = {}
        self.load()

    @staticmethod
    def _row(row: sqlite3.Row) -> Worker:
        return Worker(
            worker_id=row["worker_id"],
            capabilities=json.loads(row["capabilities_json"]),
            max_concurrency=row["max_concurrency"],
            active_tasks=row["active_tasks"],
            status=row["status"],
            last_heartbeat=row["last_heartbeat"],
        )

    def load(self) -> None:
        with self.backend.connect() as db:
            rows = db.execute("SELECT * FROM workers").fetchall()
        self.workers = {row["worker_id"]: self._row(row) for row in rows}

    def save(self) -> None:
        with self.backend.transaction() as db:
            for worker in self.workers.values():
                db.execute(
                    """
                    INSERT INTO workers(
                        worker_id, capabilities_json, max_concurrency,
                        active_tasks, status, last_heartbeat
                    )
                    VALUES(?,?,?,?,?,?)
                    ON CONFLICT(worker_id) DO UPDATE SET
                        capabilities_json=excluded.capabilities_json,
                        max_concurrency=excluded.max_concurrency,
                        active_tasks=excluded.active_tasks,
                        status=excluded.status,
                        last_heartbeat=excluded.last_heartbeat
                    """,
                    (
                        worker.worker_id,
                        json.dumps(worker.capabilities),
                        worker.max_concurrency,
                        worker.active_tasks,
                        worker.status,
                        worker.last_heartbeat,
                    ),
                )

    def register(
        self,
        worker_id: str,
        capabilities: list[str],
        max_concurrency: int,
    ) -> Worker:
        if max_concurrency < 1:
            raise ValueError("max_concurrency must be >= 1")
        now = _utcnow()
        with self.backend.transaction() as db:
            db.execute(
                """
                INSERT INTO workers(
                    worker_id, capabilities_json, max_concurrency,
                    active_tasks, status, last_heartbeat
                )
                VALUES(?, ?, ?, 0, 'online', ?)
                ON CONFLICT(worker_id) DO UPDATE SET
                    capabilities_json=excluded.capabilities_json,
                    max_concurrency=excluded.max_concurrency,
                    status='online',
                    last_heartbeat=excluded.last_heartbeat
                """,
                (
                    worker_id,
                    json.dumps(sorted(set(capabilities))),
                    max_concurrency,
                    now,
                ),
            )
            self.backend.append_event(
                db,
                "worker-registered",
                {"worker_id": worker_id, "capabilities": sorted(set(capabilities))},
            )
            row = db.execute(
                "SELECT * FROM workers WHERE worker_id=?",
                (worker_id,),
            ).fetchone()
        worker = self._row(row)
        self.workers[worker_id] = worker
        return worker

    def heartbeat(self, worker_id: str, active_tasks: int | None = None) -> Worker:
        now = _utcnow()
        with self.backend.transaction() as db:
            row = db.execute(
                "SELECT * FROM workers WHERE worker_id=?",
                (worker_id,),
            ).fetchone()
            if row is None:
                raise KeyError(worker_id)
            active = row["active_tasks"] if active_tasks is None else max(0, active_tasks)
            db.execute(
                """
                UPDATE workers
                SET active_tasks=?, status='online', last_heartbeat=?
                WHERE worker_id=?
                """,
                (active, now, worker_id),
            )
            row = db.execute(
                "SELECT * FROM workers WHERE worker_id=?",
                (worker_id,),
            ).fetchone()
        worker = self._row(row)
        self.workers[worker_id] = worker
        return worker

    def adjust_active_tasks(self, worker_id: str, delta: int) -> Worker:
        with self.backend.transaction() as db:
            row = db.execute(
                "SELECT active_tasks FROM workers WHERE worker_id=?",
                (worker_id,),
            ).fetchone()
            if row is None:
                raise KeyError(worker_id)
            active = max(0, int(row["active_tasks"]) + int(delta))
            db.execute(
                "UPDATE workers SET active_tasks=? WHERE worker_id=?",
                (active, worker_id),
            )
            row = db.execute(
                "SELECT * FROM workers WHERE worker_id=?",
                (worker_id,),
            ).fetchone()
        worker = self._row(row)
        self.workers[worker_id] = worker
        return worker

    def detect_dead(self, timeout_seconds: int = 120) -> list[Worker]:
        self.load()
        now = datetime.now(timezone.utc)
        dead: list[Worker] = []
        for worker in list(self.workers.values()):
            if not worker.last_heartbeat:
                stale = True
            else:
                seen = datetime.fromisoformat(
                    worker.last_heartbeat.replace("Z", "+00:00")
                )
                stale = (now - seen).total_seconds() > timeout_seconds
            if stale and worker.status != "dead":
                with self.backend.transaction() as db:
                    db.execute(
                        "UPDATE workers SET status='dead' WHERE worker_id=?",
                        (worker.worker_id,),
                    )
                worker.status = "dead"
                dead.append(worker)
        self.load()
        return dead

    def available(self) -> list[Worker]:
        self.load()
        return [
            worker
            for worker in self.workers.values()
            if worker.status == "online"
            and worker.active_tasks < worker.max_concurrency
        ]


class SQLiteClaimStore:
    def __init__(self, backend: SQLiteBackend):
        self.backend = backend
        self.claims: dict[str, ClaimRecord] = {}
        self.load()

    @staticmethod
    def _row(row: sqlite3.Row) -> ClaimRecord:
        return ClaimRecord(
            key=row["key"],
            worker_id=row["worker_id"],
            repository=row["repository"],
            task=row["task"],
            status=row["status"],
            claimed_at=row["claimed_at"],
            ack_deadline=row["ack_deadline"],
            completed_at=row["completed_at"],
        )

    def load(self) -> None:
        with self.backend.connect() as db:
            rows = db.execute("SELECT * FROM claims").fetchall()
        self.claims = {row["key"]: self._row(row) for row in rows}

    def save(self) -> None:
        with self.backend.transaction() as db:
            for claim in self.claims.values():
                db.execute(
                    """
                    INSERT INTO claims(
                        key, worker_id, repository, task, status,
                        claimed_at, ack_deadline, completed_at
                    )
                    VALUES(?,?,?,?,?,?,?,?)
                    ON CONFLICT(key) DO UPDATE SET
                        worker_id=excluded.worker_id,
                        repository=excluded.repository,
                        task=excluded.task,
                        status=excluded.status,
                        claimed_at=excluded.claimed_at,
                        ack_deadline=excluded.ack_deadline,
                        completed_at=excluded.completed_at
                    """,
                    (
                        claim.key,
                        claim.worker_id,
                        claim.repository,
                        claim.task,
                        claim.status,
                        claim.claimed_at,
                        claim.ack_deadline,
                        claim.completed_at,
                    ),
                )

    def claim(
        self,
        *,
        key: str,
        worker_id: str,
        repository: str,
        task: str,
        ack_timeout_seconds: int = 120,
    ) -> ClaimRecord:
        now = datetime.now(timezone.utc)
        deadline = (now + timedelta(seconds=ack_timeout_seconds)).isoformat()
        with self.backend.transaction() as db:
            row = db.execute("SELECT * FROM claims WHERE key=?", (key,)).fetchone()
            if row is not None and row["status"] in {"claimed", "acked", "completed"}:
                raise RuntimeError(f"job already {row['status']}")
            db.execute(
                """
                INSERT INTO claims(
                    key, worker_id, repository, task, status,
                    claimed_at, ack_deadline, completed_at
                )
                VALUES(?, ?, ?, ?, 'claimed', ?, ?, NULL)
                ON CONFLICT(key) DO UPDATE SET
                    worker_id=excluded.worker_id,
                    repository=excluded.repository,
                    task=excluded.task,
                    status='claimed',
                    claimed_at=excluded.claimed_at,
                    ack_deadline=excluded.ack_deadline,
                    completed_at=NULL
                """,
                (key, worker_id, repository, task, now.isoformat(), deadline),
            )
            row = db.execute("SELECT * FROM claims WHERE key=?", (key,)).fetchone()
        claim = self._row(row)
        self.claims[key] = claim
        return claim

    def ack(self, key: str, worker_id: str) -> ClaimRecord:
        with self.backend.transaction() as db:
            row = db.execute("SELECT * FROM claims WHERE key=?", (key,)).fetchone()
            if row is None:
                raise KeyError(key)
            if row["worker_id"] != worker_id:
                raise RuntimeError("claim owner mismatch")
            if row["status"] != "completed":
                db.execute(
                    "UPDATE claims SET status='acked' WHERE key=?",
                    (key,),
                )
            row = db.execute("SELECT * FROM claims WHERE key=?", (key,)).fetchone()
        claim = self._row(row)
        self.claims[key] = claim
        return claim

    def complete(self, key: str, worker_id: str) -> ClaimRecord:
        now = _utcnow()
        with self.backend.transaction() as db:
            row = db.execute("SELECT * FROM claims WHERE key=?", (key,)).fetchone()
            if row is None:
                raise KeyError(key)
            if row["worker_id"] != worker_id:
                raise RuntimeError("claim owner mismatch")
            db.execute(
                """
                UPDATE claims
                SET status='completed', completed_at=?
                WHERE key=?
                """,
                (now, key),
            )
            row = db.execute("SELECT * FROM claims WHERE key=?", (key,)).fetchone()
        claim = self._row(row)
        self.claims[key] = claim
        return claim

    def expired_unacked(self) -> list[ClaimRecord]:
        now = _utcnow()
        with self.backend.connect() as db:
            rows = db.execute(
                """
                SELECT * FROM claims
                WHERE status='claimed' AND ack_deadline <= ?
                """,
                (now,),
            ).fetchall()
        return [self._row(row) for row in rows]


class SQLiteJobQueue:
    def __init__(self, backend: SQLiteBackend):
        self.backend = backend

    def enqueue(self, payload: dict) -> dict:
        handoff = payload.get("handoff", payload)
        repository = str(handoff.get("repository", ""))
        task = str(handoff.get("task", ""))
        if not repository or not task:
            raise ValueError("job requires repository and task")
        key = str(payload.get("idempotency_key") or task_key(repository, task))
        priority = float(handoff.get("priority", 0.0))
        now = _utcnow()
        normalized = {
            **payload,
            "idempotency_key": key,
            "handoff": handoff,
        }
        with self.backend.transaction() as db:
            existing = db.execute(
                "SELECT status FROM jobs WHERE key=?",
                (key,),
            ).fetchone()
            if existing is not None and existing["status"] not in {"failed", "dead-letter"}:
                raise RuntimeError(f"job already {existing['status']}")
            db.execute(
                """
                INSERT INTO jobs(
                    key, repository, task, payload_json, priority, status,
                    assigned_worker, claimed_by, claimed_at, ack_deadline,
                    completed_at, delivery_attempt, created_at, updated_at
                )
                VALUES(?, ?, ?, ?, ?, 'queued', ?, NULL, NULL, NULL, NULL, 0, ?, ?)
                ON CONFLICT(key) DO UPDATE SET
                    payload_json=excluded.payload_json,
                    priority=excluded.priority,
                    status='queued',
                    assigned_worker=excluded.assigned_worker,
                    claimed_by=NULL,
                    claimed_at=NULL,
                    ack_deadline=NULL,
                    completed_at=NULL,
                    updated_at=excluded.updated_at
                """,
                (
                    key,
                    repository,
                    task,
                    json.dumps(normalized, ensure_ascii=False),
                    priority,
                    payload.get("worker_id"),
                    now,
                    now,
                ),
            )
            self.backend.append_event(
                db,
                "job-enqueued",
                {"key": key, "priority": priority},
                repository=repository,
                task_key_value=key,
            )
        return self.get(key)

    def get(self, key: str) -> dict:
        with self.backend.connect() as db:
            row = db.execute("SELECT * FROM jobs WHERE key=?", (key,)).fetchone()
        if row is None:
            raise KeyError(key)
        return self._job_dict(row)

    @staticmethod
    def _job_dict(row: sqlite3.Row) -> dict:
        return {
            "key": row["key"],
            "repository": row["repository"],
            "task": row["task"],
            "payload": json.loads(row["payload_json"]),
            "priority": row["priority"],
            "status": row["status"],
            "assigned_worker": row["assigned_worker"],
            "claimed_by": row["claimed_by"],
            "claimed_at": row["claimed_at"],
            "ack_deadline": row["ack_deadline"],
            "completed_at": row["completed_at"],
            "delivery_attempt": row["delivery_attempt"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }


    def peek_candidates(
        self,
        *,
        worker_id: str | None = None,
        limit: int = 100,
    ) -> list[dict]:
        with self.backend.connect() as db:
            if worker_id is None:
                rows = db.execute(
                    """
                    SELECT * FROM jobs
                    WHERE status='queued'
                    ORDER BY priority DESC, created_at ASC
                    LIMIT ?
                    """,
                    (max(1, min(limit, 1000)),),
                ).fetchall()
            else:
                rows = db.execute(
                    """
                    SELECT * FROM jobs
                    WHERE status='queued'
                      AND (assigned_worker IS NULL OR assigned_worker=?)
                    ORDER BY priority DESC, created_at ASC
                    LIMIT ?
                    """,
                    (worker_id, max(1, min(limit, 1000))),
                ).fetchall()
        return [self._job_dict(row) for row in rows]


    def claim_key(
        self,
        key: str,
        worker_id: str,
        *,
        ack_timeout_seconds: int = 120,
    ) -> dict | None:
        now = datetime.now(timezone.utc)
        deadline = (
            now + timedelta(seconds=ack_timeout_seconds)
        ).isoformat()
        with self.backend.transaction() as db:
            row = db.execute(
                """
                SELECT * FROM jobs
                WHERE key=? AND status='queued'
                  AND (assigned_worker IS NULL OR assigned_worker=?)
                """,
                (key, worker_id),
            ).fetchone()
            if row is None:
                return None
            updated = db.execute(
                """
                UPDATE jobs
                SET status='claimed', claimed_by=?, claimed_at=?,
                    ack_deadline=?, delivery_attempt=delivery_attempt+1,
                    updated_at=?
                WHERE key=? AND status='queued'
                """,
                (
                    worker_id,
                    now.isoformat(),
                    deadline,
                    now.isoformat(),
                    key,
                ),
            )
            if updated.rowcount != 1:
                return None
            self.backend.append_event(
                db,
                "job-claimed",
                {"worker_id":worker_id},
                repository=row["repository"],
                task_key_value=key,
            )
            claimed = db.execute(
                "SELECT * FROM jobs WHERE key=?",
                (key,),
            ).fetchone()
        return self._job_dict(claimed)

    def claim_next(
        self,
        worker_id: str,
        *,
        capabilities: list[str] | None = None,
        ack_timeout_seconds: int = 120,
    ) -> dict | None:
        capabilities_set = set(capabilities or [])
        now = datetime.now(timezone.utc)
        deadline = (now + timedelta(seconds=ack_timeout_seconds)).isoformat()
        with self.backend.transaction() as db:
            rows = db.execute(
                """
                SELECT * FROM jobs
                WHERE status='queued'
                  AND (assigned_worker IS NULL OR assigned_worker=?)
                ORDER BY priority DESC, created_at ASC
                LIMIT 100
                """,
                (worker_id,),
            ).fetchall()
            chosen = None
            for row in rows:
                payload = json.loads(row["payload_json"])
                required = set(payload.get("required_capabilities", []))
                if required.issubset(capabilities_set):
                    chosen = row
                    break
            if chosen is None:
                return None
            updated = db.execute(
                """
                UPDATE jobs
                SET status='claimed', claimed_by=?, claimed_at=?,
                    ack_deadline=?, delivery_attempt=delivery_attempt+1,
                    updated_at=?
                WHERE key=? AND status='queued'
                """,
                (
                    worker_id,
                    now.isoformat(),
                    deadline,
                    now.isoformat(),
                    chosen["key"],
                ),
            )
            if updated.rowcount != 1:
                return None
            self.backend.append_event(
                db,
                "job-claimed",
                {"worker_id": worker_id},
                repository=chosen["repository"],
                task_key_value=chosen["key"],
            )
            row = db.execute(
                "SELECT * FROM jobs WHERE key=?",
                (chosen["key"],),
            ).fetchone()
        return self._job_dict(row)

    def ack(self, key: str, worker_id: str) -> dict:
        return self._transition(key, worker_id, {"claimed"}, "acked", "job-acked")

    def complete(self, key: str, worker_id: str) -> dict:
        return self._transition(
            key,
            worker_id,
            {"claimed", "acked"},
            "completed",
            "job-completed",
            completed=True,
        )

    def fail(self, key: str, worker_id: str, reason: str) -> dict:
        return self._transition(
            key,
            worker_id,
            {"claimed", "acked"},
            "failed",
            "job-failed",
            extra={"reason": reason},
        )

    def cancel(self, key: str, worker_id: str, reason: str = "operator cancel") -> dict:
        return self._transition(
            key,
            worker_id,
            {"claimed", "acked"},
            "cancelled",
            "job-cancelled",
            completed=True,
            extra={"reason": reason},
        )

    def _transition(
        self,
        key: str,
        worker_id: str,
        allowed_statuses: set[str],
        target: str,
        event_type: str,
        *,
        completed: bool = False,
        extra: dict | None = None,
    ) -> dict:
        now = _utcnow()
        with self.backend.transaction() as db:
            row = db.execute("SELECT * FROM jobs WHERE key=?", (key,)).fetchone()
            if row is None:
                raise KeyError(key)
            if row["claimed_by"] != worker_id:
                raise RuntimeError("job claim owner mismatch")
            if row["status"] not in allowed_statuses:
                raise RuntimeError(f"job cannot transition from {row['status']}")
            db.execute(
                """
                UPDATE jobs
                SET status=?, completed_at=?, updated_at=?
                WHERE key=?
                """,
                (target, now if completed else None, now, key),
            )
            self.backend.append_event(
                db,
                event_type,
                extra or {},
                repository=row["repository"],
                task_key_value=key,
            )
            row = db.execute("SELECT * FROM jobs WHERE key=?", (key,)).fetchone()
        return self._job_dict(row)

    def recover_job(self, key: str, *, max_attempts: int = 3) -> dict:
        now = _utcnow()
        with self.backend.transaction() as db:
            row = db.execute(
                "SELECT * FROM jobs WHERE key=?",
                (key,),
            ).fetchone()
            if row is None:
                raise KeyError(key)
            if row["status"] != "claimed":
                raise RuntimeError(
                    f"job is not recoverable from {row['status']}"
                )
            if not row["ack_deadline"] or row["ack_deadline"] > now:
                raise RuntimeError("job claim has not expired")
            target = (
                "dead-letter"
                if int(row["delivery_attempt"]) >= int(max_attempts)
                else "queued"
            )
            db.execute(
                """
                UPDATE jobs
                SET status=?, claimed_by=NULL, claimed_at=NULL,
                    ack_deadline=NULL, updated_at=?
                WHERE key=?
                """,
                (target, now, key),
            )
            action = {
                "key":key,
                "action":target,
                "delivery_attempt":row["delivery_attempt"],
            }
            self.backend.append_event(
                db,
                "job-recovered",
                action,
                repository=row["repository"],
                task_key_value=key,
            )
            updated = db.execute(
                "SELECT * FROM jobs WHERE key=?",
                (key,),
            ).fetchone()
        return self._job_dict(updated)

    def recover_expired(self, *, max_attempts: int = 3) -> list[dict]:
        now = _utcnow()
        actions = []
        with self.backend.transaction() as db:
            rows = db.execute(
                """
                SELECT * FROM jobs
                WHERE status='claimed' AND ack_deadline <= ?
                """,
                (now,),
            ).fetchall()
            for row in rows:
                target = (
                    "dead-letter"
                    if int(row["delivery_attempt"]) >= max_attempts
                    else "queued"
                )
                db.execute(
                    """
                    UPDATE jobs
                    SET status=?, claimed_by=NULL, claimed_at=NULL,
                        ack_deadline=NULL, updated_at=?
                    WHERE key=?
                    """,
                    (target, now, row["key"]),
                )
                action = {
                    "key": row["key"],
                    "action": target,
                    "delivery_attempt": row["delivery_attempt"],
                }
                actions.append(action)
                self.backend.append_event(
                    db,
                    "job-recovered",
                    action,
                    repository=row["repository"],
                    task_key_value=row["key"],
                )
        return actions
