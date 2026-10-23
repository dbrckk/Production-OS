import os
import subprocess
import sys
import textwrap
from pathlib import Path

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

    # Execute the actual embedded GitHub Actions pre-check, without network
    # requests or a model task. The handoff and execution SHA must coincide.
    root = Path(__file__).resolve().parents[1]
    workflow = (root / ".github/workflows/production-os-source-qualification.yml").read_text()
    handoff = (root / ".github/workflows/production-os-review-handoff.yml").read_text()
    assert (
        "ref: ${{ github.event_name == 'pull_request' && "
        "github.event.pull_request.head.sha || inputs.expected_sha }}"
    ) in workflow
    assert '"inputs": {"expected_sha": sha}' in handoff
    # Only allow handoff on the immutable, already-vetted candidate.
    # Even with GitHub Actions' PR creation disabled, qualification is
    # requested first and the subsequent PR failure stays a job failure.
    assert handoff.index(
        'request("POST", "/actions/workflows/production-os-source-qualification.yml/dispatches"'
    ) < handoff.index('created = request("POST", "/pulls"')
    assert "exact candidate branch lookup" in handoff
    assert "reviewed source diff comparison" in handoff
    assert "existing draft PR lookup" in handoff
    assert "immutable qualification dispatch" in handoff
    assert "GitHub rejected trusted draft PR creation" in handoff
    script = textwrap.dedent(
        workflow.split("          python - <<'PY'\n", 1)[1]
        .split("          PY\n", 1)[0]
    )
    valid_sha = "a" * 40
    valid_env = {
        "EXPECTED_SHA": valid_sha,
        "DISPATCH_SHA": valid_sha,
        "DISPATCH_REF": "refs/heads/studio/mp-" + ("b" * 24),
        "SOURCE_BRANCH": "",
        "SOURCE_REPOSITORY": "",
        "EVENT_NAME": "workflow_dispatch",
        "READ_TOKEN": "offline-fixture-only",
        "REPOSITORY": "dbrckk/Production-OS",
    }
    for override, succeeds in (
        ({}, True),
        ({"EXPECTED_SHA": "invalid"}, False),
        ({"DISPATCH_SHA": "c" * 40}, False),
        ({"DISPATCH_REF": "refs/heads/main"}, False),
        ({"REPOSITORY": "attacker/repo"}, False),
    ):
        result = subprocess.run(
            [sys.executable, "-c", script],
            env={**os.environ, **valid_env, **override},
            capture_output=True,
            text=True,
            check=False,
        )
        assert (result.returncode == 0) is succeeds, result.stderr

    # The PR-event route is a separate trust boundary. Run the same embedded
    # pre-check against fake read-only GitHub responses, never a network API.
    fixture = textwrap.dedent("""
        import io
        import json
        import os
        import urllib.request

        class Response:
            def __init__(self, payload):
                self.stream = io.BytesIO(json.dumps(payload).encode("utf-8"))
            def __enter__(self):
                return self
            def __exit__(self, *_args):
                self.stream.close()
            def read(self, *args):
                return self.stream.read(*args)

        def fake_urlopen(request, timeout=20):
            url = request.full_url
            if "/git/ref/heads/" in url:
                sha = "c" * 40 if os.getenv("SIMULATE_MOVED") else "a" * 40
                return Response({"object": {"sha": sha}})
            if "/compare/main..." in url:
                extra = os.getenv("SIMULATE_BAD_PATCH")
                patch = (
                    '@@ -9,7 +9,7 @@\\n'
                    '-    text = re.sub(r"-+", "-", text).strip("-.").lower()\\n'
                    '+    text = re.sub(r"-+", "-", text).strip("-.").lower().replace(".", "-")'
                )
                if extra:
                    patch = patch.replace(".replace", ".WRONG")
                return Response({
                    "status": "diverged",
                    "files": [{
                        "filename": "src/production_os/worktree_contract.py",
                        "status": "modified",
                        "additions": 1, "deletions": 1, "changes": 2,
                        "patch": patch,
                    }],
                })
            raise AssertionError("Unexpected offline HTTP request: " + url)

        urllib.request.urlopen = fake_urlopen
    """)
    pr_env = {
        **valid_env,
        "EVENT_NAME": "pull_request",
        "DISPATCH_REF": "refs/pull/297/merge",
        "SOURCE_BRANCH": "studio/mp-" + ("b" * 24),
        "SOURCE_REPOSITORY": "dbrckk/Production-OS",
    }
    for override, succeeds in (
        ({}, True),
        ({"SIMULATE_MOVED": "1"}, False),
        ({"SIMULATE_BAD_PATCH": "1"}, False),
        ({"SOURCE_REPOSITORY": "untrusted/repo"}, False),
        ({"SOURCE_BRANCH": "unreviewed-branch"}, False),
        ({"EXPECTED_SHA": "invalid"}, False),
    ):
        result = subprocess.run(
            [sys.executable, "-c", fixture + "\n" + script],
            env={**os.environ, **pr_env, **override},
            capture_output=True,
            text=True,
            check=False,
        )
        assert (result.returncode == 0) is succeeds, result.stderr


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



