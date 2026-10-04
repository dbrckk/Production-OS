import pytest

import production_os.storage as storage


@pytest.mark.parametrize("location", [
    "postgresql://localhost/production",
    "postgres://localhost/production",
    "host=localhost dbname=production user=worker",
    "user=worker password='test password' dbname=production host=localhost",
    "dbname = 'production database' host = localhost",
    "service=production",
    "sslmode=require host=localhost dbname=production",
    "options='-c statement_timeout=5000' dbname=production",
    "  host=localhost dbname=production  ",
])
def test_postgres_locations_use_postgres(location):
    assert storage.is_postgres(location)


@pytest.mark.parametrize("location", [
    "production.db", "./host=production.db", "/tmp/host=production.db",
    "artifacts/production.db", "cache=production.db", ":memory:",
])
def test_sqlite_paths_keep_sqlite_routing(location):
    assert not storage.is_postgres(location)


def test_keyword_dsn_never_creates_sqlite_on_postgres_failure(monkeypatch, tmp_path):
    location = "host=localhost dbname=production"

    def postgres(_location):
        raise RuntimeError("PostgreSQL unavailable")

    def sqlite(_location):
        pytest.fail("PostgreSQL failures must not fall back to SQLite")

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(storage, "PostgresBackend", postgres)
    monkeypatch.setattr(storage, "SQLiteBackend", sqlite)

    with pytest.raises(RuntimeError, match="PostgreSQL unavailable"):
        storage.open_backend(location)
    assert list(tmp_path.iterdir()) == []


def test_malformed_keyword_dsn_is_handled_by_postgres(monkeypatch):
    location = "host='unterminated"
    seen = []
    monkeypatch.setattr(storage, "PostgresBackend", lambda value: seen.append(value))

    storage.open_backend(location)

    assert seen == [location]
