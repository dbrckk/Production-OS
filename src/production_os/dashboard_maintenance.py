from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path


TERMINAL_EXECUTION_STATUSES = {"succeeded", "failed", "cancelled"}


@dataclass(frozen=True)
class RetentionSpec:
    label: str
    table: str
    timestamp_column: str
    env_name: str
    default_days: int
    key_column: str = "id"
    mode: str = "prunable"


RETENTION_SPECS = (
    RetentionSpec(
        "api_usage",
        "api_usage_events",
        "occurred_at",
        "PRODUCTION_OS_RETENTION_API_USAGE_DAYS",
        90,
    ),
    RetentionSpec(
        "worker_logs",
        "worker_log_events",
        "created_at",
        "PRODUCTION_OS_RETENTION_WORKER_LOG_DAYS",
        30,
    ),
    RetentionSpec(
        "executions",
        "job_executions",
        "created_at",
        "PRODUCTION_OS_RETENTION_EXECUTION_DAYS",
        90,
        mode="execution",
    ),
    RetentionSpec(
        "control_audit",
        "control_audit_events",
        "requested_at",
        "PRODUCTION_OS_RETENTION_CONTROL_AUDIT_DAYS",
        180,
    ),
    RetentionSpec(
        "repository_snapshots",
        "project_repository_snapshots",
        "captured_at",
        "PRODUCTION_OS_RETENTION_SNAPSHOT_DAYS",
        90,
    ),
    RetentionSpec(
        "progress_snapshots",
        "project_progress_snapshots",
        "captured_at",
        "PRODUCTION_OS_RETENTION_SNAPSHOT_DAYS",
        90,
    ),
    RetentionSpec(
        "events",
        "events",
        "created_at",
        "PRODUCTION_OS_RETENTION_EVENT_DAYS",
        90,
    ),
    RetentionSpec(
        "remediations",
        "dashboard_remediation_events",
        "requested_at",
        "PRODUCTION_OS_RETENTION_REMEDIATION_DAYS",
        180,
        mode="protected",
    ),
)


class RetentionCandidateConflict(RuntimeError):
    def __init__(self, expected: int, actual: int):
        super().__init__(
            f"retention candidate count changed: expected {expected}, actual {actual}"
        )
        self.expected = expected
        self.actual = actual


def _is_postgres(backend) -> bool:
    return backend.__class__.__name__.startswith("Postgres")


def _execute(db, backend, statement: str, params: tuple = ()):
    sql = statement.replace("?", "%s") if _is_postgres(backend) else statement
    return db.execute(sql, params)


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
    if _is_postgres(backend):
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


def _select_columns(spec: RetentionSpec) -> str:
    columns = [
        f"{spec.key_column} AS row_key",
        f"{spec.timestamp_column} AS timestamp",
    ]
    if spec.mode == "execution":
        columns.append("status AS row_status")
    return ", ".join(columns)


def _old_row_disposition(
    spec: RetentionSpec,
    row,
    *,
    cutoff: datetime,
) -> str:
    parsed = _parse_time(row["timestamp"])
    if parsed is None:
        return "invalid"
    if parsed >= cutoff:
        return "recent"
    if spec.mode == "protected":
        return "protected"
    if spec.mode == "execution":
        status = str(row["row_status"] or "")
        return (
            "prunable"
            if status in TERMINAL_EXECUTION_STATUSES
            else "protected"
        )
    return "prunable"


