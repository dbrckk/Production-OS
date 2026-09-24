# Repo Brain

- Index mode: incremental
- Files indexed: 230
- Files reparsed this run: 6
- Symbols: 1748
- Internal import edges: 635
- Impacted files: 33
- Selected tests: 26

## Languages
- python: 230 files

## Highest-density symbol files
- src/production_os/cli.py: 80 symbols
- tests/test_asset_forge.py: 56 symbols
- src/production_os/postgres_backend.py: 55 symbols
- src/production_os/sqlite_backend.py: 55 symbols
- src/production_os/dashboard_store.py: 49 symbols
- tests/test_dashboard_ui_v3.py: 43 symbols
- src/production_os/github_client.py: 37 symbols
- src/production_os/dashboard_service.py: 36 symbols
- src/production_os/workflow_engine.py: 35 symbols
- tests/test_transparency_receipts.py: 29 symbols
- src/production_os/control_plane.py: 22 symbols
- src/production_os/rekor_checkpoint_state.py: 22 symbols
- src/production_os/release_ledger.py: 22 symbols
- tests/test_release_ledger.py: 22 symbols
- src/production_os/asset_forge.py: 21 symbols
- src/production_os/transparency_receipts.py: 21 symbols
- tests/test_dashboard_api.py: 19 symbols
- tests/test_dashboard_control_api.py: 19 symbols
- tests/test_workflow_engine.py: 18 symbols
- src/production_os/runtime_state.py: 17 symbols

## Agent routing
- Read impact.json first after project/change context.
- Use selected-tests.json before broad validation.
- Search lookup.json for symbol routing; ast-grep enrichment may provide exact ranges.
- Verify source before editing.

## ast-grep enrichment
- ast-grep outline: available
- AST index mode: incremental
- AST files reparsed this run: 6
- outline files retained: 230
- top-level items retained: 2199
- direct members retained: 824
- symbol shards: 25
- route named symbols via ast-routing.json, then fetch one ast-symbols/<initial>.json shard

