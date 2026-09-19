from types import SimpleNamespace
import tempfile
from pathlib import Path

from production_os.controller import _required_capabilities_for
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
