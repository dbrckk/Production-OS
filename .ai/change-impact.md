# Change impact

Base: 3ba41030169f1ca1849983eace9c6e456e8bef24
Head: 760c4867abda7d201d81b8aad6a15d91986b58cc

## Changed files
- M compose.worker.yaml
- M src/production_os/remote_worker_runner.py
- M src/production_os/sqlite_backend.py
- M src/production_os/task_capabilities.py
- M src/production_os/workflow_engine.py
- M tests/test_remote_worker_runner.py
- A tests/test_specialist_job_preferences.py
- M tests/test_worker_compose_deployment.py

## Affected areas
- (root)
- src
- tests

## Related test candidates
- tests/test_remote_worker_runner.py
- tests/test_sqlite_backend.py
- tests/test_task_capabilities.py
- tests/test_workflow_engine.py

## Agent guidance
- Read this file before broad repository exploration.
- Inspect only the affected areas first.
- Use .ai/commands.json to choose validation commands.
- Expand scope only if the change crosses module boundaries or tests fail.
