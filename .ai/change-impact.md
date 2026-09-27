# Change impact

Base: 153e7b7c43de173c617f03a4bee6b837c9c4fed4
Head: 7df2e9b0491090564cc0aecf82014aebec0f56fc

## Changed files
- M docs/remote-worker-executor-protocol.md
- M src/production_os/managed_projects.py
- M src/production_os/workflow_engine.py
- A src/production_os/worktree_contract.py
- M tests/test_cooperative_managed_projects.py
- M tests/test_cooperative_specialist_e2e.py
- M tests/test_managed_github_reconciliation.py
- M tests/test_release32_one_tap_e2e.py
- A tests/test_worktree_contract.py

## Affected areas
- docs
- src
- tests

## Related test candidates
- tests/test_workflow_engine.py
- tests/test_worktree_contract.py

## Agent guidance
- Read this file before broad repository exploration.
- Inspect only the affected areas first.
- Use .ai/commands.json to choose validation commands.
- Expand scope only if the change crosses module boundaries or tests fail.
