from production_os.sqlite_backend import SQLiteBackend, SQLiteJobQueue
from production_os.workflow_engine import WorkflowEngine, WorkflowTaskSpec


def test_splittable_task_expands_into_parallel_shards(tmp_path):
    backend=SQLiteBackend(tmp_path/"db.sqlite")
    engine=WorkflowEngine(backend,SQLiteJobQueue(backend))

    workflow=engine.create(
        name="split",
        repository="o/a",
        tasks=[
            WorkflowTaskSpec(
                "batch",
                "Process batch",
                {
                    "splittable":True,
                    "split_items":[1,2,3,4,5],
                    "split_size":2,
                },
                estimated_minutes=9,
            ),
            WorkflowTaskSpec(
                "final",
                "Finalize",
                {},
                dependencies=("batch",),
            ),
        ],
    )

    tasks={task["task_id"]:task for task in workflow["tasks"]}
    shard_ids=sorted(
        task_id
        for task_id in tasks
        if task_id.startswith("batch#shard-")
    )
    assert len(shard_ids)==3
    assert tasks["batch"]["status"]=="pending"
    assert all(tasks[task_id]["status"]=="ready" for task_id in shard_ids)

    jobs=engine.dispatch_ready(workflow["id"],limit=10)
    assert len(jobs)==3

    for shard_id in shard_ids:
        engine.record_result(
            workflow["id"],
            shard_id,
            succeeded=True,
            result={"ok":True},
        )

    current=engine.get(workflow["id"])
    tasks={task["task_id"]:task for task in current["tasks"]}
    assert tasks["batch"]["status"]=="succeeded"
    assert tasks["final"]["status"]=="queued"
