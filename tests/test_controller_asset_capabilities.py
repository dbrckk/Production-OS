from types import SimpleNamespace

from production_os.controller import _required_capabilities_for


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
