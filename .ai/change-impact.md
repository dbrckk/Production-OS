# Change impact

Base: 699fe30b9e28fa8354e2b5138cc3c5a70feeee58
Head: e57c478e9fecba10ba5ee44d3d00fb9105dc35ed

## Changed files
- M src/production_os/control_plane.py
- M src/production_os/dashboard_ui.py
- M src/production_os/managed_projects.py
- M src/production_os/postgres_backend.py
- M src/production_os/sqlite_backend.py
- M tests/test_dashboard_control_audit.py
- M tests/test_dashboard_remediation_history.py
- M tests/test_dashboard_store_postgres.py
- M tests/test_dashboard_ui_v3.py
- M tests/test_managed_projects_http_v4.py
- M tests/test_managed_projects_v4.py
- M tests/test_workflow_postgres.py

## Affected areas
- src
- tests

## Related test candidates
- tests/test_control_plane.py
- tests/test_postgres_backend.py
- tests/test_sqlite_backend.py

## Agent guidance
- Read this file before broad repository exploration.
- Inspect only the affected areas first.
- Use .ai/commands.json to choose validation commands.
- Expand scope only if the change crosses module boundaries or tests fail.
