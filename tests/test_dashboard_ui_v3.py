from production_os.dashboard_ui import DASHBOARD_HTML


def test_dashboard_has_primary_views_and_clickable_entities():
    for label in ("Vue générale", "Projets", "Workers", "Activité"):
        assert label in DASHBOARD_HTML
    for view in ("overview","projects","workers","activity"):
        assert f'data-view="{view}"' in DASHBOARD_HTML


def test_polling_does_not_reload_or_replace_location():
    assert "location.reload(" not in DASHBOARD_HTML
    assert "window.location =" not in DASHBOARD_HTML
    assert "history.replaceState" in DASHBOARD_HTML


def test_dashboard_has_worker_and_project_detail_tabs():
    for label in ("Aperçu","Tâches","Logs","API","Historique","Avancement","Commits","Workflows","Qualité"):
        assert label in DASHBOARD_HTML


def test_dashboard_preserves_launch_and_mobile_accessibility():
    assert 'id="repository"' in DASHBOARD_HTML
    assert 'id="instruction"' in DASHBOARD_HTML
    assert "Lancer la production" in DASHBOARD_HTML
    assert 'name="viewport"' in DASHBOARD_HTML
    assert "@media" in DASHBOARD_HTML
    assert "overflow-x:hidden" in DASHBOARD_HTML.replace(" ","")
    assert "aria-live" in DASHBOARD_HTML
    assert "Pause worker" not in DASHBOARD_HTML
    assert "Annuler la tâche" not in DASHBOARD_HTML


def test_dashboard_v3_is_bound_to_observability_read_apis():
    for endpoint in (
        "/v1/dashboard/overview",
        "/v1/dashboard/projects",
        "/v1/dashboard/workers",
        "/v1/dashboard/activity",
    ):
        assert endpoint in DASHBOARD_HTML
    for function_name in (
        "loadOverview",
        "loadProjectsView",
        "loadWorkersView",
        "loadActivityView",
        "loadProjectDetail",
        "loadWorkerDetail",
    ):
        assert f"function {function_name}" in DASHBOARD_HTML or f"async function {function_name}" in DASHBOARD_HTML
