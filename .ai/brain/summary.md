# Repo Brain

- Index mode: incremental
- Files indexed: 277
- Files reparsed this run: 8
- Symbols: 2287
- Internal import edges: 787
- Impacted files: 21
- Selected tests: 15

## Languages
- python: 277 files

## Highest-density symbol files
- tests/test_dashboard_ui_v3.py: 94 symbols
- src/production_os/cli.py: 83 symbols
- src/production_os/postgres_backend.py: 56 symbols
- src/production_os/sqlite_backend.py: 56 symbols
- tests/test_asset_forge.py: 56 symbols
- src/production_os/dashboard_service.py: 52 symbols
- src/production_os/dashboard_store.py: 49 symbols
- tests/test_dashboard_backups.py: 49 symbols
- src/production_os/github_client.py: 42 symbols
- src/production_os/workflow_engine.py: 39 symbols
- src/production_os/managed_projects.py: 33 symbols
- tests/test_dashboard_api.py: 30 symbols
- tests/test_transparency_receipts.py: 29 symbols
- src/production_os/control_plane.py: 26 symbols
- src/production_os/dashboard_backups.py: 25 symbols
- src/production_os/rekor_checkpoint_state.py: 22 symbols
- src/production_os/release_ledger.py: 22 symbols
- tests/test_release_ledger.py: 22 symbols
- tests/test_workflow_engine.py: 22 symbols
- src/production_os/asset_forge.py: 21 symbols

## Agent routing
- Read impact.json first after project/change context.
- Use selected-tests.json before broad validation.
- Search lookup.json for symbol routing; ast-grep enrichment may provide exact ranges.
- Verify source before editing.

## ast-grep enrichment
- ast-grep outline: available
- AST index mode: incremental
- AST files reparsed this run: 8
- outline files retained: 277
- top-level items retained: 2951
- direct members retained: 924
- symbol shards: 25
- route named symbols via ast-routing.json, then fetch one ast-symbols/<initial>.json shard

