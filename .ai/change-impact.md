# Change impact

Base: baadb2270d85f06dc0644837d69228790e31e442
Head: 8f64c4cfcea68c5fe3adc41d7da81fbee2f66c82

## Changed files
- M README.md
- A docs/superpowers/plans/2026-09-24-dashboard-control-center-release-4.md
- M src/production_os/control_plane.py
- A src/production_os/dashboard_incidents.py
- M src/production_os/dashboard_service.py
- M src/production_os/dashboard_store.py
- M src/production_os/dashboard_ui.py
- M src/production_os/postgres_backend.py
- M src/production_os/sqlite_backend.py
- M tests/test_dashboard_control_audit.py
- M tests/test_dashboard_control_e2e.py
- A tests/test_dashboard_incident_signals.py
- A tests/test_dashboard_incidents.py
- M tests/test_dashboard_store_postgres.py
- M tests/test_dashboard_ui_v3.py

## Affected areas
- (root)
- docs
- src
- tests

## Related test candidates
- tests/test_control_plane.py
- tests/test_dashboard_incidents.py
- tests/test_dashboard_store.py
- tests/test_postgres_backend.py
- tests/test_sqlite_backend.py

## Agent guidance
- Read this file before broad repository exploration.
- Inspect only the affected areas first.
- Use .ai/commands.json to choose validation commands.
- Expand scope only if the change crosses module boundaries or tests fail.
