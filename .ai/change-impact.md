# Change impact

Base: bdde2ce158c22355d10d828c8a2eb72e0b0e9b51
Head: 1156579d523f8c9b842a4090105b1b55bee514a8

## Changed files
- M src/production_os/executor_worktree.py
- A src/production_os/filesystem_lock.py
- M src/production_os/repository_cache.py
- A tests/test_filesystem_lock.py
- M tests/test_repository_cache.py

## Affected areas
- src
- tests

## Related test candidates
- tests/test_executor_worktree.py
- tests/test_filesystem_lock.py
- tests/test_repository_cache.py

## Agent guidance
- Read this file before broad repository exploration.
- Inspect only the affected areas first.
- Use .ai/commands.json to choose validation commands.
- Expand scope only if the change crosses module boundaries or tests fail.
