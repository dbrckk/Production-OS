from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from pathlib import Path


RETENTION_SPECS = (
    ("worker_logs", "worker_log_events", "created_at", "PRODUCTION_OS_RETENTION_WORKER_LOG_DAYS", 30),
    ("api_usage", "api_usage_events", "occurred_at", "PRODUCTION_OS_RETENTION_API_USAGE_DAYS", 90),
    ("executions", "job_executions", "created_at", "PRODUCTION_OS_RETENTION_EXECUTION_DAYS", 90),
    ("control_audit", "control_audit_events", "requested_at", "PRODUCTION_OS_RETENTION_CONTROL_AUDIT_DAYS", 180),
    ("remediations", "dashboard_remediation_events", "requested_at", "PRODUCTION_OS_RETENTION_REMEDIATION_DAYS", 180),
    ("repository_snapshots", "project_repository_snapshots", "captured_at", "PRODUCTION_OS_RETENTION_SNAPSHOT_DAYS", 90),
    ("progress_snapshots", "project_progress_snapshots", "captured_at", "PRODUCTION_OS_RETENTION_SNAPSHOT_DAYS", 90),
    ("events", "events", "created_at", "PRODUCTION_OS_RETENTION_EVENT_DAYS", 90),
)


def _parse_time(value):
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _retention_days(env_name: str, default: int) -> int:
    raw = str(os.getenv(env_name) or "").strip()
    if not raw:
        return default
    try:
        value = int(raw)
    except ValueError:
        return default
    return value if value > 0 else default


def _database_size_bytes(backend) -> int | None:
    if backend.__class__.__name__.startswith("Postgres"):
        with backend.connect() as db:
            row = db.execute(
                "SELECT pg_database_size(current_database()) AS bytes"
            ).fetchone()
        if not row:
            return None
        value = row["bytes"]
        return int(value) if value is not None else None

    path = getattr(backend, "path", None)
    if path is None:
        return None
    base = Path(path)
    total = 0
    found = False
    for candidate in (
        base,
        Path(str(base) + "-wal"),
        Path(str(base) + "-shm"),
    ):
        try:
            if candidate.exists():
                total += int(candidate.stat().st_size)
                found = True
        except OSError:
            continue
    return total if found else None


def _table_snapshot(
    backend,
    *,
    label: str,
    table: str,
    timestamp_column: str,
    retention_days: int,
    now: datetime,
) -> dict:
    with backend.connect() as db:
        rows = db.execute(
            f"SELECT {timestamp_column} AS timestamp FROM {table}"
        ).fetchall()

    valid: list[datetime] = []
    invalid = 0
    for row in rows:
        parsed = _parse_time(row["timestamp"])
        if parsed is None:
            invalid += 1
            continue
        valid.append(parsed)

    cutoff = now - timedelta(days=retention_days)
    candidates = sum(value < cutoff for value in valid)
    return {
        "name":label,
        "table":table,
        "rows":len(rows),
        "valid_timestamps":len(valid),
        "invalid_timestamps":invalid,
        "oldest_at":min(valid).isoformat() if valid else None,
        "newest_at":max(valid).isoformat() if valid else None,
        "retention_days":retention_days,
        "cutoff_at":cutoff.isoformat(),
        "candidate_rows":candidates,
    }


def storage_maintenance_snapshot(
    backend,
    *,
    now: datetime | None = None,
) -> dict:
    current = now or datetime.now(timezone.utc)
    if current.tzinfo is None:
        current = current.replace(tzinfo=timezone.utc)
    current = current.astimezone(timezone.utc)

    tables = []
    errors = []
    for label, table, timestamp_column, env_name, default_days in RETENTION_SPECS:
        try:
            tables.append(
                _table_snapshot(
                    backend,
                    label=label,
                    table=table,
                    timestamp_column=timestamp_column,
                    retention_days=_retention_days(env_name, default_days),
                    now=current,
                )
            )
        except Exception:
            errors.append({"name":label, "error":"unavailable"})

    total_candidates = sum(
        int(row.get("candidate_rows") or 0)
        for row in tables
    )
    total_rows = sum(int(row.get("rows") or 0) for row in tables)
    try:
        size_bytes = _database_size_bytes(backend)
    except Exception:
        size_bytes = None
        errors.append({"name":"database_size", "error":"unavailable"})

    status = (
        "unknown"
        if errors
        else ("attention" if total_candidates > 0 else "healthy")
    )
    return {
        "status":status,
        "backend_kind":(
            "postgres"
            if backend.__class__.__name__.startswith("Postgres")
            else "sqlite"
        ),
        "database_size_bytes":size_bytes,
        "total_rows":total_rows,
        "candidate_rows":total_candidates,
        "tables":tables,
        "errors":errors,
        "generated_at":current.isoformat(),
    }
