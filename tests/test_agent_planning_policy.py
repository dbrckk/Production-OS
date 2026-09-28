from production_os.agent_planning_policy import planning_policy_for_repository
from production_os.managed_projects import ManagedProjectService
from production_os.sqlite_backend import SQLiteBackend, SQLiteJobQueue
from production_os.workflow_engine import WorkflowEngine, WorkflowTaskSpec


def _build(tmp_path):
    backend = SQLiteBackend(tmp_path / "planning-policy.sqlite")
    queue = SQLiteJobQueue(backend)
    engine = WorkflowEngine(backend, queue)
    return backend, engine


def _completed_workflow(engine, repository: str, *, succeeded: bool):
    workflow = engine.create(
        name="history",
        repository=repository,
        tasks=[
            WorkflowTaskSpec(
                task_id="work",
                title="Work",
                payload={},
                max_attempts=1,
            ),
        ],
    )
    engine.dispatch_ready(workflow["id"], limit=1)
    engine.record_result(
        workflow["id"],
        "work",
        succeeded=succeeded,
        result=(
            {"validation":{"status":"passed"}}
            if succeeded
            else {"validation":{"status":"failed"}}
        ),
    )
    return engine.get(workflow["id"])


def test_planning_policy_keeps_default_without_enough_history(tmp_path):
    backend, engine = _build(tmp_path)
    _completed_workflow(engine, "owner/repo", succeeded=True)

    policy = planning_policy_for_repository(
        backend,
        "owner/repo",
    )

    assert policy.source == "default"
    assert policy.sample_size == 1
    assert policy.max_agents == 6
    assert policy.success_rate is None


def test_planning_policy_reduces_fanout_for_risky_history(tmp_path):
    backend, engine = _build(tmp_path)
    _completed_workflow(engine, "owner/repo", succeeded=True)
    _completed_workflow(engine, "owner/repo", succeeded=False)
    _completed_workflow(engine, "owner/repo", succeeded=False)

    policy = planning_policy_for_repository(
        backend,
        "owner/repo",
    )

    assert policy.source == "historical-benchmark"
    assert policy.sample_size == 3
    assert policy.success_rate == 0.333333
    assert policy.max_agents == 3
    assert "elevated execution risk" in policy.guidance


def test_planning_policy_uses_moderate_fanout_for_mixed_history(tmp_path):
    backend, engine = _build(tmp_path)
    _completed_workflow(engine, "owner/repo", succeeded=True)
    _completed_workflow(engine, "owner/repo", succeeded=True)
    _completed_workflow(engine, "owner/repo", succeeded=False)

    policy = planning_policy_for_repository(
        backend,
        "owner/repo",
    )

    assert policy.success_rate == 0.666667
    assert policy.max_agents == 4
    assert "moderate parallelism" in policy.guidance


def test_managed_project_embeds_evidence_policy_in_planner_contract(tmp_path):
    backend, engine = _build(tmp_path)
    for succeeded in (True, False, False):
        _completed_workflow(engine, "owner/repo", succeeded=succeeded)

    managed = ManagedProjectService(engine)
    specs = managed._cooperative_workflow_specs(
        project_id="project-1234",
        repository="owner/repo",
        final_goal="Implement a backend feature",
        instruction="Implement a backend feature",
        generation=1,
        kind="initial",
        token_budget=1000,
        agent_preference="auto",
    )

    assert len(specs) == 1
    planner = specs[0]
    config = planner.payload["dynamic_agent_planner"]
    handoff = planner.payload["handoff"]
    assert config["max_agents"] == 3
    assert config["planning_policy"]["source"] == "historical-benchmark"
    assert config["planning_policy"]["sample_size"] == 3
    assert handoff["planning_policy"]["max_agents"] == 3
    assert (
        handoff["tool_contracts"]["dynamic_agent_plan"]["max_agents"]
        == 3
    )
    assert "Use at most 3 tasks" in handoff["task"]


def test_planning_policy_is_repository_scoped(tmp_path):
    backend, engine = _build(tmp_path)
    for succeeded in (False, False, False):
        _completed_workflow(engine, "owner/risky", succeeded=succeeded)
    for succeeded in (True, True, True):
        _completed_workflow(engine, "owner/strong", succeeded=succeeded)

    risky = planning_policy_for_repository(backend, "owner/risky")
    strong = planning_policy_for_repository(backend, "owner/strong")

    assert risky.max_agents == 3
    assert strong.max_agents == 6
    assert risky.success_rate == 0.0
    assert strong.success_rate == 1.0
