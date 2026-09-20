from production_os.control_plane import DASHBOARD_HTML


def test_dashboard_daily_surface_is_repo_instruction_only():
    assert 'id="repository"' in DASHBOARD_HTML
    assert 'id="instruction"' in DASHBOARD_HTML
    assert 'onclick="launchWorkflow()"' in DASHBOARD_HTML
    assert 'id="agent"' not in DASHBOARD_HTML
    assert 'id="budget"' not in DASHBOARD_HTML
    assert '<label>Operator token</label>' not in DASHBOARD_HTML
    assert "agent_preference:'codex'" in DASHBOARD_HTML
    assert "token_budget:30000" in DASHBOARD_HTML
    assert 'id="worker-status"' in DASHBOARD_HTML
    assert "visual-asset-production" in DASHBOARD_HTML
    assert "visual-asset-3d-production" in DASHBOARD_HTML


def test_dashboard_pairing_is_hidden_from_normal_surface():
    assert 'id="settings"' in DASHBOARD_HTML
    assert "localStorage.setItem(TOKEN_KEY,value)" in DASHBOARD_HTML
    assert 'style.display' in DASHBOARD_HTML


def test_dashboard_surfaces_visual_quality_without_extra_controls():
    assert 'id="visual-quality"' in DASHBOARD_HTML
    assert 'id="visual-quality-detail"' in DASHBOARD_HTML
    assert "Régénéré" in DASHBOARD_HTML
    assert "Qualité faible" in DASHBOARD_HTML
    assert "loadVisualQuality()" in DASHBOARD_HTML
    assert "setInterval(loadVisualQuality,10000)" in DASHBOARD_HTML


def test_dashboard_visual_quality_follows_selected_repository():
    assert "item.repository===selectedRepository" in DASHBOARD_HTML
    assert "addEventListener('change',loadVisualQuality)" in DASHBOARD_HTML


def test_dashboard_lists_per_asset_visual_quality_details():
    assert 'id="visual-assets-list"' in DASHBOARD_HTML
    assert "item.cache_hit?' · cache':''" in DASHBOARD_HTML
    assert "score '+score+' · essais '+attempts" in DASHBOARD_HTML
