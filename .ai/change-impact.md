# Change impact

Base: da6a8019c3f5d31a4fa53f2a7165079f4c64c20a
Head: cd15f24c1b2a590a1ba1febfe7d4ce7792dc8a8f

## Changed files
- M README.md
- A docs/superpowers/plans/2026-09-24-dashboard-control-center-release-6.md
- M src/production_os/control_plane.py
- M src/production_os/dashboard_service.py
- M src/production_os/dashboard_store.py
- M src/production_os/dashboard_ui.py
- M src/production_os/postgres_backend.py
- M src/production_os/sqlite_backend.py
- M tests/test_dashboard_control_audit.py
- A tests/test_dashboard_remediation_api.py
- A tests/test_dashboard_remediation_history.py
- M tests/test_dashboard_store_postgres.py
- M tests/test_dashboard_ui_v3.py

## Affected areas
- (root)
- docs
- src
- tests

## Related test candidates
- tests/test_control_plane.py
- tests/test_dashboard_store.py
- tests/test_postgres_backend.py
- tests/test_sqlite_backend.py

## Agent guidance
- Read this file before broad repository exploration.
- Inspect only the affected areas first.
- Use .ai/commands.json to choose validation commands.
- Expand scope only if the change crosses module boundaries or tests fail.
