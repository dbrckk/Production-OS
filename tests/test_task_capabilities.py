from production_os.task_capabilities import (
    VISUAL_CAPABILITY,
    VISUAL_3D_CAPABILITY,
    inferred_required_capabilities,
    is_visual_asset_task,
)


def test_visual_tasks_are_detected_from_task_text():
    assert is_visual_asset_task({"task": "Create and integrate new enemy sprites"})
    assert is_visual_asset_task({"task": "Improve the 3D character model and GLB"})
    assert is_visual_asset_task({"task": "Polish UI icons and vector graphics"})


def test_3d_generation_requires_dedicated_3d_worker():
    required = inferred_required_capabilities(
        {"task": "Create a new 3D character model and export GLB"}
    )
    assert VISUAL_CAPABILITY in required
    assert VISUAL_3D_CAPABILITY in required


def test_3d_validation_only_does_not_require_generation_capability():
    required = inferred_required_capabilities(
        {"task": "Validate the existing GLB and check mesh quality"}
    )
    assert VISUAL_CAPABILITY in required
    assert VISUAL_3D_CAPABILITY not in required


def test_non_visual_software_task_is_not_misclassified():
    assert not is_visual_asset_task({"task": "Restore CI and update unit tests"})
    assert not is_visual_asset_task({"task": "Refactor repository caching logic"})


def test_inferred_capabilities_preserve_explicit_requirements():
    required = inferred_required_capabilities(
        {
            "task": "Generate a sprite sheet",
            "required_capabilities": ["android"],
        }
    )
    assert required == ["android", VISUAL_CAPABILITY]
