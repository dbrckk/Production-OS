# Change impact

Base: 7b9efe1616825e6e78be563f65696c865a70ca72
Head: 935ac148e2d5d408ad0e27d89cb2983ec5210d9a

## Changed files
- M src/production_os/control_plane.py
- M src/production_os/postgres_backend.py
- M src/production_os/sqlite_backend.py
- M tests/test_postgres_backend.py
- M tests/test_sqlite_backend.py
- M tests/test_worker_availability_api.py

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
