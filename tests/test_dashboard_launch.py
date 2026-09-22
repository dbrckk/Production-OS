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
    assert "#settings{display:none" in DASHBOARD_HTML
    assert "classList.toggle('open'" in DASHBOARD_HTML


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
    assert "cohérence '+score+semantic+' · essais '+attempts" in DASHBOARD_HTML


def test_dashboard_visual_quality_has_previews_and_history():
    assert 'id="visual-quality-history"' in DASHBOARD_HTML
    assert "githubAssetUrls" in DASHBOARD_HTML
    assert "asset-thumb" in DASHBOARD_HTML
    assert "Promise.all(" in DASHBOARD_HTML
    assert "workflows.slice(0,5)" in DASHBOARD_HTML
    assert 'target="_blank"' in DASHBOARD_HTML


def test_dashboard_lists_semantic_art_score_per_asset():
    assert "item.semantic_score" in DASHBOARD_HTML
    assert "' · art '+Number(item.semantic_score).toFixed(2)" in DASHBOARD_HTML


def test_dashboard_surfaces_asset_library_version_and_preference():
    assert "libraryVersion" in DASHBOARD_HTML
    assert "libraryQuality" in DASHBOARD_HTML
    assert "library_preferred" in DASHBOARD_HTML
    assert "lib v" in DASHBOARD_HTML
    assert "qualité lib" in DASHBOARD_HTML


def test_dashboard_pairing_modal_is_mobile_visible_and_closable():
    assert '#settings.open{display:block}' in DASHBOARD_HTML
    assert 'function setSettingsOpen(open)' in DASHBOARD_HTML
    assert 'setSettingsOpen(false)' in DASHBOARD_HTML
    assert 'id="settings-button"' in DASHBOARD_HTML


def test_dashboard_worker_status_uses_authenticated_api():
    assert "const data=await api('/v1/workers')" in DASHBOARD_HTML
    assert "fetch('/v1/workers')" not in DASHBOARD_HTML
    assert "Worker : appairage requis via ⚙." in DASHBOARD_HTML


def test_dashboard_launch_opens_pairing_when_token_missing():
    assert "if(!token()){" in DASHBOARD_HTML
    assert "Appairage requis avant le premier lancement." in DASHBOARD_HTML
    assert "setSettingsOpen(true)" in DASHBOARD_HTML


def test_dashboard_pairing_validates_operator_token_before_accepting():
    assert "await api('/v1/workers')" in DASHBOARD_HTML
    assert "Token opérateur invalide." in DASHBOARD_HTML
    assert "Vérification de l’appairage..." in DASHBOARD_HTML


def test_dashboard_v2_surfaces_runtime_health_and_recent_runs():
    assert 'id="server-state"' in DASHBOARD_HTML
    assert 'id="pair-state"' in DASHBOARD_HTML
    assert 'id="worker-state"' in DASHBOARD_HTML
    assert 'id="recent-runs"' in DASHBOARD_HTML
    assert "loadRecentRuns()" in DASHBOARD_HTML
    assert "refreshDashboard()" in DASHBOARD_HTML


def test_dashboard_v2_explains_offline_worker_and_queued_launch():
    assert 'id="runtime-warning"' in DASHBOARD_HTML
    assert "Worker hors ligne" in DASHBOARD_HTML
    assert "Production créée · en attente du worker" in DASHBOARD_HTML


def test_dashboard_v2_has_readable_auth_errors():
    assert "Token opérateur refusé par le serveur." in DASHBOARD_HTML
    assert "Ce token n’a pas le rôle requis." in DASHBOARD_HTML
    assert "r.status===401" in DASHBOARD_HTML
    assert "r.status===403" in DASHBOARD_HTML


def test_dashboard_v2_has_mobile_primary_launch_action():
    assert 'id="launch-button"' in DASHBOARD_HTML
    assert "Lancer la production" in DASHBOARD_HTML
    assert "@media(max-width:560px)" in DASHBOARD_HTML
