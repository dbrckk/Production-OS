# Repo Brain

- Files indexed: 185
- Symbols: 1208
- Internal import edges: 313

## Languages
- python: 185 files

## Highest-density symbol files
- src/production_os/cli.py: 76 symbols
- src/production_os/postgres_backend.py: 53 symbols
- src/production_os/sqlite_backend.py: 53 symbols
- src/production_os/workflow_engine.py: 33 symbols
- tests/test_transparency_receipts.py: 29 symbols
- src/production_os/rekor_checkpoint_state.py: 22 symbols
- src/production_os/release_ledger.py: 22 symbols
- tests/test_release_ledger.py: 22 symbols
- src/production_os/control_plane.py: 21 symbols
- src/production_os/transparency_receipts.py: 21 symbols
- src/production_os/github_client.py: 18 symbols
- src/production_os/runtime_state.py: 17 symbols
- tests/test_workflow_engine.py: 17 symbols
- src/production_os/rekor_witness_quorum.py: 16 symbols
- tests/test_trust_status_summary.py: 16 symbols
- src/production_os/execution_optimizer.py: 15 symbols
- src/production_os/workers.py: 14 symbols
- tests/test_incident_history.py: 14 symbols
- tests/test_rekor_witness_quorum.py: 14 symbols
- src/production_os/speculation.py: 13 symbols

## Agent routing
- Search lookup.json first for direct symbol-to-file routing.
- Use symbols.json only when broader symbol metadata is needed.
- Use code-graph.json to inspect likely internal import relationships.
- Use imports.json when a changed file crosses module boundaries.
- Treat graph edges as static hints; verify source before editing.

## ast-grep enrichment
- ast-grep outline: available
- outline files: 185
- top-level items: 1626
- direct members: 676
- symbol shards: 25
- route named symbols via ast-routing.json, then fetch one ast-symbols/<initial>.json shard

