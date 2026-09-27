# Change impact

Base: 14cc218fe566635df76feac70b9224974fe0d462
Head: 3a957cfc21e4ef6f6f365e11000f5f6f69d0f386

## Changed files
- A src/production_os/github_change_review.py
- M src/production_os/github_work_state.py
- A src/production_os/rollback_plan.py
- A tests/test_github_change_review.py
- M tests/test_github_work_state.py
- M tests/test_release51_one_tap_runner_e2e.py
- A tests/test_rollback_plan.py

## Affected areas
- src
- tests

## Related test candidates
- tests/test_github_change_review.py
- tests/test_github_work_state.py
- tests/test_rollback_plan.py

## Agent guidance
- Read this file before broad repository exploration.
- Inspect only the affected areas first.
- Use .ai/commands.json to choose validation commands.
- Expand scope only if the change crosses module boundaries or tests fail.
