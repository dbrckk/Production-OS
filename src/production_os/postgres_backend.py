from __future__ import annotations

import json
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from typing import Iterator

from .claims import ClaimRecord
from .runtime_state import RuntimeRecord, task_key
from .workers import Worker, _capacity_snapshot

try:
    import psycopg
    from psycopg.rows import dict_row
except ImportError:
    psycopg = None
    dict_row = None


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


class PostgresBackend:
    SCHEMA_VERSION = 9

    def __init__(self, dsn: str):
        if psycopg is None:
            raise RuntimeError(
                "PostgreSQL support requires: pip install 'production-os[postgres]'"
            )
        self.dsn = dsn
        self.initialize()

    def connect(self):
        return psycopg.connect(
            self.dsn,
            autocommit=True,
            row_factory=dict_row,
        )

    @contextmanager
    def transaction(self, *, immediate: bool = True) -> Iterator:
        connection = psycopg.connect(
            self.dsn,
            autocommit=False,
            row_factory=dict_row,
        )
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def initialize(self) -> None:
        with self.connect() as db:
            with db.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS schema_meta (
                        key TEXT PRIMARY KEY,
                        value TEXT NOT NULL
                    )
                """)
                cur.execute("""
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
                        priority DOUBLE PRECISION NOT NULL DEFAULT 0,
                        interruptible BOOLEAN NOT NULL DEFAULT FALSE,
                        preempt_requested BOOLEAN NOT NULL DEFAULT FALSE,
                        checkpoint_ref TEXT,
                        started_at TEXT
                    )
                """)
                cur.execute("""
                    CREATE UNIQUE INDEX IF NOT EXISTS idx_runtime_repo_task
                    ON runtime_records(repository, task)
                """)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS workers (
                        worker_id TEXT PRIMARY KEY,
                        capabilities_json TEXT NOT NULL,
                        max_concurrency INTEGER NOT NULL,
                        active_tasks INTEGER NOT NULL DEFAULT 0,
                        status TEXT NOT NULL DEFAULT 'online',
                        last_heartbeat TEXT,
                        capacity_json TEXT
                    )
                """)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS claims (
                        key TEXT PRIMARY KEY,
                        worker_id TEXT NOT NULL,
                        repository TEXT NOT NULL,
                        task TEXT NOT NULL,
                        status TEXT NOT NULL,
                        claimed_at TEXT NOT NULL,
                        ack_deadline TEXT NOT NULL,
                        completed_at TEXT
                    )
                """)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS jobs (
                        key TEXT PRIMARY KEY,
                        repository TEXT NOT NULL,
                        task TEXT NOT NULL,
                        payload_json TEXT NOT NULL,
                        priority DOUBLE PRECISION NOT NULL DEFAULT 0,
                        status TEXT NOT NULL DEFAULT 'queued',
                        assigned_worker TEXT,
                        claimed_by TEXT,
                        claimed_at TEXT,
                        ack_deadline TEXT,
                        completed_at TEXT,
                        delivery_attempt INTEGER NOT NULL DEFAULT 0,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL
                    )
                """)
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_jobs_status_priority
                    ON jobs(status, priority DESC, created_at ASC)
                """)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS events (
                        id BIGSERIAL PRIMARY KEY,
                        event_type TEXT NOT NULL,
                        repository TEXT,
                        task_key TEXT,
                        payload_json TEXT NOT NULL,
                        created_at TEXT NOT NULL
                    )
                """)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS webhook_deliveries (
                        delivery_id TEXT PRIMARY KEY,
                        event_name TEXT NOT NULL,
                        repository TEXT,
                        received_at TEXT NOT NULL
                    )
                """)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS workflows (
                        id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        repository TEXT NOT NULL,
                        status TEXT NOT NULL DEFAULT 'pending',
                        metadata_json TEXT NOT NULL DEFAULT '{}',
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL
                    )
                """)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS workflow_tasks (
                        workflow_id TEXT NOT NULL REFERENCES workflows(id)
                            ON DELETE CASCADE,
                        task_id TEXT NOT NULL,
                        title TEXT NOT NULL,
                        payload_json TEXT NOT NULL,
                        status TEXT NOT NULL DEFAULT 'pending',
                        priority DOUBLE PRECISION NOT NULL DEFAULT 0,
                        dependencies_json TEXT NOT NULL DEFAULT '[]',
                        claimed_job_key TEXT,
                        result_json TEXT,
                        attempts INTEGER NOT NULL DEFAULT 0,
                        max_attempts INTEGER NOT NULL DEFAULT 1,
                        estimated_minutes DOUBLE PRECISION NOT NULL DEFAULT 1,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL,
                        PRIMARY KEY(workflow_id, task_id)
                    )
                """)
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_workflow_tasks_status
                    ON workflow_tasks(workflow_id, status, priority DESC)
                """)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS artifacts (
                        id TEXT PRIMARY KEY,
                        workflow_id TEXT NOT NULL REFERENCES workflows(id)
                            ON DELETE CASCADE,
                        task_id TEXT,
                        name TEXT NOT NULL,
                        uri TEXT NOT NULL,
                        sha256 TEXT,
                        metadata_json TEXT NOT NULL DEFAULT '{}',
                        created_at TEXT NOT NULL
                    )
                """)
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_artifacts_workflow
                    ON artifacts(workflow_id, task_id)
                """)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS releases (
                        id TEXT PRIMARY KEY,
                        workflow_id TEXT NOT NULL REFERENCES workflows(id)
                            ON DELETE RESTRICT,
                        artifact_id TEXT NOT NULL REFERENCES artifacts(id)
                            ON DELETE RESTRICT,
                        repository TEXT NOT NULL,
                        source_revision TEXT,
                        workflow_generation INTEGER,
                        validation_json TEXT NOT NULL,
                        metadata_json TEXT NOT NULL DEFAULT '{}',
                        status TEXT NOT NULL,
                        rollback_of TEXT REFERENCES releases(id)
                            ON DELETE RESTRICT,
                        created_at TEXT NOT NULL
                    )
                """)
                cur.execute("""
                    CREATE UNIQUE INDEX IF NOT EXISTS idx_release_promoted_artifact
                    ON releases(artifact_id)
                    WHERE status='promoted'
                """)
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_releases_workflow
                    ON releases(workflow_id, created_at)
                """)
                cur.execute("""
                    CREATE UNIQUE INDEX IF NOT EXISTS idx_release_single_rollback
                    ON releases(rollback_of)
                    WHERE rollback_of IS NOT NULL
                """)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS execution_history (
                        id BIGSERIAL PRIMARY KEY,
                        repository TEXT NOT NULL,
                        task TEXT NOT NULL,
                        worker_id TEXT NOT NULL,
                        duration_seconds DOUBLE PRECISION NOT NULL,
                        succeeded BOOLEAN NOT NULL,
                        capabilities_json TEXT NOT NULL DEFAULT '[]',
                        created_at TEXT NOT NULL
                    )
                """)
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_execution_history_task
                    ON execution_history(repository, task, created_at DESC)
                """)
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_execution_history_worker
                    ON execution_history(worker_id, created_at DESC)
                """)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS result_cache (
                        fingerprint TEXT PRIMARY KEY,
                        repository TEXT NOT NULL,
                        task TEXT NOT NULL,
                        result_json TEXT NOT NULL,
                        artifact_json TEXT NOT NULL DEFAULT '[]',
                        created_at TEXT NOT NULL,
                        last_used_at TEXT NOT NULL,
                        hits INTEGER NOT NULL DEFAULT 0
                    )
                """)
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_result_cache_repo_task
                    ON result_cache(repository, task, last_used_at DESC)
                """)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS speculation_groups (
                        group_id TEXT PRIMARY KEY,
                        canonical_job_key TEXT NOT NULL,
                        winner_job_key TEXT,
                        created_at TEXT NOT NULL,
                        resolved_at TEXT
                    )
                """)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS speculation_members (
                        group_id TEXT NOT NULL REFERENCES speculation_groups(group_id)
                            ON DELETE CASCADE,
                        job_key TEXT NOT NULL,
                        worker_id TEXT,
                        created_at TEXT NOT NULL,
                        PRIMARY KEY(group_id, job_key)
                    )
                """)
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_speculation_members_job
                    ON speculation_members(job_key)
                """)
                cur.execute("""
                    ALTER TABLE workers
                    ADD COLUMN IF NOT EXISTS capacity_json TEXT
                """)
                cur.execute("""
                    INSERT INTO schema_meta(key, value)
                    VALUES('schema_version', %s)
                    ON CONFLICT(key) DO UPDATE SET value=EXCLUDED.value
                """, (str(self.SCHEMA_VERSION),))

    def append_event(
        self,
        db,
        event_type: str,
        payload: dict,
        *,
        repository: str | None = None,
        task_key_value: str | None = None,
    ) -> int:
        with db.cursor() as cur:
            cur.execute(
                """
                INSERT INTO events(
                    event_type, repository, task_key, payload_json, created_at
                )
                VALUES(%s, %s, %s, %s, %s)
                RETURNING id
                """,
                (
                    event_type,
                    repository,
                    task_key_value,
                    json.dumps(payload, ensure_ascii=False, sort_keys=True),
                    _utcnow(),
                ),
            )
            row = cur.fetchone()
        return int(row["id"])

    def events_after(self, event_id: int = 0, limit: int = 100) -> list[dict]:
        with self.connect() as db:
            with db.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, event_type, repository, task_key,
                           payload_json, created_at
                    FROM events
                    WHERE id > %s
                    ORDER BY id ASC
                    LIMIT %s
                    """,
                    (max(0, event_id), max(1, min(limit, 1000))),
                )
                rows = cur.fetchall()
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


class PostgresRuntimeState:
    def __init__(self, backend: PostgresBackend):
        self.backend = backend
        self.records: dict[str, RuntimeRecord] = {}
        self.load()

    @staticmethod
    def _row(row: dict) -> RuntimeRecord:
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
            with db.cursor() as cur:
                cur.execute("SELECT * FROM runtime_records")
                rows = cur.fetchall()
        self.records = {row["key"]: self._row(row) for row in rows}

    def save(self) -> None:
        with self.backend.transaction() as db:
            with db.cursor() as cur:
                for record in self.records.values():
                    cur.execute(
                        """
                        INSERT INTO runtime_records(
                            key, repository, task, status, attempts,
                            consecutive_failures, lease_owner, lease_expires_at,
                            cooldown_until, last_decision, updated_at, priority,
                            interruptible, preempt_requested, checkpoint_ref,
                            started_at
                        )
                        VALUES(
                            %s,%s,%s,%s,%s,%s,%s,%s,
                            %s,%s,%s,%s,%s,%s,%s,%s
                        )
                        ON CONFLICT(key) DO UPDATE SET
                            repository=EXCLUDED.repository,
                            task=EXCLUDED.task,
                            status=EXCLUDED.status,
                            attempts=EXCLUDED.attempts,
                            consecutive_failures=EXCLUDED.consecutive_failures,
                            lease_owner=EXCLUDED.lease_owner,
                            lease_expires_at=EXCLUDED.lease_expires_at,
                            cooldown_until=EXCLUDED.cooldown_until,
                            last_decision=EXCLUDED.last_decision,
                            updated_at=EXCLUDED.updated_at,
                            priority=EXCLUDED.priority,
                            interruptible=EXCLUDED.interruptible,
                            preempt_requested=EXCLUDED.preempt_requested,
                            checkpoint_ref=EXCLUDED.checkpoint_ref,
                            started_at=EXCLUDED.started_at
                        """,
                        (
                            record.key, record.repository, record.task,
                            record.status, record.attempts,
                            record.consecutive_failures, record.lease_owner,
                            record.lease_expires_at, record.cooldown_until,
                            record.last_decision, record.updated_at,
                            record.priority, record.interruptible,
                            record.preempt_requested, record.checkpoint_ref,
                            record.started_at,
                        ),
                    )

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

    def get(self, repository: str, task: str) -> RuntimeRecord:
        key = task_key(repository, task)
        with self.backend.transaction() as db:
            with db.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO runtime_records(key, repository, task, status)
                    VALUES(%s, %s, %s, 'idle')
                    ON CONFLICT(key) DO NOTHING
                    """,
                    (key, repository, task),
                )
                cur.execute(
                    "SELECT * FROM runtime_records WHERE key=%s",
                    (key,),
                )
                row = cur.fetchone()
        record = self._row(row)
        self.records[key] = record
        return record

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
            with db.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO runtime_records(key, repository, task, status)
                    VALUES(%s, %s, %s, 'idle')
                    ON CONFLICT(key) DO NOTHING
                    """,
                    (key, repository, task),
                )
                cur.execute(
                    "SELECT * FROM runtime_records WHERE key=%s FOR UPDATE",
                    (key,),
                )
                row = cur.fetchone()
                current = self._row(row)
                if self.is_leased(current, now):
                    raise RuntimeError("task already leased")
                cur.execute(
                    """
                    UPDATE runtime_records
                    SET lease_owner=%s, lease_expires_at=%s, status='running',
                        started_at=%s, priority=%s, interruptible=%s,
                        preempt_requested=FALSE, updated_at=%s
                    WHERE key=%s
                    """,
                    (
                        owner, expires, now.isoformat(), float(priority),
                        bool(interruptible), now.isoformat(), key,
                    ),
                )
                self.backend.append_event(
                    db,
                    "lease-acquired",
                    {"owner":owner, "lease_expires_at":expires},
                    repository=repository,
                    task_key_value=key,
                )
                cur.execute(
                    "SELECT * FROM runtime_records WHERE key=%s",
                    (key,),
                )
                row = cur.fetchone()
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
            with db.cursor() as cur:
                cur.execute(
                    "SELECT * FROM runtime_records WHERE key=%s FOR UPDATE",
                    (key,),
                )
                row = cur.fetchone()
                if row is None:
                    raise RuntimeError("task has no active lease")
                current = self._row(row)
                if not self.is_leased(current, now):
                    raise RuntimeError("task has no active lease")
                if current.lease_owner != owner:
                    raise RuntimeError("lease owner mismatch")
                expires = (now + timedelta(minutes=minutes)).isoformat()
                cur.execute(
                    """
                    UPDATE runtime_records
                    SET lease_expires_at=%s, updated_at=%s
                    WHERE key=%s
                    """,
                    (expires, now.isoformat(), key),
                )
                cur.execute(
                    "SELECT * FROM runtime_records WHERE key=%s",
                    (key,),
                )
                row = cur.fetchone()
        record = self._row(row)
        self.records[key] = record
        return record

    def release_lease(self, repository: str, task: str) -> RuntimeRecord:
        key = task_key(repository, task)
        now = _utcnow()
        with self.backend.transaction() as db:
            with db.cursor() as cur:
                cur.execute(
                    "SELECT * FROM runtime_records WHERE key=%s FOR UPDATE",
                    (key,),
                )
                row = cur.fetchone()
                if row is None:
                    raise KeyError(key)
                status = (
                    "idle"
                    if row["status"] in {"running", "preempt-requested"}
                    else row["status"]
                )
                cur.execute(
                    """
                    UPDATE runtime_records
                    SET lease_owner=NULL, lease_expires_at=NULL,
                        status=%s, updated_at=%s
                    WHERE key=%s
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
                cur.execute(
                    "SELECT * FROM runtime_records WHERE key=%s",
                    (key,),
                )
                row = cur.fetchone()
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
                cooldown = (
                    now + timedelta(minutes=cooldown_minutes)
                ).isoformat()
        elif decision == "replan":
            status = "replan"
            cooldown = (
                now + timedelta(minutes=max(10, cooldown_minutes // 2))
            ).isoformat()

        with self.backend.transaction() as db:
            with db.cursor() as cur:
                cur.execute(
                    """
                    UPDATE runtime_records
                    SET attempts=%s, consecutive_failures=%s,
                        lease_owner=NULL, lease_expires_at=NULL,
                        last_decision=%s, status=%s, cooldown_until=%s,
                        updated_at=%s
                    WHERE key=%s
                    """,
                    (
                        attempts, failures, decision, status, cooldown,
                        now.isoformat(), current.key,
                    ),
                )
                self.backend.append_event(
                    db,
                    "task-outcome",
                    {"decision":decision, "status":status},
                    repository=repository,
                    task_key_value=current.key,
                )
                cur.execute(
                    "SELECT * FROM runtime_records WHERE key=%s",
                    (current.key,),
                )
                row = cur.fetchone()
        record = self._row(row)
        self.records[current.key] = record
        return record


class PostgresWorkerRegistry:
    def __init__(self, backend: PostgresBackend):
        self.backend = backend
        self.workers: dict[str, Worker] = {}
        self.load()

    @staticmethod
    def _row(row: dict) -> Worker:
        return Worker(
            worker_id=row["worker_id"],
            capabilities=json.loads(row["capabilities_json"]),
            max_concurrency=row["max_concurrency"],
            active_tasks=row["active_tasks"],
            status=row["status"],
            last_heartbeat=row["last_heartbeat"],
            capacity=(
                json.loads(row["capacity_json"])
                if row.get("capacity_json")
                else None
            ),
        )

    def load(self) -> None:
        with self.backend.connect() as db:
            with db.cursor() as cur:
                cur.execute("SELECT * FROM workers")
                rows = cur.fetchall()
        self.workers = {row["worker_id"]: self._row(row) for row in rows}

    def save(self) -> None:
        for worker in list(self.workers.values()):
            self.register(
                worker.worker_id,
                worker.capabilities,
                worker.max_concurrency,
            )
            with self.backend.transaction() as db:
                with db.cursor() as cur:
                    cur.execute(
                        """
                        UPDATE workers
                        SET active_tasks=%s, status=%s, last_heartbeat=%s,
                            capacity_json=%s
                        WHERE worker_id=%s
                        """,
                        (
                            worker.active_tasks, worker.status,
                            worker.last_heartbeat,
                            (
                                json.dumps(worker.capacity, ensure_ascii=False)
                                if worker.capacity is not None
                                else None
                            ),
                            worker.worker_id,
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
            with db.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO workers(
                        worker_id, capabilities_json, max_concurrency,
                        active_tasks, status, last_heartbeat
                    )
                    VALUES(%s,%s,%s,0,'online',%s)
                    ON CONFLICT(worker_id) DO UPDATE SET
                        capabilities_json=EXCLUDED.capabilities_json,
                        max_concurrency=EXCLUDED.max_concurrency,
                        status='online',
                        last_heartbeat=EXCLUDED.last_heartbeat
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
                    {
                        "worker_id":worker_id,
                        "capabilities":sorted(set(capabilities)),
                    },
                )
                cur.execute(
                    "SELECT * FROM workers WHERE worker_id=%s",
                    (worker_id,),
                )
                row = cur.fetchone()
        worker = self._row(row)
        self.workers[worker_id] = worker
        return worker

    def heartbeat(
        self,
        worker_id: str,
        active_tasks: int | None = None,
        *,
        capacity: dict | None = None,
    ) -> Worker:
        now = _utcnow()
        normalized_capacity = (
            _capacity_snapshot(capacity)
            if capacity is not None
            else None
        )
        with self.backend.transaction() as db:
            with db.cursor() as cur:
                cur.execute(
                    "SELECT * FROM workers WHERE worker_id=%s FOR UPDATE",
                    (worker_id,),
                )
                row = cur.fetchone()
                if row is None:
                    raise KeyError(worker_id)
                active = (
                    row["active_tasks"]
                    if active_tasks is None
                    else max(0, active_tasks)
                )
                current_capacity = row.get("capacity_json")
                capacity_json = (
                    json.dumps(normalized_capacity, ensure_ascii=False)
                    if normalized_capacity is not None
                    else current_capacity
                )
                cur.execute(
                    """
                    UPDATE workers
                    SET active_tasks=%s, status='online', last_heartbeat=%s,
                        capacity_json=%s
                    WHERE worker_id=%s
                    """,
                    (active, now, capacity_json, worker_id),
                )
                cur.execute(
                    "SELECT * FROM workers WHERE worker_id=%s",
                    (worker_id,),
                )
                row = cur.fetchone()
        worker = self._row(row)
        self.workers[worker_id] = worker
        return worker

    def adjust_active_tasks(self, worker_id: str, delta: int) -> Worker:
        with self.backend.transaction() as db:
            with db.cursor() as cur:
                cur.execute(
                    "SELECT active_tasks FROM workers WHERE worker_id=%s FOR UPDATE",
                    (worker_id,),
                )
                row = cur.fetchone()
                if row is None:
                    raise KeyError(worker_id)
                active = max(0, int(row["active_tasks"]) + int(delta))
                cur.execute(
                    "UPDATE workers SET active_tasks=%s WHERE worker_id=%s",
                    (active, worker_id),
                )
                cur.execute(
                    "SELECT * FROM workers WHERE worker_id=%s",
                    (worker_id,),
                )
                row = cur.fetchone()
        worker = self._row(row)
        self.workers[worker_id] = worker
        return worker

    def detect_dead(self, timeout_seconds: int = 120) -> list[Worker]:
        self.load()
        now = datetime.now(timezone.utc)
        dead = []
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
                    with db.cursor() as cur:
                        cur.execute(
                            "UPDATE workers SET status='dead' WHERE worker_id=%s",
                            (worker.worker_id,),
                        )
                worker.status = "dead"
                dead.append(worker)
        self.load()
        return dead

    def available(self) -> list[Worker]:
        self.load()
        return [
            w for w in self.workers.values()
            if w.status == "online" and w.active_tasks < w.max_concurrency
        ]


class PostgresClaimStore:
    def __init__(self, backend: PostgresBackend):
        self.backend = backend
        self.claims: dict[str, ClaimRecord] = {}
        self.load()

    @staticmethod
    def _row(row: dict) -> ClaimRecord:
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
            with db.cursor() as cur:
                cur.execute("SELECT * FROM claims")
                rows = cur.fetchall()
        self.claims = {row["key"]: self._row(row) for row in rows}

    def save(self) -> None:
        with self.backend.transaction() as db:
            with db.cursor() as cur:
                for claim in self.claims.values():
                    cur.execute(
                        """
                        INSERT INTO claims(
                            key, worker_id, repository, task, status,
                            claimed_at, ack_deadline, completed_at
                        )
                        VALUES(%s,%s,%s,%s,%s,%s,%s,%s)
                        ON CONFLICT(key) DO UPDATE SET
                            worker_id=EXCLUDED.worker_id,
                            repository=EXCLUDED.repository,
                            task=EXCLUDED.task,
                            status=EXCLUDED.status,
                            claimed_at=EXCLUDED.claimed_at,
                            ack_deadline=EXCLUDED.ack_deadline,
                            completed_at=EXCLUDED.completed_at
                        """,
                        (
                            claim.key, claim.worker_id, claim.repository,
                            claim.task, claim.status, claim.claimed_at,
                            claim.ack_deadline, claim.completed_at,
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
        deadline = (
            now + timedelta(seconds=ack_timeout_seconds)
        ).isoformat()
        with self.backend.transaction() as db:
            with db.cursor() as cur:
                cur.execute(
                    "SELECT * FROM claims WHERE key=%s FOR UPDATE",
                    (key,),
                )
                row = cur.fetchone()
                if row is not None and row["status"] in {
                    "claimed", "acked", "completed"
                }:
                    raise RuntimeError(f"job already {row['status']}")
                cur.execute(
                    """
                    INSERT INTO claims(
                        key, worker_id, repository, task, status,
                        claimed_at, ack_deadline, completed_at
                    )
                    VALUES(%s,%s,%s,%s,'claimed',%s,%s,NULL)
                    ON CONFLICT(key) DO UPDATE SET
                        worker_id=EXCLUDED.worker_id,
                        repository=EXCLUDED.repository,
                        task=EXCLUDED.task,
                        status='claimed',
                        claimed_at=EXCLUDED.claimed_at,
                        ack_deadline=EXCLUDED.ack_deadline,
                        completed_at=NULL
                    """,
                    (
                        key, worker_id, repository, task,
                        now.isoformat(), deadline,
                    ),
                )
                cur.execute(
                    "SELECT * FROM claims WHERE key=%s",
                    (key,),
                )
                row = cur.fetchone()
        claim = self._row(row)
        self.claims[key] = claim
        return claim

    def ack(self, key: str, worker_id: str) -> ClaimRecord:
        with self.backend.transaction() as db:
            with db.cursor() as cur:
                cur.execute(
                    "SELECT * FROM claims WHERE key=%s FOR UPDATE",
                    (key,),
                )
                row = cur.fetchone()
                if row is None:
                    raise KeyError(key)
                if row["worker_id"] != worker_id:
                    raise RuntimeError("claim owner mismatch")
                if row["status"] != "completed":
                    cur.execute(
                        "UPDATE claims SET status='acked' WHERE key=%s",
                        (key,),
                    )
                cur.execute(
                    "SELECT * FROM claims WHERE key=%s",
                    (key,),
                )
                row = cur.fetchone()
        claim = self._row(row)
        self.claims[key] = claim
        return claim

    def complete(self, key: str, worker_id: str) -> ClaimRecord:
        now = _utcnow()
        with self.backend.transaction() as db:
            with db.cursor() as cur:
                cur.execute(
                    "SELECT * FROM claims WHERE key=%s FOR UPDATE",
                    (key,),
                )
                row = cur.fetchone()
                if row is None:
                    raise KeyError(key)
                if row["worker_id"] != worker_id:
                    raise RuntimeError("claim owner mismatch")
                cur.execute(
                    """
                    UPDATE claims
                    SET status='completed', completed_at=%s
                    WHERE key=%s
                    """,
                    (now, key),
                )
                cur.execute(
                    "SELECT * FROM claims WHERE key=%s",
                    (key,),
                )
                row = cur.fetchone()
        claim = self._row(row)
        self.claims[key] = claim
        return claim

    def expired_unacked(self) -> list[ClaimRecord]:
        now = _utcnow()
        with self.backend.connect() as db:
            with db.cursor() as cur:
                cur.execute(
                    """
                    SELECT * FROM claims
                    WHERE status='claimed' AND ack_deadline <= %s
                    """,
                    (now,),
                )
                rows = cur.fetchall()
        return [self._row(row) for row in rows]


class PostgresJobQueue:
    def __init__(self, backend: PostgresBackend):
        self.backend = backend

    @staticmethod
    def _job_dict(row: dict) -> dict:
        return {
            "key":row["key"],
            "repository":row["repository"],
            "task":row["task"],
            "payload":json.loads(row["payload_json"]),
            "priority":row["priority"],
            "status":row["status"],
            "assigned_worker":row["assigned_worker"],
            "claimed_by":row["claimed_by"],
            "claimed_at":row["claimed_at"],
            "ack_deadline":row["ack_deadline"],
            "completed_at":row["completed_at"],
            "delivery_attempt":row["delivery_attempt"],
            "created_at":row["created_at"],
            "updated_at":row["updated_at"],
        }

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
            "idempotency_key":key,
            "handoff":handoff,
        }
        with self.backend.transaction() as db:
            with db.cursor() as cur:
                cur.execute(
                    "SELECT status FROM jobs WHERE key=%s FOR UPDATE",
                    (key,),
                )
                existing = cur.fetchone()
                if (
                    existing is not None
                    and existing["status"] not in {"failed", "dead-letter"}
                ):
                    raise RuntimeError(f"job already {existing['status']}")
                cur.execute(
                    """
                    INSERT INTO jobs(
                        key, repository, task, payload_json, priority, status,
                        assigned_worker, claimed_by, claimed_at, ack_deadline,
                        completed_at, delivery_attempt, created_at, updated_at
                    )
                    VALUES(
                        %s,%s,%s,%s,%s,'queued',
                        %s,NULL,NULL,NULL,NULL,0,%s,%s
                    )
                    ON CONFLICT(key) DO UPDATE SET
                        payload_json=EXCLUDED.payload_json,
                        priority=EXCLUDED.priority,
                        status='queued',
                        assigned_worker=EXCLUDED.assigned_worker,
                        claimed_by=NULL,
                        claimed_at=NULL,
                        ack_deadline=NULL,
                        completed_at=NULL,
                        updated_at=EXCLUDED.updated_at
                    """,
                    (
                        key, repository, task,
                        json.dumps(normalized, ensure_ascii=False),
                        priority, payload.get("worker_id"), now, now,
                    ),
                )
                self.backend.append_event(
                    db,
                    "job-enqueued",
                    {"key":key, "priority":priority},
                    repository=repository,
                    task_key_value=key,
                )
                cur.execute(
                    "SELECT * FROM jobs WHERE key=%s",
                    (key,),
                )
                row = cur.fetchone()
        return self._job_dict(row)

    def get(self, key: str) -> dict:
        with self.backend.connect() as db:
            with db.cursor() as cur:
                cur.execute("SELECT * FROM jobs WHERE key=%s", (key,))
                row = cur.fetchone()
        if row is None:
            raise KeyError(key)
        return self._job_dict(row)


    def peek_candidates(
        self,
        *,
        worker_id: str | None = None,
        limit: int = 100,
    ) -> list[dict]:
        with self.backend.connect() as db:
            with db.cursor() as cur:
                if worker_id is None:
                    cur.execute(
                        """
                        SELECT * FROM jobs
                        WHERE status='queued'
                        ORDER BY priority DESC, created_at ASC
                        LIMIT %s
                        """,
                        (max(1, min(limit, 1000)),),
                    )
                else:
                    cur.execute(
                        """
                        SELECT * FROM jobs
                        WHERE status='queued'
                          AND (assigned_worker IS NULL OR assigned_worker=%s)
                        ORDER BY priority DESC, created_at ASC
                        LIMIT %s
                        """,
                        (worker_id, max(1, min(limit, 1000))),
                    )
                rows = cur.fetchall()
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
            with db.cursor() as cur:
                cur.execute(
                    """
                    SELECT * FROM jobs
                    WHERE key=%s AND status='queued'
                      AND (assigned_worker IS NULL OR assigned_worker=%s)
                    FOR UPDATE SKIP LOCKED
                    """,
                    (key, worker_id),
                )
                row = cur.fetchone()
                if row is None:
                    return None
                cur.execute(
                    """
                    UPDATE jobs
                    SET status='claimed', claimed_by=%s, claimed_at=%s,
                        ack_deadline=%s,
                        delivery_attempt=delivery_attempt+1,
                        updated_at=%s
                    WHERE key=%s AND status='queued'
                    """,
                    (
                        worker_id,
                        now.isoformat(),
                        deadline,
                        now.isoformat(),
                        key,
                    ),
                )
                self.backend.append_event(
                    db,
                    "job-claimed",
                    {"worker_id":worker_id},
                    repository=row["repository"],
                    task_key_value=key,
                )
                cur.execute(
                    "SELECT * FROM jobs WHERE key=%s",
                    (key,),
                )
                claimed = cur.fetchone()
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
        deadline = (
            now + timedelta(seconds=ack_timeout_seconds)
        ).isoformat()
        with self.backend.transaction() as db:
            with db.cursor() as cur:
                cur.execute(
                    """
                    SELECT * FROM jobs
                    WHERE status='queued'
                      AND (assigned_worker IS NULL OR assigned_worker=%s)
                    ORDER BY priority DESC, created_at ASC
                    FOR UPDATE SKIP LOCKED
                    LIMIT 100
                    """,
                    (worker_id,),
                )
                rows = cur.fetchall()
                chosen = None
                for row in rows:
                    payload = json.loads(row["payload_json"])
                    required = set(payload.get("required_capabilities", []))
                    if required.issubset(capabilities_set):
                        chosen = row
                        break
                if chosen is None:
                    return None
                cur.execute(
                    """
                    UPDATE jobs
                    SET status='claimed', claimed_by=%s, claimed_at=%s,
                        ack_deadline=%s,
                        delivery_attempt=delivery_attempt+1,
                        updated_at=%s
                    WHERE key=%s
                    """,
                    (
                        worker_id, now.isoformat(), deadline,
                        now.isoformat(), chosen["key"],
                    ),
                )
                self.backend.append_event(
                    db,
                    "job-claimed",
                    {"worker_id":worker_id},
                    repository=chosen["repository"],
                    task_key_value=chosen["key"],
                )
                cur.execute(
                    "SELECT * FROM jobs WHERE key=%s",
                    (chosen["key"],),
                )
                row = cur.fetchone()
        return self._job_dict(row)

    def ack(self, key: str, worker_id: str) -> dict:
        return self._transition(
            key, worker_id, {"claimed"}, "acked", "job-acked"
        )

    def complete(self, key: str, worker_id: str) -> dict:
        return self._transition(
            key, worker_id, {"claimed", "acked"},
            "completed", "job-completed", completed=True
        )

    def fail(self, key: str, worker_id: str, reason: str) -> dict:
        return self._transition(
            key, worker_id, {"claimed", "acked"},
            "failed", "job-failed", extra={"reason":reason}
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
            with db.cursor() as cur:
                cur.execute(
                    "SELECT * FROM jobs WHERE key=%s FOR UPDATE",
                    (key,),
                )
                row = cur.fetchone()
                if row is None:
                    raise KeyError(key)
                if row["claimed_by"] != worker_id:
                    raise RuntimeError("job claim owner mismatch")
                if row["status"] not in allowed_statuses:
                    raise RuntimeError(
                        f"job cannot transition from {row['status']}"
                    )
                cur.execute(
                    """
                    UPDATE jobs
                    SET status=%s, completed_at=%s, updated_at=%s
                    WHERE key=%s
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
                cur.execute(
                    "SELECT * FROM jobs WHERE key=%s",
                    (key,),
                )
                row = cur.fetchone()
        return self._job_dict(row)

    def recover_expired(self, *, max_attempts: int = 3) -> list[dict]:
        now = _utcnow()
        actions = []
        with self.backend.transaction() as db:
            with db.cursor() as cur:
                cur.execute(
                    """
                    SELECT * FROM jobs
                    WHERE status='claimed' AND ack_deadline <= %s
                    FOR UPDATE SKIP LOCKED
                    """,
                    (now,),
                )
                rows = cur.fetchall()
                for row in rows:
                    target = (
                        "dead-letter"
                        if int(row["delivery_attempt"]) >= max_attempts
                        else "queued"
                    )
                    cur.execute(
                        """
                        UPDATE jobs
                        SET status=%s, claimed_by=NULL, claimed_at=NULL,
                            ack_deadline=NULL, updated_at=%s
                        WHERE key=%s
                        """,
                        (target, now, row["key"]),
                    )
                    action = {
                        "key":row["key"],
                        "action":target,
                        "delivery_attempt":row["delivery_attempt"],
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
