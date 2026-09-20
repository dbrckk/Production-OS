# Repo Brain

- Index mode: incremental
- Files indexed: 194
- Files reparsed this run: 2
- Symbols: 1345
- Internal import edges: 549
- Impacted files: 14
- Selected tests: 12

## Languages
- python: 194 files

## Highest-density symbol files
- src/production_os/cli.py: 80 symbols
- tests/test_asset_forge.py: 56 symbols
- src/production_os/postgres_backend.py: 53 symbols
- src/production_os/sqlite_backend.py: 53 symbols
- src/production_os/workflow_engine.py: 33 symbols
- tests/test_transparency_receipts.py: 29 symbols
- src/production_os/github_client.py: 28 symbols
- src/production_os/rekor_checkpoint_state.py: 22 symbols
- src/production_os/release_ledger.py: 22 symbols
- tests/test_release_ledger.py: 22 symbols
- src/production_os/asset_forge.py: 21 symbols
- src/production_os/control_plane.py: 21 symbols
- src/production_os/transparency_receipts.py: 21 symbols
- tests/test_workflow_engine.py: 18 symbols
- src/production_os/runtime_state.py: 17 symbols
- src/production_os/rekor_witness_quorum.py: 16 symbols
- tests/test_trust_status_summary.py: 16 symbols
- src/production_os/execution_optimizer.py: 15 symbols
- src/production_os/workers.py: 14 symbols
- tests/test_incident_history.py: 14 symbols

## Agent routing
- Read impact.json first after project/change context.
- Use selected-tests.json before broad validation.
- Search lookup.json for symbol routing; ast-grep enrichment may provide exact ranges.
- Verify source before editing.

## ast-grep enrichment
- ast-grep outline: available
- AST index mode: incremental
- AST files reparsed this run: 2
- outline files retained: 194
- top-level items retained: 1770
- direct members retained: 708
- symbol shards: 25
- route named symbols via ast-routing.json, then fetch one ast-symbols/<initial>.json shard

