import json

from production_os.sqlite_backend import SQLiteBackend, SQLiteRuntimeState
from production_os.sqlite_migration import import_json_state


def test_import_runtime_json(tmp_path):
    source=tmp_path/"runtime.json"
    source.write_text(json.dumps({
        "records":{
            "abc":{
                "key":"abc",
                "repository":"o/a",
                "task":"x",
                "status":"failed",
                "attempts":2,
            }
        }
    }),encoding="utf-8")
    backend=SQLiteBackend(tmp_path/"db.sqlite")
    result=import_json_state(backend,runtime_state=str(source))
    assert result["counts"]["runtime_records"]==1
    state=SQLiteRuntimeState(backend)
    assert state.records["abc"].attempts==2
