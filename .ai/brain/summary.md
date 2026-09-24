# Repo Brain

- Index mode: incremental
- Files indexed: 210
- Files reparsed this run: 21
- Symbols: 1521
- Internal import edges: 581
- Impacted files: 64
- Selected tests: 49

## Languages
- python: 210 files

## Highest-density symbol files
- src/production_os/cli.py: 80 symbols
- tests/test_asset_forge.py: 56 symbols
- src/production_os/postgres_backend.py: 53 symbols
- src/production_os/sqlite_backend.py: 53 symbols
- src/production_os/github_client.py: 36 symbols
- src/production_os/workflow_engine.py: 33 symbols
- src/production_os/dashboard_store.py: 30 symbols
- tests/test_transparency_receipts.py: 29 symbols
- src/production_os/dashboard_service.py: 27 symbols
- src/production_os/rekor_checkpoint_state.py: 22 symbols
- src/production_os/release_ledger.py: 22 symbols
- tests/test_release_ledger.py: 22 symbols
- src/production_os/asset_forge.py: 21 symbols
- src/production_os/control_plane.py: 21 symbols
- src/production_os/transparency_receipts.py: 21 symbols
- tests/test_dashboard_ui_v3.py: 18 symbols
- tests/test_workflow_engine.py: 18 symbols
- src/production_os/runtime_state.py: 17 symbols
- src/production_os/rekor_witness_quorum.py: 16 symbols
- tests/test_dashboard_launch.py: 16 symbols

## Agent routing
- Read impact.json first after project/change context.
- Use selected-tests.json before broad validation.
- Search lookup.json for symbol routing; ast-grep enrichment may provide exact ranges.
- Verify source before editing.

## ast-grep enrichment
- ast-grep outline: available
- AST index mode: incremental
- AST files reparsed this run: 21
- outline files retained: 210
- top-level items retained: 1939
- direct members retained: 774
- symbol shards: 25
- route named symbols via ast-routing.json, then fetch one ast-symbols/<initial>.json shard

