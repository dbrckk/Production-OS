# Repo Brain

- Index mode: incremental
- Files indexed: 245
- Files reparsed this run: 5
- Symbols: 1985
- Internal import edges: 692
- Impacted files: 34
- Selected tests: 31

## Languages
- python: 245 files

## Highest-density symbol files
- src/production_os/cli.py: 81 symbols
- tests/test_dashboard_ui_v3.py: 69 symbols
- tests/test_asset_forge.py: 56 symbols
- src/production_os/postgres_backend.py: 55 symbols
- src/production_os/sqlite_backend.py: 55 symbols
- src/production_os/dashboard_store.py: 49 symbols
- tests/test_dashboard_backups.py: 49 symbols
- src/production_os/dashboard_service.py: 44 symbols
- src/production_os/github_client.py: 37 symbols
- src/production_os/workflow_engine.py: 37 symbols
- tests/test_transparency_receipts.py: 29 symbols
- src/production_os/dashboard_backups.py: 25 symbols
- src/production_os/control_plane.py: 22 symbols
- src/production_os/rekor_checkpoint_state.py: 22 symbols
- src/production_os/release_ledger.py: 22 symbols
- tests/test_release_ledger.py: 22 symbols
- src/production_os/asset_forge.py: 21 symbols
- src/production_os/transparency_receipts.py: 21 symbols
- src/production_os/managed_projects.py: 20 symbols
- tests/test_dashboard_api.py: 20 symbols

## Agent routing
- Read impact.json first after project/change context.
- Use selected-tests.json before broad validation.
- Search lookup.json for symbol routing; ast-grep enrichment may provide exact ranges.
- Verify source before editing.

## ast-grep enrichment
- ast-grep outline: available
- AST index mode: incremental
- AST files reparsed this run: 5
- outline files retained: 245
- top-level items retained: 2526
- direct members retained: 866
- symbol shards: 25
- route named symbols via ast-routing.json, then fetch one ast-symbols/<initial>.json shard

