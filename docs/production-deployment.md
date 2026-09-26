# Production deployment

This guide covers the Production-OS control plane. Execution is performed by the external `dbrckk/ai-dev-server` GitHub Actions worker; do **not** run `remote-worker-poll` as an execution worker because that command only polls/claims jobs.

## 1. Create operator and worker tokens

Generate two random bearer tokens and keep the raw values out of the repository.

Create `artifacts/auth.json` with SHA-256 digests:

```json
{
  "tokens": [
    {
      "name": "operator",
      "role": "operator",
      "sha256": "<sha256-of-operator-token>"
    },
    {
      "name": "github-actions-worker",
      "role": "worker",
      "sha256": "<sha256-of-worker-token>"
    }
  ]
}
```

The operator raw token is paired once in the mobile dashboard. The worker raw token is configured only as the `PRODUCTION_OS_WORKER_TOKEN` secret in `dbrckk/ai-dev-server`.

## 2. Configure GitHub Actions execution

In `dbrckk/ai-dev-server`, configure:

- variable `PRODUCTION_OS_URL`: public HTTPS Production-OS URL;
- secret `PRODUCTION_OS_WORKER_TOKEN`: raw worker token matching `auth.json`;
- secret `PRODUCTION_OS_OPERATOR_TOKEN`: raw operator token used for worker registration;
- secret `STUDIO_GITHUB_TOKEN`: repository-capable GitHub token;
- secret `STUDIO_API_KEY`: coding-model provider key.

The existing `production-os-actions-worker.yml` runs on a five-minute schedule and supports explicit workflow dispatch.

On the Production-OS service, set `GITHUB_TOKEN` to a server-side GitHub token allowed to dispatch that workflow. The token is never returned to dashboard JavaScript.

## 3. Docker Compose

Copy the environment template:

```bash
cp .env.example .env
```

Fill secrets locally, then create persistent state:

```bash
mkdir -p artifacts/backups
```

On Linux bind mounts, ensure container uid `10001` can write the state directory:

```bash
sudo chown -R 10001:10001 artifacts
```

Start:

```bash
docker compose up -d --build
docker compose ps
```

The service has a container healthcheck against `/health`, restarts unless explicitly stopped, receives a 30-second graceful shutdown window, stores SQLite and backups under `/data`, and wires the GitHub Actions dispatch configuration.

## 4. Verify from the mobile dashboard

Open `/dashboard`, pair the operator token once, then check the **Déploiement** status card.

Expected healthy states:

- `worker disponible`: a worker is online and has capacity; or
- `GitHub Actions déclenchable`: no worker is currently online, but the Control Plane can dispatch the external worker;
- `backups prêts` for SQLite.

If the card reports `chemin d’exécution non vérifié`, a launch remains durable and queued, but Production-OS cannot currently prove that a worker can be started.

## 5. Render

For Render, configure the equivalent environment variables and a persistent disk mounted at `/data`. Set the service health check path to:

```text
/health
```

Do not create a Render background worker from `remote-worker-poll`; the real execution worker is the ai-dev-server GitHub Actions workflow.

Because Render workspaces are account-specific, live service changes should be made only after explicitly selecting the intended Render workspace.
