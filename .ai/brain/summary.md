# Repo Brain

- Index mode: incremental
- Files indexed: 255
- Files reparsed this run: 7
- Symbols: 2053
- Internal import edges: 726
- Impacted files: 45
- Selected tests: 41

## Languages
- python: 255 files

## Highest-density symbol files
- tests/test_dashboard_ui_v3.py: 83 symbols
- src/production_os/cli.py: 81 symbols
- tests/test_asset_forge.py: 56 symbols
- src/production_os/postgres_backend.py: 55 symbols
- src/production_os/sqlite_backend.py: 55 symbols
- src/production_os/dashboard_store.py: 49 symbols
- tests/test_dashboard_backups.py: 49 symbols
- src/production_os/dashboard_service.py: 47 symbols
- src/production_os/github_client.py: 37 symbols
- src/production_os/workflow_engine.py: 37 symbols
- tests/test_transparency_receipts.py: 29 symbols
- src/production_os/control_plane.py: 25 symbols
- src/production_os/dashboard_backups.py: 25 symbols
- tests/test_dashboard_api.py: 24 symbols
- src/production_os/managed_projects.py: 22 symbols
- src/production_os/rekor_checkpoint_state.py: 22 symbols
- src/production_os/release_ledger.py: 22 symbols
- tests/test_release_ledger.py: 22 symbols
- src/production_os/asset_forge.py: 21 symbols
- src/production_os/transparency_receipts.py: 21 symbols

## Agent routing
- Read impact.json first after project/change context.
- Use selected-tests.json before broad validation.
- Search lookup.json for symbol routing; ast-grep enrichment may provide exact ranges.
- Verify source before editing.

## ast-grep enrichment
- ast-grep outline: available
- AST index mode: incremental
- AST files reparsed this run: 7
- outline files retained: 255
- top-level items retained: 2648
- direct members retained: 874
- symbol shards: 25
- route named symbols via ast-routing.json, then fetch one ast-symbols/<initial>.json shard

