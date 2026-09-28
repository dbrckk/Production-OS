from production_os.agent_benchmark import (
    BENCHMARK_SCHEMA,
    AutonomousBenchmark,
    compare_reports,
)
from production_os.dashboard_store import DashboardStore
from production_os.sqlite_backend import SQLiteBackend, SQLiteJobQueue
from production_os.workflow_engine import WorkflowEngine, WorkflowTaskSpec


def _build(tmp_path):
    backend = SQLiteBackend(tmp_path / "benchmark.sqlite")
    queue = SQLiteJobQueue(backend)
    return backend, queue, WorkflowEngine(backend, queue), DashboardStore(backend)


def _execution_job(job, *, attempt=1):
    return {
        **job,
        "delivery_attempt":attempt,
    }


def test_benchmark_reads_real_workflow_execution_history(tmp_path):
    backend, _queue, engine, store = _build(tmp_path)
    workflow = engine.create(
        name="benchmark",
        repository="owner/repo",
        tasks=[
            WorkflowTaskSpec(task_id="code", title="Code", payload={}),
            WorkflowTaskSpec(
                task_id="validate",
                title="Validate",
                payload={},
                dependencies=("code",),
            ),
        ],
    )
    code_job = engine.dispatch_ready(workflow["id"], limit=1)[0]
    store.start_execution(_execution_job(code_job), "worker-code")
    store.finish_execution(
        code_job["key"],
        "worker-code",
        status="succeeded",
        duration_seconds=12,
        result={
            "usage":{
                "provider":"free",
                "model":"code-model",
                "api_calls":1,
                "input_tokens":10,
                "cached_input_tokens":0,
                "output_tokens":5,
                "reasoning_tokens":0,
                "total_tokens":15,
                "estimated_cost_usd":0.0,
            },
        },
    )
    engine.record_result(
        workflow["id"],
        "code",
        succeeded=True,
        result={"summary":"done"},
    )

    current = engine.get(workflow["id"])
    validate_task = next(
        task for task in current["tasks"]
        if task["task_id"] == "validate"
    )
    validate_job = engine.queue.get(validate_task["claimed_job_key"])
    store.start_execution(_execution_job(validate_job), "worker-test")
    store.finish_execution(
        validate_job["key"],
        "worker-test",
        status="succeeded",
        duration_seconds=8,
        result={
            "usage":{
                "provider":"free",
                "model":"test-model",
                "api_calls":1,
                "input_tokens":6,
                "cached_input_tokens":0,
                "output_tokens":4,
                "reasoning_tokens":0,
                "total_tokens":10,
                "estimated_cost_usd":0.0,
            },
        },
    )
    engine.record_result(
        workflow["id"],
        "validate",
        succeeded=True,
        result={
            "summary":"validated",
            "validation":{"status":"passed","tests":["unit"]},
        },
    )

    row = AutonomousBenchmark(backend).workflow(workflow["id"])

    assert row.succeeded is True
    assert row.task_count == 2
    assert row.succeeded_tasks == 2
    assert row.execution_count == 2
    assert row.failed_executions == 0
    assert row.validation_passes == 1
    assert row.validation_failures == 0
    assert row.cumulative_execution_seconds == 20.0
    assert row.observed_cost_usd == 0.0
    assert row.unknown_cost_executions == 0
    assert row.providers == ("free",)
    assert row.models == ("code-model", "test-model")


def test_benchmark_counts_retry_failures_and_operator_controls(tmp_path):
    backend, queue, engine, store = _build(tmp_path)
    workflow = engine.create(
        name="retry",
        repository="owner/repo",
        tasks=[
            WorkflowTaskSpec(
                task_id="code",
                title="Code",
                payload={},
                max_attempts=2,
            ),
        ],
    )
    first = engine.dispatch_ready(workflow["id"], limit=1)[0]
    store.start_execution(_execution_job(first), "worker-a")
    store.finish_execution(
        first["key"],
        "worker-a",
        status="failed",
        duration_seconds=4,
        result={},
    )
    engine.record_result(
        workflow["id"],
        "code",
        succeeded=False,
        result={
            "summary":"failed",
            "validation":{"status":"failed"},
        },
    )

    current = engine.get(workflow["id"])
    retry_task = next(
        task for task in current["tasks"]
        if task["task_id"] == "code"
    )
    retry_job = queue.get(retry_task["claimed_job_key"])
    store.start_execution(
        _execution_job(retry_job, attempt=2),
        "worker-a",
    )
    store.finish_execution(
        retry_job["key"],
        "worker-a",
        status="succeeded",
        duration_seconds=6,
        result={
            "usage":{
                "provider":"p",
                "model":"m",
                "api_calls":1,
                "input_tokens":1,
                "cached_input_tokens":0,
                "output_tokens":1,
                "reasoning_tokens":0,
                "total_tokens":2,
                "estimated_cost_usd":0.25,
            },
        },
    )
    engine.record_result(
        workflow["id"],
        "code",
        succeeded=True,
        result={"validation":{"status":"passed"}},
    )

    with backend.transaction() as db:
        db.execute(
            """
            INSERT INTO control_audit_events(
                id, action, worker_id, job_key, requested_by,
                outcome, error_code, requested_at
            ) VALUES(?,?,?,?,?,?,?,?)
            """,
            (
                "audit-1",
                "retry",
                "worker-a",
                retry_job["key"],
                "operator:test",
                "accepted",
                None,
                "2026-09-28T07:00:00+00:00",
            ),
        )

    row = AutonomousBenchmark(backend).workflow(workflow["id"])

    assert row.succeeded is True
    assert row.execution_count == 2
    assert row.failed_executions == 1
    assert row.retry_executions == 1
    assert row.operator_interventions == 1
    assert row.observed_cost_usd == 0.25
    assert row.unknown_cost_executions == 1


