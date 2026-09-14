from __future__ import annotations

from .postgres_backend import (
    PostgresBackend,
    PostgresClaimStore,
    PostgresJobQueue,
    PostgresRuntimeState,
    PostgresWorkerRegistry,
)
from .sqlite_backend import (
    SQLiteBackend,
    SQLiteClaimStore,
    SQLiteJobQueue,
    SQLiteRuntimeState,
    SQLiteWorkerRegistry,
)


def is_postgres(location: str) -> bool:
    return location.startswith("postgresql://") or location.startswith("postgres://")


def open_backend(location: str):
    if is_postgres(location):
        return PostgresBackend(location)
    return SQLiteBackend(location)


def runtime_state_for(backend):
    if isinstance(backend, PostgresBackend):
        return PostgresRuntimeState(backend)
    return SQLiteRuntimeState(backend)


def worker_registry_for(backend):
    if isinstance(backend, PostgresBackend):
        return PostgresWorkerRegistry(backend)
    return SQLiteWorkerRegistry(backend)


def claim_store_for(backend):
    if isinstance(backend, PostgresBackend):
        return PostgresClaimStore(backend)
    return SQLiteClaimStore(backend)


def job_queue_for(backend):
    if isinstance(backend, PostgresBackend):
        return PostgresJobQueue(backend)
    return SQLiteJobQueue(backend)
