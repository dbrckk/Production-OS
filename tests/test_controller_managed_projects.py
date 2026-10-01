from __future__ import annotations

import inspect
import json
from types import SimpleNamespace

import pytest

import production_os.controller as controller
from production_os.budgets import BudgetLedger
from production_os.cli import _parse_args
from production_os.controller import run_control_cycle
from production_os.emergency import set_emergency_stop
from production_os.managed_projects import ManagedProjectService
from production_os.quarantine import QuarantineStore
from production_os.rate_limit import RateLimitStore
from production_os.storage import (
    job_queue_for,
    open_backend,
    runtime_state_for,
    worker_registry_for,
)
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


def _managed_cycle_setup(
    tmp_path,
    monkeypatch,
    *,
    lane="NOW",
    register_worker=True,
    evidence=None,
):
    action = SimpleNamespace(
        repository="owner/repo",
        task="Fix autonomous regression",
        rationale="Regression detected by controller",
        acceptance_criteria=["Regression is fixed", "Tests pass"],
        evidence=list(evidence or ["ci:regression"]),
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
    if register_worker:
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



def _project_service(backend):
    return ManagedProjectService(
        WorkflowEngine(backend, job_queue_for(backend))
    )


def _with_resource_request(monkeypatch, *, tokens=25):
    original = controller._handoff_for_action

    def wrapped(*args, **kwargs):
        handoff = original(*args, **kwargs)
        handoff["resource_request"] = {"tokens":tokens}
        return handoff

    monkeypatch.setattr(controller, "_handoff_for_action", wrapped)


@pytest.mark.parametrize(
    "blocker",
    ["emergency", "policy", "budget", "approval", "rate-limit", "runtime"],
)
def test_managed_safety_gate_blocks_before_project_creation(
    tmp_path,
    monkeypatch,
    blocker,
):
    kwargs, backend = _managed_cycle_setup(tmp_path, monkeypatch)

    if blocker == "emergency":
        path = tmp_path / "emergency.json"
        set_emergency_stop(path, reason="test")
        kwargs["emergency_stop_path"] = str(path)
    elif blocker == "policy":
        path = tmp_path / "policy.json"
        path.write_text(
            json.dumps({"defaults":{"disabled":True}}),
            encoding="utf-8",
        )
        kwargs["policy_path"] = str(path)
    elif blocker == "budget":
        _with_resource_request(monkeypatch, tokens=25)
        policy = tmp_path / "policy.json"
        policy.write_text(
            json.dumps({"defaults":{"budgets":{"tokens":10}}}),
            encoding="utf-8",
        )
        kwargs["policy_path"] = str(policy)
        kwargs["budget_path"] = str(tmp_path / "budget.json")
    elif blocker == "approval":
        policy = tmp_path / "policy.json"
        policy.write_text(
            json.dumps({"defaults":{"approval_required_from":"low"}}),
            encoding="utf-8",
        )
        kwargs["policy_path"] = str(policy)
        kwargs["approval_path"] = str(tmp_path / "approvals.json")
    elif blocker == "rate-limit":
        path = tmp_path / "rate.json"
        store = RateLimitStore(path)
        for _ in range(20):
            decision = store.check_and_record(
                "repo:owner/repo",
                limit=20,
                window_seconds=3600,
            )
            assert decision.allowed is True
        kwargs["rate_limit_path"] = str(path)
    elif blocker == "runtime":
        state = runtime_state_for(backend)
        state.record_outcome(
            "owner/repo",
            "Fix autonomous regression",
            "promote",
        )

    result = run_control_cycle(**kwargs)

    assert _project_service(backend).list() == []
    assert result["managed_projects"] == []
    assert result["dispatches"] == []


def test_managed_backpressure_blocks_before_project_creation(
    tmp_path,
    monkeypatch,
):
    kwargs, backend = _managed_cycle_setup(
        tmp_path,
        monkeypatch,
        register_worker=False,
    )

    result = run_control_cycle(**kwargs)

    assert _project_service(backend).list() == []
    assert result["managed_projects"] == []


def test_successful_project_accounting_is_idempotent_across_cycles(
    tmp_path,
    monkeypatch,
):
    kwargs, backend = _managed_cycle_setup(tmp_path, monkeypatch)
    _with_resource_request(monkeypatch, tokens=25)
    budget_path = tmp_path / "budget.json"
    rate_path = tmp_path / "rate.json"
    kwargs["budget_path"] = str(budget_path)
    kwargs["rate_limit_path"] = str(rate_path)

    first = run_control_cycle(**kwargs)
    second = run_control_cycle(**kwargs)

    project_id = first["managed_projects"][0]["project_id"]
    assert second["managed_projects"][0]["project_id"] == project_id
    ledger = BudgetLedger(budget_path)
    assert ledger.payload["usage"]["owner/repo"]["tokens"] == 25
    assert ledger.payload["usage"]["__portfolio__"]["tokens"] == 25
    rate = RateLimitStore(rate_path)
    assert len(rate.events["repo:owner/repo"]) == 1


def test_accounting_recovers_after_post_creation_commit_failure(
    tmp_path,
    monkeypatch,
):
    kwargs, backend = _managed_cycle_setup(tmp_path, monkeypatch)
    _with_resource_request(monkeypatch, tokens=25)
    budget_path = tmp_path / "budget.json"
    rate_path = tmp_path / "rate.json"
    kwargs["budget_path"] = str(budget_path)
    kwargs["rate_limit_path"] = str(rate_path)

    real_commit = controller.commit_autonomous_admission
    calls = {"count":0}

    def crash_once(*args, **kwargs):
        calls["count"] += 1
        if calls["count"] == 1:
            raise RuntimeError("simulated crash before accounting commit")
        return real_commit(*args, **kwargs)

    monkeypatch.setattr(controller, "commit_autonomous_admission", crash_once)

    first = run_control_cycle(**kwargs)
    assert first["managed_projects"] == []
    projects = _project_service(backend).list()
    assert len(projects) == 1

    second = run_control_cycle(**kwargs)

    assert second["managed_projects"][0]["project_id"] == projects[0]["id"]
    ledger = BudgetLedger(budget_path)
    assert ledger.payload["usage"]["owner/repo"]["tokens"] == 25
    assert ledger.payload["usage"]["__portfolio__"]["tokens"] == 25
    rate = RateLimitStore(rate_path)
    assert len(rate.events["repo:owner/repo"]) == 1


def test_controller_restart_reuses_active_managed_project(
    tmp_path,
    monkeypatch,
):
    kwargs, backend = _managed_cycle_setup(tmp_path, monkeypatch)

    first = run_control_cycle(**kwargs)
    first_project = first["managed_projects"][0]
    first_workflow = first_project["current_workflow_id"]

    backend = open_backend(kwargs["database_path"])
    second = run_control_cycle(**kwargs)
    projects = _project_service(backend).list()

    assert len(projects) == 1
    assert second["managed_projects"][0]["project_id"] == first_project["project_id"]
    assert second["managed_projects"][0]["current_workflow_id"] == first_workflow


def test_terminal_same_fingerprint_is_skipped_but_new_evidence_creates_project(
    tmp_path,
    monkeypatch,
):
    kwargs, backend = _managed_cycle_setup(tmp_path, monkeypatch)

    first = run_control_cycle(**kwargs)
    first_id = first["managed_projects"][0]["project_id"]

    with backend.transaction() as db:
        db.execute(
            "UPDATE managed_projects SET status='DONE' WHERE id=?",
            (first_id,),
        )

    same = run_control_cycle(**kwargs)
    assert same["managed_projects"][0]["project_id"] == first_id
    assert same["managed_projects"][0]["created"] is False

    kwargs2, backend2 = _managed_cycle_setup(
        tmp_path,
        monkeypatch,
        evidence=["ci:regression", "issue:reopened"],
    )
    changed = run_control_cycle(**kwargs2)

    ids = {row["id"] for row in _project_service(backend2).list()}
    assert first_id in ids
    assert changed["managed_projects"][0]["project_id"] != first_id
    assert len(ids) == 2
