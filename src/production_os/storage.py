from __future__ import annotations

import re

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


# Recognize libpq's reserved connection keywords without requiring the optional
# PostgreSQL driver. Parsing and validation remain the driver's responsibility;
# malformed connection strings must never become SQLite filenames.
_POSTGRES_CONNINFO_KEYS = frozenset("""
    service user password passfile channel_binding connect_timeout dbname host
    hostaddr port client_encoding options application_name fallback_application_name
    keepalives keepalives_idle keepalives_interval keepalives_count tcp_user_timeout
    sslmode sslnegotiation sslcompression sslcert sslkey sslcertmode sslpassword
    sslrootcert sslcrl sslcrldir sslsni requirepeer require_auth min_protocol_version
    max_protocol_version ssl_min_protocol_version ssl_max_protocol_version gssencmode
    krbsrvname gsslib gssdelegation replication target_session_attrs load_balance_hosts
    scram_client_key scram_server_key oauth_issuer oauth_client_id oauth_client_secret
    oauth_scope sslkeylogfile
""".split())


def is_postgres(location: str) -> bool:
    location = str(location).strip()
    if location.startswith(("postgresql://", "postgres://")):
        return True
    keyword = re.match(r"([a-z_]+)\s*=", location)
    return keyword is not None and keyword.group(1) in _POSTGRES_CONNINFO_KEYS


def open_backend(location: str):
    if is_postgres(location):
        return PostgresBackend(str(location).strip())
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
