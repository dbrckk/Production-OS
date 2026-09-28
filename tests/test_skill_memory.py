from production_os.skill_memory import SKILL_SCHEMA, SkillStore
from production_os.sqlite_backend import SQLiteBackend, SQLiteJobQueue
from production_os.workflow_engine import WorkflowEngine, WorkflowTaskSpec


def test_skill_store_records_success_and_retrieves_relevant_skill(tmp_path):
    backend = SQLiteBackend(tmp_path / "skills.sqlite")
    store = SkillStore(backend)

    learned = store.record_success(
        repository="owner/repo",
        task="Fix flaky authentication tests",
        capabilities=["test-debug"],
        result={
            "validation":{"status":"passed"},
            "learned_skill":{
                "schema_version":SKILL_SCHEMA,
                "title":"Stabilize auth tests",
                "trigger_terms":["authentication", "tests", "flaky"],
                "procedure":[
                    "Reproduce the flaky authentication test repeatedly.",
                    "Inspect shared state and isolate test credentials.",
                    "Run the targeted test loop before the full suite.",
                ],
            },
        },
    )

    assert learned is not None
    assert learned.successes == 1
    assert learned.confidence == 0.8

    selected = store.select(
        repository="owner/repo",
        task="Repair authentication test flakiness",
        capabilities=["test-debug"],
    )

    assert [skill.skill_id for skill in selected] == [learned.skill_id]
    assert selected[0].procedure[0].startswith("Reproduce")


def test_repeated_verified_skill_increases_confidence(tmp_path):
    backend = SQLiteBackend(tmp_path / "skills.sqlite")
    store = SkillStore(backend)
    result = {
        "validation":{"status":"passed"},
        "learned_skill":{
            "schema_version":SKILL_SCHEMA,
            "title":"Safe schema migration",
            "trigger_terms":["schema", "migration"],
            "procedure":["Add backward-compatible schema first.", "Run migration tests."],
        },
    }

    first = store.record_success(
        repository="owner/repo",
        task="Add schema migration",
        capabilities=["code-implementation"],
        result=result,
    )
    second = store.record_success(
        repository="owner/repo",
        task="Add schema migration",
        capabilities=["code-implementation"],
        result=result,
    )

    assert first is not None and second is not None
    assert second.successes == 2
    assert second.confidence > first.confidence


def test_skill_selection_is_repository_scoped(tmp_path):
    backend = SQLiteBackend(tmp_path / "skills.sqlite")
    store = SkillStore(backend)
    store.record_success(
        repository="owner/a",
        task="Optimize cache invalidation",
        capabilities=["code-implementation"],
        result={
            "learned_skill":{
                "schema_version":SKILL_SCHEMA,
                "title":"Cache invalidation",
                "trigger_terms":["cache", "invalidation"],
                "procedure":["Invalidate only affected cache keys."],
            },
        },
    )

    assert store.select(
        repository="owner/b",
        task="Fix cache invalidation",
        capabilities=["code-implementation"],
    ) == []


def test_workflow_injects_learned_skill_into_future_handoff(tmp_path):
    backend = SQLiteBackend(tmp_path / "workflow.sqlite")
    queue = SQLiteJobQueue(backend)
    engine = WorkflowEngine(backend, queue)

    first = engine.create(
        name="learn",
        repository="owner/repo",
        tasks=[
            WorkflowTaskSpec(
                task_id="fix",
                title="Fix auth tests",
                payload={
                    "handoff":{
                        "repository":"owner/repo",
                        "task":"Fix flaky authentication tests",
                        "preferred_capabilities":["test-debug"],
                    },
                },
            ),
        ],
    )
    engine.dispatch_ready(first["id"])
    engine.record_result(
        first["id"],
        "fix",
        succeeded=True,
        result={
            "validation":{"status":"passed"},
            "learned_skill":{
                "schema_version":SKILL_SCHEMA,
                "title":"Stabilize auth tests",
                "trigger_terms":["authentication", "tests", "flaky"],
                "procedure":[
                    "Reproduce the failure repeatedly.",
                    "Isolate shared test state.",
                ],
            },
        },
    )

    second = engine.create(
        name="reuse",
        repository="owner/repo",
        tasks=[
            WorkflowTaskSpec(
                task_id="repair",
                title="Repair auth tests",
                payload={
                    "handoff":{
                        "repository":"owner/repo",
                        "task":"Repair authentication test flakiness",
                        "preferred_capabilities":["test-debug"],
                    },
                },
            ),
        ],
    )
    jobs = engine.dispatch_ready(second["id"])
    handoff = jobs[0]["payload"]["handoff"]

    assert handoff["learned_skills"][0]["title"] == "Stabilize auth tests"
    assert handoff["tool_contracts"]["skill_learning"] == {
        "schema":SKILL_SCHEMA,
        "result_field":"learned_skill",
        "max_procedure_steps":12,
        "optional":True,
    }


def test_invalid_learned_skill_does_not_corrupt_successful_result(tmp_path):
    backend = SQLiteBackend(tmp_path / "workflow.sqlite")
    queue = SQLiteJobQueue(backend)
    engine = WorkflowEngine(backend, queue)
    workflow = engine.create(
        name="invalid-learning",
        repository="owner/repo",
        tasks=[
            WorkflowTaskSpec(
                task_id="task",
                title="Task",
                payload={"handoff":{"repository":"owner/repo", "task":"Do work"}},
            ),
        ],
    )
    engine.dispatch_ready(workflow["id"])

    try:
        engine.record_result(
            workflow["id"],
            "task",
            succeeded=True,
            result={
                "summary":"work succeeded",
                "learned_skill":{
                    "schema_version":"bad-schema",
                    "title":"Bad",
                    "procedure":["one"],
                },
            },
        )
    except ValueError:
        pass
    else:
        raise AssertionError("invalid learned skill must be rejected before acceptance")

    current = engine.get(workflow["id"])
    task = current["tasks"][0]
    assert task["status"] == "queued"
