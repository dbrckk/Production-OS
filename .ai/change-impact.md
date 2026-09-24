# Change impact

Base: be3d4f216f364b515efdfdb7b6dfd5a065b966c2
Head: 5846e966858e6e6b6d8fb18a1c21e6ec7d376de1

## Changed files
- M README.md
- A docs/superpowers/plans/2026-09-22-dashboard-control-center-release-2.md
- A docs/superpowers/plans/2026-09-22-dashboard-observability-release-1.md
- A docs/superpowers/specs/2026-09-22-dashboard-observability-control-center-design.md
- M src/production_os/control_plane.py
- A src/production_os/dashboard_github.py
- A src/production_os/dashboard_security.py
- A src/production_os/dashboard_service.py
- A src/production_os/dashboard_store.py
- A src/production_os/dashboard_ui.py
- A src/production_os/dashboard_usage.py
- M src/production_os/github_client.py
- M src/production_os/postgres_backend.py
- A src/production_os/project_progress.py
- M src/production_os/sqlite_backend.py
- A tests/test_dashboard_api.py
- A tests/test_dashboard_github.py
- A tests/test_dashboard_observability_e2e.py
- A tests/test_dashboard_security.py
- A tests/test_dashboard_store.py
- A tests/test_dashboard_store_postgres.py
- A tests/test_dashboard_ui_v3.py
- A tests/test_dashboard_usage.py
- M tests/test_github_client_pr_files.py
- A tests/test_project_progress.py

## Affected areas
- (root)
- docs
- src
- tests

## Related test candidates
- tests/test_control_plane.py
- tests/test_dashboard_github.py
- tests/test_dashboard_security.py
- tests/test_dashboard_store.py
- tests/test_dashboard_usage.py
- tests/test_postgres_backend.py
- tests/test_project_progress.py
- tests/test_sqlite_backend.py

## Agent guidance
- Read this file before broad repository exploration.
- Inspect only the affected areas first.
- Use .ai/commands.json to choose validation commands.
- Expand scope only if the change crosses module boundaries or tests fail.
