# Repo Brain

- Index mode: incremental
- Files indexed: 222
- Files reparsed this run: 13
- Symbols: 1661
- Internal import edges: 615
- Impacted files: 60
- Selected tests: 49

## Languages
- python: 222 files

## Highest-density symbol files
- src/production_os/cli.py: 80 symbols
- tests/test_asset_forge.py: 56 symbols
- src/production_os/postgres_backend.py: 55 symbols
- src/production_os/sqlite_backend.py: 55 symbols
- src/production_os/dashboard_store.py: 43 symbols
- src/production_os/github_client.py: 36 symbols
- src/production_os/workflow_engine.py: 35 symbols
- src/production_os/dashboard_service.py: 33 symbols
- tests/test_dashboard_ui_v3.py: 31 symbols
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
- AST files reparsed this run: 13
- outline files retained: 222
- top-level items retained: 2095
- direct members retained: 814
- symbol shards: 25
- route named symbols via ast-routing.json, then fetch one ast-symbols/<initial>.json shard

