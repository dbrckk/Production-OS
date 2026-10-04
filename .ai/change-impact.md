# Change impact

Base: 7e0d47a8fd54e7faa3b3947b07259a5e065c3bdb
Head: 4f547bed6c97c7c2a024400af0c604ae854da75d

## Changed files
- M README.md
- M src/production_os/cli.py
- M src/production_os/controller.py
- M src/production_os/postgres_backend.py
- M src/production_os/release_ledger.py
- M src/production_os/storage.py
- A tests/test_controller_error_recovery.py
- M tests/test_controller_leader.py
- M tests/test_dashboard_store_postgres.py
- M tests/test_database_maintenance_lock.py
- M tests/test_production_stack_e2e.py
- A tests/test_release_postgres.py
- A tests/test_storage_routing.py
- M tests/test_trust_status_summary.py

## Affected areas
- (root)
- src
- tests

## Related test candidates
- tests/test_cli.py
- tests/test_postgres_backend.py
- tests/test_release_ledger.py

## Agent guidance
- Read this file before broad repository exploration.
- Inspect only the affected areas first.
- Use .ai/commands.json to choose validation commands.
- Expand scope only if the change crosses module boundaries or tests fail.
