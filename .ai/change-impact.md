# Change impact

Base: 8a3be70735d71bcda65e83d02ac1e5a133eec5db
Head: 10c8ee417f6c863a94141fbac259a12fd09dce6d

## Changed files
- M .github/workflows/ci.yml
- M src/production_os/control_plane.py
- M src/production_os/dashboard_store.py
- M src/production_os/dashboard_ui.py
- M tests/test_dashboard_api.py
- M tests/test_dashboard_launch.py
- M tests/test_dashboard_launch_ux.py
- M tests/test_release32_one_tap_e2e.py

## Affected areas
- .github
- src
- tests

## Related test candidates
- tests/test_control_plane.py
- tests/test_dashboard_store.py

## Agent guidance
- Read this file before broad repository exploration.
- Inspect only the affected areas first.
- Use .ai/commands.json to choose validation commands.
- Expand scope only if the change crosses module boundaries or tests fail.
