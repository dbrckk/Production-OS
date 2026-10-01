from __future__ import annotations

import inspect
from types import SimpleNamespace

import pytest

import production_os.controller as controller
from production_os.cli import _parse_args
from production_os.controller import run_control_cycle
from production_os.managed_projects import ManagedProjectService
from production_os.storage import job_queue_for, open_backend, worker_registry_for
from production_os.workflow_engine import WorkflowEngine


def _cycle_kwargs(tmp_path):
    return {
        "owner":"owner",
        "runtime_state_path":str(tmp_path / "runtime.json"),
        "queue_dir":str(tmp_path / "queue"),
        "snapshot_dir":str(tmp_path / "snapshots"),
        "metrics_path":str(tmp_path / "metrics.json"),
        "health_path":str(tmp_path / "health.json"),
        "journal_path":str(tmp_path / "journal.jsonl"),
    }


def test_controller_defaults_execution_mode_to_legacy_during_migration():
    signature = inspect.signature(run_control_cycle)

    assert signature.parameters["execution_mode"].default == "legacy"
    assert signature.parameters["project_token_budget"].default == 12000


def test_controller_cli_accepts_managed_execution_mode():
    args = _parse_args([
        "controller",
        "--owner", "owner",
        "--queue-dir", "/tmp/queue",
        "--snapshot-dir", "/tmp/snapshots",
        "--metrics", "/tmp/metrics.json",
        "--health", "/tmp/health.json",
        "--journal", "/tmp/journal.jsonl",
        "--execution-mode", "managed",
        "--project-token-budget", "24000",
    ])

    assert args.execution_mode == "managed"
    assert args.project_token_budget == 24000


def test_controller_managed_mode_requires_database_path(tmp_path):
    with pytest.raises(
        ValueError,
        match="managed execution mode requires database_path",
    ):
        run_control_cycle(
            **_cycle_kwargs(tmp_path),
            execution_mode="managed",
        )


def test_controller_rejects_unknown_execution_mode(tmp_path):
    with pytest.raises(ValueError, match="execution_mode"):
        run_control_cycle(
            **_cycle_kwargs(tmp_path),
            execution_mode="both",
        )


def test_controller_rejects_nonpositive_project_token_budget(tmp_path):
    with pytest.raises(ValueError, match="project_token_budget"):
        run_control_cycle(
            **_cycle_kwargs(tmp_path),
            project_token_budget=0,
        )



class _FakeGitHub:
    def list_repositories(self, _owner):
        return [{
            "full_name":"owner/repo",
            "fork":False,
            "archived":False,
        }]

    def collect_evidence(self, _repo):
        return object()


def _managed_cycle_setup(tmp_path, monkeypatch, *, lane="NOW"):
    action = SimpleNamespace(
        repository="owner/repo",
        task="Fix autonomous regression",
        rationale="Regression detected by controller",
        acceptance_criteria=["Regression is fixed", "Tests pass"],
        evidence=["ci:regression"],
        priority=90.0,
    )
    assessment = SimpleNamespace(
        actions=[action],
        profile="python-service",
        evidence=SimpleNamespace(
            full_name="owner/repo",
            language=None,
            default_branch="main",
        ),
    )
    monkeypatch.setattr(controller, "GitHubClient", _FakeGitHub)
    monkeypatch.setattr(
        controller,
        "assess_repository",
        lambda _evidence: assessment,
    )
    monkeypatch.setattr(controller, "detect_reuse", lambda _items: [])
    monkeypatch.setattr(
        controller,
        "build_schedule",
        lambda *_args, **_kwargs: {
            "work":[{
                "lane":lane,
                "repository":"owner/repo",
                "task":"Fix autonomous regression",
            }],
        },
    )
    monkeypatch.setattr(
        controller,
        "allocate_resources",
        lambda *_args, **_kwargs: {},
    )
    monkeypatch.setattr(
        controller,
        "build_snapshot",
        lambda *_args, **_kwargs: {
            "schema_version":"test/controller-snapshot/v1",
        },
    )
    monkeypatch.setattr(controller, "save_snapshot", lambda *_args: None)

    database = tmp_path / "production.sqlite"
    backend = open_backend(str(database))
    registry = worker_registry_for(backend)
    registry.register(
        "worker-a",
        ["code-implementation", "test-debug", "code-review"],
        2,
    )
    kwargs = {
        **_cycle_kwargs(tmp_path),
        "runtime_state_path":None,
        "database_path":str(database),
        "execution_mode":"managed",
    }
    return kwargs, backend


