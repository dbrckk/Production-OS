import os

import pytest

from production_os.postgres_backend import PostgresBackend
from tests.test_dashboard_store import (
    REQUIRED_EXECUTION_COLUMNS,
    REQUIRED_TABLES,
)


DSN = os.getenv("PRODUCTION_OS_TEST_POSTGRES")

pytestmark = pytest.mark.skipif(
    not DSN,
    reason="PRODUCTION_OS_TEST_POSTGRES not configured",
)


def test_postgres_schema_v9_matches_dashboard_contract():
    backend = PostgresBackend(DSN)

    with backend.connect() as db:
        with db.cursor() as cur:
            cur.execute(
                "SELECT value FROM schema_meta WHERE key='schema_version'"
            )
            version = cur.fetchone()["value"]
            cur.execute(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema='public'
                """
            )
            tables = {row["table_name"] for row in cur.fetchall()}
            cur.execute(
                """
                SELECT column_name
                FROM information_schema.columns
                WHERE table_schema='public'
                  AND table_name='job_executions'
                """
            )
            execution_columns = {
                row["column_name"] for row in cur.fetchall()
            }

    assert version == "9"
    assert REQUIRED_TABLES <= tables
    assert REQUIRED_EXECUTION_COLUMNS <= execution_columns


def test_postgres_schema_v9_initialization_is_idempotent():
    backend = PostgresBackend(DSN)
    PostgresBackend(DSN)

    with backend.connect() as db:
        with db.cursor() as cur:
            cur.execute(
                "SELECT key, value FROM schema_meta WHERE key='schema_version'"
            )
            rows = cur.fetchall()

    assert rows == [{"key": "schema_version", "value": "9"}]
