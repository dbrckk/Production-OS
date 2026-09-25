import pytest

from production_os.managed_projects import ManagedProjectService
from production_os.sqlite_backend import SQLiteBackend, SQLiteJobQueue
from production_os.workflow_engine import WorkflowEngine, WorkflowTaskSpec


def service(tmp_path):
    backend = SQLiteBackend(tmp_path / "db.sqlite")
    queue = SQLiteJobQueue(backend)
    workflows = WorkflowEngine(backend, queue)
    return ManagedProjectService(workflows), workflows


def test_managed_project_requires_human_completion_after_execution(tmp_path):
    projects, workflows = service(tmp_path)
    created = projects.create(
        repository="dbrckk/example",
        final_goal="Ship a verified playable release",
        token_budget=250_000,
        agent_preference="codex",
        requested_by="operator:test",
    )
    assert created["state"] == "RUNNING"
    assert created["status"] == "ACTIVE"
    assert created["generation"] == 1
    assert created["token_budget"] == 250_000
    assert len(created["runs"]) == 1

    workflows.record_result(
        created["workflow_id"],
        "implementation",
        succeeded=True,
        result={
            "usage":{
                "total_tokens":12_345,
                "runs":2,
                "agents":{"codex":2},
            }
        },
    )
    review = projects.get(created["project_id"])
    assert review["state"] == "REVIEW_REQUIRED"
    assert review["usage"]["total_tokens"] == 12_345
    assert review["usage"]["runs"] == 2
    assert review["usage"]["agents"] == {"codex":2}

    done = projects.mark_done(created["project_id"], approved_by="operator:test")
    assert done["state"] == "DONE"
    assert done["approved_by"] == "operator:test"


def test_followup_instruction_creates_new_immutable_workflow_generation(tmp_path):
    projects, workflows = service(tmp_path)
    created = projects.create(
        repository="dbrckk/example",
        final_goal="Ship",
        token_budget=10_000,
    )
    first_workflow_id = created["workflow_id"]
    workflows.record_result(
        first_workflow_id,
        "implementation",
        succeeded=True,
        result={"usage":{"total_tokens":100}},
    )
    first_before = workflows.get(first_workflow_id)

    resumed = projects.add_instruction(
        created["project_id"],
        "Polish mobile controls",
        requested_by="operator:test",
    )
    assert resumed["state"] == "RUNNING"
    assert resumed["status"] == "ACTIVE"
    assert resumed["generation"] == 2
    assert resumed["workflow_id"] != first_workflow_id
    assert [run["generation"] for run in resumed["runs"]] == [1, 2]
    assert resumed["runs"][-1]["kind"] == "instruction"

    first_after = workflows.get(first_workflow_id)
    assert first_after == first_before

    second = workflows.get(resumed["workflow_id"])
    task = second["tasks"][0]
    assert task["task_id"] == "implementation"
    assert task["status"] == "queued"
    assert task["payload"]["handoff"]["task"] == "Polish mobile controls"


def test_retest_creates_new_generation_with_original_final_goal(tmp_path):
    projects, workflows = service(tmp_path)
    created = projects.create(
        repository="dbrckk/example",
        final_goal="Ship",
        token_budget=10_000,
    )
    workflows.record_result(
        created["workflow_id"],
        "implementation",
        succeeded=True,
    )

    running = projects.request_verification(
        created["project_id"],
        requested_by="operator:test",
    )
    assert running["generation"] == 2
    assert running["runs"][-1]["kind"] == "retest"
    task = workflows.get(running["workflow_id"])["tasks"][0]
    assert task["payload"]["managed_project_generation"] == 2
    assert task["payload"]["handoff"]["final_goal"] == "Ship"


def test_failed_generation_maps_to_needs_attention_and_allows_followup(tmp_path):
    projects, workflows = service(tmp_path)
    created = projects.create(
        repository="dbrckk/example",
        final_goal="Ship",
        token_budget=10_000,
    )
    for _ in range(3):
        workflows.record_result(
            created["workflow_id"],
            "implementation",
            succeeded=False,
        )
    attention = projects.get(created["project_id"])
    assert attention["status"] == "NEEDS_ATTENTION"

    resumed = projects.add_instruction(
        created["project_id"],
        "Recover from failure",
    )
    assert resumed["generation"] == 2
    assert resumed["status"] == "ACTIVE"


