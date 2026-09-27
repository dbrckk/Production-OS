# Change impact

Base: adac8a3dc5d29890a1730242ea7094d344e89bb4
Head: 1e8b5d3d06af5e7afc4094f66b7438331e30523c

## Changed files
- M Dockerfile
- M Dockerfile.browser-worker
- M Dockerfile.mobile-worker
- M compose.worker.yaml
- M docs/remote-worker-executor-protocol.md
- M src/production_os/cli.py
- M src/production_os/remote_worker_runner.py
- A src/production_os/repository_cache.py
- M tests/test_browser_worker_image.py
- M tests/test_executor_worktree.py
- M tests/test_mobile_worker_image.py
- A tests/test_repository_cache.py
- M tests/test_worker_compose_deployment.py

## Affected areas
- (root)
- docs
- src
- tests

## Related test candidates
- tests/test_cli.py
- tests/test_remote_worker_runner.py
- tests/test_repository_cache.py

## Agent guidance
- Read this file before broad repository exploration.
- Inspect only the affected areas first.
- Use .ai/commands.json to choose validation commands.
- Expand scope only if the change crosses module boundaries or tests fail.
