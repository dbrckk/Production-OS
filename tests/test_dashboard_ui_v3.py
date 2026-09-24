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


def test_project_detail_exposes_api_usage_breakdown():
    for label in ("Fournisseur", "Modèle", "Appels API projet", "Tokens projet"):
        assert label in DASHBOARD_HTML
    assert "usage.providers" in DASHBOARD_HTML
    assert "usage.timeline" in DASHBOARD_HTML


def test_worker_control_tab_has_safe_actions():
    html = DASHBOARD_HTML
    for action in ("pause", "resume", "drain", "kick"):
        assert f'data-control-action="{action}"' in html
    assert 'data-control-action="cancel-current"' in html
    assert 'data-control-action="retry"' in html
    assert "confirmControlAction" in html
    assert "runWorkerControl" in html


def test_ui_distinguishes_requested_from_acknowledged():
    assert "Action demandée" in DASHBOARD_HTML
    assert "Confirmée par le worker" in DASHBOARD_HTML
    assert "Réveil automatique prévu ≤ 5 min" in DASHBOARD_HTML
    assert "Réveil GitHub Actions demandé" in DASHBOARD_HTML


def test_control_refresh_preserves_navigation_and_scroll_contract():
    assert "history.replaceState" in DASHBOARD_HTML
    assert "window.scrollY" in DASHBOARD_HTML
    assert "window.scrollTo" in DASHBOARD_HTML
    assert "location.reload(" not in DASHBOARD_HTML


def test_overview_renders_operational_alerts():
    assert "Alertes opérationnelles" in DASHBOARD_HTML
    assert "data.alerts" in DASHBOARD_HTML
    assert "item.severity" in DASHBOARD_HTML
    assert "item.message" in DASHBOARD_HTML


def test_dashboard_has_autopilot_primary_view():
    assert 'data-view="autopilot"' in DASHBOARD_HTML
    assert 'id="view-autopilot"' in DASHBOARD_HTML
    assert 'id="autopilot-list"' in DASHBOARD_HTML
    assert "async function loadAutopilot" in DASHBOARD_HTML
    assert "/v1/dashboard/autopilot?limit=50" in DASHBOARD_HTML


def test_autopilot_view_exposes_queue_explanations():
    for label in (
        "Worker préféré",
        "Capacités requises",
        "Chemin critique",
        "ETA",
        "Capacité worker saturée",
        "Worker en pause ou drain",
    ):
        assert label in DASHBOARD_HTML
    assert "row.predicted_minutes" in DASHBOARD_HTML
    assert "row.wait_reason" in DASHBOARD_HTML
    assert "row.preferred_worker" in DASHBOARD_HTML


def test_autopilot_navigation_preserves_polling_scroll_contract():
    assert "autopilot:loadAutopilot" in DASHBOARD_HTML
    assert "window.scrollY" in DASHBOARD_HTML
    assert "window.scrollTo" in DASHBOARD_HTML
    assert "location.reload(" not in DASHBOARD_HTML


def test_autopilot_surfaces_degraded_ranking_state():
    assert "Ranking :" in DASHBOARD_HTML
    assert "Dégradé · workflow de référence indisponible" in DASHBOARD_HTML
    assert 'row.ranking_status==="degraded"' in DASHBOARD_HTML


def test_autopilot_view_shows_capacity_summary():
    for label in (
        "Prêts maintenant",
        "Bloqués",
        "Slots libres",
        "ETA connue",
        "Couverture",
    ):
        assert label in DASHBOARD_HTML
    assert "summary.ready_now" in DASHBOARD_HTML
    assert "summary.free_slots" in DASHBOARD_HTML
    assert "summary.known_eta_minutes" in DASHBOARD_HTML


def test_activity_view_renders_operator_control_audit():
    assert "Audit des contrôles" in DASHBOARD_HTML
    assert "/v1/dashboard/control-audit?limit=50" in DASHBOARD_HTML
    assert "row.requested_by" in DASHBOARD_HTML
    assert "row.outcome" in DASHBOARD_HTML
    assert "row.error_code" in DASHBOARD_HTML


def test_overview_renders_operational_health():
    assert "/v1/dashboard/health" in DASHBOARD_HTML
    assert "Santé opérationnelle" in DASHBOARD_HTML
    assert "health.status" in DASHBOARD_HTML
    assert "health.reasons" in DASHBOARD_HTML


def test_worker_control_exposes_recover_stuck_only_from_recoverable_jobs():
    assert 'data-control-action="recover-stuck"' in DASHBOARD_HTML
    assert "detail.recoverable_jobs" in DASHBOARD_HTML
    assert "Récupérer ce job bloqué" in DASHBOARD_HTML


def test_overview_renders_and_acknowledges_durable_incidents():
    assert "/v1/dashboard/incidents?limit=20" in DASHBOARD_HTML
    assert "async function acknowledgeIncident" in DASHBOARD_HTML
    assert "Acquitter" in DASHBOARD_HTML
    assert "item.target_type" in DASHBOARD_HTML
    assert "item.target_id" in DASHBOARD_HTML


