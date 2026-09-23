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


def test_dashboard_overview_is_bound_to_observability_api():
    assert "/v1/dashboard/overview" in DASHBOARD_HTML
    assert "async function loadOverview" in DASHBOARD_HTML
    assert 'id="overview-metrics"' in DASHBOARD_HTML


def test_dashboard_v3_has_usage_window_controls():
    for label in ("24h", "7d", "30d"):
        assert label in DASHBOARD_HTML
    assert "setDashboardWindow" in DASHBOARD_HTML


def test_dashboard_workers_view_is_bound_to_observability_api():
    assert "/v1/dashboard/workers" in DASHBOARD_HTML
    assert "async function loadWorkersView" in DASHBOARD_HTML
    assert "async function loadWorkerDetail" in DASHBOARD_HTML
    assert 'id="workers-list"' in DASHBOARD_HTML
    assert 'id="worker-detail"' in DASHBOARD_HTML


def test_dashboard_projects_view_is_bound_to_observability_api():
    assert "/v1/dashboard/projects" in DASHBOARD_HTML
    assert "async function loadProjectsView" in DASHBOARD_HTML
    assert "async function loadProjectDetail" in DASHBOARD_HTML
    assert 'id="projects-list"' in DASHBOARD_HTML
    assert 'id="project-detail"' in DASHBOARD_HTML


def test_dashboard_activity_view_is_bound_to_observability_api():
    assert "/v1/dashboard/activity" in DASHBOARD_HTML
    assert "async function loadActivityView" in DASHBOARD_HTML
    assert 'id="activity-list"' in DASHBOARD_HTML


def test_worker_detail_exposes_live_task_and_health_information():
    for label in ("Tâche actuelle", "Dernier heartbeat", "Progression"):
        assert label in DASHBOARD_HTML
    assert "progress_percent" in DASHBOARD_HTML
    assert "last_heartbeat" in DASHBOARD_HTML


def test_worker_detail_exposes_api_usage_breakdown():
    for label in ("Appels API", "Tokens", "Coût estimé"):
        assert label in DASHBOARD_HTML
    assert "estimated_cost_usd" in DASHBOARD_HTML


def test_worker_detail_exposes_execution_history():
    for label in ("Historique d’exécution", "Durée", "Résultat"):
        assert label in DASHBOARD_HTML
    assert "duration_seconds" in DASHBOARD_HTML
    assert "started_at" in DASHBOARD_HTML


def test_worker_detail_exposes_structured_recent_logs():
    for label in ("Logs récents", "Niveau", "Étape"):
        assert label in DASHBOARD_HTML
    assert "row.stage" in DASHBOARD_HTML
    assert "row.level" in DASHBOARD_HTML


def test_worker_detail_exposes_capabilities_and_health():
    for label in ("Capacités", "Santé du worker", "Concurrence"):
        assert label in DASHBOARD_HTML
    assert "worker.capabilities" in DASHBOARD_HTML
    assert "worker.status" in DASHBOARD_HTML
    assert "worker.max_concurrency" in DASHBOARD_HTML


def test_project_detail_exposes_progress_evidence():
    for label in ("Confiance", "Preuves", "Travail restant", "Blocages"):
        assert label in DASHBOARD_HTML
    assert "progress.estimate.evidence" in DASHBOARD_HTML
    assert "progress.estimate.remaining_work" in DASHBOARD_HTML
    assert "progress.estimate.blockers" in DASHBOARD_HTML


def test_project_detail_exposes_progress_components():
    for label in ("Code", "Tests", "Stabilité", "Release"):
        assert label in DASHBOARD_HTML
    assert "estimate.components" in DASHBOARD_HTML


def test_project_detail_exposes_commit_window_and_sources():
    for label in ("Fenêtre commits", "Commits Production-OS", "Commits branche GitHub"):
        assert label in DASHBOARD_HTML
    assert "commits.window" in DASHBOARD_HTML
    assert "commits.production_os" in DASHBOARD_HTML
    assert "commits.github_default_branch" in DASHBOARD_HTML
