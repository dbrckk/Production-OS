# Render Free deployment for Production-OS (existing Neon database)

This is the **active** hosting configuration. `render.yaml` creates exactly
**one Render Free web service**. It does not create a database, a paid service,
a persistent disk, a cron job or an extra worker. GitHub Actions remains the
execution tier. Prior free-host alternatives are archived as a fallback in
`docs/free-hosting-migration.md`; **do not deploy them**.

## Verified existing architecture

- Source: `dbrckk/Production-OS`, `main` (Render builds
  `Dockerfile.free-hosting`, running `scripts/render-start.py`).
- Worker: `dbrckk/ai-dev-server`, GitHub Actions
  `production-os-actions-worker.yml` (schedule every 5 minutes).
- Persistent database: existing Neon project **production-os**, database
  **production_os**, branch **production**, region **Frankfurt**.
  Preserve the original database; it has application tables and historical
  workflows/jobs. A fresh empty PostgreSQL database **is not a migration**.
- API: port **8787**, database-aware readiness **GET /readyz**, protected
  routes including **GET /v1/workflows**.
- Old Render account: its free-tier service was suspended after
  `Free Tier Usage Exceeded`. A prior "live deploy" is not proof the service
  is reachable. Do not enable two live controllers against the same DB.

## Setup from the new Render account

1. Open https://dashboard.render.com/blueprints in the intended Render
   account, choose **New Blueprint** and connect the existing GitHub repo
   `dbrckk/Production-OS` on branch **main**.
2. Keep the default Blueprint path **render.yaml**. Inspect the planned
   resources before approval: **one web service, plan Free, Frankfurt**,
   with the name `production-os-control-plane`; **no Render database**.
   Never approve an automatically selected paid tier.
3. In the Blueprint's **secret environment variable** prompts, supply the
   four mandatory values. Render's `sync: false` keeps values out of Git:
   - `DATABASE_URL`: the **existing** Neon PostgreSQL connection string
     for `production_os`, SSL enabled. Obtain via Neon Console, or safely
     from an authorized secret manager. **Never copy into Git or chat.**
   - `PRODUCTION_OS_WORKER_TOKEN`: must equal the worker secret currently
     configured in **ai-dev-server -> Settings -> Secrets and variables ->
     Actions -> Secrets**.
   - `PRODUCTION_OS_OPERATOR_TOKEN`: must equal the operator/canary
     Actions secret in **ai-dev-server**. Must be distinct from the worker
     token.
   - `GITHUB_TOKEN`: a separate, least-privilege GitHub token permitted to
     dispatch the `production-os-actions-worker.yml` workflow in
     `dbrckk/ai-dev-server`. Do not use the Neon password as a token.
4. The Blueprint sets the worker ID, repository, workflow, branch and port
   to existing audited defaults. Allow the first deployment to finish.
   Retrieve its **actual Render-assigned HTTPS URL**; do not assume a
   particular service hostname.
5. Verify **GET /readyz** returns HTTP 200 with `status: ready` and
   `database: reachable`, and **GET /v1/workflows** without Authorization
   returns HTTP 401. Health-only 200 on `/healthz` is not enough.
6. Only after those checks, change **ai-dev-server -> Settings -> Secrets
   and variables -> Actions -> Variables -> PRODUCTION_OS_URL** to the
   actual, reachable new HTTPS base URL. The worker and canary workflows
   otherwise **fall back to the old suspended Render hostname**, so this
   variable is essential to the cutover.
7. Confirm the old Render service cannot accept writes before allowing new
   launches. Do not clear leases, delete data, or replay jobs to force a
   successful check.
8. Trigger exactly one bounded existing canary; demand a genuine worker
   claim, model execution, durable final state, **automatically** created
   exact-SHA draft PR and independently successful CI before declaring the
   autonomous workflow verified. A PR manually constructed by an operator
   does not count. Keep the marker canary draft until these prerequisites
   are satisfied.

## Rotating secrets safely

GitHub Actions secret **values cannot be read back** from the GitHub UI.
If the existing operator/worker tokens are unavailable, generate **new**
independent random tokens and rotate both sides as one coordinated change.
Avoid switching the GitHub worker secret to a new value before Render is
ready to accept it. A missing/wrong token must result in authentication
failure, never an anonymous API.

If the Render ChatGPT connector reports `link_id must identify an eligible
linked account`, the **connector is not usable** even if the Render dashboard
has GitHub linked. Reconnect the **Render plugin to ChatGPT** using the new
account; GitHub-to-Render authorization and ChatGPT-to-Render authorization
are two separate connections. Do not claim a deploy succeeded until the
service is listed in the intended Render workspace.

## Free-tier limits and operational expectations

Render Free instances can spin down after inactivity, making the next
request slower. The existing GitHub Actions worker is scheduled every 5
minutes; verify it still performs successful, authorized API calls and
observe quota use before promising sustained 24/7 autonomy. Each Render
account's free quota is provider-enforced; this migration does **not**
guarantee the old or new account will avoid suspension, nor does it increase
AI model/GitHub Actions quotas. Keep paid auto-upgrades disabled.

## Rollback and audit

- Do not change `PRODUCTION_OS_URL` until new readiness + authorization
  checks pass. Keep the previous value for audit, not as a guaranteed
  working rollback destination.
- If the new host fails, stop new task launches and prevent concurrent
  writers; do not invent successful canary receipts.
- CI checks blueprint resource count, Free plan, absence of managed database
  and explicit `sync: false` secret prompts; it also boots the real free
  Docker image against disposable PostgreSQL credentials.
