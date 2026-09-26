from production_os.dashboard_ui import DASHBOARD_HTML


def test_production_inbox_exposes_mobile_filter_tabs_and_counts():
    for label in ("Toutes", "Actives", "À revoir", "Problèmes", "Terminées"):
        assert label in DASHBOARD_HTML
    assert 'data-production-filter="all"' in DASHBOARD_HTML
    assert 'data-production-filter="active"' in DASHBOARD_HTML
    assert 'data-production-filter="review"' in DASHBOARD_HTML
    assert 'data-production-filter="problems"' in DASHBOARD_HTML
    assert 'data-production-filter="completed"' in DASHBOARD_HTML
    assert "setProductionFilter" in DASHBOARD_HTML
    assert "summary.total" in DASHBOARD_HTML


def test_production_inbox_requests_selected_server_filter():
    assert "productionFilter" in DASHBOARD_HTML
    assert '"&filter="+encodeURIComponent(productionFilter)' in DASHBOARD_HTML
    assert "loadProductionInbox" in DASHBOARD_HTML


def test_production_inbox_filter_does_not_duplicate_mutation_contracts():
    assert "productionInboxActions" in DASHBOARD_HTML
    assert "cancelLastProduction(this.dataset.projectId)" in DASHBOARD_HTML
    assert "lastProductionManagedAction(this.dataset.projectId,'verify')" in DASHBOARD_HTML
    assert "lastProductionManagedAction(this.dataset.projectId,'complete')" in DASHBOARD_HTML

def test_production_inbox_exposes_search_sort_and_shareable_url_state():
    assert 'id="production-search"' in DASHBOARD_HTML
    assert 'id="production-sort"' in DASHBOARD_HTML
    assert "Rechercher repo, objectif ou ID" in DASHBOARD_HTML
    assert "Priorité opérateur" in DASHBOARD_HTML
    assert "Activité récente" in DASHBOARD_HTML
    assert "setProductionSearch" in DASHBOARD_HTML
    assert "setProductionSort" in DASHBOARD_HTML
    assert 'params.set("production_filter",productionFilter)' in DASHBOARD_HTML
    assert 'params.set("production_q",productionSearch)' in DASHBOARD_HTML
    assert 'params.set("production_sort",productionSort)' in DASHBOARD_HTML
    assert 'q.get("production_filter")' in DASHBOARD_HTML
    assert 'q.get("production_q")' in DASHBOARD_HTML
    assert 'q.get("production_sort")' in DASHBOARD_HTML


def test_production_inbox_requests_server_search_and_sort():
    assert '"&q="+encodeURIComponent(productionSearch)' in DASHBOARD_HTML
    assert '"&sort="+encodeURIComponent(productionSort)' in DASHBOARD_HTML
    assert "summary.matching" in DASHBOARD_HTML

def test_production_inbox_has_shareable_inline_detail_panel():
    assert 'id="production-detail"' in DASHBOARD_HTML
    assert "openProductionInboxItem" in DASHBOARD_HTML
    assert "closeProductionInboxDetail" in DASHBOARD_HTML
    assert "loadProductionInboxDetail" in DASHBOARD_HTML
    assert '"/v1/dashboard/production-status?project_id="' in DASHBOARD_HTML
    assert "Historique des générations" in DASHBOARD_HTML
    assert "Vue Managed avancée" in DASHBOARD_HTML


def test_production_inbox_open_stays_in_productions_and_reuses_safe_actions():
    start = DASHBOARD_HTML.index("function productionInboxActions")
    end = DASHBOARD_HTML.index("function updateDashboardUrl", start)
    body = DASHBOARD_HTML[start:end]
    assert "openProductionInboxItem(this.dataset.projectId)" in body
    assert "cancelLastProduction(this.dataset.projectId)" in body
    assert "lastProductionManagedAction(this.dataset.projectId,'verify')" in body
    assert "lastProductionManagedAction(this.dataset.projectId,'complete')" in body
    assert "openLastProduction(this.dataset.projectId)" not in body


def test_production_inbox_target_restores_detail_even_outside_visible_list():
    start = DASHBOARD_HTML.index("async function loadProductionInbox")
    end = DASHBOARD_HTML.index("async function loadAttention", start)
    body = DASHBOARD_HTML[start:end]
    assert "loadProductionInboxDetail(appState.focus)" in body
    assert "CSS.escape(String(appState.focus))" in body

