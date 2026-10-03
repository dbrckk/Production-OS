# Repo Brain

- Index mode: incremental
- Files indexed: 339
- Files reparsed this run: 3
- Symbols: 3083
- Internal import edges: 977
- Impacted files: 14
- Selected tests: 12

## Languages
- python: 339 files

## Highest-density symbol files
- tests/test_dashboard_ui_v3.py: 112 symbols
- src/production_os/cli.py: 92 symbols
- src/production_os/dashboard_store.py: 61 symbols
- src/production_os/postgres_backend.py: 56 symbols
- src/production_os/sqlite_backend.py: 56 symbols
- tests/test_asset_forge.py: 56 symbols
- tests/test_browser_computer.py: 55 symbols
- src/production_os/dashboard_service.py: 54 symbols
- tests/test_remote_worker_runner.py: 52 symbols
- tests/test_dashboard_backups.py: 49 symbols
- src/production_os/github_client.py: 42 symbols
- src/production_os/workflow_engine.py: 42 symbols
- tests/test_controller_managed_projects.py: 38 symbols
- src/production_os/managed_projects.py: 35 symbols
- src/production_os/control_plane.py: 31 symbols
- tests/test_browser_loop.py: 31 symbols
- tests/test_dashboard_api.py: 30 symbols
- tests/test_transparency_receipts.py: 29 symbols
- src/production_os/dashboard_backups.py: 25 symbols
- tests/test_controller_leader.py: 24 symbols

## Agent routing
- Read impact.json first after project/change context.
- Use selected-tests.json before broad validation.
- Search lookup.json for symbol routing; ast-grep enrichment may provide exact ranges.
- Verify source before editing.

## ast-grep enrichment
- ast-grep outline: available
- AST index mode: incremental
- AST files reparsed this run: 3
- outline files retained: 339
- top-level items retained: 3870
- direct members retained: 1238
- symbol shards: 25
- route named symbols via ast-routing.json, then fetch one ast-symbols/<initial>.json shard

