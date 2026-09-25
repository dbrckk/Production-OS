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
    assert "api('/v1/dashboard/launch'" in DASHBOARD_HTML
    assert "instruction:task" in DASHBOARD_HTML


def test_overview_renders_storage_maintenance_card():
    assert "/v1/dashboard/maintenance" in DASHBOARD_HTML
    assert "Stockage & rétention" in DASHBOARD_HTML
    assert "maintenance.database_size_bytes" in DASHBOARD_HTML
    assert "maintenance.prunable_candidate_rows" in DASHBOARD_HTML
    assert "maintenance.protected_candidate_rows" in DASHBOARD_HTML
    assert "row.retention_days" in DASHBOARD_HTML
    assert "row.invalid_timestamps" in DASHBOARD_HTML


def test_storage_maintenance_failure_does_not_break_overview():
    assert '.catch(function(){' in DASHBOARD_HTML
    assert 'status:"unknown"' in DASHBOARD_HTML
    assert "Diagnostic de stockage indisponible." in DASHBOARD_HTML


def test_storage_retention_ui_separates_prunable_and_protected_rows():
    assert "maintenance.prunable_candidate_rows" in DASHBOARD_HTML
    assert "maintenance.protected_candidate_rows" in DASHBOARD_HTML
    assert "Prunables :" in DASHBOARD_HTML
    assert "Protégées :" in DASHBOARD_HTML
    assert "row.prunable_candidate_rows" in DASHBOARD_HTML
    assert "row.protected_candidate_rows" in DASHBOARD_HTML


def test_retention_prune_requires_explicit_confirmation_and_exact_phrase():
    assert "async function pruneExpiredHistory" in DASHBOARD_HTML
    assert "window.confirm(" in DASHBOARD_HTML
    assert 'confirm:"PRUNE_EXPIRED_HISTORY"' in DASHBOARD_HTML
    assert "expected_candidate_rows:count" in DASHBOARD_HTML
    assert "/v1/dashboard/maintenance/prune" in DASHBOARD_HTML


def test_retention_prune_button_only_renders_for_positive_prunable_count():
    assert "const pruneButton=prunable>0" in DASHBOARD_HTML
    assert 'data-prunable="' in DASHBOARD_HTML
    assert "Nettoyer l’historique expiré" in DASHBOARD_HTML


def test_overview_renders_backup_readiness_and_safe_create_button():
    assert "/v1/dashboard/backups" in DASHBOARD_HTML
    assert "Sauvegarde" in DASHBOARD_HTML
    assert "Dernière sauvegarde vérifiée" in DASHBOARD_HTML
    assert "createVerifiedBackup" in DASHBOARD_HTML
    assert "CREATE_VERIFIED_BACKUP" in DASHBOARD_HTML
    assert "backups.create_supported===true" in DASHBOARD_HTML
    assert "Restauration" in DASHBOARD_HTML


def test_backup_ui_does_not_render_server_paths():
    assert "PRODUCTION_OS_BACKUP_DIR" not in DASHBOARD_HTML
    assert "backup_dir" not in DASHBOARD_HTML
    assert "database_path" not in DASHBOARD_HTML


def test_backup_catalog_exposes_restore_readiness_and_safe_staging():
    assert "verifyBackupReadiness" in DASHBOARD_HTML
    assert "VERIFY_BACKUP_FOR_RESTORE" in DASHBOARD_HTML
    assert "Vérifier restaurabilité" in DASHBOARD_HTML
    assert "/verify" in DASHBOARD_HTML
    assert "Aucune restauration ne sera exécutée" in DASHBOARD_HTML
    assert "restauration toujours désactivée" in DASHBOARD_HTML
    assert "stageBackupRestore" in DASHBOARD_HTML
    assert "STAGE_VERIFIED_RESTORE" in DASHBOARD_HTML
    assert "Préparer restauration" in DASHBOARD_HTML
    assert "/stage-restore" in DASHBOARD_HTML
    assert "activation désactivée" in DASHBOARD_HTML


def test_restore_staging_ui_never_exposes_live_activation_or_paths():
    assert "Restaurer maintenant" not in DASHBOARD_HTML
    assert "RESTORE_BACKUP" not in DASHBOARD_HTML
    assert "ACTIVATE_RESTORE" not in DASHBOARD_HTML
    assert "PRODUCTION_OS_BACKUP_DIR" not in DASHBOARD_HTML
    assert "backup_path" not in DASHBOARD_HTML


def test_dashboard_has_managed_projects_view():
    assert 'data-view="managed"' in DASHBOARD_HTML
    assert 'id="view-managed"' in DASHBOARD_HTML
    assert "async function loadManagedProjects" in DASHBOARD_HTML
    assert "/v1/managed-projects" in DASHBOARD_HTML


