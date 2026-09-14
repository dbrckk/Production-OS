from production_os.sqlite_backend import SQLiteBackend, SQLiteJobQueue
from production_os.workflow_engine import WorkflowEngine, WorkflowTaskSpec


def test_workflow_change_impact_skips_unaffected_tasks(tmp_path):
    backend=SQLiteBackend(tmp_path/"db.sqlite")
    engine=WorkflowEngine(backend,SQLiteJobQueue(backend))

    workflow=engine.create(
        name="incremental",
        repository="o/a",
        metadata={"changed_paths":["android/app/Main.kt"]},
        tasks=[
            WorkflowTaskSpec(
                "backend-tests",
                "Backend tests",
                {
                    "impact":{
                        "paths":["backend/**"],
                        "skip_when_unaffected":True,
                    }
                },
            ),
            WorkflowTaskSpec(
                "android-tests",
                "Android tests",
                {
                    "impact":{
                        "paths":["android/**"],
                        "skip_when_unaffected":True,
                    }
                },
            ),
            WorkflowTaskSpec(
                "package",
                "Package",
                {},
                dependencies=("android-tests",),
            ),
        ],
    )

    tasks={task["task_id"]:task for task in workflow["tasks"]}
    assert tasks["backend-tests"]["status"]=="succeeded"
    assert tasks["backend-tests"]["result"]["skipped"] is True
    assert tasks["android-tests"]["status"]=="ready"
    assert tasks["package"]["status"]=="pending"

    jobs=engine.dispatch_ready(workflow["id"])
    assert len(jobs)==1
    assert jobs[0]["task"]=="Android tests"
