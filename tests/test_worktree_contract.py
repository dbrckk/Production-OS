from production_os.sqlite_backend import SQLiteBackend, SQLiteJobQueue
from production_os.workflow_engine import WorkflowEngine, WorkflowTaskSpec
from production_os.worktree_contract import build_worktree_contract


def test_worktree_contract_is_deterministic_and_attempt_scoped():
    first = build_worktree_contract(
        repository="owner/repo",
        workflow_id="wf-123",
        task_id="implementation-code",
        attempt=1,
        base_ref="abc123",
    )
    again = build_worktree_contract(
        repository="owner/repo",
        workflow_id="wf-123",
        task_id="implementation-code",
        attempt=1,
        base_ref="abc123",
    )
    retry = build_worktree_contract(
        repository="owner/repo",
        workflow_id="wf-123",
        task_id="implementation-code",
        attempt=2,
        base_ref="abc123",
    )

    assert first == again
    assert first["schema_version"] == "production-os/git-worktree-isolation/v1"
    assert first["mode"] == "git-worktree"
    assert first["branch"].startswith("production-os/")
    assert first["branch"] != retry["branch"]
    assert first["workspace_key"] != retry["workspace_key"]
    assert first["requirements"]["exclusive_workspace"] is True
    assert first["requirements"]["commit_changes_before_success"] is True


def test_dispatch_ready_injects_unique_worktree_contracts_for_parallel_tasks(tmp_path):
    backend = SQLiteBackend(tmp_path / "workflow.sqlite")
    queue = SQLiteJobQueue(backend)
    engine = WorkflowEngine(backend, queue)
    workflow = engine.create(
        name="parallel",
        repository="owner/repo",
        tasks=[
            WorkflowTaskSpec(
                task_id="code",
                title="code",
                payload={
                    "isolation":{"mode":"git-worktree"},
                    "handoff":{"repository":"owner/repo", "task":"code"},
                },
            ),
            WorkflowTaskSpec(
                task_id="tests",
                title="tests",
                payload={
                    "isolation":{"mode":"git-worktree"},
                    "handoff":{"repository":"owner/repo", "task":"tests"},
                },
            ),
        ],
    )

    jobs = engine.dispatch_ready(workflow["id"], limit=10)

    assert len(jobs) == 2
    by_task = {
        job["payload"]["workflow_task_id"]:job
        for job in jobs
    }
    code = by_task["code"]["payload"]["handoff"]["isolation"]
    tests = by_task["tests"]["payload"]["handoff"]["isolation"]
    assert code["branch"] != tests["branch"]
    assert code["workspace_key"] != tests["workspace_key"]
    assert code["attempt"] == 1
    assert tests["attempt"] == 1


def test_integration_target_contract_is_preserved_in_dispatch(tmp_path):
    backend = SQLiteBackend(tmp_path / "integration.sqlite")
    queue = SQLiteJobQueue(backend)
    engine = WorkflowEngine(backend, queue)
    workflow = engine.create(
        name="integration",
        repository="owner/repo",
        tasks=[
            WorkflowTaskSpec(
                task_id="integration",
                title="integrate",
                payload={
                    "isolation":{
                        "mode":"git-worktree",
                        "integration_target":True,
                    },
                    "handoff":{"repository":"owner/repo", "task":"integrate"},
                },
            ),
        ],
    )

    job = engine.dispatch_ready(workflow["id"], limit=1)[0]
    isolation = job["payload"]["handoff"]["isolation"]

    assert isolation["integration_target"] is True
    assert isolation["requirements"]["no_shared_working_tree_writes"] is True