def test_managed_projects_view_exposes_safe_review_and_attention_actions():
    assert 'status==="REVIEW_REQUIRED"||status==="NEEDS_ATTENTION"' in DASHBOARD_HTML
    assert 'const canComplete=status==="REVIEW_REQUIRED"' in DASHBOARD_HTML
    assert "Ajouter instruction" in DASHBOARD_HTML
    assert "Retester" in DASHBOARD_HTML
    assert "Valider DONE" in DASHBOARD_HTML
    assert "managedAction" in DASHBOARD_HTML
    assert 'confirm:"MARK_PROJECT_DONE"' in DASHBOARD_HTML


def test_managed_projects_navigation_preserves_existing_polling_contract():
    assert "managed:loadManagedProjects" in DASHBOARD_HTML
    assert "window.scrollY" in DASHBOARD_HTML
    assert "window.scrollTo" in DASHBOARD_HTML
    assert "location.reload(" not in DASHBOARD_HTML


def test_managed_projects_mobile_creation_form_is_inline_and_server_backed():
    assert 'id="managed-create-repository"' in DASHBOARD_HTML
    assert 'id="managed-create-goal"' in DASHBOARD_HTML
    assert 'id="managed-create-budget"' in DASHBOARD_HTML
    assert 'id="managed-create-agent"' in DASHBOARD_HTML
    assert "async function createManagedProject" in DASHBOARD_HTML
    assert '"/v1/managed-projects"' in DASHBOARD_HTML
    assert "agent_preference:agent" in DASHBOARD_HTML
    assert "token_budget:Math.floor(budget)" in DASHBOARD_HTML


def test_managed_project_instruction_uses_inline_textarea_not_prompt():
    assert "window.prompt(" not in DASHBOARD_HTML
    assert 'id="managed-instruction-' in DASHBOARD_HTML
    assert 'placeholder="Instruction supplémentaire"' in DASHBOARD_HTML
    assert "managedAction(this.dataset.projectId,'instructions')" in DASHBOARD_HTML


def test_managed_projects_mobile_view_renders_generation_history():
    assert "Génération actuelle" in DASHBOARD_HTML
    assert "Générations :" in DASHBOARD_HTML
    assert "row.runs" in DASHBOARD_HTML
    assert "run.generation" in DASHBOARD_HTML
    assert "run.kind" in DASHBOARD_HTML


def test_managed_repository_picker_reuses_server_repository_discovery():
    assert "managed-create-repository" in DASHBOARD_HTML
    assert "api('/v1/dashboard/repositories')" in DASHBOARD_HTML
    assert "https://api.github.com" not in DASHBOARD_HTML


def test_backup_overview_renders_restore_activation_history():
    assert "Historique des activations" in DASHBOARD_HTML
    assert "backups.activations" in DASHBOARD_HTML
    assert "row.candidate_id" in DASHBOARD_HTML
    assert "row.rollback_backup_id" in DASHBOARD_HTML
    assert "row.activated_at" in DASHBOARD_HTML
    assert "Restaurer maintenant" not in DASHBOARD_HTML


def test_backup_overview_renders_storage_inventory_read_only():
    assert "backups.storage" in DASHBOARD_HTML
    assert "Stockage backup" in DASHBOARD_HTML
    assert "backupStorage.total_size_bytes" in DASHBOARD_HTML
    assert "backupStorage.backup_count" in DASHBOARD_HTML
    assert "backupStorage.restore_candidate_count" in DASHBOARD_HTML
    assert "backupStorage.activation_receipt_count" in DASHBOARD_HTML
    assert "backupStorage.temp_file_count" in DASHBOARD_HTML
    assert "backupStorage.unknown_file_count" in DASHBOARD_HTML
    assert "Nettoyer les backups" not in DASHBOARD_HTML
    assert "Supprimer les backups" not in DASHBOARD_HTML


def test_backup_temp_cleanup_ui_is_guarded_and_stale_only():
    assert "async function pruneStaleBackupTemps" in DASHBOARD_HTML
    assert 'confirm:"PRUNE_STALE_BACKUP_TEMPS"' in DASHBOARD_HTML
    assert "expected_candidate_count:count" in DASHBOARD_HTML
    assert "/v1/dashboard/backups/prune-temp" in DASHBOARD_HTML
    assert "const staleTempCount=Number(backupStorage.stale_temp_count||0)" in DASHBOARD_HTML
    assert "const backupTempPruneButton=staleTempCount>0" in DASHBOARD_HTML
    assert "Nettoyer temporaires anciens" in DASHBOARD_HTML
    assert "Nettoyer les backups" not in DASHBOARD_HTML
    assert "Supprimer les backups" not in DASHBOARD_HTML


