# Change impact

Base: 4df69b8ad09c1385c779589f594af22dedeecebd
Head: 739cd5bb0a47d484fe1afb9ffb045ebf05ac1328

## Changed files
- M .github/workflows/ci.yml
- M docs/render-free-deployment.md
- M render.yaml
- M scripts/render-start.py
- A scripts/verify-render-cutover.py
- M src/production_os/control_plane.py
- M src/production_os/dashboard_health.py
- M src/production_os/dashboard_service.py
- M src/production_os/dashboard_ui.py
- M tests/test_control_plane.py
- M tests/test_dashboard_api.py
- M tests/test_dashboard_health.py
- M tests/test_dashboard_launch_readiness.py
- M tests/test_dashboard_worker_detail_freshness.py
- M tests/test_render_start.py
- A tests/test_verify_render_cutover.py

## Affected areas
- .github
- docs
- (root)
- scripts
- src
- tests

## Related test candidates
- tests/test_control_plane.py
- tests/test_dashboard_health.py

## Agent guidance
- Read this file before broad repository exploration.
- Inspect only the affected areas first.
- Use .ai/commands.json to choose validation commands.
- Expand scope only if the change crosses module boundaries or tests fail.
