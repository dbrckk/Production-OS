from production_os.result_cache import ResultCache, fingerprint
from production_os.sqlite_backend import SQLiteBackend


def test_result_cache_roundtrip(tmp_path):
    backend=SQLiteBackend(tmp_path/"db.sqlite")
    cache=ResultCache(backend)
    key=fingerprint(repository="o/a",task="Build",inputs={"commit":"abc"})
    assert cache.get(key) is None
    cache.put(
        key=key,
        repository="o/a",
        task="Build",
        result={"artifact":"app.aab"},
    )
    hit=cache.get(key)
    assert hit["result"]["artifact"]=="app.aab"
    assert hit["hits"]==1
