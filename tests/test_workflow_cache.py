from production_os.sqlite_backend import SQLiteBackend, SQLiteJobQueue
from production_os.workflow_engine import WorkflowEngine, WorkflowTaskSpec


def test_cacheable_workflow_task_reuses_result(tmp_path):
    backend=SQLiteBackend(tmp_path/"db.sqlite")
    engine=WorkflowEngine(backend,SQLiteJobQueue(backend))

    first=engine.create(
        name="first",
        repository="o/a",
        tasks=[
            WorkflowTaskSpec(
                "build",
                "Build",
                {
                    "cacheable":True,
                    "cache_inputs":{"commit":"abc"},
                },
            )
        ],
    )
    engine.dispatch_ready(first["id"])
    engine.record_result(
        first["id"],
        "build",
        succeeded=True,
        result={"artifact":"app.aab"},
    )
    assert engine.get(first["id"])["status"]=="succeeded"

    second=engine.create(
        name="second",
        repository="o/a",
        tasks=[
            WorkflowTaskSpec(
                "build",
                "Build",
                {
                    "cacheable":True,
                    "cache_inputs":{"commit":"abc"},
                },
            )
        ],
    )
    jobs=engine.dispatch_ready(second["id"])
    assert jobs==[]
    current=engine.get(second["id"])
    assert current["status"]=="succeeded"
    result=current["tasks"][0]["result"]
    assert result["cache_hit"] is True
    assert result["cached_result"]["artifact"]=="app.aab"
