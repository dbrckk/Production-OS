# Free hosting migration: Render -> Northflank (or Koyeb)

**Status: deployment-ready configuration, not a deployed migration.** The Render
workspace was suspended on 2026-10-26 with the provider event
`Free Tier Usage Exceeded`; an old `live` deploy is **not** an accessible API.
Do not claim autonomous worker completion until a genuine remote canary has
completed and its exact-SHA PR/CI are confirmed.

## Architecture and cost boundaries

- **Preferred for testing:** Northflank Developer Sandbox: 2 free services,
  1 free database/addon, always-on (no automatic sleep). **Only one free web
  service is needed: the existing `production-os` Neon database already
  provides persistence.** Requires an account, verified payment method and
  staying inside the Sandbox quota; it is not a production SLA. Check the
  selected resource is explicitly **Free / $0** before creating it.
  Current source: https://northflank.com/pricing
- **Fallback:** Koyeb Free: one web service, 512 MB RAM / 0.1 vCPU,
  sleeps after 1 hour without traffic. Use an independent persistent Postgres,
  such as Neon Free; Koyeb's own free database permits only 5 hours of active
  use per month. Koyeb can require credit card pre-authorization.
  https://www.koyeb.com/docs/reference/instances
- **Do not use** the free container's ephemeral disk for the application DB.
  `DATABASE_URL` **must** point to persistent PostgreSQL. The existing
  `scripts/render-start.py` fails closed if it or either auth token is absent.
- GitHub Actions in `dbrckk/ai-dev-server` remains the **execution** tier.
  The hosted service only runs the Python API/controller and uses PostgreSQL.
  This free deployment does not grant extra Actions minutes or model tokens.
- Onboarding fees, card verification holds and possible usage outside free
  quotas are provider-specific. No paid resource is authorized by this file.

## Deploy on Northflank (Android browser compatible)

1. Create/select a **Developer Sandbox**, **not** Pay-as-you-go.
   Northflank may require a payment method even on the free tier.
2. **Reuse the existing Neon project named `production-os`** (primary branch
   `production`, Frankfurt). It already contains the durable Production-OS
   schema including `jobs`, `workflows`, `workers` and `managed_projects`.
   **Do not create an empty new database or Northflank addon.** Obtain the
   existing connection string securely from the Neon console and configure
   it as `DATABASE_URL` (SSL enabled).
3. Create a **combined** GitHub service from `dbrckk/Production-OS`,
   branch `main`, builder **Dockerfile** and file path
   `Dockerfile.free-hosting`. Choose the explicitly free resource size.
4. Expose **port 8787**, HTTP/public (TLS assigned by the host). Configure
   readiness URL `/readyz`; `/healthz` only checks liveness.
5. Set environment variables and *secret* values below in Northflank, not
   in source control or CI logs. The same operator/worker token values must
   be provisioned in the corresponding GitHub Actions Secrets.
6. Verify a public HTTPS URL is assigned; only then set the GitHub Actions
   variable `PRODUCTION_OS_URL` in **dbrckk/ai-dev-server** to that exact
   base URL. Use GitHub Settings -> Secrets and variables -> Actions ->
   Variables. Do not change it if data migration or readiness is incomplete.

| Variable | Required | Value / role |
|---|---|---|
| `DATABASE_URL` | yes, secret | Existing persistent PostgreSQL URL, or private Northflank addon connection URL. Require TLS for public/external Postgres. |
| `PRODUCTION_OS_WORKER_TOKEN` | yes, secret | Identical to worker Actions secret; 32+ random bytes recommended. |
| `PRODUCTION_OS_OPERATOR_TOKEN` | yes, secret | Identical to canary/operator Actions secret; distinct from worker token. |
| `PRODUCTION_OS_WORKER_ID` | yes | `github-actions-worker` |
| `GITHUB_TOKEN` | yes for automatic dispatch | GitHub token with only the scopes needed to dispatch the worker workflow. |
| `PRODUCTION_OS_ACTIONS_REPOSITORY` | yes for automatic dispatch | `dbrckk/ai-dev-server` |
| `PRODUCTION_OS_ACTIONS_WORKFLOW` | yes for automatic dispatch | `production-os-actions-worker.yml` |
| `PRODUCTION_OS_ACTIONS_REF` | recommended | `main` |
| `PORT` | recommended | `8787` |

GitHub Actions **Variables** in `dbrckk/ai-dev-server`:
`PRODUCTION_OS_URL=https://<real-new-hostname>`. Never paste the real
operator/worker/GitHub tokens into public variables or commits.

## Existing data and cutover

1. Verify the existing `production-os` PostgreSQL project in Neon and
   securely recover its **current primary database** connection string.
   Confirm it matches the old Production-OS instance before cutover: the
   matching schema alone does not prove every Render variable pointed there.
   Never copy a privileged database URL into a PR, log or GitHub variable.
2. **Reuse the same persistent PostgreSQL** when possible: this preserves
   queued jobs, leases, workflow history, idempotency keys and auth-adjacent
   state across deployment. Ensure only one control plane accepts writes
   while switching.
3. If moving PostgreSQL providers, perform a verified **PostgreSQL dump and
   restore** to the new database *before* changing the worker endpoint.
   Validate row counts, schema and workflow IDs. **Never start a fresh blank
   production database and call that a migration.** Keep the source DB intact
   until successful reconciliation. Do not print connection strings.
4. Verify the actual HTTPS `/readyz` returns HTTP 200 with
   `{"status":"ready"}`, and an unauthenticated protected `/v1/` route
   returns 401. A mere `/healthz` 200 is insufficient.
5. Update `PRODUCTION_OS_URL` only after the above checks. Trigger one
   authorized, bounded canary, and collect worker claim/ack/finish, the
   published immutable commit, the **automatically created** draft PR and
   independently passing exact-SHA CI. A manually recovered PR **does not**
   establish autonomy. Do not automatically merge canary branches.
6. If validation fails, restore the previous Actions variable **only if the
   previous server is actually reachable**; otherwise keep dispatch paused
   and do not create duplicate task generations.

## Equivalent Koyeb setup

Choose one Free Web Service in Frankfurt with GitHub + Dockerfile
`Dockerfile.free-hosting`, HTTP port 8787 and the same secrets. Use a durable
**external** PostgreSQL URL; do not use Koyeb Free Database for a durable
24/7 queue. Expect waking after inactivity and make the worker readiness
probe tolerant of a cold start (existing canary preflight uses a bounded
read-only readiness retry). A free Koyeb instance cannot host permanent
volumes. https://www.koyeb.com/docs/faqs/pricing

## Offline CI gate

The canonical GitHub CI builds `Dockerfile.free-hosting`, starts its *actual*
entrypoint with disposable test tokens and the CI PostgreSQL service, checks
`/readyz` and protects API access. This is a deployment **smoke test**, not
proof that Northflank/Koyeb was provisioned nor evidence of a completed
worker production.

## Operational risks

- Northflank Sandbox capacity/quotas may change; neither free hosting nor
  GitHub Actions scheduling is a hard uptime guarantee.
- If `GITHUB_TOKEN` lacks workflow dispatch rights, launches remain queued
  and must be reported as blocked, never as autonomous success.
- Existing limits on external AI model quotas and workflow runtime still apply.
- Avoid duplicate live control planes writing to the same DB during cutover.
- Avoid paid upgrades, unauthorized charges and making public a database or
  authentication token.
