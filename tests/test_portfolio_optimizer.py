from production_os.execution_optimizer import ExecutionOptimizer
from production_os.portfolio_optimizer import PortfolioOptimizer
from production_os.sqlite_backend import SQLiteBackend, SQLiteJobQueue
from production_os.workflow_engine import WorkflowEngine, WorkflowTaskSpec


def test_critical_blocking_job_is_ranked_first(tmp_path):
    backend=SQLiteBackend(tmp_path/"db.sqlite")
    queue=SQLiteJobQueue(backend)
    workflows=WorkflowEngine(backend,queue)
    execution=ExecutionOptimizer(backend)
    optimizer=PortfolioOptimizer(workflows,execution)

    wf=workflows.create(
        name="pipeline",
        repository="o/a",
        tasks=[
            WorkflowTaskSpec(
                "root","Root",{},priority=10,estimated_minutes=2
            ),
            WorkflowTaskSpec(
                "middle","Middle",{},("root",),
                priority=10,estimated_minutes=5
            ),
            WorkflowTaskSpec(
                "end","End",{},("middle",),
                priority=10,estimated_minutes=1
            ),
        ],
    )
    workflows.dispatch_ready(wf["id"])
    critical_job=queue.peek_candidates()[0]

    independent=queue.enqueue({
        "handoff":{
            "repository":"o/b",
            "task":"Independent",
            "priority":20,
        }
    })

    ranked=optimizer.rank([independent,critical_job])
    assert ranked[0]["job"]["key"]==critical_job["key"]
    assert ranked[0]["critical"] is True
    assert ranked[0]["descendants"]==2
