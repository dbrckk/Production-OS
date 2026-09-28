from production_os.agent_planning_policy import planning_policy_for_repository
from production_os.fanout_learning import learn_repository_fanout
from production_os.sqlite_backend import SQLiteBackend, SQLiteJobQueue
from production_os.workflow_engine import WorkflowEngine, WorkflowTaskSpec


def _build(tmp_path):
    backend = SQLiteBackend(tmp_path / "fanout-learning.sqlite")
    queue = SQLiteJobQueue(backend)
    return backend, WorkflowEngine(backend, queue)


def _history(engine, repository: str, *, max_agents: int, succeeded: bool):
    workflow = engine.create(
        name=f"fanout-{max_agents}",
        repository=repository,
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
                max_attempts=1,
            ),
        ],
    )
    terminal = "succeeded" if succeeded else "failed"
    with engine.backend.transaction() as db:
        db.execute(
            """
            UPDATE workflow_tasks
            SET status=?, result_json='{}'
            WHERE workflow_id=? AND task_id='planner'
            """,
            (terminal, workflow["id"]),
        )
        db.execute(
            """
            UPDATE workflows
            SET status=?
            WHERE id=?
            """,
            (terminal, workflow["id"]),
        )
    return workflow["id"]


def test_fanout_learning_selects_better_observed_bucket(tmp_path):
    backend, engine = _build(tmp_path)
    for _ in range(3):
        _history(
            engine,
            "owner/repo",
            max_agents=3,
            succeeded=True,
        )
    for succeeded in (True, False, False):
        _history(
            engine,
            "owner/repo",
            max_agents=6,
            succeeded=succeeded,
        )

    learned = learn_repository_fanout(
        backend,
        "owner/repo",
    )

    assert learned is not None
    assert learned.recommended_max_agents == 3
    assert learned.sample_size == 6
    assert learned.compared_buckets == 2
    assert [bucket.max_agents for bucket in learned.evidence] == [3, 6]
    assert learned.evidence[0].success_rate == 1.0
    assert learned.evidence[1].success_rate == 0.333333


def test_fanout_learning_requires_multiple_well_sampled_buckets(tmp_path):
    backend, engine = _build(tmp_path)
    for _ in range(3):
        _history(
            engine,
            "owner/repo",
            max_agents=3,
            succeeded=True,
        )
    for _ in range(2):
        _history(
            engine,
            "owner/repo",
            max_agents=6,
            succeeded=True,
        )

    learned = learn_repository_fanout(
        backend,
        "owner/repo",
    )

    assert learned is None


def test_planning_policy_uses_learned_lower_fanout(tmp_path):
    backend, engine = _build(tmp_path)
    for _ in range(3):
        _history(
            engine,
            "owner/repo",
            max_agents=3,
            succeeded=True,
        )
    for succeeded in (True, False, False):
        _history(
            engine,
            "owner/repo",
            max_agents=6,
            succeeded=succeeded,
        )

    policy = planning_policy_for_repository(
        backend,
        "owner/repo",
        sample_limit=20,
    )

    assert policy.source == "learned-fanout"
    assert policy.max_agents == 3
    assert policy.fanout_learning is not None
    assert policy.fanout_learning["recommended_max_agents"] == 3


def test_global_risk_ceiling_caps_learned_high_fanout(tmp_path):
    backend, engine = _build(tmp_path)
    for _ in range(3):
        _history(
            engine,
            "owner/repo",
            max_agents=3,
            succeeded=False,
        )
    for _ in range(3):
        _history(
            engine,
            "owner/repo",
            max_agents=6,
            succeeded=True,
        )

    learned = learn_repository_fanout(
        backend,
        "owner/repo",
    )
    policy = planning_policy_for_repository(
        backend,
        "owner/repo",
        sample_limit=20,
    )

    assert learned is not None
    assert learned.recommended_max_agents == 6
    assert policy.success_rate == 0.5
    assert policy.source == "learned-fanout-capped"
    assert policy.max_agents == 3
    assert policy.fanout_learning["recommended_max_agents"] == 6