def _table_snapshot(
    backend,
    *,
    spec: RetentionSpec,
    retention_days: int,
    now: datetime,
) -> dict:
    cutoff = now - timedelta(days=retention_days)
    total = 0
    valid_count = 0
    invalid = 0
    prunable = 0
    protected = 0
    oldest = None
    newest = None
    with backend.connect() as db:
        cursor = db.execute(
            f"SELECT {_select_columns(spec)} FROM {spec.table}"
        )
        for row in cursor:
            total += 1
            parsed = _parse_time(row["timestamp"])
            if parsed is None:
                invalid += 1
                continue
            valid_count += 1
            if oldest is None or parsed < oldest:
                oldest = parsed
            if newest is None or parsed > newest:
                newest = parsed
            disposition = _old_row_disposition(
                spec,
                row,
                cutoff=cutoff,
            )
            if disposition == "prunable":
                prunable += 1
            elif disposition == "protected":
                protected += 1

    return {
        "name":spec.label,
        "table":spec.table,
        "rows":total,
        "valid_timestamps":valid_count,
        "invalid_timestamps":invalid,
        "oldest_at":oldest.isoformat() if oldest is not None else None,
        "newest_at":newest.isoformat() if newest is not None else None,
        "retention_days":retention_days,
        "cutoff_at":cutoff.isoformat(),
        "candidate_rows":prunable + protected,
        "prunable_candidate_rows":prunable,
        "protected_candidate_rows":protected,
        "protected":spec.mode == "protected",
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
    for spec in RETENTION_SPECS:
        try:
            tables.append(
                _table_snapshot(
                    backend,
                    spec=spec,
                    retention_days=_retention_days(
                        spec.env_name,
                        spec.default_days,
                    ),
                    now=current,
                )
            )
        except Exception:
            errors.append({"name":spec.label, "error":"unavailable"})

    total_candidates = sum(
        int(row.get("candidate_rows") or 0)
        for row in tables
    )
    prunable_candidates = sum(
        int(row.get("prunable_candidate_rows") or 0)
        for row in tables
    )
    protected_candidates = sum(
        int(row.get("protected_candidate_rows") or 0)
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
        "backend_kind":"postgres" if _is_postgres(backend) else "sqlite",
        "database_size_bytes":size_bytes,
        "total_rows":total_rows,
        "candidate_rows":total_candidates,
        "prunable_candidate_rows":prunable_candidates,
        "protected_candidate_rows":protected_candidates,
        "tables":tables,
        "errors":errors,
        "generated_at":current.isoformat(),
    }


def _collect_prunable_keys(
    db,
    backend,
    *,
    now: datetime,
) -> dict[str, list[object]]:
    selected: dict[str, list[object]] = {}
    for spec in RETENTION_SPECS:
        if spec.mode == "protected":
            continue
        cutoff = now - timedelta(
            days=_retention_days(spec.env_name, spec.default_days)
        )
        keys: list[object] = []
        cursor = _execute(
            db,
            backend,
            f"SELECT {_select_columns(spec)} FROM {spec.table}",
        )
        for row in cursor:
            if _old_row_disposition(spec, row, cutoff=cutoff) == "prunable":
                keys.append(row["row_key"])
        selected[spec.label] = keys
    return selected


def prune_expired_history(
    backend,
    *,
    expected_candidate_rows: int,
    now: datetime | None = None,
) -> dict:
    if (
        isinstance(expected_candidate_rows, bool)
        or not isinstance(expected_candidate_rows, int)
        or expected_candidate_rows < 0
    ):
        raise ValueError(
            "expected_candidate_rows must be a non-negative integer"
        )

    current = now or datetime.now(timezone.utc)
    if current.tzinfo is None:
        current = current.replace(tzinfo=timezone.utc)
    current = current.astimezone(timezone.utc)

    deleted: dict[str, int] = {}
    with backend.transaction() as db:
        keys_by_label = _collect_prunable_keys(
            db,
            backend,
            now=current,
        )
        actual = sum(len(keys) for keys in keys_by_label.values())
        if actual != expected_candidate_rows:
            raise RetentionCandidateConflict(
                expected_candidate_rows,
                actual,
            )

        spec_by_label = {spec.label:spec for spec in RETENTION_SPECS}
        for label, keys in keys_by_label.items():
            spec = spec_by_label[label]
            count = 0
            for offset in range(0, len(keys), 200):
                chunk = keys[offset:offset + 200]
                if not chunk:
                    continue
                placeholders = ",".join("?" for _ in chunk)
                cursor = _execute(
                    db,
                    backend,
                    f"DELETE FROM {spec.table} "
                    f"WHERE {spec.key_column} IN ({placeholders})",
                    tuple(chunk),
                )
                if cursor.rowcount is not None and cursor.rowcount >= 0:
                    count += int(cursor.rowcount)
            deleted[label] = count

        deleted_total = sum(deleted.values())
        if deleted_total != actual:
            raise RuntimeError(
                "retention deletion count changed during cleanup"
            )

    return {
        "deleted_rows":sum(deleted.values()),
        "deleted_by_table":deleted,
        "expected_candidate_rows":expected_candidate_rows,
        "completed_at":current.isoformat(),
    }
