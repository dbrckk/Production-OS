from production_os.dashboard_ui import DASHBOARD_HTML


def test_dashboard_css_uses_defined_border_token_for_cooperative_stages():
    assert "var(--border)" not in DASHBOARD_HTML
    assert ".coop-stage{" in DASHBOARD_HTML
    assert "border:1px solid var(--line)" in DASHBOARD_HTML


def test_dashboard_navigation_matches_eight_destinations_without_overflow_prone_six_column_grid():
    assert DASHBOARD_HTML.count('data-view="') >= 8
    assert "grid-template-columns:repeat(6,1fr)" not in DASHBOARD_HTML
    assert "grid-template-columns:repeat(4,minmax(0,1fr))" in DASHBOARD_HTML
    assert "grid-template-columns:repeat(2,minmax(0,1fr))" in DASHBOARD_HTML


def test_dashboard_exposes_visible_keyboard_focus_and_reduced_motion_contracts():
    assert ":focus-visible" in DASHBOARD_HTML
    assert "outline:3px solid var(--accent)" in DASHBOARD_HTML
    assert "@media(prefers-reduced-motion:reduce)" in DASHBOARD_HTML
    assert "transition-duration:.01ms!important" in DASHBOARD_HTML


def test_dashboard_long_content_wraps_instead_of_forcing_horizontal_scroll():
    assert ".card,.run,.status-card,.coop-stage{overflow-wrap:anywhere}" in DASHBOARD_HTML
    assert ".run-title{font-size:.85rem;font-weight:800;min-width:0;overflow-wrap:anywhere}" in DASHBOARD_HTML
    assert "min-height:44px" in DASHBOARD_HTML