@pytest.mark.parametrize("lane", ["NOW", "PARALLEL"])
def test_managed_mode_action_creates_managed_project(
    tmp_path,
    monkeypatch,
    lane,
):
    kwargs, backend = _managed_cycle_setup(
        tmp_path,
        monkeypatch,
        lane=lane,
    )
    monkeypatch.setattr(
        controller,
        "dispatch_handoff",
        lambda *_args, **_kwargs: (
            (_ for _ in ()).throw(
                AssertionError("managed mode must not legacy-dispatch")
            )
        ),
    )

    result = run_control_cycle(**kwargs)

    service = ManagedProjectService(
        WorkflowEngine(backend, job_queue_for(backend))
    )
    projects = service.list()
    assert len(projects) == 1
    assert projects[0]["repository"] == "owner/repo"
    assert projects[0]["created_by"] == "controller"
    assert result["dispatches"] == []
    assert len(result["managed_projects"]) == 1
    assert result["managed_projects"][0]["project_id"] == projects[0]["id"]


def test_second_cycle_reuses_same_project_without_duplicate_workflow(
    tmp_path,
    monkeypatch,
):
    kwargs, backend = _managed_cycle_setup(tmp_path, monkeypatch)

    first = run_control_cycle(**kwargs)
    second = run_control_cycle(**kwargs)

    service = ManagedProjectService(
        WorkflowEngine(backend, job_queue_for(backend))
    )
    projects = service.list()
    assert len(projects) == 1
    assert first["managed_projects"][0]["project_id"] == projects[0]["id"]
    assert second["managed_projects"][0]["project_id"] == projects[0]["id"]
    assert (
        first["managed_projects"][0]["current_workflow_id"]
        == second["managed_projects"][0]["current_workflow_id"]
    )


def test_managed_mode_never_calls_dispatch_handoff(tmp_path, monkeypatch):
    kwargs, _backend = _managed_cycle_setup(tmp_path, monkeypatch)
    calls = []

    def forbidden(*_args, **_kwargs):
        calls.append("legacy")
        raise AssertionError("legacy dispatch called")

    monkeypatch.setattr(controller, "dispatch_handoff", forbidden)

    run_control_cycle(**kwargs)

    assert calls == []


def test_managed_launch_failure_never_falls_back_to_legacy(
    tmp_path,
    monkeypatch,
):
    kwargs, _backend = _managed_cycle_setup(tmp_path, monkeypatch)
    legacy_calls = []
    monkeypatch.setattr(
        controller,
        "launch_autonomous_project",
        lambda *_args, **_kwargs: (
            (_ for _ in ()).throw(RuntimeError("managed launch failed"))
        ),
        raising=False,
    )
    monkeypatch.setattr(
        controller,
        "dispatch_handoff",
        lambda *_args, **_kwargs: legacy_calls.append("legacy"),
    )

    result = run_control_cycle(**kwargs)

    assert legacy_calls == []
    assert result["dispatches"] == []
    assert result["managed_projects"] == []


def test_legacy_mode_still_calls_dispatch_handoff(tmp_path, monkeypatch):
    kwargs, _backend = _managed_cycle_setup(tmp_path, monkeypatch)
    kwargs["execution_mode"] = "legacy"
    calls = []

    class _Dispatch:
        def to_dict(self):
            return {
                "repository":"owner/repo",
                "task":"Fix autonomous regression",
                "key":"legacy-key",
            }

    def fake_dispatch(*_args, **_kwargs):
        calls.append("legacy")
        return _Dispatch()

    monkeypatch.setattr(controller, "dispatch_handoff", fake_dispatch)

    result = run_control_cycle(**kwargs)

    assert calls == ["legacy"]
    assert len(result["dispatches"]) == 1
    assert result.get("managed_projects", []) == []


def test_managed_cycle_response_contains_managed_projects_and_empty_dispatches(
    tmp_path,
    monkeypatch,
):
    kwargs, _backend = _managed_cycle_setup(tmp_path, monkeypatch)

    result = run_control_cycle(**kwargs)

    assert result["dispatches"] == []
    assert len(result["managed_projects"]) == 1
