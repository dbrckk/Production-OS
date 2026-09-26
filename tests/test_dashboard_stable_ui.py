from production_os.dashboard_ui import DASHBOARD_HTML


def test_stable_ui_exposes_layered_design_tokens():
    for token in (
        "--surface-0:",
        "--surface-1:",
        "--surface-2:",
        "--radius-card:",
        "--radius-control:",
        "--shadow-card:",
        "--control-height:",
    ):
        assert token in DASHBOARD_HTML


def test_stable_ui_has_keyboard_focus_and_reduced_motion_contracts():
    assert ":focus-visible" in DASHBOARD_HTML
    assert "@media (prefers-reduced-motion: reduce)" in DASHBOARD_HTML
    assert "animation-duration:.01ms" in DASHBOARD_HTML
    assert "transition-duration:.01ms" in DASHBOARD_HTML


def test_stable_ui_mobile_layout_prevents_document_overflow():
    assert "overflow-x:hidden" in DASHBOARD_HTML
    assert "overflow-wrap:anywhere" in DASHBOARD_HTML
    assert "@media(max-width:560px)" in DASHBOARD_HTML
    assert "flex-wrap:wrap" in DASHBOARD_HTML


def test_stable_ui_preserves_all_dashboard_destinations():
    for view in (
        "overview",
        "productions",
        "workers",
        "attention",
        "managed",
        "repositories",
    ):
        assert f'data-view="{view}"' in DASHBOARD_HTML


def test_stable_ui_preserves_operator_mutation_hooks():
    for hook in (
        "cancelLastProduction",
        "lastProductionManagedAction",
        "setWorkerState",
        "submitProductionInstruction",
    ):
        assert hook in DASHBOARD_HTML
