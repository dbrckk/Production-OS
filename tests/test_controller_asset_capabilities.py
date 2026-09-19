from types import SimpleNamespace
import tempfile
from pathlib import Path

from production_os.controller import _handoff_for_action, _required_capabilities_for
from production_os.workers import WorkerRegistry, select_worker


def _assessment(profile="android-game", language="Kotlin"):
    return SimpleNamespace(
        profile=profile,
        evidence=SimpleNamespace(language=language),
    )


def test_visual_task_requires_visual_asset_worker():
    handoff = {
        "task": "Create and integrate new enemy sprites",
        "reuse_candidates": [
            {
                "source": "dbrckk/asset-forge",
                "target": "dbrckk/deadline-zero",
                "capability": "visual-asset-pipeline",
            }
        ],
    }
    required = _required_capabilities_for(_assessment(), handoff)
    assert "android" in required
    assert "visual-asset-production" in required


def test_asset_forge_availability_alone_does_not_require_visual_worker():
    handoff = {
        "task": "Restore CI and update unit tests",
        "reuse_candidates": [
            {
                "source": "dbrckk/asset-forge",
                "target": "dbrckk/deadline-zero",
                "capability": "visual-asset-pipeline",
            }
        ],
    }
    required = _required_capabilities_for(_assessment(), handoff)
    assert required == ["android"]


def test_visual_handoff_declares_asset_forge_machine_contract():
    action = SimpleNamespace(
        repository="dbrckk/deadline-zero",
        task="Create and integrate new enemy sprites",
        rationale="Missing production art",
        acceptance_criteria=["Sprites are integrated and validated"],
        evidence=["visual gap"],
        priority=100,
    )

    handoff = _handoff_for_action(action, [])

    contract = handoff["tool_contracts"]["asset_forge"]
    assert contract["request_schema"] == "asset-forge/production-request/v1"
    assert contract["report_schema"] == "asset-forge/production-report/v1"
    assert contract["command"] == "asset-forge fulfill"
    assert contract["required_capability"] == "visual-asset-production"


def test_3d_generation_handoff_declares_3d_worker_capability():
    action = SimpleNamespace(
        repository="dbrckk/zero-to-empire",
        task="Generate a new 3D character model",
        rationale="Missing character model",
        acceptance_criteria=["Model is generated and validated"],
        evidence=["3D asset gap"],
        priority=100,
    )

    handoff = _handoff_for_action(action, [])

    contract = handoff["tool_contracts"]["asset_forge"]
    assert contract["required_capability"] == "visual-asset-3d-production"


def test_android_visual_job_selects_ai_dev_style_worker():
    handoff = {"task": "Create and integrate new enemy sprites"}
    required = _required_capabilities_for(_assessment(), handoff)

    with tempfile.TemporaryDirectory() as td:
        registry = WorkerRegistry(Path(td) / "workers.json")
        registry.register(
            "ai-dev-server-1",
            [
                "android",
                "node",
                "python",
                "repo-analysis",
                "software-development",
                "visual-asset-production",
            ],
            1,
        )
        worker = select_worker(registry, required)

    assert worker is not None
    assert worker.worker_id == "ai-dev-server-1"
