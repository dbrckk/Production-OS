# Change impact

Base: f79359a1e82cafcf7abb0f4f58be05e34a1f6907
Head: e3c61df28b5ca888c9d3f169f127627adaf72370

## Changed files
- M README.md
- M src/production_os/control_plane.py
- A src/production_os/dashboard_alerts.py
- A src/production_os/dashboard_control.py
- M src/production_os/dashboard_service.py
- M src/production_os/dashboard_store.py
- M src/production_os/dashboard_ui.py
- M src/production_os/postgres_backend.py
- M src/production_os/sqlite_backend.py
- M src/production_os/workflow_engine.py
- A tests/test_dashboard_alerts.py
- A tests/test_dashboard_control.py
- A tests/test_dashboard_control_api.py
- A tests/test_dashboard_control_e2e.py
- M tests/test_dashboard_ui_v3.py
- M tests/test_portfolio_claim_api.py

## Affected areas
- (root)
- src
- tests

## Related test candidates
- tests/test_control_plane.py
- tests/test_dashboard_alerts.py
- tests/test_dashboard_control.py
- tests/test_dashboard_store.py
- tests/test_postgres_backend.py
- tests/test_sqlite_backend.py
- tests/test_workflow_engine.py

## Agent guidance
- Read this file before broad repository exploration.
- Inspect only the affected areas first.
- Use .ai/commands.json to choose validation commands.
- Expand scope only if the change crosses module boundaries or tests fail.