def test_backup_overview_renders_filesystem_capacity_read_only():
    assert "backupStorage.filesystem" in DASHBOARD_HTML
    assert "backupFilesystem.status" in DASHBOARD_HTML
    assert "backupFilesystem.available_bytes" in DASHBOARD_HTML
    assert "backupFilesystem.used_percent" in DASHBOARD_HTML
    assert "Filesystem :" in DASHBOARD_HTML
    assert "Disponible :" in DASHBOARD_HTML
    assert "Nettoyer automatiquement" not in DASHBOARD_HTML
    assert "AUTO_PRUNE" not in DASHBOARD_HTML

def test_backup_overview_renders_verified_backup_age_distribution():
    assert "backupStorage.backup_age" in DASHBOARD_HTML
    assert "backupAge.buckets" in DASHBOARD_HTML
    assert "Âge backups vérifiés" in DASHBOARD_HTML
    assert "backupAgeBuckets.under_24h" in DASHBOARD_HTML
    assert "backupAgeBuckets.one_to_seven_days" in DASHBOARD_HTML
    assert "backupAgeBuckets.seven_to_thirty_days" in DASHBOARD_HTML
    assert "backupAgeBuckets.over_thirty_days" in DASHBOARD_HTML
    assert "timestamps invalides" in DASHBOARD_HTML

def test_backup_overview_renders_retention_preview_read_only():
    assert "backupStorage.retention_preview" in DASHBOARD_HTML
    assert "backupRetention.protected_reasons" in DASHBOARD_HTML
    assert "Prévisualisation rétention" in DASHBOARD_HTML
    assert "backupRetention.candidate_count" in DASHBOARD_HTML
    assert "backupRetention.candidate_bytes" in DASHBOARD_HTML
    assert "backupRetention.protected_count" in DASHBOARD_HTML
    assert "historique restauration" in DASHBOARD_HTML
    assert "Supprimer les vieux backups" not in DASHBOARD_HTML

def test_backup_retention_cleanup_ui_requires_preview_fingerprint():
    assert "pruneExpiredBackups" in DASHBOARD_HTML
    assert "PRUNE_EXPIRED_VERIFIED_BACKUPS" in DASHBOARD_HTML
    assert "expected_candidate_fingerprint" in DASHBOARD_HTML
    assert "backupRetention.candidate_fingerprint" in DASHBOARD_HTML
    assert "Nettoyer anciens backups" in DASHBOARD_HTML
    assert "this.dataset.retentionFingerprint" in DASHBOARD_HTML

def test_one_tap_production_is_primary_and_uses_server_managed_launch():
    assert 'id="one-tap-production"' in DASHBOARD_HTML
    assert DASHBOARD_HTML.index('id="one-tap-production"') < DASHBOARD_HTML.index('class="v3-nav"')
    assert "async function launchWorkflow" in DASHBOARD_HTML
    assert "api('/v1/dashboard/launch'" in DASHBOARD_HTML
    assert "repository:repository" in DASHBOARD_HTML
    assert "instruction:task" in DASHBOARD_HTML
    launch_start = DASHBOARD_HTML.index("async function launchWorkflow")
    launch_end = DASHBOARD_HTML.index("async function refreshDashboard", launch_start)
    launch_body = DASHBOARD_HTML[launch_start:launch_end]
    assert "/v1/workflows" not in launch_body
    assert "token_budget" not in launch_body
    assert "agent_preference" not in launch_body
    assert "Production lancée et persistante" in launch_body


def test_managed_technical_creation_options_are_collapsed_by_default():
    assert '<details class="advanced-options">' in DASHBOARD_HTML
    assert "<summary>Options avancées</summary>" in DASHBOARD_HTML
    assert 'id="managed-create-budget"' in DASHBOARD_HTML
    assert 'id="managed-create-agent"' in DASHBOARD_HTML
    assert '<details class="advanced-options" open' not in DASHBOARD_HTML


def test_managed_view_can_be_restored_from_navigation_query():
    assert '["attention","overview","projects","workers","autopilot","managed","activity"]' in DASHBOARD_HTML

def test_attention_center_is_default_mobile_view():
    assert 'data-view="attention"' in DASHBOARD_HTML
    assert 'id="view-attention" class="v3-view active"' in DASHBOARD_HTML
    assert "À faire maintenant" in DASHBOARD_HTML
    assert 'const appState={view:"attention"' in DASHBOARD_HTML
    assert '["attention","overview","projects","workers","autopilot","managed","activity"]' in DASHBOARD_HTML