def test_overview_renders_server_backed_incident_playbooks():
    assert "renderIncidentPlaybook" in DASHBOARD_HTML
    assert "item.playbook" in DASHBOARD_HTML
    assert "suggestion.availability" in DASHBOARD_HTML
    assert "suggestion.reason" in DASHBOARD_HTML
    assert 'data-playbook-action="' in DASHBOARD_HTML


def test_incident_playbook_actions_are_explicit_and_reuse_control_api():
    assert "runIncidentPlaybookAction" in DASHBOARD_HTML
    assert "runWorkerControl(workerId,action,jobKey||null,incidentId||null)" in DASHBOARD_HTML
    assert "confirmControlAction" in DASHBOARD_HTML
    assert "disabled" in DASHBOARD_HTML


def test_incident_inspection_playbooks_only_navigate():
    assert 'action==="inspect-worker"' in DASHBOARD_HTML
    assert 'action==="inspect-job"' in DASHBOARD_HTML
    assert "openWorker(encodeURIComponent(workerId))" in DASHBOARD_HTML


def test_incident_playbook_actions_send_incident_id():
    assert "data-incident-id" in DASHBOARD_HTML
    assert "this.dataset.incidentId" in DASHBOARD_HTML
    assert "body.incident_id=incidentId" in DASHBOARD_HTML


def test_activity_view_renders_remediation_history():
    assert "/v1/dashboard/remediations?limit=50" in DASHBOARD_HTML
    assert "Historique des remédiations" in DASHBOARD_HTML
    assert "row.incident_id" in DASHBOARD_HTML
    assert "row.outcome" in DASHBOARD_HTML
    assert "row.requested_by" in DASHBOARD_HTML


def test_direct_worker_controls_do_not_require_incident_id():
    assert "async function runWorkerControl(workerId,action,jobKey=null,incidentId=null)" in DASHBOARD_HTML
    assert "if(incidentId)body.incident_id=incidentId" in DASHBOARD_HTML


def test_activity_view_renders_remediation_verification_status():
    assert "row.verification_state" in DASHBOARD_HTML
    assert "row.verification_checks" in DASHBOARD_HTML
    assert "row.verified_at" in DASHBOARD_HTML
    assert "résultat " in DASHBOARD_HTML
    assert "vérification " in DASHBOARD_HTML


def test_activity_view_renders_remediation_analytics_with_sample_sizes():
    assert "/v1/dashboard/remediation-analytics?window=" in DASHBOARD_HTML
    assert "Analytics des remédiations" in DASHBOARD_HTML
    assert "Taux de résolution observé" in DASHBOARD_HTML
    assert "Échantillon d’efficacité" in DASHBOARD_HTML
    assert "remediationSummary.effectiveness_denominator" in DASHBOARD_HTML
    assert "row.effectiveness_denominator" in DASHBOARD_HTML
    assert "Par action" in DASHBOARD_HTML
    assert "Par incident" in DASHBOARD_HTML


def test_activity_view_renders_remediation_recurrence_status():
    assert "row.recurrence_state" in DASHBOARD_HTML
    assert "row.recurred_at" in DASHBOARD_HTML
    assert "Surveillance de récidive" in DASHBOARD_HTML
    assert "Récidives observées" in DASHBOARD_HTML
    assert "Taux de récidive observé" in DASHBOARD_HTML
    assert "remediationSummary.recurrence_denominator" in DASHBOARD_HTML
    assert "remediationSummary.observed_recurrence_rate" in DASHBOARD_HTML


def test_activity_view_renders_remediation_durability_timing():
    assert "Médiane avant récidive" in DASHBOARD_HTML
    assert "Âge médian des résolutions surveillées" in DASHBOARD_HTML
    assert "remediationSummary.median_time_to_recurrence_seconds" in DASHBOARD_HTML
    assert "remediationSummary.min_time_to_recurrence_seconds" in DASHBOARD_HTML
    assert "remediationSummary.max_time_to_recurrence_seconds" in DASHBOARD_HTML
    assert "remediationSummary.median_watching_age_seconds" in DASHBOARD_HTML


def test_launch_repository_picker_is_server_backed():
    assert "/v1/dashboard/repositories" in DASHBOARD_HTML
    assert "https://api.github.com/users/dbrckk/repos" not in DASHBOARD_HTML
    assert "async function loadRepositories" in DASHBOARD_HTML


def test_mobile_launch_flow_remains_repo_plus_instruction():
    assert 'id="repository"' in DASHBOARD_HTML
    assert 'id="instruction"' in DASHBOARD_HTML
    assert "Lancer la production" in DASHBOARD_HTML
    assert "async function launchWorkflow" in DASHBOARD_HTML
    assert "final_goal:task" in DASHBOARD_HTML
