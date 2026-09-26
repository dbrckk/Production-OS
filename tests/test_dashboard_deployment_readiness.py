from __future__ import annotations

from production_os.control_plane import ControlPlane
import production_os.dashboard_service as dashboard_service


def test_deployment_readiness_flags_unverified_execution_and_missing_backups(
    tmp_path,
    monkeypatch,
):
    control = ControlPlane(str(tmp_path / "deployment-unready.sqlite"))
    monkeypatch.setattr(
        dashboard_service,
        "backup_storage_inventory",
        lambda _backend: {
            "status":"unconfigured",
            "backend_kind":"sqlite",
        },
    )

    payload = control.dashboard.deployment_readiness()

    assert payload["schema_version"] == "production-os/deployment-readiness/v1"
    assert payload["status"] == "degraded"
    assert payload["execution"]["mode"] == "unverified"
    assert payload["execution"]["available_workers"] == 0
    assert payload["execution"]["github_actions_dispatch"] is False
    assert payload["storage"] == {
        "backend":"sqlite",
        "recovery":"unconfigured",
        "backup_status":"unconfigured",
    }
    assert {item["code"] for item in payload["issues"]} == {
        "execution_path_unverified",
        "backup_unconfigured",
    }


def test_deployment_readiness_is_ready_with_available_worker_and_backups(
    tmp_path,
    monkeypatch,
):
    control = ControlPlane(str(tmp_path / "deployment-worker.sqlite"))
    control.workers.register("worker-a", [], 2)
    monkeypatch.setattr(
        dashboard_service,
        "backup_storage_inventory",
        lambda _backend: {
            "status":"ready",
            "backend_kind":"sqlite",
        },
    )

    payload = control.dashboard.deployment_readiness()

    assert payload["status"] == "ready"
    assert payload["execution"]["mode"] == "immediate"
    assert payload["execution"]["available_workers"] == 1
    assert payload["storage"]["recovery"] == "ready"
    assert payload["issues"] == []


def test_deployment_readiness_accepts_configured_github_actions_dispatch(
    tmp_path,
    monkeypatch,
):
    control = ControlPlane(str(tmp_path / "deployment-actions.sqlite"))
    control.dashboard_control.github = object()
    control.dashboard_control.actions_repository = "dbrckk/ai-dev-server"
    control.dashboard_control.actions_workflow = "production-os-actions-worker.yml"
    monkeypatch.setattr(
        dashboard_service,
        "backup_storage_inventory",
        lambda _backend: {
            "status":"ready",
            "backend_kind":"sqlite",
        },
    )

    payload = control.dashboard.deployment_readiness()

    assert payload["status"] == "ready"
    assert payload["execution"]["mode"] == "github-actions-dispatch"
    assert payload["execution"]["github_actions_dispatch"] is True
    assert payload["execution"]["actions_repository"] == "dbrckk/ai-dev-server"
    assert (
        payload["execution"]["actions_workflow"]
        == "production-os-actions-worker.yml"
    )
