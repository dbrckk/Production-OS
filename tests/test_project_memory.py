from production_os.managed_projects import ManagedProjectService
from production_os.project_memory import MEMORY_SCHEMA, ProjectMemoryStore
from production_os.sqlite_backend import SQLiteBackend, SQLiteJobQueue
from production_os.workflow_engine import WorkflowEngine, WorkflowTaskSpec


def _engine(tmp_path):
    backend = SQLiteBackend(tmp_path / "memory.sqlite")
    return WorkflowEngine(backend, SQLiteJobQueue(backend))


def test_project_memory_records_sanitized_structured_outcome(tmp_path):
    engine = _engine(tmp_path)
    store = ProjectMemoryStore(engine.backend)

    recorded = store.record_from_result(
        repository="owner/repo",
        project_id="project-1",
        generation=1,
        workflow_id="wf-1",
        task_id="implementation",
        kind="initial",
        result={
            "summary":"Implemented API pagination.",
            "validation":{"status":"passed"},
            "commit_shas":["a" * 40],
            "changed_files":["src/api.py", "tests/test_api.py"],
            "project_memory":{
                "decisions":["Use cursor pagination."],
                "constraints":[
                    "Keep the public API backwards compatible.",
                    "token=super-secret-value-123456",
                ],
                "facts":["Existing clients rely on page_size."],
                "risks":["Large pages can increase latency."],
                "next_steps":["Monitor pagination regressions."],
            },
        },
    )

    assert recorded is not None
    assert recorded["schema_version"] == MEMORY_SCHEMA
    assert recorded["decisions"] == ["Use cursor pagination."]
    assert recorded["constraints"] == [
        "Keep the public API backwards compatible."
    ]
    assert recorded["commit_shas"] == ["a" * 40]

    recalled = store.recall(
        repository="owner/repo",
        project_id="project-1",
        query="pagination API backwards compatible",
    )
    assert len(recalled) == 1
    assert recalled[0].summary == "Implemented API pagination."
    assert recalled[0].validation_status == "passed"


def test_workflow_result_automatically_creates_managed_project_memory(tmp_path):
    engine = _engine(tmp_path)
    workflow = engine.create(
        name="managed",
        repository="owner/repo",
        tasks=[
            WorkflowTaskSpec(
                task_id="implementation",
                title="Implement",
                payload={
                    "managed_project_id":"project-auto",
                    "managed_project_generation":2,
                    "managed_project_kind":"instruction",
                    "handoff":{
                        "repository":"owner/repo",
                        "task":"Implement durable behavior.",
                    },
                },
            )
        ],
    )
    engine.dispatch_ready(workflow["id"])

    engine.record_result(
        workflow["id"],
        "implementation",
        succeeded=True,
        result={
            "summary":"Durable behavior implemented.",
            "project_memory":{
                "decisions":["Persist state before acknowledging success."],
            },
        },
    )

    recalled = engine.project_memory.recall(
        repository="owner/repo",
        project_id="project-auto",
        query="persist state durable",
    )
    assert len(recalled) == 1
    assert recalled[0].generation == 2
    assert recalled[0].kind == "instruction"
    assert recalled[0].decisions == (
        "Persist state before acknowledging success.",
    )


def test_managed_project_specs_recall_prior_project_memory(tmp_path):
    engine = _engine(tmp_path)
    managed = ManagedProjectService(engine)
    managed.project_memory.record_from_result(
        repository="owner/repo",
        project_id="project-memory",
        generation=1,
        workflow_id="old-workflow",
        task_id="review",
        kind="initial",
        result={
            "summary":"Authentication migration completed.",
            "validation":{"status":"passed"},
            "project_memory":{
                "decisions":["Keep session cookies HttpOnly."],
                "constraints":["Do not rename the public login endpoint."],
            },
        },
    )

    task = managed._workflow_spec(
        project_id="project-memory",
        repository="owner/repo",
        final_goal="Improve authentication",
        instruction="Add refresh-token rotation",
        generation=2,
        kind="instruction",
        token_budget=1000,
        agent_preference="auto",
    )

    context = task.payload["handoff"]["project_memory"]
    assert context["schema_version"] == (
        "production-os/project-memory-context/v1"
    )
    assert context["items"]
    assert context["items"][0]["decisions"] == [
        "Keep session cookies HttpOnly."
    ]


def test_cooperative_planner_receives_memory_as_structured_and_text_context(tmp_path):
    engine = _engine(tmp_path)
    managed = ManagedProjectService(engine)
    managed.project_memory.record_from_result(
        repository="owner/repo",
        project_id="project-planner",
        generation=1,
        workflow_id="wf-old",
        task_id="validation",
        kind="initial",
        result={
            "summary":"Dashboard query batching is stable.",
            "project_memory":{
                "constraints":["Preserve the existing REST contract."],
            },
        },
    )

    tasks = managed._cooperative_workflow_specs(
        project_id="project-planner",
        repository="owner/repo",
        final_goal="Improve dashboard performance",
        instruction="Optimize dashboard requests",
        generation=2,
        kind="instruction",
        token_budget=1000,
        agent_preference="auto",
    )

    planner = tasks[0]
    handoff = planner.payload["handoff"]
    assert handoff["project_memory"]["items"]
    assert "Relevant durable project memory:" in handoff["task"]
    assert "Preserve the existing REST contract." in handoff["task"]



def test_project_memory_deduplicates_identical_repeated_outcomes(tmp_path):
    engine = _engine(tmp_path)
    store = ProjectMemoryStore(engine.backend)
    kwargs = {
        "repository":"owner/repo",
        "project_id":"project-dedupe",
        "generation":1,
        "workflow_id":"wf-1",
        "task_id":"review",
        "kind":"initial",
        "result":{
            "summary":"Verified the migration.",
            "validation":{"status":"passed"},
            "project_memory":{
                "decisions":["Keep the compatibility shim."],
            },
        },
    }

    first = store.record_from_result(**kwargs)
    second = store.record_from_result(**kwargs)

    assert first is not None
    assert second is not None
    assert first["deduplicated"] is False
    assert second["deduplicated"] is True
    assert second["event_id"] == first["event_id"]

    recalled = store.recall(
        repository="owner/repo",
        project_id="project-dedupe",
        query="migration compatibility shim",
        limit=10,
    )
    assert len(recalled) == 1