def test_dependent_worktree_bases_from_single_upstream_commit(tmp_path):
    backend = SQLiteBackend(tmp_path / "upstream-base.sqlite")
    queue = SQLiteJobQueue(backend)
    engine = WorkflowEngine(backend, queue)
    workflow = engine.create(
        name="upstream-base",
        repository="owner/repo",
        tasks=[
            WorkflowTaskSpec(
                task_id="integration",
                title="integration",
                payload={
                    "isolation":{"mode":"git-worktree"},
                    "handoff":{"repository":"owner/repo", "task":"integrate"},
                },
            ),
            WorkflowTaskSpec(
                task_id="validation",
                title="validation",
                payload={
                    "isolation":{
                        "mode":"git-worktree",
                        "integration_target":True,
                    },
                    "handoff":{"repository":"owner/repo", "task":"validate"},
                },
                dependencies=("integration",),
            ),
        ],
    )

    first = engine.dispatch_ready(workflow["id"], limit=10)
    assert len(first) == 1
    claimed_integration = queue.claim_next("integrator", capabilities=[])
    assert claimed_integration is not None
    assert claimed_integration["payload"]["workflow_task_id"] == "integration"
    engine.record_result(
        workflow["id"],
        "integration",
        succeeded=True,
        result={
            "summary":"integrated",
            "commit_shas":["a"*40],
        },
    )

    validation = queue.claim_next("validator", capabilities=[])
    assert validation is not None
    isolation = validation["payload"]["handoff"]["isolation"]
    assert isolation["base_ref"] == "a"*40


def test_multi_parent_integration_does_not_guess_one_upstream_base(tmp_path):
    backend = SQLiteBackend(tmp_path / "multi-parent-base.sqlite")
    queue = SQLiteJobQueue(backend)
    engine = WorkflowEngine(backend, queue)
    workflow = engine.create(
        name="multi-parent",
        repository="owner/repo",
        tasks=[
            WorkflowTaskSpec(
                task_id="a",
                title="a",
                payload={
                    "isolation":{"mode":"git-worktree"},
                    "handoff":{"repository":"owner/repo", "task":"a"},
                },
            ),
            WorkflowTaskSpec(
                task_id="b",
                title="b",
                payload={
                    "isolation":{"mode":"git-worktree"},
                    "handoff":{"repository":"owner/repo", "task":"b"},
                },
            ),
            WorkflowTaskSpec(
                task_id="integration",
                title="integration",
                payload={
                    "isolation":{
                        "mode":"git-worktree",
                        "integration_target":True,
                    },
                    "handoff":{"repository":"owner/repo", "task":"integrate"},
                },
                dependencies=("a","b"),
            ),
        ],
    )
    engine.dispatch_ready(workflow["id"], limit=10)
    claimed_a = queue.claim_next("worker-a", capabilities=[])
    claimed_b = queue.claim_next("worker-b", capabilities=[])
    assert claimed_a is not None
    assert claimed_b is not None
    assert {
        claimed_a["payload"]["workflow_task_id"],
        claimed_b["payload"]["workflow_task_id"],
    } == {"a", "b"}
    engine.record_result(
        workflow["id"],
        "a",
        succeeded=True,
        result={"commit_shas":["a"*40]},
    )
    engine.record_result(
        workflow["id"],
        "b",
        succeeded=True,
        result={"commit_shas":["b"*40]},
    )

    integration = queue.claim_next("integrator", capabilities=[])
    assert integration is not None
    isolation = integration["payload"]["handoff"]["isolation"]
    assert isolation["base_ref"] == "HEAD"
