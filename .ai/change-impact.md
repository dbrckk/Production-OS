# Change impact

Base: 6b9e6a32da720c2de8d506e93000682f65670fe4
Head: 1296a4950bc656af89fdfcb11c7c7ecbff88f4d7

## Changed files
- M src/production_os/github_change_review.py
- M src/production_os/github_client.py
- M src/production_os/github_work_state.py
- M src/production_os/managed_projects.py
- A tests/test_github_automerge.py
- M tests/test_github_change_review.py
- M tests/test_github_work_state.py
- M tests/test_managed_github_reconciliation.py

## Affected areas
- src
- tests

## Related test candidates
- tests/test_github_change_review.py
- tests/test_github_work_state.py

## Agent guidance
- Read this file before broad repository exploration.
- Inspect only the affected areas first.
- Use .ai/commands.json to choose validation commands.
- Expand scope only if the change crosses module boundaries or tests fail.
