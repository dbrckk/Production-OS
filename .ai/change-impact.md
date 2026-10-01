# Change impact

Base: b1c3c1f2837d5a3411e7c9f6ede702d0aa9ba5ee
Head: 3d0644a149047817e44404c39bee6f9972663f6a

## Changed files
- M README.md
- M compose.yaml
- A docs/superpowers/plans/2026-09-30-controller-managed-projects.md
- A docs/superpowers/specs/2026-09-30-controller-managed-projects-design.md
- A src/production_os/autonomous_admission.py
- A src/production_os/autonomous_projects.py
- M src/production_os/budgets.py
- M src/production_os/cli.py
- M src/production_os/controller.py
- M src/production_os/dispatch.py
- M src/production_os/rate_limit.py
- M src/production_os/workers.py
- A tests/test_autonomous_admission.py
- A tests/test_autonomous_projects.py
- M tests/test_controller_daemon_deployment.py
- A tests/test_controller_managed_projects.py
- M tests/test_policy_budgets.py
- M tests/test_workers.py

## Affected areas
- (root)
- docs
- src
- tests

## Related test candidates
- tests/test_autonomous_admission.py
- tests/test_autonomous_projects.py
- tests/test_cli.py
- tests/test_workers.py

## Agent guidance
- Read this file before broad repository exploration.
- Inspect only the affected areas first.
- Use .ai/commands.json to choose validation commands.
- Expand scope only if the change crosses module boundaries or tests fail.
