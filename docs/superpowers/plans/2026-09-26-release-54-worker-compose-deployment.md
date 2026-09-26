# Release 54 — Compose remote worker deployment

## Goal

Make the persistent remote worker deployable next to the Production-OS control plane without embedding worker credentials or executor implementation details in the repository.

## Deployment contract

- keep the existing control-plane service in `compose.yaml`
- add `compose.worker.yaml` as an explicit overlay
- gate the worker behind the `worker` Compose profile
- wait for `/healthz` before starting the worker
- source the worker bearer token only from `PRODUCTION_OS_WORKER_TOKEN`
- pass the external executor through `PRODUCTION_OS_WORKER_EXECUTOR_COMMAND`
- mount the executor directory read-only
- preserve configurable concurrency, heartbeat, executor timeout and ACK timeout
- enable Docker init/reaping
- give SIGTERM enough grace for Release 53 cooperative child termination and active-job cleanup

## Operator command

```bash
PRODUCTION_OS_WORKER_TOKEN=... \
PRODUCTION_OS_WORKER_EXECUTOR_COMMAND="python /worker/executor.py" \
docker compose -f compose.yaml -f compose.worker.yaml --profile worker up --build
```

The executor remains an external trust boundary by design. Production-OS does not ship a fake executor or inject the worker bearer token into it.

## Validation

- static deployment contract test
- full Python suite
- existing Docker smoke
- existing CLI smoke
- Compose config validation when Docker Compose is available