def test_attention_center_uses_server_aggregated_feed_and_action_counts():
    assert "/v1/dashboard/attention?limit=50" in DASHBOARD_HTML
    assert "async function loadAttention" in DASHBOARD_HTML
    assert "summary.action_required" in DASHBOARD_HTML
    assert "summary.projects_to_review" in DASHBOARD_HTML
    assert "summary.projects_needing_attention" in DASHBOARD_HTML
    assert "summary.blocked_jobs" in DASHBOARD_HTML
    assert "summary.incidents" in DASHBOARD_HTML
    assert "summary.recently_completed" in DASHBOARD_HTML
    assert "CI / validation" in DASHBOARD_HTML
    assert "Rien d’urgent." in DASHBOARD_HTML


def test_attention_items_navigate_to_existing_operational_views():
    assert "openAttentionItem" in DASHBOARD_HTML
    assert "view:view||\"overview\"" in DASHBOARD_HTML
    assert "focus:targetId||null" in DASHBOARD_HTML
    assert "Ouvrir" in DASHBOARD_HTML
    assert "attention:loadAttention" in DASHBOARD_HTML

def test_attention_center_exposes_contextual_server_actions():
    assert "renderAttentionActions" in DASHBOARD_HTML
    assert "attentionManagedAction" in DASHBOARD_HTML
    assert "acknowledgeAttentionIncident" in DASHBOARD_HTML
    assert "attentionPlaybookAction" in DASHBOARD_HTML
    assert 'name==="verify"||name==="complete"' in DASHBOARD_HTML
    assert 'name==="acknowledge"' in DASHBOARD_HTML
    assert 'name==="playbook"' in DASHBOARD_HTML
    assert 'confirm:"MARK_PROJECT_DONE"' in DASHBOARD_HTML
    assert "Valider définitivement ce projet comme DONE ?" in DASHBOARD_HTML


def test_attention_open_deep_links_to_exact_managed_project_or_job():
    assert "focus:targetId||null" in DASHBOARD_HTML
    assert 'appState.focus=q.get("target")||null' in DASHBOARD_HTML
    assert 'params.set("target",appState.focus)' in DASHBOARD_HTML
    assert 'data-managed-project-id="' in DASHBOARD_HTML
    assert 'data-job-key="' in DASHBOARD_HTML
    assert "attention-focus" in DASHBOARD_HTML
    assert "scrollIntoView" in DASHBOARD_HTML


def test_attention_feed_caps_blocked_job_cards_without_hiding_total():
    assert "summary.blocked_jobs_shown" in DASHBOARD_HTML
    assert "affichés" in DASHBOARD_HTML

def test_attention_project_cards_accept_inline_follow_up_instruction():
    assert "attentionManagedInstruction" in DASHBOARD_HTML
    assert 'id="attention-instruction-' in DASHBOARD_HTML
    assert 'placeholder="Instruction supplémentaire"' in DASHBOARD_HTML
    assert '"/instructions"' in DASHBOARD_HTML
    assert "Saisis une instruction." in DASHBOARD_HTML


def test_completed_attention_items_remain_openable_for_inspection():
    load_start = DASHBOARD_HTML.index("async function loadAttention")
    load_end = DASHBOARD_HTML.index("async function loadManagedProjects", load_start)
    attention_body = DASHBOARD_HTML[load_start:load_end]
    assert "const openButton=item.view" in attention_body

def test_managed_and_attention_cards_render_normalized_production_outcome():
    assert "renderProductionOutcome" in DASHBOARD_HTML
    assert "outcome.validation_status" not in DASHBOARD_HTML
    assert "value.workflow_status" in DASHBOARD_HTML
    assert "value.validation_status" in DASHBOARD_HTML
    assert "value.validation_tests" in DASHBOARD_HTML
    assert "value.commit_shas" in DASHBOARD_HTML
    assert "value.artifact_count" in DASHBOARD_HTML
    assert "value.changed_file_count" in DASHBOARD_HTML
    assert "value.pull_request" in DASHBOARD_HTML
    assert "<strong>Résultat :</strong>" in DASHBOARD_HTML
    assert "<strong>Workflow :</strong>" in DASHBOARD_HTML
    assert "<strong>Validation :</strong>" in DASHBOARD_HTML
    assert "<strong>Tests :</strong>" in DASHBOARD_HTML
    assert "<strong>Commits :</strong>" in DASHBOARD_HTML
    assert "<strong>Artefacts :</strong>" in DASHBOARD_HTML
    assert "<strong>Fichiers modifiés :</strong>" in DASHBOARD_HTML
    assert "<strong>PR :</strong>" in DASHBOARD_HTML
    assert "renderProductionOutcome(item.outcome||{},false)" in DASHBOARD_HTML
    assert "renderProductionOutcome(outcome,true)" in DASHBOARD_HTML

