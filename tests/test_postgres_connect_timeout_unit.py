import production_os.postgres_backend as postgres_backend_module
from production_os.postgres_backend import PostgresBackend


def test_postgres_connect_uses_bounded_connect_timeout(monkeypatch):
    calls = []
    sentinel = object()

    class FakePsycopg:
        @staticmethod
        def connect(*args, **kwargs):
            calls.append((args, kwargs))
            return sentinel

    monkeypatch.setattr(postgres_backend_module, "psycopg", FakePsycopg)
    backend = object.__new__(PostgresBackend)
    backend.dsn = "postgresql://example.invalid/db"

    assert backend.connect() is sentinel
    assert calls[0][1]["connect_timeout"] == backend.CONNECT_TIMEOUT_SECONDS
    assert backend.CONNECT_TIMEOUT_SECONDS == 10