def test_benchmark_report_aggregates_without_inventing_unknown_cost(tmp_path):
    backend, _queue, engine, _store = _build(tmp_path)
    successful = engine.create(
        name="ok",
        repository="owner/one",
        tasks=[WorkflowTaskSpec(task_id="done", title="Done", payload={})],
    )
    engine.dispatch_ready(successful["id"])
    engine.record_result(
        successful["id"],
        "done",
        succeeded=True,
        result={},
    )
    failed = engine.create(
        name="bad",
        repository="owner/two",
        tasks=[
            WorkflowTaskSpec(
                task_id="bad",
                title="Bad",
                payload={},
                max_attempts=1,
            )
        ],
    )
    engine.dispatch_ready(failed["id"])
    engine.record_result(
        failed["id"],
        "bad",
        succeeded=False,
        result={"validation":{"status":"failed"}},
    )

    report = AutonomousBenchmark(backend).report([
        successful["id"],
        failed["id"],
    ])

    assert report["schema_version"] == BENCHMARK_SCHEMA
    assert report["workflow_count"] == 2
    assert report["success_count"] == 1
    assert report["success_rate"] == 0.5
    assert report["validation_failures"] == 1
    assert len(report["workflows"]) == 2


def test_compare_reports_returns_metric_deltas_without_declaring_winner():
    candidate = {
        "schema_version":BENCHMARK_SCHEMA,
        "workflow_count":10,
        "success_rate":0.9,
        "operator_interventions":1,
        "retry_executions":2,
        "validation_failures":1,
        "execution_failure_rate":0.05,
        "cumulative_execution_seconds":100,
        "median_wall_clock_seconds":20,
        "observed_cost_usd":0.0,
    }
    baseline = {
        "schema_version":BENCHMARK_SCHEMA,
        "workflow_count":10,
        "success_rate":0.8,
        "operator_interventions":3,
        "retry_executions":4,
        "validation_failures":2,
        "execution_failure_rate":0.1,
        "cumulative_execution_seconds":130,
        "median_wall_clock_seconds":30,
        "observed_cost_usd":1.0,
    }

    comparison = compare_reports(candidate, baseline)

    assert comparison["deltas"]["success_rate"] == 0.1
    assert comparison["deltas"]["operator_interventions"] == -2
    assert comparison["deltas"]["observed_cost_usd"] == -1.0
    assert "winner" not in comparison



def test_agent_benchmark_cli_parses_multiple_workflows_and_baseline():
    from production_os.cli import _parse_args

    args = _parse_args([
        "agent-benchmark",
        "--database", "benchmark.sqlite",
        "--workflow-id", "wf-a",
        "--workflow-id", "wf-b",
        "--baseline", "baseline.json",
    ])

    assert args.database == "benchmark.sqlite"
    assert args.workflow_id == ["wf-a", "wf-b"]
    assert args.baseline == "baseline.json"



def test_benchmark_records_dynamic_planner_policy_and_actual_fanout(tmp_path):
    backend, _queue, engine, _store = _build(tmp_path)
    workflow = engine.create(
        name="adaptive",
        repository="owner/adaptive",
        tasks=[
            WorkflowTaskSpec(
                task_id="planner",
                title="Planner",
                payload={
                    "dynamic_agent_planner":{
                        "max_agents":3,
                        "planning_policy":{
                            "source":"historical-benchmark",
                            "sample_size":7,
                            "max_agents":3,
                        },
                    },
                },
            ),
            WorkflowTaskSpec(
                task_id="planner.agent.code",
                title="Code",
                payload={"dynamic_agent_child":True},
                dependencies=("planner",),
            ),
            WorkflowTaskSpec(
                task_id="planner.agent.tests",
                title="Tests",
                payload={"dynamic_agent_child":True},
                dependencies=("planner",),
            ),
        ],
    )

    row = AutonomousBenchmark(backend).workflow(workflow["id"])

    assert row.planning_policy_source == "historical-benchmark"
    assert row.planner_max_agents == 3
    assert row.dynamic_agent_count == 2
    payload = row.to_dict()
    assert payload["planning_policy_source"] == "historical-benchmark"
    assert payload["planner_max_agents"] == 3
    assert payload["dynamic_agent_count"] == 2


def test_benchmark_report_aggregates_planner_policy_observability(tmp_path):
    backend, _queue, engine, _store = _build(tmp_path)
    ids = []
    for index, max_agents in enumerate((3, 5), start=1):
        workflow = engine.create(
            name=f"adaptive-{index}",
            repository="owner/adaptive",
            tasks=[
                WorkflowTaskSpec(
                    task_id="planner",
                    title="Planner",
                    payload={
                        "dynamic_agent_planner":{
                            "max_agents":max_agents,
                            "planning_policy":{
                                "source":"historical-benchmark",
                                "max_agents":max_agents,
                            },
                        },
                    },
                ),
                WorkflowTaskSpec(
                    task_id="planner.agent.code",
                    title="Code",
                    payload={"dynamic_agent_child":True},
                    dependencies=("planner",),
                ),
            ],
        )
        ids.append(workflow["id"])

    report = AutonomousBenchmark(backend).report(ids)

    assert report["dynamic_agent_count"] == 2
    assert report["average_planner_max_agents"] == 4.0
    assert report["planning_policy_sources"] == {
        "historical-benchmark":2,
    }
