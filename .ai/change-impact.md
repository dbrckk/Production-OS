# Change impact

Base: 7f369084c7c1296b17deb6ed94bcc0439e808ef2
Head: 0cdef847d44da2029bf208ee51c317a655ef43d7

## Changed files
- M README.md
- A docs/superpowers/plans/2026-09-25-release-19-restore-staging.md
- M src/production_os/control_plane.py
- M src/production_os/dashboard_backups.py
- M src/production_os/dashboard_service.py
- M src/production_os/dashboard_ui.py
- M tests/test_dashboard_backup_api.py
- M tests/test_dashboard_backups.py
- M tests/test_dashboard_ui_v3.py
- A tests/test_release19_restore_staging_e2e.py

## Affected areas
- (root)
- docs
- src
- tests

## Related test candidates
- tests/test_control_plane.py
- tests/test_dashboard_backups.py

## Agent guidance
- Read this file before broad repository exploration.
- Inspect only the affected areas first.
- Use .ai/commands.json to choose validation commands.
- Expand scope only if the change crosses module boundaries or tests fail.