def test_active_generation_rejects_followup(tmp_path):
    projects, _ = service(tmp_path)
    created = projects.create(
        repository="dbrckk/example",
        final_goal="Ship",
        token_budget=10_000,
    )
    with pytest.raises(RuntimeError, match="require review or attention"):
        projects.add_instruction(
            created["project_id"],
            "Too early",
        )
    assert projects.get(created["project_id"])["generation"] == 1


def test_managed_project_list_excludes_normal_workflows(tmp_path):
    projects, workflows = service(tmp_path)
    created = projects.create(
        repository="dbrckk/example",
        final_goal="Ship",
        token_budget=10_000,
    )
    workflows.create(
        name="ordinary",
        repository="dbrckk/other",
        tasks=[
            WorkflowTaskSpec(
                task_id="ordinary",
                title="Ordinary task",
                payload={},
            )
        ],
    )
    listed = projects.list()
    assert [item["project_id"] for item in listed] == [created["project_id"]]


def test_managed_project_rejects_invalid_budget_and_repository(tmp_path):
    projects, _ = service(tmp_path)
    with pytest.raises(ValueError, match="token_budget"):
        projects.create(
            repository="dbrckk/example",
            final_goal="Ship",
            token_budget=0,
        )
    with pytest.raises(ValueError, match="owner/name"):
        projects.create(
            repository="not-a-repository",
            final_goal="Ship",
            token_budget=1000,
        )


def test_legacy_v4_workflow_is_migrated_on_first_read(tmp_path):
    projects, workflows = service(tmp_path)
    legacy = workflows.create(
        name="legacy-managed",
        repository="dbrckk/legacy",
        metadata={
            "managed_project":{
                "schema_version":"production-os/managed-project/v2",
                "final_goal":"Legacy goal",
                "token_budget":12345,
                "agent_preference":"codex",
                "human_state":"active",
            }
        },
        tasks=[
            WorkflowTaskSpec(
                task_id="goal",
                title="Legacy goal",
                payload={},
            )
        ],
    )
    workflows.record_result(legacy["id"], "goal", succeeded=True)

    migrated = projects.get(legacy["id"])
    assert migrated["state"] == "REVIEW_REQUIRED"
    assert migrated["workflow_id"] == legacy["id"]
    assert migrated["generation"] == 1
    assert migrated["token_budget"] == 12345
    assert migrated["runs"][0]["kind"] == "legacy"

def test_deterministic_project_id_is_idempotent_and_rejects_parameter_reuse(tmp_path):
    projects, workflows = service(tmp_path)
    project_id = "launchrequest0123456789abcdef0123"

    first = projects.create(
        repository="dbrckk/example",
        final_goal="Ship once",
        token_budget=30000,
        agent_preference="auto",
        requested_by="operator:test",
        project_id=project_id,
    )
    replay = projects.create(
        repository="dbrckk/example",
        final_goal="Ship once",
        token_budget=30000,
        agent_preference="auto",
        requested_by="operator:test",
        project_id=project_id,
    )

    assert replay["project_id"] == first["project_id"] == project_id
    assert replay["workflow_id"] == first["workflow_id"]
    assert replay["generation"] == 1
    assert len(replay["runs"]) == 1
    with workflows.backend.connect() as db:
        project_count = db.execute(
            "SELECT COUNT(*) AS count FROM managed_projects WHERE id=?",
            (project_id,),
        ).fetchone()["count"]
        run_count = db.execute(
            "SELECT COUNT(*) AS count FROM managed_project_runs WHERE project_id=?",
            (project_id,),
        ).fetchone()["count"]
        job_count = db.execute(
            "SELECT COUNT(*) AS count FROM jobs WHERE repository=?",
            ("dbrckk/example",),
        ).fetchone()["count"]
    assert project_count == 1
    assert run_count == 1
    assert job_count == 1

    with pytest.raises(RuntimeError, match="different launch parameters"):
        projects.create(
            repository="dbrckk/example",
            final_goal="Different instruction",
            token_budget=30000,
            agent_preference="auto",
            requested_by="operator:test",
            project_id=project_id,
        )


def test_deterministic_project_id_validation_preserves_default_creation(tmp_path):
    projects, _ = service(tmp_path)

    normal = projects.create(
        repository="dbrckk/example",
        final_goal="Normal launch",
        token_budget=1000,
    )
    assert len(normal["project_id"]) == 32

    with pytest.raises(ValueError, match="project_id is invalid"):
        projects.create(
            repository="dbrckk/example",
            final_goal="Invalid deterministic id",
            token_budget=1000,
            project_id="../bad",
        )

