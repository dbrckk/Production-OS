from production_os.agent_plan import PLAN_SCHEMA
from production_os.sqlite_backend import SQLiteBackend, SQLiteJobQueue
from production_os.workflow_engine import WorkflowEngine, WorkflowTaskSpec


def _build(tmp_path):
    backend = SQLiteBackend(tmp_path / "dynamic-agent.sqlite")
    queue = SQLiteJobQueue(backend)
    return WorkflowEngine(backend, queue), queue


def _planner_spec():
    return WorkflowTaskSpec(
        task_id="planner",
        title="Plan implementation",
        payload={
            "dynamic_agent_planner":{
                "available_token_budget":500,
                "max_agents":4,
                "integration_token_budget":100,
                "handoff":{
                    "final_goal":"Implement feature safely",
                    "agent_preference":"auto",
                },
            },
            "handoff":{
                "repository":"owner/repo",
                "task":"Plan the work.",
                "token_budget":100,
                "preferred_capabilities":["code-planning"],
            },
        },
        max_attempts=2,
    )


def test_planner_result_expands_parallel_agents_and_integration(tmp_path):
    engine, queue = _build(tmp_path)
    workflow = engine.create(
        name="dynamic",
        repository="owner/repo",
        tasks=[_planner_spec()],
    )
    planner_job = engine.dispatch_ready(workflow["id"], limit=10)[0]
    assert planner_job["payload"]["workflow_task_id"] == "planner"

    expanded = engine.record_result(
        workflow["id"],
        "planner",
        succeeded=True,
        result={
            "summary":"plan ready",
            "agent_plan":{
                "schema_version":PLAN_SCHEMA,
                "tasks":[
                    {
                        "task_id":"backend",
                        "title":"Implement backend",
                        "instruction":"Implement backend behavior.",
                        "token_budget":300,
                        "preferred_capabilities":["code-implementation"],
                    },
                    {
                        "task_id":"tests",
                        "title":"Build tests",
                        "instruction":"Build independent regression tests.",
                        "token_budget":200,
                        "preferred_capabilities":["test-debug"],
                    },
                ],
            },
        },
    )

    by_id = {task["task_id"]:task for task in expanded["tasks"]}
    assert set(by_id) == {
        "planner",
        "planner.agent.backend",
        "planner.agent.tests",
        "planner.integration",
    }
    assert by_id["planner"]["status"] == "succeeded"
    assert by_id["planner.agent.backend"]["status"] == "queued"
    assert by_id["planner.agent.tests"]["status"] == "queued"
    assert by_id["planner.integration"]["status"] == "pending"
    assert by_id["planner.agent.backend"]["dependencies"] == ["planner"]
    assert by_id["planner.agent.tests"]["dependencies"] == ["planner"]
    assert set(by_id["planner.integration"]["dependencies"]) == {
        "planner.agent.backend",
        "planner.agent.tests",
    }

    code = queue.claim_next(
        "code-worker",
        capabilities=["code-implementation"],
    )
    tests = queue.claim_next(
        "test-worker",
        capabilities=["test-debug"],
    )
    assert code is not None
    assert tests is not None
    assert (
        code["payload"]["handoff"]["isolation"]["mode"]
        == "git-worktree"
    )
    assert (
        tests["payload"]["handoff"]["isolation"]["mode"]
        == "git-worktree"
    )

    engine.record_result(
        workflow["id"],
        "planner.agent.backend",
        succeeded=True,
        result={"summary":"backend done", "commit_shas":["a"*40]},
    )
    progressed = engine.record_result(
        workflow["id"],
        "planner.agent.tests",
        succeeded=True,
        result={"summary":"tests done", "commit_shas":["b"*40]},
    )

    integration = next(
        task for task in progressed["tasks"]
        if task["task_id"] == "planner.integration"
    )
    assert integration["status"] == "queued"
    integration_job = queue.claim_next(
        "integration-worker",
        capabilities=["code-implementation"],
    )
    assert integration_job is not None
    upstream = integration_job["payload"]["handoff"]["upstream_context"]
    assert {row["task_id"] for row in upstream} == {
        "planner.agent.backend",
        "planner.agent.tests",
    }


def test_planner_child_dependencies_preserve_ordered_dag(tmp_path):
    engine, _queue = _build(tmp_path)
    workflow = engine.create(
        name="dynamic-deps",
        repository="owner/repo",
        tasks=[_planner_spec()],
    )
    engine.dispatch_ready(workflow["id"])
    expanded = engine.record_result(
        workflow["id"],
        "planner",
        succeeded=True,
        result={
            "agent_plan":{
                "schema_version":PLAN_SCHEMA,
                "tasks":[
                    {
                        "task_id":"api",
                        "title":"API",
                        "instruction":"Implement API.",
                        "token_budget":250,
                    },
                    {
                        "task_id":"client",
                        "title":"Client",
                        "instruction":"Implement client against API.",
                        "token_budget":250,
                        "dependencies":["api"],
                    },
                ],
            },
        },
    )

    by_id = {task["task_id"]:task for task in expanded["tasks"]}
    assert by_id["planner.agent.api"]["dependencies"] == ["planner"]
    assert by_id["planner.agent.client"]["dependencies"] == [
        "planner.agent.api"
    ]
    assert by_id["planner.agent.api"]["status"] == "queued"
    assert by_id["planner.agent.client"]["status"] == "pending"


def test_invalid_planner_plan_is_rejected_before_child_dispatch(tmp_path):
    engine, _queue = _build(tmp_path)
    workflow = engine.create(
        name="invalid-plan",
        repository="owner/repo",
        tasks=[_planner_spec()],
    )
    engine.dispatch_ready(workflow["id"])

    try:
        engine.record_result(
            workflow["id"],
            "planner",
            succeeded=True,
            result={
                "agent_plan":{
                    "schema_version":PLAN_SCHEMA,
                    "tasks":[
                        {
                            "task_id":"too-expensive",
                            "title":"Too expensive",
                            "instruction":"Spend too much.",
                            "token_budget":501,
                        },
                    ],
                },
            },
        )
    except ValueError as exc:
        assert "available token budget" in str(exc)
    else:
        raise AssertionError("invalid planner output must be rejected")

    current = engine.get(workflow["id"])
    assert {
        task["task_id"]
        for task in current["tasks"]
    } == {"planner"}
