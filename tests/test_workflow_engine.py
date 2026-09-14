import pytest

from production_os.sqlite_backend import SQLiteBackend, SQLiteJobQueue
from production_os.workflow_engine import WorkflowEngine, WorkflowTaskSpec


def engine(tmp_path):
    backend=SQLiteBackend(tmp_path/"db.sqlite")
    return WorkflowEngine(backend,SQLiteJobQueue(backend))


def test_workflow_fanout_fanin(tmp_path):
    wf=engine(tmp_path)
    created=wf.create(
        name="release",
        repository="o/a",
        tasks=[
            WorkflowTaskSpec("build","Build",{},estimated_minutes=5),
            WorkflowTaskSpec(
                "unit","Unit tests",{},("build",),estimated_minutes=2
            ),
            WorkflowTaskSpec(
                "lint","Lint",{},("build",),estimated_minutes=1
            ),
            WorkflowTaskSpec(
                "package","Package",{},("unit","lint"),estimated_minutes=3
            ),
        ],
    )
    assert created["status"]=="running"
    assert [
        t["task_id"] for t in created["tasks"] if t["status"]=="ready"
    ]==["build"]

    jobs=wf.dispatch_ready(created["id"])
    assert len(jobs)==1
    wf.record_result(created["id"],"build",succeeded=True)

    current=wf.get(created["id"])
    ready={
        t["task_id"] for t in current["tasks"]
        if t["status"]=="queued"
    }
    assert ready=={"unit","lint"}

    wf.record_result(created["id"],"unit",succeeded=True)
    wf.record_result(created["id"],"lint",succeeded=True)
    current=wf.get(created["id"])
    assert next(
        t for t in current["tasks"] if t["task_id"]=="package"
    )["status"]=="queued"

    wf.record_result(created["id"],"package",succeeded=True)
    assert wf.get(created["id"])["status"]=="succeeded"


def test_workflow_rejects_cycle(tmp_path):
    wf=engine(tmp_path)
    with pytest.raises(ValueError):
        wf.create(
            name="bad",
            repository="o/a",
            tasks=[
                WorkflowTaskSpec("a","A",{},("b",)),
                WorkflowTaskSpec("b","B",{},("a",)),
            ],
        )


def test_workflow_retry_budget(tmp_path):
    wf=engine(tmp_path)
    created=wf.create(
        name="retry",
        repository="o/a",
        tasks=[
            WorkflowTaskSpec(
                "test","Test",{},max_attempts=2
            )
        ],
    )
    wf.dispatch_ready(created["id"])
    wf.record_result(
        created["id"],"test",succeeded=False,result={"error":"x"}
    )
    current=wf.get(created["id"])["tasks"][0]
    assert current["status"]=="queued"
    assert current["attempts"]==2
    wf.record_result(
        created["id"],"test",succeeded=False,result={"error":"x2"}
    )
    assert wf.get(created["id"])["status"]=="failed"


def test_critical_path(tmp_path):
    wf=engine(tmp_path)
    created=wf.create(
        name="critical",
        repository="o/a",
        tasks=[
            WorkflowTaskSpec("a","A",{},estimated_minutes=2),
            WorkflowTaskSpec("b","B",{},("a",),estimated_minutes=5),
            WorkflowTaskSpec("c","C",{},("a",),estimated_minutes=1),
            WorkflowTaskSpec("d","D",{},("b","c"),estimated_minutes=3),
        ],
    )
    path=wf.critical_path(created["id"])
    assert path["task_ids"]==["a","b","d"]
    assert path["estimated_minutes"]==10


def test_change_impact_can_be_recomputed_before_execution(tmp_path):
    wf=engine(tmp_path)
    created=wf.create(
        name="incremental",
        repository="o/a",
        metadata={"changed_paths":["src/core.py"]},
        tasks=[
            WorkflowTaskSpec(
                "src-tests",
                "Source tests",
                {
                    "impact":{
                        "paths":["src/**"],
                        "skip_when_unaffected":True,
                    }
                },
            ),
            WorkflowTaskSpec(
                "docs-tests",
                "Docs tests",
                {
                    "impact":{
                        "paths":["docs/**"],
                        "skip_when_unaffected":True,
                    }
                },
            ),
        ],
    )
    first={task["task_id"]:task for task in created["tasks"]}
    assert first["src-tests"]["status"]=="ready"
    assert first["docs-tests"]["status"]=="succeeded"
    assert first["docs-tests"]["result"]["skipped"] is True

    wf.apply_change_impact(created["id"],["docs/guide.md"])
    current={
        task["task_id"]:task
        for task in wf.get(created["id"])["tasks"]
    }
    assert current["src-tests"]["status"]=="succeeded"
    assert current["src-tests"]["result"]["skipped"] is True
    assert current["docs-tests"]["status"]=="ready"
    assert current["docs-tests"]["result"] is None


def test_change_impact_recompute_rejected_after_dispatch(tmp_path):
    wf=engine(tmp_path)
    created=wf.create(
        name="incremental",
        repository="o/a",
        tasks=[
            WorkflowTaskSpec(
                "tests",
                "Tests",
                {
                    "impact":{
                        "paths":["src/**"],
                        "skip_when_unaffected":True,
                    }
                },
            ),
        ],
    )
    jobs=wf.dispatch_ready(created["id"])
    assert len(jobs)==1

    with pytest.raises(
        RuntimeError,
        match="workflow execution started",
    ):
        wf.apply_change_impact(created["id"],["README.md"])

