# Change impact

Base: 9ba773d07fc2dbc95d0d4edd1ac8305504b81114
Head: d1508f61c5d56f1b1a6fcde896b5b043587fc944

## Changed files
- M src/production_os/control_plane.py
- M src/production_os/dashboard_ui.py
- A src/production_os/managed_projects.py
- M src/production_os/workflow_engine.py
- M tests/test_dashboard_ui_v3.py
- A tests/test_managed_projects_http_v4.py
- A tests/test_managed_projects_v4.py
- M tests/test_workflow_engine.py
- M tests/test_workflow_postgres.py

## Affected areas
- src
- tests

## Related test candidates
- tests/test_control_plane.py
- tests/test_workflow_engine.py

## Agent guidance
- Read this file before broad repository exploration.
- Inspect only the affected areas first.
- Use .ai/commands.json to choose validation commands.
- Expand scope only if the change crosses module boundaries or tests fail.
