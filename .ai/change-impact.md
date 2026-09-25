# Change impact

Base: 9095554afe3d736d9553dd771f6bd87383db06ee
Head: 15ba18d589653f020e296e3a508b39d2348377c1

## Changed files
- M README.md
- A docs/superpowers/plans/2026-09-25-release-20-maintenance-lock.md
- M src/production_os/control_plane.py
- A src/production_os/database_maintenance_lock.py
- A tests/test_database_maintenance_lock.py

## Affected areas
- (root)
- docs
- src
- tests

## Related test candidates
- tests/test_control_plane.py
- tests/test_database_maintenance_lock.py

## Agent guidance
- Read this file before broad repository exploration.
- Inspect only the affected areas first.
- Use .ai/commands.json to choose validation commands.
- Expand scope only if the change crosses module boundaries or tests fail.
