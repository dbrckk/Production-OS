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

    current = engine.record_result(
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

    task = current["tasks"][0]
    assert task["status"] == "succeeded"
    assert engine.skills.select(
        repository="owner/repo",
        task="Do work",
        capabilities=[],
    ) == []


def test_learned_skill_rejects_secret_like_material(tmp_path):
    backend = SQLiteBackend(tmp_path / "skills.sqlite")
    store = SkillStore(backend)

    try:
        store.record_success(
            repository="owner/repo",
            task="Configure deployment",
            capabilities=["code-implementation"],
            result={
                "learned_skill":{
                    "schema_version":SKILL_SCHEMA,
                    "title":"Configure deployment",
                    "trigger_terms":["deployment"],
                    "procedure":[
                        "Set token=abcdefghijklmnop before deployment.",
                    ],
                },
            },
        )
    except ValueError as exc:
        assert "credentials or secrets" in str(exc)
    else:
        raise AssertionError("secret-like learned procedure must be rejected")



def test_verified_skill_can_transfer_cross_repository_after_two_validations(tmp_path):
    backend = SQLiteBackend(tmp_path / "skills-transfer.sqlite")
    store = SkillStore(backend)
    result = {
        "validation":{"status":"passed"},
        "learned_skill":{
            "schema_version":SKILL_SCHEMA,
            "title":"Safe cache invalidation",
            "trigger_terms":["cache", "invalidation", "targeted"],
            "procedure":[
                "Identify affected cache keys.",
                "Invalidate only the targeted keys.",
                "Run cache regression tests.",
            ],
        },
    }
    first = store.record_success(
        repository="owner/source",
        task="Fix targeted cache invalidation",
        capabilities=["code-implementation"],
        result=result,
    )
    second = store.record_success(
        repository="owner/source",
        task="Fix targeted cache invalidation",
        capabilities=["code-implementation"],
        result=result,
    )

    assert first is not None and second is not None
    assert second.verified_successes == 2
    assert second.confidence >= 0.84

    selected = store.select(
        repository="owner/other",
        task="Repair targeted cache invalidation",
        capabilities=["code-implementation"],
    )

    assert [skill.skill_id for skill in selected] == [second.skill_id]
    assert selected[0].repository == "owner/source"


def test_unverified_repetition_does_not_promote_skill_cross_repository(tmp_path):
    backend = SQLiteBackend(tmp_path / "skills-unverified.sqlite")
    store = SkillStore(backend)
    result = {
        "learned_skill":{
            "schema_version":SKILL_SCHEMA,
            "title":"Cache invalidation guess",
            "trigger_terms":["cache", "invalidation", "targeted"],
            "procedure":["Invalidate targeted cache keys."],
        },
    }
    learned = None
    for _ in range(8):
        learned = store.record_success(
            repository="owner/source",
            task="Fix targeted cache invalidation",
            capabilities=["code-implementation"],
            result=result,
        )

    assert learned is not None
    assert learned.verified_successes == 0
    assert learned.confidence <= 0.75
    assert store.select(
        repository="owner/other",
        task="Repair targeted cache invalidation",
        capabilities=["code-implementation"],
    ) == []


def test_cross_repo_transfer_requires_capability_match_when_requested(tmp_path):
    backend = SQLiteBackend(tmp_path / "skills-capability.sqlite")
    store = SkillStore(backend)
    result = {
        "validation":{"status":"passed"},
        "learned_skill":{
            "schema_version":SKILL_SCHEMA,
            "title":"Safe cache invalidation",
            "trigger_terms":["cache", "invalidation", "targeted"],
            "procedure":["Invalidate targeted cache keys.", "Run tests."],
        },
    }
    for _ in range(2):
        store.record_success(
            repository="owner/source",
            task="Fix targeted cache invalidation",
            capabilities=["code-implementation"],
            result=result,
        )

    assert store.select(
        repository="owner/other",
        task="Repair targeted cache invalidation",
        capabilities=["browser-ui-validation"],
    ) == []


def test_failed_reuse_penalizes_injected_skill_confidence(tmp_path):
    backend = SQLiteBackend(tmp_path / "skill-feedback.sqlite")
    queue = SQLiteJobQueue(backend)
    engine = WorkflowEngine(backend, queue)
    result = {
        "validation":{"status":"passed"},
        "learned_skill":{
            "schema_version":SKILL_SCHEMA,
            "title":"Stabilize auth tests",
            "trigger_terms":["authentication", "tests", "flaky"],
            "procedure":["Reproduce repeatedly.", "Isolate state.", "Run tests."],
        },
    }
    learned = engine.skills.record_success(
        repository="owner/repo",
        task="Fix flaky authentication tests",
        capabilities=["test-debug"],
        result=result,
    )
    assert learned is not None

    workflow = engine.create(
        name="reuse-failure",
        repository="owner/repo",
        tasks=[
            WorkflowTaskSpec(
                task_id="repair",
                title="Repair auth tests",
                payload={
                    "handoff":{
                        "repository":"owner/repo",
                        "task":"Repair flaky authentication tests",
                        "preferred_capabilities":["test-debug"],
                    },
                },
                max_attempts=1,
            ),
        ],
    )
    jobs = engine.dispatch_ready(workflow["id"])
    injected = jobs[0]["payload"]["handoff"]["learned_skills"]
    assert injected[0]["skill_id"] == learned.skill_id

    engine.record_result(
        workflow["id"],
        "repair",
        succeeded=False,
        result={"reason":"regression"},
    )

    with backend.connect() as db:
        row = db.execute(
            """SELECT confidence,failed_uses,last_failure_at
               FROM learned_skills WHERE skill_id=?""",
            (learned.skill_id,),
        ).fetchone()
    assert int(row["failed_uses"]) == 1
    assert float(row["confidence"]) < learned.confidence
    assert row["last_failure_at"] is not None


def test_successful_reuse_slightly_boosts_skill_confidence(tmp_path):
    backend = SQLiteBackend(tmp_path / "skill-feedback-success.sqlite")
    queue = SQLiteJobQueue(backend)
    engine = WorkflowEngine(backend, queue)
    learned = engine.skills.record_success(
        repository="owner/repo",
        task="Repair schema migration",
        capabilities=["code-implementation"],
        result={
            "validation":{"status":"passed"},
            "learned_skill":{
                "schema_version":SKILL_SCHEMA,
                "title":"Safe schema migration",
                "trigger_terms":["schema", "migration", "repair"],
                "procedure":["Apply compatible schema first.", "Run migrations."],
            },
        },
    )
    assert learned is not None
    workflow = engine.create(
        name="reuse-success",
        repository="owner/repo",
        tasks=[
            WorkflowTaskSpec(
                task_id="repair",
                title="Repair migration",
                payload={
                    "handoff":{
                        "repository":"owner/repo",
                        "task":"Repair schema migration",
                        "preferred_capabilities":["code-implementation"],
                    },
                },
            ),
        ],
    )
    engine.dispatch_ready(workflow["id"])
    engine.record_result(
        workflow["id"],
        "repair",
        succeeded=True,
        result={"summary":"done"},
    )

    with backend.connect() as db:
        row = db.execute(
            "SELECT confidence,failed_uses FROM learned_skills WHERE skill_id=?",
            (learned.skill_id,),
        ).fetchone()
    assert int(row["failed_uses"]) == 0
    assert float(row["confidence"]) > learned.confidence


def test_skill_schema_upgrade_columns_exist(tmp_path):
    backend = SQLiteBackend(tmp_path / "skill-schema.sqlite")
    with backend.connect() as db:
        columns = {
            row["name"]
            for row in db.execute(
                "PRAGMA table_info(learned_skills)"
            ).fetchall()
        }
        version = db.execute(
            "SELECT value FROM schema_meta WHERE key='schema_version'"
        ).fetchone()["value"]

    assert {"verified_successes", "failed_uses", "last_failure_at"} <= columns
    assert int(version) >= 17
